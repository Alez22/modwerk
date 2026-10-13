# SPDX-License-Identifier: GPL-3.0-or-later
"""Private preparation boundaries; synthetic authored images, no stock fixture."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module
prep = load('runtime_spans', ROOT / 'scripts/prepare-runtime-spans.py')
packages = load('runtime_span_test_packages', ROOT / 'sdk/machines/octatrack/elekloader/module_packages.py')
scanner = load('runtime_span_test_scanner', ROOT / 'sdk/machines/octatrack/elekloader/check_stock_free.py')


class ProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'authored.s'; self.source.write_text('.text\nauthored:\n  nop\n  rts\n')
        self.image = bytes(range(1, 25)) + bytes(8)
        self.sources = {'authored.s': prep.digest(self.source.read_bytes())}
        self.copy = dict(offset=0, length=24, address=0x40001000, sha256=prep.digest(self.image[:24]),
                         purpose='independently assembled synthetic instructions',
                         authored=dict(source='authored.s', lines=[2, 4], symbol='authored', method='native-unit'))
        self.recipe = dict(schema=1, imageSha256=prep.digest(self.image), sources=self.sources, copies=[self.copy], fills=[])
        self.stock_at = lambda address, n: self.image[address - 0x40001000:address - 0x40001000 + n]

    def validate(self, recipe=None, offsets=()):
        prep.validate_review(self.image, offsets, recipe or self.recipe, self.sources, self.root, self.stock_at)

    def test_accepts_exact_authored_provenance_with_actual_matching_stock(self):
        self.validate()

    def test_source_image_span_and_stock_guard_cannot_be_relabeled(self):
        for patch in ({'schema': 2}, {'sources': {}}, {'imageSha256': '0' * 64},
                      {'copies': [{**self.copy, 'sha256': '0' * 64}]},
                      {'copies': [{**self.copy, 'address': 0x40001001}]}):
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                self.validate({**self.recipe, **patch})
        self.source.write_text('.text\nauthored:\n  rts\n')
        with self.assertRaisesRegex(ValueError, 'source'):
            self.validate()

    def test_code_fills_missing_source_and_unreviewed_method_are_refused(self):
        for patch in ({'fills': [dict(offset=0, length=24, value=255)]},
                      {'copies': [{**self.copy, 'purpose': ''}]},
                      {'copies': [{**self.copy, 'authored': {}}]},
                      {'copies': [{**self.copy, 'authored': {**self.copy['authored'], 'lines': [2, 5]}}]},
                      {'copies': [{**self.copy, 'authored': {**self.copy['authored'], 'source': '../authored.s'}}]},
                      {'copies': [{**self.copy, 'authored': {**self.copy['authored'], 'method': 'assumed'}}]}):
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                self.validate({**self.recipe, **patch})

    def test_copy_cannot_overlap_relocations_another_copy_or_image_bounds(self):
        for offsets in ([0], [22]):
            with self.subTest(offsets=offsets), self.assertRaisesRegex(ValueError, 'overlap'):
                self.validate(offsets=offsets)
        for copies in ([self.copy, self.copy], [{**self.copy, 'offset': -1}],
                       [{**self.copy, 'length': 33}], [{**self.copy, 'offset': 20}],
                       [{**self.copy, 'address': 0xfffffff0}]):
            with self.subTest(copies=copies), self.assertRaises(ValueError):
                self.validate({**self.recipe, 'copies': copies})

    def test_private_artifacts_are_exclusive_and_not_in_git(self):
        folder = prep.private_directory(self.root / 'private')
        file = folder / 'proof.json'; prep.save(file, {'synthetic': True})
        self.assertEqual(folder.stat().st_mode & 0o777, 0o700)
        self.assertEqual(file.stat().st_mode & 0o777, 0o600)
        with self.assertRaises(FileExistsError):
            prep.save(file, b'overwrite')
        symlink = folder / 'link'; symlink.symlink_to(self.source)
        with self.assertRaises(FileExistsError):
            prep.save(symlink, b'overwrite')
        with self.assertRaisesRegex(ValueError, 'Git'):
            prep.private_directory(ROOT / 'private-runtime-test' / 'nested')


class StrictScannerTests(unittest.TestCase):
    def scan(self, data, stock, dsp=()):
        class PackageView:
            LIMIT = packages.LIMIT
            runs = staticmethod(packages.runs)
            dsp_words = staticmethod(lambda _: dsp)
        prep.stock_free(data, stock, [('MAIN', stock)], PackageView, scanner)

    def test_both_existing_scanner_thresholds_stay_enforced(self):
        shared = bytes(range(1, 25))
        with self.assertRaisesRegex(ValueError, 'strict'):
            self.scan(b'package' + shared, b'original' + shared)
        # A zero-heavy run escapes the nonzero limit but remains a legacy hit.
        shared = bytes([1, 2, 3, 4, 5]) + bytes(11)
        self.assertFalse(any(n >= packages.LIMIT for n in packages.runs(shared, shared).values()))
        with self.assertRaisesRegex(ValueError, 'strict'):
            self.scan(shared, shared)

    def test_dsp_views_and_new_boundary_matches_cannot_escape_scan(self):
        shared = bytes(range(1, 25))
        with self.assertRaisesRegex(ValueError, 'strict'):
            self.scan(bytes(64), shared, [shared])
        self.scan(bytes(64), shared)

    def test_relocation_oracle_keeps_fixed_stock_addresses_fixed(self):
        import struct
        image = struct.pack('>II', 0x10, 0x40001000)
        shifted = prep.relocated(image, [0], 0x10000)
        self.assertEqual(struct.unpack('>II', shifted), (0x10010, 0x40001000))


if __name__ == '__main__':
    unittest.main()
