/* SPDX-License-Identifier: GPL-3.0-or-later */
#ifndef MODWERK_SAVED_SET_REFUSAL_H
#define MODWERK_SAVED_SET_REFUSAL_H
#include <stdint.h>
#define MSXR_REQUEST 37u
#define MSXR_BYTES 24u
enum msxr_origin { MSXR_NONE=0, MSXR_BEGIN=1, MSXR_ENGINE_READ=2 };
/* Named booleans only. No pointers, source words, names or file contents. */
enum msxr_factor {
    MSXR_WAKE=1u<<0, MSXR_RESET=1u<<1, MSXR_LAPSE=1u<<2,
    MSXR_RECEIVING=1u<<3, MSXR_HELD=1u<<4, MSXR_CONTROLLER=1u<<5,
    MSXR_MODSET=1u<<6, MSXR_PUBLICATION=1u<<7, MSXR_TRANSFER=1u<<8,
    MSXR_SELECTION=1u<<9, MSXR_MOVING=1u<<10, MSXR_REBINDING=1u<<11,
    MSXR_NUDGE=1u<<12, MSXR_DIAGNOSTIC=1u<<13, MSXR_SELFTEST=1u<<14,
    MSXR_COMPACTION=1u<<15, MSXR_PICKS=1u<<16,
    MSXR_MACHINE_RUNNING=1u<<17, MSXR_TRANSPORT_RUNNING=1u<<18,
    MSXR_RECORDING=1u<<19, MSXR_HOOKS=1u<<20,
    MSXR_LOGGER=1u<<21, MSXR_NOT_READING=1u<<22,
    MSXR_OWNED=1u<<23, MSXR_TOKEN_EXHAUSTED=1u<<24,
    MSXR_HOST_UNPROVED=1u<<25
};
struct msxr_cache {
    uint32_t sequence, ticks, refusal;
    uint16_t token;
    uint8_t origin, status;
};
/* Caller holds the actual board stable lock and supplies the evaluated gate.
 * Saturation retains the last record; sequence never wraps or reuses zero. */
void msxr_capture(struct msxr_cache *, unsigned origin, uint32_t ticks,
                  uint32_t refusal, unsigned token, unsigned status);
/* Pure cached encoding. This read neither evaluates nor renews any gate. */
unsigned msxr_read(const struct msxr_cache *, uint8_t out[MSXR_BYTES]);
#endif
