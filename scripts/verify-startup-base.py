#!/usr/bin/env python3
"""Explicit private check of the base's startup (sdk/runtime/startup/base.json); never part of npm check.

Boots a composed MAIN image in the headless emulator with the boot logo on, records the panel stream
(LCD blocks, LED levels) while it plays and checks, for MKI and MKII:
  * the last logo frame equals the authored pixels exactly (mark, wordmark, NEW, version);
  * every LED level inside the logo window equals what the firmware's own boot formula gives for the
    authored lamp table at the recovered loop time (the time step patch took effect);
  * the unit hands over to the normal screen afterwards.
Firmware, images and captures stay private; only --gif / --png (authored boot graphics) and --record
(hashes and results) write anything, and only where you point them.

  verify-startup-base.py --image MAIN.raw --version 0.3.1 --emulator ot_emu [--docker-image IMAGE]
                         [--gif OUT.gif] [--png OUT.png] [--record OUT.json]

--emulator is the Linux ot_emu; with --docker-image it runs in that image (Docker Desktop must be up).
"""
import argparse, hashlib, importlib.util, json, struct, subprocess, sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('startup_build', ROOT / 'sdk/runtime/startup/build.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)
FRAME = {**{o: 10 for o in range(0x10, 0x18)}, **{o: 2 for o in [*range(0x20, 0x40), *range(0xa0, 0xb0)]},
         **{o: 1 for o in range(0x40, 0x50)}, 0x60: 2, 0x70: 2, 0x74: 2, 0xb5: 6, 0xb7: 2}  # tools/panel/panel_link.py


def capture(args, mkii, step=5.0, total=3300.0):
    image = Path(args.image).resolve()
    emu = Path(args.emulator).resolve()
    tail = ['--image', f'/b/{image.name}' if args.docker_image else str(image), '--boot-logo', '--ms', '50', '--main-level', 'off',
            '--interactive', '--rtc', 'off'] + (['--mkii'] if mkii else [])
    cmd = (['docker', 'run', '-i', '--rm', '--shm-size=128m', '-v', f'{emu.parent}:/e:ro', '-v', f'{image.parent}:/b:ro', args.docker_image,
            f'/e/{emu.name}'] if args.docker_image else [str(emu)]) + tail
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1)
    ask = lambda text: (p.stdin.write(text + '\n'), p.stdin.flush(), p.stdout.readline().strip())[2]
    line = ''
    for _ in range(200):   # the banner comes first
        line = p.stdout.readline()
        if line.startswith('ready') or not line:
            break
    if not line.startswith('ready'):
        raise RuntimeError('The emulator did not become ready.')
    plane, frames, led, buf, t = bytearray(1024), [], [], bytearray(), 0.0
    while t < total:
        ask(f'run {step}')
        t += step
        reply = ask('tx')
        buf += bytes.fromhex(reply.split(' ', 1)[1]) if ' ' in reply else b''
        dirty = False
        while buf and len(buf) >= FRAME.get(buf[0], 1):
            m = bytes(buf[:FRAME.get(buf[0], 1)]); del buf[:len(m)]
            if 0x10 <= m[0] < 0x18 and m[1] % 8 == 0 and m[1] < 128:
                plane[(m[0] & 7) * 128 + m[1]:(m[0] & 7) * 128 + m[1] + 8] = m[2:10]; dirty = True
            elif 0x30 <= m[0] < 0x40:
                led.append((t, m[1], m[0] & 15))
        if dirty:
            frames.append((t, bytes(plane)))
    ask('quit'); p.wait(timeout=30)
    return frames, led


def lcd(plane):
    im = Image.new('1', (128, 64), 0)
    for page in range(8):
        for col in range(128):
            for bit in range(8):
                if plane[page * 128 + col] >> bit & 1:
                    im.putpixel((col, 8 * (7 - page) + bit), 1)
    return im


def authored_pixels(version):
    art, edition = json.loads(build.ARTWORK.read_text()), json.loads(build.EDITION.read_text())
    return build.authored_ink(art, edition['layout']['dy']) | build.text_points(edition, version)[1]


def led_check(led, table):
    """Group the level stream into loop iterations (lamps are walked in ascending order) and, for each
    inside the logo window, find the loop time step s that explains every level it set."""
    rs = lambda v: (v + (1023 if v < 0 else 0)) >> 10
    phases = [((struct.unpack_from('>ii', table, 8 * i)), i) for i in range(len(table) // 8)]
    waves = {}
    for (x, y), i in phases:
        waves[2 * i], waves[2 * i + 1] = rs(y - x - 8200), rs(x + y - 25800)
    groups, last = [], None
    for t, i, level in led:
        if last is None or i // 2 < last:
            groups.append([])
        groups[-1].append((t, i, level)); last = i // 2
    state, fits, wrong = {}, [], 0
    for g in groups:
        for _, i, level in g:
            state[i] = level
        t = g[0][0]
        if not 200 < t < 2900:
            continue
        best = min(range(-120, 260), key=lambda s: sum(state[i] != max(0, 15 - abs(w + s)) for i, w in waves.items() if i in state))
        miss = sum(state[i] != max(0, 15 - abs(w + best)) for i, w in waves.items() if i in state)
        wrong += miss > 0
        fits.append((t, best))
    t0 = sorted(t - 5 * (192 + 2 * s) for t, s in fits)[len(fits) // 2]   # capture time of the loop's time zero
    return len(fits), wrong, t0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--image', required=True); ap.add_argument('--version', required=True); ap.add_argument('--emulator', required=True)
    ap.add_argument('--docker-image'); ap.add_argument('--gif'); ap.add_argument('--png'); ap.add_argument('--record')
    args = ap.parse_args()
    expected, edition = authored_pixels(args.version), json.loads(build.EDITION.read_text())
    results = {}
    for model, mkii in (('MKI', False), ('MKII', True)):
        frames, led = capture(args, mkii)
        window = [f for f in frames if f[0] <= 2700]
        final = lcd(window[-1][1]).load()
        got = {(x, y) for y in range(64) for x in range(128) if final[x, y]}
        n, wrong, t0 = led_check(led, build.lamp_table(edition['led']['mkii' if mkii else 'mki']))
        after = lcd(frames[-1][1]).tobytes() != lcd(window[-1][1]).tobytes() and frames[-1][0] > 2800
        results[model] = dict(finalFramePixels=len(got), missing=len(expected - got), extra=len(got - expected),
                              ledIterationsChecked=n, ledIterationsUnexplained=wrong, handsOverToUi=after, loopTimeZeroCaptureMs=t0)
        print(model, results[model])
        assert not (expected ^ got) and wrong == 0 and after, model + ' failed'
        if mkii and (args.gif or args.png):
            logo = [lcd(next(p for tt, p in reversed(frames) if tt <= t0 + 40 * k)) for k in range(70)]
            scale = lambda im: im.convert('P').resize((768, 384), Image.NEAREST)
            if args.gif:
                scale(logo[0]).save(args.gif, save_all=True, append_images=[scale(im) for im in logo[1:]], duration=[160] + [40] * 68 + [840], loop=0)
            if args.png:
                scale(lcd(window[-1][1])).save(args.png)
    if args.record:
        sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
        Path(args.record).write_text(json.dumps(dict(
            kind='modwerk-base-startup-emulator', version=args.version, imageSha256=sha(args.image), emulatorSha256=sha(args.emulator),
            captureMethod='--boot-logo --ms 50 --main-level off --interactive --rtc off (+ --mkii); run 5 ms, read the panel UART with tx',
            results=results, hardware='untested',
            sourceSha256={p: sha(ROOT / p) for p in ('sdk/runtime/startup/build.py', 'sdk/runtime/startup/base.json', 'sdk/runtime/startup/artwork.json',
                                                      'scripts/verify-startup-base.py')}), indent=1) + '\n')
    print('startup base: both models passed')


if __name__ == '__main__':
    sys.exit(main())
