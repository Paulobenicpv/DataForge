"""Regressões da inicialização, dos conversores e dos arquivos distribuídos."""
from decimal import Decimal
from pathlib import Path
import json
import runpy
import subprocess
import sys
import tempfile
import unittest
import pandas as pd
from dataforge.orchestration.pipeline import run
from dataforge.transformation.cleaner import transform

ROOT = Path(__file__).resolve().parents[2]


class ReleaseFixTests(unittest.TestCase):
    def test_launcher_and_installation_checker_are_present(self):
        self.assertTrue((ROOT / 'INICIAR.bat').is_file())
        self.assertTrue((ROOT / 'scripts/verificar_instalacao.py').is_file())
        checker = subprocess.run([sys.executable, str(ROOT / 'scripts/verificar_projeto.py')],
                                 capture_output=True, text=True, check=False)
        self.assertEqual(checker.returncode, 0, checker.stdout + checker.stderr)

    def test_missing_converter_is_reported_before_install(self):
        verifier = ROOT / 'scripts/verificar_projeto.py'
        namespace = runpy.run_path(str(verifier))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in namespace['REQUIRED']:
                if name.endswith('/converters.py'):
                    continue
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch()
            script = root / 'scripts/verificar_projeto.py'
            script.write_text(verifier.read_text(encoding='utf-8'), encoding='utf-8')
            process = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, check=False)
            self.assertEqual(process.returncode, 1)
            self.assertIn('src/dataforge/transformation/converters.py', process.stdout)

    def test_decimal_precision(self):
        frame = pd.DataFrame({'valor': ['9007199254740993.123456789']}, dtype='string')
        out, audit = transform(frame, {'conversions': {'valor': {'type': 'number'}}})
        self.assertEqual(out.loc[0, 'valor'], Decimal('9007199254740993.123456789'))
        self.assertFalse(audit['conversion_errors'])

    def test_invalid_thousands_group_is_preserved(self):
        frame = pd.DataFrame({'valor': ['12.34,50']}, dtype='string')
        out, audit = transform(frame, {'conversions': {'valor': {
            'type': 'number', 'decimal': ',', 'thousands': '.'}}})
        self.assertEqual(out.loc[0, 'valor'], '12.34,50')
        self.assertEqual(audit['conversion_errors'][0]['invalid_cells'], 1)

    def test_export_keeps_time_and_fraction(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'base.csv'
            source.write_text('data;id\n24/10/2026 10:25:37.123456;001\n', encoding='utf-8')
            run(source, root / 'out', {'conversions': {'data': {
                'type': 'date', 'format': '%d/%m/%Y %H:%M:%S.%f'}}})
            text = (root / 'out/dados_tratados.csv').read_text(encoding='utf-8-sig')
            self.assertIn('10:25:37.123456', text)
            self.assertIn(';001', text)

    def test_windows_json_bom(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, config, output = root / 'base.csv', root / 'config.json', root / 'out'
            source.write_text('id;nome\n001; Ana \n', encoding='utf-8')
            config.write_text(json.dumps({'trim': True}), encoding='utf-8-sig')
            process = subprocess.run([sys.executable, '-m', 'dataforge', str(source),
                                      '--config', str(config), '--output', str(output)],
                                     capture_output=True, text=True, check=False)
            self.assertEqual(process.returncode, 0, process.stderr)
