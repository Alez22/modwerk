# SPDX-License-Identifier: MIT
"""The private native consumer tool refuses unsafe outputs and wrong stock early."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / 'sdk/machines/octatrack/module-adapters/probe_fm_consumers.py'


class ConsumerProbePreflight(unittest.TestCase):
    def run_probe(self, work, out, *extra):
        stock = work / 'stock.bin'
        stock.write_bytes(b'not firmware')
        return subprocess.run([sys.executable, '-B', TOOL, '--stock', stock,
                               '--package', work / 'missing.mwrm', '--capture', work / 'missing.json',
                               '--upstream', work / 'missing-upstream', '--native', work / 'missing-native',
                               '--out', out, *extra], capture_output=True, text=True)

    def test_original_stock_identity_is_checked_before_outputs_or_native_compilation(self):
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            out = work / 'private-output'
            result = self.run_probe(work, out)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('exact reviewed original 1.40C', result.stderr)
            self.assertFalse(out.exists())

    def test_stock_derived_outputs_cannot_enter_the_source_checkout(self):
        with tempfile.TemporaryDirectory() as temp:
            result = self.run_probe(Path(temp), ROOT / 'never-write-private-firmware')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('outside the source checkout', result.stderr)
            self.assertFalse((ROOT / 'never-write-private-firmware').exists())

    def test_alternate_source_snapshot_cannot_allow_outputs_in_the_tool_checkout(self):
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            result = self.run_probe(work, ROOT / 'never-write-private-firmware', '--source-root', work)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('outside the source checkout', result.stderr)
            self.assertFalse((ROOT / 'never-write-private-firmware').exists())


if __name__ == '__main__':
    unittest.main()
