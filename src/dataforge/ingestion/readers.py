"""Leitura tabular estrita; IDs e textos literais são preservados."""
from __future__ import annotations
import csv
import io
from pathlib import Path
import pandas as pd
from dataforge.ingestion.headers import unique_headers


def read_table(path: Path, *, separator=None, encoding='utf-8-sig', sheet=0):
    path = Path(path)
    if separator is not None and (not isinstance(separator, str) or len(separator) != 1):
        raise ValueError('Separador deve ter exatamente um caractere.')
    if path.suffix.lower() in ('.csv', '.tsv', '.txt'):
        text = path.read_text(encoding=encoding, errors='strict')
        if not text.strip():
            raise ValueError('Arquivo vazio.')
        sep = separator
        if sep is None and path.suffix.lower() == '.tsv':
            sep = '\t'
        if sep is None:
            try:
                sep = csv.Sniffer().sniff(text[:65536], delimiters=';,\t|').delimiter
            except csv.Error as exc:
                raise ValueError(
                    'Não foi possível detectar o separador. Selecione-o na tela ou use --separator '
                    '(inclusive em CSV de coluna única).'
                ) from exc
        reader = csv.reader(io.StringIO(text, newline=''), delimiter=sep, strict=True)
        try:
            headers = next(reader)
        except (StopIteration, csv.Error) as exc:
            raise ValueError('Cabeçalho CSV inválido.') from exc
        if not headers:
            raise ValueError('Cabeçalho vazio. A primeira linha deve conter as colunas.')
        records = []
        try:
            for number, row in enumerate(reader, 2):
                if len(row) != len(headers):
                    raise ValueError(
                        f'Registro CSV {number}: esperado {len(headers)} campos; recebido {len(row)}. '
                        'Nenhum registro foi ignorado.'
                    )
                records.append(row)
        except csv.Error as exc:
            raise ValueError(f'CSV inválido próximo à linha física {reader.line_num}: {exc}') from exc
        df = pd.DataFrame(records, columns=unique_headers(headers), dtype='string')
        metadata = {'separator': sep, 'encoding': encoding}
    elif path.suffix.lower() == '.xlsx':
        if not isinstance(sheet, (str, int)) or isinstance(sheet, bool):
            raise ValueError('Selecione uma aba pelo nome ou índice inteiro.')
        raw = pd.read_excel(path, sheet_name=sheet, header=None, dtype='string',
                            keep_default_na=False, engine='openpyxl')
        if raw.empty:
            raise ValueError('Planilha vazia.')
        headers = raw.iloc[0].tolist()
        df = raw.iloc[1:].reset_index(drop=True)
        df.columns = unique_headers(headers)
        metadata = {'sheet': sheet}
    else:
        raise ValueError('Formato aceito: CSV, TSV, TXT delimitado ou XLSX.')
    metadata['headers'] = [{'original': str(a), 'loaded': b} for a, b in zip(headers, df.columns)]
    return df, metadata
