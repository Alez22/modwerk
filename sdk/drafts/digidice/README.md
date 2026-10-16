# digidice (draft)

A random melody generator for the Digitakt mk1, inspired by Vermona's meloDICEr. A page opened with a key combo rolls a melody into the active track, audio or MIDI, as ordinary trigs with a note, a velocity and a length each. After that it is a normal pattern: edit it, save it, copy it or undo it.

**Status:** phase 1 of the plan below. Only the generator engine exists, tested on a host. Nothing has run on a Digitakt, and there is no mod yet. This folder moves to `sdk/digitakt/modules/` in phase 2.

## Controls (planned)

One page, eight encoders:

| Encoder | Control | Range | What it does |
| --- | --- | --- | --- |
| A | DENSITY | 0–127 | Chance each rhythm slot plays. 0 is silence, 127 every slot |
| B | NOTE VALUE | 1, 2, 3, 4, 6, 8 steps | The basic gap between slots |
| C | VARIATION | 0–127 | Chance a slot's gap halves or doubles |
| D | LEGATO | 0–127 | Note length as a share of the gap; 127 ties to the next slot |
| E | ROOT | C–B | |
| F | SCALE | CHROM, MAJOR, MINOR, DORIAN, MIXO, HARMIN, MAJPEN, MINPEN | Every note stays in the scale |
| G | RANGE | 0–24 | Scale degrees above the root |
| H | VEL | 0–127 | Velocity spread around the track's default |

Keys while the page is open: YES rolls everything, LEFT rolls the rhythm only, RIGHT rolls the notes only, NO closes the page. Turning a knob re-generates from the current seeds, so it reshapes the pattern instead of replacing it. Opening the page takes the stock undo snapshot once, so one undo restores the pattern from before any rolls.

Timing is the instrument's own: the track's length and speed, the tempo and swing. The mod keeps no clock.

## The engine

[engine.h](engine.h) and [engine.c](engine.c): plain C99 with no libc, no floating point and no 64-bit arithmetic. `dd_generate(settings, rhythm_seed, note_seed, length, vel_base, out)` fills 64 steps.

- Every random decision is a hash of (seed, position, decision), not a draw from a stream, so changing one control never reshuffles the others. Raising DENSITY only adds notes; the notes already there keep their place, note, velocity and length.
- The rhythm (which steps play, the gaps, lengths and velocities) depends only on the rhythm seed. Each step's note depends only on the note seed, as on the meloDICEr, where every step has a note and the rhythm decides which ones play. So rolling one half keeps the other.
- `note` is in semitones above the C below the root. The mod maps it to the track's NOTE once the hardware checks show what NOTE means on audio and MIDI tracks.
- `len` is in eighths of a step. The mod maps it to the nearest TRIG page LEN value once that table is confirmed on the unit.

```sh
cc -std=c99 -Wall -Wextra -Werror -fsanitize=address,undefined engine.c test_engine.c -o test_engine && ./test_engine
```

[test_engine.c](test_engine.c) covers:
- determinism
- every note in its scale and range across 20,000 random settings
- trigs only inside the track length
- the DENSITY extremes and exact spacing
- VARIATION giving both halves and doubles
- DENSITY only ever adding notes
- partial rolls keeping the other half
- the LEGATO and VEL extremes
- clamping and seed advance

For ColdFire V4e (`m68k-linux-gnu-gcc-12 -mcpu=5475 -ffreestanding -Os`), the engine is 1,028 bytes with no undefined symbols.

## Plan

0. **Hardware checks (go/no-go), when a unit is available:**
   - the checks in [pattern-write.md](../../digitakt/research/pattern-write.md), with [dtpeek.py](../../digitakt/research/dtpeek.py)
   - what NOTE means on audio and MIDI tracks
   - the LEN table
   - a key combo the OS leaves free
   - a test mod that writes a fixed phrase through the OS setters
1. **Generator engine.** This folder.
2. **The mod, v1:**
   - the page: key combo, drawing, encoders and keys
   - writes through the OS setters from `ev_tick`/`ev_key`, only for steps that changed, about 150 ms after a knob stops
   - the undo snapshot
   - README, TESTING, thumbnail, `module:doctor`, a build beside digihealth, and photos from the unit
3. **Later:** per-note weights on trig keys 1–12 (the meloDICEr's twelve faders), mutating a few steps each loop, saved settings, OS 1.53.

## Licence

MIT. See [LICENSE](LICENSE). The engine and tests are original work. No Elektron firmware, extracted routines or tables, and no Vermona code or material, are included. "meloDICEr" is Vermona's product name, used here only to describe the inspiration.
