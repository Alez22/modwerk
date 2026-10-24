# Beat Slicer

Version: `0.1.37-experimental` · author: @twwwy · **unlisted development draft**.

## Overview

Beat Slicer plans slice starts at beat intervals derived from sample BPM or
project BPM. It is a one-shot sample-editor operation, with no effect slot or
independent sequencer clock. A private full-boot Octatrack emulator fixture now
exercises the stock-menu entry, controls and read-only previews. This is **not
an installable module**: production source admission, editor/loader lifecycle,
Apply/playback and browser/USB integration remain unfinished.

The grid starts at sample trim start. One beat is a quarter note of the chosen
BPM; track speed and swing do not move offline sample markers. Project BPM is
captured for the operation. Later tempo changes must never rewrite slices
automatically. The current core accepts 30–300 BPM in 1/24-BPM units.

## Controls

The private native fixture exercises these read-only controls:

| Control | Values and behavior |
| --- | --- |
| BPM SOURCE | SAMPLE (default): sample ATTR BPM; PROJECT: captured runtime project tempo. Refuse missing or invalid BPM. External-clock and pattern-tempo behavior remain unqualified. |
| SPACING | 1, 4, 16, 32 or 64 beats; default 1. |
| BOUNDARY | SMOOTH (default): search both stereo channels within ±2 ms for a quiet boundary; EXACT: mathematical beat grid. Neither guarantees click-free playback. |
| Preview | Show captured tempo, total/existing/new markers and fade warnings. No sample changes. |
| BACK / NO | Leave the private preview without changing markers. Reopening preserves options and issues fresh request/selection identities. |

Confirm/Apply remains planned and unavailable. It must follow the stock slicing
workflow, committing the exact prepared candidate once. Afterwards, use stock
DELETE SLICE or DELETE ALL SLICES. No Beat Slicer Undo action or separate history
dialog is planned. Clearing removes markers; it does not restore a previous
layout. Internal rollback remains necessary for failed publication.

At stock's grid zero-cross question, NO accepts unaligned slices rather than
cancelling. The normal stock workflow and the resident contribution are tested
separately and together in private emulator boots; physical comparison remains
open.

## Usage

Target: Octatrack MKII OS 1.40C through the Modwerk base and USB bridge. MKI is a
future qualification target.

Proposed access, exercised privately: Flex/Static audio track → AED → AMP
(SLICE) → YES → BEAT GRID. The current native source fixture reads Flex;
Static streaming is not implemented. No stock gesture or screen is claimed by
this unlisted draft, and no Beat Slicer package is installed on the instrument.

## Planned acceptance tutorial

These steps describe the intended finished module, not currently available
firmware behavior:

1. In a disposable project, load a copy of a known-tempo sample. Open Beat Grid
   and choose SAMPLE or PROJECT BPM, then 4 BEATS and SMOOTH.
2. Preview marker counts and fade warnings. Back out once and verify the original
   markers remain intact. Reopen and preview again.
3. Once native Apply and playback policy are qualified, confirm the exact plan
   and audition adjacent/random slices. Use stock DELETE SLICE and DELETE ALL
   SLICES; verify that clearing changes markers without changing audio.
4. Create another grid, save sample settings through stock, save the disposable
   project and reload both. Compare complete slice records and qualify a physical
   reboot on the exact installed build.

## Preservation and compatibility

Existing start, end and loop records, including their ordinals, must survive
unchanged. The portable candidate builder uses a conservative **preserve
ordinals or refuse** policy because stock sorts records by start: adding an
earlier marker can renumber a pattern's slice locks. That restriction still
requires owner review before release. Refuse more than 64 total starts rather
than truncating the sample or deleting old markers.

Installing the eventual module must not alter a sample. Preserve audio, trim,
loop points, other slots and project defaults. Slice settings belong to the
sample slot and affect tracks using that slot; the finished dialog must disclose
that scope. The planner never writes project or `.ot` files.

**Smooth playback remains an acceptance requirement.** Quiet boundaries cannot
prevent every click in stereo, DC-offset material, retriggers or abrupt endings.
The planner checks both sides of each start and the final trim frame against a
−60 dBFS peak threshold and flags boundaries needing fades. It does not implement
playback fades. Until a verified native playback policy exists, unsafe Apply
must be refused. Do not fade source audio destructively or change AMP defaults
to conceal clicks.

No production hook, event number, loader registry or installable package is
added by these prototypes. Private stock sites are bound to an exact local
firmware hash; they are not an exported ABI. Common-companion placement,
installation orders, full module-set lifecycle and physical headroom remain
unqualified. See [integration requirements](INTEGRATION.md).

## Current implementation and evidence

The portable planner, staged PCM reader, preview guard/session, marker
candidate and transaction coordinator have host and compiled ColdFire tests.
The transaction's failed-write rollback remains internal; its older explicit
Undo API is retained research, not the planned player workflow.

The [Flex source backend](FLEX_SOURCE.md) composes complete metadata capture and
bounded copied PCM reads. [Full-boot source tests](BOOT_SOURCE.md) exercise real
stock-loaded PCM and invalidation by normal edits. Ownership and admission remain
fixture-controlled. Stock counters and dirty flags do not cover every writer;
see [writer coverage](WRITER_COVERAGE.md).

The [copied UI/engine exchange](PREVIEW_ASYNC.md) gives one engine consumer
ownership of the mutable session. UI callbacks submit tagged intents and read
copied results. The private native budget is one work call per engine callback:
up to eight owned reader transitions and one revalidated live copy, plus optional
setup/publication. Long-source and synthetic cost probes measure total work and
the longest callback separately. Instructions and emulated elapsed time are not
hardware cycles, physical latency or audible-headroom measurements.

[Native UI fixtures](NATIVE_UI.md) cover both stock menu layouts, all control
combinations, waiting cancellation and owner retirement. The
[selection-context guard](SELECTION_CONTEXT.md) binds each callback to the actual
captured task/table/row/callback/owner/epoch. Separate original-versus-wrapped
stock-dispatch probes check registers, SR, stack and caller-visible effects.

The [resident-menu variant](RESIDENT_MENU.md) supports repeated openings using
two immutable, pinned layouts. A separate 90 BPM run verifies captured project tempo against the unchanged
sample tempo. Normal stock grid creation/clearing can change
between those layouts in one session. It preserves options and advances UI and
request identities. Retiring the fixed owner withdraws the contribution, but
its tables remain pinned; replacement and memory reclamation are not implemented.

The [runtime-owner helper](MENU_OWNER.md) distinguishes current publication from
intact images retained for staging or rollback. Tests use the actual loader on the host and as compiled ColdFire code with
synthetic machine services. Production transition-time retirement and typed
contribution admission remain separate work.

The [full-owner menu backend](MENU_OWNER_BACKEND.md) now connects those leases
to the compositor through copied action allowlists and a trusted base dispatcher.
Its host tests cover coexisting owners and actual loader transitions. Newer
ColdFire execution links the actual SDK loader; machine services and menu
models remain synthetic. It does not admit packages,
resolve module entry points or install native transition hooks.

The isolated loader fixture also executes the real upload controller and whole-set
backend through replacement/removal, disconnect at every two-row publication
boundary and complete-set acceptance. An unchanged companion stays usable,
while retired activations require fresh admission even after restoration. This
uses explicit test-side retirement, synthetic machine services and no USB IO.

Recorder-stop research now follows the actual queued cleanup command after
shortages and length-limited stops, including two independently queued recorders.
The compiled worker observer covers each command’s
map-tail stores and retires before an unmasked queue wait. These isolated tests
retain synthetic active state; they do not enable a live source provider.

[Stock observations](BOOT_OBSERVATION.md) also cover normal slicing, clearing,
sample-settings saving and project reloads on disposable fixtures. A fresh
emulator process does not prove physical reboot persistence. Exact results,
source revisions, counters and remaining limits are in [TESTING.md](TESTING.md).

Run `python3 -B sdk/drafts/beat-slicer/audit_evidence.py` to verify retained report
source bindings. It neither reruns binaries nor qualifies hardware. `verify.py`
deliberately refuses publication; the draft is absent from `sdk/catalog.json`
and changes no released download.

## Screens, audio and authorship

Private emulator LCD dumps verify the exercised native layouts; they are not
physical-unit captures or published module media. No audio or hardware
qualification is claimed.

Original MIT core, helpers and test extensions by twwwy and contributors. The
runtime-owner host test includes the repository's unchanged GPL loader fixture;
its licence and attribution remain in the original files, and the combined test
binary is not published. No Elektron firmware, extracted routines/tables,
factory samples, memory dumps or built firmware images are committed.
