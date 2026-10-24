"""Métricas de qualidade sem amostras de valores no relatório."""
def profile(df):
    return {'rows': len(df), 'columns': len(df.columns),
            'duplicate_rows': int(df.duplicated().sum()),
            'fields': [{'name': c, 'dtype': str(df[c].dtype),
                        'empty': int((df[c].isna() | df[c].astype('string').str.strip().eq('')).sum()),
                        'distinct_non_null': int(df[c].nunique(dropna=True))} for c in df.columns]}
