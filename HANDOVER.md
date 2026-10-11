# Handover: Octatrack no-reboot module loader (10 October 2026)

For the next agent working on this branch. Not committed; delete it once you
have taken over.

## Where

- Worktree: `/Users/jannikassfalg/.codex/worktrees/octatrack-elekloader-usb/modwerk`
- Branch: `codex/octatrack-elekloader-migration`, pushed head `2122bdac`.
- Owner rule: keep everything on this branch until it is stable. No PR;
  commit and push only.
- Read first: `docs/OCTATRACK_USB_CHECKPOINT.md`, then
  `docs/OCTATRACK_ELEKLOADER_MIGRATION.md` (hardware runs, catalogue
  modules, "Working on the unit safely", the end-user workflow and fail-safe
  sync table), `sdk/runtime/loader/README.md`,
  `sdk/machines/octatrack/elekloader/README.md`, `sdk/runtime/upload/README.md`.

## Uncommitted files in the worktree: do not commit or extend them

An experimental task was stopped part-way. It left these changes, which are
not part of the plan:

- modified: `scripts/device.mjs`, `scripts/verify-upload-wire.mjs`,
  `sdk/machines/octatrack/elekloader/{build_core.py,ep0.c,test_recipe.py,usb_bridge.py,verify_vendor_usb.py}`,
  `sdk/runtime/loader/{loader.c,loader.h}`, `sdk/runtime/upload/upload.h`,
  `src/engine/elekloader/upload-wire.ts`
- new: `sdk/machines/octatrack/elekloader/{boot.c,boot.h,boot.s,dsp_park.asm,test_boot.c}`

Ask the owner whether to keep or revert them before you start. If they say
revert: `git checkout -- <the modified files>` and delete the new ones. Build
the next work from the pushed head either way, and stage files by name so
none of these slip into a commit.

## The owner and how to work

- The owner drives the hardware with you from the terminal, not the web
  page. Steps for them must be exact and short.
- Never brick the unit. Everything done over USB is RAM-only; flash changes
  only when the owner installs an OS from the card, and only builds that
  passed `check_flash_safety.py`. Recovery: hold FUNC at power-on, MIDI
  UPGRADE over DIN with the stock `.syx`.
- The owner likes the "ponytail" style: smallest complete change, a small
  check for new logic, and end replies with what was skipped and the risks.
- The owner's unit currently runs `usbtest6` (base `d0eb5878…`), installed
  from `~/Downloads/modwerk-usb-test/` (hashes in `SHA256SUMS.txt`).
- The owner reported a stock 1.40C freeze when leaving USB disk mode with the
  cable still in, likely macOS not having ejected the card. Advice: eject in
  Finder first. A base-side guard ("EJECT ON COMPUTER FIRST") is a possible
  later item, not started.

## What works (each recorded in the migration doc with evidence)

- EP0 vendor transport (`sdk/runtime/upload/vendor.c`, TS client
  `src/engine/elekloader/upload-usb.ts`): IDENTIFY 72 bytes, DIAG v3 68 bytes,
  SUBMIT/RESULT frames. No EP0 reply may be a multiple of 64 bytes (a stale
  zero-length packet froze the unit once).
- Machine-neutral loader (`sdk/runtime/loader`, package ABI 3): C modules
  with tick/draw/key/encoder hooks, data, relocations, and patches to stock
  code applied with interrupts masked after a paused-task scan; module
  memory never reused before a reboot. Octatrack glue:
  `sdk/machines/octatrack/elekloader/runtime.c`.
- Catalogue modules: `build_ports.py` converts them with Elekloader,
  `sdk/runtime/loader/build.py --elemod` makes runtime packages,
  `verify_static.py` proves byte-for-byte equality with Elekloader's static
  link. PREVIEW VOL loaded, worked audibly and was removed on the owner's
  MKII. RECORDER LOOP FIX and PLAYMODES verified in the emulator only.
- Host time limit: 10 s without a request during an upload or trial rolls
  the trial back (verified on hardware by killing the CLI mid-trial).
- `npm run device -- status | try FILE [--seconds N] [--accept] | remove | lifecycle [--emulator]`
  (`scripts/device.mjs`), through
  `~/.cache/modwerk-upstream/venv/bin/python -B sdk/machines/octatrack/elekloader/usb_bridge.py /tmp/modwerk-ot.sock`
  (short socket path: macOS limits Unix socket paths).

## Commands

- Node 24: `PATH=/Users/jannikassfalg/.nvm/versions/node/v24.21.0/bin:$PATH` (the default shell node is 18).
- Base build: `python3 -B sdk/machines/octatrack/elekloader/build_core.py --stock ~/Downloads/OCTATRACK_OS1.40C_dist/OCTATRACK_OS1.40C.bin --upstream ~/.cache/modwerk-upstream/elekloader --output <new private dir>`,
  then `check_flash_safety.py --stock … --build <dir> --upstream …`.
- Upstream tool checkouts: `npm run upstream:tools` (Octabam pinned, Elekloader at the kit commit) in `~/.cache/modwerk-upstream`.
- Emulator: Docker image `modwerk-octabam-infrastructure:validation`. The
  `ot_emu` binary was built into the session scratchpad, which may be gone.
  To rebuild: `sh scripts/vendor.sh mc68k dsp56300` in
  `~/.cache/modwerk-upstream/octabam`, then
  `cmake -S tools/emu/ot_emu -B <out> && cmake --build <out> --target ot_emu` inside the image.
  Run: `ot_emu --image MAIN.raw --usb-host /tmp/ot-usb.sock --ms 600000`, then
  `verify_vendor_usb.py`, `scripts/verify-octatrack-vendor-client.mjs SOCK proofs.json`
  or `device.mjs --emulator …`. `ot_emu` takes one connection per run and
  takes no panel input while it holds the USB bench.
- Checks before each commit: `npm run check -- --base origin/main`
  (docs-only: `--base HEAD`). Current `main` itself fails `modules:check`
  and some tests since MIDI Scenes 0.2.5 (#394: missing qualification,
  a test still expecting 0.2.4). Compare against a clean `main` before
  blaming the branch, and never chain `… | tail && git commit`, which hides
  a failed check. Timeouts under load on this Mac pass when rerun alone.

## Next task: MODWERK LINK (owner's choice of name and next step)

The on-unit mode that gates every write over USB: physical presence
required, shows the session and state (LINKED / TRIAL / KEPT / ROLLED BACK),
and leaving it on the unit leaves upload mode and rolls back an unaccepted
trial. IDENTIFY, HELLO and DIAG stay read-only and always available. Design
notes so far: panel key codes are `row·8 + bit`; FUNCTION `0x2d`, YES
`0x31`, NO `0x32`, UP `0x33`, PLAY `0x28`, STOP `0x27`
(`~/.cache/modwerk-upstream/octabam/docs/firmware/PANEL.md`). The loader's
`ev_key` and `ev_draw` hooks show how the base can take keys and draw.
Nothing is implemented yet.

## Other open items

- Data-table sites in the loader (QUANTIZER, REPITCH, VECTOR, SYNTH need
  them; the data cache must be handled).
- Modules that add to the core's tables (CC MAP), MIDI and frame hooks.
- DSP modules (runtime DSP allocation on both cores).
- USB MIDI and USB Audio folded into the base.
- Fix `main`'s MIDI Scenes check failures (separate PR off `main`).
- Optional hardware test: the time limit's retry while playing.
