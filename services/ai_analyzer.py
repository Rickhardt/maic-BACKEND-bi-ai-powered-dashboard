import json
from typing import Dict, Any, List
import os
import logging
import traceback
from dotenv import load_dotenv

# Configurar logging
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Intentar importar Anthropic (Claude API)
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


def analyze_dataframe_mock(schema: Dict[str, Any], summary: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Versión mock del analizador de IA que simula respuestas inteligentes
    basadas en la estructura de los datos.
    
    Args:
        schema: Información del esquema del DataFrame
        summary: Estadísticas descriptivas
        
    Returns:
        Lista de sugerencias de visualización
    """
    columns = schema.get('columns', [])
    dtypes = schema.get('dtypes', {})
    numeric_cols = [col for col, dtype in dtypes.items() if 'int' in dtype or 'float' in dtype]
    categorical_cols = [col for col, dtype in dtypes.items() if 'object' in dtype or 'category' in dtype]
    
    suggestions = []
    
    # Sugerencia 1: Gráfico de barras si hay columnas categóricas y numéricas
    if categorical_cols and numeric_cols:
        cat_col = categorical_cols[0]
        num_col = numeric_cols[0]
        suggestions.append({
            'title': f'Distribución de {num_col} por {cat_col}',
            'chart_type': 'bar',
            'parameters': {
                'x_axis': cat_col,
                'y_axis': num_col,
                'group_by': cat_col,
                'aggregate': 'sum'
            },
            'insight': f'Este gráfico muestra cómo se distribuye {num_col} entre las diferentes categorías de {cat_col}. Útil para identificar patrones y comparar valores entre grupos.'
        })
    
    # Sugerencia 2: Gráfico de líneas si hay datos numéricos secuenciales
    if len(numeric_cols) >= 2:
        suggestions.append({
            'title': f'Tendencia de {numeric_cols[0]} vs {numeric_cols[1]}',
            'chart_type': 'line',
            'parameters': {
                'x_axis': numeric_cols[0],
                'y_axis': numeric_cols[1]
            },
            'insight': f'Visualiza la relación y tendencia entre {numeric_cols[0]} y {numeric_cols[1]}. Ideal para identificar correlaciones y patrones temporales o secuenciales.'
        })
    
    # Sugerencia 3: Gráfico de pie si hay una columna categórica y numérica
    if categorical_cols and numeric_cols:
        cat_col = categorical_cols[0]
        num_col = numeric_cols[0]
        suggestions.append({
            'title': f'Proporción de {num_col} por {cat_col}',
            'chart_type': 'pie',
            'parameters': {
                'category': cat_col,
                'value': num_col,
                'group_by': cat_col,
                'aggregate': 'sum'
            },
            'insight': f'Este gráfico circular muestra la proporción relativa de {num_col} para cada categoría de {cat_col}. Perfecto para entender la distribución porcentual.'
        })
    
    # Sugerencia 4: Scatter plot si hay múltiples columnas numéricas
    if len(numeric_cols) >= 2:
        suggestions.append({
            'title': f'Relación entre {numeric_cols[0]} y {numeric_cols[1]}',
            'chart_type': 'scatter',
            'parameters': {
                'x_axis': numeric_cols[0],
                'y_axis': numeric_cols[1]
            },
            'insight': f'Un gráfico de dispersión que revela la relación entre {numeric_cols[0]} y {numeric_cols[1]}. Útil para detectar correlaciones, outliers y patrones no lineales.'
        })
    
    # Sugerencia 5: Análisis de distribución si hay suficientes datos numéricos
    if numeric_cols:
        num_col = numeric_cols[0]
        suggestions.append({
            'title': f'Distribución de {num_col}',
            'chart_type': 'bar',
            'parameters': {
                'x_axis': 'index',
                'y_axis': num_col
            },
            'insight': f'Visualiza la distribución de valores de {num_col} en el dataset. Ayuda a identificar valores atípicos y entender la dispersión de los datos.'
        })
    
    # Sugerencias para cuando solo hay columnas categóricas
    if categorical_cols and not numeric_cols:
        # Sugerencia: Conteo de frecuencias de la primera columna categórica
        if len(categorical_cols) >= 1:
            cat_col = categorical_cols[0]
            suggestions.append({
                'title': f'Frecuencia de {cat_col}',
                'chart_type': 'bar',
                'parameters': {
                    'x_axis': cat_col,
                    'y_axis': 'count',
                    'group_by': cat_col,
                    'aggregate': 'count'
                },
                'insight': f'Este gráfico muestra la frecuencia de cada valor único en {cat_col}. Útil para identificar los valores más comunes y la distribución de categorías.'
            })
        
        # Sugerencia: Relación entre dos columnas categóricas (conteo cruzado)
        if len(categorical_cols) >= 2:
            cat_col1 = categorical_cols[0]
            cat_col2 = categorical_cols[1]
            suggestions.append({
                'title': f'Distribución de {cat_col1} por {cat_col2}',
                'chart_type': 'bar',
                'parameters': {
                    'x_axis': cat_col1,
                    'y_axis': 'count',
                    'group_by': cat_col1,
                    'aggregate': 'count',
                    'category': cat_col2
                },
                'insight': f'Este gráfico muestra cómo se distribuyen los valores de {cat_col1} en relación con {cat_col2}. Ayuda a identificar patrones y relaciones entre categorías.'
            })
        
        # Sugerencia: Gráfico de pie con frecuencias
        if len(categorical_cols) >= 1:
            cat_col = categorical_cols[0]
            suggestions.append({
                'title': f'Proporción de {cat_col}',
                'chart_type': 'pie',
                'parameters': {
                    'category': cat_col,
                    'value': 'count',
                    'group_by': cat_col,
                    'aggregate': 'count'
                },
                'insight': f'Este gráfico circular muestra la proporción relativa de cada valor en {cat_col}. Perfecto para visualizar la distribución porcentual de categorías.'
            })
    
    # Limitar a máximo 5 sugerencias
    return suggestions[:5]


def analyze_dataframe_claude(schema: Dict[str, Any], summary: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Versión real del analizador que usa Claude API (Anthropic).
    
    Args:
        schema: Información del esquema del DataFrame
        summary: Estadísticas descriptivas
        
    Returns:
        Lista de sugerencias de visualización
    """
    if not ANTHROPIC_AVAILABLE:
        logger.info("Anthropic library not available, using mock analyzer")
        return analyze_dataframe_mock(schema, summary)
    
    api_key = os.getenv('AI_API_KEY')
    if not api_key:
        logger.info("AI_API_KEY not found, using mock analyzer")
        return analyze_dataframe_mock(schema, summary)
    
    # Intentar inicializar el cliente de Anthropic
    try:
        client = Anthropic(api_key=api_key)
        logger.info("Anthropic client initialized successfully")
    except TypeError as e:
        # Capturar específicamente errores de argumentos inesperados
        logger.warning(f"Error de tipo al inicializar cliente Anthropic (posible incompatibilidad de versión): {e}")
        logger.warning(f"Full traceback: {traceback.format_exc()}")
        logger.warning("Falling back to mock analyzer")
        return analyze_dataframe_mock(schema, summary)
    except Exception as e:
        logger.warning(f"Error al inicializar cliente Anthropic: {e}")
        logger.warning(f"Full traceback: {traceback.format_exc()}")
        logger.warning("Falling back to mock analyzer")
        return analyze_dataframe_mock(schema, summary)
    
    prompt = f"""Eres un analista de datos experto. Analiza la siguiente información de un DataFrame y sugiere 3-5 visualizaciones útiles.

Información del DataFrame:
- Columnas: {schema.get('columns', [])}
- Tipos de datos: {schema.get('dtypes', {})}
- Forma: {schema.get('shape', (0, 0))}
- Estadísticas: {json.dumps(summary.get('summary_stats', {}), indent=2)}

Responde ÚNICAMENTE con un JSON válido (sin markdown, sin texto adicional). Array de objetos con:
- title: string (título descriptivo, ej: "Frecuencia de Planes por Nombre")
- chart_type: string (uno de: "bar", "line", "pie", "scatter")
- parameters: object (x_axis, y_axis, category, value, group_by, aggregate según corresponda)
- insight: string (2-3 oraciones explicando: qué visualiza, qué significa, qué patrones revela)

Ejemplo:
[
  {{
    "title": "Frecuencia de Planes de Proceso",
    "chart_type": "bar",
    "parameters": {{
      "x_axis": "PROCESSPLANNAME",
      "y_axis": "count",
      "group_by": "PROCESSPLANNAME",
      "aggregate": "count"
    }},
    "insight": "Muestra la frecuencia de cada plan de proceso. Los valores altos indican planes ejecutados repetidamente. Útil para identificar procesos críticos y optimizar recursos."
  }}
]

Genera el JSON ahora:"""

    try:
        logger.info("Calling Claude API for data analysis...")
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            temperature=0.7,
            system="Eres un experto analista de datos que genera sugerencias de visualización en formato JSON.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        logger.info("Claude API call successful")
        
        content = message.content[0].text.strip()
        # Limpiar el contenido si tiene markdown code blocks
        if content.startswith('```json'):
            content = content[7:]
        if content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()
        
        suggestions = json.loads(content)
        logger.info(f"Successfully parsed {len(suggestions)} suggestions from Claude")
        return suggestions if isinstance(suggestions, list) else []
    
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON from Claude API response: {e}")
        logger.error(f"Response content: {content if 'content' in locals() else 'N/A'}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        logger.info("Falling back to mock analyzer")
        return analyze_dataframe_mock(schema, summary)
    
    except Exception as e:
        logger.error(f"Error calling Claude API: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        logger.info("Falling back to mock analyzer")
        return analyze_dataframe_mock(schema, summary)


def analyze_dataframe(schema: Dict[str, Any], summary: Dict[str, Any], use_claude: bool = False) -> List[Dict[str, Any]]:
    """
    Función principal para analizar un DataFrame y generar sugerencias de visualización.
    
    Args:
        schema: Información del esquema del DataFrame
        summary: Estadísticas descriptivas
        use_claude: Si True, usa API de IA (Claude); si False, usa mock
        
    Returns:
        Lista de sugerencias de visualización
    """
    if use_claude:
        logger.info("Using Claude AI analyzer")
        return analyze_dataframe_claude(schema, summary)
    else:
        logger.info("Using mock analyzer")
        return analyze_dataframe_mock(schema, summary)