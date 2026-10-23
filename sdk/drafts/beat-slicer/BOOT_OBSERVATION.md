# Full stock project observation

`boot_observe.py` connects an actual stock project/file load in the pinned
headless emulator to the host planner and marker-preparation code. It does not
install Beat Slicer, inject code, call firmware functions, edit the panel or
enable a live native reader. Both DSP cores and frame scheduling run during
load; emulator execution is paused during memory observations and planning.

Use a private disposable card created through stock, containing an original
stereo 16-bit 44.1 kHz WAV assigned to a Flex slot. Keep the card, source WAV,
project files, binaries, memory reads and emulator logs outside Git. The probe
copies the supplied card, disables write-back, verifies both card copies stay
unchanged and exports only a stock-free receipt. It refuses a stock/card hash
mismatch, an incomplete LOAD PROJECT, unsupported format, invalid allocation,
different PCM, changed tempo/markers or inconsistent snapshots.

The observed 1.40C MKII-panel setup used:

1. Create a disposable set/project and load the original WAV through the stock
   browser. Loading a slot does not assign it to the track: confirm the loaded
   slot before opening AED, then check the editor title's source kind and slot.
2. AED → FX1 opens ATTR. In this fixture, three DOWN presses select ORIGINAL
   TEMPO; RIGHT changes 120.00 to 120.25 BPM. Project tempo remains 120 BPM.
3. AED → AMP opens SLICE; plain YES opens its action menu. LFO opens EDIT.
   CREATE SLICE GRID → 4 SLICES → YES for zero-cross alignment exercises the
   real deferred search/completion path. These are stock actions, not Beat Grid.
4. Capture the complete marker table's hash before saving: 64 big-endian
   start/end/loop records, then the big-endian count. Save the disposable
   project and wait for completion, checking the expected saved files. A card
   flush only makes completed sector writes durable; it does not finish a
   firmware save that is still running.
5. Close the emulator and run the observer against that exact card and WAV.
   It starts a fresh emulator, requires the stock LOAD PROJECT completion,
   compares every PCM byte and the complete marker-table hash, then runs four
   previews (sample/project tempo × exact/smooth) and preservation preflight.

Example inside the existing isolated private mounts, serialized with other
checks and with Docker shared memory set to 256 MiB:

```sh
python3 -B /source/sdk/drafts/beat-slicer/boot_observe.py \
  --emulator /output/build/emulator/ot_emu --main /stock/stock-main.bin \
  --card /evidence/private-card.img --card-sha256 <exact-card-sha256> \
  --set-name BEATLAB --project-name '<private-fixture-project>' \
  --wav /evidence/original.wav --slot 0 --sample-bpm24 2886 --markers 4 \
  --marker-sha256 <complete-marker-table-sha256> \
  --output /evidence/new-private-observation
```

The report names the source, emulator, stock, card and WAV hashes. Raw logs
and the copied card remain private in the output directory. The source sample
rate comes from the verified WAV and matching loaded frame extent, not a new
native rate getter. Other rates/encodings, replacement failure, Static streaming,
concurrent writers, physical audio/save/reboot behavior and Beat Slicer's
Apply/Undo and USB lifecycle remain unqualified.

The initial exploratory session also attempted borrowed stock lookup calls.
The emulator refused them before execution because its main task was not in
the required parked state. Those calls provide no lookup evidence. The
observer uses bounded memory reads and never bypasses that guard. Full stock
lookup execution remains covered separately by the compiled isolated probes.
