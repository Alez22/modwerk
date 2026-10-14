/* SPDX-License-Identifier: GPL-3.0-or-later
 * MWLD v1: public read-only cached load, never starts a meter or self-test. */
#ifndef MODWERK_LOAD_WIRE_H
#define MODWERK_LOAD_WIRE_H
#include <stdint.h>
#define MODWERK_LOAD_BYTES 48u
struct modwerk_load_cache { uint32_t flags, frames, at[3], values[5]; };
static inline void modwerk_load_encode(uint8_t *out, uint32_t ticks, const volatile struct modwerk_load_cache *cache)
{
    out[0] = 'M'; out[1] = 'W'; out[2] = 'L'; out[3] = 'D';
    out[4] = 1; out[5] = (uint8_t)cache->flags; out[6] = 0; out[7] = MODWERK_LOAD_BYTES;
    uint32_t words[10] = {ticks, cache->frames, cache->at[0], cache->at[1], cache->at[2],
                         cache->values[0], cache->values[1], cache->values[2], cache->values[3], cache->values[4]};
    for (unsigned i = 0; i < 10u; ++i)
        for (unsigned b = 0; b < 4u; ++b) out[8u + 4u * i + b] = (uint8_t)(words[i] >> (24u - 8u * b));
}
/* MWLD v2 (the slot meter, build_core.py --slot-meter): v1's 48 bytes with version 2 and length 184, then the frame's
 * chip cycles (u32), the slot count (16), cycles a count (2), two zero bytes, and 8 bytes a slot (FX1 T1-T8, then FX2):
 * effect id, state (0 nothing runs, 1 measured, 2 not measured yet, 3 not measurable), age in ticks (u16, 0xffff
 * none) and the window's mean and peak counts a frame (u16 each). */
#define MODWERK_LOAD_SLOTS_BYTES 184u
struct modwerk_slot_reading { uint8_t id, state; uint16_t mean, peak; uint32_t at; };
static inline void modwerk_load_encode_slots(uint8_t *out, uint32_t ticks, const volatile struct modwerk_load_cache *cache,
                                             const volatile struct modwerk_slot_reading *slots, uint32_t frame_cycles)
{
    modwerk_load_encode(out, ticks, cache);
    out[4] = 2; out[7] = (uint8_t)MODWERK_LOAD_SLOTS_BYTES;
    for (unsigned b = 0; b < 4u; ++b) out[48u + b] = (uint8_t)(frame_cycles >> (24u - 8u * b));
    out[52] = 16; out[53] = 2; out[54] = out[55] = 0;
    for (unsigned i = 0; i < 16u; ++i) {
        uint8_t *e = out + 56u + 8u * i;
        uint32_t age = slots[i].state == 1u ? ticks - slots[i].at : 0xffffu;
        if (age > 0xffffu) age = 0xffffu;
        e[0] = slots[i].id; e[1] = slots[i].state;
        e[2] = (uint8_t)(age >> 8); e[3] = (uint8_t)age;
        e[4] = (uint8_t)(slots[i].mean >> 8); e[5] = (uint8_t)slots[i].mean;
        e[6] = (uint8_t)(slots[i].peak >> 8); e[7] = (uint8_t)slots[i].peak;
    }
}
#endif
