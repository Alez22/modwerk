/* SPDX-License-Identifier: GPL-3.0-or-later
 * Host check of status.c's slot meter (build_core.py --slot-meter): nothing is armed or read for slots until a host
 * asks (MWLD v2), each core then watches its running slots in turn, a reading counts only when both words carry
 * the watched slot's key and no pick landed during the read, the v2 record carries them, and the meter stops once
 * nobody asks. */
#include "status.c"
#include <stdio.h>

static unsigned failures;
#define CHECK(x) do { if (!(x)) { failures++; fprintf(stderr, "%s:%d: %s\n", __FILE__, __LINE__, #x); } } while (0)
volatile uint32_t dl_frames, dl_residency_words[2], modwerk_dsp_meter_bits, modwerk_dsp_meter[7];
volatile int32_t modwerk_dsp_meter_core = -1;
const uint16_t modwerk_dsp_arena[2];
/* dsp.c's reads: the last request, completed by the test. */
static int read_core = -1;
static unsigned read_first, read_words_asked, reads;
int modwerk_dsp_meter_read(unsigned core, unsigned first, unsigned words)
{
    read_core = (int)core, read_first = first, read_words_asked = words, ++reads;
    modwerk_dsp_meter_core = (int32_t)core, modwerk_dsp_meter_bits = 0;
    return 1;
}
/* dsp.c's METER: every request answered at once; id 9 runs nothing. */
volatile int32_t modwerk_dsp_slot_armed[2];
static unsigned arms, arm_core_last, arm_id_last, arm_key_last;
int modwerk_dsp_slot_arm(unsigned core, unsigned id, unsigned key)
{
    ++arms, arm_core_last = core, arm_id_last = id, arm_key_last = key;
    modwerk_dsp_slot_armed[core] = key && id == 9u ? -1 : 1;
    return 1;
}
uint32_t dl_buffers_in_use(void) { return 0; }
unsigned modwerk_runtime_active(void) { return 0; }
volatile struct selftest modwerk_selftest;
volatile uint32_t modwerk_selftest_key;
void modwerk_test_close_menu(void) {}
int modwerk_selftest_start(void) { return 1; }
void modwerk_selftest_abort(void) {}
void modwerk_selftest_refresh(void) {}
uint32_t modwerk_runtime_free(uint32_t *largest) { if (largest) *largest = 0; return 0; }
volatile uint32_t modwerk_runtime_ticks;
unsigned modwerk_dsp_missing_list(uint8_t *out, unsigned first, unsigned most)
{
    (void)first, (void)most;
    out[0] = 'M', out[1] = 'W', out[2] = 'M', out[3] = 0;
    return 4u;
}
int modwerk_modset_restored(void) { return 0; }
volatile uint32_t modwerk_modset_result;
uint8_t modwerk_test_live_fx[16];
volatile uint32_t dl_selection_completed, modwerk_boot_accepted;
const fx_set modwerk_fx_modules = {{0}};
unsigned modwerk_dsp_module_loads(struct modwerk_module_load *out) { (void)out; return 0; }

/* One status tick (status.c acts on every 30th call), 30 runtime ticks later. */
static void tick(void)
{
    for (unsigned i = 0; i < 30u; ++i) modwerk_runtime_ticks = modwerk_runtime_ticks + 1u, modwerk_status_tick();
}
/* The pending read completes with these slot words. */
static void answer(uint32_t w5, uint32_t w6)
{
    for (unsigned i = 0; i < 7u; ++i) modwerk_dsp_meter[i] = 0;
    modwerk_dsp_meter[3] = 500u << 10, modwerk_dsp_meter[5] = w5, modwerk_dsp_meter[6] = w6;
    modwerk_dsp_meter_bits = 24u * read_words_asked;
}
static unsigned u16(const uint8_t *p) { return (unsigned)p[0] << 8 | p[1]; }

int main(void)
{
    uint8_t out[MODWERK_LOAD_SLOTS_BYTES];
    modwerk_test_live_fx[0] = 27;      /* T1 FX1: core 1, r7 $6100 */
    modwerk_test_live_fx[8 + 5] = 23;  /* T6 FX2: core 0, position 1, r7 $6500 */
    modwerk_test_live_fx[8 + 6] = 9;   /* T7 FX2: core 0, runs nothing (refused) */
    for (unsigned i = 0; i < 4u; ++i) { tick(); answer(0, 0); }
    CHECK(!arms && reads && read_first == 1u && read_words_asked == 3u); /* nobody asked: v1's reads only */

    CHECK(modwerk_status_load_slots(out) == 184u && out[4] == 2u && out[7] == 184u && out[0] == 'M' && out[3] == 'D');
    tick(); /* the reading before finishes (3 words); both cores get a slot */
    CHECK(arms == 2u);
    CHECK(watched[1] == 0 && watched[0] == 13);
    answer(0, 0);
    tick(); /* a 6-word read starts on one core */
    CHECK(read_words_asked == 6u && read_first == 1u);
    int core = read_core;
    if (core == 1) answer(0x61u << 16 | 1234u, 0x61u << 16 | 2345u);
    else answer(0x65u << 16 | 1111u, 0x65u << 16 | 2222u);
    tick();
    CHECK(slot_now[core == 1 ? 0 : 13].state == 1u && slot_now[core == 1 ? 0 : 13].mean == (core == 1 ? 1234u : 1111u));
    /* The other core: a window from before its slot (key 0) does not count. */
    CHECK(read_words_asked == 6u && read_core == (core ^ 1));
    answer(0, 0x65u << 16 | 99u);
    tick();
    CHECK(slot_now[core == 1 ? 13 : 0].state == 2u);
    /* A pick landing during the read discards it. */
    if (read_core == 0 || read_core == 1) {
        unsigned c = (unsigned)read_core, i = c == 1u ? 0u : 13u, key = c == 1u ? 0x61u : 0x65u;
        dl_selection_completed = dl_selection_completed + 1u;
        uint16_t before = slot_now[i].mean;
        answer(key << 16 | 7u, key << 16 | 8u);
        tick();
        CHECK(slot_now[i].mean == before);
    }
    /* Core 0 moves on to T7 FX2 after a reading on T6, which it refuses: shown as not measurable. */
    for (unsigned n = 0; n < 12u; ++n) {
        if (read_core == 0) answer(0x65u << 16 | 1111u, 0x65u << 16 | 2222u); else answer(0x61u << 16 | 1234u, 0x61u << 16 | 2345u);
        tick();
    }
    CHECK(slot_now[13].state == 1u && slot_now[13].mean == 1111u && slot_now[13].peak == 2222u);
    CHECK(slot_now[14].state == 3u);
    CHECK(slot_now[0].state == 1u && slot_now[0].peak == 2345u);
    publish_slots(); publish_load();
    CHECK(modwerk_status_load_slots(out) == 184u);
    CHECK(out[48] == 0u && out[49] == 1u && out[50] == 0x1bu && out[51] == 0x48u); /* 72,520 */
    CHECK(out[52] == 16u && out[53] == 2u);
    const uint8_t *t1 = out + 56, *t6 = out + 56 + 8 * 13, *t7 = out + 56 + 8 * 14, *t2 = out + 56 + 8;
    CHECK(t1[0] == 27u && t1[1] == 1u && u16(t1 + 4) == 1234u && u16(t1 + 6) == 2345u && u16(t1 + 2) < 1000u);
    CHECK(t6[0] == 23u && t6[1] == 1u && u16(t6 + 4) == 1111u);
    CHECK(t7[0] == 9u && t7[1] == 3u && u16(t7 + 2) == 0xffffu);
    CHECK(t2[0] == 0u && t2[1] == 0u);
    /* An effect change on a slot clears its reading. */
    modwerk_test_live_fx[0] = 31;
    tick();
    CHECK(slot_now[0].id == 31u && slot_now[0].state == 2u && !slot_now[0].mean);
    /* Nobody asks for 10 s: both cores stop watching (METER with key 0) and reads go back to three words. */
    for (unsigned n = 0; n < 24u; ++n) { answer(0, 0); tick(); }
    CHECK(arm_key_last == 0u && watched[0] < 0 && watched[1] < 0 && read_words_asked == 3u);
    unsigned before = arms;
    for (unsigned n = 0; n < 6u; ++n) { answer(0, 0); tick(); }
    CHECK(arms == before);
    if (failures) fprintf(stderr, "%u failed\n", failures);
    return failures ? 1 : 0;
}
