/* SPDX-License-Identifier: GPL-3.0-or-later
 * The unit's load and memory, live (build_core.py --dsp-loader; owner, 11 October 2026): the ColdFire's load,
 * each DSP core's load (mean and peak), each core's code arena, the delay-buffer blocks in use and the module
 * pool. Measured all the time, cheaply, into modwerk_status[] (the loader report carries it over USB:
 * `npm run device -- stats`); CUE + PROJ shows it as a dialog, NO or CUE + PROJ closes it.
 *
 * ColdFire: main's idle spin (status.s) adds up, in counts of the free-running frame timer DTIM3, each pass
 * nothing broke: load = 1 - idle counts / the counts that went by. DSP: each core's receiver publishes a window
 * of 1,024 frames' idle passes (dsp_receiver.asm), read back by PEEK 24 bits a tick, the cores in turn; a
 * frame is 72,520 cycles. */
#include <stdint.h>
#include "loader.h"

#define CUE 0x2a
#define PROJ 0x1c
#define NO 0x32
#define FRAME_CYCLES 72520u /* 4,532 a sample (the board's clock), 16 samples */
/* Cycles a hundred idle passes take: core 0's main loop and core 1's counted wait (c1wait), each calibrated on the
 * unit with 1,000 more cycles a frame (`--dsp-burn`): 50.0 and 69.1 fewer passes (11 October 2026). */
static const uint32_t idle_cycles[2] = {2000u, 1448u};
enum { CPU, DSP0_MEAN, DSP0_PEAK, DSP1_MEAN, DSP1_PEAK, BUFFERS, POOL_USED, MODULES, WRAP, ARENA, SUM0, SUM1, STATUS_WORDS };
/* WRAP: timer counts a frame; SUM0/1: each core's last window, idle passes summed over 1,024 frames */

extern volatile uint32_t dl_frames, dl_residency_words[2];
extern volatile uint32_t modwerk_dsp_meter_bits, modwerk_dsp_meter[5];
extern volatile int32_t modwerk_dsp_meter_core;
extern const uint16_t modwerk_dsp_arena[2];
int modwerk_dsp_meter_read(unsigned core, unsigned first, unsigned words);
uint32_t dl_buffers_in_use(void); /* manager.c (build_core.py's edit): FX1 and FX2 block masks, core 0 then 1 */
#define DTCN3 (*(volatile uint32_t *)0xfc07c00cu) /* the frame timer's count: free-running, all 32 bits */

/* status.s's: the idle counts so far, and the longest pass that still counts as idle (0 until the first
 * window has measured the timer's rate: nothing counts). */
volatile uint32_t modwerk_idle_counts, modwerk_idle_gap;
volatile uint32_t modwerk_status[STATUS_WORDS]; /* per mille, masks, bytes, counts: the report's tail */
uint32_t modwerk_status_report(uint32_t *out)
{
    for (unsigned i = 0; i < STATUS_WORDS; ++i) out[i] = modwerk_status[i];
    return STATUS_WORDS;
}

/* Busy, per mille, from a core's idle passes a frame. */
static uint32_t busy(unsigned core, uint32_t idle)
{
    uint32_t c = idle * idle_cycles[core] / 100u;
    return c >= FRAME_CYCLES ? 0 : 1000u - c * 1000u / FRAME_CYCLES;
}

static uint32_t last_frames, last_idle, last_count, ticks;
static int reading = -1, read_last = 1; /* the core whose window (least, most, sum) is being read back */
static unsigned waited;
static uint32_t cpu_recent[8];
void modwerk_status_tick(void)
{
    if (++ticks % 30u) return; /* twice a second */
    uint32_t count = DTCN3, frames = dl_frames, idle = modwerk_idle_counts;
    uint32_t counts = count - last_count, df = frames - last_frames, di = idle - last_idle;
    last_count = count, last_frames = frames, last_idle = idle;
    if (df) modwerk_status[WRAP] = counts / df, modwerk_idle_gap = counts / df / 362u + 2u; /* about 1 µs */
    uint32_t per = counts / 1000u;
    modwerk_status[CPU] = per && ticks > 30u && di / per < 1000u ? 1000u - di / per : 0;
    cpu_recent[(ticks / 30u) % 8u] = modwerk_status[CPU]; /* the page's CPU peak: the last four seconds */
    if (reading >= 0) { /* least, most and sum of 1,024 frames, read 24 bits a tick */
        if (modwerk_dsp_meter_core == reading && modwerk_dsp_meter_bits >= 72u) {
            modwerk_status[reading ? DSP1_MEAN : DSP0_MEAN] = busy((unsigned)reading, modwerk_dsp_meter[3] >> 10);
            modwerk_status[reading ? SUM1 : SUM0] = modwerk_dsp_meter[3];
            modwerk_status[reading ? DSP1_PEAK : DSP0_PEAK] = busy((unsigned)reading, modwerk_dsp_meter[1]);
            reading = -1;
        } else if (++waited > 6u) reading = -1; /* the manager took the core: start again */
    }
    if (reading < 0 && modwerk_dsp_meter_read((unsigned)(read_last ^ 1), 1, 3))
        reading = read_last ^= 1, waited = 0;
    uint32_t largest;
    modwerk_status[BUFFERS] = dl_buffers_in_use();
    modwerk_status[POOL_USED] = RUNTIME_POOL_BYTES - modwerk_runtime_free(&largest);
    modwerk_status[MODULES] = modwerk_runtime_active();
    modwerk_status[ARENA] = modwerk_dsp_arena[0] | (uint32_t)modwerk_dsp_arena[1] << 16;
}

/* The modal: while it shows it takes every key and encoder, so nothing changes under it; NO or CUE + PROJ
 * closes it, and the screen it covered is back as it was. */
static int open, taken; /* shown; a key press the handler took, whose release it takes too */
int modwerk_status_key(int code, int pressed)
{
    static int cue;
    if (code == CUE) cue = pressed;
    if (pressed && code == PROJ && cue) { open = !open; taken = code; return 1; }
    if (pressed && code == NO && open) { open = 0; taken = code; return 1; }
    if (!pressed && code == taken) { taken = 0; return 1; }
    return open && code != CUE; /* CUE's own release reaches stock, as it would without the page */
}
int modwerk_status_enc(int encoder, int delta) { (void)encoder, (void)delta; return open; }

/* Drawing: the frame is a quarter turn round, a row of 8 bytes per x, MSB first, pixel (x, y) at bit 63 - y. */
static void fill(unsigned char *frame, unsigned x0, unsigned y0, unsigned x1, unsigned y1, int on) /* inclusive */
{
    for (unsigned x = x0; x <= x1 && x < 128u; ++x)
        for (unsigned y = y0; y <= y1 && y < 64u; ++y) {
            unsigned bit = 63u - y, at = x * 8u + (bit >> 3);
            unsigned char mask = (unsigned char)(0x80u >> (bit & 7u));
            frame[at] = on ? frame[at] | mask : frame[at] & (unsigned char)~mask;
        }
}
static void outline(unsigned char *frame, unsigned x0, unsigned y0, unsigned x1, unsigned y1)
{
    fill(frame, x0, y0, x1, y0, 1), fill(frame, x0, y1, x1, y1, 1), fill(frame, x0, y0, x0, y1, 1), fill(frame, x1, y0, x1, y1, 1);
}
/* A bar w x h at (x, y): its outline, filled to `permille`, a tick through it at `peak` (0 none). */
static void bar(unsigned char *frame, unsigned x, unsigned y, unsigned w, unsigned h, uint32_t permille, uint32_t peak)
{
    outline(frame, x, y, x + w - 1u, y + h - 1u);
    uint32_t n = (w - 2u) * (permille < 1000u ? permille : 1000u) / 1000u;
    if (n) fill(frame, x + 1u, y + 1u, x + n, y + h - 2u, 1);
    if (peak) {
        unsigned at = x + 1u + (unsigned)((w - 3u) * (peak < 1000u ? peak : 1000u) / 1000u);
        fill(frame, at, y - 1u, at, y + h, 1);
    }
}
static char *number(char *s, uint32_t v)
{
    char d[10];
    unsigned n = 0;
    do d[n++] = (char)('0' + v % 10u), v /= 10u; while (v);
    while (n) *s++ = d[--n];
    return s;
}
#define FONT 0x400ba876u     /* the small UI font, 5 px capitals (Octabam's PANEL.md) */
#define SURFACE 0x400bf10au  /* the UI's surface descriptor: copied, with the frame as its picture */
#define DRAW_TEXT ((void (*)(uint32_t, void *, int, int, int, const char *))0x40012bd8u)
static uint32_t surface[7];
/* Text whose capitals' top row is `top` (the text call counts y up from the bottom). */
static void label(unsigned x, unsigned top, const char *t) { DRAW_TEXT(FONT, surface, (int)x, 59 - (int)top, -1, t); }
static void percent(unsigned x, unsigned top, uint32_t permille)
{
    char t[8], *s = number(t, (permille + 5u) / 10u);
    *s++ = '%', *s = 0;
    label(x, top, t);
}
static uint32_t share(uint32_t part, uint32_t whole) { return whole ? (part > whole ? 1000u : part * 1000u / whole) : 0; }
#define TEXT_WIDTH ((int (*)(uint32_t, int, const char *))0x40012f30u) /* (font, limit, str): its width in px */
/* The page, a dialog as stock draws them (a frame over the screen, its title and a rule): three load bars
 * (the ColdFire, then each DSP core by its tracks) with their peaks, then the memory: each core's code arena
 * and the module pool. Bars to read from a distance, numbers to check. */
#define X0 8u
#define X1 119u
#define Y0 1u
#define Y1 62u
void modwerk_status_draw(unsigned char *frame)
{
    if (!open) return;
    for (unsigned i = 0; i < 7u; ++i) surface[i] = ((const volatile uint32_t *)SURFACE)[i];
    surface[3] = (uint32_t)(uintptr_t)frame;
    fill(frame, X0, Y0, X1, Y1, 0);
    outline(frame, X0, Y0, X1, Y1);
    static const char title[] = "MODWERK STATUS";
    label((unsigned)(64 - TEXT_WIDTH(FONT, -1, title) / 2), Y0 + 3u, title);
    fill(frame, X0, Y0 + 10u, X1, Y0 + 10u, 1);
    uint32_t cpu_peak = 0;
    for (unsigned i = 0; i < 8u; ++i) cpu_peak = cpu_recent[i] > cpu_peak ? cpu_recent[i] : cpu_peak;
    static const char *const names[3] = {"CPU", "T1-4", "T5-8"};
    const uint32_t load[3] = {modwerk_status[CPU], modwerk_status[DSP1_MEAN], modwerk_status[DSP0_MEAN]},
                   peak[3] = {cpu_peak, modwerk_status[DSP1_PEAK], modwerk_status[DSP0_PEAK]};
    for (unsigned i = 0; i < 3u; ++i) {
        unsigned y = Y0 + 14u + 8u * i;
        label(X0 + 4u, y, names[i]);
        bar(frame, X0 + 30u, y, 58, 6, load[i], peak[i]);
        percent(X0 + 92u, y, load[i]);
    }
    for (unsigned x = X0 + 4u; x < X1 - 3u; x += 2) fill(frame, x, Y0 + 38u, x, Y0 + 38u, 1);
    uint32_t largest, pool = RUNTIME_POOL_BYTES - modwerk_runtime_free(&largest);
    static const char *const memory[3] = {"P T1-4", "P T5-8", "POOL"};
    const uint32_t used[3] = {share(dl_residency_words[1], modwerk_dsp_arena[1]), share(dl_residency_words[0], modwerk_dsp_arena[0]),
                              share(pool, RUNTIME_POOL_BYTES)};
    for (unsigned i = 0; i < 3u; ++i) {
        unsigned y = Y0 + 42u + 6u * i;
        label(X0 + 4u, y - 1u, memory[i]);
        bar(frame, X0 + 30u, y, 58, 4, used[i], 0);
        percent(X0 + 92u, y - 1u, used[i]);
    }
}
