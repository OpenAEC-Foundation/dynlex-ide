#!/usr/bin/env python3
"""Build Studio in its pinned dynlex.com host, or run the editor's Wasm fixtures."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from export_sdk import ROOT, export

HOST_REVISION = '5fd628b4f2f4c35b49f2bfc84bcd0913f7e04e11'
HOST_REPOSITORY = 'https://github.com/OpenAEC-Foundation/dynlex-website.git'


def test_editor(host, workspace):
    compiler = Path(subprocess.check_output([sys.executable, 'scripts/dependencies.py'], cwd=host, text=True).strip())
    sys.path.insert(0, str(host / 'scripts'))
    from dependencies import dependency

    sources = dependency('dynlex-ui').source_files('packages/dynlex-ui')
    sources.update(dependency('dynlex-ide').source_files('packages/dynlex-ide'))
    jobs = []
    fixtures = sorted((ROOT / 'tests/shared').glob('*/main.dl'))
    for source in fixtures:
        entry = 'packages/dynlex-ide/' + source.relative_to(ROOT).as_posix()
        sources[entry] = source.read_text()
        jobs.append({'entry': entry, 'kind': 'wasm', 'output': source.parent.name + '.wasm'})
    request = workspace / 'fixtures.json'
    request.write_text(json.dumps({'sources': sources, 'jobs': jobs}))
    subprocess.run(['node', compiler / 'scripts/compile_project.mjs', request, workspace], check=True)
    for source, job in zip(fixtures, jobs, strict=True):
        result = subprocess.check_output(['node', compiler / 'scripts/run_program.mjs', workspace / job['output']], text=True)
        if result != source.with_name('expected.txt').read_text():
            raise AssertionError(f'{source.parent.name}: unexpected output {result!r}')
        print(f'PASS {source.parent.name}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host-repository', default=HOST_REPOSITORY,
                        help='Git URL or local repository containing the pinned website host revision')
    parser.add_argument('--output', type=Path, default=ROOT / 'build/site')
    parser.add_argument('--test', action='store_true', help='Run all editor fixtures instead of building the site')
    args = parser.parse_args()
    repository = args.host_repository
    if Path(repository).exists():
        repository = str(Path(repository).resolve())
    (ROOT / 'build').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT / 'build') as temporary:
        workspace = Path(temporary)
        host = workspace / 'host'
        subprocess.run(['git', 'init', '--quiet', host], check=True)
        subprocess.run(['git', 'fetch', '--quiet', '--depth=1', repository, HOST_REVISION], cwd=host, check=True)
        subprocess.run(['git', 'checkout', '--quiet', '--detach', 'FETCH_HEAD'], cwd=host, check=True)
        archive = workspace / 'dynlex-ide.zip'
        export(archive)
        subprocess.run([sys.executable, 'scripts/update_dependency.py', archive], cwd=host, check=True)
        if args.test:
            test_editor(host, workspace)
        else:
            subprocess.run(['npm', 'ci'], cwd=host, check=True)
            subprocess.run([sys.executable, 'scripts/build_site.py', '--output', args.output.resolve()], cwd=host, check=True)


if __name__ == '__main__':
    main()
