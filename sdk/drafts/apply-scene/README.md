# Apply Scene

Version: 0.1.0 · author: @npp1993

> **Draft.** This module stays in `sdk/drafts/` until it has a hardware report and screenshots. To build it, copy or link this folder to `modules/apply-scene/` in a scratch copy of `sdk/octabam`. Its manifest paths are relative to that root.

Hold [SCENE A] or [SCENE B] and press [YES]: the sound the crossfader blends right now becomes the active Part's base sound. The screen shows SCENE APPLIED.

## Overview

Scenes on the Octatrack lock target values. The crossfader blends side A's value into side B's value for every parameter either scene locks; a side with no lock uses the Part's own value. Apply Scene takes that blend at the current crossfader position and writes it into the active Part, as if you had turned each knob to that position yourself. From there you keep working as usual: turn knobs, make new scenes, morph again.

The scenes, the scene selection, the scene mutes, the crossfader and the saved Part are not touched. RELOAD PART therefore brings back the Part as it was last saved.

## Controls

| Gesture | What it does |
|---|---|
| Hold [SCENE A] or [SCENE B], press [YES] | Writes the current blend into the active Part and shows SCENE APPLIED |

There are no settings.

## Usage

1. Lock some parameters in SCENE A and SCENE B in the usual way (hold the scene key and turn knobs on any page).
2. Move the crossfader until the sound is right.
3. Hold SCENE A or SCENE B and press YES. SCENE APPLIED appears.
4. Save the Part to keep it (FUNC + PART, SAVE), or RELOAD PART (FUNC + CUE) to go back to the last saved Part.

## What is written

For each of the eight audio tracks, every scene-lockable parameter that either selected scene locks:

- SRC page 1 of the machine the track uses (Flex, Static, Thru, Neighbor or Pickup; the stored pages of the other machines are not touched);
- LFO page 1 (SPD1 to SPD3, DEP1 to DEP3);
- AMP page 1;
- FX1 and FX2 page 1.

The value is the one stock's scene morph plays: side A's lock (or the Part value when A has none or SCENE A is muted) blended with side B's the same way, weighted by the crossfader. Stock hands the DSP a value with a fraction; the Part stores whole knob steps, so the written value is the nearest step. The write goes through stock's own parameter store, the one MIDI CC uses: it skips parameters the page does not have and keeps every value inside the parameter's range, then marks the Part as edited.

Not written: XVOL and XLV (the crossfader volume locks have no Part knob and stay scene locks), trig locks and LFO modulation (the result is the sound on steps without a trig lock), page 2 (stock cannot scene-lock it), and with MASTER TRACK on, track 8's SRC and AMP. Nothing happens in MIDI mode.

## Quick tutorial

1. On a track playing a loop, hold SCENE A and turn FX1's first knob to the left; hold SCENE B and turn it to the right. Leave the crossfader in the middle.
2. Hold SCENE A and press YES. SCENE APPLIED appears, and FX1's first knob now shows the middle value.
3. Move the crossfader to either end: the sound still reaches each scene's lock. Press FUNC + CUE to reload the Part and the knob returns to where it was.

## Compatibility and limitations

- Changes one stock gesture: SCENE A or B held + YES no longer shows ARM ALL. YES alone still does.
- After applying, the crossfader stays where it is. A parameter locked in both scenes does not move. A parameter locked in only one scene moves, because stock now blends that lock with the new base: the sound can jump.
- Undo is stock RELOAD PART, which also discards any other unsaved edits since the last Part save.
- One apply runs about 2.3 to 5.5 million ColdFire instructions in the UI task (measured under the emulator for 106 to 160 parameter changes). How long that takes on the unit is not measured yet.
- Patch site: the entry of stock's YES handler (0x4005e4c8). No DSP code, no saved data of its own, 448 bytes of code.
- Not tested on hardware yet. See [TESTING.md](TESTING.md).

## Tests and measurements

See [TESTING.md](TESTING.md). `verify.py` runs the built image under ot_emu.

## Authorship and licences

Original code by @npp1993, MIT (see [LICENSE](LICENSE)). Stock code is referenced by address, length and SHA-256 only.

## Screens and audio

Screenshots are pending.
