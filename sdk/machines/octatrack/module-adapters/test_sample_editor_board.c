/* SPDX-License-Identifier: MIT
 * Runs the actual board adapter against an authored sparse metadata model.
 * This proves adapter failure handling, not stock writer coverage or hardware.
 */
#include "sample_editor_board.h"
#include <stdio.h>
#include <string.h>
#define CHECK(x) do {if(!(x)){printf("FAIL line %u\n",(unsigned)__LINE__);return 1;}}while(0)
static struct {uint32_t address,value;} memory[1024];
static unsigned used,masked,locked,bad,writes,refreshes,retired,live,metadata_reads,frame_services;
static uint32_t fail_address,fail_mode;
static uint32_t active_settings,row_writes;
static unsigned inject_writer,queued_writer,engine_writes;
static int stopped,transport,storage;
static uint32_t extent[2048];
static struct runtime_owner owner;
static uint32_t get(uint32_t address)
{for(unsigned i=0;i<used;++i)if(memory[i].address==address)return memory[i].value;return 0;}
static void put(uint32_t address,uint32_t value)
{
    for(unsigned i=0;i<used;++i)if(memory[i].address==address){memory[i].value=value;return;}
    if(used==1024){bad=1;return;}
    memory[used].address=address;memory[used++].value=value;
}
static int metadata_address(uint32_t at)
{
    return (at>=0x100b14f0u && at<0x100b14f0u+136u*1096u) ||
        (at>=0x100d5b30u && at<0x100d5b30u+128u*1096u) ||
        (at>=0x46c90a78u && at<0x46c90a78u+128u*44u) ||
        (at>=0x46c922c4u && at<0x46c922c4u+136u*44u);
}
int mw_sample_host_audio_preemptible(void){return !masked;}
uint32_t mw_sample_host_read(uint32_t address)
{
    if(metadata_address(address)) {
        ++metadata_reads;
        if(inject_writer){queued_writer=1;inject_writer=0;}
        if(!locked || masked)bad=1;else ++frame_services;
    }
    return get(address);
}
void mw_sample_host_write(uint32_t address,uint32_t value)
{
    if(!locked || masked)bad=1;else ++frame_services;
    if(address>=active_settings+312u && address<active_settings+1080u) {
        ++row_writes;
        if(get(active_settings+1092u))bad=1;
    }
    ++writes;
    if(address==fail_address && fail_mode) {
        if(fail_mode==1){fail_mode=0;return;}
        value^=1;
    }
    put(address,value);
}
uint32_t modwerk_machine_mask(void){return masked++;}
void modwerk_machine_unmask(uint32_t saved){if(masked!=saved+1)bad=1;masked=saved;}
uint32_t modwerk_machine_lock(void){return locked++;}
void modwerk_machine_unlock(uint32_t saved)
{
    if(locked!=saved+1)bad=1;
    locked=saved;
    if(!locked && queued_writer){queued_writer=0;++engine_writes;put(0x46c922d8,get(0x46c922d8)+1);}
}
int modwerk_machine_stopped(void){return stopped;}
int mw_sample_transport_ready(void){return transport;}
int mw_sample_storage_ready(void){return storage;}
int mw_sample_ep0_wake(const void *message){return message==&extent[0];}
int modwerk_runtime_owner_held(const struct runtime_owner *value,unsigned *hint)
{(void)hint;return live && !memcmp(value,&owner,sizeof owner);}
const struct runtime_module *modwerk_runtime_module(unsigned position)
{return live && !position?(const struct runtime_module *)extent:0;}
void mw_sample_menu_retire_locked(const struct runtime_dsp *from)
{(void)from;if(!masked)bad=1;++retired;}
void mw_sample_host_refresh(void)
{if(!locked || masked)bad=1;++refreshes;}
static uint32_t setup(unsigned kind,unsigned slot)
{
    used=masked=locked=bad=writes=refreshes=retired=metadata_reads=frame_services=0;live=1;
    fail_address=fail_mode=inject_writer=queued_writer=engine_writes=row_writes=0;stopped=transport=storage=1;
    memset(&mw_sample_editor,0,sizeof mw_sample_editor);
    memset(&owner,0,sizeof owner);memset(extent,0,sizeof extent);
    owner.generation=1;owner.module=17;owner.owned_extent=(uintptr_t)extent;
    owner.extent_bytes=sizeof extent;owner.image_offset=128;owner.image_bytes=1024;
    owner.package_sha256[31]=33;owner.controller_sha256[31]=44;
    put(0x46c8d1a0,kind);put(0x46c8d19c,slot);put(0x46105408,1);
    put(0x460d1cb8,1);put(0x80001814,2880);put(0x400ceb3c,9);
    uint32_t controls=(kind?0x46c922c4u:0x46c90a78u)+44u*slot;
    uint32_t settings=(kind?0x100b14f0u:0x100d5b30u)+1096u*slot;
    active_settings=settings;
    put(controls+16,88200);put(controls+20,7);put(controls+36,123);
    put(settings+276,2880);put(settings+304,88200);put(settings+308,UINT32_MAX);
    for(unsigned i=0;i<192;++i)put(settings+312+4*i,0xe0000000u+i);
    mw_sample_engine_idle();return settings;
}
int main(void)
{
    struct modwerk_sample_view *view=(void *)((uint8_t *)extent+1152);
    struct modwerk_sample_grid *grid=(void *)((uint8_t *)extent+2048);
    uint32_t token;
    for(unsigned kind=0;kind<2;++kind)for(unsigned slot=0;slot<128;slot+=127)
    for(unsigned failure=0;failure<5;++failure) {
        uint32_t settings=setup(kind,slot),before[192];
        for(unsigned i=0;i<192;++i)before[i]=get(settings+312+4*i);
        CHECK(mw_sample_editor_begin(&mw_sample_editor,&owner,&token)==MODWERK_SAMPLE_OK);
        CHECK(mw_sample_editor_api.copy(token,view)==MODWERK_SAMPLE_OK);
        CHECK(view->kind==kind && view->slot==slot && view->frames==88200);
        CHECK(mw_sample_editor_api.copy(token,(void *)extent)==MODWERK_SAMPLE_INVALID);
        CHECK(mw_sample_editor_api.copy(token,(void *)((uint8_t *)extent+sizeof extent-4))==MODWERK_SAMPLE_INVALID);
        grid->count=4;for(unsigned i=0;i<4;++i)grid->starts[i]=22050*i;
        CHECK(mw_sample_editor_api.confirm(token,grid)==MODWERK_SAMPLE_CONFIRMING && !writes);
        if(failure){fail_address=failure<3?settings+316:0x400ceb3cu;fail_mode=failure%2?1:2;}
        unsigned answer=mw_sample_editor_answer(&mw_sample_editor,token,1);
        CHECK(answer==(failure==0?MODWERK_SAMPLE_APPLIED:failure%2?MODWERK_SAMPLE_NO_CHANGE:MODWERK_SAMPLE_FAULT));
        CHECK(get(settings+1092)==(failure?0:4));
        if(failure%2) {
            CHECK(get(0x400ceb3c)==9);
            for(unsigned i=0;i<192;++i)CHECK(before[i]==get(settings+312+4*i));
        }
        if(!failure) {
            CHECK(get(0x400ceb3c)==UINT32_MAX);
            for(unsigned i=0;i<4;++i) {
                CHECK(get(settings+312+12*i)==22050*i);
                CHECK(get(settings+316+12*i)==22050*(i+1));
                CHECK(get(settings+320+12*i)==UINT32_MAX);
            }
            for(unsigned i=12;i<192;++i)CHECK(before[i]==get(settings+312+4*i));
            mw_sample_refresh_ui();CHECK(refreshes==1);mw_sample_refresh_ui();CHECK(refreshes==1);
        }
        CHECK(!masked && !locked && !bad && metadata_reads && frame_services);
    }
    /* Replacement uses the real board API buffer checks and writer. NO and
     * transient busy preserve a complete nonempty table; YES may reduce it. */
    for(unsigned kind=0;kind<2;++kind)for(unsigned slot=0;slot<128;slot+=127) {
        uint32_t settings=setup(kind,slot),before[192];
        put(settings+1092,4);
        for(unsigned i=0;i<4;++i) {
            put(settings+312+12*i,22050*i);put(settings+316+12*i,22050*(i+1));
            put(settings+320+12*i,UINT32_MAX);
        }
        for(unsigned i=0;i<192;++i)before[i]=get(settings+312+4*i);
        CHECK(mw_sample_editor_begin(&mw_sample_editor,&owner,&token)==MODWERK_SAMPLE_OK);
        grid->count=2;grid->starts[0]=0;grid->starts[1]=44100;
        CHECK(mw_sample_editor_api.replace(token,(void *)extent)==MODWERK_SAMPLE_INVALID);
        CHECK(mw_sample_editor_api.confirm(token,grid)==MODWERK_SAMPLE_PRESERVATION);
        CHECK(mw_sample_editor_api.replace(token,grid)==MODWERK_SAMPLE_CONFIRMING && !writes);
        CHECK(mw_sample_editor_answer(&mw_sample_editor,token,0)==MODWERK_SAMPLE_NO_CHANGE);
        CHECK(get(settings+1092)==4 && !writes);
        CHECK(mw_sample_editor_begin(&mw_sample_editor,&owner,&token)==MODWERK_SAMPLE_OK);
        CHECK(mw_sample_editor_api.replace(token,grid)==MODWERK_SAMPLE_CONFIRMING);
        transport=0;CHECK(mw_sample_editor_answer(&mw_sample_editor,token,1)==MODWERK_SAMPLE_BUSY);
        CHECK(get(settings+1092)==4 && !writes);
        for(unsigned i=0;i<192;++i)CHECK(before[i]==get(settings+312+4*i));
        transport=1;CHECK(mw_sample_editor_answer(&mw_sample_editor,token,1)==MODWERK_SAMPLE_APPLIED);
        CHECK(get(settings+1092)==2 && get(settings+316)==44100 && get(settings+324)==44100);
        CHECK(get(settings+328)==88200 && get(0x400ceb3c)==UINT32_MAX);
        for(unsigned i=6;i<192;++i)CHECK(before[i]==get(settings+312+4*i));
        CHECK(!masked && !locked && !bad);
    }
    /* Recorder admission follows the buffer selected in AED, independently
     * of its playback track and other recorders. Both state-bank selections,
     * every buffer and all metadata formats use the real adapter. */
    for(unsigned track=0;track<8;++track)for(unsigned selected=0;selected<2;++selected)
    for(unsigned format=0;format<4;++format) {
        uint32_t slot=128u+track,settings=setup(1,slot);
        stopped=0;put(0x80004f18,selected<<track);
        put(0x46c922c4u+44u*slot,format);
        uint32_t active=0x80004f1eu+84u*(track+8u*selected);
        uint32_t other=0x80004f1eu+84u*(track+8u*(1u-selected));
        put(other,2);
        put(0x80004f1eu+84u*((track+1u)%8u),2); /* another buffer records */
        CHECK(mw_sample_editor_begin(&mw_sample_editor,&owner,&token)==MODWERK_SAMPLE_OK);
        CHECK(mw_sample_editor_api.copy(token,view)==MODWERK_SAMPLE_OK && view->slot==slot);
        for(unsigned state=1;state<=3;++state) {
            put(active,state);
            CHECK(mw_sample_editor_begin(&mw_sample_editor,&owner,&token)==MODWERK_SAMPLE_STALE);
        }
        put(active,0);put(other,1);
        CHECK(mw_sample_editor_begin(&mw_sample_editor,&owner,&token)==MODWERK_SAMPLE_STALE);
        put(other,3);
        CHECK(mw_sample_editor_begin(&mw_sample_editor,&owner,&token)==MODWERK_SAMPLE_STALE);
        put(other,2);
        CHECK(mw_sample_editor_begin(&mw_sample_editor,&owner,&token)==MODWERK_SAMPLE_OK);
        grid->count=2;grid->starts[0]=0;grid->starts[1]=44100;
        CHECK(mw_sample_editor_api.replace(token,grid)==MODWERK_SAMPLE_CONFIRMING);
        CHECK(mw_sample_editor_answer(&mw_sample_editor,token,1)==MODWERK_SAMPLE_APPLIED);
        CHECK(get(settings+1092u)==2 && get(settings+328u)==88200 && !bad && frame_services);
        /* Starting this recorder cancels a pending YES. Stopping it with
         * otherwise identical metadata cannot revive or auto-apply it. */
        CHECK(mw_sample_editor_begin(&mw_sample_editor,&owner,&token)==MODWERK_SAMPLE_OK);
        grid->count=1;grid->starts[0]=0;
        CHECK(mw_sample_editor_api.replace(token,grid)==MODWERK_SAMPLE_CONFIRMING);
        unsigned stopped_writes=writes;put(active,2);
        CHECK(mw_sample_editor_answer(&mw_sample_editor,token,1)==MODWERK_SAMPLE_STALE);
        put(active,0);
        CHECK(mw_sample_editor_answer(&mw_sample_editor,token,1)==MODWERK_SAMPLE_STALE);
        CHECK(writes==stopped_writes && get(settings+1092u)==2);
        /* A changed control identity must stale even a same-length view.
         * This models identity changes; it does not assert that the stock
         * counter advances for every recording (native probes show otherwise). */
        CHECK(mw_sample_editor_begin(&mw_sample_editor,&owner,&token)==MODWERK_SAMPLE_OK);
        grid->count=1;
        CHECK(mw_sample_editor_api.replace(token,grid)==MODWERK_SAMPLE_CONFIRMING);
        put(0x46c922c4u+44u*slot+20u,8);
        unsigned before_writes=writes;
        CHECK(mw_sample_editor_answer(&mw_sample_editor,token,1)==MODWERK_SAMPLE_STALE);
        CHECK(writes==before_writes && get(settings+1092u)==2);
    }
    /* A short replacement drops later active markers; growing the recording
     * again cannot resurrect them from an old proposal or inactive rows. */
    {
        uint32_t settings=setup(1,128),controls=0x46c922c4u+44u*128u;
        put(settings+1092u,4);
        for(unsigned i=0;i<4;++i) {
            put(settings+312u+12u*i,22050u*i);put(settings+316u+12u*i,22050u*(i+1u));
            put(settings+320u+12u*i,UINT32_MAX);
            grid->starts[i]=22050u*i;
        }
        CHECK(mw_sample_editor_begin(&mw_sample_editor,&owner,&token)==MODWERK_SAMPLE_OK);
        grid->count=4;CHECK(mw_sample_editor_api.replace(token,grid)==MODWERK_SAMPLE_CONFIRMING);
        put(controls+16u,44100);put(controls+20u,8);put(settings+304u,44100);put(settings+1092u,2);
        CHECK(mw_sample_editor_answer(&mw_sample_editor,token,1)==MODWERK_SAMPLE_STALE && !writes);
        put(controls+16u,132300);put(controls+20u,9);put(settings+304u,132300);
        CHECK(mw_sample_editor_answer(&mw_sample_editor,token,1)==MODWERK_SAMPLE_STALE && !writes);
        CHECK(mw_sample_editor_begin(&mw_sample_editor,&owner,&token)==MODWERK_SAMPLE_OK);
        CHECK(mw_sample_editor_api.copy(token,view)==MODWERK_SAMPLE_OK);
        CHECK(view->count==2 && view->records[0].start==0 && view->records[1].start==22050 &&
              view->records[1].end==44100 && view->frames==132300);
        grid->count=6;for(unsigned i=0;i<6;++i)grid->starts[i]=22050u*i;
        CHECK(mw_sample_editor_api.replace(token,grid)==MODWERK_SAMPLE_CONFIRMING);
        CHECK(mw_sample_editor_answer(&mw_sample_editor,token,0)==MODWERK_SAMPLE_NO_CHANGE);
        CHECK(get(settings+1092u)==2 && !writes);
        CHECK(mw_sample_editor_begin(&mw_sample_editor,&owner,&token)==MODWERK_SAMPLE_OK);
        CHECK(mw_sample_editor_api.replace(token,grid)==MODWERK_SAMPLE_CONFIRMING);
        CHECK(mw_sample_editor_answer(&mw_sample_editor,token,1)==MODWERK_SAMPLE_APPLIED);
        CHECK(get(settings+1092u)==6 && get(settings+316u+12u*5u)==132300 && !bad);
    }
    for(unsigned track=0;track<8;++track) {
        uint32_t slot=128u+track,settings=setup(1,slot);
        put(0x46c922c4u+44u*slot+16u,0);put(settings+304u,0);
        CHECK(mw_sample_editor_begin(&mw_sample_editor,&owner,&token)==MODWERK_SAMPLE_OK);
        CHECK(mw_sample_editor_api.copy(token,view)==MODWERK_SAMPLE_OK && !view->frames && !view->count);
        grid->count=0;
        CHECK(mw_sample_editor_api.replace(token,grid)==MODWERK_SAMPLE_CONFIRMING);
        CHECK(mw_sample_editor_answer(&mw_sample_editor,token,1)==MODWERK_SAMPLE_NO_CHANGE);
        CHECK(!writes && !get(settings+1092u) && !bad);
    }
    for(unsigned kind=0;kind<2;++kind) {
        uint32_t settings=setup(kind,0);
        put((kind?0x46c922c4u:0x46c90a78u)+16u,0);put(settings+304u,0);
        CHECK(mw_sample_editor_begin(&mw_sample_editor,&owner,&token)==MODWERK_SAMPLE_UNSUPPORTED);
    }
    setup(0,128);CHECK(mw_sample_editor_begin(&mw_sample_editor,&owner,&token)==MODWERK_SAMPLE_UNSUPPORTED);
    setup(1,136);CHECK(mw_sample_editor_begin(&mw_sample_editor,&owner,&token)==MODWERK_SAMPLE_UNSUPPORTED);
    /* A failed publication-count clear cannot begin changing active rows.
     * A transient failure restores the old complete table; a persistent one
     * poisons the service without writing any row. */
    for(unsigned failure=1;failure<=2;++failure) {
        uint32_t settings=setup(1,0),before[192];
        put(settings+1092,4);
        for(unsigned i=0;i<4;++i) {
            put(settings+312+12*i,22050*i);put(settings+316+12*i,22050*(i+1));
            put(settings+320+12*i,UINT32_MAX);
        }
        for(unsigned i=0;i<192;++i)before[i]=get(settings+312+4*i);
        CHECK(mw_sample_editor_begin(&mw_sample_editor,&owner,&token)==MODWERK_SAMPLE_OK);
        grid->count=2;grid->starts[0]=0;grid->starts[1]=44100;
        CHECK(mw_sample_editor_api.replace(token,grid)==MODWERK_SAMPLE_CONFIRMING);
        fail_address=settings+1092;fail_mode=failure;
        CHECK(mw_sample_editor_answer(&mw_sample_editor,token,1)==
              (failure==1?MODWERK_SAMPLE_NO_CHANGE:MODWERK_SAMPLE_FAULT));
        for(unsigned i=0;i<192;++i)CHECK(before[i]==get(settings+312+4*i));
        CHECK(failure==1?get(settings+1092)==4:!row_writes);
        CHECK(!bad && frame_services && !masked && !locked);
    }
    /* Audio may run during a snapshot, but a queued engine writer waits for
     * the level-4 boundary. Its later change invalidates the copied preview. */
    setup(1,0);CHECK(mw_sample_editor_begin(&mw_sample_editor,&owner,&token)==MODWERK_SAMPLE_OK);
    inject_writer=1;
    CHECK(mw_sample_editor_api.copy(token,view)==MODWERK_SAMPLE_OK);
    CHECK(engine_writes==1 && !queued_writer && frame_services && !bad);
    grid->count=1;grid->starts[0]=0;
    CHECK(mw_sample_editor_api.replace(token,grid)==MODWERK_SAMPLE_STALE && !writes);
    /* An ISR/high-mask caller cannot start any heavy metadata operation. */
    setup(1,0);masked=1;
    CHECK(mw_sample_editor_begin(&mw_sample_editor,&owner,&token)==MODWERK_SAMPLE_BUSY);
    CHECK(!metadata_reads && !writes && !bad);masked=0;
    /* Readiness is the conjunction of real service gates; no writes on any
     * refused opening. Only the base's exact immutable EP0 wake is exempt. */
    for(unsigned gate=0;gate<8;++gate) {
        setup(1,0);
        if(gate==0){put(0x46c8d19c,128);put(0x80004f1e,1);}
        if(gate==1)transport=0;
        if(gate==2)storage=0;
        if(gate==3)put(0x460d17d2,1);
        if(gate==4)put(0x460e6bcc,1);
        if(gate==5)put(0x460e76a0,1);
        if(gate==6)put(0x460d1cb8,0);
        if(gate==7)mw_sample_engine_job(&extent[1]);
        CHECK(mw_sample_editor_begin(&mw_sample_editor,&owner,&token)==
              (gate==0?MODWERK_SAMPLE_STALE:MODWERK_SAMPLE_BUSY) && !writes);
    }
    /* Static and file-backed Flex edits can run during pattern playback,
     * including while the same track's independent recorder is recording. */
    for(unsigned kind=0;kind<2;++kind)for(unsigned selected=0;selected<2;++selected)
    for(unsigned track=0;track<8;++track) {
        setup(kind,0);stopped=0;put(0x80004f18,selected<<track);
        uint32_t active=0x80004f1eu+84u*(track+8u*selected);
        uint32_t other=0x80004f1eu+84u*(track+8u*(1u-selected));
        put(other,2); /* retained completed bank, not recording */
        CHECK(mw_sample_editor_begin(&mw_sample_editor,&owner,&token)==MODWERK_SAMPLE_OK);
        for(unsigned state=1;state<=3;++state) {
            put(active,state);
            CHECK(mw_sample_editor_begin(&mw_sample_editor,&owner,&token)==MODWERK_SAMPLE_OK);
        }
        put(active,0);put(other,1);
        CHECK(mw_sample_editor_begin(&mw_sample_editor,&owner,&token)==MODWERK_SAMPLE_OK);
        put(other,3);
        CHECK(mw_sample_editor_begin(&mw_sample_editor,&owner,&token)==MODWERK_SAMPLE_OK);
        put(active,2);put(other,0);
        CHECK(mw_sample_editor_begin(&mw_sample_editor,&owner,&token)==MODWERK_SAMPLE_OK);
        grid->count=1;grid->starts[0]=0;
        CHECK(mw_sample_editor_api.replace(token,grid)==MODWERK_SAMPLE_CONFIRMING);
        CHECK(mw_sample_editor_answer(&mw_sample_editor,token,1)==MODWERK_SAMPLE_APPLIED);
        CHECK(get((kind?0x100b14f0u:0x100d5b30u)+1092u)==1 && frame_services && !bad);
    }
    setup(1,0);CHECK(mw_sample_editor_begin(&mw_sample_editor,&owner,&token)==MODWERK_SAMPLE_OK);
    mw_sample_engine_job(extent);
    CHECK(mw_sample_editor_api.copy(token,view)==MODWERK_SAMPLE_BUSY);
    mw_sample_engine_idle();CHECK(mw_sample_editor_api.copy(token,view)==MODWERK_SAMPLE_OK);
    mw_sample_engine_job(&extent[1]);mw_sample_engine_idle();
    CHECK(mw_sample_editor_api.copy(token,view)==MODWERK_SAMPLE_STALE && !writes);
    /* A byte-16 record is only a candidate. Actual dispatch, matching command
     * identity and file-backed arguments are required; reads stay blocked for
     * the entire job. Mutated dispatch/late reuse can never revive a token. */
    for(unsigned scenario=0;scenario<6;++scenario) {
        uint8_t message[28]={16},foreign[28]={16};
        message[5]=1;
        setup(1,0);CHECK(mw_sample_editor_begin(&mw_sample_editor,&owner,&token)==MODWERK_SAMPLE_OK);
        mw_sample_engine_job(message);
        CHECK(mw_sample_editor_api.copy(token,view)==MODWERK_SAMPLE_BUSY);
        if(scenario==0)mw_sample_waveform_job(message);
        if(scenario==1)message[0]=17; /* writer dispatched instead: no observer */
        if(scenario==2)mw_sample_waveform_job(foreign);
        if(scenario==3){message[5]=4;mw_sample_waveform_job(message);}
        if(scenario==4){mw_sample_waveform_job(message);put(0x46c922d8,8);}
        if(scenario==5){mw_sample_waveform_job(message);mw_sample_engine_job(extent);}
        CHECK(mw_sample_editor_api.copy(token,view)==(scenario==5?MODWERK_SAMPLE_STALE:MODWERK_SAMPLE_BUSY));
        mw_sample_engine_idle();mw_sample_waveform_job(message); /* too late */
        CHECK(mw_sample_editor_api.copy(token,view)==(scenario==0?MODWERK_SAMPLE_OK:MODWERK_SAMPLE_STALE));
        CHECK(!writes && !masked && !locked && !bad);
    }
    /* A completed/empty recorder waveform uses the same actual dispatch seam.
     * Classify the command's source, not the current playback track or an
     * unrelated recorder. A recording command source still retires the view. */
    for(unsigned slot=128;slot<136;++slot)for(unsigned empty=0;empty<2;++empty)
    for(unsigned recording=0;recording<2;++recording) {
        uint32_t settings=setup(1,slot);
        if(empty){put(0x46c922c4u+44u*slot+16u,0);put(settings+304u,0);}
        uint8_t message[28]={16};message[5]=1;message[9]=(uint8_t)slot;
        CHECK(mw_sample_editor_begin(&mw_sample_editor,&owner,&token)==MODWERK_SAMPLE_OK);
        put(0x80004f1eu+84u*((slot-128u+1u)%8u),2); /* unrelated recorder */
        mw_sample_engine_job(message);
        if(recording)put(0x80004f1eu+84u*(slot-128u),2);
        mw_sample_waveform_job(message);mw_sample_engine_idle();
        CHECK(mw_sample_editor_api.copy(token,view)==(recording?MODWERK_SAMPLE_STALE:MODWERK_SAMPLE_OK));
        CHECK(!writes && !bad && !masked && !locked);
    }
    setup(0,0);CHECK(mw_sample_editor_begin(&mw_sample_editor,&owner,&token)==MODWERK_SAMPLE_OK);
    struct runtime_dsp from={0};from.present=1;from.module=owner.module;
    from.image=(const uint8_t *)(owner.owned_extent+owner.image_offset);
    mw_sample_owner_changing(&from);
    CHECK(retired==1 && mw_sample_editor_api.copy(token,view)==MODWERK_SAMPLE_STALE && !writes);
    CHECK(!masked && !locked && !bad);
    puts("PASS: both native metadata paths, buffer ownership, atomic rollback and fail-closed gates");return 0;
}
