# SPDX-License-Identifier: GPL-3.0-or-later
"""The base edition of the startup animation (sdk/runtime/startup/base.json): the NEW and version
particles, the LED show and its time step. Authored data and the encoder only; no firmware."""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import unittest

ROOT = Path(__file__).resolve().parents[2]
STARTUP = ROOT / 'sdk/runtime/startup'
spec = importlib.util.spec_from_file_location('startup_build', STARTUP / 'build.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)
EDITION = json.loads((STARTUP / 'base.json').read_text())
ART = json.loads((STARTUP / 'artwork.json').read_text())


def sha(data):
    return hashlib.sha256(data).hexdigest()


def records(data):
    return [struct.unpack_from('>hhh', data, 6 * i) for i in range(len(data) // 6)]


def shown(x, y):
    """The stock renderer's final display pixel of a record."""
    return 63 + x, 21 - y


def lamp_waves(table):
    """What the boot loop computes per lamp from its stock-format (x, y): channel A and B phase."""
    rs = lambda v: (v + (1023 if v < 0 else 0)) >> 10
    return [(rs(y - x - 8200), rs(x + y - 25800)) for x, y in (struct.unpack_from('>ii', table, 8 * i) for i in range(len(table) // 8))]


def levels(phase, d2):
    """The loop at time d2 (5 ms units) with the base's one-step shift instead of three."""
    s = int((d2 - 192) / 2)
    return max(0, 15 - abs(phase + s))


class PublicStartupTests(unittest.TestCase):
    def test_default_writes_are_unchanged(self):
        recorded = json.loads((ROOT / 'docs/media/startup/verification.json').read_text())['writes']
        got = build.writes()
        self.assertEqual([sha(data) for _, data in got], [w['replacementSha256'] for w in recorded])
        self.assertEqual([g['address'] for g, _ in got], [w['address'] for w in recorded])


class BaseTextTests(unittest.TestCase):
    def setUp(self):
        self.writes = build.writes('0.3.1')
        self.particles = records(self.writes[0][1])

    def test_record_count_and_extra_writes(self):
        self.assertEqual(len(self.particles), ART['particles'])
        self.assertEqual([g['address'] for g, _ in self.writes[2:]], [EDITION['guards'][k]['address'] for k in ('mkii', 'mki', 'stepRound', 'stepShift', 'wordmarkY')])

    def test_text_sits_beside_the_mark_and_below_the_wordmark(self):
        text, pixels = build.text_points(EDITION, '0.3.1')
        mark = ART['mark']
        dy = EDITION['layout']['dy']
        ink = {(mark['x'] + x, mark['y'] + dy + y) for y, row in enumerate(mark['rows']) for x, c in enumerate(row) if c == '#'}
        landed = {shown(x, y) for x, y, _ in self.particles}
        self.assertEqual(landed, ink | pixels)
        self.assertEqual(len([p for p in pixels if p[0] < 47]) + len([p for p in pixels if p[0] > 80]), len(pixels), 'NEW and the version flank the mark')
        self.assertTrue(any(p[0] < 47 for p in pixels) and any(p[0] > 80 for p in pixels))
        self.assertTrue(all(y <= 60 for _, y in pixels), 'the stock renderer moves the bottom three rows')
        # white space: the lowered mark and wordmark keep clear of the screen edges
        shown_ink = build.authored_ink(ART, dy)
        self.assertGreaterEqual(min(y for _, y in shown_ink), 4)
        self.assertGreaterEqual(63 - max(y for _, y in shown_ink), 6)

    def test_the_wordmark_row_moves_with_the_mark(self):
        guard, data = [w for w in self.writes if w[0] is EDITION['guards']['wordmarkY'] or w[0] == EDITION['guards']['wordmarkY']][0]
        self.assertEqual(struct.unpack('>H', data)[0], 10 - EDITION['layout']['dy'])

    def test_every_particle_lands_before_the_loop_ends(self):
        for _, _, delay in self.particles:
            self.assertLessEqual(512 - delay, 559 - 8)

    def test_version_is_checked(self):
        for bad in ('0.3', '0.3.1-dev', 'x'):
            with self.assertRaises(ValueError):
                build.writes(bad)
        with self.assertRaises(ValueError):
            build.writes('0.10.100')   # wider than the space beside the mark

    def test_a_longer_version_shortens_the_tail_instead_of_overflowing(self):
        for version in ('0.4.0', '0.10.1', '9.9.9'):
            data = build.writes(version)[0][1]
            self.assertEqual(len(data), ART['particles'] * 6)


class BaseLedTests(unittest.TestCase):
    def test_tables_match_their_guards(self):
        for key, lamps in (('mkii', 67), ('mki', 44)):
            self.assertEqual(len(EDITION['led'][key]), lamps)
            self.assertEqual(EDITION['guards'][key]['bytes'], lamps * 8)
        for guard in EDITION['guards'].values():
            self.assertEqual(len(guard['sha256']), 64)
        for words in EDITION['stepWords'].values():
            self.assertEqual(len(bytes.fromhex(words)), 2)

    def test_each_channel_peaks_at_its_authored_time_and_ends_dark(self):
        for key in ('mkii', 'mki'):
            waves = lamp_waves(build.lamp_table(EDITION['led'][key]))
            for (red, green), (pa, pb) in zip(EDITION['led'][key], waves):
                for ms, phase in ((red, pa), (green, pb)):
                    series = [levels(phase, d2) for d2 in range(0, 560)]
                    self.assertEqual(max(series), 15)
                    # the loop truncates toward zero, so a negative step can reach 15 one tick early
                    self.assertIn(series.index(15) * 5, (ms - 5, ms))
                    self.assertEqual(series[559], 0, 'nothing is left lit when the loop ends')

    def test_the_show_follows_the_animation(self):
        red = [a for a, _ in EDITION['led']['mkii']]
        tracks = red[20:28]
        self.assertEqual(tracks, sorted(set(tracks)), 'T1-T8 follow the tiles locking in')
        self.assertEqual(red[42], max(red), 'REC is the last light, with the detached tile')
        self.assertGreater(red[42], tracks[-1])
        # the converging wave ends at the middle of the panel, no later than the frame closing
        self.assertLessEqual(max(g for _, g in EDITION['led']['mkii']), 1300)
        self.assertEqual([a for a, _ in EDITION['led']['mki'][20:28]], tracks, 'MKI has the same tile cues')
        self.assertEqual(EDITION['led']['mki'][42][0], red[42])


if __name__ == '__main__':
    unittest.main()
