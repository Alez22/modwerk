# Direct Jump: tests and measurements

Recorded 24 October 2026. Version `0.1.0-experimental`.

- Source: sambanks/octabam `b725fb1a20e77bea37930be4f934a13ba53abc23` (`modules/direct-jump-kyoti/`), which pins the author's repository Zac-Kyoti/octatrack-kyoti-fw at `329b801cf90f32cbca97c6699a908908968e4df6` (`octabam-modules/direct-jump-kyoti/`). Modwerk source commit `6116a6a4d127ee0bac0ec835a474984be8b2c73e`.
- Tested image: a static native octabam build of this module alone with every stock effect kept (`scripts/export-composition-proofs.py --vendored-sdk --static-stock --modules direct-jump-kyoti --select direct-jump-kyoti:true --image-dir`, run from a private copy of this checkout's `sdk/octabam` with the original MAIN OS): MAIN OS SHA-256 `9af03715a100eeb80c564312e1d6c3d5666ba287a79f03555f19195285a07172`. The unit lands in the DRAM reserve at `0x40a955e0`.
- Original MAIN OS 1.40C: SHA-256 `164f31224bf61181e3f50e7dec40df9afcae5b16dbf6e4c0d0cc5e986af0a84e`.
- Emulator: octabam's `ot_emu` from the `npm run upstream:tools` checkout, SHA-256 `bdbe962c14fc3560fb3196b01566646b80a74fd451883873a77290b4973dbbf1`. It does not run a real unit's timing.

## Hardware (owner's MKII, 24 October 2026)

The USB package `c277d24f…` on the owner's Octatrack MKII, driven over USB by the agent; the owner did the power cycle. Full record: [evidence/hardware.md](evidence/hardware.md).

- **Flashed beta base `b5fae2ae`:** installed and kept as a tester's sync does it; self-test passed (1/1 intact, longest frame 372 µs, card set saved); after the owner's power cycle the kept set came back with Direct Jump and the self-test passed again; removal emptied the set.
- **RAM-booted development twin `7889c57a`** (the beta flags plus `--dev`, built from this branch), two trials, each rolled back: the sites held the unit's `jsr`/`jmp` and the [PTN]-layer slot `dj_toggle`; [PTN] + [YES] toggled with the toasts and the chooser stayed shut; with the toggle on, A16 (64 steps) jumped to A02 (16 steps) and back on the next step, the master position following the unit's tick count since START modulo the playing pattern's length within one tick of read lag (A16 came back at step 48, not at its start); three landings fell on step boundaries 8 to 12 ticks after the last reading taken before the key gesture; three cues in one gesture landed the last; with the toggle off a cue waited for the playing pattern's end, as on stock; each rollback left the four sites stock.

## Not tested

- On hardware: a jump into another Part, START SILENT, trig conditions, PER TRACK scales, external MIDI gear (Program Change, the absent MIDI START), the arranger and chains, a cancelled cue (USB key presses arrive about a step apart), listening, the card build, an MKI, and the site's own review/Keep/Undo pages.
- Beside Play Modes, MIDI Scenes, Mute Modes and Analog BD as a running combination (the gate and `modules:compat` find no shared bytes).

## Source identity

`upstream/README.md` and `LICENSE` are the author's files byte for byte (`sdk/imports/direct-jump-kyoti-b725fb1.json` records their Git blobs and SHA-256s). `patch_directjump_v7.s` is his file with one change, marked MODWERK: the landing's three kernel posts (`{0x15, bank}`, `{0x14, part}`, `{0x11, pattern}`) go through one added helper, `dj_post`, which reaches the kernel's post routine through `%a1`, and the second purge table's two addresses are loaded in the other order. The calls, their arguments and their order are unchanged. Without it, four runs of the USB package (up to 24 bytes) repeat stock's own posting and cancellation code and the strict stock-free scan refuses it.

Assembled with `m68k-elf-as -mcpu=5407` or `-mcpu=54455` (identical) and linked at `0x400d6d38`, the unit is 2,016 bytes, SHA-256 `2965bf7d4866fc6818040f6128cd0a2ece62305b534882d97e2379a40a249684`; `manifest.py` names that reference, and native octabam re-links the unit there and compares on every build. With the change taken back, the same source links to the author's 2,026 bytes, `a0f480909d91b7fac0fb77d08dd8b5e2199fc14731d4bb427be71478e296bf9e`, his manifest's oracle (checked locally, 24 October 2026).

The four stock guards (`0x400a1f72`, `0x400a221c`, `0x40043418`, six bytes each, and the four NULL bytes at `0x400bf0c0`) are the SHA-256 of the author's declared expectations and match the original MAIN OS.

## The gate

`verify.py`, run from a private copy of this checkout's `sdk/octabam` with the tested image, the original MAIN OS and the ColdFire port:

```sh
DJ_IMAGE=<MAIN OS> DJ_STOCK=<original MAIN OS> OT_EMU=<path to ot_emu> python3 modules/direct-jump-kyoti/verify.py
```

Result on the tested image: **all 32 checks passed** (about nine minutes).

1. The image: the original OS matches the three guards and the [PTN]-layer YES slot is NULL; the source links to the manifest's reference; the landing and MIDI START sites hold a `jsr` and the [PTN] release a `jmp` onto the unit's symbols; the slot names `dj_toggle`; after boot the unit in DRAM is this source linked at its address.
2. The toggle (MKII panel, empty card): OFF after boot; [YES] alone leaves it OFF; [PTN] + [YES] turns it ON and opens the toast; releasing [PTN] closes the toast and leaves the chooser shut (stock's [PTN] mode byte stays 0); again OFF, and ON. The original OS under the same keys opens no toast and opens the chooser.
3. OFF is stock: PLAY, then A02 cued at master step 7. Both images land at the end of A01, and the module image runs through the same 260 distinct sequencer states as the original OS (per track: step, previous step, ticks in step, armed, countdown, reload and scale; the master step, tick and scale, the first-fire and hold masks and the metronome counters; the author's reference-lock vector).
4. ON: A01 playing from START, A02 cued at clock tick 41 (master step 7, its last tick). The reference run plays A02 from START on the same image. A02 is edited in RAM; each case first checks that the reference run really plays the edit (its master and track step counts), then that the jump lands inside its window, and that from the tick after the landing to tick 300 every tick's state vector equals the reference's:
   - A02 16 steps (as A01): landed at tick 42, the next step; 258 ticks equal. With MIDI transport send on, the landing reached stock's MIDI START gate (`dj_nofa` ran) and the START send after it did not run.
   - A02 7 steps (NORMAL) on Part 2: landed at tick 42; 258 ticks equal; the active Part is 2 afterwards.
   - A02 in PER TRACK mode, master 16 steps at 1x, T1 16 steps 1x, T2 7 steps 2x, T3 5 steps 3/4x, T4 3 steps 1/2x, MIDI T1 5 steps 3/2x: landed at tick 48, the first tick at which every track is at a step boundary (the common step of these scales is 24 ticks); 252 ticks equal.
5. A power cycle of the port: the battery RAM of a run left ON, booted again, comes up OFF.

The two bytes that do differ from the reference are left out on purpose: the previous-pattern byte (`0x800065c1`; A01 here, nothing in the reference) and the landing snapshot word stock rewrites at its next wrap (`0x8000663a`). Neither is in the author's vector.

## The USB package

`python3 -B sdk/runtime/loader/build.py --octabam direct-jump-kyoti --upstream ~/.cache/modwerk-upstream/elekloader --stock <OS 1.40C update file>` builds the published ABI 7 package `public/octatrack-modules/direct-jump-kyoti/0.1.0-experimental.mwrm`, SHA-256 `c277d24f24bd05d4d75dc008ffced79471e6bf14068de65435175b3a506f655f` (2,350 bytes, module `075d79a3`, named Direct Jump): 2,016 bytes of code and data, no bss, 18 relocations, four stock-code sites (the three detours and the pointer), each named by the SHA-256 of the stock bytes and checked against the original OS. The strict scans of `module_packages.py --stock` pass: the longest run of the package also found in the stock OS has 10 counted bytes (the limit is 12), and `check_stock_free.py` finds no 16-byte run.

The package needs no base change. Direct Jump has no effect id, so it adds no row to `src/engine/assets/chooser-metadata.json` (the configurator gives a module without an effect id the same empty entry by itself), and the published beta base, whose identity hashes that file, stays as it is.

## Memory

2,016 bytes in the DRAM reserve (code, the two toast strings and 62 bytes of state), three six-byte detours and the four-byte pointer: 2,038 bytes. No DSP memory, no heap, no saved data. The state is the ON/OFF word, a tick counter since START, the landing's parameters and the last Program Change sent.

## Performance

`evidence/performance.json` (`npm run perf:audit -- check` passes); everything below is ot_emu (the ColdFire port, MKII panel) on the tested image, not chip timing.

- **Per tick.** PC watches on `dj_land`'s entry and return and on both sides of each stock call, with cues at four phases of the step on a 16-step, a 7-step (Part 2) and a PER TRACK pattern (tracks from 2x to 1/8x). OFF: 18 instructions a tick. ON, idle: about 35. An ordinary landing tick: 2,133 authored (2,344 with the stock calls). The dearest tick, a cue that lands on the tick that arms it: 2,946 authored (3,166 with the stock calls). A static count of the source bounds that path at 5,700 authored instructions. At 16 cycles an instruction: measured 47,136, static 91,200.
- **Where it runs.** The sequencer tick interrupt, whose ICR reads 3 (level 3) in the port: below the level-5 DSP frame interrupt, which preempts it. Its deadline is the next tick, 8.33 ms at the top tempo of 300 BPM (2,200,000 cycles at 264 MHz); the static bound also fits one 362.8 µs frame.
- **Load and stress, 62 s, the same input on the original OS and on the module image with Direct Jump ON:** one three-byte message every ms (notes on and off and CCs on channels 1-8) plus a MIDI clock byte every 10 ms (about 250 BPM), A02 edited to 7 steps on Part 2, a cue every second alternating A01 and A02, STOP and PLAY at 7, 22, 37 and 52 s. Longest frame interrupt (entry `0x4000aad4` to epilogue `0x4000d9a6`, over 174,000 frames): 29,434 instructions on the original OS, 29,442 with the module, 167.3 µs both in the port's time (3,990 instructions a sample). Idle: 56.64 % and 56.28 %. Every note, CC and clock message reached its handler on both images; 62 cues made 62 jumps (5 pattern changes on the original OS, where cues wait for the pattern end); no hang.
- **Unit.** The base's self-test on the owner's MKII with Direct Jump installed: longest frame 372 µs (no comparison run without it).
