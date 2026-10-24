"""Validação e cópia independente das regras de transformação."""
from __future__ import annotations
from copy import deepcopy

DEFAULTS = {
    'trim': True, 'normalize_headers': False, 'drop_duplicates': False,
    'drop_empty_rows': False, 'drop_empty_columns': False,
    'uppercase': [], 'conversions': {},
}


def validate_config(config: dict) -> dict:
    if not isinstance(config, dict):
        raise ValueError('A configuração deve ser um objeto JSON.')
    unknown = set(config) - set(DEFAULTS)
    if unknown:
        raise ValueError(f'Opções desconhecidas: {sorted(map(str, unknown))}')
    result = deepcopy({**DEFAULTS, **config})
    for key in ('trim', 'normalize_headers', 'drop_duplicates', 'drop_empty_rows', 'drop_empty_columns'):
        if type(result[key]) is not bool:
            raise ValueError(f'{key} deve ser booleano.')
    if not isinstance(result['uppercase'], list) or not all(
        isinstance(c, str) and c for c in result['uppercase']
    ):
        raise ValueError('uppercase deve ser uma lista de nomes de colunas não vazios.')
    if not isinstance(result['conversions'], dict):
        raise ValueError('conversions deve ser um objeto.')
    for column, rule in result['conversions'].items():
        if not isinstance(column, str) or not column:
            raise ValueError('Nome de coluna para conversão deve ser texto não vazio.')
        if not isinstance(rule, dict) or rule.get('type') not in ('number', 'date'):
            raise ValueError(f'Conversão inválida: {column}')
        allowed = {'type', 'format'} if rule['type'] == 'date' else {'type', 'decimal', 'thousands'}
        if set(rule) - allowed:
            raise ValueError(f'Opções incompatíveis com a conversão: {column}')
        if rule['type'] == 'date':
            fmt = rule.get('format')
            if not isinstance(fmt, str) or not fmt or fmt in ('mixed', 'ISO8601'):
                raise ValueError(f'Informe formato explícito para {column}, por exemplo %d/%m/%Y.')
        else:
            decimal = rule.get('decimal', '.')
            thousands = rule.get('thousands')
            if not isinstance(decimal, str) or decimal not in ('.', ','):
                raise ValueError(f'Separador decimal inválido: {column}')
            if thousands is not None and (
                not isinstance(thousands, str) or thousands not in ('.', ',', ' ')
                or thousands == decimal
            ):
                raise ValueError(f'Separador de milhar inválido: {column}')
    return result
