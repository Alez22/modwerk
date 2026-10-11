# More than 32 effect ids on the Octatrack

Owner, 11 October 2026: more than 13 module effects at once, and a chooser list longer than 32 entries. What
limits it today and the two ways past it, from a read-only disassembly of stock 1.40C (sha 164f3122…) and
Octabam's notes. **[doc]** Octabam's notes, **[code]** read from the disassembly or source, **[inf]** inferred.
Nothing below has been run on the unit yet.

## What limits it

**The DSP.** One 64-word record holds init[32] at X:0x215 and proc[32] at X:0x235 in both payloads [doc]
(DSP.md §5). A slot's id is `x:(r6+$1b) >> 8` (FX2: `+$1c`), used unmasked [code]. Six two-word instructions
per payload read the tables with a full 24-bit displacement (payload A: proc P:0x4b4, 0x4ce, 0x4ea, 0x504; init
P:0x4cb, 0x501), so the tables can move by rewriting one operand word per site [code]. Stock runs init only when
a slot's id changes [code]. X:0x255 (the Y-buffer bases) and a live ring at X:0x25d-0x3dc follow the tables, so
they cannot grow in place [doc, code]. Candidate room: X:0x08d98-0x08fff (616 words, "unreferenced" in DSP.md §7,
never probed) [doc], but that is the $8000 partition where core 0's ESAI DMA lives, and dense core work there
stalls the DMA (OCTATRACK_HARDWARE_TRAPS.md, reported on an MKI); stock's unreferenced X:$7a92-$7fff in the $6000
block was clean there and is the better home. X above 36K does not work. The base's receiver refuses ids over 31 (`dsp_receiver.asm`
BIND/UNBIND/BYPASS), `dsp_loader.py` hard-codes INIT/PROC 0x215/0x235 and 32, `transfer.c` refuses id >= 32.

**The ColdFire.** FX1_IDS 0x400d5f58 and FX2_IDS 0x400d5fdc (32 entries and a zero word, 7 `lea` sites each),
FX1_ID2POS 0x400d60d0 and ID2POS 0x400d6150 (32 entries, 2 sites each) sit back to back with a code-pointer table
after them [code]. All 18 reads load the Part's id with `mvsb` and index unmasked: ids 32-127 read past the
tables, 128-255 before them [code]. The Part validator 0x40002318 (bank file load 0x4008cea0, battery restore
0x40025770) clamps FX ids to 0-31 (`moveq #31` at 0x400023b6/bc, 0x400023de/e4) and page values to the
descriptor's range [code]. Nothing else is indexed by id: LFO destinations, scenes and parameter locks address
parameter slots 0-29 [doc].

**The Part** (6,322 bytes) keeps FX1 ids at +0x00-07, FX2 at +0x08-0f, page-1 values at +0x11a + 24t, page-2
at +0x2f2 + 30t [doc]. It has no free bytes (PARTS.md §9) [doc]; whatever sits in it travels with save, reload,
paste, clear and track copy [doc, code].

**The base.** Everything per id is 32 wide: dsp.c (dl_catalog, dl_codes, owner*, moving, the uint32 masks),
fxmap.c (32 map entries in battery RAM, the line parser), fxpage.c (lists, pages, serves, wide), the transport's
allocator (DL_PACKAGES 32), manager, buffers and selection (`id > 31`), and the site's 13 custom ids.

## A. Wider ids (up to 127)

Move the DSP's init/proc tables into free X and rewrite the six operands per payload; move the four ColdFire
tables and patch their 18 `lea`s; raise the validator's clamp to the new size; widen every base structure.
Ids stay in the Part, so save, reload, paste, clear and track copy need nothing. The ceiling is 127 (108 module
ids) unless the 20 signed reads change too.

- Opened on stock or an older base, a project's ids of 32 and up are clamped to 31. On stock that is a null
  stub (dry); on an older Modwerk base 31 is a module handle (TapeHead), so the wrong effect would run and be
  saved. Keeping 31 dry in new bases makes the clamp harmless from now on.
- Unproven: the free X region (probe it on the unit across every stock effect and module; not the $8000 block),
  and how the wider
  table is filled at boot (another payload X record, or the receiver copying it at its first frame).

## B. One reserved id dispatching to a second table

Stock's tables stay 32 wide; one id R runs a dispatcher that picks the module from a selector stored in one of
R's page-2 slots (copied with the Part, reaches the DSP in r6+$c-$e, and stock cannot lock or modulate it).

- Each module behind R loses one of its 12 parameter slots, and it collides with PLOCKS P2.
- FX*_IDS[R] (the knob page) has to be swapped for the selected track on every view, and the setter takes its
  defaults from FX*_IDS[id], not from the row picked.
- The validator clamps R's slots to the installed descriptor at load, so it must be made permissive.
- Stock never re-inits when only the selector changes: the dispatcher has to run sub-inits itself, restore
  X:$213 and keep r1, and map instances from r7 (DSP.md §7).
- ID2POS[R] gives one cursor row for every module behind R; the selection guard's no-change test must include
  the selector.

## Recommendation

A. It keeps Part semantics free (the hardest part of B), touches a known, finite set of sites, and the DSP side
is six operand words per payload. First step: prove a home for the tables free on the unit with every stock effect and module
running, preferring X:$7a92-$7fff (the $6000 block) over the ESAI block, then move the DSP tables with 64 ids,
then the ColdFire tables, then widen the base. The dispatch reads are a few per slot a frame, not dense work.
