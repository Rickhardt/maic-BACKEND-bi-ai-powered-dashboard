import pandas as pd
import os
from typing import Dict, Any, Tuple
from pathlib import Path


def process_file(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Procesa un archivo .xlsx o .csv y retorna el DataFrame junto con metadatos.
    
    Args:
        file_path: Ruta al archivo a procesar
        
    Returns:
        Tuple con (DataFrame, metadatos)
    """
    file_extension = Path(file_path).suffix.lower()
    
    # Leer archivo según extensión
    if file_extension == '.csv':
        df = pd.read_csv(file_path, encoding='utf-8')
    elif file_extension in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path, engine='openpyxl')
    else:
        raise ValueError(f"Formato de archivo no soportado: {file_extension}")
    
    # Extraer metadatos
    metadata = {
        'columns': df.columns.tolist(),
        'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
        'shape': df.shape,
        'summary_stats': df.describe().to_dict() if not df.empty else {},
        'null_counts': df.isnull().sum().to_dict(),
        'memory_usage': df.memory_usage(deep=True).sum(),
    }
    
    # Agregar información adicional
    metadata['info'] = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
        'categorical_columns': df.select_dtypes(include=['object', 'category']).columns.tolist(),
        'datetime_columns': df.select_dtypes(include=['datetime']).columns.tolist(),
    }
    
    return df, metadata


def get_chart_data(
    df: pd.DataFrame,
    chart_type: str,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Procesa los datos del DataFrame según los parámetros del gráfico
    y retorna datos agregados listos para visualizar.
    
    Args:
        df: DataFrame con los datos
        chart_type: Tipo de gráfico (bar, line, pie, scatter)
        parameters: Parámetros del gráfico
        
    Returns:
        Diccionario con datos formateados para visualización
    """
    x_axis = parameters.get('x_axis')
    y_axis = parameters.get('y_axis')
    category = parameters.get('category')
    value = parameters.get('value')
    group_by = parameters.get('group_by')
    aggregate = parameters.get('aggregate', 'sum')
    
    result = {
        'data': [],
        'labels': None
    }
    
    try:
        if chart_type == 'bar' or chart_type == 'line':
            if x_axis and y_axis:
                # Agrupar y agregar si es necesario
                if group_by:
                    grouped = df.groupby(group_by)[y_axis]
                    if aggregate == 'sum':
                        aggregated = grouped.sum()
                    elif aggregate == 'mean':
                        aggregated = grouped.mean()
                    elif aggregate == 'count':
                        aggregated = grouped.count()
                    else:
                        aggregated = grouped.sum()
                    
                    result['data'] = [
                        {'name': str(name), 'value': float(val)}
                        for name, val in aggregated.items()
                    ]
                    result['labels'] = [str(name) for name in aggregated.index]
                else:
                    # Datos simples sin agrupación
                    result['data'] = [
                        {'name': str(df.iloc[i][x_axis]), 'value': float(df.iloc[i][y_axis])}
                        for i in range(min(len(df), 100))  # Limitar a 100 puntos
                    ]
                    result['labels'] = [str(df.iloc[i][x_axis]) for i in range(min(len(df), 100))]
        
        elif chart_type == 'pie':
            if category and value:
                if group_by:
                    grouped = df.groupby(group_by)[value]
                    if aggregate == 'sum':
                        aggregated = grouped.sum()
                    elif aggregate == 'mean':
                        aggregated = grouped.mean()
                    else:
                        aggregated = grouped.sum()
                else:
                    aggregated = df.groupby(category)[value].sum()
                
                result['data'] = [
                    {'name': str(name), 'value': float(val)}
                    for name, val in aggregated.items()
                ]
                result['labels'] = [str(name) for name in aggregated.index]
        
        elif chart_type == 'scatter':
            if x_axis and y_axis:
                result['data'] = [
                    {'x': float(df.iloc[i][x_axis]), 'y': float(df.iloc[i][y_axis])}
                    for i in range(min(len(df), 500))  # Limitar a 500 puntos para scatter
                ]
        
        # Si no hay datos, intentar con las columnas disponibles
        if not result['data'] and len(df) > 0:
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            if len(numeric_cols) >= 2:
                result['data'] = [
                    {'name': str(i), 'value': float(df.iloc[i][numeric_cols[0]])}
                    for i in range(min(len(df), 50))
                ]
                result['labels'] = [str(i) for i in range(min(len(df), 50))]
    
    except Exception as e:
        # En caso de error, retornar datos vacíos
        result['data'] = []
        result['error'] = str(e)
    
    return result
