#!/usr/bin/env python3
"""Create reproducible v0.2.2 full-source and portable-install ZIP release assets.

Requires only Python standard library and works offline. No runtime chat data is read.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CORE = (
    '.gitignore', 'BUILD-MANIFEST.json', 'CHANGELOG.md',
    'Install.cmd', 'Install.ps1', 'Install.sh', 'LICENSE', 'README.md',
    'SECURITY.md', 'Uninstall.cmd', 'Uninstall.ps1', 'Uninstall.sh', 'plugin.js'
)
SOURCE_DIRS = ('.github', 'desktop', 'docs', 'scripts', 'src', 'tests', 'upstream')
ZIP_TIME = (2026, 11, 14, 0, 0, 0)


def files_for(full):
    files = [ROOT / item for item in CORE]
    if full:
        for name in SOURCE_DIRS:
            files.extend(path for path in (ROOT / name).rglob('*')
                         if path.is_file() and not any(part in {'__pycache__', '.pytest_cache', '.git'} for part in path.parts)
                         and path.suffix != '.pyc')
    for item in files:
        if not item.is_file():
            raise RuntimeError(f'Release file missing: {item}')
    return sorted(files, key=lambda p: p.relative_to(ROOT).as_posix())


def add_zip_item(zf, arcname, data):
    item = zipfile.ZipInfo(arcname, ZIP_TIME)
    item.create_system = 3
    item.external_attr = 0o644 << 16
    item.compress_type = zipfile.ZIP_DEFLATED
    zf.writestr(item, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def package(output):
    manifest = json.loads((ROOT / 'BUILD-MANIFEST.json').read_text('utf-8'))
    version = manifest['version']
    sha = hashlib.sha256((ROOT / 'plugin.js').read_bytes()).hexdigest()
    if sha != manifest['compiled_sha256']:
        raise RuntimeError('Compiled plugin does not match build manifest')
    if (ROOT / 'plugin.js').read_bytes() != (ROOT / 'desktop/plugin.js').read_bytes():
        raise RuntimeError('Root and desktop plugin.js differ')
    if f"const PLUGIN_VERSION = '{version}-vault'" not in (ROOT / 'plugin.js').read_text('utf-8'):
        raise RuntimeError('Plugin version does not match manifest')
    output.mkdir(parents=True, exist_ok=True)
    artifacts = []
    for label, full in [('FULL_SOURCE', True), ('PORTABLE_INSTALL', False)]:
        dest = output / f'Hermes_ChatVault_v{version}_{label}.zip'
        with zipfile.ZipFile(dest, 'w') as zf:
            for path in files_for(full):
                name = f'Hermes-ChatVault-v{version}/{path.relative_to(ROOT).as_posix()}'
                add_zip_item(zf, name, path.read_bytes())
        with zipfile.ZipFile(dest) as zf:
            if zf.testzip() is not None:
                raise RuntimeError(f'Invalid ZIP: {dest}')
        artifacts.append(dest)
    checksums = output / f'Hermes_ChatVault_v{version}_SHA256SUMS.txt'
    checksums.write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in artifacts), encoding='utf-8')
    return artifacts + [checksums]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist')
    args = parser.parse_args()
    for item in package(args.output.resolve()):
        print(f'RELEASE ASSET: {item} ({item.stat().st_size} bytes)')
