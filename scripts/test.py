#!/usr/bin/env python3
"""Cross-check editor fixtures with native and shipped compilers and the live language server."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--dynlex', required=True, type=Path)
parser.add_argument('--ui', required=True, type=Path)
parser.add_argument('--case', action='append', choices=sorted(p.parent.name for p in (ROOT / 'tests/shared').glob('*/main.dl')))
parser.add_argument('--browser', action='store_true', help='Also run the Find/Replace interaction fixture in private Xvfb displays')
args = parser.parse_args()
core, ui = args.dynlex.resolve(), args.ui.resolve()
subprocess.run([sys.executable, ROOT / 'scripts/generate_source_colors.py', '--dynlex', core, '--check'], check=True)
(ROOT / 'build').mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(dir=ROOT / 'build') as temporary:
    project = Path(temporary)
    ide = project / 'packages/dynlex-ide'
    for name in ['editor', 'studio', 'tests']:
        shutil.copytree(ROOT / name, ide / name)
    for name in ['ui', 'testing', 'platform']:
        shutil.copytree(ui / name, project / 'packages/dynlex-ui' / name)
    for fixture in sorted((ide / 'tests/shared').glob('*/main.dl')):
        name = fixture.parent.name
        if args.case and name not in args.case:
            continue
        for optimization in ['-O0', '-O2']:
            binary = project / 'fixture.out'
            subprocess.run([core / 'build/dynlex', fixture, optimization, '-o', binary], check=True)
            output = subprocess.check_output([binary], text=True)
            if output != fixture.with_name('expected.txt').read_text():
                raise AssertionError(f'{name} {optimization}: unexpected output {output!r}')
        subprocess.run(['node', ui / 'tests/browser/shared_frontends.mjs', core, name, project, 'packages/dynlex-ide'], check=True)
    subprocess.run(['node', ide / 'tests/browser/source_connection.mjs', core], cwd=ide, check=True)
    if args.browser:
        output = project / 'search'
        subprocess.run([sys.executable, ui / 'scripts/build.py', '--dynlex', core, '--entry', ide / 'tests/browser/search.dl', '--output', output], check=True)
        environment = dict(os.environ, DYNLEX_BACKGROUND_BROWSER='1', XDG_SESSION_TYPE='x11')
        for key in ['WAYLAND_DISPLAY', 'WAYLAND_SOCKET', 'VK_DRIVER_FILES', 'VK_ICD_FILENAMES']:
            environment.pop(key, None)
        for mode in ['webgpu', 'webgl-no-adapter', 'webgl-no-api']:
            subprocess.run(['xvfb-run', '-a', '-s', '-screen 0 1400x1000x24', 'node',
                            ui / 'tests/browser/run.mjs', output, mode, core, ide / 'tests/browser/search.mjs'],
                           cwd=ui, env=environment, check=True)
