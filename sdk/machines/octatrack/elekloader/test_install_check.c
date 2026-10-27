/* SPDX-License-Identifier: GPL-3.0-or-later
 * Host check of the install check (dsp.c, a sync's self-test: request 21 with value 2), against a modelled DSP: which module's code
 * sits on which core, and the SUM jobs that check it. It jobs_started every module's code that is on a core and only that,
 * names a module whose code does not sum, fails when the frames stop or come late, when the loader is off or counts a
 * stall, rejection or rollback meanwhile, and when a live module's base feature cannot come up. It never touches the
 * live FX set, a knob lane, a Part or the transport, and it runs playing or not. (cc -DMODWERK_HOST
 * -DMODWERK_DSP_ALLOWANCE0=3120 -DMODWERK_DSP_ALLOWANCE1=3565 -DMODWERK_DSP_RESERVE=342) */
#define MODWERK_HOST_SELFTEST
#include "sha256.c"
volatile uint32_t modwerk_flash_refusal; /* flash.c, not linked here */
#include "dsp.c"
int modwerk_runtime_restoring(void) { return 0; } /* loader.c's: no restore here */
volatile uint32_t dl_residency_words[2]; /* manager.c: each core's resident code words (dsp.c's budget box) */
#include "fxmap.c"
#include <stdio.h>
#include <string.h>
const struct fx_legacy modwerk_fx_legacy[] = {{0x873d83ccu, 27, "E-Verb"}};
const uint32_t modwerk_fx_legacy_count = 1;
int modwerk_fxpage_build(unsigned id, uint8_t *recipe, uint32_t bytes, unsigned slots) { (void)id; (void)recipe; (void)bytes; (void)slots; return 1; }
void modwerk_fxpage_drop(unsigned id) { (void)id; }
int modwerk_runtime_owner_snapshot(const uint8_t *p,struct runtime_owner *o) { (void)p;(void)o;return 0; }
int modwerk_runtime_owner_valid(const struct runtime_owner *o) { (void)o;return 0; }
int modwerk_runtime_owner_canonical(const struct runtime_owner *o,uintptr_t *a) { (void)o;(void)a;return 0; }
const struct runtime_module *modwerk_runtime_module(unsigned p) { (void)p;return 0; }
void modwerk_runtime_journal_snapshot(struct runtime_journal_progress *p) { *p=(struct runtime_journal_progress){0}; }
int modwerk_fxpage_validate(unsigned i,const uint8_t *p,uint32_t n,unsigned s) { (void)i;(void)p;(void)n;(void)s;return 0; }
int modwerk_fxpage_current(unsigned i,const uint8_t *p,uint32_t n,unsigned s) { (void)i;(void)p;(void)n;(void)s;return 0; }
int modwerk_fxpage_commit_checked(unsigned i,uint8_t *p,uint32_t n,unsigned s) { (void)i;(void)p;(void)n;(void)s;return 0; }

static unsigned failures;
#define CHECK(x) do { if (!(x)) { failures++; fprintf(stderr, "%s:%d: %s\n", __FILE__, __LINE__, #x); } } while (0)

const fx_set modwerk_fx_modules = {{1u << 26 | 1u << 27 | 1u << 28}};
struct dl_package dl_catalog[MODWERK_FX_IDS];
struct code dl_codes[2][MODWERK_FX_IDS];
const uint16_t modwerk_dsp_arena[2] = {2396, 3269};
static int loader_busy; /* a change is being published: the check does not start */
int dl_publication_idle(void) { return !loader_busy; }
uint32_t dl_slot_cycles(unsigned i) { (void)i; return 0; }

/* What the check reads of the loader and the meters. */
volatile uint8_t dl_intended_override[16];
volatile uint32_t modwerk_status[12], modwerk_status_reads, modwerk_status_fast;
volatile uint32_t dl_residency_rollbacks, dl_residency_failures, dl_frame_gap, dl_frames, dl_rejected[2], dl_errors;
volatile uint32_t dl_residency_enabled = 1;
volatile uint32_t modwerk_modset_generation, modwerk_modset_count, modwerk_modset_result, dl_pool_base[2];
static unsigned modules;
unsigned modwerk_runtime_active(void) { return modules; }
unsigned modwerk_runtime_intact(void) { return modules; }
uint32_t modwerk_runtime_broken(void) { return 0; }
static enum runtime_refusal test_refusal; /* the loader's own last refusal */
enum runtime_refusal modwerk_runtime_refusal(void) { return test_refusal; }
static int test_keybus_lost; /* controller_board.c's answer: a live reader whose key bus cannot come up this boot */
int modwerk_controller_keybus_lost(void) { return test_keybus_lost; }
int modwerk_machine_stopped(void) { return 1; }
static int keys_posted;
void modwerk_post_key(unsigned code, int pressed) { (void)code, (void)pressed; ++keys_posted; }
int dl_bound(unsigned core, unsigned id) { (void)core, (void)id; return 0; }

/* The modelled DSP: placed[c][id] whether id's code sits on core c (at id * 4096), bad: the id whose code does not sum,
 * stuck: SUM jobs never finish, frozen: frames stop. Each job finishes the tick after it starts. */
static uint8_t placed[2][MODWERK_FX_IDS];
static int job[2] = {-2, -2}, pending[2], bad = -1, stuck, frozen;
static unsigned jobs_started, sum_words[MODWERK_FX_IDS];
int dl_placed(unsigned core, unsigned id) { return id < MODWERK_FX_IDS && placed[core][id] ? (int)(id * 4096u) : -1; }
int dl_sum_start(unsigned core, unsigned offset, unsigned count, uint32_t expected)
{
    (void)expected;
    if (job[core] != -2) return 0;
    unsigned id = offset / 4096u;
    sum_words[id] += count, ++jobs_started;
    job[core] = 0, pending[core] = (int)id == bad ? -1 : 1;
    return 1;
}
int dl_job_status(unsigned core) { return job[core]; }
void dl_job_release(unsigned core) { job[core] = -2; }
static void dsp(void)
{
    if (!frozen) ++dl_frames;
    for (unsigned c = 0; c < 2u; ++c) if (job[c] == 0 && !stuck) job[c] = pending[c];
}

static uint32_t code[4096];
static const uint16_t relocations[1];
static struct runtime_dsp none;
static struct runtime_dsp module(uint8_t id, uint32_t words, uint16_t cycles, uint32_t runtime_id, const char *name)
{
    struct runtime_dsp d = {.words = code, .relocations = relocations, .count = words, .init = 1, .proc = 2, .cycles = cycles,
                            .id = id, .slots = 2, .kind = RUNTIME_HARDWARE, .state = 70, .module = runtime_id, .layout = 1};
    for (unsigned i = 0; name[i] && i < 15u; ++i) d.name[i] = name[i];
    return d;
}
static uint8_t bank[0x9504a + 4 * 6322];
static void (*during)(unsigned tick); /* called on every tick of a run, when a check needs the test running */
static unsigned ticks;
/* One run with the modules installed and the live set `live`; the record afterwards. */
static void run(const uint8_t *live, struct runtime_dsp *fx, unsigned n)
{
    for (unsigned k = 0; k < MODWERK_FX_IDS; ++k) release(k);
    for (unsigned k = 0; k < MODWERK_FX_IDS; ++k) dl_catalog[k] = (struct dl_package)STOCK, sum_words[k] = 0;
    for (unsigned k = 0; k < n; ++k) modwerk_machine_dsp_switch(&none, &fx[k]);
    modules = n, jobs_started = 0, keys_posted = 0;
    memcpy(modwerk_test_live_fx, live, 16);
    for (unsigned i = 0; i < sizeof bank; i += 97u) bank[i] = (uint8_t)i;
    modwerk_test_bank = bank;
    static uint8_t before[sizeof bank];
    memcpy(before, bank, sizeof bank);
    CHECK(modwerk_selftest_check());
    for (ticks = 0; modwerk_selftest.state == SELFTEST_RUNNING && ticks < 200000u; ++ticks) {
        dsp(), selftest_tick();
        if (during) during(ticks);
    }
    CHECK(modwerk_selftest.state == SELFTEST_PASSED || modwerk_selftest.state == SELFTEST_FAILED);
    CHECK(!memcmp(modwerk_test_live_fx, live, 16));       /* every slot runs what it ran */
    CHECK(!memcmp(bank, before, sizeof bank) && !keys_posted); /* no Part touched, no key pressed */
    CHECK(job[0] == -2 && job[1] == -2);                   /* no SUM job left behind */
    for (unsigned k = 0; k < n; ++k) modwerk_machine_dsp_switch(&fx[k], &none);
}
static void stall_once(unsigned tick) { if (tick == 10u) ++modwerk_dsp_stalls; }
static void late_frame(unsigned tick) { if (tick == 5u) dl_frame_gap = SELFTEST_FRAME_LIMIT + 1u; }
static void press_no(unsigned tick) { if (tick == FRAMES_TICKS + 1u) modwerk_selftest_abort(); }
int main(void)
{
    (void)rebind_tick; /* test_dsp.c covers it */
    dl_pool_base[0] = dl_pool_base[1] = 0x40;
    const uint8_t blank[16] = {0}, live[16] = {27, 0, 0, 0, 26, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
    struct runtime_dsp pair[3] = {module(27, 1588, 600, 0x873d83ccu, "E-Verb"), module(26, 600, 500, 0x5678u, "Small"),
                                  module(28, 300, 200, 0x1234u, "Idle")};
    /* E-Verb's code on core 1, Small's on core 0 and core 1, Idle's nowhere yet: three jobs_started, every word of each, and Idle
     * is not loaded for it. It passes in about half a second plus the jobs_started, the live set as it was. */
    placed[1][27] = 1, placed[0][26] = placed[1][26] = 1;
    run(live, pair, 3);
    CHECK(modwerk_selftest.state == SELFTEST_PASSED && !modwerk_selftest.failed);
    CHECK(modwerk_selftest.dsp == 3 && modwerk_selftest.ran == 3 && modwerk_selftest.total == 4 && modwerk_selftest.done == 4);
    CHECK(sum_words[27] == 1588 && sum_words[26] == 2 * 600 && !sum_words[28] && jobs_started == 7 + 3 + 3);
    CHECK(ticks < FRAMES_TICKS + 20u);
    /* Damaged code: the SUM fails, the check fails as corrupt and names it. */
    bad = 26;
    run(live, pair, 3);
    bad = -1;
    CHECK(modwerk_selftest.state == SELFTEST_FAILED && modwerk_selftest.failed == SELFTEST_CORRUPT);
    CHECK(modwerk_selftest.culprit == 0x5678u && !strcmp((const char *)modwerk_selftest.culprit_name, "Small"));
    /* No module's code on a core: nothing to sum, it passes. */
    memset(placed, 0, sizeof placed);
    run(blank, pair, 3);
    CHECK(modwerk_selftest.state == SELFTEST_PASSED && !modwerk_selftest.ran && !jobs_started);
    placed[1][27] = 1;
    /* Frames stopped (aox's unit, 27 October 2026: the DSPs stopped after a power-on restore): it fails as stopped after
     * half a second, starts no SUM on a stopped DSP and blames no module. */
    frozen = 1;
    run(live, pair, 3);
    frozen = 0;
    CHECK(modwerk_selftest.state == SELFTEST_FAILED && modwerk_selftest.failed == SELFTEST_STOPPED && !jobs_started && !modwerk_selftest.culprit);
    /* A stall earlier this boot shut the loader off: stopped, whatever else runs. */
    dl_residency_enabled = 0;
    run(live, pair, 3);
    dl_residency_enabled = 1;
    CHECK(modwerk_selftest.state == SELFTEST_FAILED && (modwerk_selftest.failed & SELFTEST_STOPPED));
    /* A stall counted while it ran, and a late frame. */
    during = stall_once;
    run(live, pair, 3);
    CHECK(modwerk_selftest.state == SELFTEST_FAILED && modwerk_selftest.failed == SELFTEST_COUNTED);
    during = late_frame;
    run(live, pair, 3);
    CHECK(modwerk_selftest.state == SELFTEST_FAILED && modwerk_selftest.failed == SELFTEST_LATE);
    /* NO while a SUM runs: stopped, its job released. */
    stuck = 1, during = press_no;
    run(live, pair, 3);
    CHECK(modwerk_selftest.state == SELFTEST_FAILED && modwerk_selftest.failed == SELFTEST_ABORTED);
    /* A SUM channel that never frees is not a verdict: it ends after ten seconds and passes on what it could sum. */
    during = 0;
    run(live, pair, 3);
    stuck = 0;
    CHECK(modwerk_selftest.state == SELFTEST_PASSED && !modwerk_selftest.ran && ticks <= FRAMES_TICKS + CODE_TICKS + 2u);
    /* The meters at the end are a reading, never a verdict: a busy pattern at 100 % passes. */
    modwerk_status[0] = modwerk_status[2] = modwerk_status[4] = 1000u;
    run(live, pair, 3);
    CHECK(modwerk_selftest.state == SELFTEST_PASSED && modwerk_selftest.cpu == 1000u && modwerk_selftest.peak[0] == 1000u);
    modwerk_status[0] = modwerk_status[2] = modwerk_status[4] = 0;
    /* While the loader publishes a change it does not start. */
    loader_busy = 1;
    CHECK(!modwerk_selftest_check());
    loader_busy = 0;
    /* A live reader whose key bus was lost this boot: it fails with SELFTEST_FEATURE (a trial is not kept), and the
     * record's refusal says RUNTIME_FEATURE while it holds. */
    test_keybus_lost = 1;
    run(blank, pair, 3);
    CHECK(modwerk_selftest.state == SELFTEST_FAILED && modwerk_selftest.failed == SELFTEST_FEATURE);
    modwerk_selftest_refresh();
    CHECK(modwerk_selftest.refusal == RUNTIME_FEATURE);
    /* The loader's own refusal comes first: the site retries RUNTIME_BUSY and explains a rejected sync from it. */
    test_refusal = RUNTIME_BUSY;
    modwerk_selftest_refresh();
    CHECK(modwerk_selftest.refusal == RUNTIME_BUSY);
    test_refusal = RUNTIME_OK, test_keybus_lost = 0;
    modwerk_selftest_refresh();
    CHECK(modwerk_selftest.refusal == RUNTIME_OK);
    if (failures) { fprintf(stderr, "%u self-test checks failed\n", failures); return 1; }
    puts("Octatrack install check: it sums the code on the cores and only that, names damaged code, fails on stopped or "
         "late frames and loader errors, passes a busy pattern, and touches no slot, Part or key.");
    return 0;
}
