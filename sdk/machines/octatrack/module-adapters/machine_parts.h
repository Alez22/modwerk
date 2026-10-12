/* SPDX-License-Identifier: GPL-3.0-or-later */
#ifndef MODWERK_MACHINE_PARTS_H
#define MODWERK_MACHINE_PARTS_H
#include <stdint.h>
typedef int (*machine_part_read)(void *, uint32_t, uint8_t *, unsigned);
/* 0 no dropped member named, 1 retained, 2 unknown/unreadable.
 * Four working and four saved RAM Parts plus their eight SRAM mirrors.
 * These are exact 1.40C layouts, not a claim that disk-only banks were read. */
int machine_part_lifetime(machine_part_read, void *, uint32_t bank, unsigned dropped);
#endif
