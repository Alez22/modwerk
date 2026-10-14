// SPDX-License-Identifier: MIT
// Private real ColdFire AB/shared-controller proof. Local source-bound images
// only. DSP audio, jobs/ACK readiness, boot and lifetime admission unqualified.
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdio>
#include <fstream>
#include <iterator>
#include <map>
#include <string>
#include <vector>
#include "machine.h"
#include "mc68k/Musashi/m68k.h"
#include "mc68k/cpuState.h"

static constexpr uint32_t stack=0x46c7f920,stop=0x47300000,bank=0x400e21e0;
static constexpr uint32_t partOffset=0x8ed80,stride=6322,sram=0x100a4ece;
static std::vector<uint8_t> load(const char *path) {
    std::ifstream f(path,std::ios::binary); assert(f.good()); return {(std::istreambuf_iterator<char>(f)),{}};
}
int main(int argc,char **argv) {
    assert(argc==6);
    const uint32_t origin=std::stoul(argv[4],nullptr,0);
    const unsigned mask=std::stoul(argv[5]); assert(mask<=7); // zero: AB alone, private source proof only
    auto image=load(argv[2]); ot::Machine m(load(argv[1]));
    for(unsigned i=0;i<image.size();i++)m.write8(origin+i,image[i]);
    std::map<std::string,uint32_t> symbols; std::ifstream f(argv[3]); std::string name; uint32_t offset;
    while(f>>name>>offset)symbols[name]=origin+offset;
    m.mapRegion(0x10000000,0x000b0000); m.mapRegion(0x100c0000,0x00040000);
    m.write32(0x46c82456,bank); m.write8(0x80000015,0);
    auto read=[&](uint32_t at,unsigned n) { std::vector<uint8_t> b(n); for(unsigned i=0;i<n;i++)b[i]=m.read8(at+i); return b; };
    auto write=[&](uint32_t at,const std::vector<uint8_t> &b) { for(unsigned i=0;i<b.size();i++)m.write8(at+i,b[i]); };
    unsigned calls=0,assignments=0,refusals=0,rendererRoutes=0,controlFrames=0;
    auto enter=[&](const std::string &symbol,const std::vector<uint32_t> &args) {
        auto *cpu=m.getCpuState();
        for(unsigned r=0;r<15;r++)m68k_set_reg(cpu,m68k_register_t(M68K_REG_D0+r),0x47070000+4*r);
        m68k_set_reg(cpu,M68K_REG_SP,stack); m.write32(stack,stop);
        for(unsigned i=0;i<args.size();i++)m.write32(stack+4+4*i,args[i]);
        m68k_set_reg(cpu,M68K_REG_PC,symbols.at(symbol));
    };
    auto call=[&](const std::string &symbol,const std::vector<uint32_t> &args) {
        auto unmapped=m.unmappedCount(); enter(symbol,args); unsigned budget=200000;
        while(m.pc()!=stop && budget--)assert(m.step());
        assert(m.pc()==stop && m.unmappedCount()==unmapped);
        assert(m68k_get_reg(m.getCpuState(),M68K_REG_SP)==stack+4);
        for(unsigned r=2;r<8;r++)assert(m68k_get_reg(m.getCpuState(),m68k_register_t(M68K_REG_D0+r))==0x47070000+4*r);
        for(unsigned r=2;r<7;r++)assert(m68k_get_reg(m.getCpuState(),m68k_register_t(M68K_REG_A0+r))==0x47070020+4*r);
        calls++; return m68k_get_reg(m.getCpuState(),M68K_REG_D0);
    };
    std::map<unsigned,unsigned> rows; unsigned row=5;
    for(unsigned kind=1;kind<=4;kind++) {
        const bool present=kind==2 || (kind==1 && (mask&1)) || (kind==3 && (mask&2)) || (kind==4 && (mask&4));
        assert(call("mr_row",{kind})==(present?row:0)); if(present)rows[kind]=row++;
    }
    const auto stockTable=read(0x400d5f38,36),stockDefaults=read(0x400d320c,12);
    auto parameterOffset=[](unsigned track,unsigned k) { return (k<6?0x2au:0x1dau)+30*track+6+k%6; };
    auto basePart=[&]() {
        std::vector<uint8_t> b(stride,0);
        // Nonowned bytes carry a reproducible marker so assignments cannot
        // silently zero or copy another track's state.
        for(unsigned i=0;i<b.size();i++)b[i]=uint8_t((i*17+3)%127);
        for(unsigned t=0;t<8;t++) { b[0x22+t]=1; b[60+30*t]=b[61+30*t]=b[62+30*t]=0; }
        return b;
    };
    for(unsigned p=0;p<4;p++)for(unsigned track=0;track<8;track++) {
        const uint32_t part=bank+partOffset+p*stride,mirror=sram+p*stride;
        m.write8(0x100b14cf,p); m.write8(0x100b14cc,track);
        std::vector<unsigned> destinations={0,1,2,3,4,rows.at(2)};
        for(auto item:rows)if(item.first!=2)destinations.push_back(item.second);
        for(unsigned destination:destinations) {
            auto before=basePart(); write(part,before);write(mirror,before);
            assert(call("mr_assign",{part,track,rows.at(2)})==1);
            assert(call("mr_current_owner",{})==2);
            for(unsigned k=0;k<12;k++) {
                m.write8(part+parameterOffset(track,k),uint8_t(101+k));
                m.write8(mirror+parameterOffset(track,k),uint8_t(101+k));
            }
            const auto active=read(part,stride);
            const unsigned result=call("mr_assign",{part,track,destination});
            assignments++;
            assert(result==(destination<5?destination:1));
            if(destination<5) {
                auto expected=active;
                for(unsigned k=0;k<3;k++)expected[60+30*track+k]=0;
                for(unsigned k=0;k<12;k++)expected[parameterOffset(track,k)]=stockDefaults[k];
                assert(read(part,stride)==expected && read(mirror,stride)==expected);
            } else if(destination==rows.at(2)) {
                assert(read(part,stride)==active && read(mirror,stride)==active);
            } else {
                unsigned expectedKind=0; for(auto item:rows)if(item.second==destination)expectedKind=item.first;
                assert(call("mr_current_owner",{})==expectedKind);
                if(expectedKind==1 || expectedKind==3) {
                    for(unsigned k=0;k<12;k++) {
                        const unsigned at=parameterOffset(track,k);
                        const uint8_t expected=(expectedKind==1 && (k==6 || k==10))?0:stockDefaults[k];
                        assert(m.read8(part+at)==expected && m.read8(mirror+at)==expected);
                    }
                    if(expectedKind==1)for(unsigned pool=0;pool<2;pool++) {
                        unsigned at=0x1da+30*track+6*pool+4;
                        assert(!m.read8(part+at) && !m.read8(mirror+at));
                    }
                } else {
                    auto defaults=read(symbols.at("fm_defaults"),12);
                    for(unsigned k=0;k<12;k++)assert(m.read8(part+parameterOffset(track,k))==defaults[k] && m.read8(mirror+parameterOffset(track,k))==defaults[k]);
                }
            }
        }
        if(mask&1) {
            auto b=basePart(); b[60+30*track]='A'; b[61+30*track]='B'; b[62+30*track]=1;
            const unsigned other=(track+1)%8; b[60+30*other]='P'; b[61+30*other]='L'; b[62+30*other]=1;
            write(part,b);write(mirror,b);
            assert(call("mr_assign",{part,track,rows.at(1)})==0xffffffffu);
            assert(read(part,stride)==b && read(mirror,stride)==b);refusals++;
        }
        auto b=basePart(); b[60+30*track]='A'; b[61+30*track]='B'; b[62+30*track]=1; write(part,b);write(mirror,b);
        call("ab_ui_tick",{}); assert(read(0x400d5f38,36)==stockTable);
        uint32_t page=call("mr_page",{part+0x22+track});
        assert(page>=origin && page+0x192<=origin+image.size());
        assert(call("mr_type",{1,part+0x22+track})==rows.at(2));
        assert(read(0x400d5f38,36)==stockTable);
        for(unsigned pool:{0u,2u}) {m.write8(part+0x22+track,pool);assert(call("mr_current_owner",{})==0);}
        m.write8(part+0x22+track,1);
        for(unsigned kind=0;kind<=4;kind++)for(unsigned ping=0;ping<2;ping++)for(unsigned split:{0u,7u,15u}) {
            const std::array<std::array<uint8_t,3>,5> sigs={{{0,0,0},{'P','L',1},{'A','B',1},{'S','2',2},{'F','M',1}}};
            for(unsigned i=0;i<3;i++)m.write8(part+60+30*track+i,sigs[kind][i]);
            // The dispatcher checks ownership; an absent saved signature may
            // reach FM's own stock fallback. Observe the exact callee boundary
            // without replacing any handler or stock renderer.
            const unsigned routedOwner=kind==1 && !(mask&1)?0:kind==3 && !(mask&3)?0:kind;
            const uint32_t target=routedOwner==2?symbols.at("ab_render"):
                (routedOwner!=1 && routedOwner!=3 && (mask&4))?symbols.at("sy_render"):0x40004008;
            enter("mr_source_render_impl",{track,ping,split,16});unsigned budget=10000;
            auto unmapped=m.unmappedCount();
            while(m.pc()!=target && budget--)assert(m.step());
            assert(m.pc()==target && m.unmappedCount()==unmapped);
            const auto sp=m68k_get_reg(m.getCpuState(),M68K_REG_SP);
            const std::array<uint32_t,4> expectedArgs={track,ping,split,16};
            for(unsigned i=0;i<4;i++)assert(m.read32(sp+4+4*i)==expectedArgs[i]);
            rendererRoutes++;calls++;
        }
        for(unsigned i=0;i<3;i++)m.write8(part+60+30*track+i,std::array<uint8_t,3>{'A','B',1}[i]);
        for(unsigned ping=0;ping<2;ping++)for(unsigned model=0;model<2;model++)for(unsigned split=0;split<16;split++) {
            const uint32_t record=0x80001c90+ping*0xa80+336*track;
            for(unsigned i=0;i<200;i++)m.write8(record+i,0xa5);
            m.write32(0x80001c80,record);m.write32(0x800062a8,0x80006500);
            std::array<uint8_t,12> knobs={12,23,34,45,56,67,uint8_t(model),89,90,101,112,123};
            for(unsigned i=0;i<6;i++)m.write16(0x80006500+2*i,unsigned(knobs[i])<<8);
            for(unsigned i=6;i<12;i++)m.write8(0x80000830+72*track+i-6,knobs[i]);
            m.write8(0x46104d0c+track,16);
            call("ab_render",{track,ping,0,split});call("ab_render",{track,ping,split,16});
            assert(m.read32(record)==0xab090000 && m.read32(record+4)==0x09090001);
            assert(!m.read32(record+8) && !m.read32(record+12));
            for(unsigned i=0;i<12;i++)assert(m.read16(record+16+2*i)==knobs[i]);
            assert(m.read32(0x80001c80)==record+160);
            for(unsigned i=160;i<200;i++)assert(m.read8(record+i)==0xa5);
            controlFrames++;
        }
    }
    std::printf("{\"mask\":%u,\"origin\":%u,\"calls\":%u,\"assignments\":%u,\"refusedPolyAssignments\":%u,\"rendererEntryRoutes\":%u,\"controlFrames\":%u,\"exactAbStockRestore\":true,\"privateDescriptors\":true,\"stockDescriptorTableUnchanged\":true,\"unmapped\":false,\"hardware\":false,\"dspAudio\":false,\"controllerReadyQualified\":false,\"admission\":false}\n",
        mask,origin,calls,assignments,refusals,rendererRoutes,controlFrames);
}
