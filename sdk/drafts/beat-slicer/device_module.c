/* SPDX-License-Identifier: MIT
 * Basic Beat Slicer controller. All instrument access is through the proposed
 * shared base editor API; no stock address, PCM reader or native writer here.
 */
#include "../../runtime/loader/modwerk_module.h"
#include "../../machines/octatrack/include/modwerk_sample_editor.h"
#include "grid_preview.h"
#include "device_font.h"

#define YES 0x31
#define NO 0x32
#define UP 0x33
#define DOWN 0x20
static const struct modwerk_sample_editor_api *editor;
static struct modwerk_sample_view view;
static struct bs_grid_plan plan;
static struct modwerk_sample_grid proposal;
static const uint32_t spacings[5]={1,4,16,32,64};
static uint32_t token,active,tempo_source,spacing,reply,geometry,dirty,captured;
static uint32_t consumed[2];

static void close_editor(void)
{
    if(active && editor)editor->cancel(token);
    active=0;token=0;editor=0;
}
static void refresh(void)
{
    static uint32_t starts[BS_MAX_SLICES];
    if(!active || !editor)return;
    unsigned current=editor->copy(token,&view);
    if(current==MODWERK_SAMPLE_BUSY)return;
    if(current!=MODWERK_SAMPLE_OK){close_editor();return;}
    captured=1;
    if(!dirty)return;
    if(view.count>BS_MAX_SLICES){geometry=BS_INVALID;dirty=0;return;}
    for(uint32_t i=0;i<view.count;++i)starts[i]=view.records[i].start;
    struct bs_grid_request request={view.frame_rate,view.trim_start,view.trim_end,
        view.sample_bpm24,view.project_bpm24,spacings[spacing],tempo_source,view.count,starts};
    geometry=bs_grid_preview(&request,&plan);dirty=0;
}
void bs_device_open(uint32_t opened,const struct modwerk_sample_editor_api *api)
{
    close_editor();
    if(!opened || !api || api->abi!=MODWERK_SAMPLE_EDITOR_ABI || api->bytes<sizeof *api ||
       !api->copy || !api->confirm || !api->cancel)return;
    editor=api;token=opened;active=1;dirty=1;captured=0;
    geometry=BS_INVALID;reply=MODWERK_SAMPLE_OK;
    refresh();
}
/* Relocated function pointer, copied inline label. The base validates this
 * complete descriptor before admission and again under its native owner lock. */
const struct modwerk_sample_action bs_sample_action={
    MODWERK_SAMPLE_EDITOR_ABI,MODWERK_SAMPLE_ACTION_BYTES,0x446c151du,0,bs_device_open,
    "BEAT SLICER",{0,0,0}
};
void module_tick(struct modwerk_runtime_api *api)
{
    if(active)refresh();
    api->value=0x42530000u | (active?0x100u:0u) | geometry;
}
static int cycle(int current,int delta,int count)
{
    int next=current+delta%count;
    if(next<0)next+=count;
    if(next>=count)next-=count;
    return next;
}
int module_enc(int encoder,int delta)
{
    if(!active)return 0;
    if(encoder==0)tempo_source=(uint32_t)cycle((int)tempo_source,delta,2);
    else if(encoder==1)spacing=(uint32_t)cycle((int)spacing,delta,5);
    else {close_editor();return 0;}
    reply=MODWERK_SAMPLE_OK;dirty=1;refresh();return 1;
}
int module_key(int code,int pressed)
{
    if(code<0 || code>=64)return 0;
    uint32_t mask=1u<<((unsigned)code%32u),bank=(unsigned)code/32u;
    if(!pressed) {
        if(!(consumed[bank]&mask))return 0;
        consumed[bank]&=~mask;return 1;
    }
    if(consumed[bank]&mask)return 1;
    if(!active)return 0;
    if(code!=YES && code!=NO && code!=UP && code!=DOWN) {
        /* Transport, recorder, Part/project and other stock gestures pass only
         * after retiring our token. No hidden global key takeover. */
        close_editor();return 0;
    }
    consumed[bank]|=mask;
    if(code==NO){close_editor();return 1;}
    if(code==UP || code==DOWN)return module_enc(1,code==UP?1:-1);
    refresh();
    if(!active || !captured || dirty || geometry!=BS_OK)return 1;
    proposal.count=plan.count;
    for(uint32_t i=0;i<BS_MAX_SLICES;++i)proposal.starts[i]=plan.starts[i];
    reply=editor->confirm(token,&proposal);
    if(reply==MODWERK_SAMPLE_CONFIRMING) {
        /* Do not cancel: the base now owns the pending stock confirmation.
         * The token cannot be reused by this module after leaving the modal. */
        active=0;token=0;editor=0;
    }
    return 1;
}
static void text(char *out,const char *in)
{while(*in)*out++=*in++;*out=0;}
static char *append(char *out,const char *in)
{while(*in)*out++=*in++;*out=0;return out;}
static char *number(char *out,uint32_t value)
{
    if(value>=100)*out++=(char)('0'+value/100u);
    if(value>=10)*out++=(char)('0'+value/10u%10u);
    *out++=(char)('0'+value%10u);*out=0;return out;
}
void module_draw(unsigned char *frame)
{
    if(!active || !frame)return;
    char line[32],*at;
    for(uint32_t i=0;i<1024;++i)frame[i]=0;
    bs_device_text(frame,1,"BEAT SLICER");
    if(!captured) {
        bs_device_text(frame,22,"WAITING FOR SOURCE");
        bs_device_text(frame,55,"NO BACK");return;
    }
    at=append(line,tempo_source?"A PROJECT ":"A SAMPLE ");
    uint32_t bpm=tempo_source?view.project_bpm24:view.sample_bpm24;
    if(bpm>=720 && bpm<=7200) {
        at=number(at,bpm/24u);*at++='.';
        uint32_t fraction=(bpm%24u*100u+12u)/24u;
        *at++=(char)('0'+fraction/10u);*at++=(char)('0'+fraction%10u);*at=0;
    } else text(at,"NO BPM");
    bs_device_text(frame,12,line);
    at=append(line,"B SPACING ");at=number(at,spacings[spacing]);append(at,spacing?" BEATS":" BEAT");
    bs_device_text(frame,22,line);
    at=append(line,view.kind==MODWERK_SAMPLE_FLEX?"FLEX SLOT ":"STATIC SLOT ");number(at,view.slot+1u);
    bs_device_text(frame,32,line);
    if(reply==MODWERK_SAMPLE_PRESERVATION)text(line,"OLD SLICES CONFLICT");
    else if(geometry==BS_TOO_MANY)text(line,"MORE THAN 64 SLICES");
    else if(geometry!=BS_OK)text(line,"CHECK BPM OR TRIM");
    else if(reply==MODWERK_SAMPLE_BUSY)text(line,"SOURCE BUSY - RETRY");
    else if(reply!=MODWERK_SAMPLE_OK)text(line,"EDIT REFUSED");
    else {at=number(line,plan.count);append(at,plan.count==1?" SLICE":" SLICES");}
    bs_device_text(frame,43,line);
    bs_device_text(frame,55,"YES CREATE NO BACK");
}
