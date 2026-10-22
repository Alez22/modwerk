# SPDX-License-Identifier: GPL-3.0-or-later
"""ABI 9 packages in the published list: the publication builder reads them, and its host entry point refuses any
`requires` bit but the key bus, the only one the site accepts (module-set.ts BASE_DSP_FEATURES). Synthetic: a published
ABI 6 package made ABI 9 by abi9.py; no firmware."""
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


abi9 = load('test_mp_abi9', ROOT / 'sdk/runtime/loader/abi9.py')
builder = load('test_mp_builder', ROOT / 'sdk/machines/octatrack/elekloader/module_packages.py')
entry = load('test_mp_entry', ROOT / 'scripts/octatrack-module-packages.py')
EVERB = (ROOT / 'public/octatrack-modules/everb/0.1.2-experimental.mwrm').read_bytes()
CLAIMS = [abi9.parse_claim(c) for c in ('y:0:r:0x800:0x200', 'y:1:r:0x800:0x200', 'y:0:r:0x33dfe:0x202', 'y:1:r:0x3bdfe:0x202')]


class PublishedAbi9(unittest.TestCase):
    def test_a_reader_reads_as_abi_9_with_its_requires_and_claims(self):
        data = abi9.upgrade(EVERB, abi9.base_features(['keybus']), CLAIMS)
        self.assertEqual(builder.capabilities(data), dict(abi=9, features=0, sites=0, copies=0, fills=0, requires=8, claims=4))
        self.assertEqual(entry.only_key_bus(builder.capabilities)(data)['requires'], 8)
        self.assertEqual(builder.capabilities(EVERB), dict(abi=6, features=0, sites=0, copies=0, fills=0))  # unchanged

    def test_any_other_base_feature_is_refused_before_it_reaches_the_list(self):
        checked = entry.only_key_bus(builder.capabilities)
        for names in (['sidechain'], ['matrix'], ['analog-bd'], ['keybus', 'sidechain']):
            with self.subTest(names=names):
                data = abi9.upgrade(EVERB, abi9.base_features(names))
                with self.assertRaisesRegex(ValueError, 'only the key bus'):
                    checked(data)

    def test_hook_entries_are_never_published(self):
        data = abi9.upgrade(EVERB, abi9.base_features(['keybus']), entries=[(0, 3, 0)])
        with self.assertRaises(ValueError):
            builder.capabilities(data)

    def test_an_abi_10_engine_reads_with_its_entries_and_its_words_are_scanned(self):
        """A base-bound controller's engine (hook_engines.py): its entry count in the manifest, and its words and
        initial words both in the stock-free scan."""
        controller = (ROOT / 'public/octatrack-modules/analog-bassdrum/0.1.5-experimental.mwrm').read_bytes()
        words, init = [0x111111 + i for i in range(8)], [0x222222 + i for i in range(5)]
        words[5] = 0x0d10c0
        data = abi9.engine(controller, words, [1 | 0x8000], 5, 3, 6, [('x', 2, 0x2840, init)])
        found = builder.capabilities(data)
        self.assertEqual((found['abi'], found['requires'], found['claims'], found['entries']), (10, 0, 1, 1))
        self.assertEqual({k: v for k, v in found.items() if k not in ('abi', 'requires', 'claims', 'entries')},
                         {k: v for k, v in builder.capabilities(controller).items() if k != 'abi'})
        big, little = builder.dsp_words(data)
        self.assertEqual(big, b''.join(w.to_bytes(3, 'big') for w in words + init))
        self.assertEqual(little, b''.join(w.to_bytes(3, 'little') for w in words + init))
        # What a trust row pins stays with the controller: another engine, the same digest.
        other = abi9.engine(controller, [0] + words[1:], [1 | 0x8000], 5, 3, 6, [('x', 2, 0x2840, init[:3])])
        self.assertEqual(abi9.controller_sha256(other), abi9.controller_sha256(data))
        self.assertNotEqual(abi9.controller_sha256(abi9.engine(controller[:-1] + b'\x01', words, [1 | 0x8000], 5, 3, 6,
                                                                [('x', 2, 0x2840, init)])), abi9.controller_sha256(data))


if __name__ == '__main__':
    unittest.main()
