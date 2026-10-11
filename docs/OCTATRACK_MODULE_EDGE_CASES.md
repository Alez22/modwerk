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
| 1 | A project names modules that are not installed | The unit says `MISSING <NAME>` for about 1.5 s (often behind stock's LOADING bar at boot; owner: keep it so) and again when a track running it is selected; those slots play dry and keep their knobs. The site reads the MISSING request (0xC1, 14) every 3 s while the unit is idle and says "Your project uses X, which isn't on your Octatrack", with Add to set (or "Load onto Octatrack to bring it back" when the set has it); modules the library does not know are named. | unit: done; site: built, not seen in a browser with the unit |
| 2 | A new base build: the saved set belongs to another build and is not restored | Every module the project names is missing, and the site says so as in 1 | built (as 1) |
| 3 | The restore installs only some modules (`SOME MODULES FAILED`) | The ones the project names show as missing on the site (1); the unit's popup does not name them | built (as 1) |
| 4 | Another project gives a handle to a different module | Two-step rebind: the old module lets go, then the new one takes the handle | built (host test, emulator) |
| 5 | More than 13 different modules in one project | 13 free handles; what the 14th pick does is not tested | open |
| 6 | A module update changes what its knobs mean | The map records a layout number, but nothing converts or warns: stored values are read with the new meaning | open |
| 7 | Updating a module a track plays | Refused as `RUNTIME_IN_USE`, and the site now says why; the user must pick another effect first | done, poor experience |
| 8 | A module removed while a saved or another Part or bank names it | Removal is allowed (only playing tracks hold it). MISSING lists it at once; reloading the Part runs those slots dry (NONE) with their bytes kept, `MISSING EUCLID` shows when the track is selected, and reinstalling restores everything | done |

## Copying and saving

| # | Case | Risk | Status |
|---|---|---|---|
| 9 | Copy and paste of a Part, track or pattern between projects | The handle byte travels, not the module: in the other project it can name another module, or none. The wrong effect plays with the wrong knob meanings | open (owner: not now) |
| 10 | Saving while a module is on trial, then rolling the trial back | The project names a module that is gone: case 1 | built (as 1) |
| 11 | SAVE TO NEW, EXPORT TO SET, a project folder copied on a computer | Whether the `#MODWERK_FX` lines go along is not tested | open |
| 12 | The map in battery RAM and the project file disagree (battery reset, a project saved on another unit) | Which wins is not tested | open |
| 13 | Parameter locks, LFO destinations, scenes and the crossfader on module knobs | Stock keeps the bytes; that they still address the right knob after a reload or rebind is not tested | open |

## Boot and power

| # | Case | Today | Status |
|---|---|---|---|
| 14 | Power lost while the set is being saved | Two files in turn: the older set stays | built (host test) |
| 15 | FUNC held at boot skips the restore | Everything the project names is missing | built, not run on the unit |
| 16 | A real power cycle into a flashed base that restores | Needs a flash with the restore | open |
| 17 | The restore held back past 10 s (playback or USB disk mode right after boot) | Hosts then go ahead, and a late restore could still overwrite a change made before it | open (shortcut in ep0.c) |

## While playing

| # | Case | Status |
|---|---|---|
| 18 | A pattern or bank change, playing, into a Part that names a missing module | open |
| 19 | The arranger switching banks and Parts with modules | open |
| 20 | The self-test while the project names missing modules | open |

## Order

1. ~~Cases 1, 2 and 3~~: built (the site's missing note).
2. Case 7: an update with the same layout swaps in place instead of being refused.
3. Case 6: layout numbers, before the first module update that changes its knobs.
4. Case 9: paste between projects (owner, 11 October 2026: not now).
