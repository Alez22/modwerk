# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure active/saved Part ownership checks; no firmware."""
from pathlib import Path
import hashlib
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1] / 'machines/octatrack/module-adapters'

class MachineParts(unittest.TestCase):
    def test_fm_state_layout_is_bound_to_the_reviewed_authored_engine(self):
        source = ROOT.parents[2] / 'octabam/modules/synth/upstream/synth/poly.s'
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),
                         'ce21f5f7cddcd7268d27e25c500f1403cc59a9dff28044b1832cf2b45592d34c')

    def test_every_ram_sram_part_and_track_is_checked(self):
        cc = shutil.which('cc')
        if not cc:
            self.skipTest('no host C compiler')
        with tempfile.TemporaryDirectory() as work:
            subprocess.run([cc, '-std=c99', '-Wall', '-Wextra', '-Werror', '-pedantic', '-I', ROOT,
                            ROOT / 'machine_parts.c', ROOT / 'test_machine_parts.c', '-o', work + '/parts'],
                           check=True, capture_output=True)
            result = subprocess.run([work + '/parts'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('explicit FM LEG/marker retention', result.stdout)

    def test_coldfire_helper_has_no_runtime_library_imports(self):
        cc,nm=shutil.which('m68k-elf-gcc'),shutil.which('m68k-elf-nm')
        if not cc or not nm:
            self.skipTest('ColdFire compiler required')
        with tempfile.TemporaryDirectory() as work:
            target=Path(work)/'parts.o'
            subprocess.run([cc,'-mcpu=5475','-msoft-float','-O2','-ffreestanding','-fno-builtin',
                            '-Wall','-Wextra','-Werror','-c',ROOT/'machine_parts.c','-o',target],
                           check=True,capture_output=True)
            self.assertNotIn(' U ',subprocess.check_output([nm,target],text=True))
