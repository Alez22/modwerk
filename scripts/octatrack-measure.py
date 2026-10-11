#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""An effect's real DSP cost on a unit, over `npm run device -- serve` (a development base with the status meters).

  scripts/octatrack-measure.py [--slot 2] [--pkg MODULE.mwrm] NAME ...   (NAME as the chooser shows it; NONE first)

For each effect: picked on T1 (core 1) and T5 (core 0) of the current Part, every knob of the main page and of
SETUP swept on T1 from its minimum (0-7 one detent at a time for mode knobs, then in 8s to 127), each left at its
dearest step before the next; T5 then gets the same settings. Cycles a sample above the NONE baseline, average
(the settings the effect starts at) and dearest (mean over 8 windows at the dearest settings, and the peak frame
seen anywhere). Run on a Part whose working copy equals its saved one, and RELOAD it after (docs/OCTATRACK_DRIVING.md).
Prints one JSON object a line; progress on stderr."""
import argparse, json, os, re, socket, sys

SOCKET = os.environ.get('MODWERK_DEV_SOCKET', '/tmp/modwerk-dev.sock')
FRAME, SAMPLES = 72520, 16
PASS = {0: 20.00, 1: 14.48}  # cycles an idle pass (status.c idle_cycles)
STEPS = list(range(8)) + list(range(15, 128, 8))
STAT = re.compile(r'stats cpu (\d+) T1-4 (\d+)/(\d+) T5-8 (\d+)/(\d+) passes ([\d.]+) ([\d.]+)')


def send(sequence, quiet=False):
    if not quiet: print('>', sequence[:100], file=sys.stderr, flush=True)
    s = socket.socket(socket.AF_UNIX); s.settimeout(120); s.connect(SOCKET)
    s.sendall((sequence + '\n').encode())
    reply = s.makefile().read()
    if 'error:' in reply: raise RuntimeError(sequence + ': ' + reply.strip())
    return reply


def windows(n):  # each core's meter window is read in turn: settle 3 s, then a window every 1.5 s
    rows = [list(map(float, m.groups())) for m in STAT.finditer(send('w3000 ' + ' '.join(['w1500 stats'] * n), quiet=True))]
    busy = lambda r, core: FRAME - r[5 + core] * PASS[core]  # passes: core 0, then core 1
    return dict(core0=sum(busy(r, 0) for r in rows) / len(rows), core1=sum(busy(r, 1) for r in rows) / len(rows),
                peak0=max(r[4] for r in rows) / 1000 * FRAME, peak1=max(r[2] for r in rows) / 1000 * FRAME)


def sweep_knob(enc):  # one connection: the knob from its minimum through STEPS, a window a step
    seq = ['enc%s-127 enc%s-127' % (enc, enc)]
    for i, step in enumerate(STEPS):
        if i: seq.append('enc%s+%d' % (enc, step - STEPS[i - 1]))
        seq.append('w1500 stats')
    rows = [list(map(float, m.groups())) for m in STAT.finditer(send(' '.join(seq), quiet=True))]
    busy = [FRAME - r[6] * PASS[1] for r in rows]
    best = STEPS[max(range(len(rows)), key=busy.__getitem__)]
    send('enc%s-127 enc%s-127' % (enc, enc) + (' enc%s+%d' % (enc, best) if best else ''), quiet=True)
    return best, max(r[2] for r in rows) / 1000 * FRAME


def measure(name, slot, base):
    fx = 'FX%d' % slot
    send('pick:T1:%s:%s pick:T5:%s:%s' % (fx, name.replace(' ', '_'), fx, name.replace(' ', '_')))
    send('PLAY w1500')
    start = windows(4)
    best, peak1 = {}, start['peak1']
    for page, key in (('main', fx), ('setup', 'FUNC+' + fx)):
        send('T1 w300 %s w800' % key)
        for enc in 'ABCDEF':
            best[page + enc], peak = sweep_knob(enc)
            peak1 = max(peak1, peak)
        if page == 'setup': send('NO w500')
    for page, key in (('main', fx), ('setup', 'FUNC+' + fx)):
        send('T5 w300 %s w800 ' % key + ' '.join('enc%s-127 enc%s-127' % (e, e) + (' enc%s+%d' % (e, best[page + e]) if best[page + e] else '') for e in 'ABCDEF'))
        if page == 'setup': send('NO w500')
    dear = windows(8)
    send('STOP w500')
    send('pick:T1:%s:NONE pick:T5:%s:NONE' % (fx, fx))
    per = lambda busy, core: round((busy - base['core%d' % core]) / SAMPLES, 1)
    return dict(name=name, slot=fx, average=dict(core1=per(start['core1'], 1), core0=per(start['core0'], 0)),
                dearest=dict(core1=per(dear['core1'], 1), core0=per(dear['core0'], 0)),
                peakFrame=dict(core1=per(max(peak1, dear['peak1']), 1), core0=per(dear['peak0'], 0)), settings=best)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--slot', type=int, default=2, choices=(1, 2))
    ap.add_argument('--pkg', action='append', default=[], help='install these first, remove them after')
    ap.add_argument('names', nargs='+')
    a = ap.parse_args()
    if 'stopped' not in send('state'): raise SystemExit('Stop the transport first.')
    for p in a.pkg: send('try ' + p)
    try:
        fx = 'FX%d' % a.slot
        send('pick:T1:%s:NONE pick:T5:%s:NONE PLAY w1500' % (fx, fx))
        base = windows(6)
        send('STOP w500')
        print(json.dumps(dict(name='NONE', slot=fx, baseline=dict(core1=round(base['core1'] / SAMPLES, 1), core0=round(base['core0'] / SAMPLES, 1)))), flush=True)
        for name in a.names:
            if name == 'NONE': continue
            try: print(json.dumps(measure(name, a.slot, base)), flush=True)
            except RuntimeError as e:
                print(json.dumps(dict(name=name, error=str(e)[:200])), flush=True)
                send('STOP w300 pick:T1:%s:NONE pick:T5:%s:NONE' % (fx, fx))
    finally:
        for p in a.pkg:
            try: send('remove ' + p)
            except RuntimeError as e: print('remove failed: %s' % e, file=sys.stderr)


main()
