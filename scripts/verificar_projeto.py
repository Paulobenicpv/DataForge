"""Verifica a integridade básica do código antes da instalação."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIRED = (
    'pyproject.toml',
    'src/dataforge/__init__.py',
    'src/dataforge/core/config.py',
    'src/dataforge/ingestion/readers.py',
    'src/dataforge/ingestion/headers.py',
    'src/dataforge/quality/profiler.py',
    'src/dataforge/transformation/cleaner.py',
    'src/dataforge/transformation/converters.py',
    'src/dataforge/export/writer.py',
    'src/dataforge/orchestration/pipeline.py',
    'src/dataforge/interfaces/desktop.py',
    'src/dataforge/interfaces/cli.py',
    'scripts/verificar_instalacao.py',
)


def main():
    missing = [name for name in REQUIRED if not (ROOT / name).is_file()]
    if missing:
        print('Projeto incompleto. Arquivos ausentes:')
        for name in missing:
            print(' - ' + name)
        print('Extraia novamente o ZIP completo em uma pasta nova.')
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
