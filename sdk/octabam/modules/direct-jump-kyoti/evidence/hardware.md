# Direct Jump 0.1.0: hardware record

Owner's Octatrack MKII, OS 1.40C, 24 October 2026. Driven over USB by the coding agent with `npm run device -- serve` and `scripts/device-send.py`, following [Driving the Octatrack](../../../../../docs/OCTATRACK_DRIVING.md). The owner did the power cycle. Nothing was saved to the owner's project; every pattern change was undone and the unit was left on its flashed base with no modules installed, as found.

- USB package: `direct-jump-kyoti/0.1.0-experimental.mwrm`, SHA-256 `c277d24f24bd05d4d75dc008ffced79471e6bf14068de65435175b3a506f655f` (ABI 7, module `075d79a3`, 2,016 bytes of code and data, four stock-code sites), built from Modwerk commit `6116a6a4d127ee0bac0ec835a474984be8b2c73e`.
- The owner's project, bank A: A01 and A16 64 steps, A02 to A15 16 steps, all at 1x on Part 1, 132 BPM.

## On the flashed beta base (`b5fae2ae`)

The base the owner's unit runs, with no modules installed before the test.

1. Installed and kept the way a tester's sync does it (stage, the base's check of each site's stock bytes against the running code, trial, Keep): accepted, generation 1, inventory `Direct Jump`.
2. Self-test: passed, module 1/1 intact, longest frame 372 µs, card set saved 1/1.
3. Power cycle by the owner: the base came back with the kept set, inventory `Direct Jump`. Self-test passed again (1/1, longest frame 372 µs).
4. Removal (kept): accepted, inventory empty.

This base answers no development requests, so the panel and RAM tests below ran on a twin.

## On a development twin (`7889c57a`, RAM-booted)

The beta base's flags (`--dsp-loader --usb-midi --usb-audio --site-events --cached-modules --table-owners --resident-stock-hooks --resident-on-demand --module-sets`) plus `--dev`, built from this branch, RAM-booted with `boot` (no flash). Two trials of the same package, each rolled back at the end; no Keep on the twin.

- **Installed.** The landing and MIDI START sites read `jsr` and the [PTN] release `jmp` into the unit at `0x40d1ca40` (to `dj_land`, `dj_nofa`, `dj_ptnrel`), and the [PTN]-layer YES slot held `dj_toggle`. OFF after each install.
- **Toggle.** [PTN] + [YES] showed DIRECT JUMP ON and set the word; releasing [PTN] left the pattern chooser shut. Again: DIRECT JUMP OFF.
- **Clock-locked jumps, ON.** Playing A16 (64 steps) from STOP, A02 (16 steps) cued with [PTN] + [TRIG 2] took over on the next step, then A16 again. Before and after each jump the master position (step × 6 + tick) equalled the unit's tick count since START plus one constant, modulo the playing pattern's length (6 × 64 ticks for A16, 6 × 16 for A02), within one tick of read lag: A16 came back at step 48, where it would have been had it played since START, not at its start. In a second run three jumps (A16 to A02, A02 to A03, A03 to A16) landed at the unit's ticks 120, 228 and 330, each a step boundary, 8 to 12 ticks after the last reading taken before the key gesture (that window includes the gesture's own USB time).
- **Re-cue.** Three cues in one held [PTN] (A02, A03, A05): A05 landed, at the clock-locked position.
- **OFF is stock.** With the toggle off, A02 cued at A16's step 21 stayed pending until A16's end and then started at its first step; A16 cued back waited for A02's end and started at its first step.
- **Removal.** Each rollback left the four sites with the stock bytes (their SHA-256 equal to the manifest's guards).

## Not tested on hardware

- A jump into a pattern on another Part, START SILENT and trig conditions on a jump (the owner's patterns are all on Part 1; the emulator gate covers the Part change).
- External MIDI gear: Program Change and the absent MIDI START (emulator only).
- PER TRACK patterns with differing scales (emulator only), the arranger and chains, a cancelled cue (USB key presses arrive about a step apart at 132 BPM, so the attempt made two jumps).
- Listening: nothing was judged by ear; the owner did not run the hand test.
- The card build, an MKI, the site's own review/Keep/Undo pages (the device tool installed and removed the package).
- How long the unit ran with the module: about 15 minutes in all.
