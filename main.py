from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import tempfile
from pathlib import Path
from typing import Optional

from models.schemas import (
    UploadResponse,
    ChartSuggestion,
    ChartDataRequest,
    ChartDataResponse,
    ChartParameters
)
from services.data_processor import process_file, get_chart_data
from services.ai_analyzer import analyze_dataframe

app = FastAPI(title="Dashboard Creator API", version="1.0.0")

# Configurar CORS
origins = [
    "http://localhost:5173",  # Vite default
    "http://localhost:3000",   # React default
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Almacenar DataFrames en memoria (en producción usar cache/DB)
dataframes_cache: dict[str, any] = {}


@app.get("/")
async def root():
    return {"message": "Dashboard Creator API", "status": "running"}


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/api/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Endpoint para subir y procesar archivos .xlsx o .csv
    """
    # Validar tipo de archivo
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ['.xlsx', '.xls', '.csv']:
        raise HTTPException(
            status_code=400,
            detail="Formato de archivo no soportado. Solo se aceptan .xlsx, .xls o .csv"
        )
    
    # Guardar archivo temporalmente
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Procesar archivo
        df, metadata = process_file(tmp_path)
        
        # Generar ID único para el archivo
        import uuid
        file_id = str(uuid.uuid4())
        
        # Guardar DataFrame en cache
        dataframes_cache[file_id] = df
        
        # Analizar con IA
        schema = {
            'columns': metadata['columns'],
            'dtypes': metadata['dtypes'],
            'shape': metadata['shape']
        }
        summary = {
            'summary_stats': metadata['summary_stats'],
            'info': metadata['info']
        }
        
        # Usar IA si está configurado, sino usar mock
        use_ai = os.getenv('AI_API_KEY') is not None
        ai_suggestions = analyze_dataframe(schema, summary, use_claude=use_ai)
        
        # Convertir a modelos Pydantic
        suggestions = [
            ChartSuggestion(**suggestion) for suggestion in ai_suggestions
        ]
        
        # Limpiar archivo temporal
        os.unlink(tmp_path)
        
        return UploadResponse(
            success=True,
            message=f"Archivo procesado exitosamente. {len(suggestions)} sugerencias generadas.",
            suggestions=suggestions,
            file_info={
                'file_id': file_id,
                'filename': file.filename,
                'rows': metadata['info']['total_rows'],
                'columns': metadata['info']['total_columns'],
                'column_names': metadata['columns']
            }
        )
    
    except Exception as e:
        # Limpiar archivo temporal en caso de error
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar archivo: {str(e)}"
        )


@app.post("/api/chart-data", response_model=ChartDataResponse)
async def get_chart_data_endpoint(request: ChartDataRequest):
    """
    Endpoint para obtener datos agregados de un gráfico específico
    """
    if not request.file_id or request.file_id not in dataframes_cache:
        raise HTTPException(
            status_code=404,
            detail="Archivo no encontrado. Por favor, sube un archivo primero."
        )
    
    df = dataframes_cache[request.file_id]
    
    try:
        # Convertir ChartParameters a dict
        params_dict = request.parameters.dict(exclude_none=True)
        
        # Obtener datos procesados
        chart_data = get_chart_data(df, request.chart_type, params_dict)
        
        if 'error' in chart_data:
            raise HTTPException(
                status_code=400,
                detail=f"Error al procesar datos: {chart_data['error']}"
            )
        
        return ChartDataResponse(
            success=True,
            chart_type=request.chart_type,
            data=chart_data['data'],
            labels=chart_data.get('labels')
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener datos del gráfico: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("BACKEND_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
