/* SPDX-License-Identifier: MIT */
#include "menu_owner_backend.h"
static int identity(const struct bs_menu_owner_lease *lease,const bs_menu_owner *owner) {
    return owner && owner->module && owner->generation &&
        lease->owner.module==owner->module && lease->owner.generation==owner->generation;
}
static int valid(void *context,const bs_menu_owner *owner) {
    struct bs_menu_owner_backend *b=context;
    if(!b || !b->bound)return 0;
    for(uint32_t i=0;i<b->count;++i)
        if(identity(b->actions[i].lease,owner))return bs_menu_owner_current_locked(b->actions[i].lease);
    return 0;
}
static int invoke(void *context,const bs_menu_owner *owner,uint32_t action) {
    struct bs_menu_owner_backend *b=context;
    if(!b || !b->bound || !action)return 0;
    for(uint32_t i=0;i<b->count;++i) {
        struct bs_menu_owner_action *entry=&b->actions[i];
        if(entry->action==action && identity(entry->lease,owner)) {
            if(!bs_menu_owner_current_locked(entry->lease))return 0;
            return b->invoke(b->context,&entry->lease->owner,action);
        }
    }
    return 0;
}
int bs_menu_owner_backend_bind_locked(struct bs_menu_owner_backend *b,uint32_t count,
    const struct bs_menu_owner_action *actions,bs_menu_owner_invoke dispatch,void *context) {
    if(!b || b->bound || !count || count>BS_MENU_ACTIONS || !actions || !dispatch)return 0;
    for(uint32_t i=0;i<count;++i) {
        if(!actions[i].lease || !actions[i].action || !bs_menu_owner_current_locked(actions[i].lease))return 0;
        for(uint32_t j=0;j<i;++j) {
            const struct runtime_owner *left=&actions[i].lease->owner,*right=&actions[j].lease->owner;
            if(left->module==right->module && left->generation==right->generation &&
               (actions[i].lease!=actions[j].lease || actions[i].action==actions[j].action))return 0;
        }
    }
    for(uint32_t i=0;i<count;++i) {
        b->actions[i].lease=actions[i].lease;b->actions[i].action=actions[i].action;
    }
    b->count=count;b->invoke=dispatch;b->context=context;
    b->backend.context=b;b->backend.owner_valid=valid;b->backend.invoke=invoke;
    b->bound=1;return 1;
}
const bs_menu_backend *bs_menu_owner_backend_get_locked(struct bs_menu_owner_backend *b) {
    return b && b->bound?&b->backend:0;
}
