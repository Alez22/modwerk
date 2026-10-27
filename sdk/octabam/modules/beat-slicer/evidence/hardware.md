# Beat Slicer 0.1.66: hardware run, 27 October 2026

- **Unit:** the owner's Octatrack MKII, OS 1.40C, driven over USB by Claude Code (`scripts/device-send.py`, `npm run device`).
- **Base:** a RAM-booted development twin of the beta base with the sample-editor service (`--sample-editor`, event `ot_sample_editor_actions` at index 36), identity `b610b11c…`. It is the beta base `903f8ed6…` built as `0.3.1-modwerk-dev.1`, which adds the development readouts (`modwerk_cost`, `guard`); the exact beta base was not booted.
- **Package:** `public/octatrack-modules/beat-slicer/0.1.66-experimental.mwrm`, SHA-256 `6650ef77a837a61a570a300c3bd0b2d4dfd4c9bed6e52bb355034d39bf5ff90d`, 5,780 bytes (4,992 of code and data, 1,388 of bss), module `c8d078f2`, built from commit `35301de1360c5b2e940c54823010356809846632`.
- **How it ran:** two timed trials (`npm run device -- try FILE --seconds N`, no `--accept`), so each rolled back by itself. Nothing was kept, saved or flashed.
- **Source:** Flex slot 004 on track 4 (a one-shot stab, sample BPM 101.04, no slices beforehand) in the project on the unit, bank B pattern 1, project tempo 119.

## Trial 1 (180 s)

| Step | Result |
|---|---|
| AED → SLICE → YES | CREATE BEAT GRID listed directly above CREATE SLICE GRID |
| Open, stopped | BPM SAMPLE, BEATS 1, 101.04, 16 SLICE, CREATE |
| BEATS 2, YES | stock CREATE SLICES? confirmation; YES gave 8 evenly spaced slices from trim start |
| PLAY, then BEATS 4, YES | REPLACE, stock REPLACE SLICES? confirmation; YES gave 4 slices while the pattern played |
| BPM PROJ | 119.00, 5 SLICE (the last one shorter), REPLACE |
| NO | popup closed; the 4 slices unchanged |
| `selftest`, stopped | passed; modules 1/1 intact; card set 4, 0/1 |
| Timed rollback | rolled back; active identity the twin's again; `inventory` empty; the SLICE menu ends at CREATE SLICE GRID again |

Afterwards the stock DELETE ALL SLICES put the sample back to no slices.

## Trial 2 (90 s): cost

`modwerk_cost` (DTIM3 counts at 132 MHz) read before and after each window; the UI tick runs 61 times a second.

| Window | UI ticks | Runtime module draw | CPU meter |
|---|---|---|---|
| Installed, popup closed (AED SLICE page) | 488 | 31 µs a tick | 45.0 % |
| Beat Slicer popup open, BEATS and BPM turned 16 times | 605 | 1,058 µs a tick (640 ms in 9.9 s, 6.5 % of the CPU) | 63.6 % |
| Stock CREATE SLICE GRID list open, same turns | 602 | 31 µs a tick | 45.1 % |

The frame interrupt stayed at 26.3 % of the CPU in all three windows, its longest frame 34.9 % of a frame with the popup open (40.1 % closed), and no machine render was skipped. While the popup is open the CPU meter rises by about 18.5 points: 6.5 come from the module's own draw hook; the rest was not traced.

## Load without the module

| State | CPU meter | Longest frame | In the frame interrupt |
|---|---|---|---|
| No module, stopped | 41.0 % | 34.5 % of a frame | 23.0 % |
| No module, playing | 52.8–60.4 % | 62.4 % | 30.5 % |
| Beat Slicer, playing, re-slice committed in the window | 51.2–55.7 % | 70.6 % | 30.5 % |

## The exact beta base (40 s trial)

Afterwards the exact beta base `903f8ed6…` (`npm run octatrack:base -- --beta`, the base #992 ships) was RAM-booted from the twin. It does not answer development requests, so no panel steps or cost readouts ran on it. A 40 s timed trial of the same package ran (the module's tick reported its idle value every second), the base self-test passed with modules 1/1 intact, and the rollback left the inventory empty with the base's own identity active.

## Not run

- Static machines (no Static slot in the project held a sample), completed recorder buffers, and slicing during recording.
- A project save, reload or power cycle with the slices kept.
- Slicing on the exact beta base (only the trial and self-test above), card builds, the MKI, other modules installed beside it.
- A MIDI flood. Beat Slicer has no MIDI path.
- A per-frame maximum for the draw: the figure above is the average over 605 frames.

twwwy's earlier MKII reports (Flex, Static and recorder buffers, more than 20 minutes) are in `TESTING.md` and `SAMPLE_EDITOR.md`; they ran an earlier package on a private build with the event at index 35.
