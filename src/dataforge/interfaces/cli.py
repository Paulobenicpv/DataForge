"""Ponto de entrada da interface de linha de comando."""
import argparse
import json
import logging
from pathlib import Path
from dataforge.orchestration.pipeline import run
LOG = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='DataForge — preparação configurável de CSV e Excel.')
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--config', type=Path)
    parser.add_argument('--separator', help='Exemplo: ; ou ,')
    parser.add_argument('--encoding', default='utf-8-sig', help='Use cp1252 para CSV Windows antigo.')
    parser.add_argument('--sheet', default=0, help='Nome da aba XLSX; padrão: primeira aba.')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    try:
        cfg = json.loads(args.config.read_text(encoding='utf-8-sig')) if args.config else {}
        report = run(args.input, args.output, cfg, separator=args.separator, encoding=args.encoding, sheet=args.sheet)
        if report['conversion_errors']:
            LOG.warning('Algumas conversões não foram aplicadas. Consulte relatorio.json.')
    except Exception as exc:
        LOG.error('%s', exc)
        raise SystemExit(1) from exc
