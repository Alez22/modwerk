# Beat Slicer testing

Current draft: 0.1.1-experimental. Local checks: 23 October 2026.
Base checkout: 610a934da51b8f8518e6296493da9059b83e9a7e.
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
