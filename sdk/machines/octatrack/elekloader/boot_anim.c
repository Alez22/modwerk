/* SPDX-License-Identifier: GPL-3.0-or-later
 * Copyright (C) 2026 Modwerk contributors
 *
 * The base's startup, in place of the stock logo loop: boot_anim.s jumps here from the loop's first
 * instruction (0x400559c6) and goes on with the stock code after the loop (0x40055b7e), which resets
 * every LED. After Manfred Mohr's hypercubes.
 *
 * A seed pixel; a four-dimensional cube unfolds out of it, past the edges of the screen and over the
 * panel, and tumbles back in. It comes to rest in the one orientation in which its sixteen corners fall
 * on a 3 x 3 grid: the Modwerk mark. Its edges drop away one by one, the corners grow into the tiles,
 * the corner (1,1,1,1) slips out of the grid as the detached tile and its momentum carries on across the
 * panel, the frame closes, the wordmark wipes in and NEW and the version are typed.
 *
 * The LEDs are the world beyond the screen: the panel is one plane with the LCD in it (54.2 hundredths
 * of a millimetre per pixel, lamp positions from the stock lamp table), and each lamp glows where the
 * cube's edges cross it. One channel only, so it stays monochrome. Drawing goes through ev_draw on the
 * frame the compositor builds (bus.s); time is the free-running DTIM3 count, as in the stock loop. */
#include <stdint.h>
#include "boot_art.h"

#ifdef MODWERK_HOST
void host_clear(void *window, int a, int b);
void host_compose(void);
void host_led_on(int id), host_led_off(int id), host_led_level(int id, int level), host_led_send(void);
extern volatile uint32_t host_dtcn3;
extern uint32_t host_mkii;
extern int32_t host_lamps[];
#define lcd_clear host_clear
#define lcd_compose host_compose
#define led_on host_led_on
#define led_off host_led_off
#define led_level host_led_level
#define led_send host_led_send
#define DTCN3 host_dtcn3
#define PANEL_MKII host_mkii
#define LAMPS_MKII host_lamps
#define LAMPS_MKI host_lamps
#else
/* OS 1.40C, as the stock logo loop calls them. */
#define lcd_clear ((void (*)(void *, int, int))0x400125ac)  /* (window, 0, -1) blanks it */
#define lcd_compose ((void (*)(void))0x40013abc)            /* windows, then ev_draw, then the changes to the LCD */
#define led_on ((void (*)(int))0x400131a0)
#define led_off ((void (*)(int))0x400131c8)
#define led_level ((void (*)(int, int))0x400135b0)          /* 0-15, sent when it changes */
#define led_send ((void (*)(void))0x400136a8)
#define DTCN3 (*(volatile uint32_t *)0xfc07c00c)           /* 132 MHz; any write clears it */
#define PANEL_MKII (*(volatile uint32_t *)0x46c8d18c)
#define LAMPS_MKII ((const int32_t *)0x400c0d08)            /* lamp (x, y) in 0.01 mm, 67 lamps */
#define LAMPS_MKI ((const int32_t *)0x400c0f20)             /* 44 lamps */
#endif

/* The score, in ms. */
#define T_OUT 120       /* the seed opens */
#define T_IN 1000       /* furthest out; back in from here */
#define T_SNAP 1750     /* corners start to settle on the grid */
#define T_REST 2000     /* at rest: sixteen corners on nine points */
#define T_DIE 2080      /* edges drop away, one every 8 ms */
#define T_DOT0 2060     /* corners grow into tiles */
#define T_DOT1 2260
#define T_DET0 2180     /* the detached tile slips out */
#define T_DET1 2340
#define T_RING0 2150    /* the frame closes, clockwise */
#define T_RING1 2550
#define T_WORD0 2250    /* the wordmark wipes in */
#define T_WORD1 2850
#define T_TYPE0 2450    /* NEW, one letter every 80 ms */
#define T_TYPE1 2730    /* the version, one character every 60 ms */
#define T_BLINK 3200    /* the cursor blinks until here */
#define T_END 3400
#define COMET_MS 900

#define R_EDGE 18       /* px: how far from an edge a lamp still glows */
#define R_COMET 40
#define FADE_MS 220     /* a lamp's afterglow from full to dark */

static int32_t now, on, lamps;
static int32_t vx[16], vy[16];          /* corners on the screen, 1/16 px */
static uint8_t edges[32][2];
static int16_t lamp_x[67], lamp_y[67];  /* lamps in screen pixels */
static int32_t glow[67];                /* 1/16 levels */

static int32_t span(int32_t t, int32_t t0, int32_t t1) /* 0..4096 */
{
    return t <= t0 ? 0 : t >= t1 ? 4096 : (t - t0) * 4096 / (t1 - t0);
}

static int32_t smooth(int32_t u)
{
    return (u * u >> 12) * (3 * 4096 - 2 * u) >> 12;
}

static int32_t lerp(int32_t a, int32_t b, int32_t u)
{
    return a + (b - a) * u / 4096;
}

/* 2^(l/256) in 1/256: the cube's size moves on a log scale. */
static int32_t exp2_q8(int32_t l)
{
    static const uint16_t frac[17] = {256, 267, 279, 291, 304, 317, 331, 345, 362, 378, 395, 412, 431, 450, 470, 490, 512};
    int32_t i = l >> 8, k = (l >> 4) & 15;
    int32_t f = frac[k] + ((frac[k + 1] - frac[k]) * (l & 15) >> 4);
    return i >= 0 ? f << i : f >> -i;
}

static void dot(unsigned char *frame, int32_t x, int32_t y)
{
    if ((uint32_t)x < 128 && (uint32_t)y < 64) {
        int32_t bit = 63 - y;
        frame[x * 8 + (bit >> 3)] |= (unsigned char)(0x80 >> (bit & 7));
    }
}

static int32_t outcode(int32_t x, int32_t y)
{
    return (x < 0) | (x > 127) << 1 | (y < 0) << 2 | (y > 63) << 3;
}

static void line(unsigned char *frame, int32_t x0, int32_t y0, int32_t x1, int32_t y1)
{
    int32_t c0 = outcode(x0, y0), c1 = outcode(x1, y1);
    while (c0 | c1) {   /* Cohen-Sutherland: only the visible part is walked */
        int32_t c = c0 ? c0 : c1, x, y;
        if (c0 & c1)
            return;
        if (c & 8) x = x0 + (x1 - x0) * (63 - y0) / (y1 - y0), y = 63;
        else if (c & 4) x = x0 + (x1 - x0) * (0 - y0) / (y1 - y0), y = 0;
        else if (c & 2) y = y0 + (y1 - y0) * (127 - x0) / (x1 - x0), x = 127;
        else y = y0 + (y1 - y0) * (0 - x0) / (x1 - x0), x = 0;
        if (c == c0) x0 = x, y0 = y, c0 = outcode(x, y);
        else x1 = x, y1 = y, c1 = outcode(x, y);
    }
    int32_t dx = x1 > x0 ? x1 - x0 : x0 - x1, dy = y1 > y0 ? y0 - y1 : y1 - y0;
    int32_t sx = x0 < x1 ? 1 : -1, sy = y0 < y1 ? 1 : -1, err = dx + dy;
    for (;;) {
        dot(frame, x0, y0);
        if (x0 == x1 && y0 == y1)
            return;
        int32_t e2 = 2 * err;
        if (e2 >= dy) err += dy, x0 += sx;
        if (e2 <= dx) err += dx, y0 += sy;
    }
}

static void blob(unsigned char *frame, int32_t cx, int32_t cy, int32_t r) /* all in 1/16 px */
{
    for (int32_t y = (cy - r) >> 4; y <= (cy + r) >> 4; y++)
        for (int32_t x = (cx - r) >> 4; x <= (cx + r) >> 4; x++) {
            int32_t dx = x * 16 + 8 - cx, dy = y * 16 + 8 - cy;
            if (dx * dx + dy * dy <= r * r)
                dot(frame, x, y);
        }
}

static void bits(unsigned char *frame, int32_t x, int32_t y, const uint8_t *rows, int32_t w, int32_t h)
{
    for (int32_t j = 0; j < h; j++)
        for (int32_t i = 0; i < w; i++)
            if (rows[j] >> (w - 1 - i) & 1)
                dot(frame, x + i, y + j);
}

/* Where a corner rests: grid point (b0 + b2, b1 + b3), 8 px apart around the mark's middle. */
static int32_t rest_x(int k) { return (BOOT_MARK_X + 9 + 8 * ((k & 1) + (k >> 2 & 1))) * 16; }
static int32_t rest_y(int k) { return (BOOT_MARK_Y + 9 + 8 * ((k >> 1 & 1) + (k >> 3 & 1))) * 16; }

static int alive(int e, int32_t t)
{
    return t >= T_OUT + (e * 13 % 32) * 18 && t < T_DIE + (e * 7 + 3) % 32 * 8;
}

/* The cube at time t: four-dimensional rotation in all six planes, spinning down onto the one
 * orientation (x+z, y+w) that folds it onto the grid, and a size that breathes out and back in. */
static void place(int32_t t)
{
    static const int8_t plane[6][2] = {{0, 1}, {0, 2}, {0, 3}, {1, 2}, {1, 3}, {2, 3}};
    static const int16_t rest[6] = {0, -128, 0, 0, -128, 0};          /* 1024 per turn */
    static const int16_t spin[6] = {1024, 1536, -768, 1280, 2048, -1024};
    int32_t l, cx = 64 * 16, cy = 32 * 16, home = smooth(span(t, T_IN, T_REST));
    if (t < T_IN)
        l = lerp(-388, 1792, span(t, T_OUT, T_IN));    /* 0.35 px per unit out to 128: the cube spans the panel */
    else
        l = lerp(1792, 640, home);                       /* back to 2^2.5: corners 8 px apart */
    cy = lerp(cy, (BOOT_MARK_Y + 17) * 16, home);
    cx = lerp(cx, (BOOT_MARK_X + 17) * 16, home);
    int32_t s = exp2_q8(l), left = 4096 - smooth(span(t, T_OUT, T_REST)), snap = smooth(span(t, T_SNAP, T_REST));
    int32_t c[6], sn[6];
    for (int p = 0; p < 6; p++) {
        int32_t a = rest[p] + spin[p] * left / 4096;
        sn[p] = boot_sin[a & 1023], c[p] = boot_sin[(a + 256) & 1023];
    }
    for (int k = 0; k < 16; k++) {
        int32_t v[4];
        for (int d = 0; d < 4; d++)
            v[d] = k >> d & 1 ? 4096 : -4096;
        for (int p = 0; p < 6; p++) {
            int32_t a = v[plane[p][0]], b = v[plane[p][1]];
            v[plane[p][0]] = (a * c[p] - b * sn[p]) >> 14;
            v[plane[p][1]] = (a * sn[p] + b * c[p]) >> 14;
        }
        int32_t x = cx + (v[0] * s >> 16), y = cy + (v[1] * s >> 16);
        x = x < -64000 ? -64000 : x > 64000 ? 64000 : x;   /* 4,000 px either way covers the panel */
        y = y < -64000 ? -64000 : y > 64000 ? 64000 : y;
        vx[k] = lerp(x, rest_x(k), snap), vy[k] = lerp(y, rest_y(k), snap);
    }
    if (t >= T_DET0) {   /* the corner (1,1,1,1) leaves the grid for the detached tile's place */
        int32_t u = smooth(span(t, T_DET0, T_DET1));
        vx[15] = lerp(rest_x(15), BOOT_DISC_X * 16 + BOOT_DISC_W * 8, u);
        vy[15] = lerp(rest_y(15), BOOT_DISC_Y * 16 + BOOT_DISC_H * 8, u);
    }
}

static int32_t appears(int g)
{
    int first = 0;
    while (first < BOOT_GLYPHS && boot_glyph[first].item != boot_glyph[g].item) first++;
    return boot_glyph[g].item ? T_TYPE1 + (g - first) * 60 : T_TYPE0 + g * 80;
}

static void type(unsigned char *frame, int32_t t)
{
    int cursor = -1, next = BOOT_GLYPHS;   /* the cell the cursor sits on; BOOT_GLYPHS = after the last one */
    for (int g = BOOT_GLYPHS - 1; g >= 0; g--) {
        if (t >= appears(g))
            for (int i = 0; i < boot_glyph[g].count; i++)
                dot(frame, boot_ink[boot_glyph[g].first + i][0], boot_ink[boot_glyph[g].first + i][1]);
        else
            next = g;
    }
    /* it waits 140 ms on the first cell of each line, and moves on as each glyph is typed */
    if (next < BOOT_GLYPHS && (t >= appears(next) - 140 || (next > 0 && boot_glyph[next].item == boot_glyph[next - 1].item && t >= appears(next - 1))))
        cursor = next;
    int32_t last = appears(BOOT_GLYPHS - 1);
    if (cursor < 0 && t >= last && t < T_BLINK && ((t - last) / 100 & 1) == 0)
        cursor = BOOT_GLYPHS;
    if (cursor >= 0) {
        const struct boot_glyph *g = &boot_glyph[cursor < BOOT_GLYPHS ? cursor : BOOT_GLYPHS - 1];
        int32_t x = cursor < BOOT_GLYPHS ? g->x : g->x + g->w + 2;
        for (int32_t j = 0; j < g->h; j++)
            for (int32_t i = 0; i < 6; i++)
                dot(frame, x + i, g->y + j);
    }
}

void modwerk_boot_draw(unsigned char *frame)
{
    int32_t t = now;
    if (!on)
        return;
    if (t < T_OUT) {   /* the seed */
        if ((t / 60 & 1) == 0)
            dot(frame, 63, 31);
        return;
    }
    for (int e = 0; e < 32; e++)
        if (alive(e, t))
            line(frame, vx[edges[e][0]] >> 4, vy[edges[e][0]] >> 4, vx[edges[e][1]] >> 4, vy[edges[e][1]] >> 4);
    if (t >= T_DOT0) {
        int32_t r = 8 + 40 * span(t, T_DOT0, T_DOT1) / 4096;   /* 1/2 px to 3 px */
        for (int k = 0; k < 15; k++) {
            if (t < T_DOT1)
                blob(frame, vx[k], vy[k], r);
            else   /* corners that share a grid point draw the same tile */
                bits(frame, (vx[k] >> 4) - 3, (vy[k] >> 4) - 3, boot_tile, 6, 6);
        }
        if (t < T_DET1)
            blob(frame, vx[15], vy[15], r + 8 * span(t, T_DET0, T_DET1) / 4096);
        else
            bits(frame, BOOT_DISC_X, BOOT_DISC_Y, boot_disc, BOOT_DISC_W, BOOT_DISC_H);
    }
    int32_t ring = 256 * span(t, T_RING0, T_RING1) / 4096;
    for (int i = 0; i < BOOT_RING && boot_ring[i][2] < ring; i++)
        dot(frame, boot_ring[i][0], boot_ring[i][1]);
    int32_t columns = 110 * span(t, T_WORD0, T_WORD1) / 4096;
    for (int32_t x = 0; x < columns; x++)
        for (int32_t y = 0; y < 15; y++)
            if (boot_word[x] >> y & 1)
                dot(frame, BOOT_WORD_X + x, BOOT_WORD_Y + y);
    type(frame, t);
}

static int32_t isqrt(uint32_t v)
{
    uint32_t r = 0, b = 1u << 30;
    while (b > v) b >>= 2;
    for (; b; b >>= 2)
        if (v >= r + b) v -= r + b, r = (r >> 1) + b;
        else r >>= 1;
    return (int32_t)r;
}

static int32_t segment(int32_t px, int32_t py, int32_t ax, int32_t ay, int32_t bx, int32_t by)
{
    int32_t dx = bx - ax, dy = by - ay, qx = px - ax, qy = py - ay;
    int32_t along = qx * dx + qy * dy, len2 = dx * dx + dy * dy;
    if (along <= 0 || len2 == 0)
        return isqrt((uint32_t)(qx * qx + qy * qy));
    if (along >= len2)
        return isqrt((uint32_t)((px - bx) * (px - bx) + (py - by) * (py - by)));
    int32_t cross = qx * dy - qy * dx;
    return (cross < 0 ? -cross : cross) / isqrt((uint32_t)len2);
}

static void light(int32_t t, int32_t dt)
{
    int32_t comet = t >= T_DET0 && t < T_DET0 + COMET_MS, kx = 0, ky = 0;
    if (comet) {   /* the detached tile's momentum, on past the screen towards the lower right */
        kx = BOOT_DISC_X + BOOT_DISC_W / 2 + (t - T_DET0) * 41 / 100;
        ky = BOOT_DISC_Y + BOOT_DISC_H / 2 + (t - T_DET0) * 28 / 100;
    }
    for (int i = 0; i < lamps; i++) {
        int32_t px = lamp_x[i], py = lamp_y[i], best = 0;
        for (int e = 0; e < 32; e++) {
            if (!alive(e, t))
                continue;
            int32_t ax = vx[edges[e][0]] >> 4, ay = vy[edges[e][0]] >> 4, bx = vx[edges[e][1]] >> 4, by = vy[edges[e][1]] >> 4;
            if (px < (ax < bx ? ax : bx) - R_EDGE || px > (ax > bx ? ax : bx) + R_EDGE ||
                py < (ay < by ? ay : by) - R_EDGE || py > (ay > by ? ay : by) + R_EDGE)
                continue;
            int32_t d = segment(px, py, ax, ay, bx, by), level = 15 - d * 15 / R_EDGE;
            if (level > best) best = level;
        }
        if (comet) {
            int32_t d = isqrt((uint32_t)((px - kx) * (px - kx) + (py - ky) * (py - ky))), level = 15 - d * 15 / R_COMET;
            if (level > best) best = level;
        }
        int32_t g = glow[i] - dt * 16 * 15 / FADE_MS;
        glow[i] = best * 16 > g ? best * 16 : g < 0 ? 0 : g;
        led_level(2 * i, glow[i] >> 4);
    }
}

void modwerk_boot_run(void *window)
{
    const int32_t *table = PANEL_MKII ? LAMPS_MKII : LAMPS_MKI;
    /* Where the LCD's top left corner sits on each panel, in the table's units. The MKII's is measured
     * against the panel drawing; the MKI's is an estimate from its lamp layout. */
    int32_t x0 = PANEL_MKII ? 12627 : 9332, y0 = PANEL_MKII ? 13659 : 12734, n = 0, then = 0;
    lamps = PANEL_MKII ? 67 : 44;
    for (int i = 0; i < lamps; i++) {
        lamp_x[i] = (int16_t)((table[2 * i] - x0) * 10 / 542);
        lamp_y[i] = (int16_t)((y0 - table[2 * i + 1]) * 10 / 542);
        glow[i] = 0;
    }
    for (int k = 0; k < 16; k++)
        for (int d = 0; d < 4; d++)
            if (!(k >> d & 1))
                edges[n][0] = (uint8_t)k, edges[n][1] = (uint8_t)(k | 1 << d), n++;
    for (int id = 0; id < 2 * lamps; id++)
        led_level(id, 0);
    for (int i = 0; i < lamps; i++)
        led_on(2 * i), led_off(2 * i + 1);
    led_send();
    DTCN3 = 0;
    on = 1;
    for (;;) {
        int32_t t = (int32_t)(DTCN3 / 132000u);
        if (t >= T_END)
            break;
        now = t;
        place(t);
        lcd_clear(window, 0, -1);
        lcd_compose();
        light(t, t - then);
        led_send();
        then = t;
    }
    on = 0;
}
