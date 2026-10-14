// SPDX-License-Identifier: GPL-3.0-or-later
// Run the private receiver's on-demand engine ops (PLACE, CAS) and the stubs
// they steer under the independent vendored DSP interpreter. The Python test
// (test_resident_engines.py) writes the memory image and a script of steps
// and checks every answer; nothing here knows the expected result.
// Inputs are fresh private assemblies only; no stock image is required.
//   P addr value          set a P word
//   X addr value          set an X word
//   PKT entry w4 w5 w7    a packet (data words zero) through `entry`: prints "A 1" accepted, "A 0" refused
//   RP addr               prints "P addr value"
//   RUN addr steps        jsr addr, then prints "PC pc" after each interpreted instruction
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include "dsp56kEmu/dsp.h"
#include "dsp56kEmu/memory.h"
#include "dsp56kEmu/peripherals.h"
using namespace dsp56k;
struct Open : IMemoryValidator {
    bool memValidateAccess(EMemArea, TWord, bool) const override { return true; }
};
int main(int argc, char **argv) {
    if(argc!=2) return 2;
    std::ifstream script(argv[1]);
    Open validator;
    Memory memory(validator,0x080000,0x800000,0x200000);
    Peripherals56362 px;
    Peripherals56367 py;
    DSP dsp(memory,&px,&py);
    for(auto &m:dsp.regs().m) m.var=0xffffff;
    const TWord packet=0x2000, stop=0x3f000;
    std::string op;
    while(script>>op) {
        if(op=="P" || op=="X") {
            TWord address,value; script>>address>>value;
            memory.set(op=="P" ? MemArea_P:MemArea_X,address,value&0xffffff);
        } else if(op=="PKT") {
            TWord entry,w4,w5,w7; script>>entry>>w4>>w5>>w7;
            for(TWord n=0;n<64;++n) memory.set(MemArea_X,packet+n,0);
            memory.set(MemArea_X,packet+4,w4); memory.set(MemArea_X,packet+5,w5); memory.set(MemArea_X,packet+7,w7);
            memory.set(MemArea_X,packet+63,0x1234);
            dsp.regs().r[0].var=packet;
            dsp.setPC(stop); dsp.jsr(entry);
            unsigned n=0;
            while(dsp.getPC().toWord()!=stop && ++n<100000) dsp.execInterpreter();
            if(n>=100000) throw std::runtime_error("receiver did not return");
            std::cout<<"A "<<((px.getHDI08().readControlRegister()&0x10)==0)<<"\n";
        } else if(op=="RP") {
            TWord address; script>>address;
            std::cout<<"P "<<address<<" "<<memory.get(MemArea_P,address)<<"\n";
        } else if(op=="RUN") {
            TWord address,steps; script>>address>>steps;
            dsp.setPC(stop); dsp.jsr(address);
            for(TWord n=0;n<steps && dsp.getPC().toWord()!=stop;++n) {
                dsp.execInterpreter();
                std::cout<<"PC "<<dsp.getPC().toWord()<<"\n";
            }
        } else throw std::runtime_error("unknown step "+op);
    }
    if(!script.eof()) return 3;
    return 0;
}
