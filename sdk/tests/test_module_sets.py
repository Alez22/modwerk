# SPDX-License-Identifier: GPL-3.0-or-later
"""Whole-set persistence with the real C saved-set implementation; no firmware."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class ModuleSetTests(unittest.TestCase):
    def test_saved_set_transaction(self):
        cc = shutil.which('cc')
        if not cc:
            self.skipTest('no host C compiler')
        with tempfile.TemporaryDirectory() as temp:
            subprocess.run([cc, '-std=c99', '-Wall', '-Wextra', '-Werror', '-pedantic', '-DMODWERK_HOST',
                            '-I', ROOT / 'sdk/runtime/upload', '-I', ROOT / 'sdk/runtime/loader',
                            '-I', ROOT / 'sdk/machines/octatrack/elekloader',
                            ROOT / 'sdk/machines/octatrack/elekloader/test_sets.c', '-o', temp + '/test'],
                           check=True, capture_output=True)
            result = subprocess.run([temp + '/test'], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
