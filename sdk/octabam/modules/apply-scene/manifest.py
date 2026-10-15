"""APPLY SCENE -- hold [SCENE A] and press [YES]: scene A's locks become the
active Part's base values; [SCENE B] + [YES] likewise for scene B; hold both
scene keys and press [YES]: the sound the crossfader blends right now
becomes the base.

For every audio track and every scene-lockable page-1 parameter (PLAYBACK of
the assigned machine, LFO SPD/DEP, AMP, FX1, FX2), the value is written to
the active working Part through stock's page-1 writer 0x40054cd8, the MIDI
CC store. One scene: its lock, muted or not; unlocked parameters stay. The
blend: for each parameter either selected scene locks, the value stock's
scene morph produces at the current fader position (the frame builder,
0x4000ce42..0x4000cefa: an absolute A/B lerp, the Part base standing in for
an unlocked or muted side), rounded to a knob step. The saved Part, both
scenes, the scene selection, the scene mutes and the crossfader stay as they
were: stock RELOAD PART is the undo, and the scenes keep morphing from the
new base. XVOL (AMP, scene-only) and XLV (LEVEL with a scene key held) have
no base knob and are not written.

Stock routines changed: one. The base-layer YES handler 0x4005e4c8 takes a
press while a scene key is down (stock's key state table, 0x46c7d8f1 +
key*24) in audio mode; on stock that press shows ARM ALL, the same as YES
alone, which stays stock. Everything else replays the two displaced
instructions. Measured under ot_emu: see verify.py and TESTING.md.
"""

from remix.schema import Category, Proof, Gate, Detour, Kind, Linked, Module
from remix.stock_guard import stock_guard

MODULE = Module(
    name="apply-scene",
    key="APPLY SCENE",
    kind=Kind.CF_PATCH,
    doc="SCENE A or B + YES: that scene's locks become the active Part's base; both scene keys + YES: the crossfader blend.",
    category=Category.PARTS, author="npp1993", author_url="https://github.com/npp1993",
    proof=Proof.PORT, proof_note="ot_emu MKII, 15 Oct 2026 (verify.py); no hardware run yet",
    # 448 bytes, position-independent: an image zero run, not the DRAM reserve.
    linked=(Linked("apply_scene", "modules/apply-scene/unit.s"),),
    detours=(
        Detour(0x4005E4C8, stock_guard(0x4005e4c8, 8, "91fea154aed7ca7f7aed1e03380f8eba791542d2f01b3f4a9b173e2dec9df118"),
               "apply_scene", "as_yes_hook",
               "base-layer YES handler entry: a press with a scene key down applies that scene, or with both the blend",
               kind="jmp", pad_to=8),
    ),
    gates=(Gate("modules/apply-scene/verify.py", remix_arg=False),),
)
