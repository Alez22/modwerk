# System

Read [the module guides index](README.md) first.

**Applies to** modules with manifest `category: system`: behaviour that belongs to the project or system menus rather than to a track or an effect. No module uses this manifest category yet; the library shows [Scale Quantizer](../../sdk/octabam/modules/quantizer/README.md), [Repitch](../../sdk/octabam/modules/repitch/README.md) and [Preview Vol](../../sdk/octabam/modules/previewvol/README.md) under System, so read their READMEs as the nearest examples and also [machines.md](machines.md) (project machines) and [playback.md](playback.md).

## Behave like the instrument

- [ ] **Put the setting in the stock menu where it belongs.** Scale Quantizer's SCALE, ROOT and GLIDE rows sit under PROJ → CONTROL → SEQUENCER. Do not add a top-level screen.
- [ ] **A way to turn it off that restores stock behaviour exactly.** Test OFF against an unmodified build.
- [ ] **Defaults are stock behaviour,** so adding the module changes nothing until the musician changes a setting. Say so.
- [ ] **Persistence is honest.** Settings storage today is "nowhere, or a private file", and the proposed shared project store is not implemented ([MODULES.md, Settings on the card](../../sdk/octabam/docs/remixer/MODULES.md#settings-on-the-card)). Do not invent a format. State whether your setting survives Part Save, project save and load and power cycles, and test it.
- [ ] **A project saved with the setting loads on a build without the module.** State what the musician sees. **Verify.**
- [ ] **Say who is affected:** which track types, which models (MKI and MKII key sequences differ), which existing projects.
- [ ] **No effect slot and no new knob** unless the feature genuinely needs one. The README says so.
- [ ] **Timing-related settings** follow [sequencing.md](sequencing.md).

For a one-shot sample editor, preserving marker starts is only part of preserving
the sample: retain complete slice end/loop records and establish whether adding
a sorted marker renumbers slice locks. Resolve stock minimum-length and
working/saved-copy behavior before enabling Apply. Bind preview to sample,
content, markers, trim and chosen tempo; a stale or cancelled preview must not
write. Quiet marker boundaries are not evidence of click-free playback.

Establish menu-pointer lifetime before adding a row: stock menus can retain
label, callback and selection storage after their opener returns. Keep that
storage base-owned and make removal retire every reference before reclaiming
module memory; a callback that is not currently running can still be retained.

## Integrate

- [ ] `sdk/catalog.json` entry, thumbnail, `resources.impact`, README sections, tutorial and screenshots of the menu path, with exact button sequences.
- [ ] If the library should group it under System while its manifest says otherwise, that is a one-line override in `src/catalog/modules.ts`, not a reason to change the manifest category.
- [ ] `npm run module:verify -- <id> --os <your 1.40C>` and `npm run module:doctor -- <id>` are green.

Compile portable C with the pinned freestanding ColdFire toolchain early and
inspect unresolved symbols (`m68k-elf-nm -u`) before claiming native readiness.
Host compilation can hide compiler-generated multiply/divide and memory helpers;
an object file alone does not prove that a module links. Use the shared
`sdk/runtime/m68k_codegen.py` flags and object guard too.

## Digitakt and Digitone

Settings rows come from the core's `ev_settings` event: add rows with `core_additem(menu, row)` and claim each row (`settings:FAST AUDIO`, for example) in `platform.claims`. Rows are claimed resources, so two mods cannot add the same one ([Digitakt guide](../../sdk/machines/digitakt/README.md)).
