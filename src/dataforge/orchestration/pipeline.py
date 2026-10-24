"""Coordena ingestão, perfil de qualidade, transformação e publicação."""
from __future__ import annotations
import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from uuid import uuid4
from dataforge import __version__
from dataforge.core.config import validate_config
from dataforge.ingestion.readers import read_table
from dataforge.quality.profiler import profile
from dataforge.transformation.cleaner import transform
from dataforge.export.writer import publish

LOG = logging.getLogger(__name__)


def sha256_file(path: Path) -> str:
    """Calcula fingerprint em blocos, sem carregar uma cópia extra em memória."""
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def run(source, output, config=None, **read_options) -> dict:
    """Executa uma tabela por lote. Retorna relatório somente após publicação."""
    started = perf_counter()
    source, output = Path(source).resolve(), Path(output).resolve()
    cfg = validate_config({} if config is None else config)
    if output.exists():
        raise ValueError('A pasta de saída já existe. Escolha outra para preservar resultados anteriores.')
    if not source.is_file():
        raise ValueError('Arquivo de entrada não encontrado.')
    run_id = str(uuid4())
    events = []

    def event(message):
        events.append(f'{datetime.now(timezone.utc).isoformat()} INFO run_id={run_id} {message}')
        LOG.info('run_id=%s %s', run_id, message)

    event('Início da ingestão')
    digest = sha256_file(source)
    df, metadata = read_table(source, **read_options)
    if sha256_file(source) != digest:
        raise ValueError('O arquivo de entrada mudou durante a leitura. Execute novamente com uma cópia estável.')
    event(f'Leitura concluída: {len(df)} linhas, {len(df.columns)} colunas')
    before = profile(df)
    cleaned, audit = transform(df, cfg)
    event(f"Transformação concluída: {len(audit['conversion_errors'])} conversões recusadas")
    report = {
        'version': __version__, 'run_id': run_id,
        'status': 'completed_with_warnings' if audit['conversion_errors'] else 'completed',
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'source_name': source.name, 'source_sha256': digest,
        'reader': metadata, 'config': cfg, 'before': before,
        'after': profile(cleaned), **audit,
        'processing_seconds_before_export': round(perf_counter() - started, 4),
    }
    event('Preparação dos arquivos de saída')
    publish(output, cleaned, report, '\n'.join(events) + '\n')
    LOG.info('run_id=%s Resultado publicado: %s', run_id, output)
    return report
