/* SPDX-License-Identifier: GPL-3.0-or-later */
#include "saved_set_refusal.h"
static void be32(uint8_t *p, uint32_t v)
{ p[0]=(uint8_t)(v>>24); p[1]=(uint8_t)(v>>16); p[2]=(uint8_t)(v>>8); p[3]=(uint8_t)v; }
void msxr_capture(struct msxr_cache *s, unsigned origin, uint32_t ticks,
                  uint32_t refusal, unsigned token, unsigned status)
{
    if (s->sequence == UINT32_MAX || (origin != MSXR_BEGIN && origin != MSXR_ENGINE_READ) ||
        token > UINT16_MAX || status > 6u) return;
    s->ticks=ticks; s->refusal=refusal; s->token=(uint16_t)token;
    s->origin=(uint8_t)origin; s->status=(uint8_t)status;
    __asm__ volatile ("" ::: "memory"); ++s->sequence;
}
unsigned msxr_read(const struct msxr_cache *s, uint8_t out[MSXR_BYTES])
{
    for (unsigned i=0; i<MSXR_BYTES; ++i) out[i]=0;
    out[0]='M'; out[1]='W'; out[2]='X'; out[3]='R'; out[4]=1; out[5]=MSXR_BYTES;
    if (s->sequence) {
        out[6]=s->origin; be32(out+8,s->ticks); be32(out+12,s->refusal);
        out[16]=(uint8_t)(s->token>>8); out[17]=(uint8_t)s->token;
        out[18]=s->status; be32(out+20,s->sequence);
    }
    return MSXR_BYTES;
}
