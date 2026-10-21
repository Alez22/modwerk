#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Exact-build offline profile board/stream checks against separate native builds.

This invokes the internal board seam through an emulator C-call fixture. It
is not a host settings protocol, hardware qualification or a Keep/Undo test.
"""
import argparse
import contextlib
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import time

from runtime_private_paths import private_directory, save

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'sdk/octabam/tools/harness'))
from usb_host import Bench, descriptors, enumerate_device, msc_test  # noqa: E402

PROFILES = ('midi-only', 'tracks-main-cue', 'tracks', 'master', 'main-cue', 'main', 'tracks-post')
FRAME_BYTES = (0, 80, 64, 8, 16, 8, 64)
CONFIGS = ('modwerk_cfg_fs', 'modwerk_cfg_hs', 'modwerk_cfg_os_fs', 'modwerk_cfg_os_hs')
CODE, SNAP = 0x40f10000, 0x40f30000
LAYOUTS = (None, 'USB AUDIO OUT TRACKS MAIN CUE', 'USB AUDIO OUT TRACKS',
           'USB AUDIO OUT MASTER', 'USB AUDIO OUT MAIN CUE', 'USB AUDIO OUT MAIN',
           'USB AUDIO OUT TRACKS POST')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def references(root):
    result, identities = [], []
    for name, layout in zip(PROFILES, LAYOUTS):
        folder = root / name
        proof = json.loads((folder / 'proofs.json').read_text())
        if (digest(folder / 'MAIN.raw') != proof['manifest']['main_sha256'] or
                proof['configuration']['usb'].get('audio') != layout):
            raise ValueError('Separate native reference identity mismatch: ' + name)
        text = (folder / 'source/usb_base.s').read_text()
        row = []
        for label in CONFIGS:
            found = re.search(r'^' + label + r':\n\s*\.byte ([^\n]+)', text, re.M)
            if not found:
                raise ValueError('Expected the separate native configuration source: ' + name)
            blob = bytes(int(word.strip(), 16) for word in found[1].split(','))
            if struct.unpack_from('<H', blob, 2)[0] != len(blob):
                raise ValueError('Invalid separate native descriptor length.')
            row.append(blob)
        result.append(row)
        identities.append(dict(profile=name, base=proof['configurationHash'],
                               imageSha256=digest(folder / 'MAIN.raw'),
                               descriptorSourceSha256=digest(folder / 'source/usb_base.s')))
    return result, identities


def wrapper(symbols):
    return f'''.text
.global call_frame
call_frame:
 lea %sp@(-44),%sp
 moveml %d2-%d7/%a2-%a6,%sp@
 jsr {symbols['audio_frame_shim']:#x}
 moveml %sp@,%d2-%d7/%a2-%a6
 lea %sp@(44),%sp
 moveq #0,%d0
 rts
.org 0x100
read_word:
 movel %sp@(4),%a0
 movel %a0@,%d0
 rts
.org 0x120
read_sr:
 moveq #0,%d0
 movew %sr,%d0
 rts
.org 0x140
call_routine:
 lea %sp@(-44),%sp
 moveml %d2-%d7/%a2-%a6,%sp@
 movel %sp@(48),%a1
 jsr %a1@
 moveml %sp@,%d2-%d7/%a2-%a6
 lea %sp@(44),%sp
 rts
'''


class Session:
    def __init__(self, args, output, symbols, proof, frames, check):
        self.symbols, self.check = symbols, check
        self.sock = output.parent / ('usb-profile-' + os.urandom(4).hex() + '.sock')
        if len(os.fsencode(self.sock)) > 100:
            raise ValueError('Choose a shorter private output parent for the Unix socket.')
        self.log = (output / 'emulator.log').open('w')
        self.child = subprocess.Popen([str(args.emulator), '--image', str(args.build / 'MAIN.raw'),
            '--usb-host', str(self.sock), '--usb-hold-ms', '600000', '--mkii'] + (['--frame'] if frames else []),
            stdout=self.log, stderr=subprocess.STDOUT)
        self.bench = None
        try:
            self.bench = Bench(str(self.sock), timeout=20)
            enumerate_device(self.bench, True)
            identity = self.identity()
            check('exact base before fixture writes', identity[:4] == b'MWUI' and identity[16:48].hex() == proof['configurationHash'])
            if not frames:
                source = output / 'wrapper.s'
                save(source, wrapper(symbols).encode())
                for cmd in [['m68k-elf-as', '-mcpu=54455', '-o', output / 'wrapper.o', source],
                            ['m68k-elf-ld', '-Ttext=' + hex(CODE), '-o', output / 'wrapper.elf', output / 'wrapper.o'],
                            ['m68k-elf-objcopy', '-O', 'binary', '-j', '.text', output / 'wrapper.elf', output / 'wrapper.bin']]:
                    subprocess.run(list(map(str, cmd)), check=True, capture_output=True, timeout=30)
                self.bench.poke(CODE, (output / 'wrapper.bin').read_bytes())
                # Dormant ISR epilogue only: an authored C return for explicit off-frame calls.
                self.bench.poke(0x4000d9a6, b'\x4e\x75')
                self.bench.poke(0x80003c10, struct.pack('>I', SNAP))
                self.bench.poke(SNAP, bytes(64))
        except BaseException:
            self.close()
            raise

    def identity(self):
        return self.bench.ctrl_in(0xc1, 3, 0, 1, 72)

    def peek(self, address, count):
        return bytes.fromhex(self.bench.cmd(f'peek {address:#x} {count}', 'peek').split()[1])

    def word(self, address):
        return self.bench.call(CODE + 0x100, address) & 0xffffffff

    def close(self):
        if self.bench:
            self.bench.sock.close()
        if self.child.poll() is None:
            self.child.terminate()
        try:
            self.child.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.child.kill()
            self.child.wait()
        self.log.close()
        with contextlib.suppress(FileNotFoundError):
            self.sock.unlink()


def readiness_checks(session):
    """Exercise the real packet reader at its lag boundary and counter wrap."""
    b, s, check = session.bench, session.symbols, session.check
    def put(name, value, size=4):
        b.poke(s['p0_' + name], value.to_bytes(size, 'big'))
    def call(name):
        return b.call(CODE + 0x140, s['p0_' + name])
    b.cmd('unplug', 'ok')
    check('readiness profile stage', b.call(s['mu_audio_stage_detached'], 1) == 0)
    b.cmd('plug', 'ok')
    enumerate_device(b, True)
    b.ctrl_nodata(1, 11, 1, 5)
    b.call(CODE)  # One authored frame sets up the real EP3 queue head.
    b.ctrl_nodata(1, 11, 0, 5)
    b.call(CODE)
    for raw, consumed, high, expected in ((128, 112, True, 0), (8, 0xfffffff8, True, 0),
                                         (144, 112, True, 1), (156, 112, False, 1)):
        call('audio_ep3_down')
        for field, value, size in (('aud_produced', raw, 4), ('usbaudio_consumed', consumed, 4),
                                  ('aud_hs', int(high), 1), ('aud_step', 11025 if high else 44100, 4),
                                  ('usbaudio_alt', 1, 1), ('aud_await', 0, 1), ('aud_tail', 0, 1),
                                  ('usbaudio_acc', 0, 4), ('usbaudio_underruns', 0, 4)):
            put(field, value, size)
        result = call('audio_pkt_build')
        check('packet readiness raw=%#x consumed=%#x HS=%s' % (raw, consumed, high), result == expected)
        if not expected:
            check('not-ready packet keeps cursor', session.word(s['p0_usbaudio_consumed']) == consumed)
            check('not-ready packet records underrun', session.word(s['p0_usbaudio_underruns']) == 1)
    call('audio_ep3_down')
    put('usbaudio_alt', 0, 1)
    for index, first, last, stride in ((0, 48, 159, 80), (3, 64, 159, 16)):
        b.poke(s['p%d_aud_produced' % index], struct.pack('>I', 128))
        for slot in (first - 1, first, last, last + 1):
            b.poke(s['shared_ring'] + slot * stride, b'Z' * stride)
        b.call(CODE + 0x140, s['p%d_audio_cushion_zero' % index])
        for slot in (first, last):
            check('fresh-start boundary cleared profile=%d slot=%d' % (index + 1, slot),
                  session.peek(s['shared_ring'] + slot * stride, stride) == bytes(stride))
        for slot in (first - 1, last + 1):
            check('fresh-start clear bounded profile=%d slot=%d' % (index + 1, slot),
                  session.peek(s['shared_ring'] + slot * stride, stride) == b'Z' * stride)


def run(args):
    symbols = json.loads((args.build / 'symbols.json').read_text())
    proof = json.loads((args.build / 'proofs.json').read_text())
    if digest(args.build / 'MAIN.raw') != proof['manifest']['main_sha256']:
        raise ValueError('The base image does not match its native proof.')
    mode = proof.get('configuration', {}).get('usb', {}).get('profiles')
    if mode != dict(schema=1, initial=6, stagingOnly=True, hostSettings=False):
        raise ValueError('Use an opt-in all-profile source build with explicit initial TRACKS POST.')
    if any(CODE <= value < SNAP + 64 for value in symbols.values() if type(value) is int):
        raise ValueError('The authored fixture scratch overlaps a linked symbol.')
    expected, refs = references(args.reference_builds)
    if args.output.exists():
        raise ValueError('Choose a new private output directory.')
    output = private_directory(args.output)
    checks, cases = [], []
    receipt = dict(kind='octatrack-usb-profile-source-probe', hardware=False,
        base=proof['configurationHash'], imageSha256=digest(args.build / 'MAIN.raw'),
        symbolsSha256=digest(args.build / 'symbols.json'), emulatorSha256=digest(args.emulator),
        referenceBuilds=refs, checks=checks, streamCases=cases,
        limitations=['Internal detached board seam, not host settings/authorization/reconnect recovery or lifecycle.',
            'No real DSP/project, cache/DMA, host class drivers, audio quality or hardware timing.',
            'Frame-free fixture patches only the dormant ISR epilogue with a C return. Streaming phase has no code patches.'])
    def check(name, condition):
        checks.append(dict(check=name, passed=bool(condition)))
        if not condition:
            raise AssertionError(name)
    session = None
    try:
        for frames in (False, True):
            folder = private_directory(output / ('stream' if frames else 'board'))
            session = Session(args, folder, symbols, proof, frames, check)
            b = session.bench
            if not frames:
                check('running controller refuses mutation', b.call(symbols['mu_audio_stage_detached'], 0) == 2)
                check('connected refusal preserves initial profile', session.word(symbols['mu_audio_profile']) == 6)
                for invalid in (7, 0xffffffff):
                    check('invalid profile refused', b.call(symbols['mu_audio_stage_detached'], invalid) == 1)
            for high in (True, False):
                for profile, name in enumerate(PROFILES):
                    b.cmd('unplug', 'ok')
                    saved = {}
                    if not frames:
                        check('controller stopped', session.word(0xfc0b0140) & 1 == 0)
                        b.poke(symbols['p3_usbaudio_alt'], b'\1')
                        check('pending stream request refuses stage', b.call(symbols['mu_audio_stage_detached'], profile) == 3)
                        b.poke(symbols['p3_usbaudio_alt'], b'\0')
                        saved = {field: session.peek(symbols['p5_' + field], count) for field, count in
                                 [('post_hidx', 4), ('post_hist', 256), ('post_state', 96), ('post_gtab', 512), ('post_emac', 12)]}
                        for address in (symbols['shared_ring'], symbols['shared_ring'] + 81920 - 64, symbols['shared_sum']):
                            b.poke(address, b'Z' * 64)
                        sr = b.call(CODE + 0x120)
                    else:
                        for address, size in ((symbols['shared_ring'], 81920), (symbols['shared_sum'], 8192)):
                            for offset in range(0, size, 1024):
                                b.poke(address + offset, b'Z' * min(1024, size - offset))
                    attempts = []
                    for _ in range(30):
                        result = b.call(symbols['mu_audio_stage_detached'], profile)
                        attempts.append(result)
                        if result != 3 or not frames:
                            break
                        time.sleep(.01)
                    check('detached profile stage accepted', result == 0)
                    if not frames:
                        check('IRQ mask restored', b.call(CODE + 0x120) & 0x2700 == sr & 0x2700)
                        check('profile committed', session.word(symbols['mu_audio_profile']) == profile)
                        check('clamp committed', session.word(symbols['mu_audio_config_length']) == len(expected[profile][0]))
                        for field, value in saved.items():
                            check('POST ' + field + ' preserved', session.peek(symbols['p5_' + field], len(value)) == value)
                        check('no bulk ring clearing', all(session.peek(address, 64) == b'Z' * 64 for address in
                              (symbols['shared_ring'], symbols['shared_ring'] + 81920 - 64, symbols['shared_sum'])))
                        for index, label in enumerate(CONFIGS):
                            address = symbols['mu_cfg_templates'] + profile * 2048 + index * 512
                            table = session.peek(address, 512)
                            check('immutable ' + label + ' matches native', table[:len(expected[profile][index])] == expected[profile][index])
                            check('unused template tail zero', not any(table[len(expected[profile][index]):]))
                            check('template stays in one page', address // 4096 == (address + 511) // 4096)
                    b.cmd('plug', 'ok')
                    _, config = enumerate_device(b, high)
                    check('enumerated descriptor matches native', config == expected[profile][int(high)])
                    check('base identity unchanged', session.identity()[16:48].hex() == proof['configurationHash'])
                    b.call(0x400108b0, 0xf8)
                    check('fresh MIDI clock', b.ep_in(2, 64) == bytes([15, 248, 0, 0]))
                    if not frames:
                        check('active descriptor length clamp', len(b.ctrl_in(0x80, 6, 0x0200, 0, 1024)) == len(config))
                        check('opposite-speed descriptor', b.ctrl_in(0x80, 6, 0x0700, 0, 1024) == expected[profile][2 + int(not high)])
                        check('storage INQUIRY', msc_test(b))
                        check('connected mutation still refused', b.call(symbols['mu_audio_stage_detached'], (profile + 1) % 7) == 2)
                        if profile:
                            check('closed alt0', b.ctrl_in(0x81, 10, 0, 5, 1) == b'\0')
                        else:
                            before = session.word(symbols['p5_post_hidx'])
                            check('off frame keeps POST history', b.call(CODE) == 0 and session.word(symbols['p5_post_hidx']) == (before + 1) % 4)
                    elif profile:
                        row = dict(profile=name, highSpeed=high, stageAttempts=attempts, packetLengths=[])
                        cases.append(row)
                        b.iso_hz(4000 if high else 1000)
                        b.ctrl_nodata(1, 11, 1, 5)
                        check('stream alt1', b.ctrl_in(0x81, 10, 0, 5, 1) == b'\1')
                        nonempty = 0
                        for _ in range(64):
                            packet = b.ep_in(3, 1024)
                            row['packetLengths'].append(len(packet))
                            if not packet:
                                continue
                            geometry = FRAME_BYTES[profile] if high else 8
                            check('prior ring sentinel excluded', b'Z' * 16 not in packet)
                            check('selected packet geometry', len(packet) % geometry == 0 and len(packet) // geometry in ((10, 11, 12) if high else (43, 44, 45)))
                            nonempty += 1
                            if nonempty == 16:
                                break
                        check('sixteen nonempty packets', nonempty == 16)
                        b.ctrl_nodata(1, 11, 0, 5)
                        check('stream alt0', b.ctrl_in(0x81, 10, 0, 5, 1) == b'\0')
                    if not profile:
                        check('off has no AudioStreaming or EP3', config[4] == 4 and not any(
                            (kind == 4 and data[5:8] == bytes([1, 2, 32])) or (kind == 5 and data[2] == 0x83)
                            for kind, data in descriptors(config)))
            if not frames:
                readiness_checks(session)
            session.close()
            session = None
        receipt['passed'] = True
    except Exception as error:
        receipt['error'] = str(error)
        raise
    finally:
        if session:
            session.close()
        save(output / 'receipt.json', receipt)
    print(json.dumps(dict(passed=True, checks=len(checks), audioStreamCases=len(cases), hardware=False)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('build', 'emulator', 'reference-builds', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    run(parser.parse_args())
