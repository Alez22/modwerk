# Package-carried stock-DSP hooks and DSP memory claims (design, for owner review)

Status, 20 October 2026: a proposal, implemented locally with option B (the base-owned key bus) chosen: first on
`claude/package-dsp-hooks` (old main, 15-16 October), now redone on `claude/keybus` from main `e370b78e` after the
review below. The owner has not reviewed it: the questions at the end are open, and the base, the loader ABI and the
receiver change only on that branch until he does. Hardware facts are quoted from the documents named; nothing new was
measured on a unit for this note.

## Review against main `e370b78e` (20 October 2026)

What main changed since the first implementation (based on `24a1ece8`), as far as it touches Sidechain Compressor, its
key window, the resident and on-demand DSP engines, the controller board, DSP placement or a ledger:

| Change | What it does | Effect on the key bus |
| --- | --- | --- |
| #640 | Engines on demand; Sidechain's key phase rule (`resident_dsp.REVIEWED`): a core not yet seeded adopts the other core's counter | Already the base of the first implementation; the tap the key bus takes is this reviewed text. |
| #661 | The op-10 CAS reloads `hookready` before clearing a disabled feature's ready bit | The fix the first implementation was rebased on; on main as written. |
| #670, #721 | `loader.c`: installing Play Modes or FM Synth no longer stops the DSPs; loader and host test fixes | Textual conflicts with ABI 9 in `loader.c`, `host_test.c` and the loader README only. |
| #697/#703, #733 | E-Verb 0.1.2 and Mini Verb 0.2.3 end their FX2 rings at `+$3DFD` (`buffer_words=15870`, modulus `$3dfe`), so they stop exactly where Sidechain's window starts (`+$3DFE`) | The window stays where it is ($202 words from `+$3DFE` of the bank-track-3 FX2 slots: Y `$33dfe` core A, `$3bdfe` core B). Not one word below it is free beside those effects, so the 15 October layout of the gated follow-up (want words at base-10..base-3 = `+$3DF6..+$3DFD`) is dead (below). |
| #698, #731 | The effects guide names Sidechain's window as a trap; card builds refuse an effect whose declared FX2 buffer reaches a range another module declares in that slot (`module-pairs.py slot_tail_meetings`); over USB the base refuses such a buffer per block (`mw_hook_buffer_permitted_held`, `stock_hook_resources.c`) | The USB rule is the one the ledger generalises: with the key bus, the window is refused to a buffer while Sidechain **or any reader** is installed. Card builds are unchanged: the key bus is a USB base feature, Sidechain's manifest still declares its window for the card ledger. |
| #705 | Output Matrix 0.1.1 (smaller core-0 DSP, the LEV label) shipped by rebuilding the base and its trust rows | The "Output Matrix's next version" half of the problem above is solved the old way; package-carried hooks remain only a proposal (sections 1-5). The Output Matrix sites in `dsp-sites.json` are checked against its new manifest. |
| #712 | Sidechain's KEY/KFLT/KGN bytes survive stock's power-up bank validation (`machine_registry.c`) | ColdFire only; nothing in the key path. |
| #721 | The board derives trust bindings only when the runtime's owners changed (`bind_live`'s epoch, 170-180 µs a tick with six modules on the owner's MKII); cached-module aliases | The key bus's "wanted" test reads each live module's `requires` word: a few loads a tick, no hashing, so it need not wait for the epoch. |
| #729 | Every DSP effect loads on demand: an engine's claim tries all four Parts, then the played Parts, then only what runs, and retires cached code first in a trim | The key bus's engine takes its region through the same claim; the first implementation's `mw_engines_want` (Sidechain's and the key bus's engines claimed together, one evacuation) still fits the tiered claim unchanged. |
| #732 | A base updates itself over USB (the card only for the first install) | A key bus base reaches testers without a card; it is still one base change and one requalification. |
| #738 | Redraw after a set change | Nothing in the key path. |

**Does upstream already provide any part of it, or conflict?** No. Main has no key bus, no DSP site catalogue, no DSP
data ledger and no base features: Sidechain's tap is still part of its resident engine (`resident_dsp.FEATURES` =
Sidechain, Output Matrix, Analog BD), the window's protection over USB is still the hard-coded `meets()` in
`stock_hook_resources.c`, and `loader.h` is still ABI 8. Nothing upstream contradicts the design; #731's run-time rule
is the one the ledger generalises. Upstream's site events (`events.json`) and table owners are ColdFire mechanisms and
have no DSP counterpart to reuse.

**Does option B still fit?** Yes, for its first step (the unconditional tap). Changes from the first implementation:

1. **The tap's price.** The first implementation charged the tap on both cores whenever its engine was placed,
   Sidechain alone included. Main charges nothing for Sidechain's tap, and that charge (41 executed instructions a
   sample a core, 72 at 7/4) is a fifth of core 0's headroom over eight stock slots (allowance 3,120, reserve 342 a
   slot): Sidechain could have been refused where main admits it. Now the tap is charged only while a live package
   *requires* the key bus; Sidechain alone is admitted and charged exactly as on main. (The tap's cost with Sidechain
   alone stays uncharged, as on main.)
2. **The gated follow-up needs a new layout.** Its want words (`+$3DF6..+$3DFD`) meet E-Verb 0.1.2's and Mini Verb
   0.2.3's rings. Local wants can go in private Y past Sidechain's words (`$a00`.., free on stock on both cores), but a
   cross-core want must be in the window, which has no free word left; a single word per core would be written by the
   readers of one core and decremented by the tap of the other, a lost update. Gating therefore needs its own design
   (and a reviewed change to Sidechain's `scdet`); it is not part of this change. The want-word API stays the base's:
   today every track is always wanted, and no reader writes anything in the bus or the window.
3. **The window's owner.** The window is the key bus's while it is held (Sidechain or a reader), Sidechain's own
   ranges keep it too, and the effects guide's trap says so.
4. **Ported, not redone**: the site catalogue and ledger (`dsp-sites.json`, `dsp_sites.py`, `dsp_ledger.h`), the tap
   split out of Sidechain's reviewed text (`split_sidechain`, its SHA-256 pins), the receiver's feature 8 (CAS, PLACE,
   1,026-word reset), the board's key bus holder and the ABI 9 loader. **Redone**: the price (1), the conflicts with
   #670/#721/#729 in `loader.c`, `controller_board.c`, `resident_engines.py` and their tests, and the base and packages,
   regenerated from main.

**Latency parity and no regression, as they now read.** Sidechain's key latency on main is set by the tap and `scdet`
alone: a key on the reader's own core is this block's audio (0 samples) when the dispatcher runs the key track first and
the last block's (16) when after, and a key from the other core is two generations behind (32) on every enable (#640,
measured 5 of 5 on the owner's MKII). The key bus keeps that by construction: the tap's instructions are Sidechain's
reviewed text, split and never edited, `scdet` keeps reading its own core's counter, and the board enables the key bus
on both cores before Sidechain's first enable. The proof is the interpreter's two-core key-phase test run against the
split units (Sidechain's detector unit plus the key bus unit, placed apart), every enable offset and skew of #640's test,
plus a reader on each core, and on the unit the same T5-against-T3 lag over repeated removals and reinstalls. No
regression means: Sidechain's package bytes unchanged but for `requiredBase`, its trust row unchanged, its admission
and charge as on main when no reader is installed, the resident (not on-demand) permanent block's words identical, and
its existing host and interpreter tests passing.

## The problem

Two modules can't ship over USB today, and the cause is the same:

- **RINGMOD SC** (a ring-mod/duck insert with its own key tap; branch `claude/ring-mod-sidechain-effect-e0027c`). Its
  effect is an ordinary relocatable insert. Its key tap is a hook in stock DSP code at the per-track FX1 dispatcher, with
  fixed Y claims on both cores. `build.py --octabam ring-sc` refuses it ("hooks in stock DSP code").
- **Output Matrix's next version** (smaller core-0 DSP, the LEV destination label). Its DSP engine is resident in the
  base, built from pinned sources (`resident_dsp.py` `SOURCES`), so any change to `matrix_mix.asm` is a new base,
  a new identity and new `requiredBase` for every base-bound package.

The base's resident DSP route is a closed list: `resident_dsp.FEATURES = (SIDECHAIN, MATRIX, ANALOG_BD)`, with per-feature
`ALLOWED` cores, pinned sources, fixed `resource_ranges` and fixed stubs. Each new hook module, and each DSP change to an
existing one, needs a base rebuild, re-pinning, Analog BD's recipe recapture (finding 17) and the owner's
requalification of the base.

## What already exists and is reused

- **Stubs at stock sites** (`resident_dsp.assemble_resident`). The base's DSP image puts a permanent JSR at each hooked
  stock site, into a two-word stub whose dormant path replays the displaced instruction. The receiver's op 10 CAS
  changes only the stub's operand, between frames, on every required core.
- **Engines on demand** (`docs/OCTATRACK_RESIDENT_ENGINES_ON_DEMAND.md`). An engine is a relocatable unit (address and
  negative-displacement relocations, proven at several bases). The ColdFire places it at the top of the arena (claim,
  evacuation, owned WRITE with read-back, PLACE writing a per-feature base word, RESET, ENABLE), only while stopped, and
  unplaces it when no holder is left. Part switches never start an engine job.
- **Per-core engine cycle charge** (`dsp.c`, `modwerk_dsp_source_claim`): a per-core price charged before every FX slot,
  7/4 of an emulator figure until a hardware figure exists.
- **Y buffer fit** (`resident_dsp.buffer_fits`): a slot's delay buffer must not meet an active feature's Y range.
- **Manifest declarations** octabam's ledger already checks on card builds: `DspHook(site, stock guard, label)` and
  `DspRange(space, start, length, half_relative)` (`tools/remix/schema.py`), and `modules:compat` for the pairs.
- **Controller trust rows** (`controller-policies.json`): the base admits a base-bound ColdFire controller only by its exact
  package hash, which is a base input.

## Proposal

### 1. A base-owned catalogue of DSP hook sites

A registry like `events.json`: `sdk/machines/octatrack/dsp-sites.json`, with `events.py`-style generation. Each entry:

- name (`dsp_` and what runs there), index (an ABI: append only, never renumber);
- per payload: P address, length in whole instructions (two words today), SHA-256 guard of the stock words;
- when it runs (for example "per track per block, before FX1, X:$420 = the track"), and the register contract: the
  registers a subscriber may clobber (for the FX1 dispatcher: a, b, r0, r1, n1, x0, which stock reloads right after);
- kind: **exclusive** (one subscriber; the base refuses a second) or **chain** (a fixed room of N subscribers, called in
  order). Start with exclusive only; chaining costs cycles at the hottest site and has no user yet.

The base build installs the JSR and a dormant stub at every catalogued site, as it does for today's resident features.
The stub's on path becomes `jsr <placed entry>`, then the displaced instruction, then `rts`: **the base replays the
stock instruction, never the package.** A package then carries no stock words at all, so it stays stock-free under the
unchanged scans. Today's engines end with the displaced instruction themselves (Sidechain's `sctap` ends with it); a
package must not.

Initial sites, all already hooked by resident features or requested:

| Site | Payload A | Payload B | Today |
| --- | --- | --- | --- |
| FX1 dispatcher (per track, before FX1) | P:$004a7 | P:$0029c | Sidechain `sctap`; RINGMOD SC's tap |
| Sidechain detector, MON commit | (from its manifest) | (from its manifest) | Sidechain |
| Output Matrix mix, phones | P:$257, P:$30a | none | Output Matrix |
| Analog BD source | (resident guard) | (resident guard) | Analog BD |

### 2. A DSP data ledger owned by the base

One table per core (and one for the shared window, which both cores see) of who owns which X/Y words:

- **stock tenants**, measured and fixed at base build (for example Y:$795..$fff free on stock on both cores, the stock FX
  slot buffer bases);
- **base-owned regions**: the resident features' ranges (`resource_ranges`), and any base table (section 4);
- **package claims**: each admitted package's declared ranges, per core, read or write.

The base already tests slot buffers against resident ranges (`buffer_fits`); the same test generalises to every claim, so
a delay buffer is never placed over a claimed Y range and a claim is refused over a live buffer. Claims follow
`DspRange`: absolute below the shared window, or half-relative inside it.

Rules the ledger enforces at admission, before anything is sent:

- one owner per site (exclusive kind) and per claimed word;
- a claim inside the shared window is compared against both cores' claims and both cores' FX2 slot buffers;
- an X claim in an 8K block a DMA uses ($0000, $2000, $8000 on core 0) is refused or flagged for review
  (`OCTATRACK_HARDWARE_TRAPS.md`, dense work beside a DMA);
- claims an effect's own code writes outside its r7 block count too, not only the hook's (RINGMOD SC's readers write the
  want word of their KEY track).

### 3. The package: an ABI 9 hook descriptor

An extension of the ABI 6 DSP descriptor (`sdk/runtime/loader/README.md`), so one package can carry an effect, a hook
engine, or both (RINGMOD SC needs both: an insert and a tap):

- **engine unit**: relocatable DSP words and relocations, assembled at two origins and proven at several bases, as
  `resident_dsp.engine_unit` does; entry offsets per site;
- **hooks**: site index and entry offset, per core (a package may hook core A only, like Output Matrix);
- **claims**: `{space, core | shared, start, words, access}`;
- **init records**: the words to write into its claims before ENABLE (zero, or a seed), so cold memory is never read as
  state (RINGMOD SC's seeded mark, Sidechain's GSEED sentinel);
- **cost**: per core, while enabled, in the existing figure kinds (executed, modeled, hardware), charged like a source
  engine (`modwerk_dsp_source_claim`): a hook at the dispatcher costs on every track of the core whether or not a reader is
  active, so it is a per-core engine price, not a per-instance one.

`build.py --dsp-hook` derives all of it from the module's manifest (`DspHook`, `DspRange`) and refuses, before
packaging: a site not in the catalogue, a stock guard that differs from the catalogue's, a register outside the site's
contract (checked on the disassembly, as build_bus's round-trip audit does), a `rep`, a stack depth over the site's
allowance, or a missing `rts`.

### 4. The lifecycle (the on-demand engine path, generalised)

Install, trial, self-test, Keep and Undo as for any package. The engine part follows today's on-demand order, with a
**hook slot** in place of a feature bit:

1. admission: ledger (sites, claims), P room (`mw_engines_admit`'s dry run, the bank's Part union), cycles;
2. WRITE (owned, read back), PLACE (op 10, word 7 = 1, word 4 the hook slot, word 5 the table offset; the base word per
   slot);
3. init records into the claims;
4. ENABLE: CAS of the stub operands on every required core, in the same frame where the hook reads the other core's
   data;
5. removal: disable on every core, then UNPLACE and free the claims, only while stopped (the on-demand rules).

The base reserves a fixed number of hook slots (say 4), each with its base word in the permanent block: a few P words per
slot on each core.

### 5. Trust

The point is to ship a hook module's DSP change as a new package, with no base rebuild. So admission can't be by an exact
package hash pinned in the base, as controller trust rows are. The proposal: a hook package is admitted like an effect
package, by the catalogue and qualification path (review, `module:verify`, hardware evidence), with the base enforcing
only the structural rules above (sites, guards, claims, cost, P room). That is a policy change for the owner: a hook
runs on every track of a core, so a bad package can silence or stall a core. It is the same class of risk as an effect
package, larger in reach.

**Output Matrix also has a ColdFire half.** Its controller is a base-bound package admitted by trust rows, and the LEV
label is a ColdFire change (a new detour, a moved stock-copy span). With this proposal its DSP change ships as a
package, but its controller change still needs new trust rows, so still a base rebuild, unless controller admission also
moves from pinned hashes to declared lease entitlements. That is a separate decision (question 4).

## The key conflict: Sidechain Compressor and RINGMOD SC

Sidechain's resident engine already owns the FX1 dispatcher site and the shared windows. RINGMOD SC's tap is nearly the
same tap: same site, same key bus ($800 + track×$40, 32 words used), same cross-core window layout (base + local×$80 +
generation×$20, base $33e00 / $3be00), same seed and counter words before the window. It adds want words that gate the
copy: $7f8+track per core, which **meet Sidechain's MON words** ($7f0..$7ff), and four words below the window.

**Option A: the ledger refuses the pair.** RINGMOD SC claims the dispatcher site and its ranges; with Sidechain installed,
admission answers `RUNTIME_CONFLICT`, and the configurator never offers both (RINGMOD SC's manifest already declares
`conflicts=SIDECHAIN_COMPRESSOR`).

- Needs nothing beyond sections 1-5.
- RINGMOD SC must take the #640 counter-phase rule into its own tap: at a runtime install the cores are enabled at
  different frames, and its tap has the pre-fix behaviour (89 or 121 samples of lag, and an occasional read of the slot
  being written, as Sidechain had).
- Users choose one or the other.

**Option B: a base-owned key bus that both read.** The base owns the tap at the dispatcher as a facility, not a feature:

- the tap is Sidechain's resident `sctap` with the #640 phase rule, publishing every track's FX1 input into the existing
  layout (local bus and cross-core window, four generations, reader two behind its own counter);
- it is a base DSP table: readers declare `reads: dsp_key_bus` and claim no tap words; the base enables the tap while at
  least one reader is installed (reference count), so idle cost is paid only then;
- Sidechain's engine drops `sctap` and reads the bus as today (same addresses, so `scdet` is unchanged);
- RINGMOD SC drops its tap and its counter; its readers read the same slots.
- So under B, RINGMOD SC carries no stock-DSP hook at all: it is an ordinary effect package whose descriptor requires
  the bus, and its readers stop writing want words (they would land on Sidechain's MON words).

Trade-offs of B:

- Both modules run together, and the phase rule lives in one place.
- RINGMOD SC loses its want-word gating, so the tap copies every track while any reader is installed. Its own estimate:
  about 2 instructions per sample idle and about 11 for a listened track with both copies. Sidechain's always-on tap cost
  is not measured on its own; measure both before choosing.
- If gating is wanted, it becomes part of the bus contract (readers mark the tracks they listen to), its want words move
  out of Sidechain's MON range, and Sidechain's `scdet` gets a reviewed change (`resident_dsp.REVIEWED`) to mark its KEY.
- Sidechain's MON stash ($820.. of each track's bus slot) stays Sidechain-private and must be declared as its claim.
- It changes a base-owned tap, so it is a base rebuild and a requalification once, when the bus is introduced.

**Chosen for the local implementation: B** (owner review pending, question 1). The plan, in two steps. First, sections 1-5 with exclusive sites, and the key bus as the first base-owned
DSP table, with Sidechain moved onto it in the same base change (its tap code is already the base's). Second, RINGMOD SC
as the first package-carried reader, then Output Matrix's DSP as the first package-carried hook. Option A is the fallback
if the owner wants RINGMOD SC sooner than the bus can be qualified.

## The key bus as implemented first, and its follow-up

**First step (chosen 15 October 2026, local): an unconditional tap.** KEYBUS is Sidechain's resident `sctap`, unchanged,
with #640's phase rule: it copies every track's FX1 input to the local bus and the window on every block. Sidechain's DSP
stays byte-identical; only its feature split moves (KEYBUS, bit 8, out of SIDECHAIN; a held SIDECHAIN holds KEYBUS).

- KEYBUS is placed only while a reader package or Sidechain is installed, so it costs nothing otherwise.
- While a live package requires it, the base charges the tap on both cores as a per-core constant, before every FX
  slot, the way a source engine is charged: counted statically from the source (`resident_dsp.keybus_executed`, 41
  executed instructions a sample for a core's four tracks, seeded), charged at 7/4 like every emulator figure until it
  is timed on a unit. Sidechain alone is not charged for it, as on main (review, change 1); a reader installed beside
  Sidechain is.
- Measuring it on a unit: NONE on every track, one pattern playing, `scripts/octatrack-measure.py` on both cores with
  nothing installed, then with a KEYBUS reader installed (KEYBUS placed and enabled, no reader on any track), then with
  Sidechain installed; the difference is the tap's cost per core.

**Resets.** KEYBUS resets the bus (Y $800, $200 words) and the window ($33dfe / $3bdfe, $202 words), 1,026 words per
core, when it is placed. Sidechain keeps its exact reset (1,042 words: Y $7f0+$210 and the window), so its contract and
DSP stay byte-identical; a held Sidechain holds KEYBUS, which the base places, resets and enables first. Side effect:
installing or reinstalling Sidechain while a reader is live re-zeroes the bus and the window once, so that reader hears
up to about a block of silent key while the tap re-adopts its counter by #640's rule.

**The reader contract is generic.** Any track can be a key, and a reader may run on either core: a reader on the key
track's own core reads the local bus (this block's audio if the key track is dispatched before it, the last block's if
after), a reader on the other core reads the window two generations behind its own core's counter (#640's phase rule:
32 samples). A reader writes nothing in the bus or the window. RINGMOD SC is the first reader; CHARACTER 0.1.2's KEY
(today upstream's bus server at y:$990/$991, or NOBUS_KEY) is planned as the second, once RINGMOD SC's is proven.

**Follow-up, not implemented: a gated tap.** Superseded as written: the layout below puts want words at
`+$3DF6..+$3DFD` of the window's slot, which E-Verb 0.1.2's and Mini Verb 0.2.3's rings now use (review, change 2); it
is kept for its reasoning. RINGMOD SC's own tap copied a track only while someone asked for it
(about 30 instructions per track per block idle). The contract for that, with every want word in the shared window so
any reader on either core can write it and nothing meets Sidechain's MON words ($7f0..$7ff); per core, base = $33e00
(tracks 5-8) or $3be00 (tracks 1-4):

| Words | Use |
| --- | --- |
| base-10..base-7 | local-bus want, one per local track (same-core readers write it) |
| base-6..base-3 | window want, one per local track (other-core readers write it) |
| base-2 | seed mark (unchanged) |
| base-1 | generation counter (unchanged) |

A reader writes 4 to the want word on every call; the tap takes 1 off each block and copies while it is above 0 (only
the low three bits count, so cold memory runs out within seven blocks). The window range grows from $202 to $20a words,
still past every stock FX2 tenant. Sidechain's `scdet` must then write the want word of its KEY track on every call (a
reviewed change to its pinned source, as #640's was), and reads stale bus words for one or two blocks after a KEY change
or a first enable. The fix for that is a short fade-in on a KEY change, as RINGMOD SC's ten-call wait (option i), also a
reviewed change.

## What it costs

- Base: the site catalogue and its generator, stubs for every catalogued site, hook slots and their base words, the
  generalised receiver op 10, the ledger in the manager, the init-record writer, the reference-counted key bus.
- Loader: ABI 9 parsing, admission, and the hook slot lifecycle in `resident_engines.c`'s place.
- Tools: `build.py --dsp-hook`, the register and `rep` audit, `modules:compat` reading the catalogue and the claims.
- Tests: host tests in the style of `test_resident_engines_board.py` (place, enable, refuse, remove, a stuck PLACE);
  the DSP interpreter run of the bus with two readers on both cores and enable offsets, as for #640's phase test.
- Hardware: the base requalified once; per module, install, removal and reinstall with the key latency the same each
  time, readers and keys on both cores, FX1 and FX2.

## Open questions for the owner

All five are open. The local implementation assumes B for question 1 and exclusive sites for question 3.

1. Option A or B for Sidechain and RINGMOD SC?
2. Admission of hook packages by structural rules plus the publication path (section 5), instead of hashes pinned in the
   base?
3. Exclusive sites only for now, or chaining from the start?
4. Should ColdFire controller admission also move from pinned trust rows to declared lease entitlements, so Output
   Matrix's ColdFire changes stop needing a base rebuild too? Separate design if yes.
5. Migrate Sidechain, Output Matrix and Analog BD's resident engines onto hook packages later, or keep them resident?
