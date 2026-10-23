# Sample-editor service proposal

Status: design for owner review, **not an exported ABI or module capability**.
No event number, base feature bit, address guard or package admission is assigned.
The implementation belongs in a separate shared-base change before Beat Slicer
can use it. This draft contains only probes and a portable planner.

## Preservation rule

The service operates on complete records, not an array of start positions.
An existing record's start, end and loop must remain identical. Its ordinal
also matters: a pattern can refer to a slice by number. Stock sorts records
by start, so inserting an earlier start can change the meaning of such a
reference even when every old position survives.

The proposed first policy is **preserve ordinals or refuse**. Simulate the
result first and return an explicit index-conflict result if any existing
record would move. Do not rewrite patterns, locks, Parts or other tracks to
compensate. Do not ask the user to silently accept lost preservation. This
allows a new grid on an unsliced sample and additions that keep all existing
ordinals; it deliberately cannot apply every merged grid on a sliced sample.
The owner must review this restriction before it is represented as supported
module behavior. Preview can still show why a proposed merge was refused.

Beat Slicer submits requested additions, not replacement records. The base
retains existing records itself, constructs new records with verified stock
endpoint conventions, and validates minimum lengths and total capacity.
Overlaps, disabled loops, duplicate starts and starts outside trim require
explicit tested rules. Unknown cases are refused; existing records are not
sanitized as a side effect of preview or cancellation. The current planner's
out-of-trim refusal is a limitation, not a native preservation implementation.

## Menu registration and lifetime

Add one named action to the SLICE action menu, preserving every stock row and
callback. The registry owns ordering and rejects duplicate action keys. A
module claims its action name, not the whole screen or stock FUNC+YES gesture.
The existing runtime loader does not admit arbitrary contributed tables;
the shared change must provide reviewed typed admission and removal.

The stock menu keeps its label, callback and selection-output pointers after
the open routine returns. They therefore cannot point to temporary stack
arrays or a module that may be removed while the menu is open. The base owns
the composed arrays and copies bounded labels into its own storage. Entries
use base-owned dispatch functions; the base resolves the action's module id,
package generation and action id while holding the loader's live-owner guard.
Never retain an unguarded function pointer into the module pool.

Selection stores the selected row, closes the menu and invokes the callback
synchronously through a null-safe indirect-call helper. A callback that starts
background work returns promptly; the base owns the job token and cancellation
path. A captured menu generation is invalidated on menu replacement/close,
sample switch, owner replacement or removal. No action row can acquire a new
meaning by reusing the same index while an earlier activation remains live.

Removal must cancel the preview and retire menu/job references before module
memory is reclaimed. It must return busy while a callback is actually running.
Loader stack/register scanning alone cannot discover a retained heap/global
pointer. Test closing, replacing and removing at each callback/job boundary.

## Snapshot and job contract

One base-owned operation token identifies the selected sample and the editor
generation. It is not a slot number or a long-lived raw settings/PCM pointer.
Capture at least:

- Sample kind/slot plus content identity and content generation. Reusing a
  slot or replacing a file with the same name must invalidate the token.
- Complete marker records and count, trim/loop state, sample rate, encoding,
  channel count and a generation covering relevant sample metadata.
- The chosen tempo source and its exact value. SAMPLE uses ATTR tempo;
  PROJECT uses the explicitly documented project tempo value. Pattern tempo
  and external-clock behavior remain to be proved before choosing the getter.
- Owner/package generation and the playback policy required by the action.

Unselected tempo changes need not invalidate a preview, but a change to the
chosen source does. Generation comparison must handle wrap/reuse and must
not turn an untracked writer into a false successful validation. Until every
relevant native writer is covered, compare the complete relevant state under
the same serialization boundary used by Apply.

PCM reads copy a bounded block into caller-owned scratch memory. They report
ready, pending, stale, unsupported or failed; a pending Static read yields
to the scheduler. No filesystem wait, allocation or sample scan runs in the
audio interrupt. A recorder or file being modified is refused until content
can be pinned consistently. A sequence of individually valid reads is not
a coherent preview if the source changes between them.

The synchronous `bs_preview` remains an arithmetic oracle. The portable
`planner_job` prototype now advances one bounded transition at a time and
requests PCM frames without calling a reader. A pending frame can yield;
replies must match that job's serial and frame, and cancellation retires the
preview. This is not a base service. The real adapter must bind each read to
the operation/content generation, discard in-flight reads before reusing job
storage, and provide measured time and cache limits. Merely limiting callback
counts does not limit the time spent in a blocking reader.

## State transitions and atomicity

`CAPTURED → SCANNING → READY → APPLYING → APPLIED`

Cancel, owner removal, sample switch and stale input retire a token without
changes. A failed read produces a failed preview; it does not downgrade
SMOOTH to EXACT or substitute the other BPM source.

Apply is accepted only for a ready token and explicit confirmation of that
preview. Under the stock writer/reader serialization boundary, revalidate
the snapshot, capacity, complete records, preservation rule and playback
policy. Prepare the entire candidate and rollback state before publishing
any changed count or record. An interrupt mask around a write is not proof
that another task, a cached alias or an active voice cannot observe half of
the edit. The stock editor's short masked block is a research lead, not a
complete transaction API.

Publish once, refresh native editor/voice state in the proven order, and let
stock manage working/saved copies and subsequent persistence. No custom
`.ot`, marker or project serializer is introduced. Failures must leave the
pre-edit state intact or roll back under the same boundary. A successful
commit is reported only after all required publication steps complete.

Undo stores complete before/after records in base-owned memory and checks
the after-generation before restoring. It must refuse after an intervening
edit or sample change. Integration with stock Undo/history remains a separate
proof; this proposal does not claim that stock has an applicable Undo service.

## Playback contract still needed

Marker placement alone cannot meet the audible acceptance requirement. The
playback path must establish what happens at start, natural end, stop,
retrigger, slice/loop wrap and discontinuous seek for Flex/Static, both
directions, RATE/PTCH, timestretch and both DSP cores. Keep effects tails and
unrelated voices out of a source transition. Preserve outgoing source history
when the chosen crossfade needs it and measure worst-case memory/CPU cost.

There is also a persistence decision: if smoothing is enabled only for samples
processed by this action, its identity/policy must survive the required stock
save/reload behavior. A RAM-only list of slots is insufficient; arbitrary
custom project metadata is not permitted. A generic base declick policy
would have a broader compatibility and ownership scope. Neither approach is
approved here. Existing stock declick behavior must be measured before adding
a new renderer hook, and the base must not contain Beat Slicer's algorithm.

Apply remains unavailable until a qualified policy exists. A quiet boundary,
emulator trace, native link or synthetic crossfade is not audible hardware
acceptance. Module-absent loading must preserve ordinary stock markers; any
loss of module-only smoothing must be clearly described and tested.

## Evidence required before assigning an ABI

The isolated CPU probes cover menu retention/dispatch, settings lookup,
complete-record sorting and insertion renumbering using synthetic state.
They do not boot a project, run the scheduler concurrently, render audio,
save sample settings or demonstrate Undo. UI callees are mocked explicitly.

Still required: full editor traces through the actual panel path; all incoming
branches and overwritten instructions for a candidate base site; callback
register/stack contracts; PCM cache/streaming lifetime; native save/reload and
Undo behavior; working/saved-copy publication; generation coverage; resource
and compatibility review; removal and missing-module handling. Only then can
the reviewed registry, loader, browser builder and module adapter be changed.
