"""Valida caminho, versão instalada e imports necessários à execução."""
from importlib.metadata import version
from pathlib import Path
import dataforge
import pandas  # noqa: F401
import openpyxl  # noqa: F401
from dataforge.orchestration.pipeline import run  # noqa: F401
from dataforge.transformation.converters import convert_series  # noqa: F401

root = Path(__file__).resolve().parent.parent
expected = root / 'src' / 'dataforge' / '__init__.py'
if Path(dataforge.__file__).resolve() != expected or version('dataforge-local') != dataforge.__version__:
    raise SystemExit(1)
