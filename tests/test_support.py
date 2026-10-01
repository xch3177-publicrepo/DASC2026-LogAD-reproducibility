"""New synthetic checks, not benchmark experiments or archived run results."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from reconstruct_tables import verify
from scan_public import scan_text
from table_support import group, markdown


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SupportTests(unittest.TestCase):
    def test_balanced_groups(self):
        self.assertEqual(group('{outer{inner}}tail', 0), ('outer{inner}', 14))
        with self.assertRaises(ValueError):
            group('{unfinished', 0)

    def test_tables_match(self):
        data = json.loads((ROOT / 'published_tables/tables.json').read_text())
        ledger = json.loads((ROOT / 'published_tables/numeric_ledger.json').read_text())
        self.assertEqual(verify(data, ledger), (ROOT / 'published_tables/reconstructed_tables.md').read_text())

    def test_table_tamper_rejected(self):
        data = json.loads((ROOT / 'published_tables/tables.json').read_text())
        ledger = json.loads((ROOT / 'published_tables/numeric_ledger.json').read_text())
        altered = copy.deepcopy(data)
        altered['tables'][0]['rows'][2]['cells'][1]['text'] = '575,062'
        with self.assertRaises(ValueError):
            verify(altered, ledger)

    def test_scanner_reports_only_type_and_line(self):
        synthetic = 'prefix\n' + 'ghp_' + 'a' * 30
        findings = scan_text(synthetic)
        self.assertIn(('github-token', 2), findings)
        self.assertNotIn('a' * 30, repr(findings))
        self.assertEqual(scan_text('ordinary public documentation'), [])

    def test_drain_synthetic_masks(self):
        module = load('legacy_drain', ROOT / 'legacy_baseline/src/drain.py')
        parser = module.Drain()
        a = parser.add_line('service accepted request 10')
        b = parser.add_line('service accepted request 11')
        self.assertEqual(a, b)
        self.assertEqual(parser.template_str(a), 'service accepted request <*>')
        self.assertEqual(parser.clusters[a].count, 2)

    def test_cli_help_and_opt_in(self):
        command = [sys.executable, '-B', str(ROOT / 'tools/run_legacy.py')]
        self.assertEqual(subprocess.run(command + ['--help'], capture_output=True).returncode, 0)
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('--allow-full-run is required', result.stderr)


@unittest.skipUnless(importlib.util.find_spec('numpy') and importlib.util.find_spec('pandas'),
                     'optional synthetic preprocessing tests require NumPy and Pandas')
class SyntheticPreprocessingTests(unittest.TestCase):
    def test_synthetic_hdfs_and_bgl(self):
        import numpy as np
        with tempfile.TemporaryDirectory(prefix='.smoke-', dir=ROOT) as directory:
            work = Path(directory)
            raw = work / 'raw'
            hdfs = raw / 'HDFS_v1/preprocessed'
            hdfs.mkdir(parents=True)
            (hdfs / 'HDFS.log_templates.csv').write_text('EventId,EventTemplate\nE1,service accepted request <*>\nE2,service failed request <*>\n')
            (hdfs / 'Event_traces.csv').write_text('Label,Features\nSuccess,"[E1,E1]"\nFail,"[E1,E2]"\n')
            bgl = raw / 'BGL'
            bgl.mkdir()
            lines = []
            for i in range(200):
                label = 'ALERT' if i == 155 else '-'
                lines.append(label + ' t n d n type component level id synthetic message ' + str(i) + '\n')
            (bgl / 'BGL.log').write_text(''.join(lines))
            env = dict(os.environ, LOGAD_RAW_ROOT=str(raw), LOGAD_PROC_DIR=str(work / 'proc'), PYTHONDONTWRITEBYTECODE='1')
            for name in ('build_hdfs.py', 'build_bgl.py'):
                subprocess.run([sys.executable, '-B', str(ROOT / 'legacy_baseline/src' / name)], env=env, capture_output=True, check=True)
            self.assertEqual(np.load(work / 'proc/hdfs_labels.npy').tolist(), [0, 1])
            self.assertEqual(np.load(work / 'proc/hdfs_counts.npy').tolist(), [[2, 0], [1, 1]])
            self.assertEqual(np.load(work / 'proc/bgl_labels.npy').tolist(), [0, 1])
            self.assertEqual(np.load(work / 'proc/bgl_counts.npy').sum(axis=1).tolist(), [100, 100])

    def test_semantic_synthetic_vectors(self):
        import numpy as np
        module = load('legacy_features', ROOT / 'legacy_baseline/src/log_features.py')
        class ToyEmbedding:
            wv = {'service': np.array([1., 0.]), 'request': np.array([0., 1.])}
        vectors = module.template_embeddings(['service request', 'unknown'], ToyEmbedding(), 2)
        np.testing.assert_allclose(vectors, [[.5, .5], [0., 0.]])
        np.testing.assert_allclose(module.session_semantic(np.array([[2, 0], [0, 1]]), vectors), vectors)


if __name__ == '__main__':
    unittest.main()
