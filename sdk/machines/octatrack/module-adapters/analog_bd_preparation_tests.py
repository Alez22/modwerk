# SPDX-License-Identifier: MIT
"""Closed private AB/controller preparation, exact imports and native ownership."""
from dataclasses import replace
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import analog_bd_composition as ab_composition
import analog_bd_runtime as ab
import machine_composition as composition

SDK = Path(__file__).resolve().parents[3] / 'octabam'
sys.path.insert(0, str(SDK / 'tools'))
from remix import registry

# Exact ordinary composition: its receipts and group recipes pin this file.
ORDINARY_SHA256 = '4cfa5ae146e1b93c16b478af5882072e3ddefb1bd32960dde577a3f1cb5b3d3e'


def selected(mask, quantizer=False):
    old = Path.cwd()
    try:
        os.chdir(SDK)
        return [registry._load_one(SDK / ('modules/' + name + '/manifest.py'))
                for name in ['analog-bassdrum', *[name for name, bit in [('poly8', 1), ('vector', 2), ('synth', 4)] if mask & bit], *(['quantizer'] if quantizer else [])]]
    finally:
        os.chdir(old)


class SourceTests(unittest.TestCase):
    def test_original_files_are_exact_and_descriptor_writes_removed(self):
        original = (SDK / 'modules/analog-bassdrum/control.c').read_text()
        source = ab.control_source(original)
        self.assertNotIn('U32(0x400d5f38u+5*4)=', source)
        self.assertIn('(void)ab_track_page', source)
        self.assertIn('int ab_render(', source)
        self.assertIn('static uint32_t ab_runtime_bound=0;', source)
        for name, digest in ab.PINS.items():
            self.assertEqual(hashlib.sha256((SDK / 'modules/analog-bassdrum' / name).read_bytes()).hexdigest(), digest)
        with self.assertRaisesRegex(ValueError, 'source changed'):
            ab.control_source(original + '\n')

    def test_private_controller_restores_ab_but_ordinary_variant_is_unchanged(self):
        self.assertEqual(hashlib.sha256(Path(composition.__file__).read_bytes()).hexdigest(), ORDINARY_SHA256)
        for poly in (False, True):
            ordinary = composition.controller_source(SDK, include_poly=poly)
            private = ab_composition.controller_source(SDK, include_poly=poly)
            self.assertNotIn('mr_restore_ab_flex', ordinary)
            self.assertIn('mr_restore_ab_flex', private)
            self.assertIn('result!=(unsigned)-1', private)
            self.assertIn('part[0x22+t]==1 && present(AB)?AB:STOCK', private)
            self.assertNotIn('U32(0x400d5f4cu)=page;', private)
            if not poly:
                self.assertIn("if(s[0]=='A' && s[1]=='B' && s[2]==1) return STOCK;", ordinary)
                self.assertIn('return (kind==AB && ab_type)', private)
                self.assertNotIn('mr_pb_table[mr_row(POLY)]=', private)

    def test_ordinary_ab_compositions_stay_closed_and_private_needs_ab(self):
        for mask in range(1, 8):
            with self.assertRaisesRegex(ValueError, 'Analog BD DSP source port'):
                composition.effective_modules(selected(mask), SDK)
        with tempfile.TemporaryDirectory() as temp, self.assertRaisesRegex(ValueError, 'explicit participant'):
            ab_composition.effective_modules(selected(1)[1:], SDK, temp)
        with self.assertRaisesRegex(ValueError, 'work directory'):
            ab_composition.effective_modules(selected(1), SDK)


@unittest.skipUnless(shutil.which('m68k-elf-gcc'), 'native ColdFire toolchain required')
class NativeTests(unittest.TestCase):
    def test_changed_ab_unit_or_common_hook_is_not_silently_replaced(self):
        bd, poly = selected(1)
        unit = bd.linked[1]
        for changed in [replace(bd, linked=(bd.linked[0], replace(unit, source='unknown.s'), bd.linked[2])),
                        replace(bd, linked=(*bd.linked, unit)),
                        replace(bd, linked=(bd.linked[0], replace(unit, include='unknown'), bd.linked[2]))]:
            with tempfile.TemporaryDirectory() as temp, self.assertRaisesRegex(ValueError, 'declaration drift|once'):
                ab.port(changed, SDK, temp)
        detour = bd.detours[0]
        changed = replace(bd, detours=(replace(detour, symbol='unknown_owner'), *bd.detours[1:]))
        with tempfile.TemporaryDirectory() as temp, self.assertRaisesRegex(ValueError, 'composition seam drift'):
            ab_composition.effective_modules([changed, poly], SDK, temp)

    def test_actual_eleven_private_compositions_one_site_owner_and_no_bss(self):
        variants = [(mask, False) for mask in range(0, 8)] + [(mask, True) for mask in range(1, 4)]
        for mask, quantizer in variants:
            with self.subTest(mask=mask, quantizer=quantizer), tempfile.TemporaryDirectory() as temp:
                folder = Path(temp)
                result = ab_composition.effective_modules(selected(mask, quantizer), SDK, folder / 'source')
                objects = []
                claims = []
                for module in result:
                    claims += [(d.site, d.site + (d.pad_to or 6), module.name) for d in module.detours]
                    claims += [(r.addr, r.addr + 4, module.name) for r in module.symbol_refs]
                    claims += [(p.addr, p.addr + len(p.write), module.name) for p in module.pokes]
                    claims += [(addr, addr + 4, module.name) for t in module.tables for addr, _ in t.refs]
                for previous, current in zip(sorted(claims), sorted(claims)[1:]):
                    self.assertLessEqual(previous[1], current[0], (mask, previous, current))
                bd = next(m for m in result if m.name == 'analog-bassdrum')
                self.assertFalse(bd.detours or bd.symbol_refs or bd.pokes)
                if mask & 4:
                    import fm_runtime
                    result = [fm_runtime.port(m, SDK, folder / 'fm', composition=True) if m.name == 'synth' else m for m in result]
                if quantizer:
                    import quantizer_runtime
                    result = [quantizer_runtime.port(m, SDK, folder / 'qz') if m.name == 'quantizer' else m for m in result]
                for index, unit in enumerate(u for m in result for u in m.linked):
                    obj = folder / (str(index) + '.o')
                    source = Path(unit.source)
                    source = source if source.is_absolute() else SDK / source
                    subprocess.run(['m68k-elf-as', '-mcpu=54455', str(source), '-o', str(obj)], cwd=SDK, check=True, capture_output=True)
                    if unit.exports:
                        subprocess.run(['m68k-elf-objcopy', *['--globalize-symbol=' + name for name in unit.exports], str(obj)], check=True, capture_output=True)
                    objects.append(obj)
                images, maps = [], []
                for origin in (0, 0x21030):
                    script, elf, binary = folder / 'link.ld', folder / 'linked.elf', folder / 'linked.private.raw'
                    script.write_text('SECTIONS { . = ' + hex(origin) + '; .text : { *(.text*) *(.rodata*) *(.data*) } .bss : { *(.bss*) *(COMMON) } /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame) } }')
                    subprocess.run(['m68k-elf-ld', '--no-warn-rwx-segments', '-T', str(script), '-o', str(elf), *map(str, objects)], check=True, capture_output=True)
                    symbols = subprocess.check_output(['m68k-elf-nm', str(elf)], text=True)
                    self.assertNotIn(' U ', symbols)
                    self.assertNotIn(' B ', symbols)
                    maps.append({line.split()[2]: int(line.split()[0], 16) for line in symbols.splitlines() if len(line.split()) == 3})
                    subprocess.run(['m68k-elf-objcopy', '-O', 'binary', str(elf), str(binary)], check=True, capture_output=True)
                    images.append(binary.read_bytes())
                low, high = images
                expected = bytearray(low)
                at = 0
                while at + 4 <= len(low):
                    a, b = int.from_bytes(low[at:at+4], 'big'), int.from_bytes(high[at:at+4], 'big')
                    if b - a == 0x21030 and a < len(low):
                        expected[at:at+4] = b.to_bytes(4, 'big'); at += 4
                    else:
                        at += 2
                self.assertEqual(bytes(expected), high)
                self.assertEqual(maps[0]['desc'] + 916, maps[0]['ab_runtime_bound'])
                self.assertLess(maps[0]['ab_runtime_bound'], len(low))
                for name in ('mr_assign', 'mr_pb_table', 'mr_source_render_impl', 'ab_render', 'ab_desc_p', 'ab_engine_select'):
                    self.assertEqual(maps[1][name], maps[0][name] + 0x21030)
                # AB is an explicit linked participant, never an inferred POLY
                # machine or a substitute for canonical DSP/Part declarations.
                self.assertEqual('pm_assign' in maps[0], bool(mask & 1))


if __name__ == '__main__':
    unittest.main()
