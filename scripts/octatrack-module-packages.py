#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Portable host entry point for the qualified Octatrack package builder."""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

APP = Path(__file__).resolve().parents[1]


def only_key_bus(capabilities):
    """An ABI 9 package may require only the key bus: the one base feature the site accepts in a manifest
    (src/engine/elekloader/module-set.ts, BASE_DSP_FEATURES), so a package needing any other bit would make the whole
    published list inconsistent there and stop every USB sync. Checked here, not in the builder, whose source is a
    base input."""
    registry = json.loads((APP / 'sdk/machines/octatrack/dsp-sites.json').read_text())
    keybus = next(f['bit'] for f in registry['features'] if f['name'] == 'keybus')

    def checked(data):
        found = capabilities(data)
        if found.get('requires', 0) & ~keybus:
            raise ValueError('A published package may require only the key bus (requires %#x).' % found['requires'])
        return found
    return checked


def main():
    spec = importlib.util.spec_from_file_location(
        'octatrack_module_packages', APP / 'sdk/machines/octatrack/elekloader/module_packages.py')
    builder = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = builder
    spec.loader.exec_module(builder)
    # The qualified builder's JSON:KEY syntax predates Windows drive letters.
    # Use its documented relative-path form, without altering any base input.
    builder.DSP = builder.DSP.relative_to(APP)
    builder.capabilities = only_key_bus(builder.capabilities)
    os.chdir(APP)
    # Python's -X utf8 does not propagate to the builder's Python children.
    os.environ['PYTHONUTF8'] = '1'
    try:
        builder.main()
    except subprocess.CalledProcessError as error:
        print(error.stdout or '', end='', file=sys.stderr)
        print(error.stderr or '', end='', file=sys.stderr)
        raise SystemExit(error.returncode) from error


if __name__ == '__main__':
    main()
