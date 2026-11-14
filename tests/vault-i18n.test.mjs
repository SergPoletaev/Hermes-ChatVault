import { test } from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import vm from 'node:vm'
const source = fs.readFileSync(new URL('../desktop/plugin.js', import.meta.url), 'utf8')
const a = source.indexOf('const STRINGS = {')
const b = source.indexOf('\nexport default {', a)
assert.ok(a > -1 && b > a)
const strings = vm.runInNewContext(`(() => { ${source.slice(a, b)}; return STRINGS; })()`)

test('Russian and English dictionaries have all UI keys', () => {
  const en = Object.keys(strings.en).sort(), ru = Object.keys(strings.ru).sort()
  assert.deepEqual(ru, en)
  assert.equal(strings.en.navLabel, 'ChatVault')
  assert.equal(strings.ru.navLabel, 'ChatVault')
  assert.notEqual(strings.ru.toggleTools, strings.en.toggleTools)
  assert.notEqual(strings.ru.quickZip, strings.en.quickZip)
  for (const key of en) {
    const a = strings.en[key], b = strings.ru[key]
    assert.equal(typeof a, typeof b, key)
    assert.notEqual(a, null, key); assert.notEqual(b, null, key)
    if (typeof a === 'string') { assert.ok(a.trim().length > 0, key); assert.ok(b.trim().length > 0, key) }
    else if (typeof a === 'function') { assert.equal(typeof a(2, 3), 'string', key); assert.equal(typeof b(2, 3), 'string', key) }
  }
})

test('unique navigation, SDK icon and context menu labels', () => {
  assert.match(source, /codicon: 'archive'/)
  assert.match(source, /ctx\.i18n\.register\(STRINGS\)/)
  assert.match(source, /ctx\.i18n\.onLocaleChange/)
  assert.match(source, /label: t\('quickPdf'\)/)
  assert.match(source, /label: t\('quickZip'\)/)
  assert.match(source, /function VaultBanner/)
  assert.match(source, /vaultLanguage.*'auto'/)
  assert.doesNotMatch(source, /navLabel: 'Share chat'/)
})

test('settings strings cover all options and privacy warnings', () => {
 for (const key of ['settingsTitle', 'settingsLead', 'languageLabel', 'vaultImagePdf', 'vaultImagePdfHelp',
   'vaultImageHtml', 'vaultImageHtmlHelp', 'vaultImagePng', 'vaultImagePngHelp', 'vaultRedactLabel',
   'vaultRedactHelp', 'privacyWarning', 'languageAuto', 'languageRussian', 'languageEnglish', 'metaThinking',
   'fileReaderUnavailable', 'zipTooLarge']) {
   assert.ok(strings.ru[key] && strings.en[key], key)
 }
})
