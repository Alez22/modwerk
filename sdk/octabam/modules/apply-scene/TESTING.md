# Apply Scene testing

## Commands and exact revision

Emulator only, 15 Oct 2026. The source is commit `ae2a6eed` on branch `claude/apply-scene` (merged with main 86e0dfb8). The image is byte for byte MAIN OS SHA-256 `c4c210ceb0e32703dcfb04b86120e334856fd83279740be54e7ef73b7939af3b`. From a90849c9 the card build links the unit in the DRAM reserve (Play Modes' path), so the site's builder and native octabam agree beside Preview Vol, Mute Modes and the caves; that image (MAIN OS `3a74ff3635ce172ec3ef5949d188ebb297b0e8d969ca2b5d060b76420dded0bc`, the unit at 0x40a955e0, loaded at boot) passed verify.py 179/179, including the worst case and the emulated power cycle. The USB package is byte-identical to ae2a6eed's. The image is the native build of a local remix holding only APPLY SCENE plus every stock effect on both menus, with `static_stock=True`:

```sh
make bus REMIX=apply-scene-stock BUILD=0          # in a scratch copy of sdk/octabam
APPLY_IMAGE=out/mainos_bus.bin OT_EMU=<octabam>/out/emu/ot_emu \
  APPLY_PROJECT=<octabam>/out/_stage_tmpl/OCTABAM/TMPL OT_PY=<octabam>/.venv/bin/python3 \
  python3 modules/apply-scene/verify.py
```

The build reports `apply_scene 636 B linked at 0x400d6b80` and `jmp 0x4005e4c8 -> apply_scene:as_yes_hook`. No DSP code and no other site.

## What verify.py checked (PASS, ot_emu `--mkii`)

The fixture: octabam's TMPL project, with bank 1 Part 1 (working and saved copies) rewritten. The machines are STATIC, FLEX, THRU, NEIGHBOR, PICKUP, FLEX, STATIC, FLEX, with MASTER TRACK on. Each track has a different stock FX1/FX2 pair with its defaults. Scenes 2 and 10 are selected. Pseudo-random locks sit on about 60 % of the 30 scene bytes of every track, so each track has bytes locked on both sides, on A only, on B only and on neither. These include slots the page does not have, AMP XVOL and XLV. Two unselected scenes also carry locks.

- **The apply.** The blend (SCENE A and SCENE B held + YES) ran at fader 127, 96, 64, 32 and 0; SCENE A + YES at fader 64 and 0; SCENE B + YES at 96 and 127. Each run wrote about 110 to 160 bytes. Each time:
  - Every byte equals the model, and no other byte of the working Part moved. One scene: that scene's lock, clamped to the page's range, on enabled slots only; unlocked bytes stay. The blend: the A/B blend, the Part value for an unlocked side, the track's weight long, MAC rounding, the nearest step, and the page's own range and enabled slots.
  - The saved Part, all scene locks, XLV, the scene selection, the mutes and the fader are unchanged.
  - The CS1 working copy equals RAM and the unsaved bit is set.
  - Exactly one toast appears, with the mode's text (SCENE A APPLIED, SCENE B APPLIED, SCENE BLEND APPLIED), or NOTHING TO APPLY when no byte changed.
- **Nothing to apply.** SCENE A + YES twice at the same fader: the second press changes no byte and shows NOTHING TO APPLY. It still calls stock's writer for the fixture's 5 locks that stock clamps back to the Part value, so stock marks the Part edited; the Part bytes stay the same. The blend with both scenes muted writes nothing, leaves the Part clean and shows NOTHING TO APPLY.
  - RELOAD PART (FUNC + CUE) brings back working = saved.
- **The keys that are down choose the mode.** Stock's held-scene word (0x460d169c) names only the last scene key pressed and clears when either is released, so the module reads stock's per-key state table instead. SCENE B then SCENE A held + YES runs the blend (the held-scene word reads A only). Both held, then one released, then YES applies the scene still held, in both orders.
- **The model is stock's.** On T3 (THRU) and T8 (the master), at fader 64 with the transport running, the AMP/FX1/FX2 halfwords of the voice records equal the model computed from the live lane. After a SCENE A apply and, separately, a blend apply at the same fader position, the 16 bytes locked in both scenes kept their halfword. The 12 bytes locked in one scene follow the model from the new base.
- **Scene mutes.** FUNC + SCENE A mutes A. The blend then treats A as unlocked; SCENE A + YES still applies A's locks. With both muted the blend writes nothing and the Part stays clean, and SCENE B + YES still applies B's locks.
- **Stock flows.**
  - YES alone still shows ARM ALL: 0x46c7ff64 is set on press and cleared on release, and no apply runs.
  - YES held before SCENE A goes to stock on both edges.
  - SCENE A + TRIG selects a scene.
  - SCENE A + knob D on the AMP page writes the scene lock and not the Part.
  - SCENE + REC, STOP and PLAY reach their stock handlers.
- **Persistence.**
  - **Save and reload:** an apply, then Part SAVE (FUNC + PART, SAVE), then PROJECT > SAVE. A fresh boot of the written card loads the applied Part as both working and saved.
  - **Power cycle:** an unsaved apply survives. The second run takes the CS1 and card of the first and does the firmware's own power-up load (`--cs1-in`, `--no-post`). The working Part is byte-identical and all eight machine types are intact, so the power-up check of the Part passed.

- **The worst case.** Every scene-lockable byte of all eight tracks locked in both selected scenes (scene A at each slot's minimum, scene B at its maximum, poked into the working Part and its CS1 copy): the blend at fader 64 wrote 201 bytes (every enabled slot) as the model, SCENE A 125 and SCENE B 172, each followed by RELOAD PART.

Cost under ot_emu, from the YES press to the toast: 2.3 to 3.4 million ColdFire instructions for 110 to 160 writes in all three modes, 6.3 million once (160 writes), and 8,268,075 for the worst case (201 writes); a repeat apply that changes nothing, 113,287. Most of it is the stock store and redraw per write. There is no idle cost and no DSP work. Hardware time is not measured.

## Stock flows

| Flow | Result |
|---|---|
| YES alone (ARM ALL) | unchanged |
| SCENE A, SCENE B or both + YES | replaced by the apply (deliberate; README) |
| SCENE + TRIG select, SCENE + knob lock, SCENE + REC/STOP/PLAY | unchanged |
| FUNC + SCENE mute | unchanged; the blend follows it, a one-scene apply ignores it |
| RELOAD PART, Part SAVE, PROJECT SAVE, project load, power cycle | unchanged; carry the applied values |
| MIDI mode | the gesture is not taken (falls through to stock); not run |
| Pattern or Part change, arranger, sequencer ACT commit | not tested |

## Performance

Not run on the unit. The ColdFire cost is in the UI task only, per press; see above. evidence/performance.json is not written yet.

## Resources

636 bytes of ColdFire code and data, placed in the image's free run (`0x400d6b80` in the test build). One byte of state (whether the YES press was taken). No DSP memory and no saved data.

## Hardware

### Earlier behaviour on OMXATS30 (15 Oct 2026)

The user's combined MKII image OMXATS30 carries the earlier source (commit 719926a2, the same module tree as 270a2dae), where SCENE A + YES and SCENE B + YES both wrote the crossfader blend. Card file `OCTATRACK_OMXATS30.bin` SHA-256 `7d1fda80c0ee0a24ab34ed073e87e7bc01e2fb05987cd61fb50dbcd4ca69f3be`, MAIN OS SHA-256 `3d620adce09a1239066ca382a6db5787aa70667ee09870fe5c364b8f9340e55e`; verify.py on it 73/73. It also holds Output Matrix, Analog BD 0.1.6 (draft), Quantize Live Rec, RINGMOD SC, LIFT, BS WAVESHAPER and Mini Verb. Reported by the user: steps 1, 2, 5 and 6 below passed (setup, apply while playing, YES alone shows ARM ALL, RELOAD PART). They also reported that FUNC + SCENE muting "does not seem to work"; not diagnosed further, because it led to the redesign below. These results do not cover the current source.

### da2d18e4 over USB on the beta base (15 Oct 2026, MKII)

Reported through the session "firmware builder", recorded as written.

- **Unit and package:** user's MKII, OS 1.40C, beta base acf91e0a350e182d…. Package apply-scene-da2d18e4.mwrm (source da2d18e4), SHA-256 577a22e9b19df7f0f299d4cb01ca146827c0914e14a73bbad53c20000540467d. The device tool results, seen by that session:
  - `try --seconds 15` without accept rolled back to the base (generation 2, base active): the Undo check.
  - `try --accept` kept it (generation 3, active 577a22e9…).
  - `remove <file> --accept` was accepted (generation 4, active 472e6d03…, the removal package).
- **User-reported, while it was installed:**
  - SCENE A + YES and SCENE B + YES applied the locked values: pass.
  - Editing from the applied values afterwards: pass.
  - XVOL/XLV stayed scene locks: pass.
  - The blend (both keys + YES, crossfader in the middle) passed.
  - On a cleared scene, SCENE + YES still shows the toast.
  - No click or freeze seen in earlier testing.
  - Audio was not checked; the user only watched the values update.
- **After removal (user-reported):** SCENE + YES does stock's arming again ("just arms track"); nothing is applied: pass.
- **Still pending:** persistence across a power cycle.

### Current source (ae2a6eed): untested on hardware

Adds NOTHING TO APPLY to da2d18e4; nothing else in the behaviour changed. USB package `apply-scene-ae2a6eed.mwrm`, 758 bytes, SHA-256 `c63e2868e39669a3b22f0077923f9d542a521f73a75f5844fe62646d1382d163` (`build.py --octabam apply-scene --name "APPLY SCENE" --stock`): ABI 7, one hashed site, 636 bytes of code, no relocations, copies or hooks. Its longest run shared with the stock OS has 11 counted bytes (limit 12); no 16-byte run (check_stock_free). On the beta base rebuilt from main 86e0dfb8 (byte-identical to the committed base, e35da4ae…), the adapted ot_emu's `sites` scenario installed it and its removal restored every site byte. To check on the unit: SCENE A + YES twice shows NOTHING TO APPLY the second time, and so does SCENE + YES on a scene with no locks.

On the unit, 15 Oct 2026 (user's MKII, OS 1.40C), installed with `npm run device -- try apply-scene-ae2a6eed.mwrm --accept` on a RAM-booted base e8601162…; the unit listed APPLY SCENE (module 103be957), generation 5. User-reported:

- NOTHING TO APPLY (the same apply twice, a scene with no locks, the blend with both scenes muted): pass.
- SCENE A + YES, SCENE B + YES and the blend still apply: pass.
- Power cycle: afterwards APPLY SCENE was not installed and SCENE + YES did stock's ARM ALL. The power cycle had returned the unit to its flashed base (acf91e0a…), and a kept set belongs to the base it was kept on, so this is not a persistence result for the module.
- Power cycle on the flashed base: reinstalled with `try --accept` on acf91e0a… (generation 1, APPLY SCENE listed). Then apply, Part SAVE, PROJECT SAVE, power off and on. User-reported: APPLY SCENE was still installed and SCENE + YES worked as expected; the applied values were still in the Part, and the scenes were as before the shutdown: pass.

### da2d18e4: card image checklist

The user asked for SCENE A + YES and SCENE B + YES to apply that scene's own locks (muted or not), and for both scene keys + YES to keep the blend. The MKII test image is APPLYSC02: APPLY SCENE alone, static stock, all stock effects. It is the image verify.py passed on: MAIN OS SHA-256 `9aa80b87e3244629dbad4c23230996a6e4f07009e66cd01b571c55843878318f`, card file `OCTATRACK_APPLYSC02.bin` SHA-256 `3aa63d9faedb15a4d38adc13de4f80e97e3aa733d486f98653b86a38f6f7d932`. Checklist:

1. Flash APPLYSC02 from the card. It should boot normally and show the image name.
2. Set up a test track. On one track playing a loop, hold SCENE A and turn FX1 knob A fully left, then hold SCENE B and turn it fully right. On the same track, lock AMP VOL in SCENE A only.
3. One scene. Put the crossfader in the middle, hold SCENE A and press YES.
   - SCENE A APPLIED fits the toast.
   - FX1 knob A now shows scene A's value (fully left); AMP VOL shows scene A's lock.
   - The sequencer keeps time and there is no dropout or click beyond the parameter change itself.
4. Repeat with SCENE B + YES: SCENE B APPLIED, FX1 knob A fully right; AMP VOL unchanged (scene B does not lock it).
5. The blend. Crossfader in the middle, hold SCENE A and SCENE B, press YES: SCENE BLEND APPLIED, FX1 knob A about the middle. Try both press orders.
6. Move the crossfader to each end: you still hear scene A's and scene B's FX1 value.
7. YES alone still shows ARM ALL.
8. Press FUNC + CUE (RELOAD PART). Everything returns to the last saved Part.
9. Save and reload.
   - Apply, then FUNC + PART > SAVE, then PROJECT > SAVE. Power off and on: the applied values are there.
   - Apply again without saving, then power off and on: the applied values are still there (unsaved), and RELOAD PART returns to the saved Part.
10. Scene mutes. Check first that FUNC + SCENE A mutes scene A on its own: the crossfader no longer morphs toward A. Then:
    - SCENE A + YES still applies A's locks (deliberate).
    - The blend with A muted uses the Part value on A's side: with the crossfader in the middle the knob lands halfway between its old value and scene B's.
11. Stress test. Lock many parameters on all eight tracks in both scenes, then apply about ten times in each mode while playing at a fast tempo. Listen for dropouts, a stalled sequencer or a frozen screen.
12. Report:
    - the image SHA-256;
    - the MKII OS screen;
    - what you ran and what you heard;
    - anything that was slow or glitched.

## OT UI capture evidence

`scripts/capture-module-ui.py` on the native build of a90849c9 (MAIN OS `3a74ff36…`; ae2a6eed's image gave pixel-identical PNGs), card staged from octabam's TMPL project; the plan and every PNG's SHA-256 are in `media/capture.json`. The plan locks FX1 BASE to 30 in scene A and 110 in scene B, applies scene A twice (SCENE A APPLIED, then NOTHING TO APPLY), sets the crossfader to 64 (`fader`, added to the capture tool for this) and applies the blend (SCENE BLEND APPLIED). Every image was opened and checked.
