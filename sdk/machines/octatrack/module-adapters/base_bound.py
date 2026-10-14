# SPDX-License-Identifier: GPL-3.0-or-later
"""Runtime packages bound to one exact public base (their manifest entry names it as requiredBase).

The controller packages (Sidechain Compressor, Output Matrix) call the base's write-lease entries by absolute address,
and the base admits them only through the trust rows built into it (controller-policies.json). The cave ports (CC Map,
Recorder Loop Fix) are linked for the base's moved arena and its runtime pool. `npm run octatrack:base` writes what they
link against, src/engine/assets/octatrack-base-binding.json, from the base it actually built (runtime_candidate.bind_base:
image, symbol map and IDENTIFY digest agree). This rebuilds each package from source and that binding, with no firmware;
given the stock OS, the cave ports' stock guards are also checked against it.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
APP = HERE.parents[3]
sys.path.insert(0, str(HERE))
import candidate_packages  # noqa: E402
import cave_runtime  # noqa: E402
import runtime_candidate  # noqa: E402
import stock_hook_controllers  # noqa: E402

BINDING = APP / 'src/engine/assets/octatrack-base-binding.json'
POLICIES = HERE / 'controller-policies.json'
# The base symbols a package names: the lease entries, the mark that the base owns Output Matrix's boot widenings, and
# the slot that tells Sidechain the base raises ev_mute_keep.
SYMBOLS = (*stock_hook_controllers.LEASE_IMPORTS, stock_hook_controllers.BASE_OWNED_MARK,
           'modwerk_raise_' + stock_hook_controllers.MUTE_KEEP['event'])
MODULES = (*stock_hook_controllers.UNITS, *cave_runtime.PORTS)


def bind(build, policies):
    """The binding of one base build_core.py made (its directory), with the trust rows it was built with."""
    build = Path(build)
    symbols = json.loads((build / 'symbols.json').read_text())
    bound = runtime_candidate.bind_base((build / 'MAIN.raw').read_bytes(), symbols,
                                        json.loads((build / 'proofs.json').read_text()))
    controllers = {row['module']: row['packageSha256'] for row in policies}
    if any(name not in stock_hook_controllers.UNITS for name in controllers):
        raise ValueError('A trust row names a module that is not a controller.')
    return dict(schema=1, identity=bound['identity'], arena=bound['arena'], pool=bound['pool'],
                symbols={name: symbols[name] for name in SYMBOLS if name in symbols}, controllers=controllers)


def load(binding=None):
    binding = json.loads(BINDING.read_text()) if binding is None else binding
    if (binding.get('schema') != 1 or not isinstance(binding.get('identity'), str) or len(binding['identity']) != 64
            or any(type(binding.get(key)) is not int for key in ('arena', 'pool'))
            or not isinstance(binding.get('symbols'), dict) or not isinstance(binding.get('controllers'), dict)):
        raise ValueError('src/engine/assets/octatrack-base-binding.json is malformed: rebuild the base.')
    return binding


def build(module, upstream, work, stock_at=None, binding=None):
    """One base-bound package and the base identity it needs."""
    binding, work = load(binding), Path(work)
    spec = importlib.util.spec_from_file_location('base_bound_builder', APP / 'sdk/runtime/loader/build.py')
    builder = importlib.util.module_from_spec(spec); spec.loader.exec_module(builder)
    if module in stock_hook_controllers.UNITS:
        encoded = stock_hook_controllers.encode(module, APP / 'sdk/octabam', builder, work, binding['symbols'], upstream)
        if binding['controllers'].get(module) != encoded['packageSha256']:
            raise ValueError('%s: the base\'s trust row names another package; rebuild the base '
                             '(npm run octatrack:base -- --controllers --write).' % module)
        data = encoded['package']
    elif module in cave_runtime.PORTS:
        bound = dict(arena=binding['arena'], poolOrigins=runtime_candidate.pool_origins(binding['pool']))
        work.mkdir(parents=True, exist_ok=True)
        data, _ = candidate_packages.authored(APP, upstream, module, builder, bound, stock_at, work, 'm68k-elf-')
    else:
        raise ValueError('No base-bound route for ' + module)
    builder.unevented(*candidate_packages.records(data))  # never a write or copy on a site the base owns
    return data, binding['identity']


def main(argv=None):
    ap = argparse.ArgumentParser(description='Write the binding of one base build (npm run octatrack:base runs this).')
    ap.add_argument('build', type=Path, help="build_core.py's output directory")
    ap.add_argument('--policies', type=Path, help='the controller trust rows it was built with')
    ap.add_argument('-o', '--output', type=Path, required=True)
    a = ap.parse_args(argv)
    rows = json.loads(a.policies.read_text()) if a.policies else []
    a.output.write_text(json.dumps(bind(a.build, rows), indent=1) + '\n')


if __name__ == '__main__':
    main()
