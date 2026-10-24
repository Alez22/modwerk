"""Compile and execute the real SDK loader and menu adapter with pinned tools.

Reuse the source-bound stock-free CPU runner from job_native.py; no firmware IO.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(*args):
    return subprocess.check_output(args, text=True).strip()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--cached',action='store_true')
    p.add_argument('--sets',action='store_true')
    p.add_argument('--executable', type=Path, required=True)
    a = p.parse_args()
    out, repo = a.output.resolve(), ROOT.parents[2]
    if out == repo or repo in out.parents:
        p.error('Keep binaries outside the repository.')
    out.mkdir(parents=True, exist_ok=False)
    spec = importlib.util.spec_from_file_location('guard', repo / 'sdk/runtime/m68k_codegen.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    flags = ['-std=c99', '-mcpu=5475', '-msoft-float', '-O2', '-ffreestanding',
             '-fno-builtin', '-fno-common', '-fno-jump-tables',
             '-fno-tree-loop-distribute-patterns', '-fno-optimize-sibling-calls',
             '-fno-asynchronous-unwind-tables', '-fno-unwind-tables', '-fno-ident',
             '-fstack-usage', '-Wall', '-Wextra', '-Werror', '-pedantic', *guard.FLAGS, '-DRUNTIME_MODULES=128u', '-DRUNTIME_POOL_BYTES=786432u', '-I', str(repo/'sdk/runtime/upload')]
    if a.cached: flags.append('-DMODWERK_CACHED_MODULES')
    if a.sets: flags.append('-DMODWERK_RUNTIME_SETS')
    subprocess.run([sys.executable,'-B',str(ROOT/'test_owner_package_vectors.py')],check=True)
    objects = []; dependencies = {}; pinned = json.loads((ROOT/'menu-owner-runtime-sources.json').read_text())
    sources=[ROOT/(n+'.c') for n in ('menu_owner','menu_owner_backend','editor_menu','test_menu_owner_loader_target')]
    if a.sets:sources.append(repo/'sdk/runtime/upload/upload.c')
    for source in sources:
        name=source.stem
        obj = out / (name + '.o')
        dep = out/(name+'.d')
        run('m68k-elf-gcc', *flags, '-MMD','-MF',str(dep), '-c', str(source), '-o', str(obj))
        for word in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
            path=Path(word).resolve()
            if path.is_relative_to(ROOT): continue
            key=path.relative_to(repo).as_posix(); value=sha(path)
            if pinned['sha256'].get(key)!=value: raise RuntimeError('SDK dependency differs: '+key)
            dependencies[key]=value
        objects.append(obj)
    guard.check(objects)
    elf, binary = out / 'menu-owner-loader-target.elf', out / 'menu-owner-loader-target.bin'
    run('m68k-elf-ld', '--no-undefined', '-e', 'bs_owner_loader_target_selftest', '-Ttext=0x47040000', '-Tbss=0x47400000',
        *map(str, objects), '-o', str(elf))
    if run('m68k-elf-nm', '-u', str(elf)):
        p.error('Unresolved runtime helpers.')
    run('m68k-elf-objcopy', '-O', 'binary', str(elf), str(binary))
    all_symbols={row.split()[-1]:int(row.split()[0],16) for row in run('m68k-elf-nm',str(elf)).splitlines() if len(row.split())==3}
    bss,=[row.split() for row in run('m68k-elf-objdump','-h',str(elf)).splitlines() if len(row.split())>4 and row.split()[1]=='.bss']
    bss_start,bss_bytes=int(bss[3],16),int(bss[2],16)
    assert bss_start==0x47400000 and 786432<bss_bytes<0x100000
    assert bss_start+bss_bytes<0x47500000
    entry, = [line.split()[0] for line in run('m68k-elf-nm', str(elf)).splitlines()
              if line.split()[-1] == 'bs_owner_loader_target_selftest']
    r = subprocess.run([str(a.executable.resolve()), str(binary), '0x' + entry],
                       text=True, capture_output=True, timeout=600)
    if 'SOURCE_SHA256: ' + sha(ROOT / 'stock_probe/job_probe.cpp') not in r.stdout.splitlines():
        p.error('Runner differs from current source; rebuild it.')
    names = ('menu_owner.c','menu_owner.h','menu_owner_backend.c','menu_owner_backend.h','editor_menu.c','editor_menu.h','test_menu_owner_loader_target.c','test_menu_owner_set.h','owner_package_vectors.h','test_owner_package_vectors.py','menu_owner_loader_native.py','menu-owner-runtime-sources.json','stock_probe/job_probe.cpp','stock_probe/CMakeLists.txt')
    report = {
        'scope': 'real compiled SDK loader/SHA with full-owner menu adapter, both layouts and two owners; actual ColdFire entry wrappers; synthetic stopped/cache/paused-task/DSP services; no module-code execution, stock menu, USB or hardware integration',
        'sourceSha256': {n: sha(ROOT / n) for n in names},
        'wholeSetScenarios':4 if a.sets else 0,'wholeSetEnabled':a.sets,
        'runtimeModules':128,'runtimePoolBytes':786432,'cachedModuleBranch':a.cached,'nativeSdkLoader':True,
        'bssStart':bss_start,'bssEnd':bss_start+bss_bytes,
        'codegenGuardSha256':sha(repo/'sdk/runtime/m68k_codegen.py'),
        'independentPackageVectors':4,'ownerFieldMismatchesPerLayout':8,
            'sdkRevision': pinned['revision'], 'sdkDependencySha256': dependencies,
        'compiler': run('m68k-elf-gcc', '--version').splitlines()[0], 'flags': flags,
        'objectSha256': {o.name: sha(o) for o in objects},
        'runnerSha256': sha(a.executable), 'codegenGuard': 'passed', 'freestandingLink': True,
        'ownerSize': run('m68k-elf-size', str(out / 'menu_owner.o')).splitlines(),
        'exchangeSize': run('m68k-elf-size', str(out / 'menu_owner_backend.o')).splitlines(),
        'exchangeStackUsage': (out / 'menu_owner_backend.su').read_text().splitlines(),
        'exitCode': r.returncode, 'stdout': r.stdout.splitlines(),
        'stderrLines': len(r.stderr.splitlines()),
        'stderrSha256': hashlib.sha256(r.stderr.encode()).hexdigest(),
        'hardware': 'not tested', 'audio': 'not tested', 'timing': 'not measured',
        'nativeSourceAccess': 'not implemented',
    }
    (out / 'menu-owner-loader-target.json').write_text(json.dumps(report, indent=2) + '\n')
    print(r.stdout, end='')
    if r.returncode:
        print(r.stderr, end='')
    raise SystemExit(r.returncode)


if __name__ == '__main__':
    main()
