# SPDX-License-Identifier: GPL-3.0-or-later
"""Stock-free, unwired task-root preparation; no complete Part collector."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'sdk/machines/octatrack/module-adapters/analog-bd-parts'
class AnalogBdPartRoots(unittest.TestCase):
    @unittest.skipUnless(shutil.which('cc') or shutil.which('gcc'),'native C compiler unavailable')
    def test_bounded_actual_layout_refusals_aliases_and_no_complete_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            binary=Path(tmp)/'part-roots'
            subprocess.run([shutil.which('cc') or shutil.which('gcc'),'-std=c99','-O2','-Wall','-Wextra','-Werror',
                '-DMODWERK_AB_COLLECT_HOST',SOURCE/'part_roots.c',SOURCE/'test_part_roots.c','-o',binary],
                check=True,capture_output=True)
            result=subprocess.run([binary],check=True,text=True,capture_output=True)
            self.assertIn('PASS bounded AB root preparation',result.stdout)
            self.assertIn('semantic end unknown',result.stdout)
    @unittest.skipUnless(shutil.which('m68k-elf-gcc'),'ColdFire compiler unavailable')
    def test_coldfire_compiles_with_actual_sr_read_and_no_mask_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            obj=Path(tmp)/'roots.o'
            subprocess.run(['m68k-elf-gcc','-mcpu=54455','-msoft-float','-Os','-ffreestanding','-fno-builtin',
                '-Wall','-Wextra','-Werror','-c',SOURCE/'part_roots.c','-o',obj],check=True,capture_output=True)
            text=subprocess.check_output(['m68k-elf-objdump','-d',obj],text=True)
            self.assertIn('%sr,',text)
            self.assertNotRegex(text,r'move\w*\s+[^\n]*,%sr')
            self.assertNotIn('mw_ab_collect_test_sr',text)
