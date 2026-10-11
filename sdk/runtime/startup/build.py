#!/usr/bin/env python3
"""Apply original Modwerk artwork to a locally composed Octatrack MAIN image.

Only two guarded graphic tables change. Firmware input and output stay local.
This is also the independent native oracle for the browser implementation.

With a base version the same writes also carry the base edition (base.json):
"NEW" and the version as extra particles, the LED choreography and its time step.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct

BASE = 0x40000400
ARTWORK = Path(__file__).with_name("artwork.json")
EDITION = Path(__file__).with_name("base.json")


def delay(x, y):
    if x >= 26 and y >= 26:
        return 20
    if 6 <= x <= 27 and 6 <= y <= 27 and (x - 6) % 8 < 6 and (y - 6) % 8 < 6:
        order = ((1, 2, 3), (8, 0, 4), (7, 6, 5))[(y - 6) // 8][(x - 6) // 8]
        return 248 - order * 18
    dx, dy = x - 16, y - 16
    if dy < 0 and dx >= 0:
        phase = dx * 32 // (dx - dy)
    elif dx >= 0 and dy >= 0:
        phase = 32 + dy * 32 // (dx + dy)
    elif dy >= 0:
        phase = 64 + -dx * 32 // (dy - dx)
    else:
        phase = 96 + -dy * 32 // (-dx - dy)
    return 255 - phase // 2


def text_points(edition, version):
    """Particle records (x, y, delay) for the base edition's text, plus the pixels they land on."""
    font, points, pixels = edition["font"], [], set()
    for item in edition["text"]:
        string = item["string"].replace("{version}", version)
        scale, gap, cells, x = item["scale"], item["gap"], [], 0
        for index, char in enumerate(string):
            if char not in font:
                raise ValueError("Startup font has no glyph for " + repr(char))
            glyph = font[char]
            for gy, row in enumerate(glyph):
                for gx, ink in enumerate(row):
                    if ink == "#":
                        cells += [(x + gx * scale + dx, gy * scale + dy, index) for dy in range(scale) for dx in range(scale)]
            x += len(glyph[0]) * scale + gap
        left = item["x"] - {"left": 0, "center": (x - gap) // 2, "right": x - gap}[item["align"]]
        for cx, cy, index in cells:
            px, py = left + cx, item["y"] + cy
            # The stock renderer lands particles on the bottom three rows one pixel to the left.
            if not (0 <= px < 128 and 0 <= py <= 60):
                raise ValueError("Startup text leaves the safe screen area: " + string)
            # The renderer lands a record when (time + delay - 256) reaches 256; time counts 5 ms.
            land = item["landMs"] + index * item["stepMs"]
            points.append((px - 63, 21 - py, 512 - round(land / 5)))
            pixels.add((px, py))
    return points, pixels


def authored_ink(art, dy=0):
    """Display pixels of the mark and the wordmark, both lowered by dy rows."""
    ink = set()
    for key in ("mark", "wordmark"):
        layer = art[key]
        ink |= {(layer["x"] + x, layer["y"] + dy + y) for y, row in enumerate(layer["rows"]) for x, pixel in enumerate(row) if pixel == "#"}
    return ink


def lamp_table(times):
    """Stock-format (x, y) lamp coordinates whose two brightness waves peak at the given times.

    The boot loop lights channel A at 15 - |((y - x - 8200) >> 10) + s| and channel B at
    15 - |((x + y - 25800) >> 10) + s|, with s the loop time in 10 ms steps minus 96; each lamp's
    two integers therefore set when its red and green channels peak."""
    table = b""
    for a, b in times:
        if a % 10 or b % 10:
            raise ValueError("LED times are multiples of 10 ms")
        pa, pb = (192 - a // 5) // 2, (192 - b // 5) // 2
        table += struct.pack(">ii", 8800 + 512 * (pb - pa), 17000 + 512 * (pb + pa))
    return table


def edition_writes(version):
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("The base version is major.minor.patch")
    edition = json.loads(EDITION.read_text())
    if edition["schema"] != 1:
        raise ValueError("Invalid startup edition")
    return edition, text_points(edition, version)


def writes(version=None):
    art = json.loads(ARTWORK.read_text())
    if (art["schema"], art["width"], art["height"], art["durationMs"], art["particles"], art["wordmark"]["x"], art["wordmark"]["y"]) != (1, 128, 64, 2800, 843, 8, 39):
        raise ValueError("Invalid startup animation layout")
    for key, width, height in (("wordmark", 110, 15), ("mark", 34, 34)):
        layer = art[key]
        if (len(layer["rows"]) != height or any(len(row) != width or set(row) - {".", "#"} for row in layer["rows"])
                or layer["x"] < 0 or layer["y"] < 0 or layer["x"] + width > 128 or layer["y"] + height > 64):
            raise ValueError("Invalid startup animation artwork")
    wordmark = b"".join(struct.pack(">I", sum(1 << (17 + y) for y in range(15) if art["wordmark"]["rows"][y][x] == "#")) for x in range(110))
    layer = art["mark"]
    edition, (text, text_pixels) = edition_writes(version) if version is not None else (None, ([], set()))
    dy = edition["layout"]["dy"] if edition else 0   # the base lowers the whole composition so the top edge breathes
    points = [(layer["x"] + x - 63, 21 - layer["y"] - dy - y, delay(x, y), x >= 26 and y >= 26)
              for y, row in enumerate(layer["rows"]) for x, pixel in enumerate(row) if pixel == "#"]
    if not 0 < len(points) <= art["particles"]:
        raise ValueError("Startup animation exceeds the stock particle budget")
    records = []
    if version is None:
        for i in range(art["particles"]):
            x, y, phase, mod = points[i if i < len(points) else (i - len(points)) * 137 % len(points)]
            records.append(struct.pack(">hhh", x, y, phase - 16 if mod and i >= len(points) else phase))
    else:
        if authored_ink(art, dy) & text_pixels:
            raise ValueError("Startup text overlaps the mark or the wordmark")
        room = art["particles"] - len(points) - len(text)
        if room < 0:
            raise ValueError("Startup text exceeds the particle budget")
        # The ninth tile's comet tail takes what the text leaves; any rest repeats earlier records.
        tail = [(x, y, phase - 16) for x, y, phase, mod in points if mod][:room]
        every = [(x, y, phase) for x, y, phase, mod in points] + text + tail
        for i in range(art["particles"]):
            records.append(struct.pack(">hhh", *every[i if i < len(every) else (i - len(every)) * 137 % len(every)]))
    particles = b"".join(records)
    result = []
    for key, data in (("particles", particles), ("wordmark", wordmark)):
        guard = art["guards"][key]
        if guard["bytes"] != len(data):
            raise ValueError("Invalid startup animation guard size")
        result.append((guard, data))
    if version is not None:
        # The wordmark's blit takes its row from `pea #10`; fewer is lower on the screen.
        moved = [("wordmarkY", struct.pack(">H", 10 - dy))] if dy else []
        for key, data in (("mkii", lamp_table(edition["led"]["mkii"])), ("mki", lamp_table(edition["led"]["mki"])),
                          ("stepRound", edition["stepWords"]["stepRound"]), ("stepShift", edition["stepWords"]["stepShift"]), *moved):
            guard = edition["guards"][key]
            data = bytes.fromhex(data) if isinstance(data, str) else data
            if guard["bytes"] != len(data):
                raise ValueError("Invalid startup edition guard size: " + key)
            result.append((guard, data))
    return result


def apply(image, version=None):
    plan = writes(version)
    # Validate both guards before making a copy or applying either write.
    for guard, data in plan:
        at = guard["address"] - BASE
        if at < 0 or at + len(data) > len(image) or hashlib.sha256(image[at:at + len(data)]).hexdigest() != guard["sha256"]:
            raise ValueError("Original startup graphics differ: " + hex(guard["address"]))
    result = bytearray(image)
    for guard, data in plan:
        at = guard["address"] - BASE
        result[at:at + len(data)] = data
    return bytes(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--base-version", help="also apply the base edition (NEW, version, LED choreography), e.g. 0.3.1")
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve():
        parser.error("Use a separate output; preserve the original image.")
    result = apply(args.input.read_bytes(), args.base_version)
    args.output.write_bytes(result)
    print(f"Modwerk startup: {len(result)} bytes, SHA-256 {hashlib.sha256(result).hexdigest()}")
