# Beat Slicer

Version: `0.1.1-experimental` · author: @twwwy · **unlisted development draft**.

## Overview

Plans slice starts at beat intervals derived from sample BPM or project BPM.
Category: **system**, because this is a one-shot sample editor operation with
no effect slot or ongoing sequencer clock. The portable C core is implemented
and host-tested. This is **not an installable Octatrack module**: editor,
playback, storage and USB integration are pending.

The grid starts at sample trim start. One beat is a quarter note of the chosen
BPM; track speed and swing do not move offline sample markers. Project BPM is
captured for the operation, not followed live. Later tempo changes must never
automatically rewrite slices.

## Controls

Proposed dialog, not implemented on the instrument:

| Control | Values and behavior |
| --- | --- |
| BPM SOURCE | SAMPLE (default): sample ATTR BPM; PROJECT: project BPM. Show the actual value; refuse missing/invalid BPM. |
| SPACING | 1, 4, 16, 32 or 64 beats (default 1). |
| BOUNDARY | SMOOTH (default): quiet-boundary search in both channels within ±2 ms; EXACT: mathematical beat grid. |
| Preview | Show resulting total, existing/new markers and boundaries needing fades. No sample changes. |
| Apply / Cancel | Explicit confirmation only. Apply remains unavailable until native integration is qualified. |

Existing markers remain exact. In SMOOTH mode, an existing marker within the
search window already covers that beat. Refuse more than 64 total slice starts
rather than truncate the sample or delete old markers. The current core accepts
30–300 BPM in 1/24 BPM units.

## Usage

The target is Octatrack MKII OS 1.40C through the Modwerk base and USB bridge.
MKI operation is a future qualification target.

Proposed access: Flex/Static audio track → AED → LFO (SLICE) → FUNC + YES →
BEAT GRID. Menu integration and this button path are unverified. No stock
gesture or screen is claimed by this draft.

## Quick tutorial

Planned acceptance workflow, unavailable until native integration:

1. In a disposable project, load a copy of a known-tempo sample. Open the
   proposed action and choose SAMPLE or PROJECT BPM.
2. Choose 4 BEATS and SMOOTH. Preview markers and fade warnings. Cancel once
   and confirm the original markers are intact.
3. Apply and audition adjacent/random slices, then exercise confirmed Undo.
   Repeat, save sample settings through stock, save the disposable project and
   reload both; compare complete slice metadata.

## Compatibility and limitations

No native hooks, guessed patch addresses, base changes, runtime subscriptions
or installable packages are included. Compatibility is unproved. See
[INTEGRATION.md](INTEGRATION.md).

Installing the eventual module must do nothing until Apply. Preserve source
audio, trim, loop points, existing slice loop/end metadata, other samples and
project defaults. Sample settings affect every track using that sample; the
dialog must disclose that scope. The core plans starts only and never writes
project or `.ot` files.

**Smooth playback is an acceptance requirement, not a verified result.** Zero
crossings alone cannot prevent clicks in stereo, DC-offset audio, retriggers
or abrupt endings. The core checks both frames bordering each start in both
channels and the last trim frame against a -60 dBFS peak threshold. It flags
unsafe boundaries but does not render or fade playback. Even a quiet boundary
is not a click-free guarantee. The adapter must provide verified playback
fades or refuse unsafe Apply; never overwrite source audio or global AMP
settings to conceal clicks.

## Tests and measurements

Run `python3 -B sdk/drafts/beat-slicer/test_planner.py` from the root. Fourteen
host tests pass, including 250 independent rational grid cases. Integer
arithmetic, no heap and no independent clock.

The local independent audit adds 2,000 randomized grid/marker cases, 200
exhaustive stereo-search cases, threshold/refusal checks and arithmetic
extremes (`test_independent.py`). The pinned ColdFire object compiles without
unresolved runtime helpers and passes the shared code-generation guard.
See [RESEARCH.md](RESEARCH.md) for shared-event and smoothing investigation.

Native cycles, device memory, actual audio and hardware are unmeasured.
[TESTING.md](TESTING.md) separates host results from pending qualification.
`verify.py` deliberately fails publication. This draft is not in
`sdk/catalog.json` and changes no released module or catalogue.

## Authorship and licences

Original MIT core and synthetic tests by twwwy and contributors. No Elektron
firmware, extracted routines/tables, factory samples or dumps. Generated with
the repository scaffold command; inherited placeholder code was removed.

## Screens and audio

No real LCD captures or audio qualification recordings exist. Proposed screen
text is not represented as captured instrument UI.
