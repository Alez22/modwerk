# Beat Slicer testing

Current draft: 0.1.4-experimental. Local checks: 23 October 2026.
The prior 0.1.3 evidence source is `105f96022b23f05eb7e1af160eab8d2e9c5317e1`.
The 0.1.4 writer report binds its source files directly and the manifest pins
the tested source commit `8c6d64e9832de11fd39490c9609d838c57aece4a`.
Only this provenance note and the manifest evidence pin follow that commit.
Initial checkout: 610a934da51b8f8518e6296493da9059b83e9a7e.
Current development includes upstream main d8059069.
The original 0.1.0 cloud record remains in evidence/host.json; its hashes
describe the imported source, not the subsequently repaired planner.

## Local import and independent verification

Imported 12 regular files from the user's archive, SHA-256
`5fd070c65d6df3ceac322de850ce7c983ee6689de1ed1e8ef51f8959b1a4d9bf`, after
checking paths, types, size and destination collisions. No local file was
overwritten. All imported bytes were verified against the ZIP. The original
14 tests passed on macOS with Apple clang before changing the planner, and
the cloud record's three source hashes matched. The archive remains intact.

`python3 -B -m unittest discover -s sdk/drafts/beat-slicer -p 'test_*.py' -v`:
**18 tests pass** on the repaired planner. Four independent tests add 2,000
seeded rational-grid/marker-union cases, 200 exhaustive stereo-search cases,
threshold edges, out-of-trim refusal, maximum-step arithmetic at the uint32
limit and half-frame tie rounding. These use synthetic PCM, not playback.
See evidence/local-host.json for hashes and tool versions.

## ColdFire compilation and link

Built `sdk/build/Dockerfile` under `/tmp/modwerk-check.lock` as
`modwerk-source-tools`, immutable image
`sha256:da70d46e10b243277fa3ae2e015f7258d56b3ee08ca4be47e61899958872e792`.
GCC 16.2.0, binutils 2.47.20260726 and the repository-patched DSP assembler
are installed inside that image. No firmware is in it.

Run `native_probe.py --output /output` inside that image, offline, with the
repository mounted read-only at `/source` and a fresh private output folder.
Keep the machine-wide lock around the container. The script imports the
shared ColdFire code-generation guard and refuses an output under the repo.

The imported planner compiled but needed `__muldi3`, `__udivdi3`, `memcpy`
and `memset` (evidence/native-import.json). Version 0.1.1 carries exact
quotient/remainder arithmetic in bounded 32-bit values and copies explicit
fields; native builds also disable loop-to-libcall conversion. Final result:

- 1,994 bytes of object text, zero data/BSS, no undefined symbols.
- Standalone freestanding link passes at a synthetic address, not a device
  address. Shared stepped-register code-generation guard passes.
- GCC reports 644 bytes for `bs_preview` and 20 for `read_peak`; these are
  static compiler stack reports, **not total device stack bounds**. The PCM
  callback and native adapter add their own usage.

See evidence/native.json for that compile/link run. Subsequent target-code
execution is documented below. No runtime package was produced and no UI
latency, cycles or real device memory was measured.

## Isolated CPU execution, 23 October 2026

The same pinned object (SHA-256
`862fbf786e4388477f7c3efa7601dad7bef8d9583c5b0a21db5351e3276594d4`)
passes **164 native planner vectors** in synthetic CPU memory, with no stock
OS input. The runner compares mathematical grids against an independent
64-bit rational oracle, exercises both tempo sources and all spacings, checks
PCM callback arguments, callee-saved registers, input immutability, boundary
flags, output sentinels and atomic invalid/read/capacity failures. This is
execution of the compiled ColdFire instructions, not on-device timing.
See `evidence/native-execution.json`.

**Six isolated stock routine probes pass** against the private original
1.40C MAIN: settings lookup boundaries, both slice-menu variants, retained
menu pointers and synchronous selection, complete-record stable sorting,
12-byte slice record pointers, and insertion that renumbers an old record.
The formatting/display/editor-follow-up calls listed in `probe.cpp` are mocked.
The stock sorter and its copy helper execute. This is not full editor,
scheduler, save/reload or playback evidence. See `evidence/stock-cpu.json`.

Both runners use the upstream `ot::Machine` source at
`8250be0c23ca0a0a953cb7e5721e3bdb98dadfe5`, mc68k pin
`4a6d0d17a1f2b30077ab726c27fe9bb770fa0456`, GNU 13.3.0 host C++, Release
without LTO. The emulator's **EMAC and peripheral gates pass** before these
results are accepted. No DSP core executes in these probes. The DSP library
dependency comes from the prepared toolchain image, not an updated SDK import.

To reproduce inside the image above, mount the repository at `/source`
read-only, the verified Octabam tools checkout at `/upstream` read-only,
mc68k at `/cpu` read-only and a private empty build folder at `/output`.
Create `/output/vendor/mc68k → /cpu` and
`/output/vendor/dsp56300 → /opt/toolchain/vendor/dsp56300`. Under the machine
lock, with Docker networking disabled:

```sh
cmake -S /source/sdk/drafts/beat-slicer/stock_probe -B /output/build \
  -DCMAKE_BUILD_TYPE=Release -DOT_LTO=OFF \
  -DOCTABAM_ROOT=/upstream -DOT_VENDOR=/output/vendor
cmake --build /output/build --target beat_slicer_stock_probe \
  beat_slicer_planner_probe ot_emac_test ot_periph_test --parallel 4
ctest --test-dir /output/build/emulator -R '^(emac|periph)$' --output-on-failure
python3 -B /source/sdk/drafts/beat-slicer/native_probe.py --output /output/native
python3 -B /source/sdk/drafts/beat-slicer/native_execution.py \
  --compiled /output/native --executable /output/build/beat_slicer_planner_probe \
  --output /output/execution
```

Only the stock probe needs an additional read-only mount of the private MAIN:

```sh
python3 -B /source/sdk/drafts/beat-slicer/stock_probe.py \
  --main /stock/stock-main.bin --executable /output/build/beat_slicer_stock_probe \
  --output /output/stock-probe.json
```

The wrapper refuses any other MAIN hash. CMake embeds each runner's source
hash, and the wrappers reject stale runner binaries before recording evidence.
Keep source fixed during builds and use fresh evidence paths. The preliminary
stock probe run made during a source refinement is excluded; only the rebuilt,
source-matched final run is recorded. All binaries/raw emulator logs remain
outside Git. The reports contain only hashes and test summaries.

## Isolated stock storage probes

Five groups pass in `stock_probe/storage_probe.cpp`, using the same pinned
CPU emulator and private original MAIN as the editor probes:

- Stock project-marker writer/parser: all 264 synthetic slots round-trip;
  complete records, count and unrelated settings are checked. Stream extent,
  record mapping and checksum coverage are checked independently.
- Bad-header, bad-checksum and truncated-input behavior: the latter two
  return errors after changing destination records; no atomic-load claim.
- Project-marker writer protection refuses before the synthetic write call.
- Separate sample-settings writer/parser: Flex and Static complete markers
  round-trip, other slots stay intact, and bad checksums fail after mutation.
- Six Flex/Static sanitizer fixtures (32/64/1,000 frames): clamping, disabled
  loops, inactive-record and other-slot isolation, and repeat idempotence.

The file read/write/size APIs are mocks over in-memory bytes. Serializer
output is not saved. Name/tempo/track-refresh callees are mocked where listed
in the source. These are stock-instruction observations in synthetic state,
**not actual Save Project, Save Sample Settings, Undo, card failure recovery,
physical reboot or playback tests**. Recorder-specific handling, older file
versions, and full editor/scheduler integration are not covered.
`evidence/stock-storage.json` binds the passing final runner to its source.

Reproduce with the mounts and machine lock used above:

```sh
cmake -S /source/sdk/drafts/beat-slicer/stock_probe -B /output/build \
  -DCMAKE_BUILD_TYPE=Release -DOT_LTO=OFF \
  -DOCTABAM_ROOT=/upstream -DOT_VENDOR=/output/vendor
cmake --build /output/build --target beat_slicer_storage_probe --parallel 4
python3 -B /source/sdk/drafts/beat-slicer/stock_probe.py --kind storage \
  --main /stock/stock-main.bin --executable /output/build/beat_slicer_storage_probe \
  --output /output/stock-storage.json
```

The wrapper rejects other MAIN hashes, stale runner source and existing
report paths. `--kind editor` remains the default for the earlier six probes.
The first four-group exploratory run is retained privately; only the final
five-group source-matched run is recorded here.

## Isolated stock pool and converter probes

`evidence/stock-reader.json` records **five passing groups** using the same
pinned CPU emulator/toolchain and hash-bound private MAIN described above:

- Control lookup distinguishes Flex/recorder from Static and rejects the
  exercised unavailable/out-of-range Flex cases. The page walker itself is
  not called with those invalid preconditions because it omits a null check.
- 88 forward lookups: four authored page layouts, two Flex slots,
  non-contiguous pages, page/sample boundaries and invalid frame coordinates.
- 36 reverse lookups establish its different pointer and raw `d1` convention.
- Four recorder fixtures with explicitly mocked active/length helpers.
- 40 PCM conversion fixtures: both byte orders, 16/24-bit signed values,
  lengths 0–9, vector/scalar paths, unchanged source and output sentinels.
  A CPU data-read watch verifies the 24-bit scalar tail's extra-byte read.

All calls check callee-saved registers and stack return. Page geometry and
allocation maps are **authored fixtures**, not observed runtime initialization.
These tests do not establish a safe native reader: no Static file streaming,
booted editor, real content generation, allocation lifetime, concurrent
recording, scheduler integration, device timing or audible output is tested.
The probes do not copy stock routines/tables into the repository.

With the earlier mounts and machine lock, reconfigure CMake to pick up the
new target, then run:

```sh
cmake --build /output/build --target beat_slicer_reader_probe --parallel 4
python3 -B /source/sdk/drafts/beat-slicer/stock_probe.py --kind reader \
  --main /stock/stock-main.bin --executable /output/build/beat_slicer_reader_probe \
  --output /output/stock-reader.json
```

Only the final source-matched run, including the read watch, is retained as
repository evidence. The preliminary run remains private. Existing reports
keep the wrapper/CMake hashes of their own runs, not the new reader target.

## Resumable preview prototype

`python3 -B sdk/drafts/beat-slicer/test_job.py` passes **500 comparisons**
against the synchronous oracle with host AddressSanitizer and UBSan. Both
full output and PCM read order match, including capacity failures, fractional
tempos, every spacing, both BPM sources and near-uint32-limit coordinates.
The same harness checks copied request metadata, cancellation at every
transition of a boundary search, repeated pending polls, rejected stale read
replies, and failed/invalid PCM at every read in that search. Incomplete,
cancelled and failed previews leave output untouched. See `evidence/job-host.json`.

The compiled ColdFire harness passes **100 comparison vectors** and those
lifecycle checks in synthetic CPU memory, with preserved registers and stack.
No stock code, scheduler, DSP, firmware input or device participates. The
resumable planner object is 1,944 bytes of text with no data/BSS; the complete
harness links without unresolved helpers and passes the shared codegen guard.
Compiler-reported stack is 44 bytes for begin, 48 (dynamic, bounded) for step,
16 for its insertion helper, 0 for supply/cancel and 4 for result. These are
individual compiler reports, not measured hardware stack or latency.
See `evidence/job-native.json` for final source hashes and exact flags.

To reproduce after the emulator setup above, under the same machine lock:

```sh
cmake --build /output/build --target beat_slicer_job_probe --parallel 4
python3 -B /source/sdk/drafts/beat-slicer/job_native.py \
  --output /output/job-native --executable /output/build/beat_slicer_job_probe
```

Reconfigure CMake first when adding the new runner to an older build folder.
Use a fresh output directory. The synchronous oracle stays separate so the
state-machine implementation is compared with independently structured code.
The earlier rational/exhaustive host tests still validate that oracle.

`bs_job_step` does one bounded transition, with each marker loop capped at
64 iterations. It performs no PCM callback or IO; `NEED_FRAME` can remain
pending until the caller supplies the matching read serial and frame. The
caller must serialize access and retire in-flight reads before reusing a job.
The job does not validate live sample/content generations or make a blocking
decoder safe. Native cache/streaming, scheduling, sample identity and editor
transactions remain unimplemented. No audible or hardware claim follows.

## Bounded PCM staging layer (0.1.2)

`python3 -B sdk/drafts/beat-slicer/test_pcm_reader.py` passes with host
AddressSanitizer and UBSan. `evidence/pcm-host.json` binds the source and flags.
The same C selftest compiles and runs in the pinned CPU emulator through
`pcm_native.py`; `evidence/pcm-native.json` records the source/object/runner
hashes, successful freestanding link, shared codegen guard and preserved
register/stack checks. No stock image is supplied to either test.

- 4,160 decoder vectors: signed extrema and seeded inputs across 16/24-bit,
  mono/stereo and both byte orders, including unaligned data and truncated
  input that must leave output untouched.
- 40 complete preview comparisons against the synchronous planner, with
  page lengths 1, 9, 17, 25 and 33 frames across all eight formats. The
  provider overwrites its scratch buffer immediately after each reply.
- Cancellation and revision invalidation at every transition of a search,
  including cache hits, pending reads and completed results. Old operation,
  revision, serial, position and extent replies leave the reader unchanged.
  Matching failed, null, empty, partial-frame and oversized replies fail
  without exposing a plan. Reusing storage with a new operation rejects an
  old reply even when serial/frame/revision match.
- Source/format refusal, sample-end bounds and near-uint32-limit coordinates.
- 256 host-only exact-buffer cases: every block length 1–32 in all eight
  formats, unaligned with the final byte at an ASan allocation boundary.
  Both the standalone decoder and staged reply path execute; provider
  storage is freed before the next cache step.

The reader object contains 1,364 bytes of code and no static data/BSS.
Compiler stack reports are 52 bytes for decode, 32 for begin, 40 for step,
60 for supply, 4 for cancel and 8 for result. These are per-function reports,
not whole-call-chain/device measurements. The cache holds 32 stereo int32
frames (256 bytes) inside caller-owned state; no heap allocation or IO occurs
in the reader. A reply decodes at most 192 input bytes. These work bounds do
not establish a UI timing budget.

Reproduce with the pinned image and machine-wide lock described above, the
source mounted read-only, the existing source-matched `beat_slicer_job_probe`
runner, and a fresh private output directory:

```sh
python3 -B /source/sdk/drafts/beat-slicer/pcm_native.py \
  --output /pcm-output/native --executable /output/build/beat_slicer_job_probe
```

This portable staging layer does not call a stock pool lookup or filesystem
service. Native format discovery, coherent Flex ownership, Static streaming,
recorder refusal, real revision tracking, scheduler integration, editor
Apply/Undo, USB packages and hardware/audio qualification remain pending.
Caller-supplied revision numbers cannot prove the sample did not change.

Repository validation on upstream `a3995bca`: the 18 planner host tests and
500 resumable-preview comparisons pass. `npm run check -- --base origin/main`
stops at the upstream `play-start` publication requirements (missing UI and
qualification evidence); `modules:generate` also refuses that module.
`module:doctor -- beat-slicer` refuses this unlisted draft as expected. None
of these publication gates has been relaxed or recorded as passing.

## Stock content-coherence probes (0.1.3)

`stock_probe/coherence_probe.cpp` passes five groups on the pinned CPU emulator
and hash-bound original MAIN. No callees are mocked. The emulator EMAC and
peripheral gates pass before the probes. `evidence/stock-coherence.json`
records the source and executable hashes; earlier reports keep the wrapper
and CMake hashes of their own runs.

- Twelve stereo polarity edits across two packed widths, three channel modes
  and a page boundary, including repeated edits. PCM matches exact expected
  values; the complete control record does not change and dirty stays set.
- Eight rotations across four mono/stereo 16/24-bit formats. PCM matches the
  expected cyclic permutation; control records are unchanged and dirty stays set.
- Eight unsupported/busy/range refusals leave audio and metadata unchanged.
- Three release/counter-wrap cases verify released-page clearing, temporary
  allocation-map publication and surviving-slot audio/control isolation.
- Eight stock-page-to-host-reader previews match the independent planner,
  preserving source bytes. After a real stock rotation, explicit test revision
  invalidation refuses the completed preview. Native writer tracking is absent.

Each stock call checks stack, callee-saved registers and restored interrupt
mask. The fixture has no concurrent tasks or interrupts. All sample geometry
and PCM are synthetic. The C planner/reader in this mixed probe executes on the
host; the stock walker and mutation routines execute as ColdFire instructions.
The separate 0.1.2 target tests remain the portable reader's ColdFire evidence.
No live sample access, Static streaming, timing, audio or hardware is qualified.

The combined runner embeds a binding of its C++ source plus all linked planner,
job and reader C/header files. The wrapper rejects a runner bound only to its
C++ source and produces no report for that mismatch (negative check passed).
This prevents a changed decoder from being paired with an older executable.

Reproduce with the pinned mounts and machine lock above, reconfiguring CMake
first, then:

```sh
cmake --build /output/build --target beat_slicer_coherence_probe --parallel 4
ctest --test-dir /output/build/emulator -R '^(emac|periph)$' --output-on-failure
python3 -B /source/sdk/drafts/beat-slicer/stock_probe.py --kind coherence \
  --main /stock/stock-main.bin --executable /output/build/beat_slicer_coherence_probe \
  --output /evidence/stock-coherence.json
```

Only the final five-group run is retained as repository evidence. The initial
four-group run is private. No portable planner/reader firmware source changed
in 0.1.3; this version adds integration probes and tightens the documented
native-provider requirements.

## Expanded writer-lifetime probes (0.1.4)

The source-matched coherence runner passes **12 groups** in
`evidence/stock-writers.json`, retaining the earlier five-group report as
historical evidence. Same pinned MAIN, Octabam/mc68k sources and immutable
toolchain image as above; EMAC and peripheral gates pass. No callees are
mocked. The original planner/job/reader C files are unchanged.

- Sixty-eight successful edit calls across rotation, polarity, stereo channel
  processing, reverse, fade, zero/half gain, normalization and cross-slot
  copy/mix compare PCM against independent expectations. New fixtures cross
  pool pages; the existing rotations retain their small repeated fixture.
- Store observers see one destination dirty store before PCM on each call,
  including already-dirty samples. There are no slot-control stores, so the
  tested busy fields and counters remain unchanged even transiently.
- These calls start at SR `0x2000`, restore that mask and preserve stack and
  callee-saved registers. Every observed PCM store is masked; instruction
  observations see an unmasked interval after some but before all PCM stores.
  No interrupt is injected and no scheduler executes: this proves the narrow
  instruction behavior, not actual task interleaving or live race freedom.
- Sixteen copy/mix fixtures cross source pages and affect only the intended
  destination frames/dirty byte. Source PCM and both slot records stay exact.
  These use matching source/destination formats; conversion between different
  formats, clipping/overflow and every stock mode are not qualified.
- Four silent normalization fixtures return `-1` after setting dirty, with
  no PCM/control writes. Thirty-five additional pool/slot/busy/range refusals
  across five edit families perform no dirty/PCM/control writes. The earlier
  eight polarity refusals, three releases and eight previews still pass.

The reverse fixtures exercise a particular inclusive-endpoint behavior with
even endpoint differences. They do not establish all odd-length or UI range
conventions. Gain/fade/normalize fixtures avoid clipping and use predictable
values; this is coherence investigation, not general audio-effect qualification.

Reproduce with the existing pinned mounts and machine-wide lock, rebuilding
`beat_slicer_coherence_probe`, running the EMAC/peripheral gates, then:

```sh
python3 -B /source/sdk/drafts/beat-slicer/stock_probe.py --kind coherence \
  --main /stock/stock-main.bin --executable /output/build/beat_slicer_coherence_probe \
  --output /evidence/stock-writers.json
```

Only the final twelve-group, source-matched report is retained. An intermediate
binary was refused by the wrapper after its source changed; it produced no
accepted report. Keep probe sources fixed from configure through execution.

The required lifetime exclusion and missing native writers are listed in
[WRITER_COVERAGE.md](WRITER_COVERAGE.md). No hooks, source revision service,
live reader, editor transaction or installable package was added. Hardware,
actual audio, live timing and persistence remain untested.

On upstream `d8059069`, Node 24.22.1 / `npm ci`, `modules:generate` and
`npm run check -- --base origin/main` pass (2,513 app tests plus SDK gates).
The 18 planner tests, 500 resumable-job comparisons and the PCM sanitizer
suite also pass. The earlier `play-start` catalogue blocker was fixed upstream;
the historical failure recorded above remains the result for that older tree.
`module:doctor -- beat-slicer` still refuses the unlisted draft as expected.
That refusal is not a passing release gate; publication remains blocked.

## Original cloud results (0.1.0)

## Commands and results

`python3 -B sdk/drafts/beat-slicer/test_planner.py`: **14 tests passed**.
Compiles host C99 with warnings-as-errors, pedantic checks and optimization
in a disposable temporary directory. Synthetic PCM only.

Coverage: both BPM sources, all five spacings, 250 Fraction-oracle grid cases
across sample rates and fractional tempos, trim origin/end, marker retention,
capacity/overflow, stereo quiet search, repeat previews, one-channel silence,
full-scale PCM, invalid input and atomic read/validation/capacity failures.

The 2,503 app tests passed before this draft; they do not qualify this module.
The focused suite checks the new core. The app does not import this draft.

## Hardware and audio

User selected MKII over USB. Read-only MCP status was established locally;
the cloud run had no instrument. No module was installed or sent.
Audible playback, clicks/pops, reverse,
retriggers, locks, timestretch and measured artifacts: **not tested**.
Playback fades are not implemented. Marker scores are not auditory evidence.

## Stock flows and persistence

**Not tested:** menu integration, Undo, sample settings save/load, Part/project
save/load, module removal and physical reboot. The planner writes no files,
marker input or audio buffer; that is not native persistence qualification.
INTEGRATION.md contains the planned acceptance flow.

## Performance and resources

ColdFire cycles, device stack/memory, UI latency and Static streaming:
**unmeasured**. Compilation/link results are above. No heap in the core; at most 65 beat candidates
and 769 search positions per snapped boundary at 192 kHz. These are algorithmic
bounds, not native timing or memory measurements.

## Qualification and capture

`verify.py` deliberately fails. `module:doctor` must refuse this unlisted
draft. No LCD captures, card/browser/runtime builds, parity checks, USB trial,
self-test, Keep/Undo/removal or hardware compatibility evidence exists.
This draft is not ready for publication.

## Stock worker lifetime probes (0.1.5)

`evidence/stock-worker.json` records **seven passing groups** from
`stock_probe/worker_probe.cpp`. It binds the private 1.40C MAIN, runner,
wrapper, CMake inputs and executable hashes. The pinned emulator/toolchain
and Docker mounts are the same as the 0.1.4 writer run above. The new target
is `beat_slicer_worker_probe`; run the wrapper with `--kind worker`.

The original synthetic fixtures execute the stock zero-gain operation handler,
queue post/receive, complete engine-task prologue, seven edit dispatch paths,
and completion allocation/posting. Only message display is mocked. They check
exact producer-originated zero gain across four packed formats and page
boundaries, writer entry/return ordering, worker stack/frame/interrupt-mask
restoration, failure results, FIFO/wrap, null callbacks, exhausted completion
records and forced command-pointer reuse. See [coverage](WRITER_COVERAGE.md#executed-worker-lifetime)
for the observed constraints and omitted paths.

Build and run inside the pinned source-tools container, with sources frozen
from configure until execution:

```sh
cmake --build /output/build --target beat_slicer_worker_probe --parallel 4
ctest --test-dir /output/build/emulator -R '^(emac|periph)$' --output-on-failure
python3 -B /source/sdk/drafts/beat-slicer/stock_probe.py --kind worker \
  --main /stock/stock-main.bin --executable /output/build/beat_slicer_worker_probe \
  --output /evidence/stock-worker.json
```

Both emulator gates pass. An initial fixture incorrectly expected `-1` for
busy/empty-range refusals; the stock routines return `-3`/`-2`, consistent with
the earlier isolated writer tests. After correcting that expectation, the
wrapper rejected the stale executable without creating evidence; rebuilding
produced the retained seven-group passing report. The earlier private failed
run is not presented as passing evidence. Historical reports remain bound to
their original source hashes; this run does not replace their provenance.

There is no live scheduler, UI completion consumer, DSP or physical unit in
these fixtures. No interrupt is injected, no cancellation or queue overflow
is qualified, and no runtime hook or live-reader service is implemented.
Hardware, audio, persistence and USB qualification remain absent.

The worker evidence's source inputs are committed at `139c3ea55002db4e639f5fcb2e4fb3d8234dbf4f`;
`tests.evidenceRevision` pins that commit. Node 24.22.1 repository validation
against upstream `4840eb336b3e64195eed1994f83ef3be79735f56` passes, including
2,519 app tests, SDK gates, lint, type checking and bundling. The fork's
`origin/main` remains at `610a934d`: the required check against that stale base
rejects inherited upstream CHANGELOG history. Validation against current
upstream is authoritative; historical changelog contents are left intact.

## Preview admission prototype (0.1.6)

`preview_guard.c` adds portable bookkeeping for the proposed shared-base
provider; see [PREVIEW_GUARD.md](PREVIEW_GUARD.md). It starts disabled and does
not install a hook, discover writers, pin PCM or provide a native lock.

- `evidence/guard-host.json`: Apple clang 17 ASan/UBSan selftest passes lifecycle,
  nested/overlapping writers, stale/duplicate/premature ends, owner revocation,
  eight-writer saturation and 32-bit ID/revision exhaustion. All 24 permutations
  of two writer starts/ends are combined with five invalidation positions:
  120 schedules. Three staged-reader cases invalidate before a pending reply,
  after a late reply, and after a completed preview; reused reader storage
  refuses the old operation's reply.
- `evidence/guard-native.json`: the same selftest compiles with pinned GCC
  16.2.0, passes the shared code-generation guard, links freestanding with no
  unresolved helpers and executes as ColdFire code with preserved registers.
  The guard object has 608 text bytes, no object data/BSS, and 48 bytes of
  caller-owned state. Compiler reports 0–4 bytes of static local stack per
  guard function; this excludes caller/return/call-chain costs and is not a
  hardware stack, cycle or latency measurement.
- `evidence/stock-guard.json`: nine source-bound stock-worker groups pass with
  a host-compiled guard observing writer entry/return and PCM writes. Added
  copy/crop/release dispatch tests include exact copy destination extent,
  nested crop/rotation lifetime, crop's counter mutation before an empty-range
  refusal, and release without a UI completion attempt. Both pinned emulator
  EMAC/peripheral gates also pass. The guard itself runs on the host in these
  stock traces; do not conflate them with the separate target selftest.

Host command:

```sh
python3 -B sdk/drafts/beat-slicer/test_preview_guard.py --output NEW_REPORT.json
```

Inside the same pinned source-tools container/mounts as the 0.1.5 worker run:

```sh
cmake --build /output/build --target beat_slicer_worker_probe beat_slicer_job_probe --parallel 4
ctest --test-dir /output/build/emulator -R '^(emac|periph)$' --output-on-failure
python3 -B /source/sdk/drafts/beat-slicer/guard_native.py \
  --output /evidence/NEW_NATIVE_DIRECTORY --executable /output/build/beat_slicer_job_probe
python3 -B /source/sdk/drafts/beat-slicer/stock_probe.py --kind worker \
  --main /stock/stock-main.bin --executable /output/build/beat_slicer_worker_probe \
  --output /evidence/NEW_STOCK_REPORT.json
```

Keep all inputs frozen through execution. The worker binary binding now covers
its C++ runner and both guard C/header inputs. A deliberately stale executable
was refused without creating a report. An initial target harness initializer
needed `memset`; explicit bounded initialization removed that dependency. A
strengthened copy fixture initially installed its write watcher before filling
test PCM; moving fixture preparation before observation corrected that test.
Only final source-matched passing reports are retained here. Historical reports
keep their original hashes and are not relabeled as current-source evidence.

No native provider is enabled. Full writer/metadata/caller coverage, live
scheduler/cancellation behavior, serialized map lookup and copying, real-unit
audio/timing/persistence, and card/browser/USB qualification remain pending.
`module:doctor` and `verify.py` still refuse publication of this unlisted draft.

The three 0.1.6 reports match source commit `f75263f3e8a7dcbf4e7f84f5e9918871b784e2ca`,
now pinned by `tests.evidenceRevision`. With Node 24.22.1 / `npm ci`, the
repository check against upstream `8965a69c` passes (2,519 app tests, SDK
checks, lint, type checking and bundle). The required comparison with the
fork's stale `origin/main` still rejects inherited upstream CHANGELOG history;
that historical file remains unchanged, and authoritative validation uses
current upstream main.
