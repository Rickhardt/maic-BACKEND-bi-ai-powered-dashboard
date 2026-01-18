from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ChartParameters(BaseModel):
    """Parámetros para un gráfico específico"""
    x_axis: Optional[str] = None
    y_axis: Optional[str] = None
    category: Optional[str] = None
    value: Optional[str] = None
    group_by: Optional[str] = None
    aggregate: Optional[str] = None  # sum, mean, count, etc.


class ChartSuggestion(BaseModel):
    """Sugerencia de visualización generada por IA"""
    title: str = Field(..., description="Título descriptivo del gráfico")
    chart_type: str = Field(..., description="Tipo de gráfico: bar, line, pie, scatter")
    parameters: ChartParameters = Field(..., description="Parámetros del gráfico")
    insight: str = Field(..., description="Análisis breve generado por IA")


class UploadResponse(BaseModel):
    """Respuesta del endpoint de carga de archivos"""
    success: bool
    message: str
    suggestions: List[ChartSuggestion]
    file_info: Dict[str, Any]


class ChartDataRequest(BaseModel):
    """Request para obtener datos de un gráfico específico"""
    chart_type: str
    parameters: ChartParameters
    file_id: Optional[str] = None  # Para identificar el archivo procesado


class ChartDataPoint(BaseModel):
    """Punto de datos para visualización"""
    name: str
    value: float
    category: Optional[str] = None


class ChartDataResponse(BaseModel):
    """Respuesta con datos agregados para visualización"""
    success: bool
    chart_type: str
    data: List[Dict[str, Any]]
    labels: Optional[List[str]] = None
