/* SPDX-License-Identifier: GPL-3.0-or-later
 * Copyright (C) 2026 Modwerk contributors
 *
 * The base's startup, in place of the stock logo loop: boot_anim.s jumps here from the loop's first
 * instruction (0x400559c6) and goes on with the stock code after the loop (0x40055b7e), which resets
 * every LED.
 *
 * Docking: the mark's ninth dot is a module arriving. First the plan: a dashed frame and nine dotted
 * slots, while the panel wakes around the screen. A placement head drops in and sets the eight tiles,
 * serpentine, each with a press and its track key; then it leaves, and the ninth slot, the socket, blinks
 * while a light far off on the trig row answers. The module runs along the trig row, turns up into the
 * screen and docks; its wave makes the frame solid, reveals MODWERK, NEW and the version and rolls on
 * across the whole panel.
 *
 * Screen and lamps are one plane: the LCD sits in the panel (54.2 hundredths of a millimetre per pixel,
 * lamp positions from the stock lamp table), so the module and the wave keep going across the edge.
 * The lamps are white on an MKII: the startup sets channel A's colour to white at the panel's LED
 * intensity and puts the firmware's own colours back (its pre-logo call) before it returns. An MKI has
 * fixed colours, so there it is channel A's red. Drawing goes through ev_draw on the frame the compositor
 * builds (bus.s); time is the free-running DTIM3 count, as in the stock loop. */
#include <stdint.h>
#include "boot_art.h"

#ifdef MODWERK_HOST
void host_clear(void *window, int a, int b);
void host_compose(void);
void host_led_on(int id), host_led_off(int id), host_led_level(int id, int level), host_led_send(void);
void host_palette(int id, int reg, int r, int g, int b);
void host_scheme(int level, int backlight, int lists, int keys);
extern volatile uint32_t host_dtcn3;
extern uint32_t host_mkii, host_intensity;
extern int32_t host_lamps[];
extern const uint32_t host_white[3];
#define lcd_clear host_clear
#define lcd_compose host_compose
#define led_on host_led_on
#define led_off host_led_off
#define led_level host_led_level
#define led_send host_led_send
#define led_palette host_palette
#define led_scheme host_scheme
#define DTCN3 host_dtcn3
#define PANEL_MKII host_mkii
#define LED_INTENSITY host_intensity
#define LAMPS_MKII host_lamps
#define LAMPS_MKI host_lamps
#define WHITE host_white
#else
/* OS 1.40C, as the stock logo loop and the boot sequence around it call them. */
#define lcd_clear ((void (*)(void *, int, int))0x400125ac)  /* (window, 0, -1) blanks it */
#define lcd_compose ((void (*)(void))0x40013abc)            /* windows, then ev_draw, then the changes to the LCD */
#define led_on ((void (*)(int))0x400131a0)
#define led_off ((void (*)(int))0x400131c8)
#define led_level ((void (*)(int, int))0x400135b0)          /* 0-15, sent when it changes */
#define led_send ((void (*)(void))0x400136a8)
#define led_palette ((void (*)(int, int, int, int, int))0x40013368)   /* (id, register 0-2, r, g, b) */
#define led_scheme ((void (*)(int, int, int, int))0x4003f430)       /* (intensity, backlight, lamp lists, keys) */
#define DTCN3 (*(volatile uint32_t *)0xfc07c00c)           /* 132 MHz; any write clears it */
#define PANEL_MKII (*(volatile uint32_t *)0x46c8d18c)
#define LED_INTENSITY (*(volatile uint32_t *)0x800000d0)    /* the setting the boot passes to led_scheme */
#define LAMPS_MKII ((const int32_t *)0x400c0d08)            /* lamp (x, y) in 0.01 mm, 67 lamps */
#define LAMPS_MKI ((const int32_t *)0x400c0f20)             /* 44 lamps */
#define WHITE ((const uint32_t *)0x400abc26)                /* the scheme's colour level per intensity */
#endif

/* The score, in ms. */
#define T_PLAN0 100     /* the plan: the dashed frame, clockwise; the panel wakes around the screen */
#define T_PLAN1 300
#define T_SLOTS 180     /* a dotted slot every 20 ms, the socket last */
#define T_DROP 440      /* the head sets a tile every 60 ms (40 ms moving, 20 ms pressing) */
#define T_WAIT 960      /* the socket blinks and the module answers, twice */
#define T_FLY0 1160     /* the module's run */
#define T_DOCK 1990
#define T_WAVE 1990     /* the dock's wave: radius (dt / 40 ms)^2 px */
#define T_END 3240

#define R_HEAD 34       /* px: how far from the module a lamp glows */
#define R_RING 30       /* px: the wave's width on the panel */
#define FADE_MS 200     /* a lamp's afterglow from full to dark */

static int32_t now, on, lamps;
static int32_t path[4][2];              /* the module's run: a cubic curve, 1/16 px */
static int16_t lamp_x[67], lamp_y[67];  /* lamps in screen pixels */
static int32_t glow[67];                /* 1/16 levels */

/* The head's round: top row left to right, middle row back, bottom row (tile k is row k / 3, column
 * k % 3); the same table gives each tile's turn, since the round swaps 3 and 5 only. */
static const uint8_t order[8] = {0, 1, 2, 5, 4, 3, 6, 7};

#define DOCK_X (BOOT_DISC_X * 16 + BOOT_DISC_W * 8)   /* the detached tile's middle, 1/16 px */
#define DOCK_Y (BOOT_DISC_Y * 16 + BOOT_DISC_H * 8)

static int32_t span(int32_t t, int32_t t0, int32_t t1) /* 0..4096 */
{
    return t <= t0 ? 0 : t >= t1 ? 4096 : (t - t0) * 4096 / (t1 - t0);
}

static int32_t smooth(int32_t u)
{
    return (u * u >> 12) * (3 * 4096 - 2 * u) >> 12;
}

static void dot(unsigned char *frame, int32_t x, int32_t y)
{
    if ((uint32_t)x < 128 && (uint32_t)y < 64) {
        int32_t bit = 63 - y;
        frame[x * 8 + (bit >> 3)] |= (unsigned char)(0x80 >> (bit & 7));
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

static int32_t isqrt(uint32_t v)
{
    uint32_t r = 0, b = 1u << 30;
    while (b > v) b >>= 2;
    for (; b; b >>= 2)
        if (v >= r + b) v -= r + b, r = (r >> 1) + b;
        else r >>= 1;
    return (int32_t)r;
}

/* 0-255 clockwise from straight up (screen y grows downwards). */
static int32_t clockwise(int32_t dx, int32_t dy)
{
    if (!dx && !dy) return 0;
    if (dy < 0 && dx >= 0) return 64 * dx / (dx - dy);
    if (dx >= 0) return 64 + 64 * dy / (dx + dy);
    if (dy >= 0) return 128 + 64 * -dx / (dy - dx);
    return 192 + 64 * -dy / (-dx - dy);
}

/* Where the module is at time t (1/16 px): along the curve, easing in and out, docked from T_DOCK on. */
static void module(int32_t t, int32_t *x, int32_t *y)
{
    int32_t u = smooth(span(t, T_FLY0, T_DOCK)), a = 4096 - u;
    int32_t w[4] = {(a * a >> 12) * a >> 12, 3 * ((a * a >> 12) * u >> 12), 3 * ((a * u >> 12) * u >> 12), (u * u >> 12) * u >> 12};
    *x = *y = 0;
    for (int k = 0; k < 4; k++)
        *x += w[k] * path[k][0] >> 12, *y += w[k] * path[k][1] >> 12;
}

static int32_t wave(int32_t t) /* px */
{
    int32_t dt = t - T_WAVE;
    return dt <= 0 ? 0 : dt * dt / 1600;
}

static int near(int32_t x, int32_t y, int32_t r) /* is pixel (x, y) within r px of the dock */
{
    int32_t dx = x * 16 + 8 - DOCK_X, dy = y * 16 + 8 - DOCK_Y;
    return dx * dx + dy * dy <= r * r * 256;
}

static void ring(unsigned char *frame, int32_t r) /* the wave on the screen: a dotted circle */
{
    int32_t cx = DOCK_X >> 4, cy = DOCK_Y >> 4, x = r, y = 0, err = 0;
    for (int n = 0; x >= y; n++) {
        if (n % 2 == 0) {
            dot(frame, cx + x, cy + y), dot(frame, cx + y, cy + x), dot(frame, cx - y, cy + x), dot(frame, cx - x, cy + y);
            dot(frame, cx - x, cy - y), dot(frame, cx - y, cy - x), dot(frame, cx + y, cy - x), dot(frame, cx + x, cy - y);
        }
        y++, err += 2 * y + 1;
        if (2 * err > 2 * x - 1) x--, err -= 2 * x + 1;
    }
}

static void dotted(unsigned char *frame, int32_t x, int32_t y, int32_t w, int32_t h)
{
    for (int32_t i = 0; i < w; i++)
        for (int32_t j = 0; j < h; j++)
            if ((i == 0 || j == 0 || i == w - 1 || j == h - 1) && (i + j) % 2 == 0)
                dot(frame, x + i, y + j);
}

static void slot(int k, int32_t *x, int32_t *y) /* a tile's middle, 1/16 px */
{
    *x = (BOOT_MARK_X + 9 + 8 * (k % 3)) * 16, *y = (BOOT_MARK_Y + 9 + 8 * (k / 3)) * 16;
}

/* The placement head at time t (1/16 px): down from above the screen onto the first slot, slot to slot,
 * then out past the top right. Returns 2 while it presses, 1 while it moves, 0 when it is gone. */
static int head(int32_t t, int32_t *x, int32_t *y)
{
    int32_t wx[10], wy[10];
    slot(0, &wx[0], &wy[0]), wy[0] = -10 * 16;
    for (int n = 0; n < 8; n++)
        slot(order[n], &wx[n + 1], &wy[n + 1]);
    wx[9] = 140 * 16, wy[9] = -10 * 16;
    if (t < T_DROP - 60 || t > T_DROP + 7 * 60 + 80)
        return 0;
    for (int n = 0; n < 9; n++) {
        int32_t depart = n ? T_DROP + (n - 1) * 60 + 20 : T_DROP - 60, arrive = n < 8 ? T_DROP + n * 60 : T_DROP + 7 * 60 + 80;
        if (t <= arrive || n == 8) {
            int32_t u = smooth(span(t, depart, arrive));
            *x = wx[n] + (wx[n + 1] - wx[n]) * u / 4096, *y = wy[n] + (wy[n + 1] - wy[n]) * u / 4096;
            return t < depart && n ? 2 : 1;
        }
    }
    return 0;
}

void modwerk_boot_draw(unsigned char *frame)
{
    int32_t t = now;
    if (!on || t < T_PLAN0)
        return;
    int32_t plan = 256 * span(t, T_PLAN0, T_PLAN1) / 4096, r = wave(t), hx, hy, h;
    for (int i = 0; i < BOOT_RING && boot_ring[i][2] < plan; i++) {   /* dashed until the dock's wave */
        int32_t x = boot_ring[i][0], y = boot_ring[i][1];
        if ((x + y) % 2 == 0 || (r && near(x, y, r)))
            dot(frame, x, y);
    }
    for (int k = 0; k < 8; k++) {
        int32_t at = T_DROP + order[k] * 60, x = BOOT_MARK_X + 6 + 8 * (k % 3), y = BOOT_MARK_Y + 6 + 8 * (k / 3);
        if (t >= at) {
            bits(frame, x, y, boot_tile, 6, 6);
            if (t < at + 20)   /* the press */
                for (int i = -1; i < 7; i++)
                    for (int j = -1; j < 7; j++)
                        dot(frame, x + i, y + j);
        } else if (t >= T_SLOTS + k * 20)
            dotted(frame, x, y, 6, 6);
    }
    if (t >= T_SLOTS + 8 * 20 && t < T_DOCK && (t < T_WAIT || t >= T_FLY0 || (t - T_WAIT) % 120 < 60))   /* the socket */
        dotted(frame, BOOT_DISC_X, BOOT_DISC_Y, BOOT_DISC_W, BOOT_DISC_H);
    if ((h = head(t, &hx, &hy)) != 0) {   /* a reticle reaching past the slot; it closes in as it presses */
        int32_t cx = hx >> 4, cy = hy >> 4, d0 = h == 2 ? 4 : 5;
        for (int32_t d = d0; d <= d0 + 2; d++)
            dot(frame, cx - d, cy), dot(frame, cx + d, cy), dot(frame, cx, cy - d), dot(frame, cx, cy + d);
    }
    if (t >= T_FLY0 && t < T_DOCK) {   /* the module on the screen, with a short streak */
        for (int k = 2; k >= 0; k--) {
            int32_t x, y;
            module(t - 25 * k, &x, &y);
            blob(frame, x, y, 56 - 16 * k);
        }
    } else if (t >= T_DOCK) {
        bits(frame, BOOT_DISC_X, BOOT_DISC_Y, boot_disc, BOOT_DISC_W, BOOT_DISC_H);
        if (t < T_DOCK + 40)   /* the clunk */
            for (int i = -1; i <= BOOT_DISC_W; i++)
                for (int j = -1; j <= BOOT_DISC_H; j++)
                    dot(frame, BOOT_DISC_X + i, BOOT_DISC_Y + j);
    }
    if (!r)
        return;
    for (int32_t x = 0; x < 110; x++)   /* what the wave has passed shows */
        for (int32_t y = 0; y < 15; y++)
            if (boot_word[x] >> y & 1 && near(BOOT_WORD_X + x, BOOT_WORD_Y + y, r))
                dot(frame, BOOT_WORD_X + x, BOOT_WORD_Y + y);
    for (int g = 0; g < BOOT_GLYPHS; g++)
        for (int i = 0; i < boot_glyph[g].count; i++) {
            const uint8_t *p = boot_ink[boot_glyph[g].first + i];
            if (near(p[0], p[1], r))
                dot(frame, p[0], p[1]);
        }
    if (r < 150)   /* until it has left the screen */
        ring(frame, r);
}

static void light(int32_t t, int32_t dt)
{
    int32_t mx = 0, my = 0, flying = t >= T_FLY0 && t < T_DOCK + 60, r = wave(t);
    if (flying)
        module(t, &mx, &my), mx >>= 4, my >>= 4;
    for (int i = 0; i < lamps; i++) {
        int32_t px = lamp_x[i], py = lamp_y[i], best = 0, level;
        /* waking: a soft pass around the screen, clockwise with the plan's frame */
        int32_t d = isqrt((uint32_t)((px - 64) * (px - 64) + (py - 32) * (py - 32)));
        if (d < 170) {
            int32_t peak = T_PLAN0 + clockwise(px - 64, py - 32) * (T_PLAN1 - T_PLAN0) / 256, off = t - peak;
            level = 5 - (off < 0 ? -off : off) / 16;
            if (level > best) best = level;
        }
        /* the tracks: T1-T8 light with the head's drops and stay faintly on until the wave */
        if (i >= 20 && i < 28 && t >= T_DROP + (i - 20) * 60) {
            int32_t since = t - T_DROP - (i - 20) * 60;
            level = since < 150 ? 15 - since * 11 / 150 : r > 0 ? 0 : 4;
            if (level > best) best = level;
        }
        /* far off, the module answering the socket */
        if (i == 0 && t >= T_WAIT && t < T_FLY0 && (t - T_WAIT) % 120 < 60)
            best = 15;
        if (flying) {
            d = isqrt((uint32_t)((px - mx) * (px - mx) + (py - my) * (py - my)));
            level = 15 - d * 15 / R_HEAD;
            if (level > best) best = level;
        }
        if (r > 0 && r < 600) {
            int32_t ox = px - (DOCK_X >> 4), oy = py - (DOCK_Y >> 4);
            d = isqrt((uint32_t)(ox * ox + oy * oy)) - r;
            level = 15 - (d < 0 ? -d : d) * 15 / R_RING;
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
    int32_t x0 = PANEL_MKII ? 12627 : 9332, y0 = PANEL_MKII ? 13659 : 12734, then = 0;
    lamps = PANEL_MKII ? 67 : 44;
    for (int i = 0; i < lamps; i++) {
        lamp_x[i] = (int16_t)((table[2 * i] - x0) * 10 / 542);
        lamp_y[i] = (int16_t)((y0 - table[2 * i + 1]) * 10 / 542);
        glow[i] = 0;
    }
    /* the run: from beyond trig 1 along the trig row, then up through the keys under the screen */
    path[0][0] = (lamp_x[0] - 40) * 16, path[0][1] = lamp_y[0] * 16;
    path[1][0] = DOCK_X + 150 * 16, path[1][1] = (lamp_y[0] + 20) * 16;
    path[2][0] = DOCK_X, path[2][1] = DOCK_Y + 150 * 16;
    path[3][0] = DOCK_X, path[3][1] = DOCK_Y;
    for (int id = 0; id < 2 * lamps; id++)
        led_level(id, 0);
    if (PANEL_MKII) {   /* channel A white, at the panel's intensity */
        int32_t level = (int32_t)WHITE[LED_INTENSITY > 2 ? 2 : LED_INTENSITY];
        for (int i = 0; i < lamps; i++)
            led_palette(2 * i, 1, level, level, level);
    }
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
        lcd_clear(window, 0, -1);
        lcd_compose();
        light(t, t - then);
        led_send();
        then = t;
    }
    on = 0;
    if (PANEL_MKII)   /* the firmware's colours as it set them before the logo; it sets the keys' after it */
        led_scheme((int)LED_INTENSITY, 0, 1, 0);
}
