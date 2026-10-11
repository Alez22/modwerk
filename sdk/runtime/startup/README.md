# Modwerk startup animation

Original monochrome artwork for the Octatrack's 128×64 LCD: an open rounded
frame that traces clockwise, eight tiles that lock in from the center around
the ring, a detached ninth tile with a short comet tail, and a geometric
MODWERK wordmark. The mark adapts `public/modwerk-mark.svg`; the lettering is
original pixel artwork, with the stock title's scale and line weight.

The stock particle convergence, horizontal title reveal, 2.8-second timer and
MKI/MKII LED choreography remain in place. No stock image, bitmap, instruction
bytes or LED tables are included here. `artwork.json` contains only authored
pixel rows, layout facts and SHA-256 guards for the two original graphic tables.

## Integration

`src/engine/startup-animation.ts` encodes the shared artwork and adds the two
guarded writes to static builds, the developer dynamic-loader path and the
standalone MIDI Scenes build. The replacement is mandatory infrastructure,
independent of module selection. Existing original-firmware validation and
atomic write-plan validation still apply. A changed graphic table or a second
application of the patch is refused.

For a native image already composed locally, use a separate private output:

```sh
python3 -B sdk/runtime/startup/build.py /private/local/mainos.bin /private/local/modwerk-mainos.bin
```

`build.py` is an independent Python encoder of the same artwork. It checks
both graphic guards before writing any output. It accepts images whose module
composition leaves those tables intact. Package the resulting MAIN image with
the existing firmware packaging tools; keep all firmware local.

## Layout and resource bounds

| Region | Address | Exact bytes |
| --- | --- | ---: |
| Particle records | `0x400a81fc` | 5,058 |
| Wordmark ink | `0x400c3c32` | 440 |

The 843 particle records each hold three signed big-endian 16-bit values. The
483 distinct mark pixels repeat at identical final positions to retain the
original record count and loop bound. Frame delays form a clockwise phase;
each tile shares a delay so it lands as a coherent block. Repeated ninth-tile
points land 80 ms after the first pass, creating a short comet tail. All delays
stay in the original 0–255 range. The renderer's smallest 7×7 sprite places its ink at (3,3), and the
renderer subtracts ten from the particle Y coordinate; final display coordinates
are therefore `(63 + X, 21 - Y)`.

The wordmark retains 110 columns, 15 rows, one 32-bit word per column and the
original opaque mask. The bitmap and LCD use reversed vertical coordinates;
the top visual row occupies bit 17 and the bottom row bit 31. No additional
flash bytes, RAM, stack, heap or sample-memory reservation are introduced.
Renderer and LED instructions are unchanged. No physical chip timing is claimed.

## Verification

With Node 24 and the local original MAIN OS 1.40C:

```sh
node scripts/verify-startup-animation-native.mjs /private/local/original-MAIN.bin /private/local/new-startup-report
```

The input can also be the owner's complete original `.bin` firmware; that adds
full firmware round trips, including preservation of its opaque tail and seed.
The private verifier compares complete browser/native image bytes for ten
profiles: core only, Repitch, Mini Verb, Tape Echo + Euclid, Analog BD,
Sidechain Compressor, USB Audio + Quantizer, standalone MIDI Scenes, the
developer dynamic-loader path and direct static composition with stock FX2.
It checks separation from other static write plans, changed-table refusals,
repeat-application refusal and original-input immutability. Temporary firmware
is removed; only a sanitized text report is retained.

Unit tests check exact table extents, bitmap orientation/padding, every final
mark pixel, bounded particle coordinates, the clockwise tile sequence and the
ninth tile's later arrival/echo.
See [the verification record](../../../docs/STARTUP_ANIMATION.md) for actual
LCD capture results and remaining checks.

## Base edition

The Elekloader base boots with its own edition of this animation, so a tester knows at a glance that
the new base is running: **NEW** left of the mark, the base version right of it (the part of
`VERSION` in `build_core.py` before the dev suffix, e.g. `0.3.1`), the mark and the wordmark as above.
Public builds keep the animation described so far, byte for byte (`test_startup_base.py` compares it with
the recorded hashes). `build.py` produces the edition when `writes()` / `apply()` get a version, and
`--base-version 0.3.1` does the same from the command line; `build_core.py` passes `VERSION` itself.

`base.json` is the authored data: the small pixel font, the text (size, place, landing times), the layout
shift and the LED show. The text uses the same stock particle records as the mark: the records the mark does
not need carry the letters, and the ninth tile's comet tail takes what is left. The edition lowers the mark
and the wordmark by three rows for balanced margins and leaves out any caption under the wordmark: the stock
renderer lands particles on the bottom three rows one pixel off, so text stays above row 61 (the encoder
refuses anything else).

The LED show replaces the two lamp tables of the boot loop (67 lamps on an MKII panel, 44 on an MKI): green
converges from the edge of the panel to the middle while the particles fly in, red follows the wordmark's
wipe from left to right, T1-T8 pop as the eight tiles lock in and REC lights as the detached tile lands. The
stock loop gives every lamp two brightness waves, 15 - |p + s|, where p comes from the lamp's table entry and
s from the loop time; `base.json` stores when each lamp's red and green peak, in milliseconds of logo time, and
the encoder turns that into table entries. Nothing is left lit when the loop ends. Three instruction
immediates change as well (six bytes, each guarded by the SHA-256 of the stock bytes): the loop's time step for
the LEDs goes from 40 ms to 10 ms per brightness level, so pulses last 0.3 s instead of 1.2 s, and the
wordmark's row moves down three rows with the mark. This is the first time the startup patch touches
instructions.

Check a composed base image with `scripts/verify-startup-base.py` (see its header). It needs the reviewed
emulator and the image; it writes nothing unless you ask for the GIF, PNG or record.

## Authorship and licence

Original Modwerk artwork and encoders © 2026 Modwerk contributors, under the
repository's GPL-3.0-or-later licence. Underlying Octatrack firmware and renderer
remain Elektron's property and are never distributed with this source.
