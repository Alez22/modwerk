#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""ABI 9 packages: base features and DSP claims (README.md, "Base features and DSP claims").

  python3 -B sdk/runtime/loader/abi9.py IN.mwrm -o OUT.mwrm --requires keybus [--claim y:0:r:0x800:0x200]

Takes a DSP package build.py made (ABI 6, 7 or 8, with DSP code) and writes the same package as ABI 9: the ABI 8 header
(76 bytes, copy and fill counts included) plus `requires` u16 (the base feature bits it needs, by name from
sdk/machines/octatrack/dsp-sites.json), the claim count u8 and the hook-entry count u8; after the fills, a 12-byte record
per claim (space, core, access, 0, address u32, words u32) and an 8-byte record per hook entry (site, cores, 0 u16, DSP
word u32), then the DSP words as before. Nothing else changes: image, relocations, sites, copies and fills are copied
byte for byte, so the stock-free checks and recipes that hold for the input hold for the output. Kept apart from build.py,
whose own hash is an input of the reviewed machine and standalone recipes.

A claim names X/Y words the DSP code reads or writes outside its own slot. A reader of a base feature (a KEYBUS reader)
claims nothing of the feature's words: the base owns them. Hook entries (a site of the base's DSP catalogue and an entry
in the DSP code) are encoded and checked, and every base refuses them until a hook-slot lifecycle exists.
"""
import argparse
import json
from pathlib import Path
import struct

HERE = Path(__file__).resolve().parent
REGISTRY = HERE.parents[1] / 'machines/octatrack/dsp-sites.json'
CLAIMS, HOOK_ENTRIES = 16, 8  # loader.h's RUNTIME_DSP_CLAIMS, RUNTIME_DSP_HOOK_ENTRIES
HEADERS = {6: 68, 7: 72, 8: 76, 9: 80}
ACCESS = {'r': 1, 'w': 2, 'rw': 3}


def base_features(names, registry=REGISTRY):
    """Base feature names (dsp-sites.json's features, e.g. keybus) as `requires` bits."""
    features = {f['name']: f['bit'] for f in json.loads(Path(registry).read_text())['features']}
    unknown = sorted(n for n in names if n not in features)
    if unknown:
        raise ValueError('No base feature %s (dsp-sites.json has %s).' % (', '.join(unknown), ', '.join(features)))
    return sum(features[n] for n in set(names))


def _meet(a, b):
    (sa, ca, aa, na), (sb, cb, ab, nb) = a, b
    return (aa >= 0x30000 and ab >= 0x30000 or (sa, ca) == (sb, cb)) and aa < ab + nb and ab < aa + na


def records(claims, entries, words):
    """The claim and hook-entry records, checked as the loader checks them. claims: (space 'x'|'y', core 0|1,
    access 'r'|'w'|'rw', address, words); entries: (site index, cores mask 1..3, DSP word)."""
    if len(claims) > CLAIMS or len(entries) > HOOK_ENTRIES or ((claims or entries) and not words):
        raise ValueError('Claims and hook entries need DSP code; at most %d and %d.' % (CLAIMS, HOOK_ENTRIES))
    out, spans = b'', []
    for space, core, access, address, n in claims:
        if space not in ('x', 'y') or core not in (0, 1) or access not in ACCESS or not 0 < n or \
                not 0 <= address < 0x40000 or address + n > 0x40000 or address < 0x30000 < address + n:
            raise ValueError('A DSP claim is a span of one core\'s X or Y memory, or of the shared window, never both.')
        span = (space, core, address, n)
        if any(_meet(span, s) for s in spans):
            raise ValueError('Two DSP claims of the package meet.')
        spans.append(span)
        out += struct.pack('>BBBxII', 1 if space == 'x' else 2, core, ACCESS[access], address, n)
    sites = set()
    for site, cores, entry in entries:
        if not 0 <= site < 256 or site in sites or cores not in (1, 2, 3) or not 0 <= entry < words:
            raise ValueError('A hook entry names one site once, its cores and one of its DSP words.')
        sites.add(site)
        out += struct.pack('>BBHI', site, cores, 0, entry)
    return out


def upgrade(data, requires=0, claims=(), entries=()):
    """`data` (an ABI 6, 7 or 8 package with DSP code) as ABI 9."""
    if data[:4] != b'MWRM' or len(data) < 68:
        raise ValueError('Not a runtime package.')
    abi, flags = struct.unpack_from('>HH', data, 4)
    if abi not in (6, 7, 8):
        raise ValueError('ABI 9 extends an ABI 6, 7 or 8 package; this one is ABI %d.' % abi)
    if not 0 <= requires < 0x10000:
        raise ValueError('requires is a 16-bit mask of base features.')
    words, relocations = struct.unpack_from('>IH', data, 32)
    if not words:
        raise ValueError('ABI 9 describes DSP code: the package has none.')
    tail = 4 * words + 2 * relocations
    header, body = HEADERS[abi], data[HEADERS[abi]:]
    if len(body) < tail:
        raise ValueError('The package is shorter than its DSP code.')
    image, _, count, hooks, sites = struct.unpack_from('>IIIII', data, 8)
    if abi == 6:
        # ABI 6 site records carry stock bytes and its relocations may come in any order: ABI 7 on reads neither so.
        offsets = struct.unpack_from('>%dI' % count, data, header + 4 * hooks + image)
        if sites or any(b < a + 4 for a, b in zip(offsets, offsets[1:])):
            raise ValueError('An ABI 6 package with stock-code sites or unordered relocations cannot become ABI 9.')
    counts = data[68:76] if abi == 8 else data[68:72] + bytes(4) if abi == 7 else bytes(8)
    added = records(claims, entries, words)
    head = data[:4] + struct.pack('>HH', 9, flags) + data[8:68] + counts + struct.pack('>HBB', requires, len(claims), len(entries))
    return head + body[:len(body) - tail] + added + body[len(body) - tail:]


def parse_claim(text):
    space, core, access, address, words = text.split(':')
    return space, int(core), access, int(address, 0), int(words, 0)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('package', type=Path)
    parser.add_argument('-o', '--output', type=Path, required=True)
    parser.add_argument('--requires', action='append', default=[], metavar='FEATURE', help='a base feature, e.g. keybus')
    parser.add_argument('--claim', action='append', default=[], metavar='SPACE:CORE:ACCESS:ADDRESS:WORDS',
                        help='X/Y words read (r) or written (w, rw) outside the slot, e.g. y:0:w:0x7a0:16')
    args = parser.parse_args()
    try:
        data = upgrade(args.package.read_bytes(), base_features(args.requires), [parse_claim(c) for c in args.claim])
    except ValueError as error:
        parser.error(str(error))
    args.output.write_bytes(data)
    print('%s: ABI 9, requires %#x, %d claims, %d bytes' % (args.output, struct.unpack_from('>H', data, 76)[0], data[78], len(data)))


if __name__ == '__main__':
    main()
