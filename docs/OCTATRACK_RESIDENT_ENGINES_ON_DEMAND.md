# Resident controller engines on demand (design, work in progress)

Status, 15 October 2026: the DSP side and the ColdFire side are written and
wired into `build_core.py --resident-stock-hooks --resident-on-demand`, and
host-tested. The ColdFire side places, runs and removes all three engines on
the unit (below). Clearing the region of live FX code (evacuation) is written
and host-tested, not yet run on a unit.

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
| A (core 0) | 2228 | 37 (stubs + 3 base words) | SC 423 (9), Matrix 773 (26, 4 negative), AB 998 (6, 1 negative) | +147 |
| B (core 1) | 1441 | 22 | SC 423 (9), AB 998 (6, 1 negative) | +114 |

Net freed with no controller active: about 2044 words on core 0 and 1305 on
core 1. With only Matrix on demand on core 0, the block is 1456 words and the
receiver grows by 81. Sidechain grew by 35 words on 15 October 2026 (the key
phase change below); the measurements on the unit below were made before it,
with 388. Arena numbers from a full base build are still to be
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
4. **ColdFire side** (`resident-runtime/resident_engines.c`, its build seams in `resident_engines.py`). Written and host-tested.
   - **Region.** Engines take the top of the core's arena, directly under the permanent block. The manager keeps a per-core reserve; the FX allocator's `capacity` is the arena less that reserve, so it stops at the lowest engine. Compaction (`dl_arena`), `dl_move`, the journal's holes and the big-blocks-from-the-top rule all read that capacity.
   - **Holes.** Each engine takes the highest span that meets no other engine (top-down first fit). A removed engine above another one leaves a hole, which the next engine reuses without a new claim.
   - **When a claim can happen.** Only while the manager is idle: no transaction, no queued pick, no open journal, no allocator or buffer transaction. A claim that lowers the capacity first plans where live FX code in the new region would move (below). It then dry-runs the bank's Part union under the lowered capacity (`dl_allocator_prepare` with every slot empty and the union as `keep`, then `dl_allocator_cancel`). The union is the four Parts' firm modules, plus the stock effects they name if those fit before the claim, plus whatever runs now; the region's code counts at its planned new place. If it does not fit, the claim is refused and nothing moves, so a Part switch never has to load code because of an engine.
   - **Admission.** For an incoming trusted controller (`modwerk_controller_admit`), the same claim runs as a dry run for its engine together with every other held or live controller's unplaced engine. It answers `RUNTIME_MEMORY` when there is no room, live FX code in the region has no place below it (or an evacuation already failed on that core this boot), or the union would not fit, and `RUNTIME_CONFLICT` when the feature's engine is stuck for this boot. A busy manager does not refuse: the tick's claim waits, so a boot restore is never refused because the project's effects were still loading.
   - **Clearing the region (evacuation).** Live FX code reaching into the region moves below it before the claim takes it, in one manager transaction of its own (phase 10), the way `dl_move` moves code:
     1. *Plan* (`engine_plan`, on every claim): each package reaching into the region, largest first, gets a new place below it, clear of every live copy (its own old copy included: it runs until its entry is rebound) and of the new places planned before it. Code of a quarter of the lowered arena or more goes top-down from the region, the rest first fit from the bottom, as the allocator places them, so compaction finds nothing to undo. No place: refused (`dl_engine_why` 2).
     2. *Dry run*: the bank's Part union, with that code at its new place, under the lowered capacity (above). Does not fit: refused (3), nothing moved.
     3. *When*: only from the engine's own claim on the board's tick, while the transport is stopped and no pattern change is queued (the placement's own guard), at least 2 s after the last key or knob (`modwerk_status_key_at`), no pick waiting, no self-test or rebind (`modwerk_dsp_moves_idle`, as compaction waits), and the manager idle (no transaction, queued pick, open journal, allocator or buffer transaction). Until then the claim answers "not yet" (7) and the engine waits (`MW_WAIT_EVACUATION`). Never at a Part switch, pattern or bank change, Part reload or project load: those start nothing here, and they press keys.
     4. *Move*: one transaction for every package of that core. The new copies are uploaded first (legacy WRITE, every chunk read back by the receiver) while the old ones run, then each id's dispatch entry is rebound to its new copy (one BIND each, applied between two frames; the slot's state stays in X and Y and init does not rerun, as compaction relies on). Then, in one step, the allocator commits and retires (the old copies become free) and the capacity drops below the region, so neither compaction nor a pick can place code there in between. The engine's claim then takes the reserve the evacuation already lowered and proceeds as before. A Part switch meanwhile waits for it (queued, as behind a compaction move) and then loads nothing.
     5. *Rollback*: a refused or timed-out step (upload or BIND) rebinds every entry the evacuation sent a BIND for back to its old copy (the old copies are still held), each sent again until acknowledged, then frees the new copies (`dl_allocator_cancel`). That core then evacuates nothing more this boot (`dl_engine_why` 8; admission answers `RUNTIME_MEMORY` while live code sits in a region there). A transport that stays busy for 600 attempts counts as a failed step.
     6. *Cost*: nothing on the frame path; one compare in `advance()`; the plan on each claim attempt, the dry runs only when the move may start or for admission. No flash or card writes.
   - **Upload.**
     1. The words are relocated on the UI task into a per-core buffer (`mw_engine_relocate`, linear in words plus relocations), so the frame interrupt scans no relocations: the owned WRITE carries no relocation list.
     2. They are uploaded with an owned `DL_WRITE` at the engine's table offset. The receiver reads every chunk back through P and refuses a chunk whose sum differs.
     3. An owned PLACE follows (op 10, word 7 = 1, word 4 the feature, word 5 the table offset).
     4. Only once PLACE is acknowledged on every required core does the board send its first RESET chunk, then ENABLE. The receiver also refuses to enable a feature whose base word is 0.
   - **When it runs.** From the board's tick only (`controller_board.c`), when a controller generation of the feature is bound and not yet reset. Never at a Part switch, pattern or bank change, Part reload or project load. A placement or an unplacement starts only while the sequencer is stopped and no pattern change is queued (`modwerk_machine_stopped` and the queued bank/pattern bytes, as compaction reads them); otherwise it waits. Nothing new runs in the frame interrupt.
   - **Lifetime.**
     - An engine belongs to its feature, not to one generation. A new generation of the same feature (a replacement, a restore) finds it placed and adopts it without reloading. The code is base data, the same for every generation.
     - An engine is unplaced (PLACE offset 0) and its span freed only when no slot of that feature is held, the board knows the feature is disabled on that core, and the sequencer is quiet. Quarantine holds it for good.
   - **Rollback.**
     - A failed WRITE (no PLACE sent) frees the span. The owned transport has closed that core for the boot, so nothing more is placed there; an engine already placed on the other core stays until no holder is left, then it is unplaced.
     - An uncertain PLACE or UNPLACE keeps the span for the rest of the boot, and admission refuses that feature (`RUNTIME_CONFLICT`).
     - The owned channel's existing fail-closed rule stands.
     - An evacuation's failure: every touched entry back on its old copy before anything is freed, that core closed to evacuation (above).
     - An engine let go while its evacuation runs: the evacuation finishes (moving back would be another move), and the reserve it lowered goes back to the FX code once no held engine on that core is still waiting for it (`mw_engines_collect`).

## Measured on the unit (15 October 2026)

- **Arena.** A private development build with `--resident-on-demand` (base `25ab5804…`, nothing placed) leaves 4,418 words on core 0 and 4,546 on core 1. The beta base `362fb24d…` leaves 2,396 and 3,269.
- **Why it matters.**
  - On #619's development twin, SPRING REV was refused "DSP MEMORY FULL" on T5–T8 of bank A Part 2: core 0 held FILTER plus the PLATE and DARK REV that Part 1 names (2,102 words), so Spring's 1,063 did not fit beside them.
  - On the on-demand build all eight picks loaded beside them, 3,165 words on core 0. Playing: T1-4 62 %, T5-8 67 %, ColdFire 50 %, no loader error.
  - Stock keeps 6,158 words of effect code per core, so a Part with all three reverbs on T5–T8 cannot load on the beta base at all.
- **Runnable since the ColdFire side (below), not yet on a unit.** That build could not run Sidechain, Output Matrix or Analog BD: nothing placed their engines.

## Switch artifacts (first take, 15 October 2026, on the build above)

**Method.** Bank A Part 2's only sounding track (T3) repeats every 4 s bit for bit. Around each switch, the take is compared with the same spot a loop earlier and a loop later.

**Results.**
- **Stock hard switch (DELAY ↔ NONE):** stays within 38,819 steps (24-bit) of one or the other.
- **Switches between byte-identical Parts (2 → 3 → 4 → 2), and FILTER → LO-FI:** about 0.5 s where T3 matches neither loop, up to about 9 % of full scale.
  - It starts about 50 ms after the switch and ends at the same point in the loop each time.
  - No dropout, no extra click, no loader error.

**Resolved (15 October 2026, second session).** The resident base does the same: see the next section. The on-demand build does not cause it; whether stock does it is still unproven (stock has no USB audio to record it with).

## Artifact checks on the unit (15 October 2026)

Method: as above, all 20 USB audio channels as float32, every comparison against the loop before or a take of the same command sequence from a fresh boot (two plays with different histories differ; the recorder's floor is about 5e-7). Twins built from one tree: A resident (`--resident-stock-hooks --dev`), B and C on demand (C with the ColdFire side).

- **Idle, nothing placed (B against A).** Same command sequence from a fresh boot: T3 and MAIN equal within 5e-7. Load equal: ColdFire 49.7 %, core 1 34.6 %, core 0 41.9 %, the same idle passes.
- **Part switches between identical Parts.** Same on A and B: T3 differs from the loop before until its next trig (about 140-900 ms, set by where in the step the switch lands), never above the loop's own peak, no click. With a DELAY on T3 it is an echo of the last 500 ms (the delay becoming audible); without, a small added sound. It looks like the Part's values replacing the current trig's locks until the next trig. Not caused by on demand.
- **DSP code uploads while playing.** Ten picks on silent tracks on both cores while T3 plays (the path an engine placement takes): T3 and MAIN bit-exact on A and on B.
- **Placement (C).** Sidechain Compressor: arena 4,418/4,546 to 4,030/4,158 words, back to 4,418/4,546 on removal, placed again on reinstall; no rejection, error or stall.
- **Placed equals resident.** T5 FX1 COMPRESSOR with KEY T3 and MON ON (T3's key across cores, through both cores' engines): T5 on C equals T5 on A in every sample, once aligned.
- **Key latency per enable (both builds).** T5 lags T3 by 89 samples after one enable, 121 after another, on A as on C: each core seeds its key counter at its own first frame after its own CAS, and the board enables core 0 a tick or more before core 1. So the key was 1 to 4 blocks late, set by the enable offset, and at 4 the reader read the slot being written (about 1 enable in 4).
  - **Fix (15 October 2026, resident engine only, not yet run on the unit).** `resident_dsp.REVIEWED` changes the pinned source for both the resident and the on-demand builds: a core not yet seeded follows the other core's counter at its local track 0 and adopts it for good at its local track 2, half a frame from the other core's advance. Both counters then agree, as when native octabam boots both cores together, and `scdet` keeps reading its own counter, two blocks behind. In the interpreter (both cores, enable offsets −5 to 5, core skews up to 1.5 track slots and one that moves every frame) the key is 2 blocks late every time and never the slot being written. A skew of more than two track slots would make it 1 or 3 blocks, still the same on every enable.
  - **Not chosen: reading the writer's counter at each read.** A reader on its core's first track (T5) races the writer's advance at the writer's first track every frame, so the key jumps between 2 and 3 blocks as the cores' loads shift (XBUS's "rotation read" defect; the test shows it).
  - **MON.** `moncommit` now consumes MON_ON. Before, a COMPRESSOR taken off a track with MON on left that track replaying the last 16-sample key stash until the next RESET (seen in the interpreter, not on the unit).
- **Output Matrix (C, rebuilt twin `43fe3fc4…`).** Placed on core 0 only (state 5 at 3,645, arena 4,418 to 3,645, slot ACTIVE). OUT CFG MATRIX with T3 routed MNL: MAIN L = 0.711853 x (T3 L + T3 R) / 2, MAIN R exact zero, CUE empty, on C as on the resident twin; MAIN L on C equals the resident twin's within 2.4e-7 over a whole loop. No engine job while playing.
- **Analog BD (C).** With the trusted package (`packages/` of the twin build; the recipe capture's own output is not trusted and stays inert), placed on both cores (2,647 and 3,548, minus 998 each), all 3,776 reset words acknowledged per core, slot ACTIVE with both enables. T3 as ANALOG BD plays a clean bass drum: body 51-53 Hz, 95 % of the energy below 150 Hz, no clipping, no DC, no click spikes; no loader error or stall, no engine job while playing. No resident reference: on the resident twin it rendered silence, as in beta finding 24.
- **Fixture.** Loading the project from the card (to recover a bank rejected after T3 was left as ANALOG BD, issue #363's case) replaced the unsaved test fixture; MODWERK-TEST2 is now saved with four trigs on T3 (bank A, 4.000 s loop, bit-exact).
- **All three together (C).** Sidechain, Output Matrix and Analog BD placed (arena 2,259/3,160, as predicted; three slots ACTIVE). While playing: eight switches between identical Parts (3, 4, 1), a pattern change A01 to A02 and back, and a Part reload. T3 and MAIN stayed bit-exact through every Part switch (no deviation at all in this project, which has no locks), the pattern change only changed the content, no click anywhere; no loader packet was sent (accepted counts unchanged) and no engine job started (`jobs` unchanged). Removing all three unplaced all five engine copies, the arena returned to 4,418/4,546 and every slot ended RELEASED with its disables acknowledged.
- **Analog BD on a restored Part (both builds, open, finding 24).** A Part that already names ANALOG BD when the module arrives (a boot, a power cycle) stays silent, even after choosing ANALOG BD again; switching T3 to STATIC and back to ANALOG BD plays the drum. The fault is in how a restored Analog BD track is bound, not in the engine.
- **Silence after a Sidechain enable (both builds, open).** 4 of about 13 enables in a series of RAM boots between different twins without a power cycle silenced every track (exact zeros where the base captures the DSP output, USB stream running, DSPs running, loader clean), until the next boot. Each had a COMPRESSOR with KEY set in the Part. After a power cycle, 0 of 21 enables. T5's monitored copy of T3 was zero too, so T3 is silent before its FX1: the Sidechain DSP code has no path to it (code review), which points at the ColdFire side (renderer, stream) or state left by earlier RAM boots. `snap.sh` snapshots of the renderer slots, running effects and Part are ready for the next occurrence.
- **Test tooling trap.** A development session left running (`device.mjs serve` restart loop) during `device.mjs boot` knocked the unit off USB until a power cycle, twice: stop and verify it before every boot.

## How the ColdFire side plugs in

- **Board.** `controller-policy/controller_board.c`, under `#ifdef MODWERK_RESIDENT_ON_DEMAND` (a default base preprocesses to the same code):
  - Before a bound generation's first RESET, `mw_engines_place` drives the placement on every required core; the slot waits (BOUND) until PLACE is acknowledged everywhere.
  - Each tick drains the engines' own owned jobs first (`mw_engines_poll`) and ends with `mw_engines_collect`, which unplaces and frees what no held slot names.
  - `modwerk_controller_admit` dry-runs the claim for an incoming trusted controller (`mw_engines_admit`).
  - `resident-runtime/stock_hook_driver.c` is not the seam: its enable path is closed in this preparation (`modwerk_stock_hook_begin` refuses every enable), and the board drives the controllers.
- **Transport.** The engines use the generated owned transport (`resident_driver.py`): `dl_owned_upload_reserve` for the WRITE (no relocation list), `dl_owned_command_reserve(core, generation, 10, feature, table offset, 1)` for PLACE and the same with offset 0 to unplace. `resident_engines.transport` lets the validator accept word 7 = 1 only with one feature bit the core carries and an offset of 0 or inside the arena; word 7 = 0 stays the CAS it was, and any other word 7 is refused.
- **Manager.** `resident_engines.manager` adds the reserve, `dl_engine_claim` (the plan and dry run, above), the evacuation (`engine_plan`, `engine_evacuate`, phase 10, handed over by one line in `advance()`), `dl_engine_release` and `modwerk_dsp_arena_now`, and the first probe sets the capacity to the arena less the reserve. `dl_engine_claim`'s `commit`: 0 dry run, 1 take it but let live code in the region wait, 2 take it and move that code first.
- **dsp.c.** `resident_engines.dsp` adds `modwerk_dsp_moves_idle` (no self-test, rebind or waiting pick) for the evacuation's wait.
- **Status.** The STATUS page, the box after a pick (`modwerk_dsp_budget`) and the host's ARENA word read `modwerk_dsp_arena_now`, the arena less the engines. Admission's own size check and the descriptor check keep the build's arena.
- **Data.** `resident-engines-data.c` (generated by `resident_engines.data_c`) holds each core's engine units, three bytes a word, their relocations, and a buffer per core sized to its largest engine. `data_c` refuses a unit whose words do not match its SHA-256 or whose relocations are out of order.
- **Diagnostics.** On a development base (`--dev`), `mw_engines_view` ("MWEV", 180 bytes in initialized data, so inside the dev MEM window; layout in `resident_engines.h`) is refreshed every board tick: per core and feature the engine's state (0 free, 1 claimed, 2 writing, 3 written, 4 placing, 5 placed, 6 unplacing, 7 stuck), its arena offset and why it waits (1 own job in flight, 2 the board's job, 3 playing or a pattern queued, 4 no room, 5 manager busy, 6 claim refused, 7 transport busy, 8 stuck, 9 an evacuation runs or waits); the arena and reserve per core; the last admission verdict per feature (1 fits, 2 memory, 3 stuck); the last claim's reason per core (`dl_engine_why`: 1 manager busy, 2 live FX code in the region with no place below it, 3 Part union, 4 inconclusive, 5 too large, 6 an evacuation started or runs, 7 an evacuation waits for 2 s without a key or a waiting pick, 8 an evacuation failed on this core); byte 42 the evacuation (step 1 upload, 2 bind, 3 rebinding the old copies, | core << 2, | cores closed to it << 4) and byte 43 evacuations done (low nibble) and failed (high), mod 16; the counters; and each controller slot's module, generation, state, ACKs and reset words. Its MEM window also reaches the base's statics up to 0x46000000. A default or beta base has none of it.
- **Install the rows' packages.** A trusted controller is the exact package its trust row names. On the first twin, Analog BD was installed from the recipe-capture run (built without the recipe applied): the base took it as an ordinary package, never bound it, and nothing placed (board test mode 11). The twin build now copies the three trusted packages beside the base (`packages/`) and deletes the capture run's output.
- **Measuring on the unit.**
  - Build: `build_core.py --dsp-loader --usb-midi --usb-audio 'USB AUDIO OUT TRACKS MAIN CUE' --site-events --table-owners sdk/machines/octatrack/module-adapters/table-owners.json --resident-stock-hooks --resident-on-demand --dev`, with the beta base's stock image and upstream. Then recapture Analog BD's recipe against that build's symbols into a scratch copy of the tree (below), build the controller rows (`base_bound.py rows`) and the base again with `--controller-policies` and `--controller-layout`.
  - RAM-boot it with `npm run device -- boot DIR`.
  - `octatrack-measure.py` and `octatrack-clicks.py` work on it unchanged.

## Checked in software (15 October 2026)

- **Host, ColdFire side** (`sdk/tests/test_resident_engines_board.py`, ASan/UBSan): the actual board, loader, generated manager and generated owned transport against a modelled receiver and made-up engine units. Place, switch on, run, switch off, unplace and free; the order WRITE, PLACE, RESET, ENABLE on each core and disable before unplace; the playing guard (no job while playing, none for an unplace either); a full core refused at admission; live FX code in the region refused until it is gone, and a later pick loading below the engines; the bank's Part union refused when it would no longer fit; a WRITE refused part way (that core's span freed, the other core placed, nothing enabled, then unplaced at removal); an uncertain PLACE (span kept, the feature refused afterwards); twelve Part switches starting no engine job, changing no reserve or capacity and loading no code; a successor adopting the placed engine with no new job; hole reuse; Output Matrix on core A only. The C relocator against `resident_dsp.relocate` at eight bases, edge words included.
- **Host, evacuation** (the same test, modes 12-21; its receiver model keeps a dispatch table and checks after every frame that each slot runs its id's whole, correct code from where the manager holds it, never a stub, freed or half-written words):
  - a 900-word effect at the top of core A's arena: admitted, moved below the region (to 136, clear of its old copy), new copy whole before its one BIND, the engine's first word after it, then placed and ACTIVE; the old copy's freed words overwritten afterwards with no effect on the slot; removal gives the capacity back and the effect stays;
  - while playing, within 2 s of a key, with a pick waiting, and playing again: nothing moves (core B, which needs no move, places at once); stopped and settled: moved, placed;
  - the bank's Part union not fitting even after the move (a Part naming a 700-word module; and a 600-word one that would fit under the engine from scratch but not beside the moved effect): refused at admission and on the tick, nothing moved; without it, moved and placed;
  - code with no place below the region (1,000 words at the top, 400 at the bottom): refused, nothing moved;
  - the new copy's upload refused part way: no BIND sent, old copy running, claim refused, that core closed to evacuation (Output Matrix then refused too); once the effect is gone the claim proceeds without a move;
  - two packages in the region moved in one transaction (both uploads before either BIND); a Part switch during it waits and loads nothing; twelve Part switches afterwards start no job and no move;
  - the second BIND refused, or applied but never answered (the transport times out): both entries back on their old copies (one of those BINDs refused once and sent again), new copies freed, claim refused, nothing of the engine on core A;
  - both cores, one evacuation each; Sidechain let go mid-move: the move finishes, the reserve comes back.
  - Mutation check (scratch, not committed): each of 14 mutants of the guards is caught by a mode: no 2 s/pick wait, a claim while playing, no reverse on failure, touched only once acknowledged, the capacity left high, old copies freed without the BINDs, the union dry run with the code where it was, a failed core evacuating again, a new copy allowed over its own old copy, an orphaned reserve kept, a claim over live code without moving it, the region test missing code that reaches into it, a failed forward step taken as done, a way back that did not land given up.
- **DSP side** (`sdk/tests/test_resident_engines.py`, in the modwerk-source-tools image; its interpreter is not the chip):
  - The real units (423, 773 and 998 words) relocated three ways agree word for word at ten arena bases: a fresh assembly at the base, `resident_dsp.relocate`, and the base's C relocator over `data_c`'s data.
  - `resident_engines_native.cpp` runs the on-demand receiver: it refuses an enable before PLACE, a second PLACE and an unplace while enabled, and its base word names the placed engine. Each stub then runs the engine placed at the arena's top and lower down, against the resident build's stub, from the same X/Y memory and registers: X, Y, the data ALU registers and the instruction counts are equal; an address register differs only where it holds a P address in the engine.
  - Each stub runs twice: from filled memory (mostly the early return), then from the feature's reset state steered down its working path. Output Matrix's mix and phones paths (188 and 22 instructions, until they leave for stock code) and Analog BD's source on core B (167) ran there. On core A, Analog BD's voice block pointer from that synthetic record lands at X:$f598xx, which the interpreter has no memory for (both builds fault there), so its first 160 instructions are compared. Sidechain's entries ran 30, 18 and 11 interpreter steps in both scenarios (a DO loop counts as one step), so how far into its detector the steered state reached is not shown.
  - Sidechain's key phase on two cores (each its own P/X/Y, their shared windows one memory, whole hook calls interleaved as the dispatcher orders them): the changed engine keys T5 from T3 and T1 from T6 two blocks late for every enable offset and skew above; upstream's delay follows the offset and reads the slot being written at an offset of 2 mod 4; a reader of the writer's counter jumps between 2 and 3 blocks under a moving skew. MON ends with its COMPRESSOR. The changed instructions disassemble as written, and each is a form upstream's code already uses.
- **Default builds unchanged.** A base built without `--resident-on-demand` links to the same bytes as before this slice, but for the identity fields (`modwerk_base_digest`, `olog_build`, `olog_configuration`, `olog_source`): checked on the resident development twin, the resident beta configuration (with and without controller rows) and the plain DSP-loader base. `controller_board.c`'s text changed, its object did not.
- **Default builds unchanged by the evacuation** (same method as above, twins built from the commit before and after it): the resident development twin and the resident beta configuration, each with and without controller rows, and the plain DSP-loader base link to the same bytes but for the identity fields; `controller_board.c`'s text changed, its object did not; the plain base's sources are all identical.
- **Analog BD's recipe.** The on-demand base moves the write-lease entries Analog BD's package calls, so its reviewed hash recipe (`machine-recipes.json` imageSha256) has to be recaptured from the stock OS for any base that ships this, as for every base change that moves them (`OCTATRACK_BETA_TEST_PLAN.md`, finding 17). A development twin recaptures it privately (`build.py --capture-stock-recipe`).

## Evacuation: the on-unit test

Not yet run. Twin: `~/.cache/modwerk-local/ot/eod/ev/C-dev` (private, configuration `efbe190c…`), the rows' three trusted packages beside it in `packages/`; Analog BD's recipe recaptured for it as before. Arena with nothing placed: 4,418 words on core A, 4,546 on core B.

**Why Output Matrix first.** With nothing placed no stock effect is a quarter of core A's arena (SPRING REV 1,063 and DARK REV 1,067 words are under 1,105), so they load from the bottom. With Output Matrix placed (773 words, core A's arena 3,645), SPRING REV is a quarter or more and the allocator puts it at the top, where Sidechain's engine then goes.

**Steps** (stopped, a scratch project whose bank A runs nothing but FILTER/DELAY on T5–T8; the diagnostics addresses are this twin's):

1. RAM-boot the twin; `loader` for the baseline counters.
2. `try …/packages/output-matrix.mwrm`. View (`mem:0x40ac85e0:44`): core A Output Matrix state 5 at offset 3,645, arena 3,645.
3. `pick:T5:FX2:SPRING_REV`. `mem:0x40d0a634:6` (the allocator's live record of id 21 on core A: offset, words, present) reads `0a16 0427 01`: 2,582, 1,063 words, at the top.
4. Make T5 sound through it while stopped (best a steady tone into a THRU machine on T5, else a hit with SPRING's decay up and its tail ringing), record the 20 USB channels, then press no key for at least 2 s.
5. `try …/packages/sidechain-compressor.mwrm` (refused with `RUNTIME_MEMORY` on the previous twin). Within about a second: view byte 42 goes 1 (upload) and 2 (bind) back to 0, byte 43 reads 1; `mem:0x40d09b58:14` (failures, moves, evacuations, then `dl_engine_why` per core) reads 0, 1, 1; `mem:0x40d0a634:6` reads `05ef 0427 01` (moved to 1,519). Then Sidechain as before: core A state 5 at 3,257, arena 3,257, reserve 1,161; core B at 4,158; slot ACTIVE.
6. `loader`: no rejected packet, no error, no rollback; one more commit.

**Listening.** On T5 (and MAIN), around step 5. Pass: the tone or tail carries on with no step, spike or gap; `octatrack-clicks.py` finds nothing there that is absent from a take of the same sequence without step 5. An artifact would be:
- a click: a one- to few-sample step or spike at the BIND;
- a dropout: a frame or more of T5 dry (the dry stub) or silent;
- distortion: noise or a burst from code running from wrong words, possibly followed by a DSP stall (frames stop, the sequencer sticks, silence until a power cycle; `report` shows it).

The move itself is `dl_move`'s mechanism (upload beside the running copy, one BIND), the one compaction uses while playing and `octatrack-movelisten.py` listens to; this test is for the evacuation's own transaction, which runs only while stopped.

**Guards.**
- PLAY before step 5: nothing moves or places (view wait 3, byte 42 stays 0, id 21 stays at 2,582); STOP, and two seconds later it moves and places.
- STOP, then a key every second: no move until two seconds after the last.
- Placed: Part switches, a pattern change and a Part reload while playing send no WRITE or BIND (`loader` counts, `dl_engine_moves` unchanged).
- Removal: `remove` Sidechain; arena back to 3,645, SPRING REV stays at 1,519.

## Open

- **Evacuation on the unit.** Written and host-tested (above), not yet run on hardware; the test is above ("Evacuation: the on-unit test"). Still unproven there: that the move is inaudible while an effect rings (no click, dropout or distortion on its track), its frame cost, and that the boot restore of a project whose bank holds big effects now comes up without "SOME MODULES FAILED" (that failure was inferred, never seen).
- **`dl_move`'s rollback (found while writing the evacuation, all bases, not changed here).** If a compaction move's upload or BIND fails, `advance()` rolls back through phase 7, which sends BYPASS for every id whose target differs from its live place: the moved effect, still running, would go to the dry stub (silent) while the allocator keeps it live at its old place, until its id changes. Inferred from the code, not seen on a unit; the evacuation does not use that path (it rebinds to the old copy). A default base must stay byte-identical in this slice, so the fix belongs in its own change.
- **Legacy jobs beside owned jobs (inferred, all resident bases).** While the board's owned RESET or CAS job (or an engine's WRITE or PLACE) holds a core, `dl_job_status` answers -2 for that core, which `advance()` takes as "the transport refused" and rolls the selection back (`DL_SELECT_UNAVAILABLE`). A Part switch that needs an upload during an engine placement or a controller reset could therefore fail. The evacuation instead retries a refused start. Not seen on a unit.
- **Hardware.** Sidechain's install, activation, removal and reinstall ran on a unit (above). Still to run:
  - that no Part switch, pattern change or reload starts an engine job with an engine placed (`mw_engines_jobs` sits outside the development MEM window; use the loader's accepted counts) and that switching still sounds as on the resident base;
  - the silence after a Sidechain enable (above), on the resident base first: it is not on-demand's, but it blocks calling Sidechain artifact-free;
  - the receiver's op-10 frame cost, and the first-frame behaviour of an engine at a new address;
  - the key phase change: T5 against T3 (KEY T3, MON ON) must lag by the same number of samples over repeated removals and reinstalls;
  - Analog BD's X tables stay at `$2840` in the DMA block (an existing trap).
- **Beta base.** `build_core.py` and the resident sources are part of the base's source hash, so regenerate the base (`npm run octatrack:base … --write`) and recapture Analog BD's recipe before this branch ships an on-demand base. The committed beta base is not on-demand.
- **Arena numbers.** Done: 4,418 / 4,546 words with nothing placed (above); with all three placed, core A keeps 2,259 and core B 3,160 (measured with Sidechain at 388 words; at 423, 2,224 and 3,125 by arithmetic).
