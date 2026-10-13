# SPDX-License-Identifier: GPL-3.0-or-later
"""Linked private trust storage stays bounded and empty before declaration filling."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('base_trust_storage_builder',
    ROOT / 'sdk/machines/octatrack/elekloader/build_core.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def fixture():
    start, load, run = 0x40a955e0, 0x40000400, 0x40000500
    image = bytearray(256 + 1696)
    image[256:976] = b'MWMD' + bytes((1, 0, 16)) + bytes(713)
    image[976:] = b'MWTD' + bytes((1, 0, 16)) + bytes(969)
    return image, {'modwerk_machine_declarations': start,
                   'modwerk_table_declarations': start + 720}, \
        {'ddr': [start, start + 1696], 'run_load': run}, load


class TrustStorage(unittest.TestCase):
    def test_complete_linked_reservations_and_unused_records(self):
        image, mapping, layout, load = fixture()
        proof = builder.check_trust_storage(image, mapping, layout, load)
        self.assertEqual([entry['bytes'] for entry in proof.values()], [720, 976])
        self.assertTrue(all(entry['count'] == 0 for entry in proof.values()))
        for at in (256, 261, 262, 975, 976, 981, 1951):
            changed = bytearray(image)
            changed[at] ^= 1
            with self.subTest(offset=at), self.assertRaises(ValueError):
                builder.check_trust_storage(changed, mapping, layout, load)

    def test_missing_symbols_uninitialized_storage_and_truncation_are_refused(self):
        image, mapping, layout, load = fixture()
        for changed in ({}, dict(mapping, modwerk_machine_declarations=True),
                        dict(mapping, modwerk_table_declarations=layout['ddr'][1]),
                        dict(mapping, modwerk_table_declarations=layout['ddr'][0] + 718),
                        dict(mapping, modwerk_table_declarations=layout['ddr'][0])):
            with self.subTest(mapping=changed), self.assertRaises(ValueError):
                builder.check_trust_storage(image, changed, layout, load)
        with self.assertRaises(ValueError):
            builder.check_trust_storage(image[:-1], mapping, layout, load)
        for changed in ({}, dict(layout, ddr=[layout['ddr'][0]]),
                        dict(layout, run_load=True), dict(layout, run_load=load - 1)):
            with self.subTest(layout=changed), self.assertRaises(ValueError):
                builder.check_trust_storage(image, mapping, changed, load)


if __name__ == '__main__':
    unittest.main()
