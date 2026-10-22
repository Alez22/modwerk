# Beat Slicer integration investigation

Local investigation, 23 October 2026. This is an unlisted draft, not a release
or a request to operate the instrument. No firmware addresses are proposed
for patching. No module, project, sample or missing-module reference was
changed on the device.

## Sources and duplicate check

- Modwerk main `610a934da51b8f8518e6296493da9059b83e9a7e` matched this checkout
  at inspection. Its seven open PRs were #790, #776, #775, #676, #564, #560
  and #555; none implements the Octatrack slice editor. The contributor fork
  had no open PRs. PR #775 is a useful example of a shared menu table, but
  concerns MIDI generators and is not a dependency.
- Pinned Octabam tooling is `8250be0c23ca0a0a953cb7e5721e3bdb98dadfe5`.
  Current upstream main was fetched and inspected at
  `ff9c5f846928cc84d69a7e559fae4b8abb0c6b4f`, without moving the pin or
  replacing Modwerk's preserved SDK. The cache retains only the tooling
  command's reviewed `usb_probe.py` and `rec.swift` repairs.
- [Octabam PR #858](https://github.com/sambanks/octabam/pull/858), head
  `c788fda0472a93961149e2d0199ec5c3f09640dd`, proposes EDIT EVENTS for held
  trig edits and pattern/track pre-copy notifications. It supplies neither
  sample-editor transactions nor sample playback smoothing. Do not depend
  on its separate module. Other open PRs were #860, #859, #854, #851, #846,
  #824 and #805.
- The local Octatrack catalogue/drafts contain no equivalent beat slicer.
  Digitakt DIGISLICER is a different machine/platform and storage design;
  its implementation is not an Octatrack ABI. No code was copied from it.
- Elekloader tools are pinned at `7b5b5b8` (kit 0.6.0), as required by the
  repository. These tool checkouts are outside Git.

## What the shared interfaces actually provide

Read `sdk/machines/octatrack/events.json`, generated `EVENTS.md` and
`include/modwerk_events.h` at the Modwerk revision above.

| Interface | Existing contract | Why it is insufficient |
| --- | --- | --- |
| `ev_play_increment` | Modify playback increment when stock recomputes it | Not a PCM renderer or a reliable per-boundary notification; never scan PCM here |
| `ev_voice_bind` / `ev_voice_bind_run` | Before stock resets/binds a track voice | No outgoing audio, slice identity, endpoint or crossfade state; cannot establish declick coverage |
| `ot_machines` | Machine rows, pages and source renderer ownership | Beat Slicer is an editor action, not a replacement machine |
| `ot_sequencer_rows` | Shared project sequencer menu rows | Not the audio editor menu or sample transaction service |
| Project load/line/write events | Project settings serialization seams | Not the stock sample-settings/marker save path |
| `dsp_track_source` | Exclusive source hook, feature 4 for Analog BD | Not a general sample boundary hook; Beat Slicer cannot claim Analog BD's owner/site |

The source registry ends at event 30. Do not reserve 31 speculatively: another
reviewed base change may append first. DSP site numbers are a separate ABI.
ABI 10 package-carried engines do not by themselves grant arbitrary DSP hooks
to a new module; current admission still binds the packaged feature to its
reviewed controller and source site.

## Offline stock analysis

The user's BIN was recognized by Elekloader as original Octatrack 1.40C:

- Container SHA-256: `34695b606eb00e1b4dded5fd0c4b66f3a460522a632e47d7416dbd220599e1ad`.
- MAIN SHA-256: `164f31224bf61181e3f50e7dec40df9afcae5b16dbf6e4c0d0cc5e986af0a84e`.
- MAIN length 1,112,560 bytes; load address supplied by the device profile.

`inspect_stock.py PRIVATE_MAIN` refuses any other hash and reports only label
addresses and pointer references. It locates CREATE SLICE GRID and DELETE ALL
SLICES in two nearby groups of references. These are search leads only:
the string search alone establishes no code entry, calling convention or
mutation semantics. No event guard or site was added. Raw firmware and any
disassembly stay outside the repository.

Subsequent private `m68k-elf-objdump` inspection provides a narrower lead:
the routine beginning at `0x40072c10` selects six-row or nine-row label and
callback arrays before calling the common menu routine at `0x4006d94c`.
Both CREATE SLICE GRID rows point to `0x40072cb8`, which opens an eleven-row
menu after validity checks. The inspected opener span is 116 bytes with
SHA-256 `bf2a6e0d9fe2a3e4cae51dafc126777b83c726fc4dd7970e7651df2e341adc44`.
That is an analysis-span identity, **not a proposed patch guard**. Full call
ABI, every incoming branch, selection lifetime and transaction/Undo behavior
still need execution traces. No code or stock table is included here.

Relevant upstream research (reported evidence, not newly observed hardware):

- `docs/firmware/STORAGE.md` section 4 describes complete marker records,
  working/saved copies, stock sanitation and a minimum 64-frame region. Its
  earlier summary and later parser description disagree on the header
  boundary (16 versus 22 bytes). Resolve this against parser execution before
  implementing any adapter. Do not create a `.ot` or project writer from a
  guessed layout.
- `docs/firmware/REPITCH.md` distinguishes the sample's ATTR tempo from the
  latched project tempo and explains forward/reverse renderer paths.
  Revalidate the chosen value at Apply; the other source must not silently
  substitute for it. Pattern tempo behavior needs an explicit UI decision and
  execution evidence.
- `docs/firmware/DSP.md` describes ColdFire grain crossfades and DSP
  interpolation. A timestretch crossfade is not proof that arbitrary slice
  starts, stops, reverse jumps or retriggers are smoothed. Its FX-instance
  address correction on current main also reinforces checking both cores;
  do not derive resource layout from the older tooling pin.

## Proposed base contract, not an implemented ABI

The first shared SDK change should own the sample editor menu and its stock
transaction boundary. It must be separately owner-reviewed before a module
can subscribe. Provisional names below intentionally have no index or address:

1. A table such as `ot_sample_editor_actions` adds a row without replacing
   FUNC+YES or claiming the whole SLICE screen. Base code owns native menu
   dispatch, redraw, lifetime and ordering; unrelated rows still call stock.
   Final record/prototype, capacity and guards follow measured callers.
2. A read-only snapshot service supplies opaque sample/content generation,
   complete slice records, trim/loop state, source/format, decoded PCM access
   and the selected tempo. No long-lived raw pointer into a mutable slot.
3. Preview runs as cancellable, bounded background work. The current planner
   is synchronous: bounded callback count is not a UI deadline or a safe
   Static-streaming budget. A measured cache/job adapter must yield without
   decoding or waiting on storage in any audio interrupt.
4. Apply compares the whole snapshot under stock's serialization boundary,
   rejects stale content/markers/trim/tempo or an active conflicting editor,
   then commits once. Preview, Cancel and failed Apply do not dirty or save
   anything. Undo retains complete records and refuses to undo across another
   edit. A later project/sample save uses stock, never a new storage format.
5. Preserve stable slice semantics, not merely starts. Inserting a start into
   a sorted list can renumber existing slices and change slice-lock playback;
   this needs native investigation and an explicit policy before Apply.
   Existing starts outside trim, per-slice ends/loops, overlapping records and
   sub-minimum final regions must be preserved or explicitly refused.
6. Retire pending previews/jobs on sample switch, editor close and uninstall.
   Prove that no menu callback, voice or PCM job retains module pointers after
   removal. Missing-module fallback must still load ordinary stock markers.

## Playback smoothing decision

Do not implement smoothing at an arbitrary effect/mixdown tap: it could fade
other voices and effect tails, miss direct/cue paths or conflict with stock
source ownership. First trace the actual start, end, retrigger, loop wrap and
discontinuous seek paths for Flex and Static on both cores, including reverse,
RATE/PTCH, timestretch, locks and multiple tracks sharing a sample.

An attack ramp alone cannot remove a discontinuity when the outgoing voice is
cut off. A release/crossfade requires a valid outgoing source/history, bounded
per-voice state and a defined policy for short slices and overlapping jumps.
Any shared boundary service belongs in the base; the module's own algorithm
and tables stay in its package. No dependency on another module, destructive
sample fades, global AMP edits or private shared-site patches are acceptable.

Even every `needs_fade == 0` result remains only an amplitude observation.
Apply stays disabled until the actual playback policy is implemented and
qualified, including save/reload and module-absent behavior. Do not label a
quiet-marker fallback as acceptance of the click/pop requirement.

## Before an exact hardware trial

Finish native linkage/execution, menu/transaction ABI proof, cancellable PCM
work, full-record preservation and stale/failed-commit regressions first.
Then source-build card/browser/runtime packages, prove stock-free export,
compatibility/admission/removal and emulator lifecycle, and measure resources.
Only then name an exact private build and request a scoped disposable-project
trial. The existing unit's missing module references remain untouched. Actual
audio and physical save/reload/reboot evidence remain separate requirements.
