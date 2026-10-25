# Proposed sample-editor base service

This is an owner-review proposal, not released capability. It is split from
[Beat Slicer staging #840](https://github.com/repeat98/modwerk/pull/840).
Do not merge or publish it until the reuse and event-allocation decisions below
are resolved. No hardware qualification is claimed for this split branch.

## Why it is proposed

An independently loaded module needs a safe way to propose slice starts without
retaining instrument pointers or replacing a stock menu another module uses.
The proposed base copies metadata, owns native confirmation and atomic marker
publication, and admits typed action records against the complete current
loader owner. Modules retain their own algorithms and controls.

**Beat Slicer is the only confirmed consumer.** Its recording-buffer extension
would still be the same module and does not establish a second consumer. A
synthetic test client proves interface behavior, not demand from another module.
No released catalogue subscriber is declared. Maintainer review must decide
whether another real module needs this AED SLICE list; otherwise its stock sites
should remain the module's own declared patch under the module guide's rule.
Do not invent future consumers to justify base ownership.

## Event allocation is unresolved

This snapshot appends `ot_sample_editor_actions` at provisional index 32.
[MIDI events #857](https://github.com/repeat98/modwerk/pull/857) proposes take
handlers at 32–34. Both allocations cannot ship together as written. The first
approved merge establishes the registry; the later proposal must append without
renumbering published entries. If #857 lands first, this table would follow at
35. No module package may be released against the provisional allocation.
The target descriptor test reads the registry index instead of assuming 32.
This branch is based on main, not stacked on #857 or another module.

## Boundary and scope

- `include/modwerk_sample_editor.h`: copied views, starts-only proposals and an
  explicitly aligned 64-byte action descriptor. No sample/PCM pointer crosses it.
- `module-adapters/sample_editor_service.*`: one-use source/owner token,
  revalidation, create/replacement confirmation and complete failure rollback.
- `sample_editor_actions.*`: copied labels and image-relative callbacks admitted
  against the exact current owner. Retirement withdraws menu reachability.
- `sample_editor_board.*`: the private 0.1.64 experiment extends file-backed
  Flex/Static slots 0–127 to inactive recorder buffers 128–135, and permits
  pattern playback. Recording blocks only its own edited buffer, not unrelated
  files or buffers. Empty recorder sources stay empty. Metadata work preserves
  frame/DMA interrupts; native playback/recorder qualification is in progress.
  PCM analysis, playback processing and implicit saves remain out of scope.
- `sample_editor_menu.c` and `sample_editor_hooks.s`: native menu/selection and
  waveform-worker boundaries, enabled only by the private `--sample-editor` flag.
  Ordinary beta bases leave the stock editor sites and contribution disabled.
- Loader changes carry typed table declarations, source-built C descriptor
  alignment and the machine's reviewed MCF54455 target/code-generation guard.

The five proposed stock spans are declared in `events.json`: SLICE opener
`0x40072c30`, opener dispatch `0x40072caa`, popup selection `0x4006d8f4`, selection
tail `0x4006d91c` and waveform command dispatch `0x400858c0`. Selection entries
are broader than one row; unchanged stock dispatch and pointer lifetime need
review across normal menus, not only this client.

The ordinary-recorder emulator fixtures distinguish the selected state bank
from an inactive bank retaining state 2 after Stop. An OR of both banks would
incorrectly keep editing blocked. Completed lengths come from published source
metadata, never reserved capacity. The slot counter did not advance across the
observed re-recordings; it cannot establish the whole content lifetime by itself.

## Review and verification

The SDK test is independent of Beat Slicer: authored backend/lifetime/rollback
fixtures plus a tiny generic source-built C action verify descriptor alignment.
Beat Slicer's actual controller/grid and package tests belong in its draft.
Run `python3 -B -m unittest discover -s sdk/tests -p test_sample_editor.py -v`;
the target case needs the reviewed `m68k-elf-gcc` toolchain.

Committed beta packages are stock-free metadata, not firmware images. Full
native/browser parity, unchanged stock paths with no subscriber, all base-bound
packages, companion resource checks and exact-build hardware qualification must
remain bound to their actual source. Combined #840 prototype receipts are
historical evidence for that combined snapshot; they are not relabeled as this
split branch. No physical test, Keep, flash or project/sample save is authorized
by opening this proposal.

Creation actions are grouped immediately before stock CREATE SLICE GRID in both pinned stock variants. Stock row order and callbacks are preserved, and remembered selections remain stock indices. This placement is shared policy, not a module-name special case.
