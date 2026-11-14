// Hermes ChatVault v0.1.0 - fork feature layer.
// This code is injected into the separately installed copy of Hermes Chat Share.
// Upstream: smallmj/hermes-chat-share v1.1.8 (MIT); requires the working embedded-media v1 fix.
// It does not modify chat history and performs no network calls.
const vaultDefaults = Object.freeze({
  vaultImagesPdf: true,
  vaultImagesHtml: true,
  vaultImagesPng: true,
  vaultRedact: false
})
const vaultMaxZipBytes = 300 * 1024 * 1024

function vaultRedactText(value) {
  let s = String(value == null ? '' : value)
  if (!optAtom.get().vaultRedact) return s
  // Heuristics are intentionally conservative. Not a DLP guarantee.
  s = s.replace(/\bBearer\s+[^\s<>"']+/gi, 'Bearer [REDACTED]')
  s = s.replace(/\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{12,}\b/g, '[API_KEY_REDACTED]')
  s = s.replace(/\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{16,}\b/g, '[TOKEN_REDACTED]')
  s = s.replace(/\b(?:AKIA|ASIA)[A-Z0-9]{16}\b/g, '[AWS_KEY_REDACTED]')
  s = s.replace(/\beyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b/g, '[JWT_REDACTED]')
  s = s.replace(/\b((?:api[_-]?key|key|token|secret|password|passwd|authorization|credential)\s*[:=]\s*)(["']?)([^\s\r\n,"'}]{5,})(["']?)/gi,
    (_m, prefix) => prefix + '[REDACTED]')
  s = s.replace(/\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/gi, '[EMAIL_REDACTED]')
  s = s.replace(/\b(?:\d{1,3}\.){3}\d{1,3}\b/g, '[IP_REDACTED]')
  s = s.replace(/(?:[A-Z]:\\|\\\\)[^\s<>"'|?*\r\n]+/gi, '[LOCAL_PATH_REDACTED]')
  s = s.replace(/\/(?:Users|home)\/[^\s<>"'\r\n]+/g, '[LOCAL_PATH_REDACTED]')
  return s
}
function vaultSafeTitle() { return vaultRedactText(stateAtom.get().title || t('shareTitle')) }
function vaultMetaLine() { return vaultRedactText(buildMetaLine(metaAtom.get())) }
function vaultCloneTurns(turns, cleanMedia) {
  return turns.map(turn => ({
    ...turn,
    user: turn.user ? { ...turn.user, text: vaultRedactText(cleanMedia ? vaultStripMedia(turn.user.text) : turn.user.text) } : null,
    asst: (turn.asst || []).map(a => ({ ...a, text: vaultRedactText(cleanMedia ? vaultStripMedia(a.text) : a.text) })),
    tools: (turn.tools || []).map(x => ({ ...x, name: vaultRedactText(x.name), ctx: vaultRedactText(x.ctx) }))
  }))
}
function vaultStripMedia(input) {
  return String(input == null ? '' : input)
    .replace(/^[ \t]*@image:[ \t]*[^\r\n]+/gmi, '[Image omitted]')
    .replace(/\[Image attached at:[ \t]*[^\]\r\n]+\]/gi, '[Image omitted]')
    .replace(/^[ \t]*MEDIA:[ \t]*[^\r\n]+/gmi, '[Image/attachment omitted]')
    .replace(/!\[([^\]]*)\]\([^\r\n)]*\)/g, '[Image omitted: $1]')
}
function vaultWantsImages(format) {
  const opt = optAtom.get()
  return format === 'html' ? opt.vaultImagesHtml !== false
    : format === 'png' ? opt.vaultImagesPng !== false
      : format === 'pdf' ? opt.vaultImagesPdf !== false : false
}
async function vaultPrepareExportTurns(turns, format) {
  if (!vaultWantsImages(format)) {
    chshEmbeddedMedia.clear()
    return vaultCloneTurns(turns, true)
  }
  // Resolve file references before text redaction: hiding paths first would break imaging.
  const embedded = await chshPrepareExportTurns(turns)
  return vaultCloneTurns(embedded, false)
}
function vaultChosenTurns() {
  const ids = new Set(selectedIds())
  return vaultCloneTurns(turnsAtom.get().filter(x => ids.has(x.id)), false)
}

// ZIP32, STORE compression, UTF-8 names, CRC32. No third-party scripts or servers.
let vaultCrcTable = null
function vaultCrc32(bytes) {
  if (!vaultCrcTable) {
    vaultCrcTable = new Uint32Array(256)
    for (let i = 0; i < 256; i++) {
      let c = i
      for (let b = 0; b < 8; b++) c = c & 1 ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1)
      vaultCrcTable[i] = c >>> 0
    }
  }
  let c = 0xFFFFFFFF
  for (const byte of bytes) c = vaultCrcTable[(c ^ byte) & 255] ^ (c >>> 8)
  return (c ^ 0xFFFFFFFF) >>> 0
}
function vaultZip(files) {
  if (!Array.isArray(files) || files.length === 0 || files.length >= 65535) throw new Error('Invalid ZIP entry count')
  const encoder = new TextEncoder()
  const payload = [], central = []
  const seen = new Set()
  let offset = 0
  let total = 0
  const u16 = (v, a, i) => { a[i] = v & 255; a[i + 1] = (v >>> 8) & 255 }
  const u32 = (v, a, i) => { u16(v, a, i); u16(v >>> 16, a, i + 2) }
  for (const entry of files) {
    const name = String(entry.name || '')
    if (!name || name.startsWith('/') || name.includes('\\') || name.split('/').includes('..') || /[\x00-\x1f]/.test(name) || seen.has(name)) {
      throw new Error('Unsafe or duplicate archive name')
    }
    seen.add(name)
    const filename = encoder.encode(name)
    const content = entry.bytes instanceof Uint8Array ? entry.bytes : encoder.encode(String(entry.text || ''))
    if (filename.length > 65535 || content.length > 0xFFFFFFFF) throw new Error('ZIP32 entry too large')
    total += content.length
    if (total > vaultMaxZipBytes) throw new Error('Archive is too large for in-memory ZIP export (300 MB limit)')
    const crc = vaultCrc32(content)
    const local = new Uint8Array(30 + filename.length)
    u32(0x04034b50, local, 0); u16(20, local, 4); u16(0x0800, local, 6)
    u16(0, local, 8); u16(0, local, 10); u16(0, local, 12)
    u32(crc, local, 14); u32(content.length, local, 18); u32(content.length, local, 22)
    u16(filename.length, local, 26); u16(0, local, 28); local.set(filename, 30)
    payload.push(local, content)
    const c = new Uint8Array(46 + filename.length)
    u32(0x02014b50, c, 0); u16(20, c, 4); u16(20, c, 6); u16(0x0800, c, 8)
    u16(0, c, 10); u16(0, c, 12); u16(0, c, 14)
    u32(crc, c, 16); u32(content.length, c, 20); u32(content.length, c, 24)
    u16(filename.length, c, 28); u16(0, c, 30); u16(0, c, 32)
    u16(0, c, 34); u16(0, c, 36); u32(0, c, 38); u32(offset, c, 42)
    c.set(filename, 46)
    central.push(c)
    offset += local.length + content.length
    if (offset > 0xFFFFFFFF) throw new Error('ZIP32 archive too large')
  }
  const centralBytes = central.reduce((s, b) => s + b.length, 0)
  const e = new Uint8Array(22)
  u32(0x06054b50, e, 0); u16(0, e, 4); u16(0, e, 6)
  u16(files.length, e, 8); u16(files.length, e, 10)
  u32(centralBytes, e, 12); u32(offset, e, 16); u16(0, e, 20)
  return new Blob([...payload, ...central, e], { type: 'application/zip' })
}

function vaultExportTxt() {
  try {
    const opt = optAtom.get()
    const turns = vaultChosenTurns()
    const lines = [vaultSafeTitle(), opt.meta === false ? '' : vaultMetaLine(), '']
    for (const turn of turns) {
      if (turn.user) lines.push('[User' + (turn.user.ts ? ' · ' + fmtTs(turn.user.ts) : '') + ']', turn.user.text, '')
      const assts = opt.full === false ? turn.asst.slice(-1) : turn.asst
      for (const a of assts) lines.push('[Assistant' + (a.ts ? ' · ' + fmtTs(a.ts) : '') + ']', a.text, '')
      if (opt.tools && opt.full !== false) for (const x of turn.tools) lines.push('[Tool: ' + x.name + ']', x.ctx || '', '')
      lines.push('---', '')
    }
    download(new Blob([lines.join('\n')], { type: 'text/plain;charset=utf-8' }), fileBase() + '.txt')
    host.notify({ kind: 'success', message: 'TXT saved' })
  } catch (err) { fail(err) }
}

async function vaultDownloadZip() {
  try {
    const html = await exportHtml()
    const md = exportMd()
    const optTxt = optAtom.get()
    const txtParts = [vaultSafeTitle(), optTxt.meta === false ? '' : vaultMetaLine(), '']
    for (const turn of vaultChosenTurns()) {
      if (turn.user) txtParts.push('User:', turn.user.text, '')
      for (const a of (optTxt.full === false ? turn.asst.slice(-1) : turn.asst)) txtParts.push('Assistant:', a.text, '')
      if (optTxt.tools && optTxt.full !== false) for (const tool of turn.tools) txtParts.push('Tool: '+tool.name, tool.ctx || '', '')
      txtParts.push('---','')
    }
    const ids = new Set(selectedIds())
    const turns = vaultChosenTurns()
    const opt = optAtom.get()
    const json = exportJson(turns, metaAtom.get(), vaultSafeTitle(), opt)
    const htmlBytes = new Uint8Array(await html.arrayBuffer())
    const mdBytes = new Uint8Array(await md.arrayBuffer())
    const files = [
      { name: 'conversation.html', bytes: htmlBytes },
      { name: 'conversation.md', bytes: mdBytes },
      { name: 'conversation.txt', text: txtParts.join('\n') },
      { name: 'conversation.json', text: json },
      { name: 'manifest.json', text: JSON.stringify({ schema: 'hermes.chatvault.archive.v1', title: vaultSafeTitle(), exportedAt: new Date().toISOString(), turns: turns.length, redacted: !!opt.vaultRedact, imagesHtml: vaultWantsImages('html') }, null, 2) },
      { name: 'README.txt', text: 'Hermes ChatVault ZIP export\nStandalone HTML + Markdown + JSON.\nImages follow the HTML export preference.\nRedaction: ' + (opt.vaultRedact ? 'ON (heuristic, review before sharing)' : 'OFF') + '\n'}
    ]
    download(vaultZip(files), fileBase() + '.zip')
    host.notify({ kind: 'success', message: 'ZIP archive saved' })
  } catch (err) { fail(err) }
}
async function vaultQuickExport(type, sessionId) {
  try {
    const sid = sessionId || host.state.focusedStoredSessionId.get() || host.state.activeSessionId.get()
    if (!sid) throw new Error('No active conversation')
    await fetchTurnsFor(sid)
    if (stateAtom.get().error) throw new Error(stateAtom.get().error)
    if (type === 'pdf') return await doDownloadPdf()
    if (type === 'html') return await doDownloadHtml()
    if (type === 'md') return doDownloadMd()
    if (type === 'json') return doDownloadJson()
    if (type === 'zip') return await vaultDownloadZip()
    if (type === 'txt') return vaultExportTxt()
    host.navigate(ROUTE)
  } catch (err) { fail(err) }
}

// Native Settings -> Plugins page, backed by the same persisted optAtom as the toolbar.
function VaultSettingsPage() {
  const opt = useValue(optAtom)
  const controls = [
    ['vaultImagesPdf', 'Embed images in PDF', 'Include local attachments in exported PDF pages.'],
    ['vaultImagesHtml', 'Embed images in HTML', 'Produce one standalone HTML with real image bytes.'],
    ['vaultImagesPng', 'Embed images in PNG', 'Include images in screenshots and copied PNG.'],
    ['vaultRedact', 'Hide sensitive text in every export', 'Heuristic masking: emails, tokens, secrets, local paths, IPs. Does NOT anonymize image pixels.']
  ]
  return jsxs('section', {
    className: 'p-4 max-w-2xl space-y-4',
    children: [
      jsx('h2', { className: 'text-base font-semibold', children: 'ChatVault export preferences' }),
      ...controls.map(([key, label, detail]) => jsxs('label', {
        className: 'flex items-start gap-3 rounded-md border border-(--border) p-3 cursor-pointer',
        children: [
          jsx('input', {
            type: 'checkbox', checked: key === 'vaultRedact' ? !!opt[key] : opt[key] !== false,
            onChange: () => { optAtom.set({ ...optAtom.get(), [key]: !optAtom.get()[key] }); savePrefs() },
            className: 'mt-1 accent-(--accent)'
          }),
          jsxs('span', { className: 'flex flex-col gap-1', children: [
            jsx('span', { className: 'text-sm font-medium', children: label }),
            jsx('span', { className: 'text-xs text-(--muted-foreground)', children: detail })
          ] })
        ]
      }, key)),
      jsx('p', { className: 'text-xs text-(--muted-foreground)', children:
        'Redaction is best-effort. Check generated files before public sharing. 7z is not supported; ZIP is available in the export toolbar.' })
    ]
  })
}
