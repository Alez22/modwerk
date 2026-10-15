# SPDX-License-Identifier: GPL-3.0-or-later
"""Resident controller engines on demand, the DSP side, from fresh private assemblies (no stock image).

1. Relocation. Each real engine unit (resident_dsp.engine_unit) relocated at several arena bases three ways must
   agree word for word: a fresh assembly of the authored source at that base, resident_dsp.relocate, and the
   base's own C relocator (resident_engines.c's mw_engine_relocate, over the C data resident_engines.data_c makes).
   A wrong relocation would be distortion on the unit.
2. Execution (resident_engines_native.cpp under the vendored DSP interpreter). The receiver of an on-demand
   build PLACEs the engine and its CAS switches the stubs on; each stub then runs the placed engine. The same
   stub of the resident build (the engine in the permanent block) runs from the same X/Y memory and registers.
   X and Y afterwards, the data ALU registers and the instruction count must be bit-identical; an address
   register may differ only by the engine's displacement (a P address it holds). The receiver also refuses an
   enable before PLACE, a second PLACE, and an unplace while enabled.

Needs dsp_asm (ELEKLOADER_DSP_ASM) and, for (2), the vendored dsp56300 build (ELEKLOADER_DSP56300: its source/
and build/source/ libraries, /opt/toolchain/vendor/dsp56300 in the modwerk-source-tools image). The interpreter
is not the chip: this proves the relocation and the receiver's arithmetic, never timing or audio on a unit.
"""
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
ADAPTER = ROOT / 'sdk/machines/octatrack/module-adapters'
ELEK = ROOT / 'sdk/machines/octatrack/elekloader'
RUNTIME = ADAPTER / 'resident-runtime'
sys.path.insert(0, str(ADAPTER))
import resident_dsp  # noqa: E402
import resident_engines  # noqa: E402
import resident_source  # noqa: E402

ASM = os.environ.get('ELEKLOADER_DSP_ASM') or shutil.which('dsp_asm')
EMU = Path(os.environ.get('ELEKLOADER_DSP56300', '/opt/toolchain/vendor/dsp56300'))
LIBS = [EMU / 'build/source' / part for part in ('dsp56kEmu/libdsp56kEmu.a', 'dsp56kBase/libdsp56kBase.a', 'asmjit/libasmjit.a')]
VTUNE = EMU / 'build/source/vtuneSdk/libvtuneSdk.a'  # the JIT's profiling hooks, where the build has them
RECEIVER_ORIGIN = 0x400
STUBS = {resident_dsp.SIDECHAIN: ('hsc_tap', 'hsc_det', 'hsc_commit'), resident_dsp.MATRIX: ('hom_mix', 'hom_phn'),
         resident_dsp.ANALOG_BD: ('hab_source',)}
# Words that steer each engine down its working path rather than its early return (on the fixed registers below,
# r6 = $6280): Sidechain's track 3 with KEY 3 and its monitor on, MATRIX selected, an Analog BD source record.
ACTIVE = {resident_dsp.SIDECHAIN: ('X 1056 3', 'X %d %d' % (0x628d, 0x30000), 'Y %d %d' % (0x7f6, 0x10000)),
          resident_dsp.MATRIX: ('X %d %d' % (0x205, 0x1000), 'X %d 1' % 0x103b),
          resident_dsp.ANALOG_BD: tuple('X %d 0' % a for a in range(0x5000, 0x5040)) +  # a quiet record: the rest zero
          ('X %d %d' % (0x209, 0x5000), 'X %d %d' % (0x5000, 0xab09), 'X %d %d' % (0x5002, 0x0909))}
# Analog BD's working path on core A then points its voice block (r5) at X:$f598xx, which the interpreter has no
# memory for (it faults, in the resident build as in the placed one): compare its first 160 instructions, to the
# voice loop. The dormant path and core B's working path run to the end.
LIMIT = {('A', resident_dsp.ANALOG_BD): 160}


def read(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fresh(ob, tag, feature, base, work, assemble, analog):
    """The authored engine assembled at `base` itself (engine_unit's own build, at any base)."""
    table, texts = resident_dsp._engines(ob, tag, base, feature, analog)
    words, _ = resident_dsp.assemble_authored('\n'.join(texts), base + len(table), work, assemble)
    return table + words


def c_relocated(units, bases, work):
    """mw_engine_relocate's words for every (tag, feature) unit at every base, from resident_engines.data_c's data."""
    bundles = {tag: dict(onDemand=sum(f for (t, f) in units if t == tag),
                         engines={f: u for (t, f), u in units.items() if t == tag}) for tag in 'AB'}
    (work / 'data.c').write_text(resident_engines.data_c(bundles))
    order = sorted(units)
    main = ['#include <stdio.h>', '#include "resident_engines.h"', 'int main(void) {',
            '    static uint32_t out[8192];', '    static const unsigned bases[] = {%s};' % ','.join('%du' % b for b in bases)]
    for tag, feature in order:
        core, k = 'AB'.index(tag), (1, 2, 4).index(feature)
        main += ['    for (unsigned b = 0; b < %d; ++b) {' % len(bases),
                 '        mw_engine_relocate(&mw_engine_units[%d][%d], bases[b], out);' % (core, k),
                 '        for (unsigned i = 0; i < mw_engine_units[%d][%d].count; ++i) printf("%%u ", (unsigned)out[i]);' % (core, k),
                 '        printf("\\n");', '    }']
    main += ['    return 0;', '}']
    (work / 'main.c').write_text('\n'.join(main) + '\n')
    (work / 'stubs.c').write_text(r'''
#include <stdint.h>
#include "transfer.h"
volatile uint32_t dl_pool_base[2], dl_pool_words[2];
int dl_owned_command_reserve(unsigned a,uint32_t b,unsigned c,unsigned d,unsigned e,unsigned f,struct dl_owned_job *g) { (void)a;(void)b;(void)c;(void)d;(void)e;(void)f;(void)g;return 0; }
int dl_owned_upload_reserve(unsigned a,uint32_t b,const struct dl_upload *c,struct dl_owned_job *d) { (void)a;(void)b;(void)c;(void)d;return 0; }
int dl_owned_submit(const struct dl_owned_job *v) { (void)v;return 0; }
int dl_owned_cancel(const struct dl_owned_job *v) { (void)v;return 0; }
int dl_owned_job_poll(const struct dl_owned_job *v,struct dl_owned_progress *p) { (void)v;(void)p;return 0; }
int dl_owned_job_release(const struct dl_owned_job *v) { (void)v;return 0; }
void dl_owned_fail_closed(unsigned c) { (void)c; }
int dl_engine_claim(unsigned c,unsigned r,int k) { (void)c;(void)r;(void)k;return 0; }
void dl_engine_release(unsigned c,unsigned r) { (void)c;(void)r; }
unsigned dl_engine_reserved(unsigned c) { (void)c;return 0; }
int mw_engines_test_quiet(void) { return 1; }
''')
    import resident_driver
    core = read('resident_engines_dsp_core', ELEK / 'build_core.py')
    (work / 'transfer.h').write_text(resident_driver.transport_header((core.DYNLOAD / 'transfer.h').read_text()))
    shutil.copyfile(ELEK / 'fxids.h', work / 'fxids.h')
    out = work / 'relocate'
    subprocess.run(['cc', '-std=c11', '-O1', '-Wall', '-Wextra', '-Werror', '-DMW_ENGINES_TEST', '-DMODWERK_FX_IDS=128',
                    '-I' + str(work), '-I' + str(RUNTIME), str(work / 'main.c'), str(work / 'stubs.c'), str(work / 'data.c'),
                    str(RUNTIME / 'resident_engines.c'), '-o', str(out)], check=True, capture_output=True)
    rows = subprocess.run([str(out)], check=True, capture_output=True, text=True).stdout.splitlines()
    result, k = {}, 0
    for key in order:
        for base in bases:
            result[key, base] = list(map(int, rows[k].split()))
            k += 1
    return result


@unittest.skipUnless(ASM and shutil.which('cc'), 'dsp_asm (ELEKLOADER_DSP_ASM) or a host C compiler unavailable')
class ResidentEngines(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packages = read('resident_engines_packages', ELEK / 'dsp_packages.py')
        cls.ob = cls.packages.Octabam(str(ROOT / 'sdk/octabam'))
        cls.work = tempfile.TemporaryDirectory(prefix='modwerk-resident-engines.')
        cls.units, cls.analog = {}, {}
        for tag in 'AB':
            cls.analog[tag] = resident_dsp._analog(cls.ob.root, tag)[0]
            for feature in resident_dsp.FEATURES:
                if feature & resident_dsp.ALLOWED[tag]:
                    cls.units[tag, feature] = resident_dsp.engine_unit(cls.ob, tag, feature, cls.work.name,
                                                                      cls.packages.assemble, cls.analog[tag])

    @classmethod
    def tearDownClass(cls):
        cls.work.cleanup()

    def test_real_units_relocate_alike_in_c_in_python_and_freshly_assembled(self):
        # Arena-like bases: the lowest legal one, the top of a 4,418/4,546-word arena under a block ending at $2000,
        # stacked placements, a 4K boundary, and the build's own proof bases.
        bases = sorted({0x0460, 0x0a41, 0x0fff, 0x1000, 0x1333, 0x17ff, 0x1c01, 0x1d5e, 0x1e00 - 998, 0x2000 - 37 - 388})
        with tempfile.TemporaryDirectory() as temp:
            relocated = c_relocated(self.units, bases, Path(temp))
        for (tag, feature), unit in self.units.items():
            self.assertEqual(len(unit['words']), {1: 388, 2: 773, 4: 998}[feature])
            for base in bases:
                with self.subTest(tag=tag, feature=feature, base=hex(base)):
                    python = resident_dsp.relocate(unit, base)
                    self.assertEqual(relocated[(tag, feature), base], python)
                    self.assertEqual(fresh(self.ob, tag, feature, base, self.work.name, self.packages.assemble,
                                           self.analog[tag]), python)

    @unittest.skipUnless(all(p.is_file() for p in LIBS) and shutil.which('c++'), 'vendored dsp56300 build unavailable')
    def test_placed_engine_runs_bit_exactly_as_the_resident_one(self):
        loader = resident_source.load_loader()
        work = Path(self.work.name)
        harness = work / 'resident-engines-native'
        subprocess.run(['c++', '-std=c++17', '-O2', '-DDSP56300_DEBUGGER=0', '-DASMJIT_STATIC',
                        '-I' + str(EMU / 'source'), '-I' + str(EMU / 'source/asmjit/src'),
                        str(ROOT / 'sdk/tests/resident_engines_native.cpp'), *map(str, LIBS),
                        *([str(VTUNE)] if VTUNE.is_file() else []), '-lpthread', '-ldl', '-o', str(harness)],
                       check=True, capture_output=True)

        def receiver(bundle, tag):
            """The receiver at RECEIVER_ORIGIN, its table reaching exactly to the block, as the build lays them."""
            def text(table):
                return loader.receiver_source(loader.RECEIVER.read_text(), (0x7c8, 0x7c9), table, tag=tag, ids=128,
                                              hook_control=resident_dsp.receiver_control(bundle),
                                              hook_reset=resident_dsp.receiver_reset(bundle))
            _, labels = self.packages.assemble(text(1200), RECEIVER_ORIGIN, str(work))
            table = bundle['origin'] - labels['dltable']
            words, final = self.packages.assemble(text(table), RECEIVER_ORIGIN, str(work))
            self.assertEqual(final['dltable'], labels['dltable'])
            self.assertEqual(final['dltable'] - RECEIVER_ORIGIN, len(words))
            return words, final, table

        def run(steps):
            path = work / 'script.txt'
            path.write_text('\n'.join(steps) + '\n')
            result = subprocess.run([str(harness), str(path)], capture_output=True, text=True, timeout=600)
            self.assertEqual(result.returncode, 0, result.stderr)
            # The emulator logs to stdout too; keep only the harness's own answers.
            return [line for line in result.stdout.split('\n') if line.split(' ')[0] in ('A', 'P', 'S', 'H', 'G', 'AR')]

        def image(words, origin):
            return ['P %d %d' % (origin + i, w) for i, w in enumerate(words)]

        def memory():
            # The engines' owned X/Y and everything low they may read, then fixed registers: the same in both runs.
            steps = ['FILL x 0 32768 11', 'FILL y 0 32768 23', 'FILL y %d %d 37' % (0x33dfe, 0x34000),
                     'FILL y %d %d 41' % (0x3bdfe, 0x3c000)]
            steps += ['R r %d %d' % (i, 0x6100 + 0x40 * i) for i in range(8)]
            steps += ['R n %d %d' % (i, i + 1) for i in range(8)] + ['R m %d %d' % (i, 0xffffff) for i in range(8)]
            return steps + ['ZERO']  # the receiver's packets leave different data registers in the two runs

        def observe():
            return ['HASH x 0 32768', 'HASH y 0 32768', 'HASH y %d %d' % (0x33dfe, 0x34000),
                    'HASH y %d %d' % (0x3bdfe, 0x3c000), 'REGS']

        for tag in 'AB':
            allowed = resident_dsp.ALLOWED[tag]
            resident = resident_dsp.place_resident(self.ob, tag, 0x2000, str(work), self.packages.assemble, 0)
            demand = resident_dsp.place_resident(self.ob, tag, 0x2000, str(work), self.packages.assemble, allowed)
            r_words, r_labels, _ = receiver(resident, tag)
            d_words, d_labels, d_table = receiver(demand, tag)
            for feature in resident_dsp.FEATURES:
                if not feature & allowed:
                    continue
                unit = demand['engines'][feature]
                n = len(unit['words'])
                for offset in (d_table - n, 64 + 333):  # the arena's top (directly under the block), and lower down
                    base = d_labels['dltable'] + offset
                    with self.subTest(tag=tag, feature=feature, base=hex(base)):
                        hwbase = demand['labels']['hwbase%d' % feature]
                        control = d_labels['hookcontrol']
                        steps = image(d_words, RECEIVER_ORIGIN) + image(demand['words'], demand['origin'])
                        steps += image(resident_dsp.relocate(unit, base), base)
                        steps += ['P %d %d' % (d_labels['hookready'], allowed),   # every reset complete
                                  'PKT %d 0 %d 0' % (control, feature),           # enable before PLACE: refused
                                  'PKT %d %d %d 1' % (control, feature, offset),  # PLACE
                                  'RP %d' % hwbase,
                                  'PKT %d %d %d 1' % (control, feature, offset),  # placed already: refused
                                  'PKT %d 0 %d 0' % (control, feature),           # enable
                                  'PKT %d %d 0 1' % (control, feature)]           # unplace while enabled: refused
                        # The feature's state as its RESET leaves it (Analog BD's authored tables, zeroed Y ranges).
                        reset = []
                        for record in resident_dsp.initialization_records(resident):
                            if any(r['owner'] == feature and r['space'] == record['space'] and r['address'] == record['address']
                                   for r in resident['resources']):
                                reset += ['%s %d %d' % (record['space'].upper(), record['address'] + i, w)
                                          for i, w in enumerate(record['words'])]

                        def go(labels):
                            # Each stub from the same memory twice: as filled (mostly the early return), then from
                            # the feature's reset state, steered down its working path.
                            out = []
                            for limit, pokes in ((400000, ()), (LIMIT.get((tag, feature), 400000), reset + list(ACTIVE[feature]))):
                                out += memory() + list(pokes)
                                out += sum((['GO %d %d %d' % (labels[s], limit, RECEIVER_ORIGIN)] + observe() for s in STUBS[feature]), [])
                            return out
                        placed = run(steps + go(demand['labels']))
                        self.assertEqual(placed[:5], ['A 0', 'A 1', 'P %d %d' % (hwbase, base), 'A 0', 'A 1'])
                        self.assertEqual(placed[5], 'A 0')
                        steps = image(r_words, RECEIVER_ORIGIN) + image(resident['words'], resident['origin'])
                        steps += ['P %d %d' % (r_labels['hookready'], allowed), 'PKT %d 0 %d 0' % (r_labels['hookcontrol'], feature)]
                        reference = run(steps + go(resident['labels']))
                        self.assertEqual(reference[0], 'A 1')
                        mine, theirs = placed[6:], reference[1:]
                        self.assertEqual(len(mine), len(theirs))
                        block = range(resident['origin'], resident['origin'] + len(resident['words']))
                        for line, (a, b) in enumerate(zip(mine, theirs)):
                            stub = (STUBS[feature] * 2)[line // 7] if line // 7 < 2 * len(STUBS[feature]) else '-'
                            if a.startswith('AR'):
                                # Only a P address may differ: into the placed engine here, into the block there.
                                for x, y in zip(map(int, a.split()[1:]), map(int, b.split()[1:])):
                                    self.assertTrue(x == y or (base <= x < base + n and y in block), (stub, a, b))
                            elif a.startswith('S ') and a.split()[2] == b.split()[2] == '0':
                                # Stopped inside the engine: the same instruction of the unit, at its two addresses.
                                first = resident_dsp.ENTRIES[feature][0]
                                start = resident['labels'][first] - unit['entries'][first]
                                self.assertEqual((a.split()[1], int(a.split()[3]) - base), (b.split()[1], int(b.split()[3]) - start), stub)
                            else:
                                self.assertEqual(a, b, stub)
                        ran = [line.split() for line in mine if line.startswith('S ')]
                        if os.environ.get('RESIDENT_ENGINES_VERBOSE'):
                            print(tag, feature, hex(base), [(s, n, how) for s, (_, n, how, _) in zip(STUBS[feature] * 2, ran)])
                        # Returned, or left for stock code (or stopped at the limit above).
                        self.assertTrue(all(how in ('1', '2') or ((tag, feature) in LIMIT and n == str(LIMIT[tag, feature]))
                                            for _, n, how, _ in ran), ran)
                        self.assertGreater(max(int(n) for _, n, _, _ in ran), 10, ran)        # more than a replay ran
                        # Disable, then unplace: the base word goes back to 0.
                        tail = run(image(d_words, RECEIVER_ORIGIN) + image(demand['words'], demand['origin']) +
                                   ['P %d %d' % (d_labels['hookready'], allowed), 'PKT %d %d %d 1' % (control, feature, offset),
                                    'PKT %d 0 %d 0' % (control, feature), 'PKT %d %d 0 0' % (control, feature),
                                    'PKT %d %d 0 1' % (control, feature), 'RP %d' % hwbase])
                        self.assertEqual(tail[:5], ['A 1', 'A 1', 'A 1', 'A 1', 'P %d 0' % hwbase])


if __name__ == '__main__':
    unittest.main()
