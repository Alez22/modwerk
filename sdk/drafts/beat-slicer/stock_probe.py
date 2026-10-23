"""Run isolated stock routines in a CPU emulator using a private, hash-bound OS.

No device access. UI/task callees are mocked where the C++ source says so.
This is not full editor execution, storage, concurrency, timing or audio proof.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from inspect_stock import STOCK_MAIN_SHA256

ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--main', type=Path, required=True)
    parser.add_argument('--executable', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--kind', choices=('editor', 'storage'), default='editor')
    args = parser.parse_args()
    source = ROOT / 'stock_probe' / ('storage_probe.cpp' if args.kind == 'storage' else 'probe.cpp')
    if digest(args.main) != STOCK_MAIN_SHA256:
        parser.error('Expected original 1.40C MAIN; refusing another input.')
    if args.output.exists():
        parser.error('Use a new report path; preserve previous evidence.')
    result = subprocess.run([str(args.executable.resolve()), str(args.main.resolve())],
                            text=True, capture_output=True, timeout=120)
    if 'SOURCE_SHA256: ' + digest(source) not in result.stdout.splitlines():
        parser.error('Probe executable does not match current source; rebuild before recording evidence.')
    report = {
        'scope': ('isolated stock storage routines with synthetic memory IO and explicit follow-up mocks; no device access'
                  if args.kind == 'storage' else
                  'isolated stock CPU routines with explicit UI/task mocks; no device access'),
        'mainSha256': STOCK_MAIN_SHA256,
        'sourceSha256': {str(p.relative_to(ROOT)): digest(p) for p in
                         (ROOT / 'stock_probe.py', source,
                          ROOT / 'stock_probe/CMakeLists.txt')},
        'executableSha256': digest(args.executable),
        'exitCode': result.returncode, 'stdout': result.stdout.splitlines(),
        'stderrLines': len(result.stderr.splitlines()),
        'stderrSha256': hashlib.sha256(result.stderr.encode()).hexdigest(),
        'hardware': 'not tested', 'audio': 'not tested', 'stockPersistence': 'not tested',
    }
    with args.output.open('x') as output:
        output.write(json.dumps(report, indent=2) + '\n')
    print(result.stdout, end='')
    if result.stderr:
        print(result.stderr, end='')
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
