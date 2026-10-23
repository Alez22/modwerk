/* SPDX-License-Identifier: MIT */
#include "flex_copy.h"
#define CHECK(x) do { if (!(x)) return __LINE__; } while (0)
#define PAGE 6144u
#define VP(type, address) ((volatile type *)(uintptr_t)(address))
struct fixture {
    struct bs_flex_binding binding;
    struct bs_source_snapshot source;
    struct bs_pcm_read request;
    uint32_t ready, controls[128*11], formats[16], offsets[256], used;
    uint16_t counts[128], pages[6];
    uintptr_t pages_at, offsets_at;
#ifndef BS_FLEX_STOCK
    uint8_t pool[8*PAGE];
#endif
    uint8_t output[BS_SESSION_BYTES+2];
    uint32_t queries, reply_error, bytes;
};
static struct fixture f;
static void clear(void *p, uint32_t n) {
    for (uint32_t i=0;i<n;++i) ((uint8_t *)p)[i]=0;
}
static void put(const volatile uint32_t *p, uint32_t i, uint32_t value) {
    ((volatile uint32_t *)(uintptr_t)p)[i]=value;
}
static void put16(const volatile uint16_t *p, uint32_t i, uint16_t value) {
    ((volatile uint16_t *)(uintptr_t)p)[i]=value;
}
static void putptr(const volatile uintptr_t *p, uintptr_t value) {
    *(volatile uintptr_t *)(uintptr_t)p=value;
}
static uint8_t value(uint32_t frame,uint32_t byte) { return (uint8_t)(frame*19+byte*31+7); }
static void query(uint32_t entry,uint32_t slot,uint32_t frame,struct bs_pool_span *out) {
    ++f.queries;
#ifdef BS_FLEX_STOCK
    bs_flex_stock_query(entry,slot,frame,out);
#else
    (void)entry;
    uint32_t format=f.binding.controls[slot*11], width=(format&2?2u:3u)*(format&1?2u:1u);
    uint32_t per_page=PAGE/width, page=frame/per_page;
    const uint16_t *pages=(const uint16_t *)*f.binding.pages_at;
    const uint32_t *offsets=(const uint32_t *)*f.binding.offsets_at;
    out->data=f.binding.pool+pages[offsets[slot]+page]*PAGE+(frame%per_page)*width;
    out->frames=per_page-frame%per_page;
    if (out->frames>f.binding.controls[slot*11+4]-frame) out->frames=f.binding.controls[slot*11+4]-frame;
#endif
    if(f.reply_error==1) ++out->data;
    if(f.reply_error==2) ++out->frames;
    if(f.reply_error==3) out->frames=0;
    if(f.reply_error==4) out->data=0;
}
static void setup(uint32_t format,uint32_t slot) {
    clear(&f,sizeof(f));
    f.binding.query=query;f.binding.lookup_entry=0x4009499c;
    f.binding.page_bytes=PAGE;f.binding.physical_pages=8;f.binding.pool_bytes=8*PAGE;
    f.binding.map_capacity=3;
    f.binding.pages_region=(const uint8_t *)f.pages;f.binding.pages_region_bytes=sizeof(f.pages);
    f.binding.offsets_region=(const uint8_t *)f.offsets;f.binding.offsets_region_bytes=sizeof(f.offsets);
#ifdef BS_FLEX_STOCK
    f.binding.ready=VP(uint32_t,0x46105408);
    f.binding.controls=VP(uint32_t,0x46c922c4);
    f.binding.formats=VP(uint32_t,0x80003c20);
    f.binding.pages_at=VP(uintptr_t,0x80006914);f.binding.offsets_at=VP(uintptr_t,0x80006918);
    f.binding.counts=VP(uint16_t,0x46c75e88);f.binding.used=VP(uint32_t,0x8000691c);
    f.binding.pool=(const uint8_t *)(uintptr_t)0x40a955e0;
#else
    f.binding.ready=&f.ready;f.binding.controls=f.controls;f.binding.formats=f.formats;
    f.binding.pages_at=&f.pages_at;f.binding.offsets_at=&f.offsets_at;
    f.binding.counts=f.counts;f.binding.used=&f.used;f.binding.pool=f.pool;
#endif
    put(f.binding.ready,0,1);put(f.binding.used,0,3);
    putptr(f.binding.pages_at,(uintptr_t)f.pages);putptr(f.binding.offsets_at,(uintptr_t)f.offsets);
    f.pages[0]=f.pages[3]=3;f.pages[1]=f.pages[4]=7;f.pages[2]=f.pages[5]=2;
    f.source.kind=BS_SOURCE_FLEX;f.source.slot=slot;
    f.source.format.bits=format&2?16:24;f.source.format.channels=format&1?2:1;
    uint32_t width=f.source.format.bits/8*f.source.format.channels,per_page=PAGE/width;
    f.source.frames=2*per_page+17;
    put(f.binding.controls,slot*11,format);put(f.binding.controls,slot*11+2,0);
    put(f.binding.controls,slot*11+4,f.source.frames);put(f.binding.controls,slot*11+5,41);
    put(f.binding.formats,format*4+1,per_page);put(f.binding.formats,format*4+2,width);
    put16(f.binding.counts,slot,3);
    for(uint32_t frame=0;frame<f.source.frames;++frame)
        for(uint32_t b=0;b<width;++b)
            ((uint8_t *)(uintptr_t)f.binding.pool)[f.pages[frame/per_page]*PAGE+(frame%per_page)*width+b]=value(frame,b);
    f.request.count=32;f.request.operation=1;f.request.revision=1;
    for(uint32_t i=0;i<sizeof(f.output);++i)f.output[i]=0xa5;
    f.bytes=0x12345678;
}
static enum bs_provider_reply run(void) {
    return bs_flex_copy_locked(&f.binding,&f.source,&f.request,f.output+1,BS_SESSION_BYTES,&f.bytes);
}
static int copies(void) {
    for(uint32_t format=0;format<4;++format)for(uint32_t slot_index=0;slot_index<2;++slot_index)
    for(uint32_t position=0;position<6;++position)for(uint32_t amount=0;amount<2;++amount) {
        setup(format,slot_index?127:0);
        uint32_t width=f.source.format.bits/8*f.source.format.channels,edge=PAGE/width;
        uint32_t first=position==0?0:position==1?edge-1:position==2?edge:position==3?edge+1:position==4?2*edge-1:2*edge+9;
        f.request.first=first;f.request.count=amount?32:1;
        if(f.request.count>f.source.frames-first)f.request.count=f.source.frames-first;
        uint32_t count=f.request.count;
        if(count>edge-first%edge)count=edge-first%edge;
        CHECK(run()==BS_PROVIDER_READY && f.queries==1 && f.bytes==count*width);
        for(uint32_t i=0;i<f.bytes;++i)CHECK(f.output[i+1]==value(first+i/width,i%width));
        CHECK(f.output[0]==0xa5);
        for(uint32_t i=f.bytes+1;i<sizeof(f.output);++i)CHECK(f.output[i]==0xa5);
        CHECK(f.binding.controls[f.source.slot*11+5]==41);
    }
    return 0;
}
static int refusals(void) {
    for(uint32_t mode=0;mode<34;++mode) {
        setup(3,0);
        switch(mode) {
        case 0: put(f.binding.ready,0,0);break;
        case 1: put(f.binding.controls,2,1);break;
        case 2: put(f.binding.controls,4,f.source.frames+1);break;
        case 3: put(f.binding.controls,0,4);break;
        case 4: f.source.kind=BS_SOURCE_STATIC;break;
        case 5: f.source.slot=128;break;
        case 6: f.source.frames=0;break;
        case 7: f.source.format.bits=8;break;
        case 8: f.source.format.channels=0;break;
        case 9: f.source.format.little_endian=1;break;
        case 10: f.request.count=0;break;
        case 11: f.request.count=33;break;
        case 12: f.request.first=f.source.frames;break;
        case 13: f.request.first=f.source.frames-1;break;
        case 14: put(f.binding.formats,3*4+1,1);break;
        case 15: put(f.binding.formats,3*4+2,1);break;
        case 16: put(f.binding.used,0,0);break;
        case 17: put(f.binding.used,0,4);break;
        case 18: put16(f.binding.counts,0,0);break;
        case 19: put16(f.binding.counts,0,2);break;
        case 20: f.offsets[0]=4;break;
        case 21: f.offsets[0]=1;break;
        case 22: f.pages[0]=8;break;
        case 23: putptr(f.binding.pages_at,0);break;
        case 24: putptr(f.binding.offsets_at,0);break;
        case 25: putptr(f.binding.pages_at,(uintptr_t)f.pages+1);break;
        case 26: putptr(f.binding.offsets_at,(uintptr_t)f.offsets+1);break;
        case 27: f.binding.pages_region_bytes=5;break;
        case 28: f.binding.offsets_region_bytes=511;break;
        case 29: f.binding.pool_bytes=8*PAGE-1;break;
        case 30: f.binding.physical_pages=0xffffffffu;break;
        case 31: f.binding.lookup_entry=0;break;
        case 32: f.binding.query=0;break;
        default:f.source.format.channels=1;break;
        }
        CHECK(run()!=BS_PROVIDER_READY && !f.queries && f.bytes==0x12345678);
        for(uint32_t i=0;i<sizeof(f.output);++i)CHECK(f.output[i]==0xa5);
    }
    for(uint32_t error=1;error<=4;++error) {
        setup(3,0);f.reply_error=error;
        CHECK(run()==BS_PROVIDER_FAILED && f.queries==1 && f.bytes==0x12345678);
        for(uint32_t i=0;i<sizeof(f.output);++i)CHECK(f.output[i]==0xa5);
    }
    setup(3,0);
    CHECK(bs_flex_copy_locked(&f.binding,&f.source,&f.request,f.output+1,1,&f.bytes)==BS_PROVIDER_FAILED);
    CHECK(!f.queries && f.bytes==0x12345678);
    return 0;
}
static int remapped(void) {
    for(uint32_t format=0;format<4;++format) {
        setup(format,127);
        putptr(f.binding.pages_at,(uintptr_t)(f.pages+3));
        putptr(f.binding.offsets_at,(uintptr_t)(f.offsets+128));
        CHECK(run()==BS_PROVIDER_READY && f.queries==1);
        uint32_t width=f.source.format.bits/8*f.source.format.channels;
        for(uint32_t i=0;i<f.bytes;++i)CHECK(f.output[i+1]==value(i/width,i%width));
    }
    return 0;
}
int bs_flex_selftest(void) {
    int error=copies();if(error)return error;
    error=refusals();if(error)return error;
    return remapped();
}
