# Apply Scene testing

## Commands and exact revision

Emulator only, 15 Oct 2026. The source is the commit that adds this file, on branch `claude/apply-scene`. The image is the native build of a local remix holding only APPLY SCENE plus every stock effect on both menus, with `static_stock=True`:

```sh
make bus REMIX=apply-scene-stock BUILD=0          # in a scratch copy of sdk/octabam
APPLY_IMAGE=out/mainos_bus.bin OT_EMU=<octabam>/out/emu/ot_emu \
  APPLY_PROJECT=<octabam>/out/_stage_tmpl/OCTABAM/TMPL OT_PY=<octabam>/.venv/bin/python3 \
  python3 modules/apply-scene/verify.py
```

The build reports `apply_scene 448 B linked at 0x400d6b80` and `jmp 0x4005e4c8 -> apply_scene:as_yes_hook`. No DSP code and no other site.

## What verify.py checked (PASS, ot_emu `--mkii`)

The fixture: octabam's TMPL project, with bank 1 Part 1 (working and saved copies) rewritten. The machines are STATIC, FLEX, THRU, NEIGHBOR, PICKUP, FLEX, STATIC, FLEX, with MASTER TRACK on. Each track has a different stock FX1/FX2 pair with its defaults. Scenes 2 and 10 are selected. Pseudo-random locks sit on about 60 % of the 30 scene bytes of every track, so each track has bytes locked on both sides, on A only, on B only and on neither. These include slots the page does not have, AMP XVOL and XLV. Two unselected scenes also carry locks.

- **The apply.** It ran with SCENE A + YES and SCENE B + YES, alternating, at fader 127, 96, 64, 32 and 0. It wrote 112 to 160 bytes per run. Each time:
  - Every byte equals the stock morph model, and no other byte of the working Part moved. The model is the A/B blend, the Part value for an unlocked side, the track's weight long, MAC rounding, the nearest step, and the page's own range and enabled slots.
  - The saved Part, all scene locks, XLV, the scene selection, the mutes and the fader are unchanged.
  - The CS1 working copy equals RAM and the unsaved bit is set.
  - Exactly one toast appears, with the module's text.
  - RELOAD PART (FUNC + CUE) brings back working = saved.
- **The model is stock's.** On T3 (THRU) and T8 (the master), at fader 64 with the transport running, the AMP/FX1/FX2 halfwords of the voice records equal the model computed from the live lane. After an apply at the same fader position, the 16 bytes locked in both scenes kept their halfword. The 12 bytes locked in one scene follow the model from the new base.
- **Scene mutes.** FUNC + SCENE A mutes A, and an apply then treats A as unlocked. With both muted, nothing is written and the Part stays clean.
- **Stock flows.**
  - YES alone still shows ARM ALL: 0x46c7ff64 is set on press and cleared on release, and no apply runs.
  - YES held before SCENE A goes to stock on both edges.
  - SCENE A + TRIG selects a scene.
  - SCENE A + knob D on the AMP page writes the scene lock and not the Part.
  - SCENE + REC, STOP and PLAY reach their stock handlers.
- **Persistence.**
  - **Save and reload:** an apply, then Part SAVE (FUNC + PART, SAVE), then PROJECT > SAVE. A fresh boot of the written card loads the applied Part as both working and saved.
  - **Power cycle:** an unsaved apply survives. The second run takes the CS1 and card of the first and does the firmware's own power-up load (`--cs1-in`, `--no-post`). The working Part is byte-identical and all eight machine types are intact, so the power-up check of the Part passed.

Cost under ot_emu, from the YES press to the toast: 2.2 to 3.4 million ColdFire instructions for 106 to 160 writes, and 5.5 million once. Most of it is the stock store and redraw per write. There is no idle cost and no DSP work. Hardware time is not measured.

## Stock flows

| Flow | Result |
|---|---|
| YES alone (ARM ALL) | unchanged |
| SCENE + YES | replaced by the apply (deliberate; README) |
| SCENE + TRIG select, SCENE + knob lock, SCENE + REC/STOP/PLAY | unchanged |
| FUNC + SCENE mute | unchanged; the apply follows it |
| RELOAD PART, Part SAVE, PROJECT SAVE, project load, power cycle | unchanged; carry the applied values |
| MIDI mode | the gesture is not taken (falls through to stock); not run |
| Pattern or Part change, arranger, sequencer ACT commit | not tested |

## Performance

Not run on the unit. The ColdFire cost is in the UI task only, per press; see above. evidence/performance.json is not written yet.

## Resources

448 bytes of ColdFire code and data, placed in the image's free run (`0x400d6b80` in the test build). One byte of state (whether the YES press was taken). No DSP memory and no saved data.

## Hardware

Untested. The MKII test image is APPLYSC01: APPLY SCENE alone, static stock, all stock effects. It is the image verify.py passed on: MAIN OS SHA-256 `40f780e65582398bcd6763dc000761b2e3b2817683b252d65cfcca3b68393a70`, card file `OCTATRACK_APPLYSC01.bin` SHA-256 `8ebf93f49077f1e6ef0629153f86537b4888928a7dc221d22e8212afd79e9d0c`. Checklist for the first run:

1. Flash APPLYSC01 from the card. It should boot normally and show the image name.
2. Set up a test track. On one track playing a loop, hold SCENE A and turn FX1 knob A fully left, then hold SCENE B and turn it fully right. On the same track, lock AMP VOL in SCENE A only.
3. Apply while playing. Put the crossfader in the middle, hold SCENE A and press YES.
   - SCENE APPLIED fits the toast.
   - The sequencer keeps time and there is no dropout or click beyond the parameter change itself.
   - FX1 knob A now shows about the middle.
4. Check the scenes afterwards. Move the crossfader to each end: you still hear scene A's and scene B's FX1 value. AMP VOL, locked in one scene only, changed when you applied, as described.
5. Repeat with SCENE B + YES at another crossfader position.
6. YES alone still shows ARM ALL.
7. Press FUNC + CUE (RELOAD PART). Everything returns to the last saved Part.
8. Check that save and reload keep it.
   - Apply, then FUNC + PART > SAVE, then PROJECT > SAVE.
   - Power off and on: the applied values are there.
   - Apply again without saving, then power off and on: the applied values are still there (unsaved), and RELOAD PART returns to the saved Part.
9. Check a muted scene. FUNC + SCENE A mutes A; an apply then uses only scene B's locks.
10. Stress test. Lock many parameters on all eight tracks in both scenes, then apply about ten times while playing at a fast tempo. Listen for dropouts, a stalled sequencer or a frozen screen.
11. Report:
    - the image SHA-256;
    - the MKII OS screen;
    - what you ran and what you heard;
    - anything that was slow or glitched.

## OT UI capture evidence

Pending. The toast was seen in the emulator framebuffer (`SCENE APPLIED` in the stock toast box).
