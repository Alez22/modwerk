# Ringmod SC testing

## The key bus reader (0.1.0-experimental, 20-21 October 2026)

Source: branch `claude/ringmod-sc-keybus` (on `claude/keybus`, the base's key bus, PR #750), module source
`e2e84eb393c7…`; local, on a Mac with the octabam toolchain and the tester's own OS 1.40C. **Nothing in this section
ran on hardware.** What changed from the previous build (`84b4529d`, history below): the dispatcher tap, its hook and
want words are gone; the key is read from the base's key bus at the same layout; a KEY or MODE change is adopted with
the key's state cleared and the depth ramps back from the next call (the ten-call wait for the tap is gone); with no
live key bus on its core (a card image) the depth stays at 0; fx id 0x06; `keystep.s` removed; KEY's track labels
padded (" T1 "). 361 → 270 DSP words.

**Render gate.** `python3 verify.py` (dsp_host; `tools/keystub.asm` publishes the key where the base's bus does; the
memory image carries the bus's live seed marks). All gates pass:

| Gate | Result |
| --- | --- |
| No instruction decodes as mpysu | pass, 270 words |
| No live key bus (no seed mark, a wrong mark, a counter of 4, only the other core seeded): both modes, both key paths | output equals input bit for bit |
| KEY OFF, a KEY byte of 100, DPTH 0 in both modes, a silent key in DUCK | bit for bit |
| DUCK and RING against the float model, 384 settings | worst error 3.14e-05 of full scale |
| A steady 55 Hz key: swing once settled; a decaying key: largest dip | 0.0000 at REL 0 and 45; 0.00000 |
| DUCK ATK 32 on a key that steps on: 63% down | after 203 samples |
| The key in the other core's window; the module on the other core (T2: T1 local, T7 across) | the same samples |
| A trig split (5): equal once the ramps have landed; a key dispatched after: one block late | pass (1.3e-07, 1.7e-07 against the model) |
| `-guard -dirty 0x5a` | no write outside the instance at all |
| MODE / KEY change mid-render: the model's fade, no step | pass; largest step 0.018 against an input of 0.25 |
| Each continuous knob turned one step every two blocks under a tone | loudest -91 dBFS at the block rate (limit -70) |

**Against the previous build, sample for sample** (`compare.py`, kept privately; dsp_host, both builds fed the same key
by the same fixture). 417 renders: the 384-setting sweep, the other-core window, both cores, trig splits at 5 and 11, a
late key, a noise key, a dirty state, five mid-render KEY/MODE changes and every knob's zipper schedule. The new source
equals `84b4529d` with its wait constant changed from 10 to 1 in all 417. Against `84b4529d` as it was, 412 differ, each
only from the first adoption on: the depth ramps in nine calls earlier and the key's low-pass and follower start from
then (the five equal ones are the bit-exact passthrough cases). So the audio path is the old one; the only intended
difference is the wait.

**Stress.** `python3 tools/stress.py 30`: eight instances and the fixture on one core for 30 s, `-guard -dirty
0x5a`, 27,561 knob moves (MODE and KEY included), four instances on a trig split: 8 of 8 instances wrote nothing
outside their blocks, no hang, no sample on the store's limit; dearest block 8,688 instructions.

**Cycle count.** `tools/build/cycle_count.py` on a scratch remix carrying RING_SC: 63 cycles/sample in the dearer loop
(DUCK, its bsr counted), RING 32; unchanged from the previous build (the loops are the same code).

**Performance record** (`evidence/performance.json`; `modules/ring-sc/perf.py`, after LOFI2's, on a private native
image `c2f9ccc2…` with the key bus's seed marks written into both payloads' dumps so the dear path runs; stock effects
on the original image; executed instructions/sample, null stub subtracted, not chip cycles):

| Effect | Worst unsplit | Worst with trig splits |
| --- | --- | --- |
| RINGMOD SC, dearest DUCK | 67.69 | 80.56 (split at 1) |
| RINGMOD SC, dearest RING | 30.94 | 38.06 |
| COMPRESSOR | 67.44 | 72.06 |
| DARK REV | 193.25 | 242.38 |
| SPRING REV | 257.50 | 314.19 |
| DJ EQ | 293.38 | 330.94 |

`benchmark_stock_dsp.py` in the same session gave the same unsplit stock figures (COMPRESSOR 67.4, SPRING REV 257.5,
DJ EQ 293.4). The base's key bus tap is not in these figures: the base charges it to RINGMOD SC on both cores while
it is installed, 41 executed instructions a sample a core for the four tracks (counted from its source), at 7/4.

**Stress project** (`perf.py stress`, the load `stress_project.py` describes driven straight into dsp_host on the same
image, 32 s plus a 2 s tail, `-guard 0x4000 -guard-shared -dirty 0x5a`, three LFOs a track on DPTH, KLPF and REL, every
slot redrawn each sixteenth at 120 BPM, KEY and MODE included, trig splits on six tracks):

| Layout | Result |
| --- | --- |
| `--both`: RINGMOD SC on FX1 and FX2 of all eight tracks (eight a core), 14 slots changed per step and track | host exit 0, no hang, 16 guarded instances, 0 stray write regions, 0 clobbers; per-core peak 628.2 / 636.8 |
| DJ EQ on every FX1, RINGMOD SC on FX2 (four a core), 12 slots changed per step | the same; RINGMOD SC 0 stray regions and 0 clobbers (DJ EQ writes its own scratch); per-core peak 1622.8 / 1623.1 |

`npm run perf:audit -- check evidence/performance.json`:

| Check | Result |
| --- | --- |
| record | dsp record for ring-sc@0.1.0-experimental |
| cycles | 8 x 63 = 504 of 3120 per sample per core (16%), measured 80.56 per instance |
| stock benchmark | 80.56 vs COMPRESSOR 72.06 (1.12x); the dearest stock effect is 330.94 |
| stress | 8 per core, eight tracks, 3 LFOs and 14 locked slots, 32 s, no clobber, no hang |

No check failed. With the base's key bus tap (41 a core while installed) one instance's footprint on its core is about
122 executed instructions a sample, under half of SPRING REV's worst.

**The USB package** (`public/octatrack-modules/ring-sc/0.1.0-experimental.mwrm`, 2,108 bytes, sha256 `8063657f…`, built with the padded KEY labels):
ABI 9, `requires` the key bus (8), four read claims (Y $800+$200 on each core, Y $33dfe+$202 and $3bdfe+$202), no hook
entries; the relocatable DSP package (270 words, four-origin proofs) from the isolated toolchain build, its page recipe
(the KEY and MODE formatters, the mode renames), 81 executed instructions a sample, 19 state words, name "Ringmod SC".
Built as `module_packages.py` builds an entry with `requiresFeatures` (build.py --dsp, then abi9.py). Checked:

- `module_packages.py`'s two stock-free scans against the tester's 1.40C: no shared run at all. (With KEY's plain
  labels OFF/T1-T8 the formatter's strings repeated a 25-byte stock string list and both scans refused it; hence the
  padded labels.)
- The on-demand board host test (`test_resident_engines_board.py`, at base 0321cf3b's source; the merge of main's Quant Live Rec that made it 163ba0e3 changed no board code) with these exact bytes (the padded-label package `8063657f…`) as its reader (module id
  swapped for the fixture's) and the base's claim admission (resident_base.patch's `modwerk_machine_dsp_claims_admit`,
  copied into the fixture): modes 39-42 pass: alone (bus placed, reset, enabled, priced), beside Sidechain in both
  orders, refused while the tap's price does not fit, removed mid-reset and installed again (fresh reset), a stuck bus
  engine refusing a second reader; and modes 43-46: after its run its removal scrubs the window's seed before the window
  is free, a second reader arriving during the disable or the scrub is told to retry, Sidechain arriving mid-scrub gets a
  fresh reset, a lagging core holds the other core's enable back; and modes 47-48: a core left unknown refuses readers
  (CONFLICT) and keeps the other core's bus off, a slot buffer over the window holds the scrub back while readers retry.
- The site's module-set checks (`module-set.ts`) accept the manifest entry and the package.

**Key latency method** (`ringlag.py`, for the MKII capture; RINGMOD SC has no MON): RING, DPTH 127, KLPF 127, the
receiver playing the key's own audio; against the module's real DSP in dsp_host it recovered 0 (key before) and 16
(key after) exactly, correlation 1.0000. The 32-sample cross-core case needs two cores: the key bus's own interpreter
test and its MKII runs measured it, not with this module.

**Native comparison.** `npm run module:verify -- ring-sc` on the tester's 1.40C (after main's Quant Live Rec and LOFI2 joined the
pool): 138 selections, 56 native module-owned images match (24 identical outright, 32 outside the platform writes), 82
refusals agree, 0 mismatches; native pairs recorded (`sdk/native-comparisons/ring-sc.json`). It needed `static-dsp.json`'s
RING_SC row; it was run with a local, uncommitted qualification stub, because the catalogue offers a module only with
its qualification record and that waits for the hardware run (with the stub, `module:doctor ring-sc` reports every
integration point green). A card image has no key bus, so those images carry an effect that passes audio; the configurator itself refuses card firmware with RINGMOD SC (USB-only, the site's rule for a package that requires a base feature).

**Not tested (this source):** all hardware behaviour (install, the bus and its price on a unit, key latency, DUCK and
RING by ear, both cores, locks and LFOs, Part and project reload, removal and a missing module, a power cycle), the
sound-quality audit (`fx:audit`; the sample loops are unchanged from the build it ran on), screenshots of this build
(the pages are the same; KEY's labels now carry spaces), MKI.

---

## History: the previous build (own dispatcher tap, `84b4529d` and before)

Everything below is about the earlier source, which carried its own key tap at the dispatcher and conflicted with
Sidechain Compressor. Kept as the record of that source; none of it is evidence for the key bus reader except where
the section above says the code is the same.

Source: branch `claude/ring-mod-sidechain-effect-e0027c`, local only, on a Mac with a local octabam toolchain and the tester's own OS 1.40C. **Nothing here ran on hardware.**

**15 October 2026 rework** (after the user found the duck buzzy and weak): KGN and XOVR removed, a fixed 4x key boost, the follower fed by the key's peak over the last 13-26 ms instead of |key| itself, KLPF on an exponential law, REL default 45, and HOLD (the peak window, 0.7-47 ms); page 1 is KEY, DPTH, KLPF over ATK, HOLD, REL. The render gate, stress run, cycle count, native build and screenshots below are from that source. The emulator results on a built image (key lag, both modes, locks and LFOs, the tap's on-demand publishing, stock audio) and the sound-quality audit are from the earlier DSP at `edf88a4c69` (12 October) and were not rerun; the tap and the key paths they exercise are unchanged.

### Commands and results

**Render gate.** `python3 verify.py` (dsp_host, the module beside `tools/keystub.asm`, which publishes its audio the way the module's own dispatcher tap does). All gates pass.

| Gate | Result |
| --- | --- |
| No instruction decodes as mpysu | pass, 361 words |
| KEY OFF, a KEY byte of 100, DPTH 0 in both modes, a silent key in DUCK: output equals input bit for bit | pass |
| DUCK and RING against the float model, 384 settings (ATK, REL, KLPF 127/90/30/0, DPTH, HOLD 34/0/127 in DUCK) | worst error 3.10e-05 of full scale |
| A steady 55 Hz key at 0.1, DPTH 64, on a steady input: swing of the output once settled | 0.0000 of the input at REL 0 and at REL 45, HOLD 34 (following \|key\| itself swung the gain from full to none 110 times a second) |
| A 55 Hz key decaying with a 100 ms time constant: largest drop of the output while the gain recovers | 0.00000 of the input: it recovers without dipping again |
| DUCK ATK 32 on a key that steps on: 63% down | after 203 samples (4.6 ms) |
| A key in the other core's publish region gives the same samples | pass |
| The same module placed on the other core (T2): T1 local and T7 across give the same samples | pass |
| The module's own tap, run in the fixture's place, gives the same samples (this core's bus only) | pass |
| A block split by a trig gives the same samples once the knob ramps have landed | pass |
| A key track dispatched after this one is heard one block late | pass |
| `-guard -dirty 0x5a`: no write outside the instance but its key track's want word | pass |
| A MODE or KEY change mid-render follows the model's fade and eight-block wait | pass; largest output step 0.018 against an input of 0.25 |
| Each continuous knob turned 20 to 110, one step every two blocks, under a 438.75 Hz tone | no block-rate step above the steady render; the loudest candidate measured -91 dBFS (limit -70) |

The step measure is `verify_knob_clicks.py`'s, reimplemented in the gate because that tool cannot feed a key. Checked on a synthetic block-rate step it read -59 dBFS where arithmetic gives about -52, so it reads low by several dB; the margin to the limit is correspondingly smaller than 9 dB.

**Stress.** `python3 tools/stress.py 30`: eight instances and the fixture on one core for 30 s, `-guard -dirty 0x5a`, 27,561 scheduled knob moves (MODE and KEY included), four instances on a trig split. Eight of eight instances wrote nothing outside their blocks but want words, no hang, no sample on the store's limit. Dearest block 8,631 instructions: at most 67.4 executed instructions a sample per instance, the fixture included (half the instances in DUCK with KLPF at different settings; HOLD among the moved knobs).

**Efficiency pass, bit-identical** (15 October 2026): short immediates, parallel and register-to-register parallel moves in the sample loops, the depth ramp inlined, redundant moves and tests dropped, the tap's pointer arithmetic simplified; only forms stock payloads already run (no `rep`, no plain (Rn+Nn) Y moves). 428 to 361 words, DUCK 70 to 63 and RING 36 to 32 instructions a sample. Against the previous source (`09de2318`), every render case of the gate (420 runs: the 384-setting sweep, both cores, both key paths, trig splits at 5 and 11, a late key, the module's own tap, the guard on a dirty state, MODE and KEY changes mid-render, every knob's zipper schedule) gave identical output sample for sample, and the tap, run with seeded want words and cold and warm counter marks on six tracks, left identical Y memory over the key bus and both cores' windows. Not rerun on a built image under `ot_emu`.

**Key level.** `ot_emu` on RINGSC02 (the same key path as RINGSC04), a 0 dBFS tone into a THRU key track, the key bus read with `--dsp-peek`: at AMP VOL 64 (the default) the key peaks at 0.254 of full scale, at AMP VOL 127 at full scale. So the fixed 4x boost brings a full-scale key at the default AMP VOL to full. A sample track's playback level was not measured.

**Native build.** A private copy of `sdk/octabam`, remix `x-rmsc`: RINGMOD SC with every stock effect but LO-FI, whose span holds it (image RINGSC05). `make image` builds. RINGMOD SC places 361 code words on each core (about 85 of them the tap; 176 words of LO-FI's span left) and its hook at the dispatcher (`P:0x4a7` on payload A, `P:0x29c` on B). One source serves both cores: it reads the track being dispatched (X:$420) to tell them apart. `cycle_count.py`: 63 in the dearer sample loop (DUCK, with its subroutine call counted; RING 32); the tap is not in that figure. Earlier composed builds (with Output Matrix, Analog BD, TapeHead, LOFI2 and Quantize Live Rec) were on the earlier DSP. Other selections, the browser builder and `module:verify`: not tested.

**Screens.** `scripts/capture-module-ui.py` on RINGSC04 with the plan in `media/capture.json` (KEY now turned four detents: one no longer moves it). The four captures in `media/` show the new layout.

**The tap publishes on demand.** `ot_emu --dsp-pcwatch` on the tap's first copy loop on core 0: no arrival in a run with no RINGMOD SC on any track, arrivals in a run with T6 keyed by T5. A reader stays silent for ten calls after KEY or MODE changes, so it never hears a bus the tap has not yet filled.

**Stock audio with the tap in place.** The same project with no effect on any track, on this image and on the earlier image that carried Sidechain Compressor's tap: MAIN left identical over 4,814 samples. A comparison against an image with no tap at all was not run.

**That image under `ot_emu`** (the ColdFire port, both DSP cores, the module's own tap; no Sidechain Compressor in the image). THRU machines fed mono noise, MAIN left read back, the gain change correlated against the key at each lag:

| Case | Lag, samples | Correlation |
| --- | --- | --- |
| DUCK on T2 FX1, KEY T1 (same core, key first) | 0 | 0.9995 |
| DUCK on T6 FX1, KEY T5 (the other core's same-core case) | 0 | 0.9995 |
| DUCK on T5 FX2, KEY T6 (same core, key after) | 16 | 0.9995 |
| DUCK on T6 FX1, KEY T1 (across the cores) | 32 | 0.9995 |
| DUCK on T3 FX1, KEY T7 (across, the other way) | 32 | 0.9995 |
| DUCK on T2 FX2, KEY T1 | 0 | 0.9995 |
| RING on T2 FX1, KEY T1 (against the signed key) | 0 | 0.9999 |
| RING on T6 FX2, KEY T1 | 32 | 0.9999 |
| RING on T1 FX2, KEY T8 | 32 | 0.9999 |
| DUCK on T2 at DPTH 127 and on T3 at DPTH 64, both KEY T1 | 0 | 0.9995, with the summed depth the two settings predict |

The emulator runs the cores in a fixed relation; the unit's cross-core timing is not measured.

**Parameter locks and LFOs on that image** (`ot_emu`, the sequencer running, the gain reduction read per 512 samples against the key):

| Case | Result |
| --- | --- |
| T2 FX1, KEY T1, trigs on steps 1-5; step 2 locks DPTH 0, step 3 locks KEY OFF, step 5 locks DPTH 64 | reduction 2.86, 0, 0, 2.86, 1.44 on the five steps: each lock lands on its step and the next unlocked step returns to the set value |
| LFO 1 on DPTH (speed 70, depth 127), DPTH 64 | the reduction climbs smoothly from 1.51 to its ceiling of 2.86, no steps between windows |
| LFO 1 on KGN (a knob since removed) | climbs smoothly from 3.3 to 13.8 |
| LFO 1 on KEY at full depth, KEY T1 | KEY is carried past T8, which reads as OFF: no reduction, the track passes, nothing faults |

Loading these projects from the card is the only persistence shown: the stored KEY, MODE and knob bytes come up as saved. Saving from the panel and a power cycle were not run.

**Panel.** `scripts/capture-module-ui.py` on that image: the FX1 chooser lists RINGMOD SC; the main page drew KEY, DPTH, KGN, ATK, REL, KLPF; in RING KEY, DPTH, KGN, "-", "-", KLPF; SETUP drew MODE and XOVR. Those captures were replaced on 15 October (Screens, above).

**KEY's step** (`ot_emu`, a later image with `keystep.s`, 13 Oct 2026; turns of one detent 100 ms apart, then of four):

| Case | Result |
| --- | --- |
| Before `keystep.s`: RINGMOD SC chosen on SETUP, FX1 pressed, KEY turned | a track a detent: the knob record still held the last staging (step 256, count 128) |
| Before: the same after AMP then FX1 | the stock select step (819, count 9): single slow detents do not move it, four detents move one track |
| With `keystep.s`: chosen on SETUP, FX1 pressed, KEY turned | single detents OFF, OFF, OFF; four detents T1, T2, T3, T4; eight back, T2 |
| With it: DPTH turned 3 back, ATK 5 up | 124 and 5: plain knobs still move one a detent |
| KEY turned with a trig held (a lock), with and without it | four detents move four tracks in both images: that branch of the knob routine is not changed |
| Stock THRU INAB, for reference | eleven single detents 250 ms apart do not move it |

**The gate** (13 Oct 2026). `keystep.s` now acts only when the descriptor the knob routine resolved is RINGMOD SC's clone (`CLONE_RING_SC`); 68 B. Built alone with every stock effect but LO-FI (whose span holds the 426 words; image RINGSC01, the earlier DSP), then swept under `ot_emu` against a control: the same image with the stock instruction put back at 0x40055140 (3 bytes differ). Each case turns all six knobs 1, 1, 3, -2, 4, 4, -8, 5 detents and reads the knob record and value, on first visit after choosing the effect on SETUP and after AMP then back:

| Case | Result |
| --- | --- |
| SRC, AMP and LFO main pages; the nine stock effects on FX1, the thirteen on FX2; RINGMOD SC's other five knobs | 302 of 306 sweeps identical to the control: records and values |
| RINGMOD SC KEY, FX1 and FX2, first visit | gated: record restaged to step 819, count 9, single detents leave KEY on OFF, about four move it a track; control: 256/128, a track a detent |
| The same after re-entry | same steps in both (819/9); only the starting track differs, carried over from the first visit |

On the user's MKII (OMXATS21, the ungated routine, 13 Oct 2026) KEY was reported to feel right; the gated build has not been on the unit. Not checked: the unit with the gated build.

### Sound quality

`npm run fx:audit`, the nine signals rendered through the module with dsp_host and the fixture, DPTH 127, KGN 45 (about the fixed 4x now used). These renders were made on the earlier DSP, which followed |key| itself, and have not been repeated.

| Render | Result |
| --- | --- |
| DUCK, steady key, ATK 127, REL 127 | passes: aliasing below -140 dBc, harmonics -119 dBc or lower, DC -100.6 dBFS, idle digital silence |
| RING, steady key (rendered when RING still had a GAIN knob, set to 4x; since removed) | passed at -12 dBFS; at -1 dBFS that 4x gain put the output on the store's limit. Not re-rendered without it |
| DUCK and RING with a 55 Hz key | the audit fails on "aliasing" of -2 to -45 dBc. These are the sidebands the key puts beside each tone, which is what the effect is; the audit's guide says to judge with modulation off |

So with a steady key the effect is clean, and it adds no DC and leaves nothing after the input stops (it has no memory of the audio). A moving key creates sidebands by design, and those above 22.05 kHz fold back; KLPF limits how high the key reaches.

### Performance

`npm run perf:audit -- check evidence/performance.json`:

| Check | Result |
| --- | --- |
| cycles | 8 x 63 = 504 of 3,120 per sample per core (16%), measured 67.4 per instance (the fixture included) |
| stock benchmark | 67.4 against COMPRESSOR's 67.4 (1.00x); SPRING REV measured 257.5 and the dearest stock effect, DJ EQ, 293.4 (`benchmark_stock_dsp.py`, same host, earlier run) |
| stress | **does not pass the audit**: it asks for eight tracks, three LFOs a track and twelve locked slots from `stress_project.py` and `pressure.py`. the repository's stress project was not built for this module (it was first blocked by a tool limit while the module still needed Sidechain Compressor, and has not been retried since). `tools/stress.py` above was run instead and is what the record states: one core, no LFOs or locks, and without the tap |

Figures are executed instructions in the emulator, not hardware cycles. The key tap is not in them: by a count of the source it costs each track about 35 instructions a block when nothing listens to it (about 2 a sample) and about 75 more for each of its two copies when something does. It was not metered.

### Stock flows

Not tested. The module changes no stock flow by design: it adds a row to the effect choosers and nothing else.

### Not tested

All hardware behaviour. Scenes and the crossfader, saving a Part or project from the panel, a power cycle, an LFO walking KEY between tracks, MKI, the browser builder, `module:verify`, and compositions other than the one above.
