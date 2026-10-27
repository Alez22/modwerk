# STRING testing

Module version 0.8.0, Digitakt I OS 1.53 (stock file SHA-256 `9bdd44bb…cc92`) and 1.54 (`f78ba80f…3cf6`), Core 2.1. Source: [Alez22/digistring](https://github.com/Alez22/digistring) commit `b23f061a6980ba9f2db4b612ac778264b6b6aeaa` (tag v0.8.0). Firmware, linked images and emulator state stay on the developer's computer; none of it is committed.

## Evidence tier

`author-hardware`: the author ran the Modwerk build M002 (OS 1.54) on a Digitakt I for 30 minutes ([hardware-testing.json](evidence/hardware-testing.json)). The OS 1.53 build is emulator-checked only.

## 1. Source build

- `bash scripts/build-elemod-isolated.sh` in the pinned toolchain image (GCC 16.2.0, image `sha256:230c6c02…04fc`), run twice: the two outputs are identical.
- `node scripts/package-elemod-recipe.mjs … --check` reproduces both committed packages:
  - OS 1.53: `digistring-0.8.0-os1.53.elemod`, SHA-256 `76579a2fd0a3851f091138c7fb719e782003487b4aa9e30ad4727882e7659f7e`
  - OS 1.54: `digistring-0.8.0-os1.54.elemod`, SHA-256 `cf64535c89b0d93eeb6d3973c86ce321f5a6a8218fa240bc1f775c549a17fcdf`
- Source identity: [evidence/source-identity.json](evidence/source-identity.json), `e4007c2c…f8cc`.
- Not byte-identical to the author's elekloader build of the same source: that one is compiled with Debian's `m68k-linux-gnu` GCC, and its `.run` is 7,962 bytes against Modwerk's 7,886. The hardware results below name the build they ran.

## 2. Link

Core 2.1 (the catalogue's `core-2.1.elemod` and `core-2.1-os1.54.elemod`) and STRING alone, linked with elekloader's Python patcher (commit 1b40132) against each stock file. Modwerk's `linkMods` gives the identical main image for both releases.

| OS | Main image SHA-256 | .syx SHA-256 | Version |
| --- | --- | --- | --- |
| 1.53 | `b71d5f11…ab75` | `fb58c1386309ffc942df1037dde2c371b2442b8de7158881aafbdd702a48377b` | M001 |
| 1.54 | `47d6bd7b…e907` | `6f404382835d1ad0aee5ba8c32d433f554f6da5799d59cbc5763130f0b06b103` | M002 |

Memory: `.run` 7,886 bytes and `.bss` 17,168 bytes (a 2 KB delay line per track) in the shared mod RAM, 104,636 bytes left beside Core 2.1; no fast SRAM.

## 3. Screens (pinned digiemu c1b5735)

[capture.json](media/capture.json): the machine list, the SRC page and EXC turned to BOW with 48 single encoder steps, from the M002 build. The M001 build (OS 1.53) gives byte-identical PNGs with the same plan.

## 4. Hardware

Alez22, Digitakt I, OS 1.54, build M002 (Core 2.1 and STRING only), 2026-10-27, 30 minutes, flashed with `amidi` in upgrade mode:

| Check | Result |
| --- | --- |
| STRING in the FUNC + SRC list, below SLICE; SRC page names and EXC icons | Works |
| BOW, HIT, NOISE and PLUCK; DECAY and TONE | Work |
| Parameter locks and LFO on STRING parameters (STRG destinations) | Work |
| Project save, power cycle and reload | The STRING track comes back unchanged |
| Stock machines on other tracks | Play normally |
| Several STRING tracks at once | Four play without crackles; with more than four the UI lags |

Judged by ear and by the UI's response; no DSP or CPU readout (digihealth is not in this build).

Earlier, with the author's elekloader build of the same v0.8.0 source (not the Modwerk packages): S081 on OS 1.53, Core 2.1 + digihealth 1.0 (FAST AUDIO on) + STRING, worked with five STRING tracks at about 95% DSP load.

## Stock flows compared

| Flow | Result |
| --- | --- |
| Machine list | Stock machines unchanged; STRING added below SLICE (emulator) |
| Stock machines on other tracks | Normal (hardware, OS 1.54) |
| Project save, reload, power cycle | Normal (hardware, OS 1.54) |

## Still to test

- The OS 1.53 build (M001) on hardware.
- CPU load in the emulator with eight STRING tracks.
- Beside every other catalogue module on hardware. It is declared incompatible with Note Accumulator, which patches the same stock routines.
