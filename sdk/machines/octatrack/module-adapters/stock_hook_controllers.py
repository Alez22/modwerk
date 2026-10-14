# SPDX-License-Identifier: GPL-3.0-or-later
"""Private source-pinned resident-hook controllers and their encoded packages.

Imported originals stay exact. A native authored-source oracle precedes each
adaptation. `encode` links the reviewed derivative against one exact base's
lease entry symbols and emits the stock-free ABI 7 package plus the trust rows
(`policy_rows`) that the same base must compile in (build_core.py
--controller-policies). Nothing here admits a package: an empty row table, the
default, refuses every lease and every controller activation.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys

import cave_runtime
_ROOT = Path(__file__).resolve().parents[4]
_spec = importlib.util.spec_from_file_location('stock_hook_private_paths', _ROOT / 'scripts/runtime_private_paths.py')
_private = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_private)

SOURCE_PINS = {
    'modules/sidechain-compressor/manifest.py': '3bba6ac8ba315e10d6d7f2cb6342fb5ce6564e1ba6cd6ec362787d685c5e0cd7',
    'modules/sidechain-compressor/upstream/tools/patch_sidechain.s': 'e47f44a7685f0ea82d908897d222c04a6c3729c87dc6443d8d18d2af914b0d20',
    'modules/output-matrix/manifest.py': '1e9f844eff11dc2e262fd7efc733ae309c4285fd0a14e494da6b568d24af1216',
    'modules/output-matrix/matrix.s': '41bb06ce2e43d46d32a4b12a1c91df6dddf03f89281c4bcfe1129baa22a7cca1',
}
UNITS = {
    'sidechain-compressor': ('modules/sidechain-compressor/upstream/tools/patch_sidechain.s', 1, ('sc_norm',)),
    'output-matrix': ('modules/output-matrix/matrix.s', 2, ('page_levels', 'matrix_leave', 'matrix_enter')),
}
# Leased entries a base trusts by default once the package is reviewed. Entering
# MATRIX stays out: its project-load clamp and CS1 power-up check are installed
# only after stock boot ran them, so a power cycle loses MATRIX (owner decision).
DEFAULT_ENTRIES = {'sidechain-compressor': ('sc_norm',), 'output-matrix': ('page_levels', 'matrix_leave')}
REQUIRED_CORES = {1: 3, 2: 1}  # stock_hooks.c: Matrix is core A only
TITLES = {'sidechain-compressor': 'SIDECHAIN COMP', 'output-matrix': 'OUTPUT MATRIX'}
REVISIONS = (1, 1, 1)  # policy, state, parameter: the scoped derivative's first reviewed contract
POLICY_CAPACITY = 24  # controller_write_lease.h MW_CONTROLLER_WRITE_POLICY_CAPACITY
SC_REFERENCE = (0x400d7000, 338, '76a4badcef6024b7de8bd6f05930146bdb6a47ffd577da340a6c252c316ff854')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def sources(name, sdk):
    if name not in UNITS:
        raise ValueError('No reviewed controller source port: ' + str(name))
    sdk = Path(sdk).resolve()
    result = {}
    for relative in ('modules/' + name + '/manifest.py', UNITS[name][0]):
        path = (sdk / relative).resolve()
        if not path.is_relative_to(sdk) or not path.is_file() or sha(path.read_bytes()) != SOURCE_PINS[relative]:
            raise ValueError('Controller source changed; review its source/ownership contract: ' + relative)
        result[relative] = path.read_text()
    return result


def write_wrapper(entry, feature, body, denied='', before='', capture='', after=''):
    """Source-only strong board lease wrapper. No caller readiness inputs.

    The 104-byte caller frame has the opaque lease, complete register/CCR
    snapshots and two source-owned notification snapshots. Begin's retained
    interrupt mask must survive: only CCR is restored until End. Failed End
    returns immediately without a stock/custom replay or notification.
    """
    return f'''
        .balign 4
        .global {entry}
{entry}:
        lea -104(%sp),%sp
        movem.l %d0-%d7/%a0-%a6,32(%sp)
        move.w %sr,%d0
        move.w %d0,92(%sp)
        pea (%sp)
        pea {feature}.w
        pea {entry}:l
        jsr modwerk_controller_write_begin
{entry}_begun:
        lea 12(%sp),%sp
        cmpi.l #1,%d0
        bne {entry}_denied
        move.w 92(%sp),%d0
        move.w %d0,%ccr
        movem.l 32(%sp),%d0-%d7/%a0-%a6
{before}
        bsr {body}
        movem.l %d0-%d7/%a0-%a6,32(%sp)
        move.w %sr,%d0
        move.w %d0,92(%sp)
{capture}
        pea (%sp)
        jsr modwerk_controller_write_end
{entry}_ended:
        addq.l #4,%sp
        cmpi.l #1,%d0
        bne {entry}_end_failed
        move.w 92(%sp),%d0
        move.w %d0,%ccr
        movem.l 32(%sp),%d0-%d7/%a0-%a6
{after}
        lea 104(%sp),%sp
        rts
{entry}_end_failed:
        move.w 92(%sp),%d0
        move.w %d0,%ccr
        movem.l 32(%sp),%d0-%d7/%a0-%a6
        lea 104(%sp),%sp
        rts
{entry}_denied:
        move.w 92(%sp),%d0
        move.w %d0,%ccr
        movem.l 32(%sp),%d0-%d7/%a0-%a6
        lea 104(%sp),%sp
{denied}
        rts
'''


def _replace_once(source, old, new):
    if source.count(old) != 1:
        raise ValueError('Reviewed derivative seam changed: ' + old.strip().splitlines()[0])
    return source.replace(old, new)


# The authored CUE + TRACK CC notification loop, cut from cue_mask_from_live so
# it runs after the lease ends (no stock call inside a held span).
_MATRIX_CC_LOOP = '''        moveq   #0,%d7
4:      moveq   #16,%d0
        add.l   %d7,%d0
        btst    %d0,%d6
        beq.s   6f
        moveq   #0,%d1
        btst    %d0,%d5
        beq.s   5f
        moveq   #1,%d1                   | now cued
5:      move.l  %d1,-(%sp)               | value
        moveq   #0x33,%d0
        move.l  %d0,-(%sp)               | CC 51
        move.l  %d7,-(%sp)               | track
        jsr     CC_OUT
        lea     12(%sp),%sp
6:      addq.l  #1,%d7
        moveq   #8,%d0
        cmp.l   %d0,%d7
        bne.s   4b
        rts
'''
_MATRIX_MODE_TAIL = '''9:      move.b  %d2,CUE_CFG
        move.b  %d2,CUE_CFG_CS1
        movem.l (%sp),%d2-%d7/%a2-%a3
        lea     32(%sp),%sp
        pea     -1.w
        jsr     MENU_REDRAW
        addq.l  #4,%sp
act_none:
        rts
'''
# YES on a CUE CFG row. NORMAL <-> STUDIO stays the authored store; a switch
# into or out of MATRIX runs the authored whole-bank conversion under the
# board lease (matrix_enter / matrix_leave). Refused: nothing changes. The
# redraw and any CC notification run after the lease ends.
_MATRIX_FRONT = '''set_mode:
        move.l  %d2,-(%sp)
        move.l  %d0,%d2                  | the new mode
        moveq   #0,%d0
        move.l  %d0,mw_matrix_cc:l       | no notification unless a conversion makes one
        mvs.b   CUE_CFG,%d1              | the old one
        cmp.l   %d1,%d2
        beq.s   mw_mode_plain
        moveq   #2,%d0
        cmp.l   %d0,%d2
        beq.s   mw_mode_enter
        cmp.l   %d0,%d1
        beq.s   mw_mode_leave
mw_mode_plain:
        move.l  %d2,%d0
        bsr     mw_matrix_mode_body
        bra.s   mw_mode_done
mw_mode_enter:
        move.l  %d2,%d0
        bsr     matrix_enter
        bra.s   mw_mode_done
mw_mode_leave:
        move.l  %d2,%d0
        bsr     matrix_leave
mw_mode_done:
        move.l  (%sp)+,%d2
        pea     -1.w
        jsr     MENU_REDRAW
        addq.l  #4,%sp
        rts
mw_matrix_mode_body:
'''


def adapted_source(name, sdk):
    """Emit an authored derivative while refusing any imported-source drift.

    Sidechain: sc_norm under a frame-time lease. Matrix: page_levels under a
    frame-time lease, and the mode transaction: the authored whole-bank
    conversion runs unchanged under one lease at the board's level-4 lock
    (tasks, USB and storage wait; frames run). Its CC 51 notifications and
    the menu redraw run after End. No truncated conversion or caller-provided
    mode flag substitutes for the lease, and Matrix retirement still refuses
    while MATRIX is selected (controller_board.c).
    """
    source = sources(name, sdk)[UNITS[name][0]]
    if name == 'sidechain-compressor':
        source = _replace_once(source, 'sc_norm:\n', 'mw_sc_norm_body:\n')
        return source + write_wrapper('sc_norm', 1, 'mw_sc_norm_body',
                                     denied='        lea 0x80000a50,%a3')
    source = _replace_once(source, 'page_levels:\n', 'mw_matrix_page_body:\n')
    source = _replace_once(source, 'set_mode:\n', _MATRIX_FRONT)
    source = _replace_once(source, _MATRIX_MODE_TAIL, _MATRIX_MODE_TAIL.replace(
        '''        pea     -1.w
        jsr     MENU_REDRAW
        addq.l  #4,%sp
''', ''))
    source = _replace_once(source, _MATRIX_CC_LOOP, '''        lea     mw_matrix_cc:l,%a0
        move.l  %d6,(%a0)                | the cue bits that changed, CC 51 after End
        move.l  %d5,4(%a0)
        rts
''')
    notify = ('''
        .text
| After the mode lease ends: CC 51 for each track whose cue state changed.
mw_matrix_notify:
        lea     -12(%sp),%sp
        movem.l %d5-%d7,(%sp)
        lea     mw_matrix_cc:l,%a0
        move.l  (%a0),%d6
        move.l  4(%a0),%d5
''' + _MATRIX_CC_LOOP.replace('        rts\n', '''        movem.l (%sp),%d5-%d7
        lea     12(%sp),%sp
        rts
''') + '''        .data
        .balign 4
mw_matrix_cc:   .long 0, 0                | changed, new cue bits
        .text
''')
    return (source + notify + write_wrapper('page_levels', 2, 'mw_matrix_page_body',
                                            denied='        move.b 0x80000032,%d3')
            + write_wrapper('matrix_leave', 2, 'mw_matrix_mode_body', after='        bsr mw_matrix_notify')
            + write_wrapper('matrix_enter', 2, 'mw_matrix_mode_body', after='        bsr mw_matrix_notify'))


def compile_original(name, sdk, builder, work, cross='m68k-elf-', pool_origins=(), fixture_imports=None):
    """Fresh low/high and optional pool links of the untouched authored source.

    `builder` is explicitly trusted source, not an MCP/uploaded argument. This
    proves native relocation only. It does not create encoded identities,
    strip DSP declarations or broaden the builder's resource admission.
    Output must already be a new private directory outside all Git worktrees.
    """
    texts = sources(name, sdk)
    work = _private.private_directory(work)
    if any(work.iterdir()):
        raise ValueError('Use a new empty private controller compilation directory.')
    if subprocess.run(['git', '-C', str(work), 'rev-parse', '--show-toplevel'], capture_output=True).returncode == 0:
        raise ValueError('Controller images must stay outside Git.')
    source = Path(sdk).resolve() / UNITS[name][0]
    objects = []
    if fixture_imports is not None:
        if (set(fixture_imports) != {'modwerk_controller_write_begin', 'modwerk_controller_write_end'}
                or any(type(value) is not int or not 0x47400000 <= value < 0x47420000 or value & 3
                       for value in fixture_imports.values())):
            raise ValueError('Private native fixture imports require the exact bounded strong lease seam.')
        source = work / 'authored-adaptation.s'
        source.write_text(adapted_source(name, sdk))
        imports = work / 'fixture-imports.s'
        imports.write_text(''.join(f'.global {symbol}\n.set {symbol}, {value}\n'
                                  for symbol, value in sorted(fixture_imports.items())))
        import_obj = work / 'fixture-imports.o'
        cave_runtime.run([cross + 'as', '-mcpu=54455', imports, '-o', import_obj])
        objects.append(import_obj)
    obj = work / 'authored.o'
    cave_runtime.run([cross + 'as', '-mcpu=54455', source, '-o', obj])
    objects.insert(0, obj)
    low, symbols, bss = cave_runtime.link_objects(builder, objects, cross, 0, work / 'low')
    high, _, high_bss = cave_runtime.link_objects(builder, objects, cross, builder.SHIFT, work / 'high')
    if bss != high_bss:
        raise ValueError('Controller BSS changes between fresh native origins.')
    offsets = builder.relocations(low, high, len(low) + bss)
    cave_runtime.validate_relocations(low, offsets, len(low) + bss)
    if name == 'sidechain-compressor' and fixture_imports is None:
        reference, _, reference_bss = cave_runtime.link_objects(builder, [obj], cross, SC_REFERENCE[0], work / 'reference')
        # The authored .text is338 bytes; the trusted runtime image has its
        # normal two-byte alignment padding. No source byte may be trimmed.
        if (len(reference)!=340 or sha(reference[:SC_REFERENCE[1]])!=SC_REFERENCE[2]
                or any(reference[SC_REFERENCE[1]:]) or reference_bss):
            raise ValueError('Sidechain authored native reference changed.')
    placed = []
    for index, origin in enumerate(pool_origins):
        if type(origin) is not int or origin < 0x40000000 or origin & 15 or origin & 0x08000000 or origin + len(low) + bss > 0x48000000:
            raise ValueError('Private controller origin is not a bounded canonical ColdFire extent.')
        fresh, _, fresh_bss = cave_runtime.link_objects(builder, objects, cross, origin, work / ('pool%d' % index))
        if fresh_bss != bss or cave_runtime.placed(low, offsets, origin) != fresh:
            raise ValueError('Controller relocation differs from fresh native pool assembly.')
        placed.append(dict(origin=origin, bytes=len(fresh), sha256=sha(fresh)))
    preparation = ('sdk/runtime/loader/build.py',
                   'sdk/machines/octatrack/module-adapters/cave_runtime.py',
                   'sdk/machines/octatrack/module-adapters/stock_hook_controllers.py',
                   'sdk/machines/octatrack/module-adapters/stock_hook_write_lease.h')
    return dict(image=low, symbols=symbols, bss=bss, offsets=offsets, nativePools=placed,
                sourceHashes={relative: sha(text.encode()) for relative, text in texts.items()},
                preparationHashes={relative: sha((_ROOT / relative).read_bytes()) for relative in preparation},
                adaptedSourceSha256=sha(source.read_bytes()),
                feature=UNITS[name][1], entries=UNITS[name][2], encodedSha256=None,
                productionLeaseBound=False, admission=False,
                fixtureImports=fixture_imports, matrixModeLeased=name == 'output-matrix')


LEASE_IMPORTS = ('modwerk_controller_write_begin', 'modwerk_controller_write_end')


def lease_imports(base_symbols):
    """The exact base's strong lease entries (its build_core symbols.json).

    A package names them by absolute address, so it belongs to that one base
    link: build_core.py --controller-policies refuses a rebuilt base whose
    symbols moved (--controller-layout).
    """
    if not isinstance(base_symbols, dict):
        raise ValueError('Controller packages need the exact base symbol map.')
    imports = {name: base_symbols.get(name) for name in LEASE_IMPORTS}
    if (any(type(v) is not int or v & 1 or not 0x40000400 <= v < 0x48000000 for v in imports.values())
            or len(set(imports.values())) != 2):
        raise ValueError('The base does not export the strong controller lease entries.')
    return imports


def controller_sites(name, upstream, symbols, builder):
    """ABI 7 stock-code sites from the module's own manifest (hashes, no bytes).

    The same records `build.py --octabam` makes for detours, pokes and symbol
    references; anything else such a package cannot carry is refused.
    """
    sys.path.insert(0, str(Path(upstream).expanduser().resolve()))
    from elekloader.sdk import octabam as port
    m = port.Octabam(str(_ROOT / 'sdk/octabam')).modules[name]
    extra = [what for what, there in (('requires', m.requires), ('tables', m.tables), ('keeps', m.keeps),
                                      ('DRAM regions', m.dram_regions), ('overrides', m.overrides),
                                      ('caves', m.cf_patches)) if there]
    extra += ['stock copies'] if any(getattr(u, 'stock_copies', ()) for u in m.linked) else []
    if extra or len(m.linked) != 1:
        raise ValueError(name + ' carries what a controller package cannot: ' + ', '.join(extra or ['units']))

    def symbol(label, addend=0):
        if label not in symbols:
            raise ValueError('%s names %s, which the derivative does not define.' % (name, label))
        return struct.pack('>I', symbols[label] + addend)
    sites = []
    for d in m.detours:
        n = d.pad_to or 6
        if d.kind not in builder.OPCODES or d.kind == 'lea' or d.target is not None or n < 6 or n % 2:
            raise ValueError('Detour at %#x: only jmp or jsr to the module\'s own symbol.' % d.site)
        digest, checked = builder.stock_digest(d.expect)
        sites.append((d.site, digest, builder.OPCODES[d.kind] + symbol(d.symbol) + b'\x4e\x71' * ((n - 6) // 2), [2], 0, checked))
    for poke in m.pokes:
        digest, checked = builder.stock_digest(poke.expect)
        sites.append((poke.addr, digest, bytes(poke.write), [], 0, checked))
    for ref in m.symbol_refs:
        digest, checked = builder.stock_digest(ref.expect.to_bytes(4, 'big'))
        sites.append((ref.addr, digest, symbol(ref.symbol, ref.addend), [0], 0, checked))
    return sorted(sites, key=lambda s: s[0])


def encode(name, sdk, builder, work, base_symbols, upstream, cross='m68k-elf-'):
    """The reviewed derivative as one stock-free ABI 7 package for one base.

    Linked at two origins (self-references only move; the lease entries are
    absolute), sites from the manifest by hash, a display name and layout 1.
    Returns the bytes, their SHA-256, the module id and every leased entry's
    image offsets (entry, Begin and End return PCs) for `policy_rows`.
    """
    texts = sources(name, sdk)
    imports = lease_imports(base_symbols)
    work = _private.private_directory(work)
    if any(work.iterdir()):
        raise ValueError('Use a new empty private controller package directory.')
    source = work / 'authored-adaptation.s'
    source.write_text(adapted_source(name, sdk))
    obj = work / 'authored.o'
    cave_runtime.run([cross + 'as', '-mcpu=54455', source, '-o', obj])
    defsyms = sorted(imports.items())
    low, symbols, bss = cave_runtime.link_objects(builder, [obj], cross, 0, work / 'low', defsyms)
    high, _, high_bss = cave_runtime.link_objects(builder, [obj], cross, builder.SHIFT, work / 'high', defsyms)
    if bss != high_bss:
        raise ValueError('Controller BSS changes between fresh native origins.')
    offsets = builder.relocations(low, high, len(low) + bss)
    cave_runtime.validate_relocations(low, offsets, len(low) + bss)
    entries = {}
    for entry in UNITS[name][2]:
        at = [symbols.get(entry + suffix) for suffix in ('', '_begun', '_ended')]
        if any(type(v) is not int or v & 1 or not 0 <= v < len(low) for v in at) or len(set(at)) != 3:
            raise ValueError('A leased entry of the derivative is not inside its image: ' + entry)
        entries[entry] = dict(entry=at[0], beginReturn=at[1], endReturn=at[2])
    sites = controller_sites(name, upstream, symbols, builder)
    data = builder.package(low, bss, [], offsets, sites=sites, name=name, hashed=True,
                           title=TITLES[name], layout=1)
    policy = dict(schema=1, module=name, feature=UNITS[name][1], revisions=list(REVISIONS),
                  sourceHashes={relative: sha(text.encode()) for relative, text in texts.items()},
                  adaptedSourceSha256=sha(source.read_bytes()), entries=entries)
    return dict(package=data, packageSha256=sha(data), moduleId=builder.module_id(name), imageBytes=len(low),
                bss=bss, sites=len(sites), entries=entries, imports=imports,
                sourcePolicySha256=sha(json.dumps(policy, sort_keys=True, separators=(',', ':')).encode()),
                policy=policy)


def policy_rows(name, encoded, entries=None):
    """Trust rows for controller_write_policy.c, one per leased entry.

    `entries` defaults to DEFAULT_ENTRIES: authorizing matrix_enter is an
    explicit owner decision (see DEFAULT_ENTRIES).
    """
    entries = DEFAULT_ENTRIES[name] if entries is None else tuple(entries)
    feature = UNITS[name][1]
    if not entries or len(set(entries)) != len(entries) or set(entries) - set(encoded['entries']):
        raise ValueError('Trust rows name only the derivative\'s own leased entries.')
    return [dict(module=name, moduleId=encoded['moduleId'], packageSha256=encoded['packageSha256'],
                 sourcePolicySha256=encoded['sourcePolicySha256'], revisions=list(REVISIONS),
                 feature=feature, requiredCores=REQUIRED_CORES[feature], version=1,
                 imageBytes=encoded['imageBytes'], entryName=entry, **encoded['entries'][entry])
            for entry in entries]


def policies_c(rows):
    """C initializers for MW_REVIEWED_CONTROLLER_POLICIES, checked like the board does."""
    if not isinstance(rows, list) or len(rows) > POLICY_CAPACITY:
        raise ValueError('Controller trust rows exceed the fixed capacity.')
    seen, text = set(), ''
    for row in rows:
        digest, policy = bytes.fromhex(row['packageSha256']), bytes.fromhex(row['sourcePolicySha256'])
        key = (digest, row['entry'])
        if (len(digest) != 32 or len(policy) != 32 or not any(digest) or not any(policy) or key in seen or
                row['feature'] not in REQUIRED_CORES or row['requiredCores'] != REQUIRED_CORES[row['feature']] or
                row['version'] != 1 or list(row['revisions']) != list(REVISIONS) or not 0 < row['moduleId'] < 1 << 32 or
                any(type(row[k]) is not int or row[k] & 1 or not 0 <= row[k] < row['imageBytes']
                    for k in ('entry', 'beginReturn', 'endReturn')) or row['beginReturn'] == row['endReturn']):
            raise ValueError('Malformed or duplicate controller trust row.')
        seen.add(key)
        hexes = lambda b: '{' + ','.join('0x%02x' % v for v in b) + '}'
        text += ('    {{%s, %s, 0x%08xu, %du, %du, %du, %du, %du}, %du, %du, %du, %du, %du}, \\\n'
                 % (hexes(digest), hexes(policy), row['moduleId'], *row['revisions'], row['feature'],
                    row['requiredCores'], row['version'], row['imageBytes'], row['entry'], row['beginReturn'], row['endReturn']))
    return text


def main(argv=None):
    parser = argparse.ArgumentParser(description='Encode the reviewed controller packages for one exact base.')
    parser.add_argument('--base-symbols', type=Path, required=True, help='that base build_core symbols.json')
    parser.add_argument('--upstream', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True, help='new private directory outside Git')
    parser.add_argument('--authorize-matrix-entry', action='store_true',
                        help='also trust matrix_enter (owner decision: MATRIX does not survive a power cycle)')
    args = parser.parse_args(argv)
    spec = importlib.util.spec_from_file_location('controller_builder', _ROOT / 'sdk/runtime/loader/build.py')
    builder = importlib.util.module_from_spec(spec); spec.loader.exec_module(builder)
    symbols = json.loads(args.base_symbols.read_text())
    out = _private.private_directory(args.out)
    if any(out.iterdir()):
        raise ValueError('Use a new empty private output directory.')
    rows, receipt = [], dict(schema=1, baseSymbolsSha256=sha(args.base_symbols.read_bytes()), packages={})
    for name in UNITS:
        encoded = encode(name, _ROOT / 'sdk/octabam', builder, out / (name + '-work'), symbols, args.upstream)
        _private.save(out / (name + '.mwrm'), encoded['package'])
        entries = DEFAULT_ENTRIES[name] + (('matrix_enter',) if name == 'output-matrix' and args.authorize_matrix_entry else ())
        rows += policy_rows(name, encoded, entries)
        receipt['packages'][name] = {k: v for k, v in encoded.items() if k != 'package'}
    policies_c(rows)
    receipt['rows'] = rows
    _private.save(out / 'controller-policies.json', json.dumps(rows, indent=1).encode())
    _private.save(out / 'receipt.json', json.dumps(receipt, indent=1, sort_keys=True).encode())
    print(json.dumps({name: dict(sha256=v['packageSha256'], sites=v['sites'], imageBytes=v['imageBytes'])
                      for name, v in receipt['packages'].items()}))


if __name__ == '__main__':
    main()
