/* SPDX-License-Identifier: GPL-3.0-or-later
 * The self-test's record: dsp.c runs the test, status.c shows it, dev.c (request 21) hands it to a host. */
#ifndef MODWERK_SELFTEST_H
#define MODWERK_SELFTEST_H
#include <stdint.h>

enum { SELFTEST_IDLE, SELFTEST_RUNNING, SELFTEST_PASSED, SELFTEST_FAILED };
enum { SELFTEST_CONFIGURATION = 1, SELFTEST_TOGETHER, SELFTEST_STRESS, SELFTEST_RESTORE }; /* phases */
/* failed: what went wrong, bits */
#define SELFTEST_BROKEN 1u       /* a module's stock-code sites no longer hold its patches */
#define SELFTEST_REFUSED 2u      /* a set that ran was refused when placed again */
#define SELFTEST_STOPPED 4u      /* frames stopped */
#define SELFTEST_PEAK 8u         /* a DSP core peaked over 90 % of a frame */
#define SELFTEST_COUNTED 16u     /* a stall, a loader rejection, error or rollback was counted */
#define SELFTEST_NOT_BACK 32u    /* the tracks did not get back what they ran */
#define SELFTEST_ABORTED 64u     /* NO, or the transport started */
#define SELFTEST_NOT_LOADED 128u /* a DSP module did not run even on its own */
#define SELFTEST_CPU 256u        /* the ColdFire peaked over 90 % */

struct selftest {
    uint32_t state, phase, failed;
    uint32_t modules, dsp, intact;  /* modules live, of them with DSP effects, live modules whose sites hold */
    uint32_t ran, peak[2], cpu;     /* DSP modules that ran; peaks per mille: T1-4 (core 1), T5-8 (core 0), the CPU */
    uint32_t done, total;           /* progress: steps done of all */
    uint8_t track[8];               /* each track's effect id in the last batch, 0 none */
};
typedef char selftest_size[sizeof(struct selftest) == 56u ? 1 : -1]; /* not a whole number of 64-byte EP0 packets */
extern volatile struct selftest modwerk_selftest;
int modwerk_selftest_start(void); /* 1 when it started: stopped, the loader idle */
void modwerk_selftest_abort(void);
#endif
