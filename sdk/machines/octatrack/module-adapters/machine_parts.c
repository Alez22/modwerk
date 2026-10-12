/* SPDX-License-Identifier: GPL-3.0-or-later
 * Stock-free layout facts: 1.40C copy routine 0x4004a908 copies 6322B
 * bank+0x8ed80+i*6322 -> bank+0x9504a+i*6322, then saved SRAM
 * 0x100ab196+i*6322. Shared authored machine owner uses machine byte
 * Part[0x22+track] < 2 and signature Part[60+30*track]. */
#include "machine_parts.h"
#define STRIDE 6322u
#define STOCK_RAM_END 0x47f00000u
static unsigned member(const uint8_t *signature)
{
    if (signature[0] == 'P' && signature[1] == 'L' && signature[2] == 1) return 1;
    if (signature[0] == 'S' && signature[1] == '2' && (signature[2] == 1 || signature[2] == 2)) return 2;
    if (signature[0] == 'F' && signature[1] == 'M' && signature[2] == 1) return 4;
    return 0;
}
int machine_part_lifetime(machine_part_read read, void *context, uint32_t bank, unsigned dropped)
{
    if (!dropped) return 0;
    if (!read || (dropped & ~7u) || bank < 0x40000000u || bank > STOCK_RAM_END - (0x9504au + 4u * STRIDE)) return 2;
    for (unsigned region = 0; region < 4; ++region) {
        uint32_t base = region == 0 ? bank + 0x8ed80u : region == 1 ? bank + 0x9504au :
                        region == 2 ? 0x100a4eceu : 0x100ab196u;
        for (unsigned part = 0; part < 4; ++part)
            for (unsigned track = 0; track < 8; ++track) {
                uint8_t type, signature[3];
                uint32_t at = base + part * STRIDE;
                if (!read(context, at + 0x22u + track, &type, 1)) return 2;
                if (type >= 2u) continue; /* only FLEX/STATIC carry this owner */
                if (!read(context, at + 60u + 30u * track, signature, 3)) return 2;
                if (member(signature) & dropped) return 1;
            }
    }
    return 0;
}
