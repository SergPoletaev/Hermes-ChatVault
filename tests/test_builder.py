import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('vault_build', ROOT / 'scripts/build.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# Structural fixture follows the source anchors of Chat Share 1.1.8 + image fix v1.
# It checks that the complete transform is syntactically valid; it is not the
# user's installed plugin and does not claim full in-app integration testing.
FIXTURE = r'''// ESM stub
import { TITLEBAR_AREAS, ROUTES_AREA, SIDEBAR_NAV_AREA, PALETTE_AREA, KEYBINDS_AREA, host, atom } from '@hermes/plugin-sdk'
const PLUGIN_ID = 'hermes-chat-share'
const PLUGIN_VERSION = '1.1.8'
const ROUTE = '/chat-share'
// END HERMES_CHAT_SHARE_EMBED_MEDIA_V1
async function chshPrepareExportTurns(turns) { return turns }
const chshEmbeddedMedia = new Map()
const turnsAtom = atom([])
const stateAtom = atom({title: '', error:''})
const metaAtom = atom(null)
const optAtom = atom({ width: 880, scale: 1, tools: true, full: true, theme: 'auto', meta: true })
const PrefsKey = 'hermes-chat-share:prefs'
function loadPrefs () {
 const raw = localStorage.getItem(PrefsKey)
 const p = JSON.parse(raw)
 for (const k of ['width', 'scale', 'tools', 'full', 'theme', 'meta']) { if(p[k] !== undefined) {} }
}
function savePrefs () {
 const { width, scale, tools, full, theme, meta } = optAtom.get()
 localStorage.setItem(PrefsKey, JSON.stringify({ width, scale, tools, full, theme, meta }))
}
function buildMetaLine(meta) { return String(meta) }
function t() { return 'title' }
function selectedIds() { return [] }
function exportJson (turns, meta, title, opt) {
 return JSON.stringify({ title, meta: opt.meta === false ? null : (buildMetaLine(meta) || null), turns })
}
async function renderImages () {
 const ids = new Set(selectedIds())
 const rawTurns = turnsAtom.get().filter(x => ids.has(x.id))
 const turns = await chshPrepareExportTurns(rawTurns)
 const th={}; const opt = optAtom.get()
 const ml = opt.meta === false ? '' : buildMetaLine(metaAtom.get())
 const pages = buildPages(turns, th, opt)
 const out=[]
 for (let k=0;k<pages.length;k++) out.push(await pageToPng(pages[k], th, { ...opt, title: k === 0 ? stateAtom.get().title : '', metaLine: ml }))
 return out
}
function fileBase () {
 const st=stateAtom.get()
 const turns=turnsAtom.get()
 const firstUser=turns.find(x=>x.user&&x.user.text)
 return slugTitle(st.title || (firstUser && firstUser.text) || 'date')
}
function slugTitle(s) { return s }
function download() {}
async function doCopyPng () {
 const imgs=await renderImages()
}
function AskModal () { return null }
async function doDownloadPng () {
 const imgs=await renderImages()
}
async function exportHtml (opts) {
 const ids=new Set(selectedIds())
 const turns = await chshPrepareExportTurns(turnsAtom.get().filter(x => ids.has(x.id)))
 const th={}
 const opt = { ...optAtom.get(), images: true }
 const ml = opt.meta === false ? '' : buildMetaLine(metaAtom.get())
 const body='<div>' + esc(stateAtom.get().title || t('shareTitle')) + turns.map(x => turnXhtml(x, { images: true, tools: opt.tools, full: opt.full }, th)).join('') + '</div>'
 const html='<title>'+esc(stateAtom.get().title || 'Hermes') + exportCss(th, { ...opt, images: true })+'</title>'+body
 chshEmbeddedMedia.clear()
 return new Blob([html],{type:'text/html'})
}
function exportMd () {
 const ids=new Set(selectedIds())
 const turns = turnsAtom.get().filter(x => ids.has(x.id))
 const opt=optAtom.get()
 let s='# '+(stateAtom.get().title || t('shareTitle'))
 const ml = opt.meta === false ? '' : buildMetaLine(metaAtom.get())
 return new Blob([s + ml + turns.length])
}
async function doDownloadHtml () {}
async function doDownloadPdf () { const imgs = await renderImages() }
function doDownloadMd () {}
function doDownloadJson () {
 const ids = new Set(selectedIds())
 const turns = turnsAtom.get().filter(x => ids.has(x.id))
 const opt=optAtom.get()
 const s=exportJson(turns, metaAtom.get(), stateAtom.get().title, opt)
 download(s, 'out.json')
}
function fail (err) {}
function esc(s) {return String(s)}
function Toolbar() {
 const opt=optAtom.get(); const setOpt=(o)=>{}
 return [
      // Row 3: export actions pulled left to sit with the rest — one
      jsx(Button, { size: 'sm', onClick: () => void doDownloadHtml(), children: 'HTML' }),
 ]
}
export default {
 id: PLUGIN_ID,
 name: 'Chat Share',
 description: 'Share conversations as long PNG screenshots, HTML, or Markdown — with per-turn selection.',
 register(ctx) {
  ctx.i18n.register(STRINGS)
  const contribute = () => ctx.registerMany([
       { id: 'page', area: ROUTES_AREA, data: { path: ROUTE } },
       { id: 'open-kb', area: KEYBINDS_AREA,
         data: { defaults: ['mod+shift+h'] } }
  ])
 }
}
'''

class TestBuilder(unittest.TestCase):
    def test_generated_js_parses(self):
        addon = (ROOT / 'src/vault-extra.js').read_text(encoding='utf-8')
        import importlib.util
        spec2 = importlib.util.spec_from_file_location('test_upgrade_v02', ROOT / 'scripts/upgrade_v02.py')
        up = importlib.util.module_from_spec(spec2)
        spec2.loader.exec_module(up)
        upstream = (ROOT / 'upstream/working-chat-share-1.1.8.js').read_text('utf-8')
        transformed = up.upgrade(mod.transform(upstream, addon))
        for marker in ('HERMES_CHATVAULT_FORK_V1', 'vaultDownloadZip', 'vaultRedactText', 'COMPOSER_AREAS.contextMenu', 'vaultResolvedString', 'function VaultBanner', 'languageShort'):
            self.assertIn(marker, transformed)
        self.assertIn("const PLUGIN_ID = 'hermes-chat-vault'", transformed)
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'plugin.mjs'
            path.write_text(transformed,encoding='utf-8')
            completed = subprocess.run(['node', '--check', str(path)], capture_output=True, text=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_refuses_unknown_or_unpatched(self):
        addon = (ROOT / 'src/vault-extra.js').read_text(encoding='utf-8')
        with self.assertRaises(RuntimeError):
            mod.transform(FIXTURE.replace('1.1.8', '1.1.9'), addon)
        with self.assertRaises(RuntimeError):
            mod.transform(FIXTURE.replace('HERMES_CHAT_SHARE_EMBED_MEDIA_V1', 'SOMETHING_ELSE'), addon)

    def test_build_complete_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp)
            source=tmp/'working.js'
            source.write_text((ROOT / 'upstream/working-chat-share-1.1.8.js').read_text('utf-8'),encoding='utf-8')
            project=mod.build(source, tmp/'out')
            for path in ('plugin.js','desktop/plugin.js','upstream/working-chat-share-1.1.8.js','src/vault-extra.js','README.md','LICENSE','BUILD-MANIFEST.json'):
                self.assertTrue((project/path).exists(),path)
            self.assertNotEqual((project/'desktop/plugin.js').read_text(), source.read_text())
            self.assertEqual(source.read_text(),(ROOT / 'upstream/working-chat-share-1.1.8.js').read_text('utf-8'))
            self.assertEqual((project/'desktop/plugin.js').read_text('utf-8'), (ROOT/'desktop/plugin.js').read_text('utf-8'))
            self.assertEqual((project/'plugin.js').read_text('utf-8'), (ROOT/'plugin.js').read_text('utf-8'))
            self.assertFalse((project/'plugin.yaml').exists())
            self.assertEqual((project/'.github/workflows/ci.yml').read_bytes(), (ROOT/'.github/workflows/ci.yml').read_bytes())
            self.assertEqual((project/'.gitignore').read_bytes(), (ROOT/'.gitignore').read_bytes())
            self.assertEqual((project/'tests/test_public_package.py').read_bytes(), (ROOT/'tests/test_public_package.py').read_bytes())

if __name__ == '__main__':
    unittest.main()
