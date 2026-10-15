# Apply Scene

Version: 0.1.0 · author: @npp1993

> **Draft.** This module stays in `sdk/drafts/` until it has a hardware report and screenshots. To build it, copy or link this folder to `modules/apply-scene/` in a scratch copy of `sdk/octabam`. Its manifest paths are relative to that root.

Hold [SCENE A] and press [YES]: scene A's locked values become the active Part's own values. [SCENE B] + [YES] does the same with scene B. Hold both scene keys and press [YES] to keep the sound the crossfader blends right now instead.

## Overview

Scenes on the Octatrack lock target values. The crossfader blends side A's value into side B's value for every parameter either scene locks; a side with no lock uses the Part's own value. Apply Scene writes scene values into the active Part, as if you had turned each knob there yourself:

- **One scene** (SCENE A or SCENE B + YES): every parameter that scene locks takes its locked value. Parameters it does not lock stay as they are. The crossfader position does not matter.
- **The blend** (SCENE A and SCENE B + YES): every parameter either scene locks takes the value the crossfader plays right now.

From there you keep working as usual: turn knobs, make new scenes, morph again.

The scenes, the scene selection, the scene mutes, the crossfader and the saved Part are not touched. RELOAD PART therefore brings back the Part as it was last saved.

## Controls

| Gesture | What it does |
|---|---|
| Hold [SCENE A], press [YES] | Writes scene A's locks into the active Part: SCENE A APPLIED |
| Hold [SCENE B], press [YES] | Writes scene B's locks into the active Part: SCENE B APPLIED |
| Hold [SCENE A] and [SCENE B], press [YES] | Writes the current crossfader blend into the active Part: SCENE BLEND APPLIED |

When no value differs from the Part (the scene has no locks, you applied the same thing twice, or both scenes are muted for the blend), the screen shows NOTHING TO APPLY instead.

There are no settings.

## Usage

1. Lock some parameters in SCENE A and SCENE B in the usual way (hold the scene key and turn knobs on any page).
2. To keep one scene: hold SCENE A (or SCENE B) and press YES. SCENE A APPLIED (or SCENE B APPLIED) appears.
3. To keep an in-between sound: move the crossfader until the sound is right, hold both SCENE A and SCENE B, and press YES. SCENE BLEND APPLIED appears.
4. Save the Part to keep it (FUNC + PART, SAVE), or RELOAD PART (FUNC + CUE) to go back to the last saved Part.

## What is written

For each of the eight audio tracks, every scene-lockable parameter that the chosen scene locks (or, for the blend, that either selected scene locks):

- SRC page 1 of the machine the track uses (Flex, Static, Thru, Neighbor or Pickup; the stored pages of the other machines are not touched);
- LFO page 1 (SPD1 to SPD3, DEP1 to DEP3);
- AMP page 1;
- FX1 and FX2 page 1.

With one scene the value is that scene's lock, whether or not the scene is muted (you asked for it by name). With the blend it is the value stock's scene morph plays: side A's lock (or the Part value when A has none or SCENE A is muted) blended with side B's the same way, weighted by the crossfader. Stock hands the DSP a value with a fraction; the Part stores whole knob steps, so the blended value is the nearest step. The write goes through stock's own parameter store, the one MIDI CC uses: it skips parameters the page does not have and keeps every value inside the parameter's range, then marks the Part as edited.

Not written: XVOL and XLV (the crossfader volume locks have no Part knob and stay scene locks), trig locks and LFO modulation (the result is the sound on steps without a trig lock), page 2 (stock cannot scene-lock it), and with MASTER TRACK on, track 8's SRC and AMP. Nothing happens in MIDI mode.

## Quick tutorial

1. On a track playing a loop, hold SCENE A and turn FX1's first knob to the left; hold SCENE B and turn it to the right.
2. Hold SCENE A and press YES. SCENE A APPLIED appears, and FX1's first knob now shows scene A's value. Put the crossfader in the middle, hold SCENE A and SCENE B and press YES: SCENE BLEND APPLIED, and the knob shows the middle value.
3. Move the crossfader to either end: the sound still reaches each scene's lock. Press FUNC + CUE to reload the Part and the knob returns to where it was.

## Compatibility and limitations

- Changes one stock gesture: YES with SCENE A, SCENE B or both held no longer shows ARM ALL. YES alone still does.
- Which keys are down decides the mode, in either press order. With both held, releasing one leaves the other's single-scene apply.
- After applying, the crossfader stays where it is and the scenes keep their locks. A parameter locked in both scenes does not change sound. A parameter locked in only one scene can: after a one-scene apply it plays that lock at every fader position, and after the blend stock blends that lock with the new base, so the sound can jump.
- Undo is stock RELOAD PART, which also discards any other unsaved edits since the last Part save.
- One apply runs a few million ColdFire instructions in the UI task (measured under the emulator; see TESTING.md). How long that takes on the unit is not measured yet.
- Patch site: the entry of stock's YES handler (0x4005e4c8). No DSP code, no saved data of its own, 636 bytes of code.
- Not tested on hardware yet. See [TESTING.md](TESTING.md).

## Tests and measurements

See [TESTING.md](TESTING.md). `verify.py` runs the built image under ot_emu.

## Authorship and licences

Original code by @npp1993, MIT (see [LICENSE](LICENSE)). Stock code is referenced by address, length and SHA-256 only.

## Screens and audio

Screenshots are pending.
