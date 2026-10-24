/* SPDX-License-Identifier: MIT */
#include "recorder_boundary.h"
static void failed(struct bs_recorder_boundary *b) {
    b->fault = 1;
    bs_guard_revoke(b->guard);
}
void bs_recorder_boundary_init(struct bs_recorder_boundary *b, struct bs_preview_guard *g) {
    if (!b) return;
    b->guard = g; b->depth = 0; b->fault = !g;
    for (uint32_t i=0; i<BS_RECORDER_DEPTH; ++i)
        b->frames[i].caller_sp = b->frames[i].ticket = 0;
    bs_guard_revoke(g);
}
void bs_recorder_enter_locked(struct bs_recorder_boundary *b, uint32_t sp,
                              uint32_t track, uint32_t selected, uint32_t other) {
    if (!b) return;
    if (!b->guard || b->fault || !sp || (sp & 3u) || track >= 8u ||
        selected > 2u || other > 2u || b->depth >= BS_RECORDER_DEPTH) { failed(b); return; }
    for (uint32_t i=0; i<b->depth; ++i)
        if (b->frames[i].caller_sp == sp) { failed(b); return; }
    struct bs_recorder_frame *f = &b->frames[b->depth++];
    f->caller_sp = sp;
    f->ticket = 0;
    if (selected || other == 1u) {
        f->ticket = bs_guard_writer_begin(b->guard);
        if (!f->ticket) failed(b);
    }
}
void bs_recorder_leave_locked(struct bs_recorder_boundary *b, uint32_t sp) {
    if (!b) return;
    if (!b->guard || b->fault || !b->depth || b->depth > BS_RECORDER_DEPTH) { failed(b); return; }
    struct bs_recorder_frame *f = &b->frames[b->depth-1u];
    if (f->caller_sp != sp || (f->ticket && !bs_guard_writer_end(b->guard, f->ticket))) {
        failed(b); return;
    }
    f->caller_sp = f->ticket = 0;
    --b->depth;
}
int bs_recorder_quiescent_locked(const struct bs_recorder_boundary *b) {
    return b && b->guard && !b->depth && !b->fault && !b->guard->poisoned;
}
