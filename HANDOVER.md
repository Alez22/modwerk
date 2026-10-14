# Handover: all twenty Octatrack modules on the dynamic loader (14 Oct 2026)

This file lives only on the branch `handover/all-twenty-20261014`. Never merge it into main.

Read AGENTS.md, docs/ADD_A_MODULE.md, docs/module-guides/README.md, sdk/machines/octatrack/EVENTS.md and sdk/octabam/AGENTS.md before changing code.

## Goal
All twenty active Octatrack modules install and run alongside each other through the dynamic USB loader, within memory and cycle limits. The loader admits or refuses a selection by each module's declared per-voice cost against the per-core DSP budget and the module pool.

Every module is fully independent:
- One package per module, with no groups, no per-combination variants, and no module that knows another.
- Shared stock code goes through the Elekloader model only. The base owns events (subscribe with an order, plus "take" and "raise" events) and tables (contribute).
- A module author declares `subscribe` and `contribute` entries in `runtime.json`. `npm run modules:compat` refuses raw patches on registered sites with an actionable message.

The beta ships all twenty or nothing. Spectrum, Modulation, Character and MIDI Scenes are paused and out of scope.

## Owner decisions (14 Oct)
- **Approved releases:** Mini Verb 0.2.2, Repitch 0.2.0, POLY8 0.3.0, and Mute Modes 0.2.1 (not 0.2.0). Credit the original Mute Modes author in its PR. The OT page screenshots may be kept from the previous versions.
- **FM Synth** stays at 0.1.2 for the beta.
- **USB Audio** is built into the beta base, with no option.
- **Preview Vol and Repitch 0.2.0** go back into the loader packages.
- **Analog BD removal** converts every known Part copy back to FLEX and fails closed. The remaining risk for unknown temporary copies is documented.
- **Pushes and merges:** agents may push working branches. Pull requests into main are merged by the owner.
- **Open question for the owner:** may the strict stock-free scan ignore runs made only of 0xFF (unused hook words), as it already ignores 0x00? Until the owner answers, subscriber packages fail that scan. Don't change the scan without the owner's yes.

## Branches
| Branch | State |
|---|---|
| `codex/octatrack-loader-integration` (4f3cb7c5c) | Main is merged in, including the compatibility gate #579 and the guide #580. Also merged: the events releases, `lane/releases-base` (Tape Echo binding refreshed, public base with USB Audio), `lane/mute-modes` (raised event `ev_mute_keep`), `lane/sidechain-matrix` up to cfa5364a4, the open DSP buffer policy and the generic source-stage DSP charge. |
| `lane/sidechain-matrix` | **Not fully merged.** Each module is one package. Output Matrix copies its stock spans, and the base keeps MATRIX across a power cycle. Sidechain contributes a KEY page to COMPRESSOR. The emulator `controllers` scenario is written but has not run. |
| `lane/machine-events` | **Not merged.** POLY8, VECTOR, FM Synth and Scale Quantizer build as independent packages. Two tables (`ot_machines`, `ot_sequencer_rows`), take events and a base machine registry. The compatibility gate passes with 0 relations. Review its `build_core.py` and `loader.c` changes at merge. |
| `lane/analog-bd` | **Not merged.** Declared DSP price, Part restore and board retirement glue. The package is built through the machine-events path once that lane is merged. |
| `codex/miniverb-cost` | Mini Verb 0.2.2 is ready. It is blocked only by a Tape Echo binding fix: the binding must accept a rebuilt, validated USB package manifest. The owner approved that fix. It is on branch `claude/tapeecho-binding-usb-rows` (06030eee5), and its own tests pass (60/60). Still to do: apply it on `codex/miniverb-cost` and run `npm run modules:check` and `npm run module:doctor -- miniverb`, then open two PRs into main, the binding fix first and Mini Verb second. |
| `claude/events-repitch`, `claude/events-poly8` | Owner approval records. Their PRs into main wait for a public base built with site events. |
| `claude/events-mute-modes` | Its 0.2.0 commits must not ship; 0.2.1 from the integration branch replaces them. |

## State of the integration branch at 4f3cb7c5c
- **Passing:**
  - SDK suite: 361 tests OK.
  - `modules:compat`: 0 problems.
  - Focused vitest: 332/333.
  - Size: MAIN is 1,245,840 B on the plain base and 1,246,713 B with `--site-events`; the limit is 1,310,720 B.
- **Known failures:**
  - The committed public base is stale (`octatrack-base.test.ts`). Regenerate it with `npm run octatrack:base -- --usb-midi --usb-audio 'USB AUDIO OUT TRACKS MAIN CUE' --write`. This is a native build, so run it locally in Docker.
  - The Tape Echo browser-preservation binding is probably stale again after 26b107ffd. Rerunning the executed parity proof needs the local OS file.
  - Repitch 0.2.0's published package and every `--prepare-ports` run fail the strict scan on the 0xFF hook words, which is the open owner question.
  - `test_recipe.py` `test_runtime_bookkeeping_on_the_host`: `modwerk_machine_reference` is defined twice when `loader.c` and `runtime.c` are compiled together.
- **Not yet wired:** nothing calls `modwerk_dsp_source_claim` yet. The machine registry in `lane/machine-events` must call it before it assigns a priced machine.

## Next steps, in order
1. **Merge into the integration branch, in this order:**
   1. the rest of `lane/sidechain-matrix`;
   2. `lane/machine-events`. Note that `ev_mute_keep` takes event index 7, so the machine events shift by one and `machine-recipes.json` must be recaptured;
   3. `lane/analog-bd`.

   Then build the Analog BD package through the machine-events path.
2. **Run the checks:**
   - full SDK suite: `python3 -X utf8 -B -m unittest discover -s sdk/tests`;
   - `npm run modules:compat`;
   - vitest on `src/dev` and `src/engine/elekloader`;
   - `npm run check -- --base origin/main`.
3. **Browser side:** `src/engine/elekloader/module-set.ts` must handle event and table packages.
4. **Docs:** add the section on events and tables to docs/module-guides/README.md, written for outside module authors.
5. **Releases:**
   - Mute Modes 0.2.1 approval record.
   - `octatrack-base.mjs` needs a site-events flag, so a public base can be built with the events.
   - Fix `module-verify` so it runs under plain Node: `import.meta.env.DEV` in `src/engine/protocol.ts` breaks it.
6. **Local only, not possible in the cloud:**
   - Native and private builds, package preparation against the user's OS, emulator runs and hardware all need the owner's private Octatrack OS file and the connected unit.
   - Use Docker's `modwerk-source-tools` image (binutils 2.47) for anything checked against recipe or image pins.
   - Hardware needs a new power-cycle OK from the owner, and never a flash without asking.

## Rules
- Never commit firmware, stock-derived bytes or tables, dumps, saved sets or native images.
- Never edit generated files by hand. Regenerate pins and hashes with their tools.
- **Keep every guard in place:** stock scan, bootloader and site guards, source proofs, the protected public base recipe and the compatibility gate. Capability 64 and default admissions stay closed.
- **No fabricated evidence:**
  - label synthetic fixtures as synthetic;
  - keep modelled cycles, executed instructions and hardware timing apart;
  - never relabel an old receipt as evidence for current source.
- Fail closed. Make the smallest complete change, and give new logic a focused test.
