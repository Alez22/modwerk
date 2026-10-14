// SPDX-License-Identifier: MIT
// Private actual-machine dispatcher proof. Local source-bound image required;
// the reviewed continuation is observed before stock redraw, never stubbed.
#include <algorithm>
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
static constexpr uint32_t stack=0x46c7f920,continuation=0x40045920,bank=0x400e21e0;
static std::vector<uint8_t> load(const char *path) {
    std::ifstream f(path,std::ios::binary);assert(f.good());return {(std::istreambuf_iterator<char>(f)),{}};
}
int main(int argc,char **argv) {
    assert(argc==6);
    const uint32_t origin=std::stoul(argv[4],nullptr,0);
    const unsigned mask=std::stoul(argv[5]);assert(mask && mask<=3);
    auto image=load(argv[2]);ot::Machine m(load(argv[1]));
    for(unsigned i=0;i<image.size();i++)m.write8(origin+i,image[i]);
    std::map<std::string,uint32_t> symbols;std::ifstream f(argv[3]);std::string name;uint32_t offset;
    while(f>>name>>offset)symbols[name]=origin+offset;
    const bool poly=mask&1,qz=symbols.count("qz_octkey");
    const uint32_t entry=poly?symbols.at("mr_octkey"):symbols.at("qz_octkey");
    m.mapRegion(0x10000000,0x000b0000);m.mapRegion(0x100c0000,0x00040000);
    m.write32(0x46c82456,bank);m.write8(0x100b14cf,0);m.write8(0x100b14cc,0);
    constexpr uint32_t part=bank+0x8ed80;
    for(unsigned i=0;i<8;i++)m.write8(part+0x22+i,1);
    m.write8(bank+0x8f04b,0);
    unsigned calls=0,polyRoutes=0,qzRoutes=0,stockRoutes=0;
    for(unsigned mode=0;mode<4;mode++)for(unsigned key:{0x34u,0x21u})
        for(int value:{-6,-4,0,3,4})for(unsigned octave:{0u,1u})for(bool synthName:{false,true}) {
        // Audio PL/1 takes POLY first; non-POLY audio and MIDI reach QZ
        // when present. An absent weak QZ target reaches exact POLY fallback.
        const bool selectedPoly=poly && mode==0,midi=mode==2;
        const bool expectedPoly=selectedPoly || !qz;
        if((expectedPoly && selectedPoly && (value<-6 || value>3)) ||
           (!expectedPoly && (value<-4 || value>4)))continue;
        const std::string file=synthName?"SYNTH_TEST.wav":"SAMPLE_TEST.wav";
        for(unsigned i=0;i<file.size()+1;i++)m.write8(0x100b14f0+i,i<file.size()?file[i]:0);
        m.write32(0x80000012,midi?1:0);
        // The separate private AB variant also preserves Quantizer's exact
        // filename/MIDI policy on signed AB audio tracks; AB never takes the
        // POLY handler merely because the shared controller is present.
        m.write8(part+0x3c,selectedPoly?'P':mode==3?'A':0);m.write8(part+0x3d,selectedPoly?'L':mode==3?'B':0);m.write8(part+0x3e,(selectedPoly || mode==3)?1:0);
        m.write32(0x460d16fc,octave);
        if(poly)m.write8(symbols.at("poly_octave"),uint8_t(value));
        if(qz)m.write8(symbols.at("qz_oct"),uint8_t(value));
        auto *cpu=m.getCpuState();for(unsigned r=0;r<15;r++)m68k_set_reg(cpu,m68k_register_t(M68K_REG_D0+r),0x47070000+4*r);
        m68k_set_reg(cpu,M68K_REG_D0,0x12345678);m68k_set_reg(cpu,M68K_REG_D1,0x34567890);
        m68k_set_reg(cpu,M68K_REG_D2,key);m68k_set_reg(cpu,M68K_REG_SP,stack);
        m.write32(stack,0x47300000);m.write32(stack+8,key);
        auto unmapped=m.unmappedCount();m68k_set_reg(cpu,M68K_REG_PC,entry);unsigned budget=10000,routes=0;
        const uint32_t handler=expectedPoly?symbols.at("poly_octave_button"):symbols.at("qz_octkey");
        while(m.pc()!=continuation && budget--) {
            if(m.pc()==handler) {
                routes++;
                assert(m68k_get_reg(cpu,M68K_REG_SP)==stack);
                assert(m68k_get_reg(cpu,M68K_REG_D0)==0x12345678 && m68k_get_reg(cpu,M68K_REG_D1)==0x34567890);
                assert(m68k_get_reg(cpu,M68K_REG_A0)==0x47070020 && m68k_get_reg(cpu,M68K_REG_A1)==0x47070024);
                assert(m68k_get_reg(cpu,M68K_REG_D2)==key);
            }
            assert(m.step());
        }
        assert(m.pc()==continuation && routes==1 && m.unmappedCount()==unmapped);
        assert(m68k_get_reg(cpu,M68K_REG_SP)==stack);
        const int delta=key==0x34?-1:1;
        if(expectedPoly && selectedPoly) {
            assert(int8_t(m.read8(symbols.at("poly_octave")))==std::clamp(value+delta,-6,3));
            assert(m.read32(0x460d16fc)==octave);polyRoutes++;
            if(qz)assert(int8_t(m.read8(symbols.at("qz_oct")))==value);
        } else if(!expectedPoly && synthName) {
            assert(int8_t(m.read8(symbols.at("qz_oct")))==std::clamp(value+delta,-4,4));
            assert(!m.read32(0x460d16fc));qzRoutes++;
            if(poly)assert(int8_t(m.read8(symbols.at("poly_octave")))==value);
        } else {
            assert(m.read32(0x460d16fc)==(octave^1));stockRoutes++;
            if(poly)assert(int8_t(m.read8(symbols.at("poly_octave")))==value);
            if(qz)assert(int8_t(m.read8(symbols.at("qz_oct")))==value);
        }
        calls++;
    }
    std::printf("{\"mask\":%u,\"origin\":%u,\"calls\":%u,\"polyRoutes\":%u,\"quantizerRoutes\":%u,\"stockFallbackRoutes\":%u,\"exactStackAndEntryRegisters\":true,\"singleHandlerContinuation\":true,\"unmapped\":false,\"hardware\":false,\"admission\":false}\n",
        mask,origin,calls,polyRoutes,qzRoutes,stockRoutes);
}
