# Driving the Octatrack from an agent

How to work a real Octatrack MKII running a Modwerk development base (`build_core.py --dsp-loader --dev`) over
USB: start the link, send steps, read the unit, change things without harming the owner's project, and keep
runs short. Everything here was done on the owner's MKII on 11 October 2026. Why things fail is in
[OCTATRACK_HARDWARE_TRAPS.md](OCTATRACK_HARDWARE_TRAPS.md).

## The rules

- Never SAVE, SAVE ALL or SYNC TO CARD the owner's project, unless the owner asks to recover something.
- Do not change the owner's Parts. Test on a bank whose working Part equals its saved Part (bank B in
  LIVE/Dev12: every Part FILTER/DELAY). Check that with `mem` (below) first, and put it back with RELOAD
  afterwards.
- Read the state before you change it, and after you put it back.
- After a power cycle, check the Part again: the unit can come back with an older working copy from the card
  (11 October 2026: a RELOAD made before the unplug was gone, and picks from before it were back).
- Keep each command short: a few steps, a time limit, its output read at once. A long run goes in the
  background and logs every step, and you look at the log.
- Never power-cycle on your own; ask the owner. Never flash.

## Start the link

```sh
export PATH=~/.nvm/versions/node/v24.21.0/bin:$PATH   # Node 24; the default node is 18 and cannot load .ts
while :; do npm run device -- serve; sleep 1; done
```

Run it in a terminal of the owner's, or in a background task: those stop after two hours. It starts the USB
bridge, keeps one connection open, pings every 4 s (so MODWERK CONNECTED shows once) and comes back after a
RAM boot. One process at a time: a second `serve` or a one-shot `npm run device` fights it for the bridge.
After an unplug, a crash restart or a RAM boot, the bridge can hold a dead handle; `pkill -f usb_bridge;
pkill -f 'node scripts/device.mjs serve'` and the loop starts both again. Match the node process exactly: a
looser pattern such as `device.mjs serve` also matches a shell whose command line contains it, and kills the
loop itself.

## Send steps

```sh
scripts/device-send.py 'part2 pick:T1:FX2:E-Verb stats'
perl -e 'alarm 10; exec @ARGV' scripts/device-send.py ui   # with a time limit
```

One line, steps separated by spaces, the reply printed. A request has a 20 s limit; the session answers an
error and moves on. macOS `nc -U` hangs up before the reply, so use the script.

| Step | What it does |
|---|---|
| `KEY`, `KEY+KEY`, `KEY*N` | press (holding all but the last); `T1`-`T8`, `TRIG1`-`TRIG16`, `FX1`, `FX2`, `SRC`, `AMP`, `LFO`, `FUNC`, `YES`, `NO`, `UP`, `DOWN`, `LEFT`, `RIGHT`, `PLAY`, `STOP`, `REC`, `CUE`, `PATTERN`, `BANK`, `PROJ`, `PART`, `AED`, `ARR`, `MIDI`, `PUSHA`-`PUSHF` |
| `+KEY`, `-KEY` | hold, let go |
| `encA+3`, `encLEVEL-2`, `fader128` | encoders A-F, LEVEL, the crossfader |
| `w300` | wait 300 ms (rarely needed: the steps below wait for their own result) |
| `pick:T1:FX2:SPRING_REV` | pick an effect by name (spaces as `_`), FX1 or FX2: the chooser opens, LEVEL scrolls the exact rows, YES; done once the track runs it (about 120 ms after YES); fails at once if the loader refuses |
| `part1`-`part4` | switch Parts (PART + an arrow), done once the Part changed |
| `ui` | each track's FX1/FX2 as they run, the current track, Part, transport |
| `stats` | CPU, each core's mean/peak per mille, idle passes |
| `loader` | packets accepted, rejected, errors, jobs, selections, commits, rollbacks, code words per core |
| `mem:0x80000ec4:16` | RAM in hex, read-only, any length (not below the image) |
| (any sequence) | answers within 20 s beyond its own `w` waits, else an error, and the next request runs |
| `png:/path.png` | a screenshot, 256 x 128: cheaper to read than the text rendering |
| `screen` | the screen as block characters (thousands of tokens; avoid) |
| `crash` | the last crash record (vector, PC, registers); `crashtest` makes one |
| `stall` | the last DSP stall record: why, the loader's whole report, each core's last packet header, the live FX ids, as they stood when the stall was seen (it survives the power cycle); `stalltest` writes one now |
| `try FILE`, `remove FILE` | install or remove a module package, accepted at once |
| `boot DIR` | RAM boot a `build_core.py` output; the session restarts on the new base |

## The panel, as it behaves

- **Effects.** FUNC+FX1/FX2 opens the chooser (the left list; its right side are the effect's setup knobs).
  Moving the cursor does not pick; YES does. NO closes. LEVEL scrolls. `pick:` does all of it.
- **Parts.** Holding PART shows the selector: UP Part 1, RIGHT 2, DOWN 3, LEFT 4. In that selector,
  PART+FUNC+PLAY reloads the active Part from its saved copy (checked byte for byte). FUNC+PART opens RENAME,
  RELOAD, SAVE, SAVE ALL: do not use SAVE.
- **Patterns.** PATTERN+TRIG n selects pattern n of this bank. Another bank: BANK, then TRIG b (bank b), then
  TRIG n (pattern n) within four seconds (the manual's "CHOOSE BANK", "CHOOSE PATTERN"). Stopped, it applies
  at once; playing, it waits for the pattern's end.
- **Samples.** FUNC+SRC opens SRC SETUP on the machine list; RIGHT enters the slot list; YES on a slot
  assigns it; YES on an empty slot opens the card browser (LIVE/AUDIO). Parts store each track's slot.
- **Status.** CUE+PROJ opens the Modwerk status dialog; NO closes it. PROJ > SYSTEM > MODWERK explains it.

## Where the state is (OS 1.40C)

| What | Where |
|---|---|
| current track, Part | byte `0x80000000`, byte `0x80000003` |
| what each track runs (FX1 T1-8, then FX2) | 16 bytes at `0x80000ec4`; a Part's effects reach it when the transport starts, not at a stopped pattern change |
| current bank | `0x46c82456` holds its base: `0x400e21e0 + bank * 0x9b340` |
| a working Part's effects | 16 bytes at bank base `+ 0x8ed80 + part * 6322` (the whole Part is 6,322 bytes) |
| the saved copy | bank base `+ 0x9504a + part * 6322` |
| a pattern's Part | byte at bank base `+ pattern * 0x8ed8 + 0x8e57` |
| current and queued bank/pattern | bytes `0x800065bd`/`be` (current), `bf`/`c0` (queued; equal to the current ones when nothing waits); long `0x800065b8` = 1 while playing |
| effect ids and chooser rows | FX1_IDS `0x400d5f58`, FX2_IDS `0x400d5fdc` (id -> descriptor, name at +9), FX1_ID2POS `0x400d60d0`, ID2POS `0x400d6150` (id -> row) |
| chooser cursor | FX1 `0x460d5c94`, FX2 `0x460d5ca8` |
| input layers (menus, windows) | list at `0x460d165c`: two entries with no menu open |
| crash record, stall record | `0x100ff800`, `0x100ff900` (battery RAM) |

To compare a Part's working and saved copies: `mem:` both addresses with length 6322 and compare the output.

## Fast and safe habits

- One session; a handful of steps per command; `perl -e 'alarm N; exec @ARGV'` around anything that talks to
  the unit.
- Let steps wait for their result (`pick:`, `part`), not fixed `w` waits.
- Before a test: `ui`, the bank and Part bytes, the Part's working-equals-saved check. After: restore and
  read them again.
- Long runs (`scripts/octatrack-qualify.py`, benchmarks) in the background with a progress log; look at the
  log instead of waiting.
- If the screen does not change for a minute, the run is stuck: kill it, restart the session, read `ui`.
- Audio: `~/.cache/modwerk-octatrack/tools/rec SECONDS OUT.wav Octatrack` records MAIN and CUE over USB
  (4 channels, 44.1 kHz, 32-bit). A sustained sound (a looped sample) shows clicks; a clap does not.
