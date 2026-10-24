/* SPDX-License-Identifier: MIT */
/* Private fixed-owner engine service, not a published source/loader ABI. */
#define bs_worker_test_guard bs_recorder_test_guard
#include "test_source_boot.c"
#include "preview_async.h"
#include "engine_boundary.h"
extern struct bs_engine_boundary bs_recorder_engine_boundary;
struct bs_preview_async bs_recorder_service;
struct bs_async_result bs_recorder_service_result_copy;
uint32_t bs_recorder_service_initialized,bs_recorder_service_calls;
uint32_t bs_recorder_service_requests,bs_recorder_service_request_id;
uint32_t bs_recorder_service_steps,bs_recorder_service_begins,bs_recorder_service_max_steps;
uint32_t bs_recorder_service_posted,bs_recorder_service_consumed,bs_recorder_service_pending;
uint32_t bs_recorder_service_last_state;
static const uint8_t wake_message[4] __attribute__((aligned(4)))={255,0,0,0};
static uint32_t mask(void) {
    uint32_t sr=0;
    __asm__ __volatile__("move.w %%sr,%0\n\tmove.w #0x2700,%%sr" : "+d"(sr) :: "memory","cc");
    return sr;
}
static void restore(uint32_t sr) {
    __asm__ __volatile__("move.w %0,%%sr" :: "d"(sr) : "memory","cc");
}
static void wake(void) {
    uint32_t sr=mask();
    if(!bs_recorder_service_pending) {
        bs_recorder_service_pending=1;++bs_recorder_service_posted;
        ((void (*)(void *,const void *))0x40000c3cu)((void *)0x460d17ceu,wake_message);
    }
    restore(sr);
}
int bs_recorder_service_wake_job(const uint8_t *message) {
    uint32_t sr=mask();
    int own=bs_recorder_service_initialized && message==wake_message &&
        bs_recorder_service_pending && bs_engine_quiescent_locked(&bs_recorder_engine_boundary);
    if(own){bs_recorder_service_pending=0;++bs_recorder_service_consumed;}
    restore(sr);
    return own;
}
void bs_recorder_service_idle(void) {
    if(!bs_recorder_service_initialized)return;
    ++bs_recorder_service_calls;
    bs_recorder_service_last_state=bs_async_service(&bs_recorder_service,1);
    bs_recorder_service_steps+=bs_recorder_service.last_steps;
    bs_recorder_service_begins+=bs_recorder_service.last_begin;
    if(bs_recorder_service.last_steps>bs_recorder_service_max_steps)
        bs_recorder_service_max_steps=bs_recorder_service.last_steps;
    if(bs_recorder_service_last_state==BS_SESSION_RUNNING)wake();
}
uint32_t bs_recorder_service_init(void) {
    if(bs_recorder_service_initialized || bs_boot_init())return 1;
    if(!bs_async_init(&bs_recorder_service,&bs_recorder_test_guard,&bs_flex_source_backend,&source,1,2))return 1;
    bs_recorder_service_initialized=1;return 0;
}
/* Zero-argument producer/observer entries: the driver never services a session. */
uint32_t bs_recorder_preview_begin(void) {
    const struct bs_preview_options options={1,1,BS_SAMPLE_BPM};
    uint32_t request=bs_async_request(&bs_recorder_service,1,2,&options);
    if(request){++bs_recorder_service_requests;bs_recorder_service_request_id=request;wake();}
    return request;
}
uint32_t bs_recorder_preview_state(void) {
    return bs_async_state(&bs_recorder_service,1,2,bs_recorder_service_request_id);
}
uint32_t bs_recorder_preview_revision(void) { return bs_recorder_service.published_token.revision; }
uint32_t bs_recorder_service_result(void) {
    return (uint32_t)bs_async_result(&bs_recorder_service,1,2,bs_recorder_service_request_id,&bs_recorder_service_result_copy);
}
