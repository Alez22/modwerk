#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Cross-compatibility gate: every module must install beside every other on its machine.

    npm run modules:compat                 # every active module, every pair and the whole set
    npm run modules:compat -- <id>         # only what involves <id>
    npm run modules:compat -- --json       # the same, machine-readable (module:doctor reads it)

Reads declarations only, through octabam's claim model (manifests, the loader integration's port recipes
when present, the committed base package): no firmware, no emulator. Shared behaviour goes through events,
as in Elekloader (docs/ADAPTING.md, rule 4): the base owns each event's stock site and modules subscribe
to it. Two owners may meet on stock bytes only where sdk/machines/octatrack/compatibility.json names both
modules and the address with a reason; the base's own exceptions are build_core.py's BASE_OWNS. Everything
else octabam's ledger refuses (FX ids, DSP hooks, core-private Y, buffer regions, data ranges) is checked
for every pair and for the whole active set.

Every elemod machine (Digitakt, Digitone and the others with an elemod SDK) is checked by the same rules from
its mods' modwerk.module.json and build.json: no two mods patch the same stock bytes in a release they share,
claim the same named resource or region, or claim a resource the core owns. Two mods may meet only where
sdk/machines/<machine>/compatibility.json lists them as pending-event: the core does not yet own that site as
an event both can subscribe to. Elemod problems name modules as <machine>/<id>.
"""
import ast
import itertools
import json
import re
import sys
import time
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP / 'sdk/octabam/tools'))
GUIDE = 'docs/module-guides/README.md#cross-compatibility'
RELATIONS = 'sdk/machines/octatrack/compatibility.json'
EVENTS = 'sdk/machines/octatrack/events.json'
RECIPES = ('sdk/machines/octatrack/module-adapters/standalone-recipes.json',
           'sdk/machines/octatrack/module-adapters/candidate-recipes.json')
BASE = 'the Modwerk base'
PROBE = 0x400D7000  # ledger.check's probe address for a floating cave's emit pokes
ROUTES = {
    'subscribe': ('the base owns this event site: subscribe a handler to the event (subscribe: event, fn, '
                  'order in the module\'s runtime.json) instead of patching it', '#events'),
    'event': ('two behaviour hooks meet on this stock site: request a new event (one reviewed entry in '
              'sdk/machines/octatrack/events.json), then subscribe to it instead of patching', '#propose-an-event'),
    'site': ('one owner per byte: patch other bytes, or request a new event if you need the same behaviour',
             '#propose-an-event'),
    'cave': ('pick free space nobody else claims, or let the build place the unit (a floating Linked unit)',
             '#cross-compatibility'),
    'table': ('this stock table already has an owner: request a new event or a shared table instead of '
              'relocating it again', '#propose-an-event'),
    'copy': ('copy these stock bytes from an unpatched location (identical bytes elsewhere in stock)',
             '#cross-compatibility'),
    'row': ('pick another chooser row (a free effect ID)', '#cross-compatibility'),
    'other': ('claim a resource nobody else uses, or request a base-owned region or event for shared state',
              '#cross-compatibility'),
    'relation': (f'correct {RELATIONS} (sdk/machines/<machine>/compatibility.json for other machines); every '
                 'entry needs owner review', '#cross-compatibility'),
    'core-event': ('two mods patch the same stock site: the core should own it as an event or table both subscribe '
                   'to; propose it, and until the core has it, list the pair in sdk/machines/<machine>/'
                   'compatibility.json as pending-event (owner review)', '#propose-an-event'),
    'claim': ('a named resource has one owner: claim another one, or ask for the core to own it and share it '
              'through an event or table', '#cross-compatibility'),
}
# octabam ledger findings this gate already compares by exact byte range (with relations), not by message.
SPAN_FINDINGS = ('ColdFire cave', 'hook site', 'poke site', 'kept bytes', 'grown table')
HOOKS = ('detour', 'hook', 'base code')  # code sites: behaviour hooks
NOT_WRITES = ('keep', 'copy')


def claims(m):
    """(kind, start, length, label) for what one module writes, owns, keeps or copies from stock."""
    from remix import ledger
    out = list(m.write_spans())
    out += [('linked unit', u.cave_addr, 6, u.label) for u in m.linked if u.cave_addr is not None]
    for c in m.cf_patches:
        if c.emit is not None:
            out += [('emit poke', a, max(len(e), len(w)), c.label)
                    for a, e, w in c.emit(c.cave_addr if c.cave_addr is not None else PROBE)[1]]
    if m.runtime is not None:
        out += [('runtime write', a, n, label) for a, n, label in ledger.runtime_write_spans(m)]
    out += [('table', t.old, 4 * t.count, t.label) for t in m.tables]
    out += [('keep', k.addr, len(k.expect), k.note or 'kept stock bytes') for k in m.keeps]
    out += [('copy', c.span.address, len(c.span), f'{u.label}:{c.symbol}') for u in m.linked for c in u.stock_copies]
    return out


def span(start, length):
    return f'0x{start:08x}..0x{start + length - 1:08x}'


def route(x, y):
    """Which route fixes this meeting of two claims, or None when they compose (reads beside reads)."""
    kinds = {x[0], y[0]}
    if kinds <= set(NOT_WRITES):
        return None
    if 'copy' in kinds:
        return 'copy'
    if 'event' in kinds:
        return 'subscribe'
    if 'table' in kinds:
        return 'table'
    if kinds & {'cave', 'linked unit'} and 'keep' not in kinds:
        return 'cave'
    return 'event' if kinds <= set(HOOKS) else 'site'


def overlaps(owners):
    """Every meeting of two owners' claims: (a, x, b, y, address, route). owners: {name: claims}."""
    for (a, ca), (b, cb) in itertools.combinations(sorted(owners.items()), 2):
        for x in ca:
            for y in cb:
                if x[1] < y[1] + y[2] and y[1] < x[1] + x[2] and route(x, y):
                    yield a, x, b, y, max(x[1], y[1]), route(x, y)


def describe(a, x, b, y, at, way):
    if way == 'copy':
        (c, cn), (p, pn) = ((x, a), (y, b)) if x[0] == 'copy' else ((y, b), (x, a))
        return (f'{cn} copies stock bytes {span(c[1], c[2])} ({c[3]}), but {pn} patches {span(p[1], p[2])} '
                f'({p[0]} {p[3]}): the copy depends on install order')
    if way == 'subscribe':
        (e, _), (p, pn) = ((x, a), (y, b)) if x[0] == 'event' else ((y, b), (x, a))
        return (f'{pn} patches {span(p[1], p[2])} ({p[0]} {p[3]}), which is the event {e[3]} '
                f'({span(e[1], e[2])}): subscribe to it in runtime.json instead of patching')
    return f'{a} ({x[0]} {x[3]}, {span(x[1], x[2])}) and {b} ({y[0]} {y[3]}, {span(y[1], y[2])}) both claim 0x{at:08x}'


def ledger_findings(selected, platform):
    """octabam's ledger on these modules (+ the platform modules they bridge), minus byte-range findings."""
    from dataclasses import replace
    from remix import ledger
    need = {o.module for m in selected for o in m.overrides} | {k for m in selected for k in m.requires}
    # Kept bytes are compared above; the ledger would read stock to compare two keeps.
    # Linked sources as POSIX paths: octabam's composition signature splits them on "modules/" (Windows has "\").
    posix = lambda m: replace(m, linked=tuple(replace(u, source=str(u.source).replace('\\', '/')) for u in m.linked))
    modules = [posix(replace(m, keeps=())) for m in selected] + [posix(platform[k]) for k in sorted(need) if k in platform]
    try:
        problems = ledger.check(modules)
    except (ValueError, SystemExit) as error:
        problems = [f'composition: {error}']
    return [p for p in problems if p.split(':', 1)[0] not in SPAN_FINDINGS]


def check(modules, base_sites=(), events=(), copies=None, relations=(), base_owns=(), platform=None, subscriptions=None):
    """Problems for these active modules: [{'modules': [...], 'text': str, 'route': str}].

    modules: octabam Module objects (all active); base_sites: (start, length, kind) the base patches;
    events: registry entries {event, site, length}; copies: {module name: [(address, length, label)]}
    from port recipes and packages; relations: the reviewed entries; base_owns: modules allowed on base sites;
    subscriptions: {module name: its runtime.json entries}. A detour a subscription `replaces` stays out of the
    module's loader package (sdk/runtime/loader/build.py replaced()), so it claims nothing here."""
    problems, names = [], {m.name for m in modules}
    owners = {m.name: claims(m) for m in modules}
    by_event = {e['event']: e for e in events}
    for m in modules:
        for entry in (subscriptions or {}).get(m.name, ()):
            if 'replaces' not in entry:  # nothing it patched goes (a raised event owns no stock bytes either)
                continue
            e = by_event.get(entry.get('event'))
            if not e:
                problems.append(dict(modules=[m.name], text=f'{m.name} replaces {entry["replaces"]} for '
                                     f'{entry.get("event")}, which is not a site event in {EVENTS}', route='event'))
                continue
            site = int(e['site'], 16)
            if not any(d.symbol == entry['replaces'] and d.site == site and (d.pad_to or 6) == e['length']
                       for d in m.detours):
                problems.append(dict(modules=[m.name], text=f'{m.name}\'s runtime.json replaces {entry["replaces"]}, '
                                     f'which is not its detour at {e["event"]}\'s site 0x{site:08x}', route='subscribe'))
                continue
            owners[m.name] = [c for c in owners[m.name] if not (c[0] == 'detour' and c[1] == site)]
    for name, items in (copies or {}).items():
        if name in owners:
            owners[name] += [('copy', a, n, label) for a, n, label in items]
    owners[BASE] = [('base ' + kind, a, n, 'site') for a, n, kind in base_sites]
    owners[BASE] += [('event', int(e['site'], 16), e['length'], e['event']) for e in events]
    known_events = {e['event'] for e in events}

    def problem(involved, text, way):
        problems.append(dict(modules=sorted(set(involved) & names), text=text, route=way))

    allowed, pending, used = {}, set(), set()
    for entry in relations:
        pair, sites, kind = entry.get('modules', []), entry.get('sites', []), entry.get('kind')
        if (len(pair) != 2 or pair[0] == pair[1] or not str(entry.get('reason', '')).strip() or not sites
                or (kind, bool(entry.get('owner')), bool(entry.get('event') and entry.get('until')))
                not in (('group-owned', True, False), ('pending-migration', False, True))):
            problem(pair, f'relation {pair}: needs two modules, a reason, its sites and a kind: group-owned (with '
                          f'the owner) or pending-migration (with the event and until)', 'relation')
            continue
        stale = [n for n in [*pair, *([entry['owner']] if entry.get('owner') else [])] if n not in names]
        if stale:
            problem(pair, f'relation {"+".join(pair)} names {", ".join(stale)}, which is no longer an active '
                          f'module: remove the entry', 'relation')
            continue
        if kind == 'pending-migration' and entry['event'] not in known_events:
            problem(pair, f'relation {"+".join(pair)} waits for {entry["event"]}, which is not in {EVENTS}',
                    'relation')
            continue
        for site in sites:
            allowed[(frozenset(pair), int(site, 16))] = entry
            if kind == 'pending-migration':  # until both subscribe, they may still patch the event's site
                pending |= {(n, int(site, 16)) for n in pair}
    for a, x, b, y, at, way in overlaps(owners):
        if BASE in (a, b):
            module, base_claim = (b, x) if a == BASE else (a, y)
            if (module, at) in pending or (base_claim[0] != 'event' and module in base_owns):
                continue
            problem((module,), describe(a, x, b, y, at, way) + ('' if way == 'subscribe' else f'; {BASE} patches it'),
                    way)
        elif (frozenset((a, b)), at) in allowed:
            used.add((frozenset((a, b)), at))
        else:
            problem((a, b), describe(a, x, b, y, at, way), way)
    for key, entry in allowed.items():
        if key not in used:
            problem(key[0], f'relation {"+".join(entry["modules"])}: nothing meets at 0x{key[1]:08x} any more; '
                            f'remove the site', 'relation')
    for a, b in itertools.combinations(modules, 2):
        for text in ledger_findings([a, b], platform or {}):
            problem((a.name, b.name), text, 'row' if text.startswith('fx2 id') else 'other')
    seen = {p['text'] for p in problems}
    for text in ledger_findings(list(modules), platform or {}):
        if text not in seen:
            problem([n for n in names if re.search(rf'\b{re.escape(n)}\b', text)], f'whole set: {text}',
                    'row' if text.startswith('fx2 id') else 'other')
    return problems


def active_ids():
    """Catalogue modules the library offers (beta included), as src/catalog/availability.ts decides."""
    source = (APP / 'src/catalog/availability.ts').read_text()
    lists = {}
    for name in ('BETA_MODULE_IDS', 'PAUSED_MODULE_IDS'):
        found = re.search(rf'export const {name}: readonly string\[\] = \[([^\]]*)\]', source)
        if not found:
            raise SystemExit(f'src/catalog/availability.ts: cannot read {name}; update scripts/module-compat.py')
        lists[name] = set(re.findall(r"'([^']+)'", found.group(1)))
    catalog = json.loads((APP / 'sdk/catalog.json').read_text())['modules']
    return [row['id'] for row in catalog
            if row['id'] not in lists['PAUSED_MODULE_IDS'] or row['id'] in lists['BETA_MODULE_IDS']]


def read_events():
    # an event a module raises (site null) owns no stock bytes: nothing to compare
    events = [e for e in json.loads((APP / EVENTS).read_text())['events'] if e.get('site') is not None]
    if not all(isinstance(e.get('event'), str) and re.fullmatch(r'0x[0-9a-fA-F]{8}', str(e.get('site')))
               and type(e.get('length')) is int and e['length'] > 0 for e in events):
        raise SystemExit(f'{EVENTS}: every event needs event (its name), site (0x… stock address) and length; '
                         f'update read_events() in scripts/module-compat.py if the registry changed shape')
    return events


def repository_inputs():
    """Everything check() needs, read from this checkout. Problems loading a manifest are returned, not raised."""
    from remix import registry
    ids, load = active_ids(), []
    try:
        known = registry.modules()
    except (ValueError, SystemExit) as error:  # the registry refuses duplicate keys and FX ids by name
        text = str(error)
        return ids, [], {}, [dict(modules=[i for i in ids if re.search(rf'\b{re.escape(i)}\b', text)], text=text,
                                  route='row' if 'FX2 id' in text else 'other')]
    by_name = {m.name: m for m in known.values()}
    platform = {m.key: m for m in known.values() if m.name in registry.PLATFORM_NAMES}
    for i in ids:
        if i not in by_name:
            load.append(dict(modules=[i], text=f'{i} is in the catalogue but has no sdk/octabam/modules/{i}/manifest.py',
                             route='other'))
    base = json.loads((APP / 'src/engine/assets/octatrack-base.elemod').read_text())
    copies = {}
    for path in RECIPES:  # the loader integration's runtime ports; absent on branches without them
        if (APP / path).exists():
            for name, recipe in json.loads((APP / path).read_text())['ports'].items():
                rows = recipe.get('copies', []) + [c for t in recipe.get('tables', []) for c in t.get('copies', [])]
                copies.setdefault(name, []).extend((c['address'], c['length'], f'{Path(path).name} copy') for c in rows)
    for layout in json.loads((APP / 'src/engine/assets/usb-audio-packages.json').read_text())['layouts']:
        copies.setdefault('usb-audio-out-' + layout['id'], []).extend(
            (c['source'], c['bytes'], f'{o["label"]}:{c["section"]}') for o in layout['objects'] for c in o.get('stockCopies', []))
    owns = next(node.value for node in ast.parse((APP / 'sdk/machines/octatrack/elekloader/build_core.py').read_text()).body
                if isinstance(node, ast.Assign) and any(getattr(t, 'id', '') == 'BASE_OWNS' for t in node.targets))
    subscriptions = {}
    for i in ids:
        path = APP / 'sdk/octabam/modules' / i / 'runtime.json'
        if path.is_file():
            subscriptions[i] = json.loads(path.read_text()).get('subscribe', [])
    inputs = dict(base_sites=[(int(s['addr'], 16), s['len'], s['kind']) for s in base['sites']], events=read_events(),
                  subscriptions=subscriptions,
                  copies=copies, relations=json.loads((APP / RELATIONS).read_text())['relations'],
                  base_owns=ast.literal_eval(owns), platform=platform)
    return ids, [by_name[i] for i in ids if i in by_name], inputs, load


def elemod_declarations(machine, document, build):
    """What a mod changes, from its manifest and build spec: (release or None, start, end, label) spans and claims."""
    spans = []
    for release, value in build.get('releases', {}).items():
        spans += [(release, int(site['addr'], 16), int(site['addr'], 16) + site['len'], f'site {site["addr"]}')
                  for site in value.get('sites', [])]
    derive = build.get('derive') or {}
    for release in derive.get('releases', []):
        spans += [(release, int(site['addr'], 16), int(site['addr'], 16) + site['len'], f'call site {site["addr"]}')
                  for site in derive.get('callSites', [])]
    spans += [(None, int(r['lo'], 16), int(r['hi'], 16), f'region {r["name"]}') for r in build.get('regions', [])]
    spans += [(None, a, b, f'{c["to"]} entry') for c in build.get('contribute', []) for a, b in c.get('claims', [])]
    return dict(name=f'{machine}/{document["id"]}', spans=spans, claims=list(document['platform'].get('claims', [])))


def check_elemod(machine, mods, core=None, relations=()):
    """Problems among one elemod machine's mods: shared stock bytes, regions or claims, and claims of core resources."""
    problems, names = [], {m['name'] for m in mods}

    def problem(involved, text, way):
        problems.append(dict(modules=sorted(set(involved) & names), text=text, route=way))

    allowed, used = {}, set()
    for entry in relations:
        pair = [f'{machine}/{n}' for n in entry.get('modules', [])]
        if (len(pair) != 2 or pair[0] == pair[1] or entry.get('kind') != 'pending-event' or not entry.get('sites')
                or not all(str(entry.get(k, '')).strip() for k in ('event', 'until', 'reason'))):
            problem(pair, f'relation {"+".join(pair)}: needs two mods, its sites, a reason and kind pending-event '
                          f'with the planned event and until', 'relation')
            continue
        stale = [n for n in pair if n not in names]
        if stale:
            problem(pair, f'relation {"+".join(pair)} names {", ".join(stale)}, which is no longer a mod: remove '
                          f'the entry', 'relation')
            continue
        for site in entry['sites']:
            allowed[(frozenset(pair), int(site, 16))] = entry
    core_claims = set((core or {}).get('claims', []))
    for m in mods:
        for claim in sorted(set(m['claims']) & core_claims):
            problem((m['name'],), f'{m["name"]} claims {claim}, which the {machine} core owns', 'claim')
    for a, b in itertools.combinations(mods, 2):
        for claim in sorted(set(a['claims']) & set(b['claims'])):
            problem((a['name'], b['name']), f'{a["name"]} and {b["name"]} both claim {claim}', 'claim')
        met = {}
        for ra, xa, ya, la in a['spans']:
            for rb, xb, yb, lb in b['spans']:
                if (ra is None or rb is None or ra == rb) and xa < yb and xb < ya:
                    met.setdefault(max(xa, xb), []).append((ra or rb, la, lb))
        for at, where in sorted(met.items()):
            key = (frozenset((a['name'], b['name'])), at)
            if key in allowed:
                used.add(key)
                continue
            releases = sorted({r for r, _, _ in where if r})
            _, la, lb = where[0]
            problem((a['name'], b['name']), f'{a["name"]} ({la}) and {b["name"]} ({lb}) both patch 0x{at:08x}'
                    + (f' in OS {", ".join(releases)}' if releases else ''),
                    'core-event' if la.startswith(('site', 'call site')) and lb.startswith(('site', 'call site')) else 'other')
    for key, entry in allowed.items():
        if key not in used:
            problem(key[0], f'relation {"+".join(sorted(key[0]))}: nothing meets at 0x{key[1]:08x} any more; '
                            f'remove the site', 'relation')
    return problems


def elemod_inputs():
    """Each elemod machine's mods, core interface and reviewed relations, read through its machine profile."""
    machines = []
    for profile_path in sorted((APP / 'sdk/machines').glob('*/machine.json')):
        profile = json.loads(profile_path.read_text())
        sdk = profile.get('sdk') or {}
        if sdk.get('platform') != 'elemod' or not (APP / sdk['modules']).is_dir():
            continue
        core_file = APP / (sdk.get('core') or {}).get('path', '') / 'interface.json'
        mods = []
        for folder in sorted(f for f in (APP / sdk['modules']).iterdir() if f.is_dir() and not f.name.startswith('_')):
            if (folder / 'modwerk.module.json').is_file():
                document = json.loads((folder / 'modwerk.module.json').read_text())
                build = json.loads((folder / document['platform']['build']).read_text())
                mods.append(elemod_declarations(profile['id'], document, build))
        relations_file = profile_path.parent / 'compatibility.json'
        machines.append(dict(machine=profile['id'], mods=mods,
                             core=json.loads(core_file.read_text()) if core_file.is_file() else None,
                             relations=json.loads(relations_file.read_text())['relations'] if relations_file.is_file() else []))
    return machines


def main(argv):
    started = time.perf_counter()
    as_json, only = '--json' in argv, [a for a in argv if not a.startswith('--')]
    ids, modules, inputs, problems = repository_inputs()
    if modules:
        problems += check(modules, **inputs)
    machines = elemod_inputs()
    for m in machines:
        problems += check_elemod(m['machine'], m['mods'], m['core'], m['relations'])
    if only:
        problems = [p for p in problems if set(only) & set(p['modules'])]
    for p in problems:
        p['fix'], anchor = ROUTES[p['route']]
        p['guide'] = GUIDE.split('#')[0] + anchor
    summary = dict(active=len(ids), pairs=len(ids) * (len(ids) - 1) // 2, relations=len(inputs.get('relations', [])),
                   events=len(inputs.get('events', [])), problems=len(problems),
                   seconds=round(time.perf_counter() - started, 2), notActive=[i for i in only if i not in ids],
                   pending=[dict(modules=r['modules'], event=r['event'], until=r['until'])
                            for r in inputs.get('relations', []) if r.get('kind') == 'pending-migration']
                   + [dict(modules=[f'{m["machine"]}/{n}' for n in r.get('modules', [])], event=r.get('event'),
                           until=r.get('until')) for m in machines for r in m['relations']],
                   machines=[dict(machine=m['machine'], mods=len(m['mods']), relations=len(m['relations']))
                             for m in machines])
    if as_json:
        print(json.dumps(dict(problems=problems, summary=summary)))
    else:
        for p in problems:
            print('✗ ' + p['text'])
            print('    fix: ' + p['fix'] + ' (' + p['guide'] + ')')
        for i in summary['notActive']:
            print(f'· {i} is not an active catalogue module (paused or unlisted), so it is not compared')
        for m in (m for m in summary['machines'] if m['mods']):
            print(f"Cross-compatibility: {m['mods']} {m['machine']} mods, {m['mods'] * (m['mods'] - 1) // 2} pairs, "
                  f"{m['relations']} reviewed relations")
        print(f"Cross-compatibility: {summary['active']} active Octatrack modules, {summary['pairs']} pairs and the "
              f"whole set, {summary['events']} events, {summary['relations']} reviewed relations; "
              f"{len(problems)} problem(s) in {summary['seconds']}s")
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
