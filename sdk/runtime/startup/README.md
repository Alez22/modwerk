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

The Elekloader base replaces the stock logo loop with its own startup,
[`boot_anim.c`](../../machines/octatrack/elekloader/boot_anim.c): **docking**. The
mark's ninth dot is a module arriving. First the mark flies in: every pixel of the
frame and the tiles comes from far beyond the screen and lands, the frame clockwise,
the tiles from the middle one round the ring, and the lamps catch the pixels as they
pass over the panel. Each landing tile lights its track key (T1-T8). The empty corner,
the socket, blinks, and a light far off at trig 1 answers. The module runs along the
trig row, turns up through the keys under the screen, enters it from below and docks.
Its wave reveals MODWERK, **NEW** and the version and rolls on across the whole
panel. It takes 3.5 s and ends on the same frame each
time (`base_art.final_pixels`), lowered three rows for room at the edges.

Screen and lamps are one plane: the LCD sits in the panel (lamp positions from the
stock lamp table at run time, 54.2 hundredths of a millimetre per pixel), so the
module and the wave cross the screen's edge without a break. The lamps are white on
an MKII. The startup sets channel A's colour to white at the panel's LED intensity
and repeats the firmware's own pre-logo colour call before it returns. An MKI has
fixed colours, so there they are red.

This folder holds the authored data the base draws from: `artwork.json` (the mark and
the wordmark, shared with public builds), `base.json` (the layout shift, the font,
NEW and the version line) and `base_art.py`, which writes them as C data
(`boot_art.h`) for `build_core.py` and gives the final frame to the tests. Public
builds are unchanged: `build.py` still writes only the two graphic tables above.

## Authorship and licence

Original Modwerk artwork and encoders © 2026 Modwerk contributors, under the
repository's GPL-3.0-or-later licence. Underlying Octatrack firmware and renderer
remain Elektron's property and are never distributed with this source.
