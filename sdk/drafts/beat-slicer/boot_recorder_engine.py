"""Compose private compiled recorder and engine observers in a full stock boot.

Normal panel input, real scheduler and both DSPs; eight reserved audio pages.
No production source admission, package, device, card save or timing claim.
"""
import argparse
from collections import Counter
import importlib.util
import json
from pathlib import Path
import shutil
import struct
import sys
import wave
from boot_observe import Port,digest
from boot_formats import observe
from boot_writer import hits,writes
from boot_recorder import key,record,snapshot,state_changes
from boot_source_native import call_original
from boot_engine_native import tap as editor_tap
from inspect_stock import STOCK_MAIN_SHA256
ROOT=Path(__file__).resolve().parent
ARENA_SHA='23c89015c010ce9d4e6e7957f9325b7da78b7ba75144de10d56cb22149f21e61'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('emulator','main','card','wav','output','arena-tool','native'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--card-sha256',required=True)
    p.add_argument('--allow-private-injection',action='store_true',required=True)
    a=p.parse_args()
    if not __debug__:p.error('Assertions must remain enabled.')
    out,repo=a.output.resolve(),ROOT.parents[2]
    if out.exists() or out==repo or repo in out.parents:p.error('Use fresh private output outside Git.')
    if digest(a.main)!=STOCK_MAIN_SHA256 or digest(a.card)!=a.card_sha256 or digest(a.arena_tool)!=ARENA_SHA:p.error('Private input identity differs.')
    native=json.loads((a.native/'recorder-engine.json').read_text())
    preparation_enabled=bool(native.get('preparationEnabled',False))
    binary,symbols_path=a.native/'recorder-engine.bin',a.native/'recorder-engine.symbols'
    if native['textBase']!=0x46019df0 or digest(binary)!=native['binarySha256'] or digest(symbols_path)!=native['symbolsSha256']:p.error('Native fixture identity differs.')
    for name,expected in native['sourceSha256'].items():
        if digest(ROOT/name)!=expected:p.error('Native source differs: '+name)
    for name,expected in native['sdkDependencySha256'].items():
        if digest(repo/name)!=expected:p.error('SDK input differs: '+name)
    symbols={r.split()[2]:int(r.split()[0],16) for r in symbols_path.read_text().splitlines()}
    spec=importlib.util.spec_from_file_location('beat_slicer_arena',a.arena_tool)
    arena=importlib.util.module_from_spec(spec);sys.modules[spec.name]=arena;spec.loader.exec_module(arena)
    placed,pool_base,pool_count=arena.layout([('recorder-engine-fixture','top',8)]);reserve=placed[0]
    assert reserve.start+16==native['textBase'] and symbols['_end']+32<=reserve.end
    assert pool_base==0x40a955e0 and pool_count==14594
    private_main=bytearray(a.main.read_bytes())
    for address,expected,value,_ in arena.pokes([('recorder-engine-fixture','top',8)]):
        at=address-0x40000400;assert private_main[at:at+len(expected)]==expected
        private_main[at:at+len(value)]=value
    with wave.open(str(a.wav),'rb') as f:
        if (f.getnchannels(),f.getsampwidth(),f.getframerate(),f.getnframes())!=(2,2,44100,44100):p.error('Wrong original WAV fixture.')
        raw=f.readframes(f.getnframes())
    original=list(struct.unpack('<'+'h'*(len(raw)//2),raw))
    out.mkdir(parents=True);patched=out/'reserved-main.private.bin';patched.write_bytes(private_main)
    card=out/'card.private.img';shutil.copyfile(a.card,card)
    command=[str(a.emulator.resolve()),'--image',str(patched),'--card',str(card),'--mount',
        '--set','BEATLAB','--project','PROJECT 261023','--load-ms','90000','--dsp','--frame',
        '--ms','3000','--interactive','--main-level','off','--rtc','host','--mkii','--lcd',str(out/'lcd.private.bin')]
    port=Port(command,out);results=[]
    try:
        port.reply(b'ready ',timeout=600);assert port.loaded
        folder=out/'loaded';folder.mkdir();loaded=observe(port,16,2,original,folder)
        for address,_,value,_ in arena.pokes([('recorder-engine-fixture','top',8)]):assert port.peek(address,len(value))==value
        data=binary.read_bytes();assert len(data)<=symbols['__bss_start']-native['textBase']
        def poke(address,value):
            for at in range(0,len(value),4096):port.command(f'poke {address+at:#x} '+value[at:at+4096].hex())
        poke(reserve.start,bytes([0xa5])*(reserve.end-reserve.start));poke(native['textBase'],data)
        poke(symbols['__bss_start'],bytes(symbols['_end']-symbols['__bss_start']))
        assert call_original(port,symbols['bs_recorder_engine_init'])==0
        g_at,b_at,e_at=(symbols[n] for n in ('bs_recorder_test_guard','bs_recorder_test_boundary','bs_recorder_engine_boundary'))
        assert struct.unpack('>12I',port.peek(g_at,48))[2]==0,'Bootstrap admitted readers'
        original_receive=port.peek(0x40084854,6)
        assert original_receive[:2]==bytes.fromhex('4eb9') and int.from_bytes(original_receive[2:],'big')==0x40000d00
        for group,prefix in (('hookSites','bs_recorder_'),('engineHookSites','bs_recorder_engine_'),('preparationHookSites','bs_recorder_prepare_')):
            for name,site in native.get(group,{}).items():
                import hashlib
                assert hashlib.sha256(port.peek(site['address'],site['length'])).hexdigest()==site['sha256']
                patch=bytes.fromhex('4ef9')+symbols[prefix+name+'_entry'].to_bytes(4,'big')
                if site['length']==8:patch+=bytes.fromhex('4e71')
                assert len(patch)==site['length'];poke(site['address'],patch)
        def native_state(enabled=True,need_idle=True):
            for _ in range(200):
                g=struct.unpack('>12I',port.peek(g_at,48));b=struct.unpack('>19I',port.peek(b_at,76));e=struct.unpack('>4I',port.peek(e_at,16))
                assert b[0]==e[0]==g_at and not b[2] and not e[3] and not g[3],'Native observer fault'
                if not b[1] and not e[1] and not any(g[4:]):break
                port.command('run 0.1')
            else:raise AssertionError('Native observers did not reach a bounded quiescent checkpoint')
            assert bool(g[2])==enabled and (e[2] or not need_idle)
            assert not any(b[3:]),'Recorder scope leaked'
            entries=int.from_bytes(port.peek(symbols['bs_recorder_test_entries'],4),'big')
            exits=int.from_bytes(port.peek(symbols['bs_recorder_test_exits'],4),'big')
            assert entries==exits,'Recorder entries/returns differ at quiescence'
            result={'revision':g[0],'serial':g[1],'entries':entries,'exits':exits,'engineIdleSeen':e[2]}
            for label,prefix in (('recorder','bs_recorder_test_'),('preparation','bs_recorder_prepare_')):
                if prefix+'enter_masks' in symbols:
                    masks=[int.from_bytes(port.peek(symbols[prefix+suffix+'_masks'],4),'big') for suffix in ('enter','leave')]
                    counts=[int.from_bytes(port.peek(symbols[prefix+suffix],4),'big') for suffix in ('entries','exits')]
                    assert counts[0]==counts[1] and masks[0]==masks[1] and (not counts[0] or masks[0]),'Caller-mask/counter trace differs'
                    result[label+'ScopesEntered']=counts[0]
                    result[label+'CallerMaskLevels']=[level for level in range(8) if masks[0]&(1<<level)]
            return result
        port.command('run 500')
        # The saved project's first editor binding is empty Static. Merely
        # opening AED does not queue a waveform job. Use the previously proved
        # normal-panel Flex assignment/selection path to obtain a real job/idle
        # pair after an observer installed during an already waiting receive.
        if not int.from_bytes(port.peek(e_at+8,4),'big'):
            for name in ('aed','edit','no','playback','playback','yes','no'):editor_tap(port,name)
            port.command('key 0x26 8');port.command('run 60');editor_tap(port,'track1')
            port.command('key 0x26 0');port.command('run 60')
            for name in ('aed','edit','yes','yes'):editor_tap(port,name)
            port.command('run 1000')
            assert int.from_bytes(port.peek(0x46c8d1a0,4),'big')==1
            assert int.from_bytes(port.peek(0x46c8d19c,4),'big')==0
        closed=native_state(False)
        folder=out/'prepared';folder.mkdir();baseline=observe(port,16,2,original,folder)
        assert baseline['pcmSha256']==loaded['pcmSha256'] and baseline['controlsSha256']==loaded['controlsSha256']
        initial_settings=(out/'loaded/settings.private.bin').read_bytes()
        prepared_settings=(out/'prepared/settings.private.bin').read_bytes()
        changed=[i for i in range(274) if initial_settings[4*i:4*i+4]!=prepared_settings[4*i:4*i+4]]
        assert changed==[271] and int.from_bytes(initial_settings[1084:1088],'big')==0
        assert int.from_bytes(prepared_settings[1084:1088],'big')==44100,'SELECT ALL preparation differs'
        assert call_original(port,symbols['bs_recorder_engine_enable'],wait_ms=1)==0
        initial_native=native_state()
        port.command(f'watchmem {g_at:#x} 48');port.command(f'watchmem {e_at+4:#x} 4')
        port.command(f'watchmem {b_at+16:#x} 4')
        port.command('watch 0x400068e4,0x40005ff0,0x40005e48')
        def capture(track):native_state();return snapshot(port,track)
        def audit(stores,track,pcm,tail):
            tickets=[0]*8;recorder_ticket=engine_ticket=0;pcm_count=tail_count=recorder_scopes=engine_scopes=0
            uncovered=Counter();covered_state=0;transitions=[]
            for event in stores:
                _,pc,address,value,size,_=event
                if g_at+16<=address<g_at+48:
                    assert size==4 and (address-g_at)%4==0;tickets[(address-g_at-16)//4]=value
                if address==b_at+16:recorder_ticket=value;recorder_scopes+=bool(value)
                if address==e_at+4:engine_ticket=value;engine_scopes+=bool(value)
                if pcm<=address<pcm+64:
                    assert recorder_ticket and recorder_ticket in tickets,'PCM store outside native recorder scope';pcm_count+=1
                if address==tail:
                    assert size==2 and value==0 and pc==0x40095afc
                    assert engine_ticket and engine_ticket in tickets,'Map cleanup outside native engine scope';tail_count+=1
                for bank in range(2):
                    state=0x80004f1c+84*(track+8*bank)
                    if address<state+84 and address+size>state:
                        if any(tickets):covered_state+=1
                        else:uncovered[(hex(pc),size)]+=1
                    if address<=state+2<address+size:
                        change=state_changes([event],track);assert len(change)==1
                        transitions.append({**change[0],'guarded':bool(any(tickets)),
                            'recorderGuarded':bool(recorder_ticket and recorder_ticket in tickets),
                            'engineGuarded':bool(engine_ticket and engine_ticket in tickets)})
            assert not any(tickets) and not recorder_ticket and not engine_ticket,'Trace did not retire at checkpoint'
            return {'pcmPrefixStores':pcm_count,'mapTailStores':tail_count,'recorderScopes':recorder_scopes,'engineScopes':engine_scopes,
                'guardedRecorderStateStores':covered_state,'unguardedRecorderStateStores':[{'pc':pc,'bytes':size,'count':count} for (pc,size),count in sorted(uncovered.items())],
                'stateTransitions':transitions}
        for track in (0,7):
            before_native=native_state();initial=capture(track);assert initial['states']==[0,0]
            row=0x46c2e9c0+2*(track+2)*14602;first=int.from_bytes(port.peek(row,2),'big')
            count=int.from_bytes(port.peek(0x46c75e88+2*(128+track),2),'big')
            assert 0<first<=pool_count and count==460
            pcm=pool_base+first*6144;tail=row+2*14601
            port.command(f'watchmem {pcm:#x} 64');port.command(f'watchmem {tail:#x} 2')
            for bank in range(2):port.command(f'watchmem {0x80004f1c+84*(track+8*bank):#x} 84')
            native_state();hits(port);writes(port)
            record(port,track);port.command('run 200');started=capture(track)
            port.command('run 300');advanced=capture(track)
            assert started['states'][started['bank']]==2 and advanced['published']>started['published']>0
            record(port,track);port.command('run 200');retriggered=capture(track)
            assert retriggered['bank']==1-started['bank'] and retriggered['states']==[2,2]
            assert 0<retriggered['published']<advanced['published']
            port.command('run 300');before_stop=capture(track)
            key(port,'stop',True);key(port,'stop',False);port.command('run 500');stopped=capture(track)
            assert stopped['bank']==retriggered['bank'] and stopped['states'][stopped['bank']]==0
            assert stopped['states'][1-stopped['bank']]==2 and stopped['positions'][stopped['bank']]==0
            assert stopped['published']>=before_stop['published'] and stopped['queueCounts']==[0,0]
            calls,stores=hits(port),writes(port);coverage=audit(stores,track,pcm,tail)
            assert coverage['pcmPrefixStores'] and coverage['mapTailStores'] and coverage['recorderScopes'] and coverage['engineScopes']
            assert [(r['bank'],r['value'],r['bytes']) for r in coverage['stateTransitions']]==[(1,1,4),(1,2,1),(0,1,4),(0,2,1),(0,0,1)]
            recorder=[r for r in calls if r[1]==0x400068e4 and r[8]==track]
            callers=Counter(hex(r[7]) for r in recorder)
            assert set(callers)=={'0x4000d342','0x4000d36e'} and len(set(callers.values()))==1
            preparation=[r for r in calls if r[1]==0x40005ff0 and r[8]==track]
            stops=[r for r in calls if r[1]==0x40005e48 and r[8]==track]
            assert len(preparation)==2 and [r[9] for r in preparation]==[0x9010,0x1010]
            assert all(r[7]==0x4000d35c and r[10:12]==[0,0xffffffff] for r in preparation)
            assert len(stops)==1 and stops[0][7]==0x40007942 and stops[0][9]>0 and stops[0][10:12]==[0,0]
            assert [r['recorderGuarded'] for r in coverage['stateTransitions']]==([True]*5 if preparation_enabled else [False,True,False,True,True])
            assert sum(x['count'] for x in coverage['unguardedRecorderStateStores'])==(0 if preparation_enabled else 24)
            port.command('run 500');idle=capture(track);idle_coverage=audit(writes(port),track,pcm,tail)
            assert idle==stopped and not idle_coverage['pcmPrefixStores'] and not idle_coverage['mapTailStores'] and not idle_coverage['recorderScopes']
            assert int.from_bytes(port.peek(row,2),'big')==first and int.from_bytes(port.peek(0x46c75e88+2*(128+track),2),'big')==count
            folder=out/f'after-track-{track+1}';folder.mkdir();after=observe(port,16,2,original,folder)
            assert after['settingsSha256']==baseline['settingsSha256'] and after['controlsSha256']==baseline['controlsSha256']
            for at in range(0,len(data),4096):assert port.peek(native['textBase']+at,min(4096,len(data)-at))==data[at:at+4096]
            assert port.peek(reserve.start,16)==bytes([0xa5])*16 and port.peek(symbols['_end'],32)==bytes([0xa5])*32
            assert port.peek(0x40084854,6)==original_receive
            state=native_state()
            if preparation_enabled:assert state['preparationScopesEntered']-before_native['preparationScopesEntered']==2
            results.append({'track':track+1,'reservedRecorderPages':count,'firstRecorderPage':first,
                'initial':initial,'started':started,'advanced':advanced,'retriggered':retriggered,'stopped':stopped,'idle':idle,
                'callerCounts':dict(callers),'preparationCalls':[{'caller':hex(r[7]),'arguments':r[8:12]} for r in preparation],
                'stopCalls':[{'caller':hex(r[7]),'arguments':r[8:12]} for r in stops],'coverage':coverage,'idleCoverage':idle_coverage,'nativeState':state,
                'unrelatedFlexPreserved':True,'nativeCodeAndCanariesIntact':True})
            print(f'PASS track {track+1}: native PCM/cleanup tickets; uncovered recorder-state stores {sum(x["count"] for x in coverage["unguardedRecorderStateStores"])}',flush=True)
    finally:port.close()
    assert digest(card)==a.card_sha256 and digest(a.card)==a.card_sha256
    names=('boot_recorder_engine.py','boot_engine_native.py','boot_recorder.py','boot_source_native.py','boot_worker_native.py','boot_writer.py',
        'boot_formats.py','boot_observe.py','test_planner.py','inspect_stock.py',*native['sourceSha256'].keys())
    report={'scope':'Private reserved-memory recorder/engine observer composition under normal recording/retrigger/STOP; real emulator scheduler/DSPs, no source reader or hardware',
        'sourceSha256':{n:digest(ROOT/n) for n in names},'mainSha256':STOCK_MAIN_SHA256,'reservedMainSha256':digest(patched),
        'nativeReceiptSha256':digest(a.native/'recorder-engine.json'),'nativeBinarySha256':digest(binary),'emulatorSha256':digest(a.emulator),
        'sdkRevision':native['sdkRevision'],'sdkDependencySha256':native['sdkDependencySha256'],'codegenGuardSha256':native['codegenGuardSha256'],
        'arenaToolSha256':ARENA_SHA,'reservedPages':8,'physicalUsablePages':pool_count,'cardSha256':a.card_sha256,'wavSha256':digest(a.wav),
        'preparationBoundaryEnabled':preparation_enabled,'closedBootstrap':closed,'preparationSettingsWordsChanged':changed,'preparedSource':baseline,'initialNative':initial_native,'results':results,'cardUnchanged':True,'receiveCallUnchanged':True,
        'exitCode':0,'hardware':'not tested','audio':'not qualified','physicalTiming':'not measured',
        'nativeSourceAccess':'not implemented; complete recorder/Pickup, allocator, UI, DMA/cache and physical writer coverage remain open'}
    (out/'recorder-engine-boot.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
