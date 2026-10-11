# Octatrack module edge cases

Owner and Claude, 11 October 2026, after the persistence run on a scratch project. What can go wrong when
modules, projects, Parts and the base meet, what the base does today, and what is proven. Status: **done**
(proven on the unit), **built** (code exists, not proven on the unit), **open** (not built or not tested).

Persistence run (LIVE/MODWERK-TEST, S44: E-Verb on T1 and T5 FX2, Euclid on T3 and T7 FX1, TapeHead on
T2 FX1, each with its own knobs; `scripts/octatrack-persist.py`): a Part reload (the `reload` step: the old
PART+FUNC+PLAY recipe clears the Part), a project reload and a RAM boot each brought back every assignment,
every knob and both Part copies exactly. Euclid removed while only the saved Part named it: MISSING listed it,
the unit said `MISSING EUCLID`, both slots ran dry (NONE) with every stored byte kept, and reinstalling it
brought back the baseline exactly. Not yet: another project and back, a real power cycle.

## Projects and the installed modules

| # | Case | Today | Status |
|---|---|---|---|
| 1 | A project names modules that are not installed | The unit opens MISSING MODULES (status.c, owner: a list to close, not a popup): every module the project names in any bank or Part that is not installed, UP and DOWN to scroll, YES or NO to close; it opens when the list gains one and has held still for half a second, once the boot's restore is over, and closes itself when nothing is missing. Selecting a track running one still says `MISSING <NAME>` briefly. Those slots play dry and keep their knobs. The site reads the same list every 3 s while the unit is idle and offers Add to set, or says a load brings them back. | unit: done (S45); site: built, not seen in a browser with the unit |
| 2 | A new base build: the saved set belongs to another build and is not restored | The page lists every module the project names (S45: E-Verb, Euclid, TapeHead); reinstalling them brought back every assignment, knob and both Part copies | done (unit) |
| 3 | The restore installs only some modules (`SOME MODULES FAILED`) | The ones the project names show as missing on the site (1); the unit's popup does not name them | built (as 1) |
| 4 | Another project gives a handle to a different module | Two-step rebind: the old module lets go, then the new one takes the handle. On the unit: MODWERK-TEST, then a second scratch project with E-Verb on another track, then back: identical to the baseline (both projects used the catalogue handles, so no handle actually moved) | built (host test, emulator); switch and back done |
| 5 | More than 13 different modules in one project | 13 free handles; the 14th is refused as FULL (host test `test_dsp.c`) and the site says the Octatrack has no room for another module. Too few for configurations of ~90 modules: see 21 | built (host test) |
| 6 | A module update changes what its knobs mean | The map records a layout number, but nothing converts or warns. Detecting it needs `modwerk_fxmap_assign`: a module taking a handle overwrites the project's map entry with its own layout at once, so the mismatch has to be caught there (old layout against new) before it is lost; a project loaded over an installed module keeps the project's layout and could be compared later. No module has layout 2 yet | open (design noted) |
| 7 | Updating a module a track plays | Refused as `RUNTIME_IN_USE`, and the site now says why; the user must pick another effect first | done, poor experience |
| 8 | A module removed while a saved or another Part or bank names it | Removal is allowed (only playing tracks hold it). MISSING lists it at once; reloading the Part runs those slots dry (NONE) with their bytes kept, `MISSING EUCLID` shows when the track is selected, and reinstalling restores everything | done |

## Copying and saving

| # | Case | Risk | Status |
|---|---|---|---|
| 9 | Copy and paste of a Part, track or pattern between projects | The handle byte travels, not the module: in the other project it can name another module, or none. The wrong effect plays with the wrong knob meanings | open (owner: not now) |
| 10 | Saving while a module is on trial, then rolling the trial back | The project names a module that is gone: case 1 | built (as 1) |
| 11 | SAVE TO NEW, EXPORT TO SET, a project folder copied on a computer | Whether the `#MODWERK_FX` lines go along is not tested | open |
| 12 | The map in battery RAM and the project file disagree (battery reset, a project saved on another unit) | Which wins is not tested | open |
| 13 | Parameter locks, LFO destinations, scenes and the crossfader on module knobs | A parameter lock on E-Verb's SIZE (A01, T1, step 1) came back byte for byte after a RAM boot and the restore (the pattern's 36,568 bytes); LFO setups and scenes live in the Part, which came back byte for byte too | done (bytes); not listened to |

## Boot and power

| # | Case | Today | Status |
|---|---|---|---|
| 14 | Power lost while the set is being saved | Two files in turn: the older set stays | built (host test) |
| 15 | FUNC held at boot skips the restore | Everything the project names is missing | built, not run on the unit |
| 16 | A real power cycle into a flashed base that restores | Needs a flash with the restore | open |
| 17 | The restore held back past 10 s (playback or USB disk mode right after boot) | Hosts then go ahead, and a late restore could still overwrite a change made before it. Installs need the transport stopped, so this needs the card unavailable or USB disk mode for 10 s after boot while installing | open (rare; shortcut in ep0.c) |

## While playing

| # | Case | Status |
|---|---|---|
| 18 | A pattern or bank change, playing, into a Part that names a missing module | Playing A01 (Part 1), queued A02 (Part 2 names the removed Air Chorus on T4): T4 took Part 2's effect at its trig and ran dry (NONE), frames went on, no stall | done |
| 19 | The arranger switching banks and Parts with modules | open |
| 20 | The self-test while the project names missing modules | Passed: 3/3 intact and ran, peaks and frames fine, card set saved | done |

## The effect list

| # | Case | Today | Status |
|---|---|---|---|
| 21 | More module effects than the list holds (owner, 11 October 2026: "I just want a longer list than 32 entries"; categories in the choosers: not now) | The chooser itself scrolls any length (stock's 7 is only its viewport, build_bus.py CHOOSER_ROWS); the 32 is the base's lists and the 32 effect ids, of which stock keeps 19. Owner: more than 13 different module effects at once are needed, so ids handed out on pick are not enough; the DSP dispatch and stock's per-id tables have to grow, or one id has to dispatch to a second-level table. Research under way | open (design) |

## Loading and memory, measured (11 October 2026, S47/S48, `scripts/octatrack-loadbench.py`, `memory`)

- **Speed.** Every pick, module or stock, ran 114-123 ms after YES whether it moved 0 or 68 packets (E-Verb's
  1,588 words): the time is the key hold and the tool's polling, not the load. The longest gap between two audio
  frames during loads was 403-420 us, the same as idle (420 us; a frame is about 363 us). A Part switch with
  modules preloaded sent no packet, and five idle seconds sent none.
- **Code leaves a core when no working Part names it**, so a second pick sends the same packets again (Mini Verb
  24, E-Verb 68); that costs nothing measurable. Modules a working Part names stay loaded (Air Chorus, named by
  Part 2, came free on core 1).
- **Packing.** Fresh, each core's code sits packed from the arena's start with no holes (core 1: 3,641 of 5,075
  words in five blocks). The allocator places first-fit and never moves live code: taking E-Verb off T1 left a
  1,588-word hole, and Mini Verb (532) then filled its start, leaving a 1,056-word hole (2,490 free, the largest
  run 1,434). A placement that fits the free words but not one run is refused as memory
  (`DL_ALLOC_TRANSITION`) after the base lets go of what it holds; live code is never moved. On the unit the
  cycle ledger refused first: E-Verb on T4 was refused for cycles (manager result -2) with core 1's code
  memory 51 % used.
- **Holes now close by moving code (S51).** A block moves into a hole the way a copying collector moves an object:
  its new copy is uploaded while the old one runs, the dispatch entry is bound to it at a frame, and the old copy
  is freed (`dl_move` in manager.c and `dl_allocator_move`, build_core.py's edits; the planner in dsp.c). A slot's
  state lives in X and Y and stock reruns init only when the id changes, so the effect never goes dry. One move at
  a time, when the manager is idle and two seconds after the last key, playing or not. On the unit: a 532-word hole
  closed in 4 moves and 507 ms (about 125 ms a move); playing, a 422-word hole closed by itself within 5 s with
  Euclid running on T3 throughout; frame gaps 408-415 us, no errors, stalls or rollbacks. Not listened to: an audio
  check (a sample through a moving module, MAIN recorded) is still to do. A first version silenced every module
  slot and reloaded (373-425 ms, stopped only); it is gone.
- **The module pool** (256 KB) held six modules in 26 KB with no hole; removing Euclid from the middle and
  installing it again left none (first fit at the lowest address; nothing moves).

## Order

1. ~~Cases 1, 2 and 3~~: done (the unit's page, the site's note).
2. Case 21: more than 13 module effects at once and a list longer than 32 (owner's priority; design first).
3. Case 7: an update with the same layout swaps in place instead of being refused (design first: the DSP
   manager must retire the old code from the slots running it before the new code binds, as the rebind does).
4. Case 6: layout numbers, before the first module update that changes its knobs.
5. Needing the owner at the unit: 15 (FUNC held at boot), 16 (a power cycle into a flashed base that restores),
   11 (SAVE TO NEW, EXPORT TO SET: read project.work in USB disk mode), 19 (the arranger), the site's note in a
   browser.
6. Case 9: paste between projects (owner, 11 October 2026: not now).
