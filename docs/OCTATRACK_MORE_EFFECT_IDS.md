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

## Decision and plan (owner, 12 October 2026)

**A, with 160 ids: every installed module effect has its own id, up to 128 modules installed** (owner, 12
October 2026: "all the installed modules available on demand, only limited by load"). First decided as 64; then
the owner asked whether 32 would do, since at most 16 effects run at once (8 tracks, two slots; machines take no
effect id). Running effects are not the limit: an id is per effect type, stock keeps 19 of the 32, and each
installed module effect holds one, so today a 14th is refused as FULL whatever runs. Handing ids out only when a
project names a module would still cap a project at 13 different module effects; the owner wants none but load.
So 160: 19 stock, 141 for modules, every installed one with its id at install, as today. The Part stores an id in
one byte, so 255 is the hard limit (and 255 is the transport's DL_NONE); 160 leaves room past 128 modules.

Past 127, stock's reads of the Part's id matter: it loads the byte sign-extended (`mvs.b`), so ids 128-255 would
index before its tables. Those reads become zero-extended (`mvz.b`, the same length, one bit different), a patch
per site. Everything per id goes behind one constant (`fxids.h`), so the width is a rebuild, not a redesign. The
chooser lists grow with it: the owner's "a longer list than 32 entries" is the lists' row capacity
(`modwerk_fx*_list[32]`, `selection.c`'s `row>=32`, `dsp.c`'s pick `row > 31`), separate from the ids but done in
the same step. 128 installed modules also needs the loader's live-module cap (`RUNTIME_MODULES`, 32) at 128 and a
larger module pool: about 5 KB a module today, so about 768 KiB instead of 256 KiB, taken from sample memory at
boot (about 1 %), and the saved set's buffer (`modset.c`) to match.

An inventory of every 32-wide site (12 October 2026, about 120 sites) found these traps beyond the list above:

- **Masks that alias.** `LIVE_FX[i] & 31u` and `& 31u` on handles (dsp.c, status.c, fxmap.c) would map ids 32-63
  onto 0-31 without a warning. Every id mask (`modwerk_dsp_modules`, `dl_stub_at_boot`, used, dry, keep, held,
  stubbed, the MISSING handles) becomes an id set, and every `& 31` a bound check instead.
- **32 as "no id".** `choose(..., 32u, ...)` for a pinned module and `blame(32u, ...)` for a module without an
  effect: both become the new constant.
- **Wire and reply sizes.** MISSING (request 14) is fixed at 316 bytes, 13 entries; MEMORY MAP (24) at 276. Wider,
  both pass the base's 512-byte reply: they need paging (and lengths that are not whole 64-byte packets).
  The loader report's used and dry masks gain words (78 words at 32 ids, 87 at 160, never a multiple of 16).
  Parsers: `scripts/device.mjs`, `src/engine/elekloader/upload-usb.ts`. The DSP packet's id field is already
  16 bits; a package carries its preferred id in one byte.
- **Battery RAM.** The handle map (`fxmap.c`, 0x100fe000) grows from 780 to 3,852 bytes at 160 ids, still below
  the crash record at 0x100ff800 (checked at compile time); give it a new magic so an old map is dropped on purpose, not by a checksum miss. The
  `#MODWERK_FX=` lines keep their format (two-digit ids); an older base ignores lines with ids of 32 and up.
- **The DSP's saved region** is two words per id at the arena's head (`DL_CODE_START`, `SAVED`, the receiver's
  `#>64`). Only stock's 32 ids have originals to keep: ids from 32 up go back to the null stub, so the region stays
  64 words and the code arena keeps its size. The receiver's `r1+32` (proc = init + 32) becomes the table width.
- **Transport copies.** `allocator`, `manager`, `transfer`, `selection` and `buffers` are Octabam's files, changed
  only by `build_core.py`'s exact-match `DSP_EDITS`; the widening goes there (and `manager.c`'s `[32]`
  declarations are matched by those edits, so both sides change together).

Order, each step host-tested before the next:

1. **On the unit:** prove the tables' new home in X (stock's unreferenced $7a92-$7fff in the $6000 block, not the
   ESAI block) free with every stock effect and module running: a probe base that fills it with a pattern and
   reads it back over USB while effects change. The one step that needs the unit before the rest.
2. **The base at N ids** behind `MODWERK_FX_IDS` (32 until step 5): the masks, sentinels and arrays above in
   dsp.c, fxmap.c (new magic), fxpage.c, status.c; MISSING and MEMORY MAP paged; the report's masks widened.
   With N = 32 this changes no behaviour, so the unit's runs so far stay valid. **Done (12 October 2026, S56):**
   `fxids.h` holds the count and an id set of 32-bit words (no 64-bit shifts, so no libgcc); `build_core.py` passes
   `FX_IDS` and emits `modwerk_fx_modules` beside the transport's one-word `modwerk_dsp_modules` (step 3 retires it).
   The handle map keeps 'MWFX' at 32 and takes 'MWF' + the count otherwise. MISSING pages by its first entry (13 a
   page), MEMORY MAP by 32 packages (a stall past the last), the report appends the masks' other words and a pad
   (78 words at 32, 87 at 160, version 12); `device.mjs` and the site's `upload-usb.ts` read all of them. The host
   tests run at 32 and at 160 ids (`test_recipe.py`: a module at handle 40 counts as 40, never as 8). S56 builds
   and draws PROJ > MODWERK in `ot_emu`.
3. **The transport** at N: `DL_PACKAGES`, the manager's per-id loops and masks, `transfer.c`'s and `selection.c`'s
   id bounds. **Done (12 October 2026, S57):** `build_core.py`'s `WIDTH_EDITS`, applied after `DSP_EDITS`: allocator,
   manager, transfer, selection and buffers sized by `MODWERK_FX_IDS`, their masks (keep, named, soft, held,
   stubbed, `dl_stub_at_boot`) id sets; the one-word `modwerk_dsp_modules` is gone. `DL_CODE_START` stays 64 (the
   saved region keeps stock's 32, step 4). At 32 the ColdFire code of selection, buffers and transfer is identical;
   place, parts, advance and dl_residency_tick compile differently, so S57 ran
   `scripts/verify-octatrack-dsp-loader.mjs` under `ot_emu --frame --dsp` (a drum template project staged with
   Octabam's `stage_card.py`): pick, remove, queue, beside and union (Modulation, Spectrum and TapeHead named by an
   inactive Part) all passed. `build_core.py --fx-ids 160` compiles and links the whole base and transport (no image
   kept).
4. **The DSP**: the receiver's id bound and saved region, init and proc tables at the new home (`dsp_loader.py`
   writes them and rewrites the six operand words per payload), ids 32 and up free from the start.
5. **The ColdFire tables and N = 160**: FX1_IDS, FX2_IDS, FX1_ID2POS and ID2POS copied to 160 entries with their
   18 `lea` sites patched, stock's sign-extended id reads made zero-extended, the Part validator's clamp raised to
   159 (three sites), the lists' row capacity raised.
6. **128 installed modules**: `RUNTIME_MODULES` 128, the module pool about 768 KiB, the saved set's buffer with it;
   the hook events' cost with many modules measured on the unit.
7. **Compatibility:** id 31 stays dry from step 5 on, so a project opened on an older base or stock (which clamp
   to 31) plays dry there instead of running another module. TapeHead's preferred handle moves off 31; the
   project map keeps existing projects on their handles until they are opened on the new base.
8. **On the unit:** more than 13 module effects at once on both cores, a project saved with ids above 31 opened
   on the old flashed base (dry, nothing else running), the edge-case runs again.

