# Filter Hz — test report

- Module: `filter-hz` 1.1.0, for Analog Rytm MKII OS 1.73 on core-ar2 0.1 and OS 1.74 on core-ar2 0.3.
  1.1.0 adds the OS 1.74 release; the 1.73 package links to the same main OS as 1.0.0.
- Source: https://github.com/Iced-Cream/rytm2_mods at `afd461d4a8ef4306bb2a57d4c61ad35c362b3940` (tag `v1.2`), `filter-hz`.
  `include/ar2-1.73.inc` (`c0f1e25c…16ce`) is byte-identical to it at `698b859` (v1.0), and
  `include/ar2-1.74.inc` (`c57431f7…874b`) at `afd461d`. `src/filter-hz.s` is rytm2_mods'
  `filter-hz.s` (`7de4714b…7a8d`) with an `.ifdef OS174` choosing the include, which is the only
  difference from its `os1.74/filter-hz.s`, and one comment naming both patch addresses.
- Original: MrScruff's rytm-mods `0008-filter-hz`, in rytm-mods-src at `cf5ac006`, marked hardware-verified there.
- Stock OS 1.73: `.syx` `8ad67108…1e52`, main OS `28d9ef40…85d6`.
- Stock OS 1.74: `.syx` `cb0f99d6…e123`, main OS `34cd0c4d…1f3b`.
- Tested build FZ01 (OS 1.73, core-ar2 0.1 + filter-hz 1.0): `.syx` `58dec6c48bcd532e71fcb2ea46229ce9c41cb5337aa89e44efe7e3b294369830`,
  main OS `97eab77fccb4420c541175b407bfc708ffe9bb9f7d69fd7e27d1f5aac0cbb0f2`.
- Tested build C3A4 (OS 1.74, core-ar2 0.3 before #153 + all eleven rytm2_mods v1.2 ports): `.syx`
  `04d987ced36850eef5eb5cd1215d411edf621a5af94f980525ab561c9108f951`, main OS `fc871476…d529`.
- Build FZ74 (OS 1.74, released core-ar2 0.3 + this module): `.syx` `62c256261d643752c9e8ffb357aada048af75a9b03c1f1aae649287e4bae7745`,
  main OS `2d8aead1932dd07003c75b233c4c93291d144c4eb5d6a8a11f1fecece1ea948d`. Tested on the unit 2026-10-22.

## Hardware

**OS 1.73.** On an Analog Rytm MKII, 2026-10-13, Iced-Cream flashed FZ01 with Elektron
Transfer and confirmed that the FILTER page's FRQ popup shows the cutoff frequency in Hz,
then restored stock 1.73. The port was later confirmed again in a build with all eleven
rytm2_mods ports. See [the 1.73 hardware report](evidence/hardware-testing.json).

**OS 1.74.** On 2026-10-22 Iced-Cream flashed FZ74 (the released core-ar2 0.3 and Filter Hz
alone) with Transfer. It booted and played as stock. FRQ fully left read 13.8Hz, fully right
21.1kHz, one step back 19.9kHz, and RES still showed a plain number. A minute of playback while
turning FRQ, with samples and delay and reverb sends on all tracks and heard over Overbridge, had
no freezes or dropouts. Stock 1.74 was restored afterwards.

Earlier, on the same unit, 2026-10-18, in R8T2 (core-ar2 0.1 ported to 1.74 and eight
ports, with rytm2_mods v1.1's Filter Hz): FRQ fully left read 13.8Hz, fully right 21.1kHz,
one step back 19.9kHz, and RES still showed a plain number. On 2026-10-20, in C3A4
(core-ar2 0.3 and all eleven v1.2 ports, including this module's v1.2 release object
`25055fc7…512a`), each mod's own test passed. Relinking C3A4's core and v1.2's eleven
release objects on stock 1.74 gives C3A4's main OS byte for byte. See
[the 1.74 hardware report](evidence/hardware-testing-1.74.json).

Duration and readings beyond those were not recorded.

## Source build comparison

The module is a submission (`modules/_submissions/`) until the browser can build it. Modwerk's own validation and compiler path, run on this folder:

```sh
node scripts/machine-modules.mjs --drafts --base origin/main
MODWERK_CROSS=m68k-linux-gnu- node scripts/build-elemod-packages.mjs --output OUT --source-commit <commit> --drafts --module analog-rytm-mkii:filter-hz
node scripts/verify-elemod-source-parity.mjs --packages OUT --oracle ORACLE --out RESULT \
  --firmware analog-rytm-mkii:Analog-Rytm_MKII_OS1.73.syx --firmware analog-rytm-mkii:Analog-Rytm_MKII_OS1.74.syx
```

`ORACLE` held:
- for 1.73, an elekloader build of `core-0.1.elemod` (core-ar2 0.1, `b5b7b10f…a5c1`) and
  rytm2_mods v1.0's release `filter-hz-1.0.elemod` (`e1d63508…87bf`);
- for 1.74, elekloader's `core-ar2-0.3.elemod` release (`core-ar2-v0.3`, 769d9aa,
  `6b97dfb3…3e58`) and rytm2_mods v1.2's release `filter-hz-1.0-os1.74.elemod` (`25055fc7…512a`).

Each materialised Modwerk package, linked with that core, gives the same main OS as the core
linked with the release object ([source-parity.json](evidence/source-parity.json)):

| Release | Modwerk package | Main OS | Equals |
| --- | --- | --- | --- |
| 1.73 | `6c6bae2b…0341` | `97eab77f…b0f2` | FZ01, the build tested on the unit |
| 1.74 | `98b1bde0…ef8a` | `2d8aead1…948d` | FZ74, the build tested on the unit |

`.run` is 256 bytes, one site, no relocations, on both. The stock bytes at both sites are the
same (`f08a5394…729c`).

Compiler: Ubuntu 24.04 `m68k-linux-gnu` GCC 13.3.0 and binutils 2.42. Modwerk's pinned Docker
toolchain was not run here, and CI's `elemod-source` job compiles published folders only. The
firmware and the linked builds stayed on the owner's computer.

## Emulator

[rytm-emu](https://github.com/trigcondition/rytm-emu), headless `dtboot`, the same input on the
module's build and on stock ([capture plan](media/capture.json)): `3c4c42c` on FZ01 and stock
1.73, and `c5732f0` on FZ74 and stock 1.74.

| Screen | Stock | With Filter Hz (1.73 and 1.74) |
| --- | --- | --- |
| FILTER page | FRQ label | identical |
| FRQ at 60 | `60` | `440Hz` |
| FRQ at 127 | `127` | `21.1kHz` |

On 1.73, across all 104 screens of the run, every difference lies in the FRQ label (x 3–95,
y 144–159 of the 384×192 PNG). On 1.74 the three screens used here are byte-identical to the
1.73 ones. Of the 104 screens, 94 differ from stock 1.74 only in the FRQ label. Turns 60, 70
and 80 also differ in the filter curve, because the two runs had reached different FRQ values
mid-turn (622Hz against 68 at turn 60). The analog voices are stubbed in the emulator, so this
says nothing about sound, which the module does not touch.

## Load and memory

256 bytes in the shared DDR area, no `.bss`, no fast SRAM. The site is in
`param_value_text`, which formats a parameter's value for the screen; for any parameter but
FRQ the stub re-runs the two displaced instructions and returns. Nothing runs in the audio,
sequencer or tick paths. Static reading, not a measurement.

## Not tested

- Filter types other than LP2 against a measured cutoff (the scale is assumed to hold).
- Other modules beside it, except rytm2_mods' own ports.
- Long sessions, project save and reload, and a power cycle with this build were not recorded.
