/* VECTOR on MIDI tracks: a MIDI generator (sdk/machines/octatrack/events.json ot_midi_generators). The same original
 * phrase engine writes the track's note trigs and NOTE, VEL and LEN locks; the stock MIDI sequencer plays them, so
 * tempo, track speed, swing, conditions and note-offs stay stock's. Its twelve controls are the track's ARP page and,
 * after FUNC+AMP, its second page. They are kept in the track's arpeggiator note bytes, which the base gives a
 * generator's track (Part 0x1832 + 16 t, value - 64: the -64..63 stock's validator keeps). Included after native.c
 * (its Part, dirty and redraw helpers). MIDI track records: octabam docs/firmware/STEP_LOCKS.md, and on the owner's
 * MKII (21 October 2026): trig mask 0 at +0, length +0x28, locks +0x30 + 32 step (NOTE 0, VEL 1, LEN 2). */
#include "modwerk_events.h"
#define MIDI_TRACKS 0x48d0u
#define MIDI_TRACK_BYTES 0x8b0u
#define MIDI_LOCKS 0x30u
#define MIDI_TIMING 0x830u           /* two bytes a step: micro timing and condition, as the audio record's 0x89a */
#define MIDI_NOTES(t) (0x1832u + 16u * (t))
#define MIDI_MARK 12u                /* a thirteenth byte: 'V' once VECTOR wrote its controls there */
#define MIDI_GATE_DEFAULT 8u         /* LEN units: 4 to 8, about a sixteenth, as the stock LEN default 6 */

static unsigned midi_value(unsigned t, unsigned k) { return (uint8_t)((int8_t)current_part()[MIDI_NOTES(t) + k] + 64); }
static void midi_put(unsigned t, unsigned k, unsigned v)
{
    unsigned at = MIDI_NOTES(t) + k, part = U8(PART_IDX) & 3u;
    current_part()[at] = (uint8_t)(v - 64u);
    U8(SRAM_PART + part * PART_STRIDE + at) = (uint8_t)(v - 64u);
}
static unsigned midi_control(unsigned t, unsigned c)
{
    if (midi_value(t, MIDI_MARK) != 'V') {
        static const uint8_t first[12] = {11, 11, 0, 1, MIDI_GATE_DEFAULT, 48, 1, 12, 12, 0, 0, 0};
        return c == 6 ? t + 1u : first[c];
    }
    unsigned v = midi_value(t, c);
    return v > vector_control_max[c] ? vector_control_max[c] : v;
}
static void midi_params(unsigned t, VectorParams *p, uint32_t *seed)
{
    uint8_t *bytes = (uint8_t *)p;
    for (unsigned c = 0; c < 12; ++c) if (c != 6) bytes[c < 6 ? c : c - 1] = (uint8_t)midi_control(t, c);
    *seed = midi_control(t, 6);
}
static void midi_save(unsigned t, const VectorParams *p, uint32_t seed)
{
    const uint8_t *bytes = (const uint8_t *)p;
    for (unsigned c = 0; c < 12; ++c) midi_put(t, c, c == 6 ? seed & 127u : bytes[c < 6 ? c : c - 1]);
    midi_put(t, MIDI_MARK, 'V');
}

static unsigned midi_bit(const uint8_t *r, unsigned mask, unsigned step) { return (r[mask * 8u + 7u - step / 8u] >> (step % 8u)) & 1u; }
static void midi_setbit(uint8_t *r, unsigned mask, unsigned step, unsigned on)
{
    uint8_t *byte = r + mask * 8u + 7u - step / 8u, b = (uint8_t)(1u << (step % 8u));
    *byte = on ? (uint8_t)(*byte | b) : (uint8_t)(*byte & (uint8_t)~b);
}
/* No trigs, trigless trigs or locks: a phrase may be written without replacing anything. Swing (mask 3) is a default. */
static int midi_empty(const volatile uint8_t *r)
{
    for (unsigned i = 0; i < 24; ++i) if (r[i]) return 0;
    for (unsigned i = 32; i < 40; ++i) if (r[i]) return 0;
    for (unsigned i = 0; i < VECTOR_STEPS * 32u; ++i) if (r[MIDI_LOCKS + i] != VECTOR_NO_LOCK) return 0;
    return 1;
}
/* A byte of the track record and its battery-backed copy, stored only when it changes. */
static void midi_set(volatile uint8_t *r, volatile uint8_t *mirror, unsigned at, uint8_t v)
{
    if (r[at] != v) { r[at] = v; mirror[at] = v; }
}
/* In place, as stock's own editors store: module code and data run uncached, so a whole-record copy in and out cost
 * about 0.8 ms of a 1.3 ms knob turn on the owner's MKII (21 October 2026); this touches the five masks, three locks
 * a step and the timing of the steps that change. NOTE locks from the phrase's semitones over `octave` (the C at or
 * under the track's NOTE), VEL from its volumes, LEN from its holds. Other locks and swing stay; old and new notes
 * lose stale timing, conditions and trigless marks. `locked` gets whether each step keeps any lock (the lock index). */
static void midi_write(volatile uint8_t *r, volatile uint8_t *mirror, const VectorPhrase *phrase, unsigned octave,
                       uint8_t locked[VECTOR_STEPS])
{
    uint8_t masks[40];
    for (unsigned k = 0; k < 40; ++k) masks[k] = r[k];
    for (unsigned i = 0; i < VECTOR_STEPS; ++i) {
        const VectorStep *s = &phrase->steps[i];
        unsigned at = MIDI_LOCKS + 32u * i, old = midi_bit(masks, 0, i);
        int note = (int)octave + ((int)s->pitch - 64) / 5;
        midi_set(r, mirror, at, s->active ? (uint8_t)(note < 0 ? 0 : note > 127 ? 127 : note) : VECTOR_NO_LOCK);
        midi_set(r, mirror, at + 1u, s->active ? s->volume : VECTOR_NO_LOCK);
        midi_set(r, mirror, at + 2u, s->active ? s->hold : VECTOR_NO_LOCK);
        midi_setbit(masks, 0, i, s->active);
        if (old || s->active) {
            midi_set(r, mirror, MIDI_TIMING + 2u * i, 0); midi_set(r, mirror, MIDI_TIMING + 2u * i + 1u, 0);
            midi_setbit(masks, 1, i, 0); midi_setbit(masks, 4, i, 0);
        }
        unsigned any = s->active;
        for (unsigned k = 3; !any && k < 32; ++k) any = r[at + k] != VECTOR_NO_LOCK;
        locked[i] = (uint8_t)any;
        midi_setbit(masks, 2, i, !s->active && any);
    }
    for (unsigned k = 0; k < 40; ++k) midi_set(r, mirror, k, masks[k]);
}
/* On the UI task, into the current pattern's record and its battery-backed copy, then published through stock's
 * track update (MIDI tracks are 8-15 there). Stock's lock index (0x400339d8) rescans every track of the pattern, 16 x
 * 64 x 32 bytes, about 3 ms on the unit; only this track's bit changes, so it is set here: bit t of each step's byte
 * at 0x46c7d2e4 (the MIDI tracks'), as that routine sets it. */
static int midi_generate(unsigned t, int replace, int fresh)
{
    unsigned p = U8(PATTERN_IDX);
    if (!valid_bank() || t >= 8 || p >= 16) return 0;
    uint32_t bank = U32(BANK_PTR), part = U8(PART_IDX), off = p * PATTERN_STRIDE + MIDI_TRACKS + t * MIDI_TRACK_BYTES;
    volatile uint8_t *r = (volatile uint8_t *)(uintptr_t)(bank + off), *mirror = (volatile uint8_t *)(uintptr_t)(SRAM_PATTERNS + off);
    if (!replace && !midi_empty(r)) return 0;
    const volatile uint8_t *pat = (const volatile uint8_t *)(uintptr_t)(bank + p * PATTERN_STRIDE);
    unsigned length = pat[0x8e55u] ? r[0x28u] : pat[0x8e53u];
    VectorParams params; uint32_t seed;
    midi_params(t, &params, &seed);
    if (fresh) seed = vector_next_seed(seed);
    const volatile uint8_t *notes = current_part() + 0x3e2u + 32u * t;  /* NOTE page: NOTE, VEL */
    if (!length || length > 64 || notes[1] > 127 || !vector_generate(&phrase, &params, length, notes[1], seed)) return 0;
    static uint8_t locked[VECTOR_STEPS];
    midi_write(r, mirror, &phrase, notes[0] - notes[0] % 12u, locked);
    midi_save(t, &params, seed);
    dirty_part(part & 3u);
    for (unsigned i = 0; i < VECTOR_STEPS; ++i)
        U8(0x46c7d2e4u + i) = (uint8_t)((U8(0x46c7d2e4u + i) & ~(1u << t)) | locked[i] << t);
    ((void (*)(unsigned))0x4009da20u)(t + 8u);
    return 1;
}

/* The page: stock's ARP descriptor with VECTOR's names and formatters in value-text cells, built in the audio page's buffer
 * (never shown together); audio's generator_page rebuilds it once src_page_ready is clear. */
static uint32_t midi_page_built = 0;
static void midi_format(char *out, unsigned c)
{
    unsigned v = midi_control(U8(TRACK_IDX), c);
    if (c == 4) { ((void (*)(char *, int))*(const uint32_t *)(uintptr_t)(0x400d3e3eu + 0xcau + 8u))(out, (int)v); return; }
    static const char *const roots[] = {"C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"};
    const char *name = c == 2 ? roots[v % 12] : c == 3 ? vector_scale_names[v % 5] :
                       c == 11 ? (v ? "REV" : "FWD") : c == 10 && !v ? "OFF" : 0;
    unsigned i = 0;
    if (name) { do out[i] = name[i]; while (name[i++]); return; }
    if (c == 8) { int s = (int)v - 12; if (s < 0) { out[i++] = '-'; v = (unsigned)-s; } else v = (unsigned)s; }
    if (v >= 100) out[i++] = (char)('0' + v / 100);
    if (v >= 10) out[i++] = (char)('0' + v / 10 % 10);
    out[i++] = (char)('0' + v % 10); out[i] = 0;
}
#define MIDI_FORMATTER(n) static void midi_format_##n(char *out, int value) { (void)value; midi_format(out, n); }
MIDI_FORMATTER(0) MIDI_FORMATTER(1) MIDI_FORMATTER(2) MIDI_FORMATTER(3) MIDI_FORMATTER(4) MIDI_FORMATTER(5)
MIDI_FORMATTER(6) MIDI_FORMATTER(7) MIDI_FORMATTER(8) MIDI_FORMATTER(9) MIDI_FORMATTER(10) MIDI_FORMATTER(11)
static uint32_t vector_midi_page(uint32_t stock, unsigned second)
{
    if (src_page_ready || midi_page_built != stock + second + 1u) {
        static void (*const formats[12])(char *, int) = {midi_format_0, midi_format_1, midi_format_2, midi_format_3,
            midi_format_4, midi_format_5, midi_format_6, midi_format_7, midi_format_8, midi_format_9, midi_format_10, midi_format_11};
        const volatile uint8_t *source = (const volatile uint8_t *)(uintptr_t)stock;
        unsigned page = second & 1u;
        uint8_t *d = src_page;
        {
            for (unsigned i = 0; i < sizeof src_page; ++i) d[i] = source[i];
            label(d + 4, "VEC");
            for (unsigned i = 0; i < 12; ++i) d[9 + i] = (uint8_t)"VECTOR 1/2\0"[i];
            d[16] = (uint8_t)('1' + page);
            for (unsigned i = 0; i < 6; ++i) {
                label(d + 0x16 + 6 * i, vector_control_names[i + 6 * page]);
                put32(d + 0xca + 4 * i, (uint32_t)(uintptr_t)formats[i + 6 * page]);
                put32(d + 0xfa + 4 * i, 0x400467a4u); /* stock's value-text cell, as the NOTE page's */
            }
            put32(d + 0x18a, 0x00005555u);
            put32(d + 0x18e, 0x55555555u);
        }
        src_page_ready = 0;
        midi_page_built = stock + second + 1u;
    }
    return (uint32_t)(uintptr_t)src_page;
}
static void vector_midi_knob(unsigned index, int delta, unsigned second)
{
    unsigned t = U8(TRACK_IDX), c = index + (second ? 6u : 0u);
    VectorParams p, before; uint32_t seed, old;
    midi_params(t, &p, &seed); before = p; old = seed;
    uint8_t *parameter = (uint8_t *)&p + (c < 6 ? c : c - 1);
    int value = (int)(c == 6 ? seed : *parameter) + delta;
    if (value < 0) value = 0;
    if (value > vector_control_max[c]) value = vector_control_max[c];
    if (c == 6) seed = (uint32_t)value; else *parameter = (uint8_t)value;
    if (c == 6 ? seed == old : *parameter == ((uint8_t *)&before)[c < 6 ? c : c - 1]) return;
    midi_save(t, &p, seed);
    if (!midi_generate(t, 1, 0)) midi_save(t, &before, old);
}
static void vector_midi_yes(void)
{
    notice(midi_generate(U8(TRACK_IDX), 1, 1) ? "VECTOR GENERATED" : "NO CHANGE");
}
/* Chosen: VECTOR's defaults, and a first phrase on an empty track; a track with notes waits for a control. */
static void vector_midi_assign(unsigned t, unsigned on)
{
    if (!on) return;
    VectorParams p = vector_defaults; p.gate = MIDI_GATE_DEFAULT;
    midi_save(t, &p, t + 1u);
    (void)midi_generate(t, 0, 0);
}
const struct modwerk_midi_generator vector_midi = {
    MODWERK_MIDI_GENERATOR_ABI, "VECTOR", 'V', vector_midi_assign, vector_midi_page, vector_midi_knob, vector_midi_yes, 0,
};
