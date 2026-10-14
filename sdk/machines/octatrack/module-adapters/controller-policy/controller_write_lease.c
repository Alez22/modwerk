/* SPDX-License-Identifier: GPL-3.0-or-later
 * Actual scoped control writes: one independent lease, no DSP submissions,
 * uploaded readiness, saved-file writes, retry or caller-owned IRQ authority.
 */
#include "controller_write_lease.h"
struct write_record {
    struct runtime_owner owner;
    struct mw_controller_binding binding;
    uintptr_t storage,cached_image,exec_image; /* binding alias; alias the module code runs from */
    uint32_t original_irq,ticket;
    uint16_t policy;
    uint8_t active;
};
static struct write_record writing;
static uint32_t last_write_ticket;
static int equal(const uint8_t *a,const uint8_t *b,unsigned n) {
    while(n--) if(*a++!=*b++) return 0;
    return 1;
}
static int trusted(const struct mw_controller_write_policy *p,const struct mw_controller_binding *b) {
    const struct mw_controller_identity *a=&p->identity,*v=&b->identity;
    return p->version && p->image_bytes && p->image_bytes==b->image_bytes &&
        p->entry<p->image_bytes && p->begin_return<p->image_bytes && p->end_return<p->image_bytes &&
        !((p->entry|p->begin_return|p->end_return)&1u) && p->begin_return!=p->end_return &&
        a->module==v->module && a->feature==v->feature && a->required_cores==v->required_cores &&
        a->policy_revision==v->policy_revision && a->state_revision==v->state_revision && a->parameter_revision==v->parameter_revision &&
        equal(a->package_sha256,v->package_sha256,32) && equal(a->source_policy_sha256,v->source_policy_sha256,32);
}
static int owner_binding(const struct runtime_owner *o,uintptr_t image,const struct mw_controller_binding *b) {
    return o->generation==b->generation && o->module==b->identity.module && image>=o->image_offset &&
        image-o->image_offset==b->canonical_extent && o->extent_bytes==b->extent_bytes &&
        o->image_offset==b->image_offset && o->image_bytes==b->image_bytes &&
        equal(o->package_sha256,b->identity.package_sha256,32);
}
static uint32_t word(unsigned at) {
    switch(at) {
    case 0:return 0x4d574c53u;
    case 1:return writing.ticket;
    case 2:return writing.owner.generation;
    case 3:return writing.owner.module;
    case 4:return (uint32_t)writing.cached_image+modwerk_controller_write_policies[writing.policy].entry;
    case 5:return writing.binding.identity.feature;
    case 6:return (uint32_t)writing.storage;
    default:return ~writing.ticket;
    }
}
/* entry: an address inside an intact owned image, in the alias its code runs
 * from. The canonical extent comes from the loader's pool geometry only. */
int modwerk_controller_write_resolve(uintptr_t entry,struct runtime_owner *owner,uintptr_t *cached_image) {
    uintptr_t canonical;
    if(!owner || !cached_image || modwerk_runtime_owner_at(entry,owner)!=1 ||
        modwerk_runtime_owner_canonical(owner,&canonical)!=1) return 0;
    *cached_image=canonical+owner->image_offset;return 1;
}
/* The lease lies wholly in the running task's own stack, at or above the
 * caller's arguments [sp, sp+frame): the caller's storage, not ours. */
int modwerk_controller_write_stack(uintptr_t sp,uintptr_t lease,unsigned frame) {
    uintptr_t lo,hi;
    return modwerk_machine_stack(&lo,&hi)==1 && sp>=lo && sp<=hi && hi-sp>=frame+sizeof(struct mw_controller_write_lease) &&
        !(lease&3u) && lease>=sp+frame && lease<=hi-sizeof(struct mw_controller_write_lease);
}
/* The assembly entry captures the real return PC/SP. These internal functions
 * are not module imports; native fixtures substitute captured facts only. */
static int begin_impl(uintptr_t entry,uint32_t feature,struct mw_controller_write_lease *lease,uintptr_t pc,uintptr_t sp)
    __attribute__((used,noinline));
static int begin_impl(uintptr_t entry,uint32_t feature,struct mw_controller_write_lease *lease,uintptr_t pc,uintptr_t sp) {
    uint32_t irq=modwerk_machine_lock();
    int ok=0;
    if(writing.active || !lease || last_write_ticket==UINT32_MAX || !modwerk_controller_write_policy_count ||
        modwerk_controller_write_policy_count>MW_CONTROLLER_WRITE_POLICY_CAPACITY ||
        modwerk_controller_write_stack(sp,(uintptr_t)lease,16u)!=1) goto out;
    struct runtime_owner owner;uintptr_t image;
    if(modwerk_controller_write_resolve(entry,&owner,&image)!=1 || modwerk_runtime_owner_valid(&owner)!=1) goto out;
    for(unsigned at=0;at<MW_CONTROLLER_SLOTS;++at) {
        const struct mw_controller_binding *b=&modwerk_controller_registry.slots[at].binding;
        if(!owner_binding(&owner,image,b)) continue;
        for(unsigned n=0;n<modwerk_controller_write_policy_count;++n) {
            const struct mw_controller_write_policy *p=&modwerk_controller_write_policies[n];
            uintptr_t exec=owner.owned_extent+owner.image_offset;
            if(feature!=p->identity.feature || !trusted(p,b) || entry!=exec+p->entry || pc!=exec+p->begin_return ||
                mw_controller_control_write_allowed(&modwerk_controller_registry,b)!=1) continue;
            writing=(struct write_record){.owner=owner,.binding=*b,.storage=(uintptr_t)lease,.cached_image=image,.exec_image=exec,
                .original_irq=irq,.ticket=++last_write_ticket,.policy=(uint16_t)n,.active=1};
            for(unsigned k=0;k<8u;++k) lease->opaque[k]=word(k);
            return 1; /* actual stable lock remains held across controller writes */
        }
    }
out:
    modwerk_machine_unlock(irq);return ok;
}
static int end_impl(struct mw_controller_write_lease *lease,uintptr_t pc,uintptr_t sp)
    __attribute__((used,noinline));
static int end_impl(struct mw_controller_write_lease *lease,uintptr_t pc,uintptr_t sp) {
    if(!writing.active) return 0;
    /* Recover this record's original IRQ state even if caller storage, PC,
     * generation or opaque words are corrupt. Never dereference unproved RAM. */
    uint32_t irq=writing.original_irq;
    int ok=lease && (uintptr_t)lease==writing.storage &&
        modwerk_controller_write_stack(sp,(uintptr_t)lease,8u)==1 &&
        pc==writing.exec_image+modwerk_controller_write_policies[writing.policy].end_return &&
        modwerk_runtime_owner_valid(&writing.owner)==1 &&
        mw_controller_control_write_allowed(&modwerk_controller_registry,&writing.binding)==1;
    for(unsigned k=0;ok && k<8u;++k) ok=lease->opaque[k]==word(k);
    if(!ok) (void)mw_controller_cancel(&modwerk_controller_registry,&writing.binding); /* quarantines predecessor too */
    writing.active=0;writing.storage=0;
    modwerk_machine_unlock(irq);return ok;
}
#ifndef MODWERK_HOST
/* ColdFire C ABI, D0=result. Caller cannot pass its return PC, SP or saved SR.
 * Scratch A0 is caller-saved. No full SR restore occurs inside module code. */
__asm__(".globl modwerk_controller_write_begin\n"
"modwerk_controller_write_begin:\n"
"move.l %sp,%a0\nmove.l %a0,-(%sp)\nmove.l (%a0),-(%sp)\n"
"move.l 12(%a0),-(%sp)\nmove.l 8(%a0),-(%sp)\nmove.l 4(%a0),-(%sp)\n"
"jsr begin_impl\nlea 20(%sp),%sp\nrts\n"
".globl modwerk_controller_write_end\n"
"modwerk_controller_write_end:\n"
"move.l %sp,%a0\nmove.l %a0,-(%sp)\nmove.l (%a0),-(%sp)\nmove.l 4(%a0),-(%sp)\n"
"jsr end_impl\nlea 12(%sp),%sp\nrts\n");
#endif
