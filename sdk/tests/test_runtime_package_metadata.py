# SPDX-License-Identifier: GPL-3.0-or-later
"""Runtime catalogue capability metadata follows bounded authored package headers."""
import importlib.util
from pathlib import Path
import struct
import unittest
import hashlib
import json
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('runtime_packages', ROOT / 'sdk/machines/octatrack/elekloader/module_packages.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class PackageMetadataTests(unittest.TestCase):
    def test_base_rebind_preserves_unrelated_published_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp);public = root / 'public';public.mkdir()
            (root / 'sdk/machines/octatrack').mkdir(parents=True)
            (root / 'sdk/catalog.json').write_text(json.dumps({'modules': [{'id': 'other', 'version': '1'}, {'id': 'bound', 'version': '1'}]}))
            (root / 'sdk/machines/octatrack/base-binding.json').write_text(json.dumps({'identity': 'ab' * 32}))
            other = public / 'other.mwrm';other.write_bytes(b'preserved published image')
            original = {'id': 'other', 'path': other.name, 'bytes': other.stat().st_size, 'sha256': hashlib.sha256(other.read_bytes()).hexdigest()}
            manifest = root / 'manifest.json';manifest.write_text(json.dumps({'packages': [original, {'id': 'bound', 'base': True}]}))
            dsp = root / 'dsp.json';dsp.write_text('{"packages":[]}')
            data = self.header();struct.pack_into('>I', data, 28, 2);data[50:55] = b'BOUND'
            with patch.object(builder, 'APP', root), patch.object(builder, 'PUBLIC', public), patch.object(builder, 'MANIFEST', manifest), patch.object(builder, 'DSP', dsp), patch.object(builder, 'tools', return_value=True), patch.object(builder, 'build', return_value=bytes(data)) as build, patch('sys.argv', ['packages', '--base-only']):
                with self.assertRaises(SystemExit) as result:
                    builder.main()
                self.assertEqual(result.exception.code, 0)
                self.assertEqual(build.call_count, 1)
                self.assertEqual(build.call_args.args[0]['id'], 'bound')
            self.assertEqual(other.read_bytes(), b'preserved published image')
            entries = json.loads(manifest.read_text())['packages']
            self.assertEqual(entries[0], original)
            self.assertEqual(entries[1]['requiredBase'], 'ab' * 32)
            self.assertEqual((public / entries[1]['path']).read_bytes(), data)

    def header(self, abi=8, flags=0, sites=0, copies=0, fills=0, hooks=0):
        data = bytearray(76)
        struct.pack_into('>4sHH', data, 0, b'MWRM', abi, flags)
        struct.pack_into('>II', data, 20, hooks, sites)
        struct.pack_into('>II', data, 68, copies, fills)
        return data

    def test_record_types_require_their_base_features(self):
        self.assertEqual(builder.capabilities(self.header(abi=6)), dict(abi=6, features=0, sites=0, copies=0, fills=0))
        self.assertEqual(builder.capabilities(self.header(abi=7, sites=15, copies=1)), dict(abi=7, features=3, sites=15, copies=1, fills=0))
        self.assertEqual(builder.capabilities(self.header(flags=4, sites=85, copies=20, fills=2)), dict(abi=8, features=31, sites=85, copies=20, fills=2))

    def test_site_event_subscribers_require_the_events_feature(self):
        data = self.header(hooks=5, sites=13) + struct.pack('>5I', *[0xffffffff] * 4, 50 << 24 | 0x40)
        self.assertEqual(builder.capabilities(data), dict(abi=8, features=129, sites=13, copies=0, fills=0))
        for data in (self.header(abi=7, hooks=5) + struct.pack('>5I', *[0xffffffff] * 4, 0x40),  # ABI 8 only
                     self.header(hooks=5)):  # truncated hook words
            with self.subTest(data=bytes(data[:8])), self.assertRaises(ValueError):
                builder.capabilities(data)

    def test_unsupported_or_truncated_headers_fail_closed(self):
        for data in (self.header(abi=4), self.header()[:71], self.header(abi=6, sites=1),
                     self.header(hooks=1), self.header(flags=8), self.header(abi=7, flags=4),
                     self.header(sites=129), self.header(copies=129), self.header(fills=65), bytes(76)):
            with self.subTest(data=data[:8]), self.assertRaises(ValueError):
                builder.capabilities(data)

    def test_dsp_scan_accepts_abi8_but_refuses_impossible_lengths(self):
        self.assertEqual(builder.dsp_words(self.header()), [b'', b''])
        data = self.header()
        struct.pack_into('>IH', data, 32, 4097, 0)
        with self.assertRaises(ValueError):
            builder.dsp_words(data)


if __name__ == '__main__':
    unittest.main()
