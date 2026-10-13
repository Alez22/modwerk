/* SPDX-License-Identifier: MIT */
#ifndef MODWERK_TABLE_ADMISSION_H
#define MODWERK_TABLE_ADMISSION_H
#include "table_declarations.h"
#include "machine_lifetime.h"
#include "loader.h"
enum table_family { TABLE_NONE, TABLE_QUANTIZER, TABLE_MUTES };
enum table_operation { TABLE_PREPARE=1, TABLE_SWITCH=2 };
/* Canonical authored owners only; exact SHA records remain mandatory. FM
 * needs both its machine declaration and its bundled Quantizer declaration. */
unsigned table_metadata_family(const struct runtime_dsp *);
int table_metadata_admission(const uint8_t table[TABLE_DECLARATION_BYTES],
    const struct runtime_dsp *from,const struct runtime_dsp *to,unsigned operation,
    machine_memory_read,void *,const struct runtime_span *,unsigned);
#endif
