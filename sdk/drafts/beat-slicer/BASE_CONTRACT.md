# Sample-editor service proposal

Status: design for owner review, **not an exported ABI or module capability**.
No event number, base feature bit, address guard or package admission is assigned.
The implementation belongs in a separate shared-base change before Beat Slicer
can use it. This draft contains portable core/admission prototypes and stock probes.

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

Do not substitute the stock control-record counter or dirty flag for the
content generation. Isolated 1.40C execution now proves that rotation and
polarity edits change PCM while all 44 control bytes, including the counter,
remain identical; repeated edits keep the dirty flag set. The release path
increments the counter and skips zero on wrap, but that covers neither these
in-place writes nor lifetime uniqueness. Comparing the complete control record
therefore cannot establish content coherence either.

The shared provider must invalidate live previews **before** a relevant writer
can change PCM, including a writer that later fails, and refuse acquisition
while a writer is active. Cover in-place edits, slot replacement/release,
recording and any other discovered writer, plus owner removal and required
metadata/tempo changes. Do not enable a live provider until that coverage and
its serialization are proved. The current probes demonstrate missing coverage;
they do not enumerate every writer or assign hook sites to a new ABI.

Expanded instruction/store observations now cover eight edit families. They
leave the busy field and counter untouched, with unmasked instruction intervals
between masked PCM writes. A dirty-store notification can invalidate existing
tokens but cannot prevent a new snapshot during an unfinished edit. Track the
whole writer lifetime and identify the destination of cross-slot copies;
retire exclusion on all return paths, including normalization's observed
dirty-without-PCM failure. See [writer coverage](WRITER_COVERAGE.md) for the
executed cases and still-missing writers. No native exclusion is implemented.

Worker lifecycle probes add two constraints: an empty command queue does not
mean the dequeued writer has finished, and UI completion is an asynchronous
notification that can be omitted when its record pool is full. Retire writer
exclusion at a verified execution boundary on every path, independently of
UI notification. Queued command pointers are not immutable operation IDs:
capture validated identity and affected destinations under proved ownership.
The current seven-operation worker trace does not cover recorder writes,
all worker opcodes, other callers, live scheduling or cancellation.

The draft [admission prototype](PREVIEW_GUARD.md) implements coarse global
revisions, unique tickets, nested-writer exclusion and revocation/exhaustion
behavior in portable C. It is not an assigned ABI or a native serialization
mechanism. The shared implementation and all writer/copy boundaries still need
review before a module can subscribe or a live provider can be enabled.

PCM reads copy a bounded block into caller-owned scratch memory. They report
ready, pending, stale, unsupported or failed; a pending Static read yields
to the scheduler. No filesystem wait, allocation or sample scan runs in the
audio interrupt. A recorder or file being modified is refused until content
can be pinned consistently. A sequence of individually valid reads is not
a coherent preview if the source changes between them.

Distinguish a raw pool page lookup from decoded PCM. Validate pool readiness,
slot kind/range, encoding, frame extent and allocation ownership before any
native lookup. Flex and Static require their own proven access paths; a slot
number alone cannot choose one. Bound copies by both the remaining sample
extent and the current contiguous page, then decode into the planner's signed,
right-aligned 24-bit values (duplicate mono). Verify each decoder's actual
read extent, including vector tails and required padding. Never retain a raw
page pointer across a yield or assume that an active recorder's current
length makes its contents stable. Reverse playback does not require a reverse
preview scan: scanning source coordinates forward avoids imposing unverified
reverse-reader conventions on this one-shot action.

The tested release routine publishes a temporary allocation-map pair before
copying the map back. A surviving slot's map offset changes even though its
control record and audio do not. Use the current maps under a verified guard
for each bounded copy; a cached map pointer plus an unchanged slot counter
does not establish ownership. The tests run without task/interrupt interleaving
and do not prove the guard needed by a live provider.

The synchronous `bs_preview` remains an arithmetic oracle. The portable
`planner_job` prototype now advances one bounded transition at a time and
requests PCM frames without calling a reader. A pending frame can yield;
replies must match that job's serial and frame, and cancellation retires the
preview. This is not a base service. The real adapter must bind each read to
the operation/content generation, discard in-flight reads before reusing job
storage, and provide measured time and cache limits. Merely limiting callback
counts does not limit the time spent in a blocking reader.

The portable `pcm_reader` now wraps that job with a 32-frame decoded cache
and bounded 16/24-bit decoding. It accepts whole-frame prefixes when a page
ends early, copies them before returning, and retains no provider pointer.
Every reply echoes the operation, revision, serial and requested extent.
Operation IDs must not be reused while old replies can exist. Step/result
calls revalidate the caller's current revision even after a completed preview;
the provider must independently pin or revalidate content around its copy.
These are tested software contracts, not implemented native generation
tracking. A slot number, timestamp or unchanged length cannot stand in for
the required revision. Native admission must refuse unsupported or mutable
sources until it can supply this contract truthfully.

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

The isolated stock marker parser has now been observed changing synthetic
slot records before rejecting a bad checksum or truncated input. Calling it
with a prepared stream is therefore not an atomic Apply implementation.
The stock sanitizer also clamps existing starts, ends and loops in the tested
Flex/Static fixtures. Preflight must establish that retained records would
remain exact; never run a sanitizer speculatively against live settings.

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
