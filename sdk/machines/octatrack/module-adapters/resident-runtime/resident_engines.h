/* SPDX-License-Identifier: GPL-3.0-or-later */
#ifndef MODWERK_RESIDENT_ENGINES_H
#define MODWERK_RESIDENT_ENGINES_H
#include <stdint.h>

/* Resident controller engines on demand (docs/OCTATRACK_RESIDENT_ENGINES_ON_DEMAND.md). Only a base built with
 * --resident-on-demand compiles this unit (MODWERK_RESIDENT_ON_DEMAND). Each on-demand engine (Sidechain 1, Output
 * Matrix 2, Analog BD 4) is a relocatable unit (resident_dsp.engine_unit) the build stores per core. While a
 * controller generation holds its feature, the unit is relocated on the UI task into a per-core buffer, uploaded
 * at the top of that core's arena with an owned WRITE (every chunk read back on the DSP), then PLACEd (op 10,
 * word 7 = 1) so the receiver's base word names it. Only then may the board RESET and ENABLE the feature. When no
 * slot of the feature is held, it is unplaced (PLACE offset 0) and its span goes back to the FX allocator.
 *
 * Nothing here runs on the frame path, at a Part switch, pattern or bank change, Part reload or project load:
 * the board calls it from its own tick, and a placement or unplacement starts only while the sequencer is
 * stopped with no pattern change queued (modwerk_machine_stopped and the queued bank/pattern bytes). */

/* One engine as the build stores it (resident-engines-data.c): its words at base 0, three bytes each, high byte
 * first; each relocation an index, | 0x8000 for a displacement to a fixed address (value - base), else an address
 * (value + base). Indices strictly increase. count 0: this core does not carry the feature. */
struct mw_engine_unit {
    const uint8_t *words;
    const uint16_t *relocations;
    uint16_t count, relocation_count;
};
extern const struct mw_engine_unit mw_engine_units[2][3];  /* [core][feature index: 1, 2, 4] */
extern uint32_t *const mw_engine_buffer[2];                /* per core, sized to its largest unit */

enum mw_engine_state { MW_ENGINE_FREE, MW_ENGINE_CLAIMED, MW_ENGINE_WRITING, MW_ENGINE_WRITTEN, MW_ENGINE_PLACING,
                       MW_ENGINE_PLACED, MW_ENGINE_UNPLACING, MW_ENGINE_STUCK };
struct mw_engine { uint16_t offset; uint8_t state, pad; uint32_t generation; }; /* offset: from DL_CODE_START */
extern struct mw_engine mw_engines[2][3];
/* Diagnostics, never an ABI: owned jobs started, placements and unplacements acknowledged, claims refused. */
extern volatile uint32_t mw_engines_jobs, mw_engines_placed_count, mw_engines_unplaced_count, mw_engines_refused;

/* Relocate a unit for absolute P address `base` into out[0..count). Linear in words plus relocations. */
void mw_engine_relocate(const struct mw_engine_unit *, uint32_t base, uint32_t *out);

/* The board's seams (controller_board.c), all under the stable lock on the board's tick. */
/* Drain this module's owned jobs: call once per board tick before anything else starts a job. */
void mw_engines_poll(void);
/* Every core in `cores` has `feature`'s engine placed and its PLACE acknowledged. */
int mw_engines_ready(unsigned feature, unsigned cores);
/* Drive placement of `feature` on `cores` for a controller generation: 1 placed everywhere, 0 not yet (a job in
 * flight, the sequencer playing, the manager busy, no room), -1 never this boot (an uncertain PLACE). A core
 * whose `busy` entry is set (the board's own job holds it) is left alone. */
int mw_engines_place(unsigned feature, unsigned cores, uint32_t generation, const uint8_t busy[2]);
/* Admission's dry run for an incoming controller of `feature`; `wanted`: every feature held, live or incoming.
 * MW_ENGINE_FITS: placed, fits, or the manager is busy (the claim then waits on the tick); MW_ENGINE_MEMORY:
 * live FX code sits where the engines go, or the bank's Part union would no longer fit under them (the board
 * answers RUNTIME_MEMORY); MW_ENGINE_STUCK_BOOT: the engine is stuck for this boot (RUNTIME_CONFLICT). */
enum { MW_ENGINE_FITS, MW_ENGINE_MEMORY, MW_ENGINE_STUCK_BOOT };
int mw_engines_admit(unsigned feature, unsigned wanted);
/* Unplace and free every engine no held slot names: only when its feature is known dormant on that core (`mask`,
 * bit c of `known`), the core is free (`busy`) and the sequencer is quiet. */
void mw_engines_collect(unsigned held, const uint8_t mask[2], unsigned known, const uint8_t busy[2]);

/* The manager's seams (resident_engines.py's manager transform). Reserve: words taken from the top of the arena. */
int dl_engine_claim(unsigned core, unsigned reserve, int commit); /* 1 fits (and taken when commit), 0 busy, -1 no */
void dl_engine_release(unsigned core, unsigned reserve);           /* only ever lowers the reserve */
unsigned dl_engine_reserved(unsigned core);
#endif
