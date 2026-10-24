from remix.stock_guard import stock_guard
"""DIRECT_JUMP_KYOTI -- an optional immediate pattern change, toggled from the
front panel with [PTN] + [YES] (a toast confirms; it comes up OFF at every
power-on, so a unit that never enables it behaves exactly as stock).

A cued pattern takes over on the NEXT STEP instead of waiting for the current
one to finish, and the landing is LOCKED TO THE MASTER CLOCK: the new pattern
plays where it would be had it been running since START, whatever its track
lengths, scales or master settings. The Part, START SILENT and trig conditions
change as on a stock pattern change, and the last MIDI Program Change sent
names the pattern that plays. The arranger and pattern chains are untouched.

HOW IT LANDS (the author's): stock already re-lands the whole sequencer from a
snapshot behind the countdown byte 0x80006687 in phase D of its tick handler.
The unit arms that countdown and prepares the snapshot on the landing tick,
suppresses the MIDI START a jump must not send, and owns the [PTN]-held [YES]
key. Every per-track counter and the pattern-boundary body stay stock.

STATE. One word, DJ_MODE (0 = OFF, 1 = ON), inside the unit. A DRAM unit is
unpacked at every boot (card build) or loaded by the base at every install and
boot (USB), so it starts at 0 by construction; no battery restore reaches it.

MODWERK. The author's declaration (octabam b725fb1a, his submodule pinned to
329b801c) carries the stock bytes it expects at each site and `requires`
BATCH_BUGFIXES. Here every stock expectation is an address/length/SHA-256 guard
read from the builder's own OS file, and there is no `requires`: Modwerk modules
never need another module. The author's own notes (upstream/README.md, "Required:
the bugfix bundle") measure the two as independent, with the Part-change trace,
the fast re-cue Program Changes and the timing matrix identical with and without
it; the bundle was required because stock can leave a garbage per-track scale
byte on a MIDI track (PER TRACK scale), and this source already reads any scale
byte above 6 as the master's (the master's as 1x), so that byte cannot divide by
zero here. The two Keeps that protected the rest of the [PTN]-layer YES record
are dropped: a USB package cannot carry them, and the symbol reference's own
guard (the slot is NULL) still refuses a changed record. The author's conflicts
name modules Modwerk does not have (octabam's DIRECT JUMP and OCTAKIT), so none
is declared. patch_directjump_v7.s is the author's file, unchanged.
"""

import os

from remix.schema import Detour, Kind, Linked, Module, SymbolRef

# This module's own directory, relative to the build's cwd (octabam's repo root).
_HERE = os.path.relpath(os.path.dirname(os.path.realpath(__file__)))

# ---- the three hook sites ----------------------------------------------------
LAND_HOOK = 0x400a1f72      # phase D of the tick handler: the landing countdown read
NOFA_HOOK = 0x400a221c      # the MIDI START (0xFA) gate a jump must not open
PTNREL_HOOK = 0x40043418    # [PTN] release: the chooser stays shut after [PTN]+[YES]
# The [PTN]-held keymap layer's YES record (0x400bf0be) is NULL in stock; its press slot:
PTN_LAYER_YES_PRESS = 0x400bf0c0

# patch_directjump_v7.s, m68k-elf-as -mcpu=5407 or 54455 (identical), linked at 0x400d6d38:
# 2016 bytes. Re-linked there and compared on every build. The author's unit at that address
# (his manifest's oracle, the DIRECT JUMP code of his KYOTI V1.0 image) is 2026 bytes, SHA-256
# a0f480909d91b7fac0fb77d08dd8b5e2199fc14731d4bb427be71478e296bf9e; this source links to exactly
# that with its MODWERK re-encoding taken back (three kernel posts through dj_post, two leas
# swapped, so no 12 bytes of the USB package repeat stock code).
UNIT_BYTES = 2016
REFERENCE = (0x400d6d38, "2965bf7d4866fc6818040f6128cd0a2ece62305b534882d97e2379a40a249684")

MODULE = Module(
    name="direct-jump-kyoti",
    key="DIRECT_JUMP_KYOTI",
    kind=Kind.CF_PATCH,
    author="Zac-Kyoti", author_url="https://github.com/Zac-Kyoti",
    doc="Clock-locked DIRECT JUMP ([PTN]+[YES]): a cued pattern lands on the "
        "next step exactly where it would be had it played since START.",
    linked=(
        Linked("dj7", os.path.join(_HERE, "patch_directjump_v7.s"), dram=True, reference=REFERENCE),
    ),
    detours=(
        Detour(LAND_HOOK, stock_guard(LAND_HOOK, 6, "4aaaa6d9488b552fc485627001a1f1b8b4fc72156809c7f9750050c787869e56"),
               "dj7", "dj_land", "phase-D countdown read: arm the stock re-landing", kind="jsr"),
        Detour(NOFA_HOOK, stock_guard(NOFA_HOOK, 6, "6d3f127d6f8c27521bb383e06dae4599364ceb88426d80464a0cdffdc7d71cda"),
               "dj7", "dj_nofa", "no MIDI START (0xFA) on a jump", kind="jsr"),
        Detour(PTNREL_HOOK, stock_guard(PTNREL_HOOK, 6, "b229662bc9a5d09d0d4613dc32ce8de200fbda85d81dd13630451d0b780946e2"),
               "dj7", "dj_ptnrel", "[PTN] release: keep the chooser shut after [PTN]+[YES]"),
    ),
    symbol_refs=(
        SymbolRef(PTN_LAYER_YES_PRESS, 0, "dj7", "dj_toggle",
                  "[PTN]-layer YES press handler (NULL in stock)"),
    ),
)
