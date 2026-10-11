#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Qualification run for a module set on a development base, over `npm run device -- serve`.

  scripts/octatrack-qualify.py [--seconds 30] PKG.mwrm ...

Installs the set, puts each DSP module alone on T1 (core 1) and T5 (core 0) and reads the load meters, then
all of them at once while the pattern plays, logging the meters. Fails when the loader rejects a packet or
errs, a crash is recorded, a pick is refused or a core's peak passes 90 % of a frame. Puts the tracks' effects
back and removes the set. Prints one JSON summary; exit status 1 on a failure. Part and bank switching need a
QA project and come next (docs/OCTATRACK_ELEKLOADER_MIGRATION.md, the stress-test plan)."""
import argparse, json, os, re, socket, sys

SOCKET = os.environ.get('MODWERK_DEV_SOCKET', '/tmp/modwerk-dev.sock')
PEAK_LIMIT = 900  # per mille of a frame
# A package's ABI 6 header: name at 50 (15 bytes), slots at 39 (1 FX1, 2 FX2, 3 both); no DSP code below ABI 5.
def package(path):
    data = open(path, 'rb').read()
    abi = int.from_bytes(data[4:6], 'big')
    if data[:4] != b'MWRM' or abi < 6: raise SystemExit(path + ': not an ABI 6 runtime module')
    return dict(path=path, name=data[50:65].split(b'\0')[0].decode('latin1'), slots=data[39], dsp=int.from_bytes(data[32:36], 'big') > 0)


def log(*a): print(*a, file=sys.stderr, flush=True)


def send(sequence):
    log('>', sequence)
    s = socket.socket(socket.AF_UNIX)
    s.settimeout(40)  # the session answers within 20 s; never wait for ever
    s.connect(SOCKET)
    s.sendall((sequence + '\n').encode())
    reply = s.makefile().read()
    if 'error:' in reply: raise RuntimeError(sequence + ': ' + reply.strip())
    return reply


def counters():
    loader = re.search(r'rejected (\d+)/(\d+) errors (\d+) .*rollbacks (\d+)', send('loader'))
    crash = re.match(r'crash (\d+)', send('crash'))
    return dict(rejected=int(loader.group(1)) + int(loader.group(2)), errors=int(loader.group(3)), rollbacks=int(loader.group(4)),
                crashes=int(crash.group(1)) if crash else 0)


def meters(n):
    rows = [list(map(int, m.groups())) for m in
            re.finditer(r'stats cpu (\d+) T1-4 (\d+)/(\d+) T5-8 (\d+)/(\d+)', send(' '.join(['w1500 stats'] * n)))]
    return dict(cpu=max(r[0] for r in rows), core1=sum(r[1] for r in rows) // len(rows), core1_peak=max(r[2] for r in rows),
                core0=sum(r[3] for r in rows) // len(rows), core0_peak=max(r[4] for r in rows))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seconds', type=int, default=30)
    ap.add_argument('packages', nargs='+')
    args = ap.parse_args()
    pkgs = [package(p) for p in args.packages]
    failures, result = [], dict(base=None, modules=[], together=None)
    if 'stopped' not in send('state'): raise SystemExit('Stop the transport first.')
    before = counters()
    live = bytes.fromhex(send('mem:0x80000ec4:16').strip())  # what each track runs now: FX1 T1-8, then FX2
    try:
        for p in pkgs: send('try ' + p['path'])
        for p in pkgs:
            if not p['dsp']: continue
            slot = 2 if p['slots'] & 2 else 1
            entry = dict(name=p['name'], slot='FX%d' % slot)
            for track in (1, 5):
                try:
                    took = re.search(r'running (\d+) ms', send('pick:T%d:FX%d:%s' % (track, slot, p['name'].replace(' ', '_'))))
                    entry['T%d' % track] = dict(meters(1), admit_ms=int(took.group(1)))
                    log('  %s on T%d:' % (p['name'], track), entry['T%d' % track])
                except RuntimeError as e:
                    failures.append(str(e)); entry['T%d' % track] = 'refused'
                send('pick:T%d:FX%d:NONE' % (track, slot))
            result['modules'].append(entry)
        # All at once: one module a track, T1-T8, FX2 where it fits, while the pattern plays.
        placed = []
        for i, p in enumerate([p for p in pkgs if p['dsp']] * 8):
            if len(placed) == 8: break
            slot = 2 if p['slots'] & 2 else 1
            try:
                send('pick:T%d:FX%d:%s' % (len(placed) + 1, slot, p['name'].replace(' ', '_'))); placed.append((len(placed) + 1, slot, p['name']))
            except RuntimeError:
                placed.append((len(placed) + 1, slot, None))  # refused by the ledger: expected once a core is full
        send('PLAY w1000')
        together = meters(max(2, args.seconds * 2 // 3))
        send('STOP w500')
        together['placed'] = [n for _, _, n in placed]
        log('  all at once:', together)
        result['together'] = together
        for core, peak in (('core1', together['core1_peak']), ('core0', together['core0_peak'])):
            if peak > PEAK_LIMIT: failures.append('%s peaked at %d per mille with everything at once' % (core, peak))
        for track, slot, name in placed:
            if name: send('pick:T%d:FX%d:NONE' % (track, slot))
    finally:
        send('STOP w300')
        for p in pkgs:
            try: send('remove ' + p['path'])
            except RuntimeError as e: failures.append(str(e))
        # shortcut: effects are put back by name only where they were NONE before the run; restore others by hand
        changed = [i for i, v in enumerate(bytes.fromhex(send('mem:0x80000ec4:16').strip())) if v != live[i]]
        if changed: failures.append('tracks not back as before (FX index %s); restore them' % changed)
    after = counters()
    if after['crashes'] != before['crashes']: failures.append('a crash was recorded during the run')
    for key in ('rejected', 'errors'):
        if after[key] != before[key]: failures.append('the loader counted %d more %s' % (after[key] - before[key], key))
    if after['rollbacks'] != before['rollbacks']: failures.append('the loader rolled back %d transaction(s)' % (after['rollbacks'] - before['rollbacks']))
    result['failures'] = failures
    print(json.dumps(result, indent=1))
    sys.exit(1 if failures else 0)


main()
