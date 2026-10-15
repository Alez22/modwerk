#!/usr/bin/env python3
"""APPLY SCENE's gate: the built image under the ColdFire port (ot_emu --mkii).

    python3 modules/apply-scene/verify.py        (from the octabam root)

Reads, and SKIPs without any of them:
  - the image: out/mainos_bus.bin built with APPLY SCENE (APPLY_IMAGE overrides);
  - the port: out/emu/ot_emu (`make emu-cf`; OT_EMU overrides);
  - a project to stage: octabam's out/_stage_tmpl/OCTABAM/TMPL (APPLY_PROJECT
    overrides), any project whose bank 1 holds eight sample tracks.

The fixture is that project with bank 1 Part 1 (working and saved copies)
rewritten: the machines STATIC, FLEX, THRU, NEIGHBOR, PICKUP, FLEX, STATIC,
FLEX; eight different stock FX1/FX2 pairs with their descriptor defaults;
scenes 2 and 10 selected; locks on every scene byte of every track in a fixed
pseudo-random pattern (both sides, A only, B only, none; disabled slots, AMP
XVOL and XLV included), and locks in two unselected scenes. Tracks 7 and 8
carry no LFO locks, so their voice records show the bare morph.

What it checks (one interactive boot, then a project reload and a power cycle):
  1. The apply, at fader 127, 96, 64, 32, 0. [SCENE A] + [YES] and [SCENE B]
     + [YES]: every page-1 byte that scene locks equals its lock (disabled
     slots untouched; clamped to the descriptor), unlocked bytes stay. Both
     scene keys + [YES]: every page-1 byte equals the stock morph model (A/B
     lerp, the Part base for an unlocked side, the track's weight long,
     rounded as the MAC rounds, then to a whole step). Each time nothing else
     in the working Part moved; the saved Part, the scene locks, XLV, the
     selection, the mutes and the fader are unchanged; the unsaved bit is
     set; the CS1 working copy equals RAM; the toast is the mode's text;
     RELOAD PART (FUNC + CUE) restores working = saved (the unsaved bit is
     reported, not asserted: stock leaves it set). The mode follows the keys
     that are down, in either press order and after one of two is released.
  2. The model is stock's: before an apply, the voice records' AMP/FX
     halfwords of tracks 3 and 8 equal the model from the live lane; after it, at
     the same fader, a byte locked in both scenes is unchanged and a byte
     locked in one follows the model from the new base.
  3. Scene mutes (FUNC + SCENE): one scene applies its locks muted or not;
     in the blend a muted side counts as unlocked, and with both muted the
     blend applies nothing and leaves the Part clean.
  4. Stock flows: YES alone still shows ARM ALL (0x46c7ff64 set on press,
     cleared on release); a YES held before the scene key goes to stock;
     SCENE + TRIG selects a scene, SCENE + knob writes a lock, SCENE +
     REC/STOP/PLAY reach their stock handlers.
  5. Persistence: after an apply, Part SAVE (FUNC + PART, SAVE) then PROJECT
     SAVE, a fresh boot of the written card loads the applied Part as both
     working and saved; a power cycle (CS1 and card of an unsaved apply, the
     firmware's own power-up load: --cs1-in --no-post) keeps the applied
     working Part and every machine type.
What it cannot see: hardware timing, audible output, the panel's own LCD.
"""
import hashlib
import io
import os
import pathlib
import queue
import random
import shutil
import subprocess
import sys
import tempfile
import threading

HERE = pathlib.Path(__file__).absolute().parent
ROOT = pathlib.Path.cwd() if (pathlib.Path.cwd() / "tools/emu").is_dir() else HERE.parents[1]
EMU = pathlib.Path(os.environ.get("OT_EMU", ROOT / "out/emu/ot_emu"))
IMAGE = pathlib.Path(os.environ.get("APPLY_IMAGE", ROOT / "out/mainos_bus.bin"))
PROJECT = pathlib.Path(os.environ.get("APPLY_PROJECT", ROOT / "out/_stage_tmpl/OCTABAM/TMPL"))
PY = pathlib.Path(os.environ.get("OT_PY", ROOT / ".venv/bin/python3"))
PY = PY if PY.exists() else pathlib.Path(sys.executable)
BASE = 0x40000400
SITE = 0x4005E4C8

# RAM
BANK_PTR, CUR_PART, SCENE_HELD = 0x46c82456, 0x100b14cf, 0x460d169c
KEY_STATE = 0x46c7d8f1           # stock's per-key state, 24 bytes a key: nonzero while down
MUTE_A, MUTE_B, FADER, WEIGHTS = 0x80000006, 0x80000007, 0x460d16c8, 0x80003c60
CS1_WORK, PART_LEN = 0x100a4ece, 0x18b2
ARM_HELD, NOTIFY = 0x46c7ff64, 0x4005a2b8
VOICE, LANE = 0x80000110, 0x80000810
# Part offsets
SEL_A, SEL_B, MACH, PB, PG, SCN, XLV = 0x10, 0x11, 0x22, 0x2a, 0x11a, 0x662, 0x1662
P2 = 0x2f2                       # per track 30: LFO p2, AMP p2, FX1 p2 (+12), FX2 p2 (+18), LFO p3
# descriptors
MACH_DESC, LFO_DESC, AMP_DESC, FX1_TAB, FX2_TAB = 0x400d5f38, 0x400d37f6, 0x400d3988, 0x400d5f58, 0x400d5fdc
MASTER_DESC, MASTER_ON = 0x400d278a, 0x80000034
# the bank file: Part records, 8 of them (1-4 working, 5-8 saved), data 9 bytes past the tag
F_PART, F_STRIDE, F_DATA = 0x8eed6, 0x18bb, 9

MACHINES = (0, 1, 2, 3, 4, 1, 0, 1)
FX1 = (0x04, 0x0c, 0x10, 0x13, 0x1c, 0x0d, 0x05, 0x18)       # FILTER EQ PHASER COMB LO-FI DJEQ SPAT COMP
FX2 = (0x08, 0x14, 0x15, 0x16, 0x18, 0x12, 0x11, 0x1c)       # DELAY PLATE SPRING DARK COMP CHORUS FLANGER LO-FI
SCENE_A, SCENE_B, OTHERS = 1, 9, (0, 15)
SOUND = (2, 7)                    # T3 (THRU) and T8 (the master) run voice records with no samples staged
KEYS = {'scene_a': 0x19, 'scene_b': 0x1a, 'yes': 0x31, 'no': 0x32, 'func': 0x2d, 'cue': 0x2a, 'part': 0x1d,
        'proj': 0x1c, 'play': 0x28, 'stop': 0x27, 'rec': 0x29, 'up': 0x33, 'down': 0x20, 'pg_amp': 0x23,
        'trig1': 0x00, 'trig2': 0x01, 'trig3': 0x02}
FAILS = []


def check(ok, what):
    print(("  ok    " if ok else "  FAIL  ") + what, flush=True)
    if not ok:
        FAILS.append(what)


class Image:
    def __init__(self, path):
        self.d = path.read_bytes()

    def u32(self, a):
        return int.from_bytes(self.d[a - BASE:a - BASE + 4], "big")

    def bytes(self, a, n):
        return self.d[a - BASE:a - BASE + n]

    def desc(self, p):
        """(init6 page 1, init6 page 2, [(enabled, min, count)] x 6) of the descriptor at p."""
        e = p - 0x38
        en = self.u32(p + 0x18e)
        slots = []
        for s in range(6):
            mn = int.from_bytes(self.bytes(e + 0xa2 + 4 * s, 4), "big", signed=True)
            cnt = int.from_bytes(self.bytes(e + 0xd2 + 4 * s, 4), "big", signed=True)
            slots.append((bool((en >> (4 * s)) & 1), mn, cnt))
        return self.bytes(e + 0x96, 6), self.bytes(e + 0x9c, 6), slots

    def page_desc(self, part, t, page, master=False):
        if master and t == 7 and page in (0, 2):
            return self.desc(MASTER_DESC)      # the master track has no SRC or AMP (0x40031da4)
        if page == 0:
            return self.desc(self.u32(MACH_DESC + 4 * part[MACH + t]))
        if page == 1:
            return self.desc(LFO_DESC)
        if page == 2:
            return self.desc(AMP_DESC)
        tab, fx = (FX1_TAB, part[t]) if page == 3 else (FX2_TAB, part[8 + t])
        return self.desc(self.u32(tab + 4 * fx))


def base_off(part, t, k):
    if k < 6:
        return PB + t * 30 + part[MACH + t] * 6 + k
    return PG + t * 24 + (k - 6)


def s16(v):
    return v - 0x10000 if v & 0x8000 else v


MODES = {"a": (("scene_a",), "SCENE A APPLIED"), "b": (("scene_b",), "SCENE B APPLIED"),
         "mix": (("scene_a", "scene_b"), "SCENE BLEND APPLIED")}
NONE_TEXT = "NOTHING TO APPLY"       # the toast when no value differed from the Part


def model(img, part, weights, muted, t, master=False, mode="mix"):
    """{part offset: expected byte} for track t: one scene's locks, or stock's morph rounded to a step."""
    w = weights[t]
    wa, wb = -s16(w >> 16), -s16(w & 0xffff)
    if mode != "mix":
        muted = [False, False]           # one scene applies muted or not
    rows = [None if muted[i] else part[SCN + (part[SEL_A + i] * 8 + t) * 32:][:32] for i in (0, 1)]
    out = {}
    for k in range(30):
        la = rows[0][k] if rows[0] is not None and rows[0][k] < 128 else None
        lb = rows[1][k] if rows[1] is not None and rows[1][k] < 128 else None
        off = base_off(part, t, k)
        base = part[off]
        if mode != "mix":
            v = la if mode == "a" else lb
            if v is None:
                continue
        else:
            if la is None and lb is None:
                continue
            a = base if la is None else la
            b = base if lb is None else lb
            hw = (a * wa + b * wb + 64) >> 7
            v = (hw + 0x80) >> 8
        if v == base:
            continue
        en, mn, cnt = img.page_desc(part, t, k // 6, master)[2][k % 6]
        if not en:
            continue
        out[off] = max(mn, min(mn + cnt - 1, v))
    return out


def morph_hw(lane_byte, la, lb, w):
    """The halfword the frame builder writes for one scene byte (lane = the knob)."""
    wa, wb = -s16(w >> 16), -s16(w & 0xffff)
    a = lane_byte if la is None else la
    b = lane_byte if lb is None else lb
    return (a * 256 * wa + b * 256 * wb + 16384) >> 15


# ------------------------------------------------------------------ fixture
def build_fixture(img, work):
    proj = work / "ASFIX"
    proj.mkdir()
    for f in PROJECT.iterdir():
        if f.is_file() and f.suffix.lower() in (".work", ".strd"):
            shutil.copy2(f, proj / f.name)
    rnd = random.Random(0xA5CE)
    plan = {}

    def mutate(data):
        for rec in (0, 4):                       # Part 1 and its saved copy
            o = F_PART + rec * F_STRIDE + F_DATA
            if data[o - F_DATA:o - F_DATA + 4] != b"PART":
                sys.exit("verify apply-scene: the project's bank 1 has no PART record where expected")
            part = bytearray(data[o:o + PART_LEN])
            for t in range(8):
                part[MACH + t] = MACHINES[t]
                part[t], part[8 + t] = FX1[t], FX2[t]
                for page, fx_tab, fx in ((3, FX1_TAB, FX1[t]), (4, FX2_TAB, FX2[t])):
                    p1, p2, _ = img.desc(img.u32(fx_tab + 4 * fx))
                    a = PG + t * 24 + (page - 1) * 6
                    part[a:a + 6] = p1
                    a = P2 + t * 30 + (page - 1) * 6
                    part[a:a + 6] = p2
            part[SEL_A], part[SEL_B] = SCENE_A, SCENE_B
            if not plan:
                for s in (SCENE_A, SCENE_B) + OTHERS:
                    for t in range(8):
                        row = bytearray(b"\xff" * 32)
                        for k in range(30):
                            if t in SOUND and 6 <= k < 12:
                                continue                  # T3/T8: no LFO locks
                            if rnd.random() < 0.6:
                                row[k] = rnd.randrange(128)
                        plan[(s, t)] = bytes(row)
                    for i in range(10):
                        plan[("xlv", s, i)] = rnd.randrange(128)
            for s in (SCENE_A, SCENE_B) + OTHERS:
                for t in range(8):
                    a = SCN + (s * 8 + t) * 32
                    part[a:a + 32] = plan[(s, t)]
                part[XLV + s * 10:XLV + s * 10 + 10] = bytes(plan[("xlv", s, i)] for i in range(10))
            data[o:o + PART_LEN] = part

    for suffix in ("work", "strd"):
        path = proj / f"bank01.{suffix}"
        if not path.is_file():
            continue
        data = bytearray(path.read_bytes())
        mutate(data)
        data[-2:] = (sum(data[0x10:-2]) & 0xffff).to_bytes(2, "big")
        path.write_bytes(bytes(data))
    card = work / "card.img"
    r = subprocess.run([str(PY), str(ROOT / "tools/emu/ot_emu/stage_card.py"), str(proj), "APPLYSC", "ASFIX",
                        "--tree", str(work / "tree"), "--out", str(card)], capture_output=True, text=True, cwd=ROOT)
    if r.returncode:
        sys.exit(f"verify apply-scene: stage_card failed:\n{r.stdout[-800:]}{r.stderr[-800:]}")
    return card


# ------------------------------------------------------------------ the port
class Emu:
    """`ot_emu --interactive`: one command line out, one reply line back."""

    def __init__(self, card, log, extra=()):
        argv = [str(EMU), "--image", str(IMAGE), "--card", str(card), "--interactive", "--mount", "--set", "APPLYSC",
                "--project", "ASFIX", "--internal-clock", "--mkii", "--card-rw", *extra]
        self.err = open(log, "wb")
        self.p = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self.err, bufsize=0)
        self.q = queue.Queue()
        self.rows = {}
        threading.Thread(target=self._rd, daemon=True).start()
        while True:
            line = self.q.get(timeout=900)
            if line is None:
                raise RuntimeError(f"ot_emu died before ready ({log})")
            if line.startswith("ready"):
                break

    def _rd(self):
        f = io.BufferedReader(self.p.stdout, buffer_size=1 << 16)
        for raw in iter(f.readline, b""):
            self.q.put(raw.decode("ascii", "replace").rstrip())
        self.q.put(None)

    def cmd(self, line, expect="ok"):
        self.p.stdin.write(line.encode() + b"\n")
        self.p.stdin.flush()
        while True:
            r = self.q.get(timeout=900)
            if r is None:
                raise RuntimeError("ot_emu died on " + line)
            head = r.split(" ", 1)[0]
            if head == expect:
                return r
            if head == "err":
                raise RuntimeError(r)

    def run(self, ms):
        self.cmd(f"run {ms}")

    def peek(self, a, n):
        out = b""
        while n > 0:
            k = min(n, 4096)
            out += bytes.fromhex(self.cmd(f"peek {a:#x} {k}", "peek")[5:])
            a += k
            n -= k
        return out

    def u32(self, a):
        return int.from_bytes(self.peek(a, 4), "big")

    def key(self, name, down):
        code = KEYS[name]
        row = 0x20 | (code >> 3)
        cur = self.rows.get(row, 0)
        cur = cur | (1 << (code & 7)) if down else cur & ~(1 << (code & 7))
        self.rows[row] = cur
        self.cmd(f"key {row:#x} {cur:#x}")

    def tap(self, name, hold=80, after=300):
        self.key(name, True)
        self.run(hold)
        self.key(name, False)
        self.run(after)

    def chord(self, held, name, after=400):
        held = (held,) if isinstance(held, str) else held
        for k in held:
            self.key(k, True)
            self.run(150)
        self.tap(name)
        for k in reversed(held):
            self.key(k, False)
            self.run(150)
        self.run(after)

    def knob(self, enc, delta):
        self.cmd(f"knob {0x30 + enc:#x} {delta & 0xff}")

    def fader(self, xf):
        self.cmd(f"key 0x40 {2 * xf + 1:#x}")
        self.run(200)

    def watch(self, addrs):
        self.cmd("watch " + ",".join(hex(a) for a in addrs))
        self.hits()                       # drop what earlier watches left

    def hits(self):
        return [tuple(int(x, 16) for x in h.split(":")) for h in self.cmd("hits", "hits").split()[2:]]

    def quit(self):
        try:
            self.cmd("quit")
        except Exception:
            pass
        self.p.wait(timeout=60)
        self.err.close()

    # the Part
    def working_addr(self):
        return self.u32(BANK_PTR) + 0x8ed80 + self.peek(CUR_PART, 1)[0] * PART_LEN

    def state(self):
        b = self.u32(BANK_PTR)
        p = self.peek(CUR_PART, 1)[0]
        w = b + 0x8ed80 + p * PART_LEN
        return {"W": self.peek(w, PART_LEN), "S": self.peek(b + 0x9504a + p * PART_LEN, PART_LEN),
                "bits": self.peek(b + 0x95048, 1)[0] >> p & 1, "cs1": self.peek(CS1_WORK + p * PART_LEN, PART_LEN),
                "mutes": self.peek(MUTE_A, 2), "fader": self.u32(FADER),
                "weights": [self.u32(WEIGHTS + 4 * t) for t in range(8)], "p": p, "bank": b,
                "master": self.peek(MASTER_ON, 1)[0] != 0}


# ------------------------------------------------------------------ checks
def apply_case(e, img, label, mode, xf, texts, press=None):
    """press: run the key sequence itself (default: hold the mode's keys, tap YES)."""
    e.fader(xf)
    before = e.state()
    muted = [before["mutes"][0] != 0, before["mutes"][1] != 0]
    want = {}
    for t in range(8):
        want.update(model(img, before["W"], before["weights"], muted, t, before["master"], mode))
    changed = {o for o, v in want.items() if v != before["W"][o]}
    text_addr = texts[mode] if changed else texts["none"]
    e.watch([SITE, NOTIFY])
    if press:
        press()
    else:
        e.chord(MODES[mode][0], "yes")
    after = e.state()
    hits = e.hits()
    got = {i: after["W"][i] for i in range(PART_LEN) if after["W"][i] != before["W"][i]}
    wrong = {hex(o): (want.get(o, before["W"][o]), after["W"][o]) for o in set(want) | set(got)
             if after["W"][o] != want.get(o, before["W"][o])}
    check(not wrong, f"{label} xf {before['fader']:3d}: {len(want)} bytes applied as the model"
          + (f"; wrong {dict(list(wrong.items())[:8])}" if wrong else ""))
    check(after["S"] == before["S"], f"{label}: the saved Part is untouched")
    check(after["W"][SCN:SCN + 0x1000] == before["W"][SCN:SCN + 0x1000]
          and after["W"][XLV:XLV + 160] == before["W"][XLV:XLV + 160]
          and after["W"][SEL_A:SEL_A + 2] == before["W"][SEL_A:SEL_A + 2]
          and after["mutes"] == before["mutes"] and after["fader"] == before["fader"],
          f"{label}: scenes, XLV, selection, mutes and fader unchanged")
    check(after["cs1"] == after["W"], f"{label}: the CS1 copy equals the working Part")
    check(after["bits"] == (1 if want or before["bits"] else 0),
          f"{label}: unsaved bit {after['bits']} ({'changes' if want else 'no change'})")
    notes = [h for h in hits if h[1] == NOTIFY]
    check(len(notes) == 1 and notes[0][8] == text_addr, f"{label}: one toast, the module's text")
    entry = [h for h in hits if h[1] == SITE]
    if entry and notes:
        print(f"        cost: {notes[0][0] - entry[0][0]} instructions from the YES to the toast "
              f"({len(want)} writes)")
    return before, after, changed


def reload_part(e, label):
    e.chord("func", "cue", after=800)
    s = e.state()
    check(s["W"][:MACH] + s["W"][MACH + 8:] == s["S"][:MACH] + s["S"][MACH + 8:],
          f"{label}: RELOAD PART (FUNC + CUE) restores working = saved")


def voice_halfwords(e, t):
    out = []
    for ping in (0, 1):
        r = e.peek(VOICE + ping * 0x200 + t * 0x40, 36)
        out.append([int.from_bytes(r[i:i + 2], "big") for i in range(0, 36, 2)])
    return out


def sound_case(e, img, xf, mode):
    """T3/T8: AMP/FX halfwords = the model, before and after an apply."""
    e.cmd("frame on")                    # the frame engine: the builder runs the morph
    e.tap("play", after=1500)
    e.fader(xf)
    e.run(300)
    s = e.state()
    rows = {t: [s["W"][SCN + (s["W"][SEL_A + i] * 8 + t) * 32:][:32] for i in (0, 1)] for t in SOUND}

    def predicted(t, w):
        lane = e.peek(LANE + t * 72, 30)
        out = {}
        for k in range(12, 30):
            la = rows[t][0][k] if rows[t][0][k] < 128 else None
            lb = rows[t][1][k] if rows[t][1][k] < 128 else None
            out[k] = morph_hw(lane[k], la, lb, w)
        return out, lane

    pre = {t: predicted(t, s["weights"][t]) for t in SOUND}
    rec = {t: voice_halfwords(e, t) for t in SOUND}
    check(all(any(rec[t][0]) for t in SOUND), "sound: T3 and T8 have live voice records")
    bad = [(t, k) for t in SOUND for k in range(12, 30)
           if rec[t][0][k - 12] != pre[t][0][k] and rec[t][1][k - 12] != pre[t][0][k]]
    check(not bad, f"sound xf {s['fader']}: T3/T8 AMP/FX voice halfwords = the model from the live lane"
          + (f"; off at {bad[:6]}" if bad else ""))
    e.chord(MODES[mode][0], "yes")
    e.run(300)
    post = {t: predicted(t, s["weights"][t]) for t in SOUND}
    rec2 = {t: voice_halfwords(e, t) for t in SOUND}
    both = [(t, k) for t in SOUND for k in range(12, 30) if rows[t][0][k] < 128 and rows[t][1][k] < 128]
    one = [(t, k) for t in SOUND for k in range(12, 30) if (rows[t][0][k] < 128) != (rows[t][1][k] < 128)]
    check(all(rec2[t][0][k - 12] == rec[t][0][k - 12] or rec2[t][1][k - 12] == rec[t][1][k - 12] for t, k in both),
          f"sound, {mode}: {len(both)} bytes locked in both scenes kept their halfword through the apply")
    bad = [(t, k) for t, k in one if rec2[t][0][k - 12] != post[t][0][k] and rec2[t][1][k - 12] != post[t][0][k]]
    check(not bad, f"sound, {mode}: {len(one)} bytes locked in one scene follow the model from the new base"
          + (f"; off at {bad[:6]}" if bad else ""))
    e.tap("stop", after=500)


def main():
    for what, path in (("image", IMAGE), ("port", EMU), ("project", PROJECT)):
        if not path.exists():
            print(f"verify apply-scene: SKIP (no {what}: {path})")
            return 0
    img = Image(IMAGE)
    if img.bytes(SITE, 2) != b"\x4e\xf9":
        print(f"verify apply-scene: SKIP ({IMAGE} has no APPLY SCENE detour at {SITE:#x})")
        return 0
    hook = img.u32(SITE + 2)
    texts = {}
    for mode, words in [(m, w) for m, (_, w) in MODES.items()] + [("none", NONE_TEXT)]:
        at = img.d.find(words.encode() + b"\0", hook - BASE, hook - BASE + 0x400)
        if at < 0:
            sys.exit(f"verify apply-scene: the unit's text {words!r} is not where the detour points")
        texts[mode] = BASE + at
    print(f"verify apply-scene: image {hashlib.sha256(img.d).hexdigest()[:12]}, hook {hook:#x}, "
          f"texts {', '.join(hex(a) for a in texts.values())}")
    work = pathlib.Path(tempfile.mkdtemp(prefix="apply_scene_verify_"))
    card = build_fixture(img, work)
    shutil.copy2(card, work / "card0.img")

    e = Emu(card, work / "main.log")
    try:
        e.run(3000)
        e.tap("yes", after=1500)                       # the clock dialog
        s0 = e.state()
        check([s0["W"][MACH + t] for t in range(8)] == list(MACHINES) and s0["W"][SEL_A] == SCENE_A,
              f"fixture loaded: machines {[s0['W'][MACH + t] for t in range(8)]}, scenes {s0['W'][SEL_A]}/{s0['W'][SEL_B]}")

        print("verify apply-scene: the apply")
        label = {"a": "SCENE A + YES", "b": "SCENE B + YES", "mix": "SCENE A + B + YES"}
        for xf in (127, 96, 64, 32, 0):
            apply_case(e, img, label["mix"], "mix", xf, texts)
            reload_part(e, f"blend xf {xf}")
        for mode, xf in (("a", 64), ("b", 96), ("a", 0), ("b", 127)):
            apply_case(e, img, label[mode], mode, xf, texts)
            reload_part(e, f"{label[mode]} xf {xf}")
        apply_case(e, img, "SCENE A + YES", "a", 64, texts)
        _, _, again = apply_case(e, img, "SCENE A + YES again", "a", 64, texts)    # toast: NOTHING TO APPLY
        check(not again, "SCENE A + YES twice: the second writes nothing (its toast checked above)")
        reload_part(e, "applied twice")

        print("verify apply-scene: the keys that are down choose the mode")
        def seq(*steps):
            def run():
                for k, d in steps:
                    if k == "yes":
                        e.tap("yes")
                    else:
                        e.key(k, d)
                        e.run(150)
                e.run(400)
            return run
        held = []
        def snoop(run):
            def go():
                e.key("scene_b", True)
                e.run(150)
                e.key("scene_a", True)
                e.run(150)
                held.append((e.u32(SCENE_HELD), e.peek(KEY_STATE + 0x19 * 24, 1)[0], e.peek(KEY_STATE + 0x1a * 24, 1)[0]))
                run()
            return go
        apply_case(e, img, "B then A held + YES", "mix", 64, texts,
                   snoop(seq(("yes", 1), ("scene_a", False), ("scene_b", False))))
        check(held and held[0][0] == 1 and held[0][1] and held[0][2],
              f"B then A held: stock's held-scene word names A only ({held[0][0] if held else '?'}), "
              f"the key table has both")
        reload_part(e, "B then A")
        apply_case(e, img, "A + B, B released, YES", "a", 32, texts,
                   seq(("scene_a", True), ("scene_b", True), ("scene_b", False), ("yes", 1), ("scene_a", False)))
        reload_part(e, "B released")
        apply_case(e, img, "A + B, A released, YES", "b", 96, texts,
                   seq(("scene_a", True), ("scene_b", True), ("scene_a", False), ("yes", 1), ("scene_b", False)))
        reload_part(e, "A released")

        print("verify apply-scene: scene mutes")
        e.chord("func", "scene_a")
        check(e.peek(MUTE_A, 1)[0] != 0, "FUNC + SCENE A mutes scene A")
        apply_case(e, img, "A muted, blend", "mix", 64, texts)
        reload_part(e, "A muted, blend")
        apply_case(e, img, "A muted, SCENE A + YES", "a", 64, texts)
        reload_part(e, "A muted, scene A")
        e.chord("func", "scene_b")
        before = e.state()
        e.watch([NOTIFY])
        e.chord(("scene_a", "scene_b"), "yes")
        after = e.state()
        notes = [h for h in e.hits() if h[1] == NOTIFY]
        check(after["W"] == before["W"] and after["bits"] == before["bits"]
              and len(notes) == 1 and notes[0][8] == texts["none"],
              "both muted, blend: nothing applied, Part clean, toast NOTHING TO APPLY")
        apply_case(e, img, "both muted, SCENE B + YES", "b", 64, texts)
        reload_part(e, "both muted, scene B")
        e.chord("func", "scene_a")
        e.chord("func", "scene_b")
        check(e.peek(MUTE_A, 2) == b"\0\0", "mutes cleared again")

        print("verify apply-scene: stock flows")
        e.watch([0x4005e294, NOTIFY])
        e.key("yes", True)
        e.run(150)
        armed = int.from_bytes(e.peek(ARM_HELD, 2), "big")
        e.key("yes", False)
        e.run(300)
        h = e.hits()
        check(armed == 0xffff and int.from_bytes(e.peek(ARM_HELD, 2), "big") == 0
              and any(x[1] == 0x4005e294 for x in h) and not any(x[1] == NOTIFY and x[8] in texts.values() for x in h),
              "YES alone: stock ARM ALL (0x46c7ff64 set on press, cleared on release), no apply")
        before = e.state()
        e.key("yes", True)
        e.run(150)
        e.key("scene_a", True)
        e.run(150)
        e.key("yes", False)
        e.run(150)
        e.key("scene_a", False)
        e.run(300)
        after = e.state()
        check(after["W"] == before["W"] and int.from_bytes(e.peek(ARM_HELD, 2), "big") == 0,
              "YES held before SCENE A: stock press and release, no apply")
        e.key("scene_a", True)
        e.run(150)
        e.tap("trig3")
        e.key("scene_a", False)
        e.run(300)
        sel = e.state()["W"][SEL_A]
        e.key("scene_a", True)
        e.run(150)
        e.tap("trig2")                   # back to the fixture's scene 2
        e.key("scene_a", False)
        e.run(300)
        check(sel == 2 and e.state()["W"][SEL_A] == SCENE_A,
              f"SCENE A + TRIG selects a scene (TRIG 3 -> {sel}, TRIG 2 -> {e.state()['W'][SEL_A]})")
        e.tap("pg_amp", after=400)
        t = e.peek(0x100b14cc, 1)[0]                      # the current track
        st = e.state()
        row = SCN + (st["W"][SEL_A] * 8 + t) * 32
        e.key("scene_a", True)
        e.run(150)
        cur = st["W"][row + 15] if st["W"][row + 15] < 128 else st["W"][PG + t * 24 + 9]
        e.knob(3, -5 if cur >= 64 else 5)                  # knob D: AMP VOL
        e.run(300)
        e.key("scene_a", False)
        e.run(300)
        st2 = e.state()
        vol = PG + t * 24 + 6 + 3
        check(st2["W"][row + 15] != st["W"][row + 15] and st2["W"][vol] == st["W"][vol],
              f"SCENE A + knob D on AMP writes T{t + 1}'s scene lock "
              f"({st['W'][row + 15]} -> {st2['W'][row + 15]}), not the Part VOL ({st2['W'][vol]})")
        e.watch([0x40062f60, 0x40062da0, 0x40062e84])
        for k in ("rec", "stop", "play"):
            e.key("scene_b", True)
            e.run(150)
            e.tap(k)
            e.key("scene_b", False)
            e.run(300)
        h = {x[1] for x in e.hits()}
        check({0x40062f60, 0x40062da0, 0x40062e84} <= h, "SCENE + REC/STOP/PLAY reach their stock handlers")
        e.tap("stop", after=300)
        reload_part(e, "after the stock scene operations")

        print("verify apply-scene: the morph is stock's")
        for mode in ("a", "mix"):
            sound_case(e, img, 64, mode)
            reload_part(e, f"after the sound case, {mode}")

        print("verify apply-scene: Part save, project save")
        before, after, want = apply_case(e, img, "before saving", "mix", 96, texts)
        applied = after["W"]
        e.key("func", True)
        e.run(150)
        e.tap("part", after=600)         # FUNC + PART: RENAME, RELOAD, SAVE, SAVE ALL
        e.key("func", False)
        e.run(300)
        e.tap("down", after=200)
        e.tap("down", after=200)
        e.tap("yes", after=800)          # SAVE: "PART 1 SAVED"
        s = e.state()
        check(s["S"] == applied and s["bits"] == 0, f"Part SAVE: saved = applied, unsaved bit {s['bits']}")
        e.tap("proj", after=800)         # PROJECT: CHANGE, SAVE, ...
        e.tap("yes", after=400)
        e.tap("down", after=300)
        e.tap("yes", after=1500)         # SAVE PROJECT? ... CONTINUE?
        e.tap("yes", after=30000)        # YES, then the save runs
        e.cmd("card flush", "card")
    finally:
        e.quit()
    e2 = Emu(card, work / "reload.log")
    try:
        e2.run(3000)
        e2.tap("yes", after=1500)
        s = e2.state()
        check(s["W"] == applied and s["S"] == applied,
              f"project reload: working and saved Part = the applied Part ({sum(a != b for a, b in zip(s['W'], applied))} bytes differ)")
    finally:
        e2.quit()

    print("verify apply-scene: power cycle")
    pc_card = work / "card_pc.img"
    shutil.copy2(work / "card0.img", pc_card)
    e3 = Emu(pc_card, work / "pc1.log")
    try:
        e3.run(3000)
        e3.tap("yes", after=1500)
        _, after, want = apply_case(e3, img, "unsaved, before power-off", "b", 32, texts)
        e3.run(1000)
        cs1 = e3.peek(0x10000000, 0x100000)
        e3.cmd("card flush", "card")
    finally:
        e3.quit()
    (work / "cs1.bin").write_bytes(cs1)
    dump = work / "pc2_part.bin"
    mach = work / "pc2_mach.bin"
    p = after["p"]
    wa = after["bank"] + 0x8ed80 + p * PART_LEN
    r = subprocess.run([str(EMU), "--image", str(IMAGE), "--card", str(pc_card), "--set", "APPLYSC", "--project", "ASFIX",
                        "--mkii", "--cs1-in", str(work / "cs1.bin"), "--no-post", "--load-ms", "90000",
                        "--mem-dump", f"{wa:#x},{PART_LEN}={dump};{CS1_WORK + p * PART_LEN:#x},{PART_LEN}={mach}"],
                       capture_output=True, text=True, timeout=1800)
    (work / "pc2.log").write_text(r.stdout + r.stderr)
    if r.returncode or not dump.exists():
        check(False, f"power cycle: the second run failed ({work / 'pc2.log'})")
    else:
        got = dump.read_bytes()
        check(got == after["W"], f"power cycle: the unsaved applied Part survived "
              f"({sum(a != b for a, b in zip(got, after['W']))} bytes differ)")
        check([got[MACH + t] for t in range(8)] == list(MACHINES), f"power cycle: machines {[got[MACH + t] for t in range(8)]}")

    print(f"verify apply-scene: {'FAIL' if FAILS else 'PASS'} ({len(FAILS)} failure(s)); work in {work}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
