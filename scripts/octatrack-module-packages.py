#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Portable host entry point for the qualified Octatrack package builder."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

APP = Path(__file__).resolve().parents[1]


def lag_guard(builder, check):
    """USB packages at an older version than the catalogue, by manifest index.

    A declared lag ("lagsBehind": the catalogue version it lags, "lagReason": why,
    with its issue) stays published as it is: its source has moved on, so it
    cannot be rebuilt. Remove both keys to rebuild it. With --check any other lag,
    or a lag note left behind, fails without a toolchain, so CI catches a release
    that left its USB package behind. Kept here, not in the builder, whose source
    the base pins."""
    manifest = json.loads(builder.MANIFEST.read_text())
    versions = {m['id']: m['version'] for m in json.loads((APP / 'sdk/catalog.json').read_text())['modules']}
    held, failed = {}, 0
    for at, entry in enumerate(manifest['packages']):
        version = versions[entry['id']]
        if entry['version'] != version and entry.get('lagsBehind') == version:
            print('%-18s kept at %s, catalogue %s: %s' % (entry['id'], entry['version'], version, entry.get('lagReason')))
        elif check and (entry['version'] != version or 'lagsBehind' in entry):
            print('%-18s DIFFERS: the USB package is %s, the catalogue %s (lagsBehind %s); rebuild it' % (
                entry['id'], entry['version'], version, entry.get('lagsBehind')))
            failed = 1
        else:
            continue
        held[at] = entry
    return manifest, held, failed


def run(builder):
    try:
        builder.main()
    except subprocess.CalledProcessError as error:
        print(error.stdout or '', end='', file=sys.stderr)
        print(error.stderr or '', end='', file=sys.stderr)
        raise SystemExit(error.returncode) from error


def main():
    spec = importlib.util.spec_from_file_location(
        'octatrack_module_packages', APP / 'sdk/machines/octatrack/elekloader/module_packages.py')
    builder = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = builder
    spec.loader.exec_module(builder)
    # The qualified builder's JSON:KEY syntax predates Windows drive letters.
    # Use its documented relative-path form, without altering any base input.
    builder.DSP = builder.DSP.relative_to(APP)
    os.chdir(APP)
    # Python's -X utf8 does not propagate to the builder's Python children.
    os.environ['PYTHONUTF8'] = '1'
    if '--prepare-ports' in sys.argv[1:]:
        return run(builder)
    check = '--check' in sys.argv[1:]
    manifest, held, failed = lag_guard(builder, check)
    if not held:
        return run(builder)
    # The builder sees the manifest without the held packages; they go back in afterwards, file and row unchanged.
    real, kept = builder.MANIFEST, {entry['path']: (builder.PUBLIC / entry['path']).read_bytes() for entry in held.values()}
    with tempfile.TemporaryDirectory() as work:
        builder.MANIFEST = Path(work) / 'packages.json'
        builder.MANIFEST.write_text(json.dumps(dict(manifest, packages=[
            entry for at, entry in enumerate(manifest['packages']) if at not in held])))
        try:
            run(builder)
            code = 0
        except SystemExit as done:
            code = done.code
        if not check:
            for path, data in kept.items():  # the builder clears public/octatrack-modules before writing
                (builder.PUBLIC / path).parent.mkdir(parents=True, exist_ok=True)
                (builder.PUBLIC / path).write_bytes(data)
            if code in (0, 1):  # the builder wrote its manifest
                written = json.loads(builder.MANIFEST.read_text())
                for at in sorted(held):
                    written['packages'].insert(at, held[at])
                real.write_text(json.dumps(written, indent=2) + '\n')
    raise SystemExit(code or failed)


if __name__ == '__main__':
    main()
