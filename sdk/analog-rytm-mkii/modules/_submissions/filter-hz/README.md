# Filter Hz

## Overview

The FILTER page's FRQ value popup shows the cutoff frequency instead of 0 to 127:
13.8Hz at 0, 440Hz at 60, 1.11kHz at 76 and 21.1kHz at 127, to three significant
figures. The scale is one semitone a step,

    f = 440 × 2^((v − 60) / 12)

as MrScruff measured it on the self-oscillating LP2 filter (every fourth value from
16 to 116 within 0.01 semitone of the formula). Only the text changes: the filter,
its range, saved kits and every other parameter are untouched.

Version **1.1.0** for Analog Rytm MKII OS **1.73**, with core-ar2 0.1, and OS
**1.74**, with core-ar2 0.3. The code is the same on both. It is
[rytm2_mods](https://github.com/Iced-Cream/rytm2_mods)' elemod port of MrScruff's
`0008-filter-hz` from [rytm-mods-src](https://github.com/Iced-Cream/rytm-mods-src),
with his code unchanged. Hardware testing is recorded in the
hardware reports for [OS 1.73](evidence/hardware-testing.json) and
[OS 1.74](evidence/hardware-testing-1.74.json), and in [TESTING.md](TESTING.md).

## Controls

| Control | Action |
| --- | --- |
| Knob E — FRQ | Unchanged control. Its value popup shows the cutoff in Hz or kHz instead of the number. |

There are no new controls, menus or settings. To get the stock popup back, build
without the module.

## Usage

The popup appears whenever FRQ is turned, on any track and in any kit.

### Quick tutorial

1. Use a build containing Filter Hz. Select a track and press FILTER to open its FILTER page.
2. Turn FRQ (knob E). The value popup reads the cutoff in hertz instead of 0 to 127: 440Hz at the stock value 60, one semitone a step.
3. Turn FRQ fully right for 21.1kHz, the open filter, or fully left for 13.8Hz. RES and every other parameter still show their plain numbers.

| Stock value | Popup |
| --- | --- |
| 0 | 13.8Hz |
| 60 | 440Hz |
| 76 | 1.11kHz |
| 126 | 19.9kHz |
| 127 | 21.1kHz |

## Compatibility and limitations

Requires core-ar2 0.1 on OS 1.73, or core-ar2 0.3 on OS 1.74. Use your own original
stock OS file.

- Built for OS 1.73 and 1.74 only.
- The scale was measured on the self-oscillating LP2 filter; the other filter types are assumed to share it.
- The popup shows the knob's value: envelope depth, LFO modulation and parameter locks applied elsewhere are not included.
- The 0 to 127 number is no longer shown for FRQ, so check the ends (13.8Hz, 21.1kHz) rather than a middle value when comparing with stock.

The module patches one site, eight bytes in `param_value_text` at `0x400a8648` (OS 1.73) or
`0x400a86b4` (OS 1.74),
the same site as the original mod. Another module patching those bytes cannot be
combined with it.

## Tests and measurements

See [TESTING.md](TESTING.md) for the commands and results. In short: the popup
shows Hz on an Analog Rytm MKII in builds of the core and Filter Hz alone, on OS
1.73 and OS 1.74, and on 1.74 beside the other rytm2_mods ports. Modwerk's own build of this folder gives main OSes
byte-identical to elekloader's builds of the rytm2_mods v1.0 (1.73) and v1.2
(1.74) releases. In rytm-emu the popup reads 440Hz and 21.1kHz where stock reads
60 and 127, with every other pixel the same, on both releases. Memory: 256 bytes
of the 128 KiB shared mod area. There is no code in the audio, sequencer or tick
paths.

## Authorship and licences

MrScruff: the original mod (rytm-mods `0008-filter-hz`), its design, code and
frequency measurements, published in rytm-mods-src with his permission.
Iced-Cream: the elemod port in rytm2_mods and this module. irpina: Elekloader and
core-ar2.

Code: [GPL-2.0-only](LICENSE), as rytm-mods-src. `include/ar2-1.73.inc` is
rytm2_mods' file at `698b859` and `include/ar2-1.74.inc` its file at `afd461d`
(v1.2), unchanged. `src/filter-hz.s` is rytm2_mods' `filter-hz.s`, with an
`.ifdef OS174` choosing the include and one comment naming both addresses. The
includes name firmware routines by address only. The upstream README is in
[upstream/README.md](upstream/README.md). Screens show Elektron's interface solely
to document the modification. No Elektron firmware is included.

## Screens and audio

These captures are from rytm-emu running a build of core-ar2 0.1 and Filter Hz
from stock OS 1.73. The same input on OS 1.74, with core-ar2 0.3, gives the same
three screens byte for byte. See [capture provenance](media/capture.json) for hashes and
inputs. The mod changes no sound, so there is no audio demonstration.

![FILTER page with ATK, DEC, SUS and REL above FRQ, RES, TYP and ENV.](media/filter-page.png)

Press FILTER on any track to open its FILTER page. FRQ is knob E, at the left of the lower row.

![FREQUENCY popup with the FRQ label reading 440Hz and the filter curve cut off in the middle.](media/frq-440hz.png)

Turn FRQ: the popup now reads the cutoff in hertz. At the stock value 60 it shows 440Hz; each step is one semitone.

![FREQUENCY popup with the FRQ label reading 21.1kHz and the filter curve fully open.](media/frq-open.png)

Turn FRQ fully right and the popup reads 21.1kHz, the open filter; fully left reads 13.8Hz.
