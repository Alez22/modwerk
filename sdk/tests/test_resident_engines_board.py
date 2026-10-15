# SPDX-License-Identifier: GPL-3.0-or-later
"""Resident controller engines on demand, the ColdFire side, on the actual board, loader, generated manager and
generated owned transport (host, ASan/UBSan).

Synthetic: the engine units (words and relocations made up here, relocated by resident_dsp.relocate for the
expected words), the controller packages and trust rows (test_controller_board's), the FX catalogue and the
bank's Parts, and a modelled DSP receiver (WRITE into a P array, PLACE and CAS as resident_dsp.receiver_place
and receiver_control state them, RESET word counts). No hardware ACK, timing or audio is claimed; the DSP side's
own execution is test_resident_engines.py's.
"""
import importlib.util
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
ADAPTER = ROOT / 'sdk/machines/octatrack/module-adapters'
POLICY = ADAPTER / 'controller-policy'
RUNTIME = ADAPTER / 'resident-runtime'
ELEK = ROOT / 'sdk/machines/octatrack/elekloader'
sys.path.insert(0, str(ADAPTER))
sys.path.insert(0, str(ELEK))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import resident_driver  # noqa: E402
import resident_dsp  # noqa: E402
import resident_engines  # noqa: E402
import resident_journal  # noqa: E402
import resident_placement  # noqa: E402
import zero_state  # noqa: E402
import test_controller_board as board  # noqa: E402
from host_flags import SANITIZE  # noqa: E402

TABLE, WORDS = 4096, 2000          # each core's pool in this fixture: arena 1936 words
ARENA = WORDS - 64
SIZES = {('A', 1): 388, ('A', 2): 773, ('A', 4): 998, ('B', 1): 388, ('B', 4): 998}


def unit(tag, feature, n):
    """A made-up engine: words at base 0 with address and displacement relocations, as engine_unit shapes them."""
    seed = (feature * 0x9e3779b1 + (tag == 'B') * 0x7f4a7c15) & 0xffffffff
    words, relocations = [], []
    for i in range(n):
        seed = (seed * 1103515245 + 12345) & 0xffffffff
        kind = seed >> 29
        if kind == 0 and i:
            relocations.append(i)
            words.append(seed % n)                       # an address inside the unit
        elif kind == 1 and i:
            relocations.append(i | 0x8000)
            words.append((0x300 + seed % 0x200) & 0xffffff)  # a displacement to a fixed stock address
        else:
            words.append(seed >> 8 & 0xffffff)
    result = dict(tag=tag, feature=feature, words=words, relocations=relocations, entries={},
                  sha256=hashlib.sha256(b''.join(w.to_bytes(3, 'big') for w in words)).hexdigest())
    result['proofs'] = [dict(base=b, sha256=hashlib.sha256(b''.join(w.to_bytes(3, 'big') for w in resident_dsp.relocate(result, b))).hexdigest())
                        for b in resident_dsp.ENGINE_PROOFS]
    return result


def bundles():
    out = {}
    for tag in 'AB':
        engines = {f: unit(tag, f, n) for (t, f), n in SIZES.items() if t == tag}
        out[tag] = dict(onDemand=sum(engines), engines=engines)
    return out


def expected(units):
    """Python-relocated words at the top of the arena (each engine alone there), for the fixture to compare."""
    text = ''
    for core, tag in enumerate('AB'):
        for feature, u in units[tag]['engines'].items():
            offset = ARENA - len(u['words'])
            words = resident_dsp.relocate(u, TABLE + 64 + offset)
            text += 'static const uint32_t top_%d_%d[%d] = {%s};\n' % (core, feature, len(words), ','.join(map(str, words)))
        text += ''.join('#define TOP_%d_%d %s\n' % (core, f, 'top_%d_%d' % (core, f) if f in units[tag]['engines'] else '0')
                        for f in (1, 2, 4))
    return text


MANAGER_UNIT = r'''
#include <stdint.h>
static uint32_t auto_serial = 0x80000000u;
static unsigned observed_valid;
static uint8_t last[16];
uint32_t test_bank = 0x400e21e0u;
uint8_t dl_journal_test_live[16];
uint8_t test_qb, test_qp, test_parts[4][16];
#include "manager.c"
struct dl_package dl_catalog[MODWERK_FX_IDS];
struct code dl_codes[2][MODWERK_FX_IDS];
const uint32_t dl_pmap16 = 0;
const fx_set dl_stub_at_boot = {{0}}, modwerk_fx_modules = {{0, 0xffffffffu}};
int modwerk_stock_hook_export_idle(void) { return 1; }
uint32_t modwerk_dsp_source_charge(unsigned c) { (void)c; return 0; }
int modwerk_dsp_buffer_permitted(unsigned c, unsigned k, unsigned b, unsigned id) { (void)c; (void)k; (void)b; (void)id; return 1; }
int modwerk_stock_hook_buffer_policy(unsigned c, unsigned id, struct mw_hook_buffer_claim *out) { (void)c; (void)id; (void)out; return 0; }
int modwerk_dsp_catalogue_handle(uint32_t module) { (void)module; return -1; }
void board_manager_running(unsigned slot, unsigned id) { allocator.active[slot] = (uint8_t)id; }
void board_manager_init(void) { initialized = 1; dl_buffers_init(&buffers, dl_pmap16); }
unsigned test_capacity(unsigned c) { return allocator.capacity[c]; }
unsigned test_initialized(void) { return initialized; }
unsigned test_idle(void) { return !phase && !waiting && !queued_token && !allocator.phase; }
int test_live(unsigned c, unsigned p) { return allocator.live[c][p].present ? (int)allocator.live[c][p].offset : -1; }
/* Id 0 (NONE) is resident, as stock's is. */
void test_none(void) { dl_catalog[0] = (struct dl_package){0, 0, 0, 3, 1, 1, 0}; }
/* A stock-free FX: id p, n words, on both cores' codes (a WRITE then a BIND each). */
static uint32_t fx_words[MODWERK_FX_IDS][1024];
void test_fx(unsigned p, unsigned n)
{
    for (unsigned i = 0; i < n; ++i) fx_words[p][i] = (p << 12) + i;
    dl_catalog[p] = (struct dl_package){(uint16_t)n, 1, 100, 3, 0, 1, 0};
    dl_codes[0][p] = dl_codes[1][p] = (struct code){fx_words[p], 0, (uint16_t)n, 0, 1, 0};
}
/* One Part switch through the actual selection route: prepare, poll to READY, commit, retire. */
static uint32_t select_token = 1;
int test_select(const uint8_t ids[16], void (*pump)(void))
{
    struct dl_selection s;
    for (unsigned i = 0; i < sizeof s; ++i) ((uint8_t *)&s)[i] = 0;
    for (unsigned i = 0; i < 16; ++i) s.target[i] = ids[i];
    uint32_t token = ++select_token;
    int r = dl_selection_prepare(&s, token);
    for (unsigned n = 0; n < 4000 && r == DL_SELECT_WAIT; ++n) { pump(); r = dl_selection_poll(token); }
    if (r != DL_SELECT_READY) return r;
    dl_selection_commit(token);
    for (unsigned n = 0; n < 4000 && phase; ++n) { pump(); dl_residency_tick(); }
    return phase ? 0 : 1;
}
'''

MODEL = r'''
#include "resident_engines.h"
#include "expected.h"
static unsigned quiet = 1;
int mw_engines_test_quiet(void) { return (int)quiet; }
unsigned test_capacity(unsigned c);
unsigned test_initialized(void);
unsigned test_idle(void);
int test_live(unsigned c, unsigned p);
void test_fx(unsigned p, unsigned n);
void test_none(void);
int test_select(const uint8_t ids[16], void (*pump)(void));
extern uint8_t test_parts[4][16];
/* Modelled receiver: WRITE into P (each chunk read back, as the receiver does), PLACE (word 7 = 1: dormant only, the
 * engine whole inside the arena, a prior unplace), CAS (word 7 = 0: never enabling an unplaced engine or one whose
 * reset is incomplete; a disable invalidates the reset), RESET counted per feature. */
static uint32_t P[2][8192];
static unsigned dsp_mask[2], words[2][3], base_word[2][3], answered[2], cas_count;
static unsigned refuse_write[2], refuse_place[2]; /* table offsets at which a WRITE chunk, a PLACE is refused */
static const unsigned totals[3] = {1042, 193, 3776};
struct entry { unsigned op, w4, w5, w7; };
static struct entry trail[2][8192];
static unsigned trails[2];
static void dsp(void)
{
    dl_frame();
    for (unsigned c = 0; c < 2; ++c) {
        if (dl_tx[c][0] != DL_MAGIC || dl_tx[c][1] == answered[c]) continue;
        answered[c] = dl_tx[c][1];
        unsigned reject = 0, op = dl_tx[c][2], w4 = dl_tx[c][4], w5 = dl_tx[c][5], w7 = dl_tx[c][7];
        assert(trails[c] < 8192);
        trail[c][trails[c]++] = (struct entry){op, w4, w5, w7};
        if (op == 3u) {
            reject = refuse_write[c] && w5 == refuse_write[c];
            for (unsigned i = 0; !reject && i < w4; ++i)
                P[c][MODWERK_DSP_TABLE0 + w5 + i] = (unsigned)dl_tx[c][8 + 2 * i] << 8 | dl_tx[c][9 + 2 * i];
        } else if (op == 11u) {
            unsigned f = w7, k = f == 1u ? 0 : f == 2u ? 1 : f == 4u ? 2 : 3;
            reject = k > 2 || w5 != words[c][k] || (dsp_mask[c] & f);
            if (!reject) words[c][k] += w4;
        } else if (op == 10u && w7 == 1u) {
            unsigned f = w4, k = f == 1u ? 0 : f == 2u ? 1 : f == 4u ? 2 : 3;
            reject = k > 2 || (dsp_mask[c] & f) || !mw_engine_units[c][k].count || (refuse_place[c] && w5 == refuse_place[c]);
            if (!reject && base_word[c][k]) { reject = w5 != 0; if (!reject) base_word[c][k] = 0; }
            else if (!reject && w5) {
                reject = w5 < 64u || w5 + mw_engine_units[c][k].count > MODWERK_DSP_WORDS0;
                if (!reject) base_word[c][k] = MODWERK_DSP_TABLE0 + w5;
            }
        } else if (op == 10u && w7 == 0u) {
            unsigned expected = w4, desired = w5, on = desired & ~expected;
            ++cas_count;
            reject = expected != dsp_mask[c];
            for (unsigned k = 0; k < 3; ++k)
                if (on >> k & 1u) reject |= words[c][k] != totals[k] || !base_word[c][k];
            if (!reject) {
                for (unsigned f = 1; f <= 4; f <<= 1) if ((expected & f) && !(desired & f)) words[c][f >> 1] = 0;
                dsp_mask[c] = desired;
            }
        } else if (op == 10u) reject = 1;
        flags[c] = ((flags[c] ^ 1u) & 1u) | (reject ? 2u : 0u);
        dl_frame();
    }
}
static void run(unsigned n) { while (n--) { modwerk_controller_tick(); dsp(); dsp(); } }
static void pump(void) { dsp(); }
static const struct mu_backend *loader = &modwerk_runtime_backend;
static enum mu_publication install(const uint8_t *data, unsigned length)
{
    assert(loader->enter(0) && loader->prepare(0, data, length));
    enum mu_publication p = loader->publish(0);
    if (p == MU_APPLIED) assert(loader->retire(0)); else assert(loader->discard(0));
    assert(loader->leave(0));
    return p;
}
static enum runtime_refusal refused(const uint8_t *data, unsigned length)
{
    assert(loader->enter(0));
    int ok = loader->prepare(0, data, length);
    enum runtime_refusal why = RUNTIME_OK;
    if (!ok) why = modwerk_runtime_refusal();
    else { enum mu_publication p = loader->publish(0); assert(p == MU_UNCHANGED); why = modwerk_runtime_refusal(); assert(loader->discard(0)); }
    assert(loader->leave(0));
    return why;
}
static uint8_t empty[32];
static const uint8_t *removal(uint32_t module)
{
    memset(empty, 0, sizeof empty); memcpy(empty, "MWRM", 4); empty[5] = 4;
    for (unsigned k = 0; k < 4; ++k) empty[28 + k] = (uint8_t)(module >> (24 - 8 * k));
    return empty;
}
static const struct mw_controller_slot *slot_for(uint32_t module, unsigned state)
{
    for (unsigned i = 0; i < MW_CONTROLLER_SLOTS; ++i)
        if (modwerk_controller_registry.slots[i].binding.identity.module == module && modwerk_controller_registry.slots[i].state == state)
            return &modwerk_controller_registry.slots[i];
    return 0;
}
static void remove_module(uint32_t module)
{
    assert(refused(removal(module), 32) == RUNTIME_BUSY);
    run(20);
    assert(install(removal(module), 32) == MU_APPLIED);
    run(20);
}
#define SC 0x95cff696u
#define MATRIX 0xcaf158b5u
#define AB 0xabdb1445u
#define K(f) ((f) == 1u ? 0u : (f) == 2u ? 1u : 2u)
/* Placed exactly: the base word the receiver keeps names the engine's table offset, P holds every relocated word,
 * and the words a placement at the arena's top must have, made by resident_dsp.relocate, where it sits there. */
static void placed_at(unsigned c, unsigned f, unsigned offset)
{
    const struct mw_engine *e = &mw_engines[c][K(f)];
    const struct mw_engine_unit *u = &mw_engine_units[c][K(f)];
    assert(e->state == MW_ENGINE_PLACED && e->offset == offset);
    unsigned base = MODWERK_DSP_TABLE0 + 64u + offset;
    assert(base_word[c][K(f)] == base);
    static uint32_t want[8192];
    mw_engine_relocate(u, base, want);
    for (unsigned i = 0; i < u->count; ++i) assert(P[c][base + i] == want[i]);
    const uint32_t *top = c == 0 ? (f == 1 ? TOP_0_1 : f == 2 ? TOP_0_2 : TOP_0_4) : (f == 1 ? TOP_1_1 : f == 2 ? TOP_1_2 : TOP_1_4);
    if (offset + u->count == MODWERK_DSP_WORDS0 - 64u) for (unsigned i = 0; i < u->count; ++i) assert(P[c][base + i] == top[i]);
}
static void unplaced(unsigned c, unsigned f)
{
    assert(mw_engines[c][K(f)].state == MW_ENGINE_FREE && !base_word[c][K(f)]);
}
/* Per core, from trail entry `from`: every op of the engine's feature in order. WRITEs into its span, one PLACE,
 * then the RESETs and the enabling CAS. */
static void ordered(unsigned c, unsigned f, unsigned offset, unsigned from)
{
    unsigned stage = 0, written = 0, n = mw_engine_units[c][K(f)].count, at = 64u + offset;
    for (unsigned i = from; i < trails[c]; ++i) {
        const struct entry *t = &trail[c][i];
        if (t->op == 3u && t->w5 >= at && t->w5 < at + n) { assert(stage == 0); written += t->w4; }
        else if (t->op == 10u && t->w7 == 1u && t->w4 == f) { assert(stage == 0 && written == n && t->w5 == at); stage = 1; }
        else if (t->op == 11u && t->w7 == f) { assert(stage == 1 || stage == 2); stage = 2; }
        else if (t->op == 10u && t->w7 == 0u && (t->w5 & ~t->w4 & f)) { assert(stage == 2); stage = 3; }
    }
    assert(stage == 3);
}
static unsigned engine_ops(unsigned c, unsigned from) /* PLACE/RESET/CAS and engine-span WRITEs since `from` */
{
    unsigned n = 0;
    for (unsigned i = from; i < trails[c]; ++i)
        if (trail[c][i].op == 10u || trail[c][i].op == 11u || (trail[c][i].op == 3u && trail[c][i].w5 >= 64u + test_capacity(c))) ++n;
    return n;
}
int main(int argc, char **argv)
{
    assert(argc == 2);
    unsigned mode = (unsigned)strtoul(argv[1], 0, 10);
    memcpy(donor, donor_original, sizeof donor);
    (void)buffers_idle; (void)refuse_cas; (void)test_initialized;
    const unsigned top = MODWERK_DSP_WORDS0 - 64u, sc = top - 388u, ab = sc - 998u, mx = top - 773u;
    test_none(); test_fx(3, 900); test_fx(5, 400); test_fx(6, 400); test_fx(7, 400); test_fx(8, 400); test_fx(9, 300);
    run(2);
    if (mode == 0) {
        /* Place, switch on, run, switch off, unplace, free. */
        assert(install(pkg_sc, sizeof pkg_sc) == MU_APPLIED);
        run(200);
        assert(slot_for(SC, MW_CTL_ACTIVE) && dsp_mask[0] == 1 && dsp_mask[1] == 1);
        for (unsigned c = 0; c < 2; ++c) {
            placed_at(c, 1, sc); ordered(c, 1, sc, 0);
            assert(dl_engine_reserved(c) == 388 && test_capacity(c) == sc && modwerk_dsp_arena_now(c) == sc);
        }
        assert(mw_engines_jobs == 4 && mw_engines_placed_count == 2);
        unsigned from[2] = {trails[0], trails[1]};
        remove_module(SC);
        assert(slot_for(SC, MW_CTL_RELEASED) && !modwerk_controller_held() && !dsp_mask[0] && !dsp_mask[1]);
        for (unsigned c = 0; c < 2; ++c) {
            unplaced(c, 1);
            assert(!dl_engine_reserved(c) && test_capacity(c) == top && modwerk_dsp_arena_now(c) == top);
            /* The disable is ACKed before the unplace. */
            unsigned disabled = 0, gone = 0;
            for (unsigned i = from[c]; i < trails[c]; ++i) {
                if (trail[c][i].op == 10u && !trail[c][i].w7 && (trail[c][i].w4 & 1u) && !(trail[c][i].w5 & 1u)) disabled = i + 1;
                if (trail[c][i].op == 10u && trail[c][i].w7 == 1u && !trail[c][i].w5) gone = i + 1;
            }
            assert(disabled && gone > disabled);
        }
        assert(mw_engines_unplaced_count == 2);
        /* In again: placed afresh at the same spot, activated. */
        assert(install(pkg_sc, sizeof pkg_sc) == MU_APPLIED);
        run(200);
        assert(slot_for(SC, MW_CTL_ACTIVE) && dsp_mask[0] == 1);
        placed_at(0, 1, sc); placed_at(1, 1, sc);
    } else if (mode == 1) {
        /* The guard: nothing is placed or unplaced while the sequencer plays or a pattern change waits. */
        quiet = 0;
        assert(install(pkg_sc, sizeof pkg_sc) == MU_APPLIED);
        run(300);
        assert(slot_for(SC, MW_CTL_BOUND) && !mw_engines_jobs && !trails[0] && !trails[1] && !dl_engine_reserved(0));
        assert(!words[0][0] && !dsp_mask[0]);
        quiet = 1;
        run(200);
        assert(slot_for(SC, MW_CTL_ACTIVE)); placed_at(0, 1, sc); placed_at(1, 1, sc);
        assert(refused(removal(SC), 32) == RUNTIME_BUSY);
        run(20);
        quiet = 0; /* the removal's switch, then play */
        assert(install(removal(SC), 32) == MU_APPLIED);
        unsigned jobs = mw_engines_jobs;
        run(300);
        assert(slot_for(SC, MW_CTL_RELEASED) && mw_engines_jobs == jobs && base_word[0][0] && base_word[1][0]);
        assert(mw_engines[0][0].state == MW_ENGINE_PLACED && dl_engine_reserved(0) == 388);
        quiet = 1;
        run(20);
        unplaced(0, 1); unplaced(1, 1);
        assert(!dl_engine_reserved(0) && !dl_engine_reserved(1));
    } else if (mode == 2) {
        /* Full: Sidechain and Analog BD fit on core A; Output Matrix does not, and is refused at admission. */
        assert(install(pkg_sc, sizeof pkg_sc) == MU_APPLIED && install(pkg_ab, sizeof pkg_ab) == MU_APPLIED);
        run(1000);
        assert(slot_for(SC, MW_CTL_ACTIVE) && slot_for(AB, MW_CTL_ACTIVE) && dsp_mask[0] == 5 && dsp_mask[1] == 5);
        for (unsigned c = 0; c < 2; ++c) { placed_at(c, 1, sc); placed_at(c, 4, ab); assert(dl_engine_reserved(c) == 1386 && test_capacity(c) == ab); }
        unsigned jobs = mw_engines_jobs;
        assert(refused(pkg_matrix, sizeof pkg_matrix) == RUNTIME_MEMORY);
        run(50);
        assert(mw_engines_jobs == jobs && !modwerk_controller_held_matrix());
        /* Analog BD out: Output Matrix fits where it was. */
        remove_module(AB);
        run(20);
        unplaced(0, 4); unplaced(1, 4);
        assert(dl_engine_reserved(0) == 388 && dl_engine_reserved(1) == 388);
        assert(install(pkg_matrix, sizeof pkg_matrix) == MU_APPLIED);
        run(300);
        assert(slot_for(MATRIX, MW_CTL_ACTIVE) && dsp_mask[0] == 3 && dsp_mask[1] == 1);
        placed_at(0, 2, sc - 773u);
        assert(mw_engines[1][1].state == MW_ENGINE_FREE && dl_engine_reserved(0) == 388 + 773 && dl_engine_reserved(1) == 388);
    } else if (mode == 3) {
        /* Live FX code where the engine goes: refused until it is gone (no evacuation in this slice). */
        uint8_t ids[16]; memset(ids, 0, sizeof ids);
        ids[4] = 3; /* core A (T5 FX1): 900 words, a quarter of the arena or more, so from the top */
        memcpy(test_parts[0], ids, 16);
        assert(test_select(ids, pump) == 1);
        assert(test_live(0, 3) == (int)(top - 900u));
        assert(refused(pkg_sc, sizeof pkg_sc) == RUNTIME_MEMORY);
        run(50);
        assert(!mw_engines_jobs && !dl_engine_reserved(0));
        ids[4] = 0; memset(test_parts[0], 0, 16);
        assert(test_select(ids, pump) == 1 && test_live(0, 3) < 0);
        assert(install(pkg_sc, sizeof pkg_sc) == MU_APPLIED);
        run(200);
        assert(slot_for(SC, MW_CTL_ACTIVE)); placed_at(0, 1, sc);
        /* Once placed, a pick of that effect loads below the engines. */
        ids[4] = 3; memcpy(test_parts[0], ids, 16);
        assert(test_select(ids, pump) == 1 && test_live(0, 3) == (int)(sc - 900u));
    } else if (mode == 4) {
        /* The bank's Part union: four stock effects of 400 words fit the whole arena (1,600 of 1,936 words) but not
         * under Sidechain's engine (1,548): refused, so that no Part switch has to load code because of it. */
        memset(test_parts, 0, sizeof test_parts);
        test_parts[0][4] = 5; test_parts[1][5] = 6; test_parts[2][6] = 7; test_parts[3][7] = 8;
        assert(refused(pkg_sc, sizeof pkg_sc) == RUNTIME_MEMORY);
        assert(!dl_engine_reserved(0) && !mw_engines_jobs);
        test_parts[3][7] = 0; /* three of them: 1,200 words */
        assert(install(pkg_sc, sizeof pkg_sc) == MU_APPLIED);
        run(200);
        assert(slot_for(SC, MW_CTL_ACTIVE)); placed_at(0, 1, sc);
    } else if (mode == 5) {
        /* Rollback part way: core B's engine WRITE is refused. Its span goes back, core A stays placed; nothing is
         * reset or enabled anywhere; the removal unplaces core A and frees it. */
        refuse_write[1] = 64u + sc + 24u; /* its second chunk */
        assert(install(pkg_sc, sizeof pkg_sc) == MU_APPLIED);
        run(300);
        placed_at(0, 1, sc);
        assert(mw_engines[1][0].state == MW_ENGINE_FREE && !base_word[1][0] && !dl_engine_reserved(1) && dl_engine_reserved(0) == 388);
        assert(slot_for(SC, MW_CTL_BOUND) && !words[0][0] && !words[1][0] && !cas_count && !dsp_mask[0]);
        assert(install(removal(SC), 32) == MU_APPLIED); /* never touched: no disable needed */
        run(20);
        assert(slot_for(SC, MW_CTL_RELEASED));
        unplaced(0, 1);
        assert(!dl_engine_reserved(0) && test_capacity(0) == top);
    } else if (mode == 6) {
        /* An uncertain PLACE (refused on core A): the span stays for this boot, the feature is never enabled, and a
         * later controller of the feature is refused at admission. */
        refuse_place[0] = 64u + sc;
        assert(install(pkg_sc, sizeof pkg_sc) == MU_APPLIED);
        run(300);
        assert(mw_engines[0][0].state == MW_ENGINE_STUCK && dl_engine_reserved(0) == 388 && test_capacity(0) == sc);
        placed_at(1, 1, sc);
        assert(slot_for(SC, MW_CTL_BOUND) && !cas_count && !words[0][0] && !words[1][0]);
        assert(install(removal(SC), 32) == MU_APPLIED);
        run(20);
        assert(mw_engines[0][0].state == MW_ENGINE_STUCK && dl_engine_reserved(0) == 388);
        unplaced(1, 1);
        assert(!dl_engine_reserved(1));
        assert(refused(pkg_sc, sizeof pkg_sc) == RUNTIME_CONFLICT);
    } else if (mode == 7) {
        /* Part switches: the bank's union loads once; switching among its Parts afterwards starts no engine job,
         * changes no reserve or capacity, sends no PLACE, RESET or CAS and writes nothing at all. */
        memset(test_parts, 0, sizeof test_parts);
        test_parts[0][4] = 5; test_parts[1][4] = 6; test_parts[2][12] = 9; test_parts[3][1] = 7;
        assert(install(pkg_sc, sizeof pkg_sc) == MU_APPLIED);
        run(200);
        assert(slot_for(SC, MW_CTL_ACTIVE));
        uint8_t part[4][16];
        memcpy(part, test_parts, sizeof part);
        assert(test_select(part[0], pump) == 1); /* the first transaction loads the whole union */
        assert(test_live(0, 5) >= 0 && test_live(0, 6) >= 0 && test_live(0, 9) >= 0 && test_live(1, 7) >= 0);
        unsigned jobs = mw_engines_jobs, from[2] = {trails[0], trails[1]}, reserved[2] = {dl_engine_reserved(0), dl_engine_reserved(1)};
        static uint32_t region[2][2048];
        for (unsigned c = 0; c < 2; ++c) memcpy(region[c], &P[c][MODWERK_DSP_TABLE0 + 64u + sc], 388 * 4);
        for (unsigned n = 0; n < 12; ++n) {
            assert(test_select(part[n % 4], pump) == 1);
            run(5);
        }
        for (unsigned c = 0; c < 2; ++c) {
            assert(dl_engine_reserved(c) == reserved[c] && test_capacity(c) == sc && !engine_ops(c, from[c]));
            for (unsigned i = from[c]; i < trails[c]; ++i) assert(trail[c][i].op != 3u); /* no code load at all */
            assert(!memcmp(region[c], &P[c][MODWERK_DSP_TABLE0 + 64u + sc], 388 * 4));
        }
        assert(mw_engines_jobs == jobs && slot_for(SC, MW_CTL_ACTIVE) && dsp_mask[0] == 1 && dsp_mask[1] == 1);
    } else if (mode == 8) {
        /* A successor of the same feature adopts the placed engine: no new job, the same words. */
        assert(install(pkg_sc, sizeof pkg_sc) == MU_APPLIED);
        run(200);
        unsigned jobs = mw_engines_jobs;
        assert(refused(pkg_sc2, sizeof pkg_sc2) == RUNTIME_BUSY);
        run(20);
        assert(install(pkg_sc2, sizeof pkg_sc2) == MU_APPLIED);
        run(300);
        const struct mw_controller_slot *next = slot_for(SC, MW_CTL_ACTIVE);
        assert(next && next->binding.image_bytes == 96 && slot_for(SC, MW_CTL_RELEASED));
        assert(mw_engines_jobs == jobs && dsp_mask[0] == 1 && dsp_mask[1] == 1);
        placed_at(0, 1, sc); placed_at(1, 1, sc);
    } else if (mode == 9) {
        /* A hole: Sidechain (top) out while Analog BD (below it) stays: the reserve stays at Analog BD; Sidechain
         * back in reuses the hole without a claim. */
        assert(install(pkg_sc, sizeof pkg_sc) == MU_APPLIED && install(pkg_ab, sizeof pkg_ab) == MU_APPLIED);
        run(1000);
        remove_module(SC);
        run(20);
        unplaced(0, 1); unplaced(1, 1);
        placed_at(0, 4, ab); placed_at(1, 4, ab);
        assert(dl_engine_reserved(0) == 1386 && test_capacity(0) == ab);
        assert(install(pkg_sc, sizeof pkg_sc) == MU_APPLIED);
        run(300);
        placed_at(0, 1, sc); placed_at(1, 1, sc);
        assert(slot_for(SC, MW_CTL_ACTIVE) && dsp_mask[0] == 5 && dl_engine_reserved(0) == 1386);
        remove_module(AB);
        run(20);
        unplaced(0, 4);
        assert(dl_engine_reserved(0) == 388 && test_capacity(0) == sc);
    } else if (mode == 10) {
        /* Output Matrix alone: core A only, at the top. */
        assert(install(pkg_matrix, sizeof pkg_matrix) == MU_APPLIED);
        run(300);
        assert(slot_for(MATRIX, MW_CTL_ACTIVE) && dsp_mask[0] == 2 && !dsp_mask[1]);
        placed_at(0, 2, mx); ordered(0, 2, mx, 0);
        assert(dl_engine_reserved(0) == 773 && !dl_engine_reserved(1) && !trails[1]);
    } else assert(0);
    return 0;
}
'''


def generated(work, units):
    spec = importlib.util.spec_from_file_location('resident_engines_board_core', ELEK / 'build_core.py')
    core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core)
    for name in core.DYNLOAD_SOURCES:
        text = reference = (core.DYNLOAD / name).read_text()
        for old, new in core.DSP_EDITS.get(name, ()) + core.WIDTH_EDITS.get(name, ()):
            assert text.count(old) == 1, name
            text = text.replace(old, new)
        if name == 'buffers.c':
            text = resident_placement.buffers(text)
        elif name == 'manager.c':
            text = resident_engines.manager(resident_journal.manager(resident_placement.manager(text)))
        elif name == 'transfer.c':
            text = resident_engines.transport(resident_driver.transport(text))
        elif name == 'transfer.h':
            text = resident_driver.transport_header(text)
        if name in zero_state.UNITS:
            text = zero_state.unit(name, text, reference)
        if name == 'transfer.c':
            text = text.replace('*(volatile uint32_t *)0xfc07c00cu', 'test_clock')
        if name == 'manager.c':  # the bank's Parts and the queued bank and pattern are the fixture's
            for old, new in (('uint32_t bank=*(volatile uint32_t *)0x46c82456u;\n    for(unsigned c=0;c<2;++c) keep[c]',
                              'extern uint32_t test_bank;uint32_t bank=test_bank;\n    for(unsigned c=0;c<2;++c) keep[c]'),
                             ('unsigned qb=*(volatile uint8_t *)0x800065bfu,qp=*(volatile uint8_t *)0x800065c0u,qpart=4u;',
                              'extern uint8_t test_qb,test_qp,test_parts[4][16];unsigned qb=test_qb,qp=test_qp,qpart=4u;'),
                             (': bank ? *(volatile uint8_t *)(uintptr_t)(bank+0x8ed80u+n*6322u+i) : 255u;',
                              ': bank ? test_parts[n][i] : 255u;')):
                assert text.count(old) == 1, old
                text = text.replace(old, new)
        (work / name).write_text(text)
    (work / 'manager_unit.c').write_text(MANAGER_UNIT)
    (work / 'resident-engines-data.c').write_text(resident_engines.data_c(units))
    (work / 'expected.h').write_text(expected(units))
    shutil.copyfile(ELEK / 'fxids.h', work / 'fxids.h')
    (work / 'packages.h').write_text(board.header())
    preamble = board.FIXTURE.split('/* Modelled receiver')[0]
    (work / 'fixture.c').write_text(preamble + 'unsigned modwerk_dsp_arena_now(unsigned);\n'
                                    'static int modwerk_controller_held_matrix(void) { return (modwerk_controller_held() & 2u) != 0; }\n'
                                    + MODEL)


def build(work):
    flags = ['-std=c11', '-Wall', '-Wextra', '-Werror', *SANITIZE, '-fno-omit-frame-pointer',
             '-DDL_NATIVE_TEST', '-DMW_CONTROLLER_TRANSPORT_TEST', '-DMW_CONTROLLER_BOARD_TEST', '-DMW_ENGINES_TEST',
             '-DMODWERK_RESIDENT_STOCK_HOOKS', '-DMODWERK_RESIDENT_ON_DEMAND',
             '-DMODWERK_RUNTIME_METADATA_EXTERNAL', '-DMODWERK_FX_IDS=64', '-DMODWERK_DSP_TABLE0=%d' % TABLE,
             '-DMODWERK_DSP_TABLE1=%d' % TABLE, '-DMODWERK_DSP_WORDS0=%d' % WORDS, '-DMODWERK_DSP_WORDS1=%d' % WORDS,
             '-DMODWERK_DSP_ALLOWANCE0=3120', '-DMODWERK_DSP_ALLOWANCE1=3565', '-DBOARD_ROWS', '-DBOARD_MANAGER',
             '-I' + str(work), '-I' + str(POLICY), '-I' + str(ADAPTER), '-I' + str(RUNTIME), '-I' + str(ELEK),
             '-I' + str(ROOT / 'sdk/runtime/loader'), '-I' + str(ROOT / 'sdk/runtime/upload')]
    out = work / 'engines-board'
    sources = [work / 'fixture.c', POLICY / 'controller_board.c', POLICY / 'controller_transport.c',
               POLICY / 'controller_association.c', ROOT / 'sdk/runtime/loader/loader.c', ROOT / 'sdk/runtime/upload/sha256.c',
               ADAPTER / 'machine_lifetime.c', work / 'manager_unit.c', work / 'allocator.c', work / 'buffers.c',
               RUNTIME / 'stock_hooks.c', RUNTIME / 'stock_hook_resources.c', RUNTIME / 'resident_engines.c',
               work / 'resident-engines-data.c']
    return out, subprocess.run(['cc', *flags, *map(str, sources), '-o', str(out)], capture_output=True, text=True)


@unittest.skipUnless(shutil.which('cc'), 'host C compiler unavailable')
class ResidentEnginesBoard(unittest.TestCase):
    MODES = 11

    def test_place_switch_run_disable_unswitch_free_and_their_refusals(self):
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            generated(work, bundles())
            binary, result = build(work)
            self.assertEqual(result.returncode, 0, result.stderr)
            for mode in range(self.MODES):
                with self.subTest(mode=mode):
                    result = subprocess.run([str(binary), str(mode)], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)

    def test_relocation_in_c_matches_resident_dsp_relocate(self):
        """The base's relocator (mw_engine_relocate) against resident_dsp.relocate, at several bases, on made-up
        units and on the edge words (0, 0xffffff, wrap both ways)."""
        units = [unit('A', 1, 388), unit('A', 2, 773), unit('B', 4, 998)]
        edge = dict(tag='A', feature=1, words=[0, 0xffffff, 5, 0x800000, 0x7fffff, 1],
                    relocations=[0, 1, 2 | 0x8000, 3 | 0x8000, 4, 5 | 0x8000])
        units.append(edge)
        bases = (0, 1, 0x1000, 0x1333, 0x17ff, 0x1c01, 0x1fff, 0xffffff)
        lines = ['#include <stdio.h>', '#include "resident_engines.h"']
        for n, u in enumerate(units):
            data = b''.join(w.to_bytes(3, 'big') for w in u['words'])
            lines += ['static const uint8_t w%d[] = {%s};' % (n, ','.join(map(str, data))),
                      'static const uint16_t r%d[] = {%s};' % (n, ','.join(map(str, u['relocations'])))]
        lines += ['const struct mw_engine_unit mw_engine_units[2][3];', 'uint32_t *const mw_engine_buffer[2];',
                  'static const struct mw_engine_unit units[] = {%s};' % ','.join(
                      '{w%d, r%d, %d, %d}' % (n, n, len(u['words']), len(u['relocations'])) for n, u in enumerate(units)),
                  'static uint32_t out[2048];',
                  'int main(void) {',
                  '    static const uint32_t bases[] = {%s};' % ','.join('%du' % b for b in bases),
                  '    for (unsigned n = 0; n < %d; ++n) for (unsigned b = 0; b < %d; ++b) {' % (len(units), len(bases)),
                  '        mw_engine_relocate(&units[n], bases[b], out);',
                  '        for (unsigned i = 0; i < units[n].count; ++i) printf("%u ", (unsigned)out[i]);',
                  '        printf("\\n");', '    }', '    return 0;', '}']
        stubs = r'''
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
'''
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp)
            spec = importlib.util.spec_from_file_location('resident_engines_reloc_core', ELEK / 'build_core.py')
            core = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(core)
            for name in ('transfer.h',):
                (work / name).write_text(resident_driver.transport_header((core.DYNLOAD / name).read_text()))
            shutil.copyfile(ELEK / 'fxids.h', work / 'fxids.h')
            (work / 'main.c').write_text('\n'.join(lines) + '\n')
            (work / 'stubs.c').write_text(stubs)
            out = work / 'reloc'
            result = subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror', *SANITIZE, '-DMW_ENGINES_TEST',
                                     '-DMODWERK_FX_IDS=64', '-I' + str(work), '-I' + str(RUNTIME), str(work / 'main.c'),
                                     str(work / 'stubs.c'), str(RUNTIME / 'resident_engines.c'), '-o', str(out)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            rows = subprocess.run([str(out)], capture_output=True, text=True, check=True).stdout.splitlines()
        k = 0
        for u in units:
            for base in bases:
                self.assertEqual(list(map(int, rows[k].split())), resident_dsp.relocate(u, base), (u['feature'], base))
                k += 1
        # And the made-up units' proofs (resident_dsp's own words at the four proof bases) are what data_c accepts.
        text = resident_engines.data_c(bundles())
        self.assertIn('mw_engine_units[2][3]', text)
        broken = bundles()
        broken['A']['engines'][1]['words'][0] ^= 1
        with self.assertRaisesRegex(ValueError, 'not the unit its proofs name'):
            resident_engines.data_c(broken)
        broken = bundles()
        broken['B']['engines'][4]['relocations'].reverse()
        with self.assertRaisesRegex(ValueError, 'unordered relocations'):
            resident_engines.data_c(broken)

    def test_seams_apply_once_and_only_to_their_sources(self):
        spec = importlib.util.spec_from_file_location('resident_engines_seam_core', ELEK / 'build_core.py')
        core = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(core)
        texts = {}
        for name in ('manager.c', 'transfer.c'):
            text = (core.DYNLOAD / name).read_text()
            for old, new in core.DSP_EDITS.get(name, ()) + core.WIDTH_EDITS.get(name, ()):
                text = text.replace(old, new)
            texts[name] = text
        manager = resident_journal.manager(resident_placement.manager(texts['manager.c']))
        once = resident_engines.manager(manager)
        self.assertIn('int dl_engine_claim(unsigned c,unsigned reserve,int commit)', once)
        self.assertIn('dl_pool_words[c]-DL_CODE_START-engine_reserved[c]', once)
        with self.assertRaisesRegex(ValueError, 'seam changed'):
            resident_engines.manager(once)
        transfer = resident_driver.transport(texts['transfer.c'])
        placed = resident_engines.transport(transfer)
        self.assertIn('proc==1u && ((id!=1u && id!=2u && id!=4u)', placed)
        with self.assertRaisesRegex(ValueError, 'seam changed'):
            resident_engines.transport(placed)
        # The default resident transport keeps refusing every op-10 packet with a nonzero word 7.
        self.assertIn('init&~(c ? 5u:7u) || proc)) return 0;', transfer)
        status = resident_engines.status((ELEK / 'status.c').read_text())
        self.assertNotIn('modwerk_dsp_arena[0]', status.split('unsigned modwerk_dsp_arena_now(unsigned);')[1])
        import resident_source
        dsp = resident_engines.dsp(resident_source.sources()['dsp.c'])
        self.assertIn('out->arena = modwerk_dsp_arena_now(c);', dsp)


if __name__ == '__main__':
    unittest.main()
