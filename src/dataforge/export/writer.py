"""Publicação do lote completo usando pasta temporária e bloqueio exclusivo."""
from __future__ import annotations
import json
import os
import shutil
import tempfile
from pathlib import Path
import pandas as pd


def publish(output: Path, frame: pd.DataFrame, report: dict, execution_log: str) -> None:
    """Não substitui execuções anteriores. O lock coordena processos DataForge."""
    output.parent.mkdir(parents=True, exist_ok=True)
    lock = output.parent / f'.{output.name}.lock'
    # Não remova locks encontrados: podem pertencer a outra execução.
    descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    staging = None
    try:
        os.close(descriptor)
        if output.exists():
            raise ValueError('Pasta de saída já existe; escolha outro nome.')
        staging = Path(tempfile.mkdtemp(prefix='.dataforge-', dir=output.parent))
        frame.to_csv(staging / 'dados_tratados.csv', sep=';', index=False,
                     encoding='utf-8-sig')
        (staging / 'relatorio.json').write_text(
            json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
        summary = (
            f"Status: {report['status']}\n"
            f"Linhas: {report['before']['rows']} -> {report['after']['rows']}\n"
            f"Colunas: {report['before']['columns']} -> {report['after']['columns']}\n"
            f"Conversões recusadas: {len(report['conversion_errors'])}\n"
            'Consulte relatorio.json para as regras e alterações.\n'
            'CSV UTF-8, delimitador ;, ponto decimal. IDs devem permanecer como Texto no Power BI.\n'
        )
        (staging / 'LEIA_RESULTADO.txt').write_text(summary, encoding='utf-8')
        (staging / 'execution.log').write_text(execution_log, encoding='utf-8')
        (staging / '_SUCCESS').write_text(report['run_id'] + '\n', encoding='utf-8')
        if output.exists():
            raise ValueError('Pasta de saída criada durante a execução; escolha outro nome.')
        staging.rename(output)
    finally:
        if staging is not None and staging.exists():
            shutil.rmtree(staging)
        lock.unlink(missing_ok=True)
