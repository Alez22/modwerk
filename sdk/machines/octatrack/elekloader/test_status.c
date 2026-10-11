/* SPDX-License-Identifier: GPL-3.0-or-later
 * Host check of status.c's keys: with the dialog closed every key reaches stock, TRIG 1 (code 0) included
 * (a release swallowed there left bank changes to pattern 1 undone on the unit, 11 October 2026); CUE +
 * PROJ opens it and takes PROJ's release; NO closes it and takes its own. */
#include "status.c"
#include <stdio.h>

static unsigned failures;
#define CHECK(x) do { if (!(x)) { failures++; fprintf(stderr, "%s:%d: %s\n", __FILE__, __LINE__, #x); } } while (0)
/* What status.c reads from the rest of the base; the keys never touch it. */
volatile uint32_t dl_frames, dl_residency_words[2], modwerk_dsp_meter_bits, modwerk_dsp_meter[5];
volatile int32_t modwerk_dsp_meter_core;
const uint16_t modwerk_dsp_arena[2];
int modwerk_dsp_meter_read(unsigned core, unsigned first, unsigned words) { (void)core, (void)first, (void)words; return 0; }
uint32_t dl_buffers_in_use(void) { return 0; }
unsigned modwerk_runtime_active(void) { return 0; }
volatile struct selftest modwerk_selftest;
volatile uint32_t modwerk_selftest_key;
static int selftest_starts, selftest_aborts, menu_closes;
void modwerk_test_close_menu(void) { ++menu_closes; }
int modwerk_selftest_start(void) { ++selftest_starts; return 1; }
void modwerk_selftest_abort(void) { ++selftest_aborts; }
void modwerk_selftest_refresh(void) {}
uint32_t modwerk_runtime_free(uint32_t *largest) { if (largest) *largest = 0; return 0; }
int main(void)
{
    CHECK(!modwerk_status_key(0, 1) && !modwerk_status_key(0, 0)); /* TRIG 1, dialog closed */
    CHECK(!modwerk_status_key(CUE, 1));
    CHECK(modwerk_status_key(PROJ, 1) && modwerk_status_key(PROJ, 0)); /* CUE + PROJ: open, its release taken */
    CHECK(!modwerk_status_key(CUE, 0));
    CHECK(modwerk_status_key(0, 1) && modwerk_status_key(0, 0));       /* open: keys stay with the dialog */
    CHECK(modwerk_status_key(NO, 1) && modwerk_status_key(NO, 0));     /* NO closes, its release taken */
    CHECK(!modwerk_status_key(0, 1) && !modwerk_status_key(0, 0));     /* closed again: TRIG 1 reaches stock */
    extern int modwerk_test_menu_open;
    modwerk_test_menu(0);                                              /* reached with PROJ's menu closed (a chooser's YES) */
    CHECK(!selftest_starts && !modwerk_status_key(0, 1) && !modwerk_status_key(0, 0)); /* nothing happens */
    modwerk_test_menu_open = 1;
    modwerk_test_menu(0);                                              /* SYSTEM > MODWERK TEST */
    CHECK(!menu_closes); modwerk_status_close_menu(); modwerk_status_close_menu();
    CHECK(menu_closes == 1);                                           /* PROJ's menu closed once, after the row's dispatch */
    CHECK(selftest_starts == 1 && modwerk_status_key(YES, 1) && modwerk_status_key(YES, 0)); /* started; keys stay with the page */
    CHECK(modwerk_status_key(NO, 1) && selftest_aborts == 1 && modwerk_status_key(NO, 0));  /* NO aborts and closes */
    CHECK(!modwerk_status_key(0, 1) && !modwerk_status_key(0, 0));     /* closed: TRIG 1 reaches stock */
    if (failures) return 1;
    puts("status keys: ok");
    return 0;
}
