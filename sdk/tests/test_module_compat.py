# SPDX-License-Identifier: GPL-3.0-or-later
"""Cross-compatibility gate (scripts/module-compat.py) on synthetic manifests: no firmware, no stock bytes."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('module_compat', ROOT / 'scripts/module-compat.py')
gate = importlib.util.module_from_spec(spec); spec.loader.exec_module(gate)
from remix.schema import Detour, Kind, MenuEntry, Module  # noqa: E402  (the gate put sdk/octabam/tools on the path)

SITE, EVENT = 0x40002318, dict(event='ev_test', site='0x40004100', length=8)


def module(name, *sites, fx=None):
    """A synthetic ColdFire module detouring 8 bytes at each site (placeholder guard bytes, not stock)."""
    return Module(name=name, key=name.upper(), kind=Kind.CF_PATCH, doc='synthetic',
                  detours=tuple(Detour(s, bytes(8), name, 'hook', pad_to=8) for s in sites),
                  menu=MenuEntry(fx, 0, b'T', b'TEST') if fx else None)


def relation(pair, kind='group-owned', sites=(SITE,), **extra):
    return dict(modules=list(pair), kind=kind, reason='synthetic review', sites=[f'0x{s:08x}' for s in sites],
                **({'owner': pair[0]} if kind == 'group-owned' else {}), **extra)


class GateTests(unittest.TestCase):
    def routes(self, problems):
        return sorted((tuple(p['modules']), p['route']) for p in problems)

    def test_clean_pair(self):
        self.assertEqual(gate.check([module('a', 0x40001000), module('b', 0x40001008)]), [])

    def test_overlapping_detours_name_both_modules_the_range_and_the_event_route(self):
        problems = gate.check([module('a', SITE), module('b', SITE + 4)])
        self.assertEqual(self.routes(problems), [(('a', 'b'), 'event')])
        self.assertIn('0x4000231c', problems[0]['text'])
        self.assertIn('0x40002318..0x4000231f', problems[0]['text'])

    def test_copy_under_another_modules_patch_is_install_order_dependent(self):
        problems = gate.check([module('a', SITE), module('b')], copies={'b': [(0x4000230e, 13, 'recipe copy')]})
        self.assertEqual(self.routes(problems), [(('a', 'b'), 'copy')])
        self.assertRegex(problems[0]['text'], r'^b copies stock bytes 0x4000230e\.\.0x4000231a .*a patches')
        # The same bytes from an unpatched location compose.
        self.assertEqual(gate.check([module('a', SITE), module('b')], copies={'b': [(0x4003886a, 13, 'x')]}), [])

    def test_base_sites_refuse_modules_unless_the_base_owns_them(self):
        base = [(SITE, 6, 'code')]
        self.assertEqual(self.routes(gate.check([module('a', SITE)], base_sites=base)), [(('a',), 'event')])
        self.assertEqual(gate.check([module('a', SITE)], base_sites=base, base_owns={'a': 'reviewed'}), [])

    def test_group_owned_overlap_is_allowed_at_exactly_its_sites(self):
        modules = [module('a', SITE), module('b', SITE)]
        self.assertEqual(gate.check(modules, relations=[relation(('a', 'b'))]), [])
        moved = [module('a', SITE, 0x40001000), module('b', SITE, 0x40001000)]
        self.assertEqual(self.routes(gate.check(moved, relations=[relation(('a', 'b'))])), [(('a', 'b'), 'event')])

    def test_stale_relations_fail(self):
        modules = [module('a', SITE), module('b')]
        for entry, text in ((relation(('a', 'gone')), 'no longer an active module'),
                            (relation(('a', 'b')), 'nothing meets at 0x40002318'),
                            (dict(relation(('a', 'b')), reason=' '), 'needs two modules')):
            with self.subTest(text=text):
                problems = gate.check(modules, relations=[entry])
                self.assertEqual([p['route'] for p in problems], ['relation'])
                self.assertIn(text, problems[0]['text'])

    def test_event_sites_belong_to_the_base_and_name_the_event(self):
        problems = gate.check([module('a', 0x40004100)], events=[EVENT])
        self.assertEqual(self.routes(problems), [(('a',), 'subscribe')])
        self.assertIn('which is the event ev_test', problems[0]['text'])

    def test_pending_migration_allows_both_modules_until_they_subscribe(self):
        modules = [module('a', 0x40004100), module('b', 0x40004100)]
        pending = relation(('a', 'b'), 'pending-migration', (0x40004100,), event='ev_test', until='both subscribe')
        self.assertEqual(gate.check(modules, events=[EVENT], relations=[pending]), [])
        self.assertIn('not in sdk/machines/octatrack/events.json',
                      gate.check(modules, events=[], relations=[pending])[0]['text'])
        third = gate.check(modules + [module('c', 0x40004100)], events=[EVENT], relations=[pending])
        self.assertEqual({p['route'] for p in third}, {'subscribe', 'event'})
        self.assertTrue(all('c' in p['modules'] for p in third))

    def test_a_subscription_that_replaces_its_detour_claims_nothing(self):
        modules = [module('a', 0x40004100), module('b', 0x40004100)]
        subs = {'a': [dict(event='ev_test', fn='f', order=20, replaces='hook')],
                'b': [dict(event='ev_test', fn='g', order=50, replaces='hook')]}
        self.assertEqual(gate.check(modules, events=[EVENT], subscriptions=subs), [])
        pending = relation(('a', 'b'), 'pending-migration', (0x40004100,), event='ev_test', until='both subscribe')
        stale = gate.check(modules, events=[EVENT], relations=[pending], subscriptions=subs)
        self.assertEqual([p['route'] for p in stale], ['relation'])  # nothing patches there any more: the entry must go
        self.assertIn('nothing meets at 0x40004100', stale[0]['text'])
        raised = {'a': [dict(event='ev_raised', fn='f', order=50)]}  # a raised event owns no stock bytes
        self.assertEqual(self.routes(gate.check(modules[:1], events=[EVENT], subscriptions=raised)), [(('a',), 'subscribe')])
        # One still patching: it alone meets the base's event site.
        self.assertEqual(self.routes(gate.check(modules, events=[EVENT], subscriptions={'a': subs['a']})),
                         [(('b',), 'subscribe')])
        for entry, text in ((dict(subs['a'][0], replaces='nothing'), 'which is not its detour'),
                            (dict(subs['a'][0], event='ev_unknown'), 'not a site event')):
            with self.subTest(text=text):
                problems = gate.check([module('a', 0x40004100)], events=[EVENT], subscriptions={'a': [entry]})
                self.assertTrue(any(text in p['text'] for p in problems))

    def test_pinned_effect_id_collision_names_another_chooser_row(self):
        problems = gate.check([module('a', fx=0x1e), module('b', fx=0x1e)])
        self.assertEqual(self.routes(problems), [(('a', 'b'), 'row')])

    def test_repository_passes(self):
        ids, modules, inputs, problems = gate.repository_inputs()
        self.assertEqual(problems + gate.check(modules, **inputs), [])
        self.assertGreaterEqual(len(modules), 20)

    def test_windows_linked_paths_give_the_same_findings(self):
        # Windows manifests carry backslash sources; octabam's composition signature splits on "modules/".
        from dataclasses import replace
        ids, modules, inputs, problems = gate.repository_inputs()
        windows = [replace(m, linked=tuple(replace(u, source=str(u.source).replace('/', '\\')) for u in m.linked))
                   for m in modules]
        self.assertTrue(any('\\' in str(u.source) for m in windows for u in m.linked))
        self.assertEqual(gate.check(windows, **inputs), gate.check(modules, **inputs))



def mod(name, *sites, release='1.0', claims=(), regions=()):
    """A synthetic elemod mod patching 6 bytes at each site in one OS release (placeholder hashes, not stock)."""
    build = dict(releases={release: dict(sites=[dict(addr=f'0x{a:08x}', len=6, stockSha256='0' * 64) for a in sites])},
                 regions=[dict(name=n, lo=f'0x{lo:08x}', hi=f'0x{hi:08x}') for n, lo, hi in regions])
    return gate.elemod_declarations('dt', dict(id=name, platform=dict(claims=list(claims))), build)


class ElemodGateTests(unittest.TestCase):
    def routes(self, problems):
        return sorted((tuple(p['modules']), p['route']) for p in problems)

    def test_clean_pair(self):
        self.assertEqual(gate.check_elemod('dt', [mod('a', 0x40001000), mod('b', 0x40001006)]), [])

    def test_shared_stock_bytes_route_to_a_core_event(self):
        problems = gate.check_elemod('dt', [mod('a', 0x40001000), mod('b', 0x40001004)])
        self.assertEqual(self.routes(problems), [(('dt/a', 'dt/b'), 'core-event')])
        self.assertIn('0x40001004', problems[0]['text'])

    def test_different_os_releases_never_meet(self):
        self.assertEqual(gate.check_elemod('dt', [mod('a', 0x40001000), mod('b', 0x40001000, release='2.0')]), [])

    def test_claims_are_exclusive_and_core_claims_belong_to_the_core(self):
        problems = gate.check_elemod('dt', [mod('a', claims=['machine:4', 'timer:DTIM0']), mod('b', claims=['machine:4'])],
                                     core=dict(claims=['timer:DTIM0']))
        self.assertEqual(self.routes(problems), [(('dt/a',), 'claim'), (('dt/a', 'dt/b'), 'claim')])

    def test_regions_meet_in_every_release(self):
        problems = gate.check_elemod('dt', [mod('a', regions=[('copy', 0x80000000, 0x80000100)]),
                                            mod('b', release='2.0', regions=[('buffer', 0x800000f0, 0x80000200)])])
        self.assertEqual(self.routes(problems), [(('dt/a', 'dt/b'), 'other')])

    def test_pending_event_allows_listed_sites_and_goes_stale(self):
        relation = dict(modules=['a', 'b'], kind='pending-event', event=['ev_test'], until='the core owns it',
                        reason='synthetic review', sites=['0x40001000'])
        pair = [mod('a', 0x40001000), mod('b', 0x40001000)]
        self.assertEqual(gate.check_elemod('dt', pair, relations=[relation]), [])
        problems = gate.check_elemod('dt', [mod('a', 0x40001000), mod('b', 0x40002000)], relations=[relation])
        self.assertEqual(self.routes(problems), [(('dt/a', 'dt/b'), 'relation')])
        self.assertIn('nothing meets', problems[0]['text'])
        for broken in (dict(relation, kind='group-owned'), dict(relation, until=''), dict(relation, modules=['a', 'gone'])):
            with self.subTest(broken=broken):
                self.assertTrue(any(p['route'] == 'relation' for p in gate.check_elemod('dt', pair, relations=[broken])))

    def test_repository_passes(self):
        machines = gate.elemod_inputs()
        self.assertIn('digitakt', [m['machine'] for m in machines])
        self.assertGreaterEqual(sum(len(m['mods']) for m in machines), 10)
        for m in machines:
            with self.subTest(machine=m['machine']):
                self.assertEqual(gate.check_elemod(m['machine'], m['mods'], m['core'], m['relations']), [])


if __name__ == '__main__':
    unittest.main()
