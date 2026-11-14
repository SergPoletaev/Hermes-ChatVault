#!/usr/bin/env python3
"""Build a standalone Hermes ChatVault fork from a known-good patched Chat Share source.

Requires upstream smallmj/hermes-chat-share v1.1.8 with the verified
HERMES_CHAT_SHARE_EMBED_MEDIA_V1 local patch. Never modifies the input.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys

VERSION = '0.2.2'
ROOT = Path(__file__).resolve().parent.parent


def replace_once(src: str, old: str, new: str, name: str) -> str:
    n = src.count(old)
    if n != 1:
        raise RuntimeError(f'{name}: expected exactly 1 anchor, got {n}')
    return src.replace(old, new, 1)


def in_function(src, start, end, callback, label):
    a = src.find(start)
    b = src.find(end, a + len(start))
    if a < 0 or b < 0 or src.find(start, a + 1) >= 0 or b <= a:
        raise RuntimeError(f'{label}: function boundaries not unique')
    return src[:a] + callback(src[a:b]) + src[b:]


def transform(original: str, addon: str) -> str:
    src = original.replace('\r\n', '\n')
    if "const PLUGIN_VERSION = '1.1.8'" not in src:
        raise RuntimeError('Expected Chat Share upstream v1.1.8: check source file')
    if 'HERMES_CHAT_SHARE_EMBED_MEDIA_V1' not in src or 'async function chshPrepareExportTurns' not in src:
        raise RuntimeError('The embedded-media v1 patch is missing; refusing to replace working plugin')
    if 'HERMES_CHATVAULT_FORK_V1' in src:
        raise RuntimeError('Input is already a ChatVault fork')

    src = replace_once(src, "const PLUGIN_VERSION = '1.1.8'", "const PLUGIN_VERSION = '0.1.0-vault'", 'plugin version')
    src = replace_once(src, 'TITLEBAR_AREAS,', 'TITLEBAR_AREAS, COMPOSER_AREAS,', 'SDK area import')
    # Changes every internal use including localStorage namespace and contribution ids,
    # leaving the upstream installation fully independent.
    src = src.replace('hermes-chat-share', 'hermes-chat-vault')
    src = src.replace('chat-share.', 'chat-vault.')
    src = replace_once(src, "const ROUTE = '/chat-share'", "const ROUTE = '/chat-vault'", 'route')
    src = src.replace("defaults: ['mod+shift+h']", "defaults: ['mod+shift+v']")
    src = replace_once(src, '// END HERMES_CHAT_SHARE_EMBED_MEDIA_V1',
        '// END HERMES_CHAT_SHARE_EMBED_MEDIA_V1\n' + addon.strip() + '\n// HERMES_CHATVAULT_FORK_V1', 'feature insertion')

    # Prefix state storage and persisted settings. Do not alter source history.
    src = replace_once(src, "meta: true })", "meta: true, ...vaultDefaults })", 'default options')
    src = replace_once(src, "'width', 'scale', 'tools', 'full', 'theme', 'meta'", "'width', 'scale', 'tools', 'full', 'theme', 'meta', 'vaultImagesPdf', 'vaultImagesHtml', 'vaultImagesPng', 'vaultRedact'", 'read settings')
    src = replace_once(src, 'const { width, scale, tools, full, theme, meta } = optAtom.get()',
        'const { width, scale, tools, full, theme, meta, vaultImagesPdf, vaultImagesHtml, vaultImagesPng, vaultRedact } = optAtom.get()', 'write settings destructure')
    src = replace_once(src, 'JSON.stringify({ width, scale, tools, full, theme, meta })',
        'JSON.stringify({ width, scale, tools, full, theme, meta, vaultImagesPdf, vaultImagesHtml, vaultImagesPng, vaultRedact })', 'write settings payload')

    # Export JSON must redact meta when opted in; title and turns redacted at call sites.
    src = replace_once(src, 'meta: opt.meta === false ? null : (buildMetaLine(meta) || null)',
        'meta: opt.meta === false ? null : (vaultRedactText(buildMetaLine(meta)) || null)', 'JSON metadata')

    def render_patch(region):
        region = replace_once(region, 'async function renderImages () {', 'async function renderImages (vaultFormat = \'pdf\') {', 'render signature')
        region = replace_once(region, 'const turns = await chshPrepareExportTurns(rawTurns)',
            'const turns = await vaultPrepareExportTurns(rawTurns, vaultFormat)', 'image hydration')
        region = replace_once(region, 'const ml = opt.meta === false ? \'\' : buildMetaLine(metaAtom.get())',
            'const ml = opt.meta === false ? \'\' : vaultMetaLine()', 'raster meta')
        region = replace_once(region, 'title: k === 0 ? stateAtom.get().title : \'\'',
            'title: k === 0 ? vaultSafeTitle() : \'\'', 'raster title')
        return region
    src = in_function(src, 'async function renderImages () {', 'function fileBase () {', render_patch, 'raster')
    # Keep filenames safe under opt-in redaction.
    src = replace_once(src, "st.title || (firstUser && firstUser.text)",
        "vaultRedactText(st.title || (firstUser && firstUser.text))", 'file name')
    # Separate PNG and PDF preference from the shared raster pipeline.
    for start, end, label in (
        ('async function doCopyPng () {', 'function AskModal () {', 'copy PNG'),
        ('async function doDownloadPng () {', 'async function exportHtml (opts) {', 'save PNG')):
        src = in_function(src, start, end,
            lambda r: replace_once(r, 'await renderImages()', "await renderImages('png')", label), label)

    def html_patch(region):
        region = replace_once(region,
            'await chshPrepareExportTurns(turnsAtom.get().filter(x => ids.has(x.id)))',
            "await vaultPrepareExportTurns(turnsAtom.get().filter(x => ids.has(x.id)), 'html')", 'HTML turns')
        region = replace_once(region, 'const opt = { ...optAtom.get(), images: true }', "const opt = { ...optAtom.get(), images: vaultWantsImages('html') }", 'HTML option')
        region = replace_once(region, "const ml = opt.meta === false ? '' : buildMetaLine(metaAtom.get())",
            "const ml = opt.meta === false ? '' : vaultMetaLine()", 'HTML meta')
        region = replace_once(region, "esc(stateAtom.get().title || t('shareTitle'))", 'esc(vaultSafeTitle())', 'HTML header')
        region = replace_once(region, 'turnXhtml(x, { images: true, tools:', "turnXhtml(x, { images: vaultWantsImages('html'), tools:", 'HTML rendering')
        region = replace_once(region, "esc(stateAtom.get().title || 'Hermes')", 'esc(vaultSafeTitle())', 'HTML document title')
        region = replace_once(region, 'exportCss(th, { ...opt, images: true })',
            "exportCss(th, { ...opt, images: vaultWantsImages('html') })", 'HTML CSS')
        return region
    src = in_function(src, 'async function exportHtml (opts) {', 'function exportMd () {', html_patch, 'HTML')

    def md_patch(region):
        region = replace_once(region, 'const turns = turnsAtom.get().filter(x => ids.has(x.id))',
            'const turns = vaultChosenTurns()', 'Markdown turns')
        region = replace_once(region, "stateAtom.get().title || t('shareTitle')", 'vaultSafeTitle()', 'Markdown title')
        region = replace_once(region, "const ml = opt.meta === false ? '' : buildMetaLine(metaAtom.get())",
            "const ml = opt.meta === false ? '' : vaultMetaLine()", 'Markdown meta')
        return region
    src = in_function(src, 'function exportMd () {', 'async function doDownloadHtml () {', md_patch, 'Markdown')

    def json_patch(region):
        region = replace_once(region, 'const turns = turnsAtom.get().filter(x => ids.has(x.id))',
            'const turns = vaultChosenTurns()', 'JSON turns')
        region = replace_once(region, 'stateAtom.get().title, opt', 'vaultSafeTitle(), opt', 'JSON title')
        return region
    src = in_function(src, 'function doDownloadJson () {', 'function fail (err) {', json_patch, 'JSON')

    # UI preferences live beside the original appearance/sharing controls and are
    # persisted by the original savePrefs() logic above.
    toggles = '''
      // ChatVault: per-format embedded-image choices and a global redaction switch.
      jsxs('div', { className: 'flex items-center gap-3 flex-wrap', children: [
        ...[
          ['vaultImagesPdf', 'PDF images'],
          ['vaultImagesHtml', 'HTML images'],
          ['vaultImagesPng', 'PNG images'],
          ['vaultRedact', 'Hide sensitive text (all exports)']
        ].map(([key, label]) => jsx('label', {
          className: 'flex items-center gap-1.5 text-xs text-(--foreground) cursor-pointer',
          children: [
            jsx('input', {
              type: 'checkbox', checked: opt[key] !== false && (key !== 'vaultRedact' || !!opt[key]),
              onChange: () => setOpt({ [key]: !opt[key] }),
              className: 'size-3.5 accent-(--accent)'
            }), label
          ]
        }, key))
      ] }),
'''
    anchor = '      // Row 3: export actions pulled left to sit with the rest'
    src = replace_once(src, anchor, toggles + '      // Row 3: export actions pulled left to sit with the rest', 'toolbar toggles')
    src = replace_once(src,
      "jsx(Button, { size: 'sm', onClick: () => void doDownloadHtml(), children: 'HTML' }),",
      "jsx(Button, { size: 'sm', onClick: () => void doDownloadHtml(), children: 'HTML' }),\n" +
      "        jsx(Button, { size: 'sm', onClick: () => void vaultDownloadZip(), children: 'ZIP' }),\n" +
      "        jsx(Button, { size: 'sm', onClick: () => void vaultExportTxt(), children: 'TXT' }),", 
      'ZIP button')

    # Quick export in the real SDK-owned composer context menu. The host removes
    # the rows automatically on plugin disable, unload or uninstall.
    menu = '''
       {
         id: 'vault-composer-export', area: COMPOSER_AREAS.contextMenu,
         data: { items: () => [
           { label: 'Export chat to PDF', onSelect: () => void vaultQuickExport('pdf') },
           { label: 'Export chat to HTML', onSelect: () => void vaultQuickExport('html') },
           { label: 'Export chat to Markdown', onSelect: () => void vaultQuickExport('md') },
           { label: 'Export chat to JSON', onSelect: () => void vaultQuickExport('json') },
           { label: 'Archive chat as ZIP', onSelect: () => void vaultQuickExport('zip') },
           { label: 'Export chat to TXT', onSelect: () => void vaultQuickExport('txt') }
         ] }
       },
'''
    src = replace_once(src, "{ id: 'page', area: ROUTES_AREA", menu + "{ id: 'page', area: ROUTES_AREA", 'composer context menu')
    # The public settings-page SDK owns registration/disposal and removes the page
    # as soon as the plugin is disabled. Settings and toolbar share one store.
    src = replace_once(src, 'ctx.i18n.register(STRINGS)',
        "ctx.i18n.register(STRINGS)\n    ctx.registerSettingsPage?.({ id: 'settings', title: 'ChatVault', icon: 'archive', render: () => jsx(VaultSettingsPage, {}) })",
        'Settings plugin page')
    src = replace_once(src, "name: 'Chat Share'", "name: 'ChatVault'", 'display name')
    src = replace_once(src, "description: 'Share conversations as long PNG screenshots, HTML, or Markdown — with per-turn selection.'",
        "description: 'Archive Hermes chats as PDF, embedded-image HTML, ZIP, JSON, Markdown and PNG with privacy options.'", 'description')
    return src


def build(installed: Path, output: Path) -> Path:
    original = installed.read_text('utf-8-sig')
    addon = (ROOT / 'src/vault-extra.js').read_text('utf-8')
    import importlib.util
    upgrade_path = ROOT / 'scripts/upgrade_v02.py'
    spec = importlib.util.spec_from_file_location('chatvault_upgrade_v02', upgrade_path)
    upgrade_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(upgrade_module)
    result = upgrade_module.upgrade(transform(original, addon))
    destination = output / 'Hermes-ChatVault'
    if destination.exists():
        raise RuntimeError(f'Output already exists: {destination}. Choose a new folder.')
    (destination / 'desktop').mkdir(parents=True)
    (destination / 'upstream').mkdir()
    (destination / 'src').mkdir()
    (destination / 'scripts').mkdir()
    (destination / 'tests').mkdir()
    (destination / 'docs').mkdir()
    result = result.replace('Keep in sync with plugin.yaml.', 'Keep in sync with the public release version.')
    (destination / 'desktop/plugin.js').write_text(result, encoding='utf-8')
    (destination / 'plugin.js').write_text(result, encoding='utf-8')
    (destination / 'upstream/working-chat-share-1.1.8.js').write_text(original, encoding='utf-8')
    for filename in ('README.md', 'LICENSE', 'SECURITY.md', '.gitignore', 'CHANGELOG.md', 'Install.ps1', 'Uninstall.ps1', 'Install.cmd', 'Uninstall.cmd', 'Install.sh', 'Uninstall.sh'):
        if filename == '.gitignore' and not (ROOT / filename).exists():
            (destination / filename).write_text('# Generated fallback: ignore local secrets and build outputs\n.env\n*.key\n*.log\n*.zip\n__pycache__/\n', encoding='utf-8')
        else:
            shutil.copy2(ROOT / filename, destination / filename)
    for dirname in ('src', 'scripts', 'tests', 'docs'):
        for path in (ROOT / dirname).iterdir():
            if path.is_file():
                shutil.copy2(path, destination / dirname / path.name)
    manifest = {
        'project': 'Hermes ChatVault', 'version': VERSION,
        'type':'desktop-only',
        'upstream': 'smallmj/hermes-chat-share v1.1.8 MIT + generic embedded-media fix',
        'compiled_sha256': hashlib.sha256((destination / 'plugin.js').read_bytes()).hexdigest(),
        'source_rebuild':'python scripts/build.py upstream/working-chat-share-1.1.8.js <output_directory>',
        'release_policy':'No real user files, credentials, session content, personal paths or local machine identifiers'
    }
    (destination / 'BUILD-MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return destination


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('installed_plugin_js', type=Path)
    parser.add_argument('output_directory', type=Path)
    args = parser.parse_args()
    try:
        result = build(args.installed_plugin_js, args.output_directory)
        print('BUILD SUCCESS:', result)
        print('Source ready:', result / 'desktop/plugin.js')
        print('MIT attribution and unified four-language README included.')
    except Exception as exc:
        print('BUILD FAILED:', exc, file=sys.stderr)
        sys.exit(1)
