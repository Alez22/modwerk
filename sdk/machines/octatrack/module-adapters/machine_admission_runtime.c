/* SPDX-License-Identifier: MIT */
/* Octatrack board boundary. Include only with the reviewed helper/collector
 * sources and fixed declarations storage. An empty storage refuses groups. */
#include "machine_admission.h"
#include "table_admission.h"
static int board_read(void *context,uint32_t address,void *out,uint32_t length)
{
    (void)context;
    uint32_t physical=address>=0x48000400u && address<0x4ff00000u?address-0x08000000u:address;
    if(!((physical>=0x40000400u && physical<0x47f00000u && length<=0x47f00000u-physical) ||
         (address>=0x10000000u && address<0x10100000u && length<=0x10100000u-address))) return 0;
    const volatile uint8_t *from=(const volatile uint8_t *)(uintptr_t)address;uint8_t *to=out;
    for(uint32_t i=0;i<length;i++) to[i]=from[i];
    return 1;
}
int modwerk_machine_metadata_admit(const struct runtime_dsp *from,struct runtime_dsp *to,
    const struct runtime_context *context,enum runtime_metadata_operation operation)
{
#ifndef MODWERK_HOST
    uint32_t sr;
    __asm__ __volatile__("move.w %%sr,%0" : "=d"(sr) :: "memory");
    if((sr&0x0700u)<0x0400u) return RUNTIME_BUSY;
#endif
    /* No root reads for ordinary modules, including the default empty base. */
    unsigned family=table_metadata_family(from)|table_metadata_family(to);
    if(!((from->flags|to->flags)&RUNTIME_GROUP_METADATA) && !family) {to->foreign_roots=0;return RUNTIME_OK;}
    uint32_t bank=*(volatile uint32_t *)(uintptr_t)0x46c82456u;
    int why=machine_metadata_admission(modwerk_machine_declarations,from,to,board_read,0,bank);
    if(why) return why;
    if(family) {
        struct runtime_span span[RUNTIME_PAUSED];
        unsigned count=modwerk_machine_paused(span,RUNTIME_PAUSED,context);
        why=table_metadata_admission(modwerk_table_declarations,from,to,operation,board_read,0,span,count);
        if(why) return why;
    }
    to->foreign_roots=to->present && ((to->flags&RUNTIME_GROUP_METADATA) || table_metadata_family(to));
    return RUNTIME_OK;
}
