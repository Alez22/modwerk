"""Exact imported source and real native controller relocation preparation."""
import importlib.util
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
ADAPTERS = ROOT / 'sdk/machines/octatrack/module-adapters'
sys.path.insert(0, str(ADAPTERS))
import stock_hook_controllers as controllers
spec = importlib.util.spec_from_file_location('stock_hook_controller_builder', ROOT / 'sdk/runtime/loader/build.py')
builder = importlib.util.module_from_spec(spec); spec.loader.exec_module(builder)
SDK = ROOT / 'sdk/octabam'
UPSTREAM = Path.home() / '.cache/modwerk-upstream/elekloader'


class StockHookControllers(unittest.TestCase):
    def test_every_imported_controller_input_is_pinned_and_unknown_modules_refuse(self):
        for name in controllers.UNITS:
            with tempfile.TemporaryDirectory() as tmp:
                sdk = Path(tmp)
                for relative, text in controllers.sources(name, SDK).items():
                    path = sdk / relative; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(text.encode())
                self.assertEqual(controllers.sources(name, sdk), controllers.sources(name, SDK))
                path.write_bytes((text + '\n').encode())
                with self.assertRaisesRegex(ValueError, 'source changed'):
                    controllers.sources(name, sdk)
        for name in ('analog-bassdrum', 'character', '../output-matrix'):
            with self.assertRaisesRegex(ValueError, 'No reviewed'):
                controllers.sources(name, SDK)

    @unittest.skipUnless(shutil.which('m68k-elf-as'), 'ColdFire assembler unavailable')
    def test_actual_authored_reference_and_two_origin_native_reconstruction(self):
        for name in controllers.UNITS:
            for imports in (None, {'modwerk_controller_write_begin': 0x47410000, 'modwerk_controller_write_end': 0x47410100}):
                with tempfile.TemporaryDirectory() as tmp:
                    result = controllers.compile_original(name, SDK, builder, Path(tmp),
                        pool_origins=(0x40c10000, 0x40c20000), fixture_imports=imports)
                    self.assertGreater(len(result['image']), 0)
                    self.assertEqual(len(result['nativePools']), 2)
                    self.assertIsNone(result['encodedSha256'])
                    self.assertFalse(result['productionLeaseBound'])
                    self.assertFalse(result['admission'])
                    self.assertEqual(result['matrixModeLeased'], name == 'output-matrix')

    @unittest.skipUnless(shutil.which('m68k-elf-as'), 'ColdFire assembler unavailable')
    def test_native_adaptation_requires_strong_backend_and_refuses_unqualified_mode_writes(self):
        for name in controllers.UNITS:
            with tempfile.TemporaryDirectory() as tmp:
                source=Path(tmp)/'controller.s'; obj=Path(tmp)/'controller.o'
                source.write_text(controllers.adapted_source(name, SDK))
                subprocess.run(['m68k-elf-as', '-mcpu=54455', source, '-o', obj], check=True, capture_output=True)
                symbols=subprocess.check_output(['m68k-elf-nm',obj],text=True)
                for entry in ('modwerk_controller_write_begin','modwerk_controller_write_end'):
                    self.assertIn(' U '+entry, symbols)
                self.assertNotIn(' W ',symbols)
                text=source.read_text()
                for entry in controllers.UNITS[name][2]:
                    self.assertEqual(text.count('\n%s:\n' % entry), 1)
                    self.assertIn(entry + '_begun:', text); self.assertIn(entry + '_ended:', text)
                if name=='output-matrix':
                    # The authored conversion runs only through the leased entries; its CC
                    # notification and the redraw are outside every held span.
                    body = text[text.index('mw_matrix_mode_body:'):text.index('mw_matrix_notify:')]
                    self.assertNotIn('jsr     MENU_REDRAW', body); self.assertNotIn('jsr     CC_OUT', body)
                    self.assertIn('bsr     convert_all', body)
                    front = text[text.index('set_mode:'):text.index('mw_matrix_mode_body:')]
                    self.assertIn('bsr     matrix_enter', front); self.assertIn('bsr     matrix_leave', front)
        for imports in ({}, {'modwerk_controller_write_begin': 0x08000000, 'modwerk_controller_write_end': 0x47410100}):
            with tempfile.TemporaryDirectory() as tmp:
                with self.assertRaisesRegex(ValueError, 'exact bounded strong'):
                    controllers.compile_original('output-matrix', SDK, builder, Path(tmp), fixture_imports=imports)

    @unittest.skipUnless(shutil.which('m68k-elf-as') and (UPSTREAM / 'elekloader/sdk/octabam.py').is_file(),
                         'ColdFire assembler or Elekloader checkout unavailable')
    def test_encoded_packages_are_base_bound_and_deterministic(self):
        base = {'modwerk_controller_write_begin': 0x41234560, 'modwerk_controller_write_end': 0x41234600}
        for name in controllers.UNITS:
            with tempfile.TemporaryDirectory() as one, tempfile.TemporaryDirectory() as two:
                a = controllers.encode(name, SDK, builder, Path(one), base, UPSTREAM)
                b = controllers.encode(name, SDK, builder, Path(two), base, UPSTREAM)
                self.assertEqual(a['package'], b['package'])
                data = a['package']
                self.assertEqual(data[:4], b'MWRM'); self.assertEqual(struct.unpack('>H', data[4:6])[0], 7)
                self.assertEqual(struct.unpack('>I', data[28:32])[0], builder.module_id(name))
                image = data[76 - 4:]  # ABI 7: 72-byte header, no hooks
                self.assertEqual(struct.unpack('>I', data[8:12])[0], a['imageBytes'])
                # The lease entries are absolute base addresses, never relocated.
                for value in base.values():
                    self.assertIn(struct.pack('>I', value), data)
                rows = controllers.policy_rows(name, a)
                self.assertEqual([r['entryName'] for r in rows], list(controllers.DEFAULT_ENTRIES[name]))
                self.assertIn('{{{0x', controllers.policies_c(rows))
                with tempfile.TemporaryDirectory() as three:
                    moved = controllers.encode(name, SDK, builder, Path(three),
                                               dict(base, modwerk_controller_write_end=0x41234700), UPSTREAM)
                self.assertNotEqual(moved['packageSha256'], a['packageSha256'])
            for bad in ({}, dict(base, modwerk_controller_write_begin=0x41234561),
                        dict(base, modwerk_controller_write_end=base['modwerk_controller_write_begin'])):
                with tempfile.TemporaryDirectory() as tmp, self.assertRaisesRegex(ValueError, 'lease entries'):
                    controllers.encode(name, SDK, builder, Path(tmp), bad, UPSTREAM)
        self.assertNotIn('matrix_enter', controllers.DEFAULT_ENTRIES['output-matrix'])

    def test_trust_rows_refuse_malformed_and_duplicate_rows(self):
        row = dict(module='output-matrix', moduleId=0xcaf158b5, packageSha256='11' * 32, sourcePolicySha256='22' * 32,
                   revisions=[1, 1, 1], feature=2, requiredCores=1, version=1, imageBytes=64, entryName='page_levels',
                   entry=8, beginReturn=16, endReturn=24)
        self.assertEqual(controllers.policies_c([row]).count('\n'), 1)
        for change in (dict(requiredCores=3), dict(feature=4, requiredCores=3), dict(entry=9), dict(endReturn=64),
                       dict(beginReturn=24), dict(packageSha256='00' * 32), dict(revisions=[1, 2, 1]), dict(version=2)):
            with self.assertRaises(ValueError):
                controllers.policies_c([dict(row, **change)])
        with self.assertRaises(ValueError):
            controllers.policies_c([row, dict(row)])
        with self.assertRaises(ValueError):
            controllers.policies_c([dict(row, entry=2 * i) for i in range(1, 27)])


if __name__ == '__main__': unittest.main()
