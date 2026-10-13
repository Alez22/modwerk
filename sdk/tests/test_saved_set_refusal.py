# SPDX-License-Identifier: GPL-3.0-or-later
"""Execute the actual generated refusal gates, not a second gate model."""
import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
ELEK = ROOT / 'sdk/machines/octatrack/elekloader'
GLUE = ROOT / 'sdk/machines/octatrack/module-adapters/saved-set-export'
spec = importlib.util.spec_from_file_location('refusal_wiring', GLUE / 'saved_set_wiring.py')
wiring = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wiring)

def body(text, signature):
    start = text.index(signature)
    at = text.index('{', start)
    depth = 1
    end = at + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end]

@unittest.skipUnless(shutil.which('cc'), 'Host C compiler unavailable')
class SavedSetRefusal(unittest.TestCase):
    def run_c(self, source, defines=()):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            fixture = work / 'fixture.c'
            fixture.write_text(source)
            executable = work / 'refusal'
            command = ['cc', '-std=c11', '-Wall', '-Wextra', '-Werror', '-pedantic',
                       *defines, '-I'+str(GLUE), '-I'+str(ROOT/'sdk/runtime/upload'),
                       '-I'+str(ROOT/'sdk/runtime/loader'),
                       '-DRUNTIME_POOL_BYTES=4096', str(fixture),
                       str(GLUE/'saved_set_refusal.c'), str(GLUE/'saved_set_session.c'),
                       str(GLUE/'saved_set_export.c'), '-o', str(executable)]
            compiled = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(compiled.returncode, 0, compiled.stderr)
            executed = subprocess.run([str(executable)], capture_output=True, text=True)
            self.assertEqual(executed.returncode, 0, executed.stderr)

    def test_cached_wire_is_readonly_origin_specific_and_never_reuses_sequence(self):
        self.run_c('''#include <assert.h>
#include <string.h>
#include "saved_set_refusal.h"
static unsigned word(const uint8_t *p) { return (unsigned)p[0]<<24|(unsigned)p[1]<<16|(unsigned)p[2]<<8|p[3]; }
int main(void) {
    struct msxr_cache s={0}, before; uint8_t out[24], repeated[24];
    assert(msxr_read(&s,out)==24 && !memcmp(out,"MWXR",4));
    assert(out[4]==1 && out[5]==24);
    for(unsigned i=6;i<24;++i) assert(!out[i]);
    msxr_capture(&s,MSXR_BEGIN,123,MSXR_TRANSFER|MSXR_OWNED,65534,2);
    before=s; assert(msxr_read(&s,out)==24); assert(msxr_read(&s,repeated)==24);
    assert(!memcmp(out,repeated,24) && !memcmp(&s,&before,sizeof s));
    assert(out[6]==MSXR_BEGIN && word(out+8)==123 && word(out+12)==(MSXR_TRANSFER|MSXR_OWNED));
    assert(out[16]==255 && out[17]==254 && out[18]==2 && word(out+20)==1);
    assert(!out[7] && !out[19]);
    msxr_capture(&s,MSXR_ENGINE_READ,124,MSXR_LOGGER,65534,1);
    assert(msxr_read(&s,out)==24 && out[6]==MSXR_ENGINE_READ && word(out+20)==2);
    before=s; msxr_capture(&s,3,999,0,1,0); assert(!memcmp(&s,&before,sizeof s));
    msxr_capture(&s,MSXR_BEGIN,999,0,65536,0); assert(!memcmp(&s,&before,sizeof s));
    msxr_capture(&s,MSXR_BEGIN,999,0,1,7); assert(!memcmp(&s,&before,sizeof s));
    s.sequence=0xfffffffeu; msxr_capture(&s,MSXR_BEGIN,125,0,1,0);
    assert(s.sequence==0xffffffffu); before=s;
    msxr_capture(&s,MSXR_ENGINE_READ,999,MSXR_LOGGER,2,1);
    assert(!memcmp(&s,&before,sizeof s));
    return 0;
}
''')

    def test_actual_dsp_factors_equal_original_conjunction(self):
        original = wiring.dsp((ELEK/'dsp.c').read_text())
        changed = wiring.dsp((ELEK/'dsp.c').read_text(), True)
        old = body(original, 'int modwerk_dsp_export_idle(void)').replace('modwerk_dsp_export_idle','original_idle')
        new = body(changed, 'uint32_t modwerk_dsp_export_refusal(void)')
        self.run_c('''#include <assert.h>
#include "saved_set_refusal.h"
static int publication=1, transfer=1, selection=1;
static unsigned dl_phase,dl_c1_phase,rebinding,moving_count,nudge,modwerk_dsp_compact_step,picks_in,picks_out;
static int probing=-1,peeking=-1,meter_wanted=-1,xwatch_wanted=-1;
#define SELFTEST_RUNNING 1u
static struct { unsigned state; } modwerk_selftest;
int dl_publication_idle(void) { return publication; }
int dl_transfer_export_idle(void) { return transfer; }
int dl_selection_export_idle(void) { return selection; }
''' + old + '\n' + new + '''
int main(void) {
    assert(original_idle() && !modwerk_dsp_export_refusal());
    unsigned *jobs[]={&dl_phase,&dl_c1_phase,&rebinding,&moving_count,&nudge,&modwerk_selftest.state,&modwerk_dsp_compact_step,&picks_in};
    const unsigned bits[]={MSXR_PUBLICATION,MSXR_PUBLICATION,MSXR_REBINDING,MSXR_MOVING,MSXR_NUDGE,MSXR_SELFTEST,MSXR_COMPACTION,MSXR_PICKS};
    for(unsigned i=0;i<8;++i) {
        *jobs[i]=1; assert(!original_idle() && modwerk_dsp_export_refusal()==bits[i]); *jobs[i]=0;
    }
    int *work[]={&publication,&transfer,&selection,&probing,&peeking,&meter_wanted,&xwatch_wanted};
    const unsigned factors[]={MSXR_PUBLICATION,MSXR_TRANSFER,MSXR_SELECTION,MSXR_DIAGNOSTIC,MSXR_DIAGNOSTIC,MSXR_DIAGNOSTIC,MSXR_DIAGNOSTIC};
    for(unsigned i=0;i<7;++i) {
        int saved=*work[i]; *work[i]=0;
        assert(!original_idle() && modwerk_dsp_export_refusal()==factors[i]); *work[i]=saved;
    }
    for(unsigned mask=0;mask<256;++mask) {
        for(unsigned i=0;i<8;++i) *jobs[i]=(mask>>i)&1u;
        unsigned expected=0; for(unsigned i=0;i<8;++i) if(*jobs[i]) expected|=bits[i];
        assert(modwerk_dsp_export_refusal()==expected);
        assert((modwerk_dsp_export_refusal()==0)==original_idle());
    }
    return 0;
}
''', ('-DMODWERK_DSP_XWATCH',))

    def test_actual_board_begin_and_reader_have_distinct_valid_factors(self):
        text=(ELEK/'ep0.c').read_text()
        selected='\n'.join(body(text, signature) for signature in (
            'static uint32_t saved_set_structural_refusal(void)',
            'static uint32_t saved_set_begin_refusal(const struct mv_transport *t)',
            'static int saved_set_structural_safe(void)', 'int modwerk_saved_set_safe(void)'))
        selected=selected.replace('REG(0x460d1cb8u)', 'transport_state').replace('REG(0x460e76a0u)', 'recording')
        self.run_c('''#include <assert.h>
#include <string.h>
#include "saved_set_refusal.h"
#include "saved_set_session.h"
#define MU_NORMAL 0
static struct msx_session session;
#define SAVED_SET (&session)
static struct msxr_cache cache;
#define EXPORT_REFUSAL (&cache)
static unsigned receiving,held,controller_started,wake_posted,transport_state=1,recording;
static struct { unsigned phase; } controller;
struct mv_transport { unsigned resets,handled,lapses,lapses_handled; };
static unsigned dsp_mask;
static int modset_idle=1, stopped=1, hooks_idle=1, logger_safe=1, locked;
uint32_t modwerk_dsp_export_refusal(void) { return dsp_mask; }
int modwerk_dsp_export_idle(void) { return !dsp_mask; }
int modwerk_modset_export_idle(void) { return modset_idle; }
int modwerk_machine_stopped(void) { return stopped; }
int modwerk_stock_hook_export_idle(void) { return hooks_idle; }
int octamod_log_can_flush(void) { assert(locked); return logger_safe; }
uint32_t modwerk_machine_lock(void) { assert(!locked); locked=1; return 77; }
void modwerk_machine_unlock(uint32_t v) { assert(locked && v==77); locked=0; }
uint32_t modwerk_runtime_calls(void) { assert(locked); return 123; }
''' + selected + '''
static int request(const struct mv_transport *t) {
    const uint8_t setup[8]={0xc1,31,1,0,1,0,80,0}; uint8_t out[480];
    unsigned mask=saved_set_begin_refusal(t);
    assert(msx_session_request(&session,setup,out,1,mask==0)==80);
    return out[5];
}
int main(void) {
    struct mv_transport t={0};
    assert(saved_set_structural_safe() && !saved_set_begin_refusal(&t));
    logger_safe=0; assert(!saved_set_begin_refusal(&t)); /* logger is not a Begin factor */
    assert(request(&t)==MSX_PENDING); session.running=1; session.running_token=session.file.token;
    assert(!modwerk_saved_set_safe() && cache.origin==MSXR_ENGINE_READ && cache.refusal==MSXR_LOGGER);
    logger_safe=1; assert(modwerk_saved_set_safe() && !cache.refusal);
    session.running=0; assert(!modwerk_saved_set_safe() && cache.refusal==MSXR_NOT_READING);
    memset(&session,0,sizeof session);
    unsigned *values[]={&receiving,&held,&controller_started,&recording,&wake_posted,&t.resets,&t.lapses};
    const unsigned bits[]={MSXR_RECEIVING,MSXR_HELD,MSXR_CONTROLLER,MSXR_RECORDING,MSXR_WAKE,MSXR_RESET,MSXR_LAPSE};
    controller.phase=1;
    for(unsigned i=0;i<7;++i) {
        *values[i]=1;
        assert(saved_set_begin_refusal(&t)==bits[i] && request(&t)==MSX_BUSY && !session.file.token);
        assert(saved_set_structural_safe()==(i>=4));
        *values[i]=0;
    }
    int *gates[]={&modset_idle,&stopped,&hooks_idle};
    const unsigned reasons[]={MSXR_MODSET,MSXR_MACHINE_RUNNING,MSXR_HOOKS};
    for(unsigned i=0;i<3;++i) {
        *gates[i]=0; assert(saved_set_begin_refusal(&t)==reasons[i] && !saved_set_structural_safe()); *gates[i]=1;
    }
    transport_state=0; assert(saved_set_begin_refusal(&t)==MSXR_TRANSPORT_RUNNING); transport_state=1;
    dsp_mask=MSXR_TRANSFER|MSXR_PICKS; assert(saved_set_begin_refusal(&t)==dsp_mask && !saved_set_structural_safe()); dsp_mask=0;
    session.file.token=65535u; assert(saved_set_begin_refusal(&t)==MSXR_TOKEN_EXHAUSTED && request(&t)==MSX_BUSY);
    session.file.token=0; session.running=1;
    assert(saved_set_begin_refusal(&t)==MSXR_OWNED && request(&t)==MSX_BUSY);
    assert(!locked);
    return 0;
}
''', ('-DMODWERK_EXPORT_REFUSALS', '-DMODWERK_RESIDENT_STOCK_HOOKS'))

if __name__ == '__main__': unittest.main()
