#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Execute guarded private FM consumers and known UI-root collection natively.

Local files only; no USB, boot, DSP execution, admission or publication.
Requires the owner's original 1.40C, a freshly captured private FM group,
reviewed source snapshot and built verified Octabam emulator archives. Outputs
include stock-derived private images and must stay outside the checkout.
The receipt describes observed cases, not exhaustive or hardware qualification.

    python3 -B .../probe_fm_consumers.py --stock OS.bin --package FM.mwrm \\
        --capture capture.json --upstream ~/.cache/modwerk-upstream/elekloader \\
        --native ~/.cache/modwerk-upstream/octabam --out /private/tmp/fm-proof

Queue this tool behind /tmp/modwerk-check.lock like every native build.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / 'sdk/runtime/loader'))
from verify_static import unpack_recipe, placed
from machine_layout import _envelope

STOCK_SHA256 = '34695b606eb00e1b4dded5fd0c4b66f3a460522a632e47d7416dbd220599e1ad'
ARCHIVES = ('libot_machine.a', 'mc68k/lib68kEmu.a', 'dsp56300/dsp56kEmu/libdsp56kEmu.a',
            'dsp56300/dsp56kBase/libdsp56kBase.a', 'dsp56300/asmjit/libasmjit.a')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def command(argv):
    result = subprocess.run(list(map(str, argv)), capture_output=True, text=True)
    if result.returncode:
        raise ValueError('Native preparation failed: ' + result.stderr[-2000:])
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for name in ('stock', 'package', 'capture', 'upstream', 'native', 'out'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--source-root', type=Path, default=ROOT)
    args = parser.parse_args()
    root, out = args.source_root.resolve(), args.out.resolve()
    if out.is_relative_to(root) or out.is_relative_to(ROOT):
        raise ValueError('Stock-derived outputs must stay outside the source checkout.')
    stock_file = args.stock.read_bytes()
    if sha(stock_file) != STOCK_SHA256:
        raise ValueError('This consumer proof requires the exact reviewed original 1.40C.')
    sys.path.insert(0, str(args.upstream.expanduser().resolve()))
    from elekloader import formats
    parsed, device, _ = formats.load(str(args.stock))
    if device.main_load != 0x40000400:
        raise ValueError('Unexpected stock image mapping.')
    original = formats.main_image(parsed, device)
    package = args.package.read_bytes()
    image, members, _, _ = _envelope(package)
    if not members & 4:
        raise ValueError('The private group does not include FM.')
    captured = args.capture.read_bytes()
    capture = json.loads(captured)
    if capture.get('schema') != 1 or capture.get('imageSha256') != sha(image) or not capture.get('sources'):
        raise ValueError('Private package/capture association changed.')
    for path, digest in capture['sources'].items():
        target = (root / path).resolve()
        if not target.is_relative_to(root) or sha(target.read_bytes()) != digest:
            raise ValueError('Reviewed source changed: ' + path)
    image, relocs, sites, copies, fills = unpack_recipe(package)
    native = args.native.expanduser().resolve()
    archives = [native / 'out/emu' / path for path in ARCHIVES]
    if not all(path.is_file() for path in archives) or not all(shutil.which(tool) for tool in
            ('c++', 'm68k-elf-gcc', 'm68k-elf-ld', 'm68k-elf-nm', 'm68k-elf-objcopy')):
        raise ValueError('ColdFire tools and built native emulator archives are required.')
    out.mkdir(parents=True, exist_ok=True)
    (out / 'symbols.txt').write_text(''.join(f'{name} {offset}\n' for name, offset in capture['symbols'].items()))
    adapter = root / 'sdk/machines/octatrack/module-adapters'
    flags = ['-mcpu=5475', '-msoft-float', '-O2', '-ffreestanding', '-fno-builtin', '-fno-jump-tables',
             '-fno-asynchronous-unwind-tables', '-ffunction-sections', '-fdata-sections', '-Wall', '-Wextra', '-Werror']
    for source in (HERE / 'fm_consumer_scanner.c', adapter / 'machine_lifetime.c'):
        command(['m68k-elf-gcc', *flags, '-I', adapter, '-c', source, '-o', out / (source.stem + '.o')])
    command(['m68k-elf-ld', '--gc-sections', '-e', 'scan', '-Ttext=0x47400000', out / 'fm_consumer_scanner.o',
             out / 'machine_lifetime.o', '-o', out / 'scanner.elf'])
    symbols = command(['m68k-elf-nm', out / 'scanner.elf'])
    if ' U ' in symbols:
        raise ValueError('The compiled collector has unresolved runtime imports.')
    scan = next(line.split()[0] for line in symbols.splitlines() if line.split()[-1] == 'scan')
    command(['m68k-elf-objcopy', '-O', 'binary', out / 'scanner.elf', out / 'scanner.bin'])
    command(['c++', '-O2', '-std=c++17', '-I' + str(native / 'tools/emu/ot_emu'), '-I' + str(native / 'vendor'),
             '-I' + str(native / 'vendor/dsp56300/source'), HERE / 'fm_consumer_fixture.cpp',
             *archives, '-lpthread', '-o', out / 'probe'])
    receipts = []
    for origin in (0x47080000, 0x47100000):
        work = out / f'{origin:08x}'
        work.mkdir(exist_ok=True)
        memory = bytearray(original)
        for address, digest, code, local, keep, checked in sites:
            offset = address - device.main_load
            if sha(original[offset:offset + checked]) != digest.hex():
                raise ValueError('Stock site guard changed: %#x' % address)
            patch = original[offset:offset + keep] + code[keep:]
            memory[offset:offset + len(patch)] = placed(patch, local, origin)
        runtime = bytearray(placed(image, relocs, origin))
        for offset, address, length, digest in copies:
            stock = original[address - device.main_load:address - device.main_load + length]
            if sha(stock) != digest.hex():
                raise ValueError('Stock copy guard changed: %#x' % address)
            runtime[offset:offset + length] = stock
        for offset, length, value in fills:
            runtime[offset:offset + length] = bytes([value]) * length
        (work / 'stock.private.raw').write_bytes(memory)
        (work / 'group.private.raw').write_bytes(runtime)
        result = subprocess.run([out / 'probe', work / 'stock.private.raw', work / 'group.private.raw',
                                 out / 'symbols.txt', f'{origin:x}', out / 'scanner.bin', scan],
                                text=True, capture_output=True)
        (work / 'probe.log').write_text(result.stdout + result.stderr)
        if result.returncode:
            raise ValueError('Consumer probe refused at %#x: %s' % (origin, result.stderr[-2000:]))
        observations = [json.loads(line) for line in result.stdout.splitlines() if line.startswith('{')]
        if len(observations) != 2 or observations[0]['escapedPointers'] or not all(observations[1].values()):
            raise ValueError('Incomplete native consumer observations.')
        receipts.append(dict(observations=observations, stockImageSha256=sha(memory), runtimeImageSha256=sha(runtime)))
    receipt = dict(schema=1, scope='FM consumers and known UI-root native observation',
                   stockSha256=sha(stock_file), stockMainSha256=sha(original),
                   packageSha256=sha(package), captureSha256=sha(captured), sources=capture['sources'],
                   probeSources={path.name: sha(path.read_bytes()) for path in
                                 (HERE / 'fm_consumer_fixture.cpp', HERE / 'fm_consumer_scanner.c',
                                  HERE / 'probe_fm_consumers.py', adapter / 'machine_lifetime.c',
                                  adapter / 'machine_lifetime.h', HERE / 'machine_layout.py',
                                  ROOT / 'sdk/runtime/loader/verify_static.py')},
                   nativeArchives={str(path.relative_to(native)): sha(path.read_bytes()) for path in archives},
                   origins=receipts, hardware=False, boot=False, dsp=False, audio=False,
                   exhaustiveConsumerCoverage=False, admission=False)
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(receipt=str(out / 'receipt.json'), origins=[item['observations'] for item in receipts])))


if __name__ == '__main__':
    main()
