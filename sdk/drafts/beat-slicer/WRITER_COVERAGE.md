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

## Consequence for the base service

An epoch increment at a dirty store can retire old previews, but cannot by
itself protect a **new** preview acquired midway through an edit. Nor can the
unchanged busy field establish that copying is safe. The base must establish
an operation lifetime: retire old tokens before mutation; refuse snapshot/read
acquisition while the writer is active; release that exclusion on every
completion/failure path. Repeated/no-op/failed edits must not accidentally
reactivate an older token. Cross-slot work must identify the destination.

The instrumentation here only observes stores and instructions. It does not
install a dirty-store hook, synthesize native revisions or implement a lock.
Masking a bounded read protects that copy only after the larger writer and
allocation ownership rules have been established.

## Missing evidence before live-provider admission

- Trace actual panel commands through enqueue, dispatch and completion. Local
  static inspection groups these calls in the stock worker dispatcher, but
  does not prove all callers, cancellation, reentrancy or queue serialization.
- Cover crop/resize, slot load/replacement, allocation/release of other slots,
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
