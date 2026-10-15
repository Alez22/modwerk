# Resident controller engines on demand (design, work in progress)

Status, 14 October 2026: design plus the DSP-side build slice. Nothing here is
wired into a base build yet, and nothing has run on hardware.

## Goal

`--resident-stock-hooks` links the Sidechain Compressor, Output Matrix and
Analog BD engines into the top of each core's program memory for good. The
owner's decision is to load an engine's DSP code only while its controller is
active. The hard rules are:

- No placement or code move at a Part switch, pattern or bank change, Part reload or project load, or while playing.
- No extra flash or card writes.
- Negligible runtime overhead.

## Measured sizes

Words, assembled in the reviewed toolchain image with `assemble_resident`/`engine_unit`:

| Core | Permanent block today | With every engine on demand | Engines (words, relocations) | Receiver growth |
| --- | --- | --- | --- | --- |
| A (core 0) | 2193 | 37 (stubs + 3 base words) | SC 388 (9), Matrix 773 (26, 4 negative), AB 998 (6, 1 negative) | +147 |
| B (core 1) | 1406 | 22 | SC 388 (9), AB 998 (6, 1 negative) | +114 |

Net freed with no controller active: about 2009 words on core 0 and 1270 on
core 1. With only Matrix on demand on core 0, the block is 1421 words and the
receiver grows by 81. Arena numbers from a full base build are still to be
measured.

## Design

1. **Stubs and their off paths stay resident**, unchanged, together with the stock-site JSRs and the COMPRESSOR bridge.
   - Each on-demand feature adds one P word to the block (`hwbase1/2/4`). It holds the absolute address of the placed engine, and is 0 while the engine is not placed (the boot upload's zero).
   - Only the receiver writes this word.
2. **Each engine is a relocatable unit** (`resident_dsp.engine_unit`): its P table, then its code. It is assembled at two high origins, so only long forms are used.
   - A word that moves with the origin is an address relocation. A word that moves against it is a displacement to a fixed stock address (`index | 0x8000`, transfer.c's convention).
   - At four arena bases, a fresh assembly must equal the relocated words, or the build stops.
3. **Receiver (generated, op 10)**. The packet's word 7 picks the operation, and an on-demand base keeps the default bytes.
   - **CAS (word 7 = 0).** CAS is unchanged, except that it refuses to enable an on-demand feature whose base word is 0. That check runs before any state or branch word changes. The "on" displacement is computed from the base word: `base + entry offset − stub`.
   - **PLACE (word 7 = 1).** Word 4 is one feature bit and word 5 a table offset; offset 0 unplaces.
     - PLACE is accepted only while the feature is dormant on this core. The engine must fit whole between offset 64 and the permanent block.
     - Placing again needs an unplace first.
   - **Neither the host nor a module names a DSP address.**
4. **ColdFire side (planned, not written).**
   - **Region.** Engines take the top of the core's arena, directly under the permanent block. The FX allocator's `capacity` is lowered to the lowest engine. Compaction and the big-blocks-from-the-top rule keep working against that capacity.
   - **Holes.** A removed engine above another engine leaves a hole, which the next engine reuses.
   - **When a claim can happen.** Only while the manager is idle, with no queued pick and no open journal. A dry run (`dl_allocator_prepare` then `cancel`) must show that the bank's Part union still fits under the lowered capacity. That union is the firm modules plus the soft stock effects, if they fit before the claim. Otherwise the claim waits, or admission refuses with `RUNTIME_MEMORY`, so a Part switch never has to load code because of an engine.
   - **Clearing the region.** If live FX code sits in the region, one automatic transaction re-places only those packages: new copies are uploaded while the old ones run, as `dl_move` does. It runs only while stopped, at least 2 s after the last key and with no pattern queued.
   - **Upload.**
     1. Words are unpacked and relocated on the UI task into a per-core buffer, so the frame interrupt scans no relocations.
     2. They are uploaded with an owned `DL_WRITE`, whose chunks are read back.
     3. An owned PLACE follows.
     4. Only then may the board send RESET (which also teaches the pool base), then ENABLE.
   - **Lifetime.**
     - An engine is owned by the controller generation.
     - A new generation of the same feature adopts an engine whose old slot is disabled (RETIRING, RELEASED or EMPTY) without reloading it. The code is base data, the same for every generation.
     - An engine is unplaced and freed only when no slot of that feature is held. Quarantine holds it for good.
   - **Rollback.**
     - A failed WRITE (no PLACE sent) frees the span.
     - An uncertain PLACE or UNPLACE keeps the span for the rest of the boot.
     - The owned channel's existing fail-closed rule stands.

## Measured on the unit (15 October 2026)

- **Arena.** A private development build with `--resident-on-demand` (base `25ab5804…`, nothing placed) leaves 4,418 words on core 0 and 4,546 on core 1. The beta base `362fb24d…` leaves 2,396 and 3,269.
- **Why it matters.**
  - On #619's development twin, SPRING REV was refused "DSP MEMORY FULL" on T5–T8 of bank A Part 2: core 0 held FILTER plus the PLATE and DARK REV that Part 1 names (2,102 words), so Spring's 1,063 did not fit beside them.
  - On the on-demand build all eight picks loaded beside them, 3,165 words on core 0. Playing: T1-4 62 %, T5-8 67 %, ColdFire 50 %, no loader error.
  - Stock keeps 6,158 words of effect code per core, so a Part with all three reverbs on T5–T8 cannot load on the beta base at all.
- **Not yet runnable.** Such a base cannot run Sidechain, Output Matrix or Analog BD, because nothing places their engines yet.

## Switch artifacts (first take, 15 October 2026, on the build above)

**Method.** Bank A Part 2's only sounding track (T3) repeats every 4 s bit for bit. Around each switch, the take is compared with the same spot a loop earlier and a loop later.

**Results.**
- **Stock hard switch (DELAY ↔ NONE):** stays within 38,819 steps (24-bit) of one or the other.
- **Switches between byte-identical Parts (2 → 3 → 4 → 2), and FILTER → LO-FI:** about 0.5 s where T3 matches neither loop, up to about 9 % of full scale.
  - It starts about 50 ms after the switch and ends at the same point in the loop each time.
  - No dropout, no extra click, no loader error.

**Open.** Whether stock does the same is not known. It needs a stock reference (an unmodified OS image, booted from RAM) before it counts as our artifact.

## Where the ColdFire side plugs in (found 15 October 2026)

- **Upload.** The generated owned transport (`resident_driver.py`, `owned_transport`) already has `dl_owned_upload_reserve(core, generation, upload, job)`. That is an owned DL_WRITE whose chunks are read back.
  - Relocate the engine's words on the UI task into a per-core buffer.
  - Upload them with it, then send PLACE as an owned op-10 command: `dl_owned_command_reserve(core, generation, 10, …)`.
  - The transport's validator has to accept PLACE (word 7 = 1). Today it accepts only CAS (word 7 = 0).
- **When to place and free.** `resident-runtime/stock_hook_driver.c`:
  - `mw_hook_driver_begin(feature, …, enable=1)` starts the RESET stream on each core. Place the engine on a core before that core's first RESET chunk, and keep the begin PENDING until PLACE is acknowledged.
  - `mw_hook_driver_retire` disables. Unplace and free only after both cores are disabled and no holder of the feature remains.
- **Region.** In the generated `manager.c`, `allocator.capacity[c]` is set once from `dl_pool_words[c] - DL_CODE_START` at the first probe.
  - Lower it to the lowest placed engine.
  - Dry-run the bank's Part union with `dl_allocator_prepare` then `dl_allocator_cancel` before claiming.
  - Refuse (`RUNTIME_MEMORY`) while live FX code sits in the region, until evacuation exists.
  - The STATUS page and the box after a pick (`status.c`) and `modwerk_dsp_budget` (`dsp.c`) divide by `modwerk_dsp_arena`. They must use the lowered capacity too.
- **Measuring on the unit.**
  - Build: `build_core.py --dsp-loader --usb-midi --usb-audio 'USB AUDIO OUT TRACKS MAIN CUE' --site-events --table-owners sdk/machines/octatrack/module-adapters/table-owners.json --resident-stock-hooks --resident-on-demand --dev`, with the beta base's stock image and upstream.
  - RAM-boot it with `npm run device -- boot DIR`.
  - `octatrack-measure.py` and `octatrack-clicks.py` work on it unchanged.

## Open

- **ColdFire side.** `resident_engines.c`/`.py`: the manager seams (claim, release, dry run, evacuation flag in `place()`), the transport validator for `proc == 1`, and the board seams (place before ENABLE, garbage collection after release).
- **Build wiring.** Done (15 October 2026): `build_core.py --resident-stock-hooks --resident-on-demand` passes every engine this core carries (`resident_dsp.ALLOWED[tag]`) to `place_resident`. It is not in the committed beta base. `build_core.py` is part of the base's source hash, so regenerate the base (`npm run octatrack:base … --write`) before this branch becomes a PR.
- **Native DSP harness.** `sdk/tests/resident_engines_native.cpp` is written but has no Python driver yet.
- **Host tests.** Place, switch, run, disable, unswitch and free; refusal when full; rollback partway through; Part-switch invariants.
- **Arena numbers.** Done: 4,418 / 4,546 words (above).
- **Hardware risks** still to test:
  - Placement uploads while playing should never happen, but the guard has to be shown to hold.
  - The receiver's op-10 frame cost.
  - The first-frame behaviour of an engine at a new address.
  - Analog BD's X tables stay at `$2840` in the DMA block (an existing trap).
