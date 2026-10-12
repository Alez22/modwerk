/* SPDX-License-Identifier: GPL-3.0-or-later; synthetic Part records only. */
#include "machine_parts.h"
#include <assert.h>
#include <string.h>
#include <stdio.h>
#define BANK 0x400e21e0u
#define STRIDE 6322u
static uint8_t regions[4][4 * STRIDE];
static unsigned reads;
static int unreadable;
static uint32_t base(unsigned r) { return r == 0 ? BANK + 0x8ed80u : r == 1 ? BANK + 0x9504au : r == 2 ? 0x100a4eceu : 0x100ab196u; }
static int read_part(void *unused, uint32_t address, uint8_t *out, unsigned n)
{
    (void)unused; ++reads;
    if (unreadable) return 0;
    for (unsigned r=0;r<4;++r) if (address >= base(r) && address-base(r) <= sizeof regions[r] && n <= sizeof regions[r]-(address-base(r))) {
        memcpy(out,regions[r]+address-base(r),n);return 1;
    }
    assert(0);return 0;
}
int main(void)
{
    const uint8_t signatures[4][3]={{'P','L',1},{'S','2',1},{'S','2',2},{'F','M',1}};
    const unsigned bits[4]={1,2,2,4};
    for (unsigned region=0;region<4;++region) for(unsigned part=0;part<4;++part) for(unsigned track=0;track<8;++track)
        for(unsigned m=0;m<4;++m) {
            memset(regions,0,sizeof regions);
            memcpy(regions[region]+part*STRIDE+60+track*30,signatures[m],3);
            assert(machine_part_lifetime(read_part,0,BANK,bits[m])==1);
            assert(machine_part_lifetime(read_part,0,BANK,7u & ~bits[m])==0);
            regions[region][part*STRIDE+0x22+track]=2;
            assert(machine_part_lifetime(read_part,0,BANK,bits[m])==0);
        }
    reads=0;assert(machine_part_lifetime(read_part,0,0,0)==0 && !reads);
    assert(machine_part_lifetime(read_part,0,0,1)==2 && !reads);
    assert(machine_part_lifetime(read_part,0,0xffffffffu,1)==2 && !reads);
    assert(machine_part_lifetime(read_part,0,0x47efffffu,1)==2 && !reads);
    assert(machine_part_lifetime(read_part,0,BANK,8)==2 && !reads);
    unreadable=1;assert(machine_part_lifetime(read_part,0,BANK,1)==2);
    puts("Machine Parts: all four working/saved RAM/SRAM regions, every Part/track/signature, retained masks, stock fallback and unknown bounds passed (synthetic data only).");
    return 0;
}
