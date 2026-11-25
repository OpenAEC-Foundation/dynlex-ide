#!/usr/bin/env python3
"""Export the reusable editor and Studio as a content-addressed source package."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def export(output):
    metadata = json.loads((ROOT / 'dynlex-package.json').read_text())
    paths = [ROOT / 'LICENSE.md', ROOT / 'dynlex-package.json', *sorted((ROOT / 'editor').glob('*.dl')),
             *sorted((ROOT / 'studio').glob('*.dl'))]
    files = {path.relative_to(ROOT).as_posix(): path.read_bytes() for path in paths}
    digests = {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}
    manifest = {
        'schema': 1, 'package': 'dynlex-ide', 'files': digests,
        **{key: metadata[key] for key in ['exports', 'dependencies', 'description', 'documentation', 'title', 'publisher', 'importName']},
        'sourceRevision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'contentHash': hashlib.sha256(json.dumps(digests, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
    }
    files['sdk.json'] = (json.dumps(manifest, sort_keys=True, indent=2) + '\n').encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as temporary:
        staged = Path(temporary) / 'sdk.zip'
        with zipfile.ZipFile(staged, 'w') as archive:
            for name, data in sorted(files.items()):
                entry = zipfile.ZipInfo(name)
                entry.create_system = 3
                entry.external_attr = 0o100644 << 16
                archive.writestr(entry, data, compress_type=zipfile.ZIP_DEFLATED)
        staged.replace(output)
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    print(export(parser.parse_args().output)['contentHash'])
