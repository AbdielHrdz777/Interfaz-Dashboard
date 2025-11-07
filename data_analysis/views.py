from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection
import pandas as pd
import numpy as np

def get_active_dataset():
    """Obtiene la configuración del dataset activo"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT file_path, delimiter, encoding 
            FROM dataset_configs 
            WHERE active = 1 
            ORDER BY created_at DESC 
            LIMIT 1
        """)
        result = cursor.fetchone()
        if result:
            return {
                'file_path': result[0],
                'delimiter': result[1],
                'encoding': result[2]
            }
    return None

def load_dataset():
    """Carga el dataset desde la configuración"""
    config = get_active_dataset()
    if not config:
        config = {
            'file_path': 'data/bookings.csv',
            'delimiter': ',',
            'encoding': 'utf-8'
        }
    
    try:
        df = pd.read_csv(
            config['file_path'],
            delimiter=config['delimiter'],
            encoding=config['encoding']
        )
        return df
    except Exception as e:
        raise Exception(f"Error loading dataset: {str(e)}")

@api_view(['GET'])
def dataset_overview(request):
    """Información general del dataset"""
    try:
        df = load_dataset()
        
        overview = {
            'total_rows': int(df.shape[0]),
            'total_columns': int(df.shape[1]),
            'columns': list(df.columns),
            'memory_usage_mb': float(df.memory_usage(deep=True).sum() / 1024**2),
            'dataset_name': 'bookings.csv'
        }
        
        return Response(overview)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def null_values_analysis(request):
    """Análisis de valores nulos"""
    try:
        df = load_dataset()
        
        null_data = []
        for col in df.columns:
            null_count = int(df[col].isnull().sum())
            null_percentage = float((null_count / len(df)) * 100)
            
            null_data.append({
                'column': col,
                'null_count': null_count,
                'null_percentage': round(null_percentage, 2),
                'non_null_count': int(len(df) - null_count)
            })
        
        null_data.sort(key=lambda x: x['null_percentage'], reverse=True)
        
        summary = {
            'total_nulls': int(df.isnull().sum().sum()),
            'columns_with_nulls': int(sum(1 for item in null_data if item['null_count'] > 0)),
            'details': null_data
        }
        
        return Response(summary)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def duplicate_analysis(request):
    """Análisis de valores duplicados"""
    try:
        df = load_dataset()
        
        total_duplicates = int(df.duplicated().sum())
        duplicate_percentage = float((total_duplicates / len(df)) * 100)
        
        column_duplicates = []
        for col in df.columns:
            if 'ID' in col or 'id' in col:
                dup_count = int(df[col].duplicated().sum())
                if dup_count > 0:
                    column_duplicates.append({
                        'column': col,
                        'duplicate_count': dup_count,
                        'duplicate_percentage': round((dup_count / len(df)) * 100, 2)
                    })
        
        result = {
            'total_duplicate_rows': total_duplicates,
            'duplicate_percentage': round(duplicate_percentage, 2),
            'unique_rows': int(len(df) - total_duplicates),
            'column_duplicates': column_duplicates
        }
        
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def data_types_analysis(request):
    """Análisis de tipos de datos"""
    try:
        df = load_dataset()
        
        type_summary = {}
        column_details = []
        
        for col in df.columns:
            dtype = str(df[col].dtype)
            
            if dtype in ['int64', 'int32', 'float64', 'float32']:
                type_category = 'numeric'
            elif dtype == 'object':
                type_category = 'text'
            elif 'datetime' in dtype:
                type_category = 'datetime'
            else:
                type_category = 'other'
            
            type_summary[type_category] = type_summary.get(type_category, 0) + 1
            
            column_details.append({
                'column': col,
                'dtype': dtype,
                'category': type_category,
                'unique_values': int(df[col].nunique()),
                'sample_value': str(df[col].iloc[0]) if len(df) > 0 else None
            })
        
        result = {
            'type_summary': type_summary,
            'column_details': column_details
        }
        
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def data_quality_score(request):
    """Cálculo de score de calidad de datos"""
    try:
        df = load_dataset()
        
        null_score = 100 - (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100)
        duplicate_score = 100 - (df.duplicated().sum() / len(df) * 100)
        
        completeness = []
        for col in df.columns:
            comp = (1 - df[col].isnull().sum() / len(df)) * 100
            completeness.append({
                'column': col,
                'completeness': round(float(comp), 2)
            })
        
        overall_score = (null_score + duplicate_score) / 2
        
        result = {
            'overall_score': round(float(overall_score), 2),
            'null_score': round(float(null_score), 2),
            'duplicate_score': round(float(duplicate_score), 2),
            'completeness_by_column': completeness,
            'quality_level': 'Excellent' if overall_score >= 90 else 'Good' if overall_score >= 70 else 'Fair' if overall_score >= 50 else 'Poor'
        }
        
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def statistical_summary(request):
    """Resumen estadístico de columnas numéricas"""
    try:
        df = load_dataset()
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        summary = []
        for col in numeric_columns:
            stats = {
                'column': col,
                'mean': float(df[col].mean()) if not df[col].isna().all() else None,
                'median': float(df[col].median()) if not df[col].isna().all() else None,
                'std': float(df[col].std()) if not df[col].isna().all() else None,
                'min': float(df[col].min()) if not df[col].isna().all() else None,
                'max': float(df[col].max()) if not df[col].isna().all() else None,
                'q25': float(df[col].quantile(0.25)) if not df[col].isna().all() else None,
                'q75': float(df[col].quantile(0.75)) if not df[col].isna().all() else None
            }
            summary.append(stats)
        
        return Response({'numeric_summary': summary})
    except Exception as e:
        return Response({'error': str(e)}, status=500)