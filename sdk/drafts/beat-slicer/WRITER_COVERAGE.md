# Live-reader writer coverage

Status: investigation for the shared-base service, **not implemented hooks or
complete writer coverage**. Live reading and Apply remain unavailable. These
addresses identify routines executed from the private, hash-bound original
1.40C MAIN; they are not exported SDK functions or approved patch sites.

## Executed in synthetic memory

The coherence runner exercises the following operations without mocking their
callees. `TESTING.md` and `evidence/stock-writers.json` bind the exact source,
emulator executable and private MAIN. All PCM, slots and allocation geometry
are authored fixtures. The scheduler, filesystem, DSP and hardware do not run.

| Operation | Entry under investigation | Coverage |
| --- | --- | --- |
| Rotation | `0x40094b6c` | Eight calls, four formats, repeated edits |
| Stereo polarity | `0x40094c94` | Twelve calls, two packed widths, three channel modes, page boundaries and repeated edits |
| Stereo channel processing | `0x40094dc8` | Eight sum/difference/swap fixtures across page boundaries |
| Copy/mix between slots | `0x40094fa4` | Sixteen fixtures: four formats and four modes, source page crossing, destination-only changes |
| Reverse | `0x40095268` | Four page-crossing fixtures with the exercised inclusive endpoint convention; the UI's complete range convention is unproved |
| Fade | `0x40095394` | Eight four-frame fades with independently calculated PCM |
| Gain | `0x40095560` | Eight zero/half-gain fixtures |
| Normalize | `0x40095774` | Four constant-amplitude fixtures plus four silent-input failures |
| Release | `0x40096300` | Three existing counter/wrap, page-clear and temporary-map fixtures; no live ownership guard proved |

Each of the 68 successful in-place/copy edit calls above writes its
destination's dirty byte before PCM. A repeated store remains observable when
that byte is already set. None writes the tested slot-control region, including
the counter and busy field. PCM stores execute with interrupt masking, but
instruction observations find the original unmasked state **between** stores,
before the operation has finished. This is an isolated execution observation,
not proof that the live scheduler actually interleaves at that point.

Silent normalization returns `-1` after marking the destination dirty, with no
PCM or control stores. Thirty-five additional busy/pool/slot/range refusals
across channel processing, reverse, fade, gain and normalization perform none
of those stores. Existing polarity refusals cover eight more cases. These are
specific fixtures, not a general promise of stock error atomicity.

## Executed worker lifetime

The 0.1.5 runner adds seven groups bound in `evidence/stock-worker.json`.
It executes the real engine-task prologue at `0x4008445c`, queue post/receive
at `0x40000c3c` / `0x40000d00`, and dispatch from the loop at `0x4008484e`.
Only message display is mocked. The rings, slots, PCM and completion-pool
occupancy are synthetic; no stock tables or code bodies are reproduced.

- Four zero-gain producer calls (`0x40074694`, one per packed format) set
  editor busy and enqueue a pointer without editing PCM. The worker dequeues,
  edits the exact page-crossing range, returns from the writer and posts a
  completion record. The queue count is already zero during PCM writes.
- Seven dispatch cases cover gain, normalize, reverse, rotate, channel swap,
  polarity and fade. The traced writer returns before completion is attempted;
  the task then restores its loop stack/frame and interrupt mask. Busy and
  empty-range gain refusals return `-3` and `-2` through deferred completion
  without PCM/dirty mutation.
- Completion helper `0x40084110` queues a UI record containing callback/result,
  rather than invoking it. The fixtures leave the UI consumer unexecuted and
  editor busy remains set after the producer-originated edit. A null callback
  or all 32 completion records occupied still permits the edit to finish, with
  **no UI notification enqueued**. Do not release writer exclusion from this
  optional notification.
- Two pending edits execute FIFO with separate completion records. Thirty-five
  standalone posts/receives exercise ring wrap below capacity. An unknown
  opcode drains without completion; an empty worker reaches the event-wait
  entry, where the test stops before running the scheduler.
- Calling the same producer twice while deliberately bypassing the outer panel
  preflight queues the same global command pointer twice. Both executions then
  observe the last payload. This tests pointer ownership; it does **not** show
  a reachable stock UI bug or prove how the real panel blocks repeated input.

These results identify boundaries to investigate, not production hook sites.
The historical 0.1.5 trace omits crop, release and copy dispatch; the extension
below adds those cases. Other engine opcodes/callers, actual UI completion
consumption, scheduler wakeups, cancellation, reentrancy and recorder writes
outside this worker remain unproved. Queue capacity/overflow is not qualified.

## Admission guard and remaining edit dispatch (0.1.6)

The expanded nine-group runner (`evidence/stock-guard.json`) binds the original
portable guard into its executable and observes the stock instruction stream.
This guard runs on the host alongside the emulated CPU; it is not a native
hook. Each observed writer entry retires a previously acquired token, PCM
writes refuse new tokens, and actual return reopens admission with a fresh
identity. This also works for refused edits and absent UI completion.

Added dispatch coverage:

- Copy (`0x40094fa4`, opcode 29) copies a distinct stereo source into a disjoint
  range in the same slot, preserving the source and all other frames. Earlier
  coherence probes separately cover cross-slot copies; this worker case does
  not establish all overlap/range conventions.
- Crop (`0x40095cd8`, opcode 27) enters rotation internally. The guard tracks
  both tickets; rotation's return leaves crop's exclusion active. A successful
  fixture changes length/counter and returns through deferred completion.
- Crop's empty-range refusal returns `-2` **after incrementing the stock slot
  counter**, without dirty/PCM writes. Error return alone is not proof that
  source metadata remained unchanged. Full slice/trim preservation and crop
  range semantics remain outside this fixture.
- Release (`0x40096300`, opcode 28) clears the two owned pages, empties the slot
  and allocation count, and advances its counter. It returns to the worker loop
  without attempting the UI completion helper. The now-idle guard does not make
  that empty slot readable: the provider must separately validate the source.

See [PREVIEW_GUARD.md](PREVIEW_GUARD.md) for capacity, revocation, exhaustion
and serialization requirements. The guard is disabled by default and remains
outside the base ABI. It cannot compensate for an unobserved writer.

## Consequence for the base service

An epoch increment at a dirty store can retire old previews, but cannot by
itself protect a **new** preview acquired midway through an edit. Nor can the
unchanged busy field establish that copying is safe. The base must establish
an operation lifetime: retire old tokens before mutation; refuse snapshot/read
acquisition while the writer is active; release that exclusion on every
completion/failure path. Repeated/no-op/failed edits must not accidentally
reactivate an older token. Cross-slot work must identify the destination.
An empty queue cannot admit a new preview while its dequeued writer runs.
Completion/cleanup must track execution even if UI notification is absent,
and owned identity must not depend on a reusable command-record pointer.

The instrumentation here only observes stores and instructions. It does not
install a dirty-store hook, synthesize native revisions or implement a lock.
Masking a bounded read protects that copy only after the larger writer and
allocation ownership rules have been established.

## Missing evidence before live-provider admission

- Extend the executed operation-handler/worker trace to the actual panel
  preflight and UI completion consumer, every caller and remaining opcode.
  Prove live cancellation, reentrancy, wakeups and serialization; the synthetic
  FIFO cases alone do not prove those behaviors.
- Extend crop/release range and allocation coverage; cover slot load/replacement,
  project/sample reload, recording/overdub and every other PCM writer. Enumerate
  cached/uncached aliases and writes that do not touch the dirty array.
- Prove map ownership and coherent source format/extent discovery during each
  bounded copy. Release can change a surviving slot's map without changing its
  control record. The current probes do not interleave an allocator or recorder.
- Cover trim/loop/markers, chosen tempo, editor/sample switch, owner replacement
  and removal. These must invalidate the right operation without using slot
  number, filename or counter reuse as identity.
- Establish Static file/stream lifetime separately. No Flex fixture proves it.
- Review whole-instruction guards, all incoming branches, ABI/register/stack
  behavior, resource limits and compatibility before proposing shared hooks.
  Qualify exact browser/USB packages and real device behavior afterwards.

Do not enable a partially covered provider. These observations refine
[BASE_CONTRACT.md](BASE_CONTRACT.md); they do not satisfy its admission gate.
