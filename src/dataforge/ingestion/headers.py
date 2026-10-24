"""Resolução determinística de nomes de colunas."""
def unique_headers(headers):
    used, result = set(), []
    for position, header in enumerate(headers, 1):
        base = str(header) if header is not None and str(header) else f'coluna_{position}'
        candidate, suffix = base, 2
        while candidate in used:
            candidate = f'{base}_{suffix}'
            suffix += 1
        used.add(candidate)
        result.append(candidate)
    return result
