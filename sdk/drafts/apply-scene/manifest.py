"""APPLY SCENE -- hold [SCENE A] or [SCENE B] and press [YES]: the sound the
crossfader blends right now becomes the active Part's base sound.

For every audio track and every scene-lockable page-1 parameter (PLAYBACK of
the assigned machine, LFO SPD/DEP, AMP, FX1, FX2) that either selected scene
locks, the value stock's scene morph produces at the current fader position
(the frame builder, 0x4000ce42..0x4000cefa: an absolute A/B lerp, the Part
base standing in for an unlocked or muted side) is written to the active
working Part through stock's page-1 writer 0x40054cd8, the MIDI CC store.
The saved Part, both scenes, the scene selection, the scene mutes and the
crossfader stay as they were: stock RELOAD PART is the undo, and the scenes
keep morphing from the new base. XVOL (AMP, scene-only) and XLV (LEVEL with
a scene key held) have no base knob and are not written.

Stock routines changed: one. The base-layer YES handler 0x4005e4c8 takes a
press while a scene key is held (0x460d169c) in audio mode; on stock that
press shows ARM ALL, the same as YES alone, which stays stock. Everything
else replays the two displaced instructions. Measured under ot_emu: see
verify.py and TESTING.md.
"""

from remix.schema import Category, Proof, Gate, Detour, Kind, Linked, Module
from remix.stock_guard import stock_guard

MODULE = Module(
    name="apply-scene",
    key="APPLY SCENE",
    kind=Kind.CF_PATCH,
    doc="Hold SCENE A or B and press YES: the crossfader's current blend becomes the active Part's base.",
    category=Category.PARTS, author="npp1993", author_url="https://github.com/npp1993",
    proof=Proof.PORT, proof_note="ot_emu MKII, 15 Oct 2026 (verify.py); no hardware run yet",
    # 448 bytes, position-independent: an image zero run, not the DRAM reserve.
    linked=(Linked("apply_scene", "modules/apply-scene/unit.s"),),
    detours=(
        Detour(0x4005E4C8, stock_guard(0x4005e4c8, 8, "91fea154aed7ca7f7aed1e03380f8eba791542d2f01b3f4a9b173e2dec9df118"),
               "apply_scene", "as_yes_hook",
               "base-layer YES handler entry: a press with a scene key held applies the scene blend",
               kind="jmp", pad_to=8),
    ),
    gates=(Gate("modules/apply-scene/verify.py", remix_arg=False),),
)
