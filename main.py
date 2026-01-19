from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import tempfile
from pathlib import Path
from typing import Optional
import traceback
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from models.schemas import (
    UploadResponse,
    ChartSuggestion,
    ChartDataRequest,
    ChartDataResponse,
    ChartParameters
)
from services.data_processor import process_file, get_chart_data
from services.ai_analyzer import analyze_dataframe, ANTHROPIC_AVAILABLE

app = FastAPI(title="Dashboard Creator API", version="1.0.0")

# Configurar CORS
origins = [
    "http://localhost:5173",  # Vite default
    "http://localhost:3000",   # React default
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "https://bi-dashboard-vert.vercel.app/"
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


@app.get("/api/test-anthropic")
async def test_anthropic():
    """
    Endpoint de prueba para verificar la inicialización del cliente de Anthropic.
    Útil para diagnosticar problemas con la API de Claude.
    """
    result = {
        "anthropic_available": ANTHROPIC_AVAILABLE,
        "api_key_configured": os.getenv('AI_API_KEY') is not None,
        "api_key_length": len(os.getenv('AI_API_KEY', '')) if os.getenv('AI_API_KEY') else 0,
        "client_initialization": "not_attempted",
        "error": None,
        "error_type": None,
        "error_details": None
    }
    
    if not ANTHROPIC_AVAILABLE:
        result["error"] = "Biblioteca anthropic no está disponible (no se pudo importar)"
        result["error_type"] = "ImportError"
        return result
    
    if not os.getenv('AI_API_KEY'):
        result["error"] = "AI_API_KEY no está configurada en las variables de entorno"
        result["error_type"] = "ConfigurationError"
        return result
    
    # Intentar inicializar el cliente
    try:
        from anthropic import Anthropic
        api_key = os.getenv('AI_API_KEY')
        
        try:
            client = Anthropic(api_key=api_key)
            result["client_initialization"] = "success"
            
            # Intentar hacer una llamada de prueba muy simple (solo verificar que el cliente funciona)
            # No hacemos una llamada real para no consumir tokens
            result["status"] = "ready"
            result["message"] = "Cliente de Anthropic inicializado correctamente"
            
        except TypeError as e:
            result["client_initialization"] = "failed"
            result["error"] = str(e)
            result["error_type"] = "TypeError"
            result["error_details"] = traceback.format_exc()
            result["status"] = "error"
            result["message"] = "Error al inicializar cliente (posible incompatibilidad de versión)"
            
        except Exception as e:
            result["client_initialization"] = "failed"
            result["error"] = str(e)
            result["error_type"] = type(e).__name__
            result["error_details"] = traceback.format_exc()
            result["status"] = "error"
            result["message"] = f"Error inesperado: {str(e)}"
            
    except Exception as e:
        result["error"] = str(e)
        result["error_type"] = type(e).__name__
        result["error_details"] = traceback.format_exc()
        result["status"] = "error"
        result["message"] = f"Error al importar o inicializar: {str(e)}"
    
    return result


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
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            content = await file.read()
            if not content or len(content) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="El archivo está vacío"
                )
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
        
        # Validar y convertir a modelos Pydantic
        suggestions = []
        for suggestion in ai_suggestions:
            try:
                # Asegurar que todos los campos requeridos estén presentes
                if 'title' not in suggestion:
                    suggestion['title'] = 'Gráfico sin título'
                if 'chart_type' not in suggestion:
                    suggestion['chart_type'] = 'bar'
                if 'parameters' not in suggestion:
                    suggestion['parameters'] = {}
                if 'insight' not in suggestion:
                    suggestion['insight'] = 'Análisis de datos'
                
                # Convertir parameters a ChartParameters si es dict
                if isinstance(suggestion['parameters'], dict):
                    suggestion['parameters'] = ChartParameters(**suggestion['parameters'])
                
                suggestions.append(ChartSuggestion(**suggestion))
            except Exception as e:
                logger.warning(f"Error al procesar sugerencia: {str(e)}. Sugerencia: {suggestion}")
                continue
        
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
            try:
                os.unlink(tmp_path)
            except:
                pass
        
        # Log del error completo para debugging
        error_trace = traceback.format_exc()
        logger.error(f"Error al procesar archivo: {str(e)}\n{error_trace}")
        
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
    port = int(os.getenv("PORT", os.getenv("BACKEND_PORT", 8000)))
    uvicorn.run(app, host="0.0.0.0", port=port)
