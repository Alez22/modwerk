"""Compile private recorder plus existing base-owned engine hook composition.

No production hook/event, source reader or package is enabled. Replay bytes stay
in private output; full-boot execution is a separate, source-bound experiment.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from recorder_native import ROOT,run,sha

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--main',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();repo=ROOT.parents[2]
    pin=json.loads((ROOT/'recorder-engine-runtime-sources.json').read_text())
    for name,expected in pin['sha256'].items():
        if sha(repo/name)!=expected:p.error('SDK dependency differs: '+name)
    subprocess.run([sys.executable,'-B',str(ROOT/'recorder_native.py'),'--main',str(a.main),
                    '--output',str(a.output),'--compile-only','--text-base','0x46019df0'],check=True)
    out=a.output.resolve();receipt=out/'recorder.json';report=json.loads(receipt.read_text())
    spec=importlib.util.spec_from_file_location('guard',repo/'sdk/runtime/m68k_codegen.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    added=[]
    for name in ('engine_boundary','test_recorder_engine'):
        obj=out/(name+'.o');run('m68k-elf-gcc',*report['flags'],'-c',str(ROOT/(name+'.c')),'-o',str(obj));added.append(obj)
    guard.check(added)
    guards=json.loads((repo/'sdk/runtime/logging/stock-guards.json').read_text());stock=a.main.read_bytes()
    assembly=['.text','.align 2']
    for name,address in (('idle',0x4008484e),('job',0x4008485e)):
        site=guards[name];assert site['address']==address and site['length']==6
        replay=stock[address-0x40000400:address-0x40000400+6]
        import hashlib
        assert hashlib.sha256(replay).hexdigest()==site['sha256']
        private=out/(name+'-replay.private.bin');private.write_bytes(replay)
        assembly += [f'.globl bs_recorder_engine_{name}_entry',f'bs_recorder_engine_{name}_entry:',
            'lea -64(%sp),%sp','movem.l %d0-%d7/%a0-%a6,(%sp)',
            'move.w %sr,%d0','move.w %d0,60(%sp)','move.l %sp,%a0',
            'lea -4(%sp),%sp','move.l %a0,(%sp)',f'jsr bs_recorder_engine_{name}',
            'lea 4(%sp),%sp','move.w 60(%sp),%d0','move.w %d0,%sr',
            'movem.l (%sp),%d0-%d7/%a0-%a6','lea 64(%sp),%sp',
            f'.incbin "{private}"',f'jmp {address+6:#x}']
    asm=out/'recorder-engine-hooks.private.S';asm.write_text('\n'.join(assembly)+'\n')
    obj=out/'recorder-engine-hooks.private.o';run('m68k-elf-gcc','-mcpu=5475','-c',str(asm),'-o',str(obj));added.append(obj)
    objects=[out/name for name in report['objectSha256']]+added
    elf,binary,symbols=out/'recorder-engine.elf',out/'recorder-engine.bin',out/'recorder-engine.symbols'
    run('m68k-elf-ld','--no-undefined','-e','bs_recorder_engine_init','-Ttext='+hex(report['textBase']),*map(str,objects),'-o',str(elf))
    if run('m68k-elf-nm','-u',str(elf)):p.error('Unresolved runtime helpers.')
    run('m68k-elf-objcopy','-O','binary',str(elf),str(binary));symbols.write_text(run('m68k-elf-nm',str(elf))+'\n')
    end=[int(row.split()[0],16) for row in symbols.read_text().splitlines() if row.split()[-1]=='_end'][0]
    if end+32>0x46025de0:p.error('Fixture exceeds explicit eight-page reservation.')
    report.update({'scope':'Private recorder/engine hook composition compilation only; execution is separate',
        'binarySha256':sha(binary),'symbolsSha256':sha(symbols),'fixtureEnd':end,
        'objectSha256':{o.name:sha(o) for o in objects},'sdkRevision':pin['revision'],'sdkDependencySha256':pin['sha256'],
        'codegenGuardSha256':sha(repo/'sdk/runtime/m68k_codegen.py'),
        'engineHookSites':{name:guards[name] for name in ('idle','job')}})
    report['sourceSha256'].update({n:sha(ROOT/n) for n in ('recorder_engine_native.py','recorder-engine-runtime-sources.json',
        'engine_boundary.c','engine_boundary.h','test_recorder_engine.c')})
    (out/'recorder-engine.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Compiled private shared-guard recorder/engine fixture; no execution or source admission claim.')
if __name__=='__main__':main()
