# SPDX-License-Identifier: GPL-3.0-or-later
"""Private AB lease source: reviewed ABI, strong imports, fallback outside the lease."""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
ADAPTER = ROOT / 'sdk/machines/octatrack/module-adapters'
SDK = ROOT / 'sdk/octabam'
sys.path.append(str(ADAPTER))
import analog_bd_write_lease as lease


def selected(mask, quantizer=False):
    sys.path.insert(0, str(SDK / 'tools'))
    from remix import registry
    old = Path.cwd()
    try:
        os.chdir(SDK)
        return [registry._load_one(SDK / ('modules/' + name + '/manifest.py'))
                for name in ['analog-bassdrum', *[n for n, bit in [('poly8', 1), ('vector', 2), ('synth', 4)] if mask & bit],
                             *(['quantizer'] if quantizer else [])]]
    finally:
        os.chdir(old)


class AnalogBdWriteLeaseTests(unittest.TestCase):
    def test_strong_imports_only_and_fallback_outside_lease(self):
        original = (SDK / 'modules/analog-bassdrum/control.c').read_text()
        text = lease.source(original)
        begin = text.index('modwerk_controller_write_begin(')
        end = text.index('modwerk_controller_write_end(')
        self.assertLess(text.index('0x40004008u'), begin)
        self.assertLess(begin, text.index('++ab_render_calls;'))
        self.assertLess(text.index('U32(0x80001c80u)=(uint32_t)'), end)
        self.assertIn('#include "stock_hook_write_lease.h"', text)
        self.assertIn('MW_CONTROLLER_WRITE_ANALOG_BD,&lease)!=1) return -1;', text)
        self.assertIn('return modwerk_controller_write_end(&lease)==1 ? 0 : -1;', text)
        self.assertNotIn('__attribute__((weak))', text)
        self.assertNotIn('mw_controller_control_write_allowed', text)
        self.assertEqual(hashlib.sha256(lease.HEADER.read_bytes()).hexdigest(), lease.HEADER_SHA256)
        with self.assertRaisesRegex(ValueError, 'source changed'):
            lease.source(original + '\n')

    @unittest.skipUnless(shutil.which('m68k-elf-gcc'), 'native ColdFire toolchain required')
    def test_every_composition_leaves_exactly_the_two_lease_imports(self):
        import analog_bd_composition
        for mask, quantizer in [(m, False) for m in range(8)] + [(m, True) for m in range(1, 4)]:
            with self.subTest(mask=mask, quantizer=quantizer), tempfile.TemporaryDirectory() as temp:
                folder = Path(temp)
                result = analog_bd_composition.effective_modules(selected(mask, quantizer), SDK, folder / 'source', lease=True)
                if mask & 4:
                    import fm_runtime
                    result = [fm_runtime.port(m, SDK, folder / 'fm', composition=True) if m.name == 'synth' else m for m in result]
                if quantizer:
                    import quantizer_runtime
                    result = [quantizer_runtime.port(m, SDK, folder / 'qz') if m.name == 'quantizer' else m for m in result]
                objects = []
                for index, unit in enumerate(u for m in result for u in m.linked):
                    obj = folder / (str(index) + '.o')
                    source = Path(unit.source)
                    subprocess.run(['m68k-elf-as', '-mcpu=54455', str(source if source.is_absolute() else SDK / source), '-o', str(obj)],
                                   cwd=SDK, check=True, capture_output=True)
                    if unit.exports:
                        subprocess.run(['m68k-elf-objcopy', *['--globalize-symbol=' + n for n in unit.exports], str(obj)], check=True, capture_output=True)
                    objects.append(obj)
                script, elf = folder / 'link.ld', folder / 'linked.elf'
                script.write_text('SECTIONS { . = 0; .text : { *(.text*) *(.rodata*) *(.data*) } .bss : { *(.bss*) *(COMMON) } /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame) } }')
                relocatable = folder / 'linked.o'
                subprocess.run(['m68k-elf-ld', '-r', '-o', str(relocatable), *map(str, objects)], check=True, capture_output=True)
                # Weak presence checks may stay unresolved; strong imports are only the lease.
                undefined = [line.split() for line in subprocess.check_output(['m68k-elf-nm', '-u', str(relocatable)], text=True).splitlines()]
                self.assertEqual(sorted(name for kind, name in undefined if kind == 'U'), sorted(lease.IMPORTS))
                imports = ['--defsym=modwerk_controller_write_begin=0x47410000', '--defsym=modwerk_controller_write_end=0x47410100']
                subprocess.run(['m68k-elf-ld', '--no-warn-rwx-segments', *imports, '-T', str(script), '-o', str(elf), *map(str, objects)],
                               check=True, capture_output=True)
                symbols = subprocess.check_output(['m68k-elf-nm', str(elf)], text=True)
                self.assertNotIn(' U ', symbols)
                self.assertNotIn(' B ', symbols)


if __name__ == '__main__':
    unittest.main()
