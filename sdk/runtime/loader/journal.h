/* SPDX-License-Identifier: GPL-3.0-or-later
 * Private engine-only volatile publication journal. No host-supplied image,
 * generation, readiness, extent or ACK authority. Feature64 remains closed. */
#ifndef MODWERK_RUNTIME_JOURNAL_H
#define MODWERK_RUNTIME_JOURNAL_H
#include "loader.h"
#define RUNTIME_JOURNAL_ROWS 20u
/* Separate from mu_publication: pending must never mean MU_UNCHANGED. */
enum runtime_journal_result { RJ_OK, RJ_PENDING, RJ_REFUSED, RJ_UNCERTAIN, RJ_STALE };
enum runtime_journal_phase { RJ_IDLE, RJ_RECEIVING, RJ_VERIFIED, RJ_PUBLISHING, RJ_TRIAL, RJ_ROLLBACK, RJ_QUARANTINE };
enum runtime_journal_observation { RJ_WAIT, RJ_READY, RJ_REJECTED, RJ_UNKNOWN };
struct runtime_journal_view {
    struct runtime_owner before, after; /* zero generation denotes an empty side */
    const struct runtime_dsp *from, *to; /* borrowed under the actual stable lock only */
    uint32_t module;
    uint16_t position;
};
struct runtime_journal_progress {
    uint32_t generation;
    uint16_t records, published;
    uint8_t phase, required, touched, confirmed;
};
/* Real production adapter must provide exact source/resource/ACK/root facts.
 * Weak absent implementation refuses every operation and confers no feature.
 * transition binds immutable tuples to actual owned jobs; READY additionally
 * means all exact operation ACKs and backend job-storage releases completed.
 * Unknown/partial work retains both images. Reads never renew a transaction. */
int modwerk_machine_journal_enabled(void);
/* Evaluated under the retained board stable lock before creating the latch.
 * Includes actual upload, modset, export and DSP/controller work. */
int modwerk_machine_journal_begin_safe(void);
int modwerk_machine_journal_admit(const struct runtime_journal_view *,unsigned);
enum runtime_journal_observation modwerk_machine_journal_transition(
    const struct runtime_journal_view *,int reverse,uint8_t masks[3]);
int modwerk_machine_journal_committed(const struct runtime_journal_view *,int reverse);
int modwerk_machine_journal_roots_clear(const struct runtime_journal_view *);
int modwerk_runtime_volatile_busy(void);
/* Trusted engine calls only, with captured caller context. Each function
 * acquires the real stable lock at its use boundary. The journal owns its
 * generation, candidates and baseline until exact rollback completion. */
enum runtime_journal_result modwerk_runtime_journal_begin(void);
enum runtime_journal_result modwerk_runtime_journal_prepare(const uint8_t *,uint32_t,const struct runtime_context *);
enum runtime_journal_result modwerk_runtime_journal_verify(void);
enum runtime_journal_result modwerk_runtime_journal_activate(void);
enum runtime_journal_result modwerk_runtime_journal_abort(void);
enum runtime_journal_result modwerk_runtime_journal_step(const struct runtime_context *);
void modwerk_runtime_journal_snapshot(struct runtime_journal_progress *);
#endif
