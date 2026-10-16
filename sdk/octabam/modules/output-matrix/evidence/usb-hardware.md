# Output Matrix 0.1.1-experimental over USB on an MKII

- **Date:** 16 October 2026. **Tester:** npp1993 (the author), at the unit; installation driven over USB by Claude Code.
- **Unit:** Octatrack MKII, OS 1.40C, flashed with beta base `99336d35…`.
- **Base under test:** RAM-booted with `npm run device -- boot DIR --chunk 4096`; nothing flashed. Base identity `3e3e3de1f350781b…`, MAIN.raw SHA-256 `5ca0afbf038e17f7919c4d7cfb6ef518e3a4d9c41a12cfa69f59f1ac64a2acc4`, built with the beta flags (`--usb-midi --usb-audio 'USB AUDIO OUT TRACKS MAIN CUE' --site-events --table-owners --resident-stock-hooks --resident-on-demand --controllers`) from source commit `44738eaf` (main `a59677ee` plus this version). The same command on unmodified main reproduced main's committed base here byte for byte first.
- **Package under test:** `public/octatrack-modules/output-matrix/0.1.1-experimental.mwrm`, SHA-256 `e2df2fbfff7f956846c030a87c50ff391af427b8719d40018e6449cef8e48acd` (ABI 7, 20 sites, 6 stock copies).

## Installation

1. `try … --seconds 10` (trial, then roll back): the trial ran 10 s with the slot running. The rollback was refused once with `needs-recovery`; a few seconds later, with no further command, the unit read `normal, generation 2` with an empty inventory, so the base finished the rollback on its own. The site's client retries a rollback from recovery for the same reason (`octatrack-link.ts`: the engine's code was still being placed).
2. `try … --seconds 5 --accept`: accepted; `status` read `normal, generation 3, active e2df2fbf…`; INVENTORY listed OUTPUT MATRIX alone.

## Panel checks (the author's results)

| # | Check | Result |
|---|---|---|
| 1 | PROJECT > CONTROL > AUDIO > OUT CFG > MATRIX, YES: the switch goes through, no freeze | pass |
| 2 | In MATRIX the LEV box shows each track's destination (MN, PHN, M+C, …) without CUE held | pass |
| 3 | CUE + LEVEL on a playing track: MAIN, CUE, PHONES, a mono jack (PHL) and OFF; audio comes out where the label says | pass |
| 4 | MIXER MIX sets the PHONES level | pass |
| 5 | OUT CFG back to NORMAL: stock behaviour returns | pass |

## Limitations

- RAM-booted base: no power cycle, project save and reload, or Part reload on this version over USB.
- Output Matrix alone on the base: no other module installed beside it; MASTER TRACK, STUDIO, the mode conversion's other Parts and banks, and CC 51 out were not checked on the unit for this version.
- Functional checks by ear; no audio recording or chip timing. The smaller DSP code's sample-identical output is shown in the emulator (TESTING.md), not measured on the unit.
- One MKII; no MKI.
