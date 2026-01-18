import json
from typing import Dict, Any, List
import os
from dotenv import load_dotenv

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
        return analyze_dataframe_mock(schema, summary)
    
    api_key = os.getenv('AI_API_KEY')
    if not api_key:
        print("Warning: AI_API_KEY not found, using mock analyzer")
        return analyze_dataframe_mock(schema, summary)
    
    client = Anthropic(api_key=api_key)
    
    prompt = f"""Eres un analista de datos experto. Analiza la siguiente información de un DataFrame y sugiere 3-5 visualizaciones específicas y útiles.

Información del DataFrame:
- Columnas: {schema.get('columns', [])}
- Tipos de datos: {schema.get('dtypes', {})}
- Forma: {schema.get('shape', (0, 0))}
- Estadísticas descriptivas: {json.dumps(summary.get('summary_stats', {}), indent=2)}

Responde ÚNICAMENTE con un JSON válido que contenga un array de objetos. Cada objeto debe tener exactamente estas claves:
- title: string (título descriptivo del gráfico)
- chart_type: string (uno de: "bar", "line", "pie", "scatter")
- parameters: object con claves como x_axis, y_axis, category, value, group_by, aggregate
- insight: string (análisis breve de 1-2 oraciones explicando qué revela este gráfico)

Ejemplo de formato:
[
  {{
    "title": "Distribución de Ventas por Región",
    "chart_type": "bar",
    "parameters": {{
      "x_axis": "Región",
      "y_axis": "Ventas",
      "group_by": "Región",
      "aggregate": "sum"
    }},
    "insight": "Este gráfico revela que la región 'Norte' tiene el mayor rendimiento en ventas."
  }}
]

Responde solo con el JSON, sin texto adicional:"""

    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            temperature=0.7,
            system="Eres un experto analista de datos que genera sugerencias de visualización en formato JSON.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
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
        return suggestions if isinstance(suggestions, list) else []
    
    except Exception as e:
        print(f"Error calling Claude API: {e}")
        print("Falling back to mock analyzer")
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
        return analyze_dataframe_claude(schema, summary)
    else:
        return analyze_dataframe_mock(schema, summary)
