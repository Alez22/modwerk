/* SPDX-License-Identifier: MIT
 * Actual independent controller and grid engine against the shared service.
 * Authored source metadata only; not a stock-menu or hardware qualification.
 */
#include "sample_editor_service.h"
#include "modwerk_module.h"
#include <stdio.h>
#include <string.h>
#define CHECK(x) do {if(!(x)){printf("FAIL line %u\n",(unsigned)__LINE__);return 1;}}while(0)
void bs_device_open(uint32_t,const struct modwerk_sample_editor_api *);
void module_tick(struct modwerk_runtime_api *);
void module_draw(unsigned char *);
int module_key(int,int);
int module_enc(int,int);
static struct mw_sample_editor service;
static struct mw_sample_capture source;
static struct runtime_owner owner;
static unsigned ready=1,held,bad,confirms,cancels,publishes;
static uint32_t lock(void *p){(void)p;if(held)bad=1;held=1;return 7;}
static void unlock(void *p,uint32_t saved){(void)p;if(!held || saved!=7)bad=1;held=0;}
static int available(void *p){(void)p;return ready;}
static int published(void *p,const struct runtime_owner *o){(void)p;return o->generation==owner.generation;}
static unsigned capture(void *p,struct mw_sample_capture *out){(void)p;*out=source;return MODWERK_SAMPLE_OK;}
static unsigned publish(void *p,const struct mw_sample_capture *before,const struct mw_sample_edit *edit)
{
    (void)p;if(!held || memcmp(before,&source,sizeof source))bad=1;
    ++publishes;source.view.count=edit->count;
    memcpy(source.view.records,edit->records,sizeof edit->records);return MODWERK_SAMPLE_APPLIED;
}
static unsigned copy(uint32_t token,struct modwerk_sample_view *out)
{return mw_sample_editor_copy(&service,token,out);}
static unsigned confirm(uint32_t token,const struct modwerk_sample_grid *grid)
{++confirms;return mw_sample_editor_confirm(&service,token,grid);}
static void cancel(uint32_t token){++cancels;mw_sample_editor_cancel(&service,token);}
static const struct mw_sample_backend backend={0,lock,unlock,available,published,capture,publish};
static const struct modwerk_sample_editor_api api={MODWERK_SAMPLE_EDITOR_ABI,sizeof api,copy,confirm,cancel};
static int active(void)
{struct modwerk_runtime_api runtime={0};module_tick(&runtime);return !!(runtime.value&0x100);}
static int tap(int code)
{return module_key(code,1) && module_key(code,0);}
int main(void)
{
    uint32_t token;
    CHECK(mw_sample_editor_init(&service,&backend));owner.generation=1;
    source.view.frames=source.view.trim_end=88200;source.view.frame_rate=44100;
    source.view.sample_bpm24=2880;source.view.project_bpm24=2160;
    for(unsigned kind=0;kind<2;++kind) {
        source.view.kind=kind;source.view.count=0;
        CHECK(mw_sample_editor_begin(&service,&owner,&token)==MODWERK_SAMPLE_OK);
        bs_device_open(token,&api);CHECK(active());
        unsigned char guarded[1026];memset(guarded,0xa5,sizeof guarded);
        module_draw(guarded+1);
        CHECK(guarded[0]==0xa5 && guarded[1025]==0xa5);
        CHECK(memcmp(guarded+1,guarded+2,1023)!=0 && !publishes);
        unsigned previous=confirms;
        CHECK(tap(0x31) && confirms==previous+1 && !active());
        CHECK(service.state==MW_SAMPLE_PROMPT && !publishes);
        CHECK(!module_key(0x31,1)); /* package no longer owns stock YES */
        CHECK(mw_sample_editor_answer(&service,token,0)==MODWERK_SAMPLE_NO_CHANGE);
        CHECK(source.view.count==0 && !publishes);
        CHECK(mw_sample_editor_begin(&service,&owner,&token)==MODWERK_SAMPLE_OK);
        bs_device_open(token,&api);CHECK(tap(0x31));
        CHECK(mw_sample_editor_answer(&service,token,1)==MODWERK_SAMPLE_APPLIED);
        CHECK(source.view.count==4 && source.view.records[1].start==22050);
        /* Existing exact records are accepted with unchanged ordinals. */
        CHECK(mw_sample_editor_begin(&service,&owner,&token)==MODWERK_SAMPLE_OK);
        bs_device_open(token,&api);CHECK(tap(0x32) && !active() && service.state==MW_SAMPLE_CLOSED);
        publishes=0;
    }
    source.view.count=0;
    CHECK(mw_sample_editor_begin(&service,&owner,&token)==MODWERK_SAMPLE_OK);
    ready=0;bs_device_open(token,&api);CHECK(active());
    unsigned previous=confirms;
    CHECK(tap(0x31) && confirms==previous && active() && !publishes);
    ready=1;CHECK(active());
    CHECK(module_enc(1,1) && module_enc(1,-1));
    CHECK(module_enc(0,1) && module_enc(0,-1));
    CHECK(tap(0x31) && confirms==previous+1 && service.state==MW_SAMPLE_PROMPT);
    mw_sample_editor_answer(&service,token,0);
    CHECK(mw_sample_editor_begin(&service,&owner,&token)==MODWERK_SAMPLE_OK);
    bs_device_open(token,&api);++source.controls[5];
    CHECK(!active() && service.state==MW_SAMPLE_CLOSED && !publishes);
    CHECK(mw_sample_editor_begin(&service,&owner,&token)==MODWERK_SAMPLE_OK);
    bs_device_open(token,&api);previous=cancels;
    CHECK(!module_key(0x30,1) && !active() && cancels==previous+1);
    CHECK(!module_enc(0,1) && !module_key(0x30,0));
    CHECK(!held && !bad && !publishes);
    puts("PASS: actual package controller/grid, frame bounds and shared confirmation for Flex/Static");return 0;
}
