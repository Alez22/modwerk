"""Exercise menu-owner publication checks against the unchanged real runtime loader.

Host machine glue is synthetic. Exact SDK dependency hashes are pinned in the
source-bound manifest; this does not install a menu registry or exercise USB.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]
SOURCES=('menu_owner.c','menu_owner.h','menu_owner_backend.c','menu_owner_backend.h','editor_menu.c','editor_menu.h','test_menu_owner_loader_target.c','owner_package_vectors.h','test_owner_package_vectors.py','test_menu_owner_loader.py','menu-owner-runtime-sources.json')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path);a=p.parse_args()
    if a.output and a.output.exists():p.error('Use a new report path.')
    subprocess.run([sys.executable,'-B',str(ROOT/'test_owner_package_vectors.py')],check=True)
    pinned=json.loads((ROOT/'menu-owner-runtime-sources.json').read_text())
    cc=os.environ.get('CC','cc');results=[];dependencies={}
    octatrack=('-DRUNTIME_MODULES=128u','-DRUNTIME_POOL_BYTES=786432u')
    variants=((),('-DMODWERK_CACHED_MODULES',),octatrack,octatrack+('-DMODWERK_CACHED_MODULES',),
              octatrack+('-DMODWERK_RUNTIME_SETS',),octatrack+('-DMODWERK_RUNTIME_SETS','-DMODWERK_CACHED_MODULES'))
    flags=['-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-pedantic','-fsanitize=address,undefined','-fno-omit-frame-pointer']
    with tempfile.TemporaryDirectory(prefix='beat-slicer-owner-') as temp:
        work=Path(temp)
        driver=work/'main.c'
        driver.write_text('#include <stdio.h>\nint bs_owner_loader_target_selftest(void);\nint main(void){int line=bs_owner_loader_target_selftest();if(line){printf("FAIL line %d\\n",line);return 1;}puts("PASS: real loader and owner-backed menu; two owners, both layouts, replacement/restoration/removal, permanent retirement and restored allocation");return 0;}\n')
        for index,defines in enumerate(variants):
            sources=[ROOT/'test_menu_owner_loader_target.c',ROOT/'menu_owner.c',ROOT/'menu_owner_backend.c',ROOT/'editor_menu.c']
            if '-DMODWERK_RUNTIME_SETS' in defines:sources.append(REPO/'sdk/runtime/upload/upload.c')
            objects=[]
            for at,source in enumerate(sources):
                obj=work/f'{index}-{at}.o';dep=work/f'{index}-{at}.d'
                args=[cc,*flags,*defines,'-I',str(REPO/'sdk/runtime/loader'),'-I',str(REPO/'sdk/runtime/upload'),
                      '-MMD','-MF',str(dep),'-c',str(source),'-o',str(obj)]
                subprocess.run(args,check=True)
                # The paths supplied here contain no whitespace. Compiler output
                # enumerates actual transitive includes, not a guessed subset.
                words=dep.read_text().replace('\\\n',' ').split(':',1)[1].split()
                for word in words:
                    path=Path(word).resolve()
                    if path.is_relative_to(ROOT):continue
                    name=path.relative_to(REPO).as_posix();digest=sha(path)
                    if pinned['sha256'].get(name)!=digest:raise RuntimeError('SDK dependency differs: '+name)
                    dependencies[name]=digest
                objects.append(obj)
            exe=work/f'owner-{index}'
            subprocess.run([cc,*flags,*map(str,objects),str(driver),'-o',str(exe)],check=True)
            result=subprocess.run([str(exe)],text=True,capture_output=True,timeout=60)
            print(result.stdout,end='');print(result.stderr,end='')
            if result.returncode:raise RuntimeError('Owner-backed menu checks failed for '+repr(defines))
            results.append({'defines':list(defines),'exitCode':result.returncode,'stdout':result.stdout.splitlines()})
    report={'scope':'actual runtime loader with synthetic host machine glue; actual loader and full-owner menu fixture; both layouts and coexisting owners; synthetic machine services and no uploaded module execution; no native dispatcher, module execution or USB',
            'sourceSha256':{n:sha(ROOT/n) for n in SOURCES},'independentPackageVectors':4,'ownerFieldMismatchesPerLayout':8,
            'sdkRevision':pinned['revision'],
            'sdkDependencySha256':dict(sorted(dependencies.items())),
            'compiler':subprocess.check_output([cc,'--version'],text=True).splitlines()[0],
            'flags':flags,'variants':results,'exitCode':0,'hardware':'not tested','nativeMenu':'not integrated',
            'limits':'Production transition-time lease retirement, typed contribution admission, complete module-set readiness and retained-reference reclamation remain absent.'}
    if a.output:a.output.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: six actual-loader configurations; SDK compilation dependencies matched the exact pinned source manifest')
if __name__=='__main__':main()
