/* SPDX-License-Identifier: GPL-3.0-or-later */
/* Synthetic board admission only; production group admission stays disabled. */
#define MODWERK_RUNTIME_METADATA_EXTERNAL
#include "loader.c"
#include "sha256.c"
void *memcpy(void *to, const void *from, unsigned long length)
{
    volatile uint8_t *out=to;
    const volatile uint8_t *in=from;
    for (unsigned long i=0;i<length;i++) out[i]=in[i];
    return to;
}
int modwerk_machine_metadata_admit(const struct runtime_dsp *from, const struct runtime_dsp *to)
{ (void)from; (void)to; return RUNTIME_OK; }
uint32_t fixture_group_image(void)
{ const struct runtime_module *m=modwerk_runtime_module(0); return m?(uint32_t)(uintptr_t)m->dsp.image:0; }
