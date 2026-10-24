"""Transformações explícitas, independentes da área de negócio."""
import re
import unicodedata
from dataforge.core.config import validate_config
from dataforge.ingestion.headers import unique_headers
from dataforge.transformation.converters import convert_series

def transform(df, config):
    cfg = validate_config(config)
    out = df.copy()
    changes, mapping, errors = [], [], []
    if cfg['normalize_headers']:
        names = []
        for c in out.columns:
            name = unicodedata.normalize('NFKD', str(c)).encode('ascii', 'ignore').decode().lower()
            names.append(re.sub(r'[^a-z0-9]+', '_', name).strip('_'))
        names = unique_headers(names)
        mapping = [{'original': a, 'normalized': b} for a, b in zip(out.columns, names)]
        out.columns = names
    requested = set(cfg['uppercase']) | set(cfg['conversions'])
    if requested - set(out.columns):
        raise ValueError(f'Colunas não encontradas (use os nomes após normalização): {sorted(requested - set(out.columns))}')
    for c in out.columns:
        if cfg['trim']:
            before = out[c].copy()
            out[c] = out[c].astype('string').str.strip()
            count = int(before.fillna('').ne(out[c].fillna('')).sum())
            if count:
                changes.append({'action': 'trim', 'column': c, 'cells': count})
        if c in cfg['uppercase']:
            before = out[c].copy()
            out[c] = out[c].astype('string').str.upper()
            changes.append({'action': 'uppercase', 'column': c, 'cells': int(before.fillna('').ne(out[c].fillna('')).sum())})
        if c in cfg['conversions']:
            rule = cfg['conversions'][c]
            values = out[c].astype('string').str.strip()
            converted = convert_series(values, rule)
            bad = values.notna() & values.ne('') & converted.isna()
            if bad.any():
                # Rejeita a conversão inteira; preserva todos os valores dessa coluna.
                errors.append({'column': c, 'invalid_cells': int(bad.sum()), 'action': 'conversion_skipped'})
            else:
                out[c] = converted
                changes.append({'action': 'convert_' + rule['type'], 'column': c, 'cells': int((values.notna() & values.ne('')).sum())})
    empty = out.isna() | out.astype('string').apply(lambda s: s.str.strip().eq('')).fillna(False)
    if cfg['drop_empty_rows']:
        mask = empty.all(axis=1)
        changes.append({'action': 'drop_empty_rows', 'rows': int(mask.sum())})
        out = out.loc[~mask]
    if cfg['drop_empty_columns']:
        cols = empty.columns[empty.all(axis=0)].tolist()
        out = out.drop(columns=cols)
        changes.append({'action': 'drop_empty_columns', 'columns': cols})
    if cfg['drop_duplicates']:
        count = int(out.duplicated().sum())
        out = out.drop_duplicates()
        changes.append({'action': 'drop_duplicates', 'rows': count})
    if not len(out.columns):
        raise ValueError('O tratamento removeria todas as colunas. Ajuste as opções.')
    return out, {'changes': changes, 'header_mapping': mapping, 'conversion_errors': errors}
