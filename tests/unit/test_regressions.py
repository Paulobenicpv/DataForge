import tempfile
import unittest
from pathlib import Path
import pandas as pd
from dataforge.ingestion.readers import read_table
from dataforge.transformation.cleaner import transform
from dataforge.orchestration.pipeline import run

class PipelineTests(unittest.TestCase):
    def test_identifiers_and_literal_na(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'x.csv'
            p.write_text('id;uf\n00123;NA\n', encoding='utf-8')
            df, _ = read_table(p)
            out, _ = transform(df, {})
            self.assertEqual(out.iloc[0].tolist(), ['00123', 'NA'])
    def test_invalid_conversion_preserves_column(self):
        df = pd.DataFrame({'data': ['01/01/2026', 'erro']}, dtype='string')
        out, audit = transform(df, {'conversions': {'data': {'type': 'date', 'format': '%d/%m/%Y'}}})
        self.assertEqual(out['data'].tolist(), df['data'].tolist())
        self.assertEqual(audit['conversion_errors'][0]['invalid_cells'], 1)
    def test_locale_number_and_dedupe_opt_in(self):
        df = pd.DataFrame({'v': ['1.234,50', '1.234,50']}, dtype='string')
        out, _ = transform(df, {'conversions': {'v': {'type': 'number', 'decimal': ',', 'thousands': '.'}}})
        self.assertEqual(len(out), 2)
        self.assertEqual(float(out.iloc[0, 0]), 1234.5)
    def test_header_collisions(self):
        df = pd.DataFrame([['a', 'b', 'c']], columns=['A', 'a', 'a_2'], dtype='string')
        out, _ = transform(df, {'normalize_headers': True})
        self.assertEqual(len(set(out.columns)), 3)
    def test_malformed_csv_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'x.csv'
            p.write_text('a;b\n1;2\n3\n')
            with self.assertRaises(ValueError):
                read_table(p, separator=';')
    def test_xlsx_and_output_integrity(self):
        with tempfile.TemporaryDirectory() as d:
            p, output = Path(d) / 'x.xlsx', Path(d) / 'out'
            pd.DataFrame({'id': ['00123'], 'nome': [' Paulo ']}).to_excel(p, index=False)
            original = p.read_bytes()
            report = run(p, output)
            self.assertEqual(report['after']['rows'], 1)
            self.assertEqual(p.read_bytes(), original)
            cleaned, _ = read_table(output / 'dados_tratados.csv')
            self.assertEqual(cleaned.iloc[0].tolist(), ['00123', 'Paulo'])
            with self.assertRaises(ValueError):
                run(p, output)
    def test_invalid_config_fails(self):
        with self.assertRaises(ValueError):
            transform(pd.DataFrame({'a': ['x']}), {'drop_duplicates': 'false'})

if __name__ == '__main__':
    unittest.main()
