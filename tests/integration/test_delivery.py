"""Testes de publicação, isolamento e entrada pública CLI."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from dataforge.orchestration.pipeline import run


class DeliveryTests(unittest.TestCase):
    def test_cli_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, output = root / 'base.csv', root / 'out'
            source.write_text('id;nome\n001; Ana \n', encoding='utf-8')
            process = subprocess.run(
                [sys.executable, '-m', 'dataforge', str(source), '--output', str(output)],
                capture_output=True, text=True, check=False)
            self.assertEqual(process.returncode, 0, process.stderr)
            report = json.loads((output / 'relatorio.json').read_text(encoding='utf-8'))
            self.assertEqual(report['status'], 'completed')
            self.assertEqual((output / '_SUCCESS').read_text().strip(), report['run_id'])
            self.assertTrue((output / 'execution.log').is_file())

    def test_export_failure_publishes_nothing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, output = root / 'base.csv', root / 'out'
            source.write_text('id;nome\n001;Ana\n', encoding='utf-8')
            with patch('pandas.DataFrame.to_csv', side_effect=OSError('Disco cheio')):
                with self.assertRaises(OSError):
                    run(source, output)
            self.assertFalse(output.exists())
            self.assertEqual(sorted(p.name for p in root.iterdir()), ['base.csv'])

    def test_existing_lock_is_respected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, output = root / 'base.csv', root / 'out'
            source.write_text('id;nome\n001;Ana\n', encoding='utf-8')
            lock = root / '.out.lock'
            lock.touch()
            with self.assertRaises(FileExistsError):
                run(source, output)
            self.assertTrue(lock.exists())
            self.assertFalse(output.exists())

    def test_warnings_visible_in_status(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'base.csv'
            source.write_text('id;data\n001;invalida\n', encoding='utf-8')
            report = run(source, root / 'out', {'conversions': {'data': {'type': 'date', 'format': '%d/%m/%Y'}}})
            self.assertEqual(report['status'], 'completed_with_warnings')
