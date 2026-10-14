# SPDX-License-Identifier: MIT
"""Private Analog BD participant composition beside the ordinary machine group.

`machine_composition.py` stays byte-exact: its compositions, receipts and
recipes keep their pins and it still refuses AB with POLY/VECTOR/FM. This file
adds the explicit AB participant variant of the same MIT shared controller:
AB signatures are honoured only on FLEX tracks while AB is linked, and the
twelve borrowed FLEX bytes are restored in both Part copies when a signed AB
track becomes another machine (standalone AB 0.1.5 semantics).

Preparation only. It establishes no controller generation, owned DSP job,
Part/UI retirement, package admission, audio or hardware qualification.
"""
from dataclasses import replace
from pathlib import Path
import subprocess
import sys

import machine_composition as base

AB = 'analog-bassdrum'
MEMBERS = ('vector', 'synth', AB)


def controller_source(sdk=base.SDK, include_poly=False):
    """The exact shared controller with AB as a linked participant."""
    text = base.controller_source(sdk, include_poly=include_poly)
    if include_poly:
        text = base._once(text, "if(s[0]=='A' && s[1]=='B' && s[2]==1) return AB;",
                          "if(s[0]=='A' && s[1]=='B' && s[2]==1) return part[0x22+t]==1 && present(AB)?AB:STOCK;")
    else:
        # The ordinary variant mapped AB/1 to STOCK; only that one line returns.
        text = base._once(text, "if(s[0]=='A' && s[1]=='B' && s[2]==1) return STOCK;",
                          "if(s[0]=='A' && s[1]=='B' && s[2]==1) return part[0x22+t]==1 && present(AB)?AB:STOCK;")
        text = base._once(text, 'return (kind==VECTOR && st_type) || (kind==FM && fm_type);',
                          'return (kind==AB && ab_type) || (kind==VECTOR && st_type) || (kind==FM && fm_type);')
    text = base._once(text, 'unsigned mr_assign(Part *part,unsigned track,unsigned row) {', '''/* Match standalone AB 0.1.5: restore borrowed FLEX bytes in both
 * Part copies before a signed AB track becomes a stock/sample machine. */
static void mr_restore_ab_flex(Part *part,Part *mirror,unsigned track) {
 const Part *stock=(const Part *)0x400d320cu;
 for(unsigned k=0;k<12;++k) {
  unsigned at=(k<6?0x2a:0x1da)+30*track+6+k%6;
  uint8_t value=stock[k];part[at]=value;mirror[at]=value;
 }
}
unsigned mr_assign(Part *part,unsigned track,unsigned row) {''')
    text = base._once(text, 'if(next==POLY) return pm_assign(part,track,1); /* Admission precedes every mutation. */', '''if(next==POLY) {
  unsigned result=pm_assign(part,track,1); /* Admission precedes every mutation. */
  if(old==AB && result!=(unsigned)-1 && owner(part,track)==POLY) {
   mr_restore_ab_flex(part,mirror,track);
   /* Retain POLY's no-TSTR and new-assignment LOOP policy after restoring
    * AB's borrowed bytes. A refused admission never reaches these stores. */
   for(unsigned pool=0;pool<2;++pool)
    part[0x1da+30*track+6*pool+4]=mirror[0x1da+30*track+6*pool+4]=0;
   part[0x1da+30*track+6]=mirror[0x1da+30*track+6]=0;
  }
  return result;
 }''')
    text = base._once(text, 'if(next==VECTOR) return st_assign(part,track,1);', '''if(next==VECTOR) {
  unsigned result=st_assign(part,track,1);
  if(old==AB && owner(part,track)==VECTOR) mr_restore_ab_flex(part,mirror,track);
  return result;
 }''')
    return base._once(text, 'else if(old && present(old)) {\n  unsigned sig=SIG+30*track;', '''else if(old && present(old)) {
  if(old==AB) mr_restore_ab_flex(part,mirror,track);
  unsigned sig=SIG+30*track;''')


def _compile(source, text, compiled, asm, hooks, cross):
    source.write_text(text)
    subprocess.run([cross + 'gcc', *base.FLAGS, '-S', str(source), '-o', str(compiled)], check=True, capture_output=True)
    asm.write_text(compiled.read_text() + '\n#APP\n' + hooks)


def effective_modules(selected, sdk_root=None, work=None, cross='m68k-elf-'):
    """AB plus any POLY/VECTOR/FM subset (mask 0 is AB alone with the bridge).

    One common site owner; AB keeps its own CF units, with only its descriptor
    writes removed (analog_bd_runtime.port). `work` must outlive assembly.
    """
    selected = list(selected)
    names = {m.name for m in selected}
    if AB not in names:
        raise ValueError('Private Analog BD preparation requires its explicit participant.')
    if work is None:
        raise ValueError('Runtime machine composition needs a private source work directory.')
    sdk = Path(sdk_root or base.SDK).resolve()
    sys.path.insert(0, str(sdk / 'tools'))
    import importlib
    policy = importlib.import_module('remix.machine_composition')
    from remix.stock_guard import stock_guard
    from remix.schema import Linked, StockCopy
    from analog_bd_runtime import port as ab_port
    from vector_runtime import port as vector_port
    base._read(sdk, 'modules/poly8/manifest.py')
    base._read(sdk, 'modules/poly8/composition.json')
    folder = Path(work).resolve();folder.mkdir(parents=True, exist_ok=True)
    names_copy = StockCopy('mr_src_names', stock_guard(0x400a78c8, 20,
                           '96966986164a24f9ca5be84cca807a016a828da2bcc3167b831be52acad2a9a7'))
    if 'poly8' in names:
        _compile(folder / 'shared-runtime-controller.c', controller_source(sdk, include_poly=True),
                 folder / 'shared-runtime-controller.s', folder / 'shared-runtime-bridge.s',
                 base.hook_source(sdk, include_poly=True), cross)
        result = []
        for module in policy.effective_modules(selected):
            if module.name == 'poly8':
                module = replace(module, linked=tuple(replace(u, source=str(folder / 'shared-runtime-bridge.s'),
                                                              stock_copies=u.stock_copies + (names_copy,))
                                                      if u.label == 'machine_registry' else u for u in module.linked))
            if module.name == 'vector':
                module = vector_port(module, sdk, folder / 'vector')
            if module.name == AB:
                module = ab_port(module, sdk, folder / 'analog-bd', cross=cross)
            result.append(module)
        return result
    from remix import registry
    template = registry._load_one(sdk / 'modules/poly8/manifest.py')
    bundled_quantizer = 'synth' in names and 'quantizer' in names
    composed = policy.effective_modules([template, *[m for m in selected if m.name in MEMBERS or
                                                    (bundled_quantizer and m.name == 'quantizer')]])
    participants = [m for m in composed if m.name != 'poly8']
    if 'synth' in names:
        original_fm = next(m for m in selected if m.name == 'synth')
        octave = tuple(d for d in original_fm.detours if d.site == 0x400449be)
        if len(octave) != 1:
            raise ValueError('FM octave-number declaration changed.')
        participants = [replace(m, detours=m.detours + octave) if m.name == 'synth' else m for m in participants]
    participants += [m for m in selected if m.name not in MEMBERS and
                     not (bundled_quantizer and m.name == 'quantizer')]
    asm = folder / 'vector-fm-bridge.s'
    _compile(folder / 'vector-fm-controller.c', controller_source(sdk), folder / 'vector-fm-controller.s',
             asm, base.hook_source(sdk), cross)
    copies = {c.symbol: c.span for u in template.linked for c in u.stock_copies}
    stock_copies = tuple(StockCopy('bridge_' + name + '_replay', copies['pm_' + name + '_replay']) for name in ('main', 'edit', 'draw'))
    stock_copies += (StockCopy('bridge_stock_pool_open', next(d.expect for d in template.detours if d.symbol == 'mr_pool_open')),
                     names_copy)
    count = 5 + len(names.intersection(MEMBERS))
    bridge = replace(template, name='machine-bridge', key='RUNTIME_MACHINE_BRIDGE',
                     doc='Internal AB/VECTOR/FM chooser and private parameter-page owner; no POLY engine or member.',
                     linked=(Linked('machine_registry', str(asm), cpu='5475', dram=True, stock_copies=stock_copies),),
                     detours=tuple(d for d in template.detours if d.unit == 'machine_registry' and d.symbol in base.COMMON),
                     symbol_refs=tuple(r for r in template.symbol_refs if r.symbol in ('mr_pb_table', 'mr_source_render', 'mr_choice_left', 'mr_pool_left', 'mr_pool_right')),
                     pokes=tuple(replace(p, write=p.write[:-1] + bytes([count if len(p.write) == 4 else count - 1]))
                                 for p in template.pokes if p.addr in policy.POLICY['countSites']))
    participants = [vector_port(m, sdk, folder / 'vector') if m.name == 'vector' else
                    ab_port(m, sdk, folder / 'analog-bd', cross=cross) if m.name == AB else m for m in participants]
    return [bridge, *participants]
