/* SPDX-License-Identifier: GPL-3.0-or-later
 * How many effect ids the base handles, and sets of them (docs/OCTATRACK_MORE_EFFECT_IDS.md: 160 is the plan, owner
 * 12 October 2026: every installed module its own id, 128 installed; 32 until the DSP and ColdFire tables move).
 * Below 255, the transport's DL_NONE. Every per-id array and mask in the base is sized by
 * MODWERK_FX_IDS, and an id is checked against it, never masked: `id & 31` would run id 33 as id 1.
 * A set is words of 32 bits, so nothing needs 64-bit shifts (no libgcc on the unit). */
#ifndef MODWERK_FXIDS_H
#define MODWERK_FXIDS_H
#include <stdint.h>
#ifndef MODWERK_FX_IDS
#define MODWERK_FX_IDS 32u
#endif
#define MODWERK_FX_WORDS ((MODWERK_FX_IDS + 31u) / 32u)
typedef char modwerk_fx_ids_below_none[MODWERK_FX_IDS < 255u ? 1 : -1]; /* 255: no package (allocator.h) */
#define MODWERK_LIST_ROWS 32u /* a chooser list's rows (NONE, stock's, the modules', then 0): not ids */
typedef struct { uint32_t w[MODWERK_FX_WORDS]; } fx_set;
static inline int fx_in(fx_set s, unsigned id) { return id < MODWERK_FX_IDS && s.w[id >> 5] >> (id & 31u) & 1u; }
static inline fx_set fx_with(fx_set s, unsigned id)
{
    if (id < MODWERK_FX_IDS) s.w[id >> 5] |= 1u << (id & 31u);
    return s;
}
static inline fx_set fx_without(fx_set s, unsigned id)
{
    if (id < MODWERK_FX_IDS) s.w[id >> 5] &= ~(1u << (id & 31u));
    return s;
}
static inline fx_set fx_or(fx_set a, fx_set b)
{
    for (unsigned i = 0; i < MODWERK_FX_WORDS; ++i) a.w[i] |= b.w[i];
    return a;
}
static inline fx_set fx_and(fx_set a, fx_set b)
{
    for (unsigned i = 0; i < MODWERK_FX_WORDS; ++i) a.w[i] &= b.w[i];
    return a;
}
static inline fx_set fx_less(fx_set a, fx_set b) /* a without b */
{
    for (unsigned i = 0; i < MODWERK_FX_WORDS; ++i) a.w[i] &= ~b.w[i];
    return a;
}
static inline int fx_any(fx_set s)
{
    for (unsigned i = 0; i < MODWERK_FX_WORDS; ++i) if (s.w[i]) return 1;
    return 0;
}
static inline int fx_same(fx_set a, fx_set b)
{
    for (unsigned i = 0; i < MODWERK_FX_WORDS; ++i) if (a.w[i] != b.w[i]) return 0;
    return 1;
}
extern const fx_set modwerk_fx_modules; /* identity.c: the module effect ids (handles) */
/* MISSING's pages (ep0.c request 14): at most this many entries, 4 + 24 x 13 = 316 bytes, as before paging. */
#define MODWERK_MISSING_PAGE 13u
#endif
