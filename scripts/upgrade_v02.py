"""Deterministic 0.1.0 -> 0.2.2 source upgrade, preserving upstream rendering.

No Electron internals are modified. All edits have explicit source anchors.
"""
import sys
from pathlib import Path


def once(s, old, new, label):
    n = s.count(old)
    if n != 1:
        raise ValueError(f'{label}: expected one anchor, found {n}')
    return s.replace(old, new, 1)


def upgrade(s):
    s = s.replace('\r\n', '\n')
    if "const PLUGIN_VERSION = '0.1.0-vault'" not in s:
        raise ValueError('Requires ChatVault v0.1.0 fork as input')
    s = once(s, "const PLUGIN_VERSION = '0.1.0-vault'", "const PLUGIN_VERSION = '0.2.2-vault'", 'version')
    s = once(s, "  vaultRedact: false\n})", "  vaultRedact: false,\n  vaultLanguage: 'auto'\n})", 'language default')
    s = once(s, "'vaultImagesPng', 'vaultRedact'", "'vaultImagesPng', 'vaultRedact', 'vaultLanguage'", 'load pref')
    s = once(s, "vaultImagesPng, vaultRedact } = optAtom.get()", "vaultImagesPng, vaultRedact, vaultLanguage } = optAtom.get()", 'save prefs destructure')
    s = once(s, "vaultImagesPng, vaultRedact })", "vaultImagesPng, vaultRedact, vaultLanguage })", 'save prefs payload')
    # UI language: auto follows the desktop host; explicit RU/EN override works independently.
    s = once(s, "const t = (key, ...args) => ctxI18nRef && ctxI18nRef.t(key, ...args)\nlet ctxI18nRef = null", '''function vaultResolvedString(language, key, args, fallback) {
  const entry = (STRINGS[language] && STRINGS[language][key]) ?? STRINGS.en[key]
  if (entry === undefined) return fallback ? fallback(key, ...args) : key
  return typeof entry === 'function' ? entry(...args) : entry
}
const t = (key, ...args) => {
  const lang = optAtom.get().vaultLanguage || 'auto'
  if (lang === 'en' || lang === 'ru') return vaultResolvedString(lang, key, args)
  return ctxI18nRef ? ctxI18nRef.t(key, ...args) : vaultResolvedString('en', key, args)
}
let ctxI18nRef = null
function useVaultT() {
  const sdkT = usePluginI18n(PLUGIN_ID)
  const opts = useValue(optAtom)
  const lang = opts.vaultLanguage || 'auto'
  return (key, ...args) => lang === 'auto' ? sdkT(key, ...args) : vaultResolvedString(lang, key, args, sdkT)
}
''', 'language wrapper')
    s = s.replace('const t = usePluginI18n(PLUGIN_ID)', 'const t = useVaultT()')
    # Replace the entire v0.1 settings page with localized, branded settings.
    start = s.index('function VaultSettingsPage() {')
    end = s.index('// HERMES_CHATVAULT_FORK_V1', start)
    settings = '''function VaultSettingsPage() {
  const opt = useValue(optAtom)
  const tr = useVaultT()
  const setOpt = patch => {
    optAtom.set({ ...optAtom.get(), ...patch })
    savePrefs()
  }
  const controls = [
    ['vaultImagesPdf', 'vaultImagePdf', 'vaultImagePdfHelp'],
    ['vaultImagesHtml', 'vaultImageHtml', 'vaultImageHtmlHelp'],
    ['vaultImagesPng', 'vaultImagePng', 'vaultImagePngHelp'],
    ['vaultRedact', 'vaultRedactLabel', 'vaultRedactHelp']
  ]
  return jsxs('section', { className: 'p-5 max-w-3xl space-y-4', children: [
    jsxs('div', { className: 'rounded-xl border border-(--border) p-4',
      style: { background: 'linear-gradient(112deg, rgba(37,99,235,.11), rgba(14,165,233,.04))' },
      children: [
        jsx('div', { className: 'text-[11px] tracking-[.18em] font-bold text-(--muted-foreground)', children: 'HERMES · CHATVAULT' }),
        jsx('h2', { className: 'font-bold text-lg mt-1', children: tr('settingsTitle') }),
        jsx('p', { className: 'text-sm mt-1 text-(--muted-foreground)', children: tr('settingsLead') })
      ] }),
    jsxs('label', { className: 'flex flex-col gap-2 rounded-lg border border-(--border) p-3', children: [
      jsx('span', { className: 'text-sm font-semibold', children: tr('languageLabel') }),
      jsx('select', { className: 'text-sm rounded-md border border-(--border) bg-(--background) text-(--foreground) px-3 py-2',
        value: opt.vaultLanguage || 'auto', onChange: e => setOpt({ vaultLanguage: e.target.value }),
        children: [
          jsx('option', { value: 'auto', children: tr('languageAuto') }),
          jsx('option', { value: 'ru', children: tr('languageRussian') }),
          jsx('option', { value: 'en', children: tr('languageEnglish') })
        ] }),
      jsx('span', { className: 'text-xs text-(--muted-foreground)', children: tr('languageHelp') })
    ] }),
    jsx('h3', { className: 'text-sm font-semibold', children: tr('settingsPrivacy') }),
    ...controls.map(([key, label, detail]) => jsxs('label', {
      className: 'flex items-start gap-3 rounded-lg border border-(--border) p-3 cursor-pointer', children: [
        jsx('input', { type: 'checkbox', checked: key === 'vaultRedact' ? !!opt[key] : opt[key] !== false,
          onChange: () => setOpt({ [key]: !opt[key] }), className: 'mt-1 size-4 accent-(--accent)' }),
        jsxs('span', { className: 'flex flex-col gap-1', children: [
          jsx('span', { className: 'text-sm font-medium', children: tr(label) }),
          jsx('span', { className: 'text-xs text-(--muted-foreground)', children: tr(detail) })
        ] })
      ]
    }, key)),
    jsx('p', { className: 'text-xs rounded-lg border border-(--border) p-3 text-(--muted-foreground)', children: tr('privacyWarning') })
  ] })
}
'''
    s = s[:start] + settings + s[end:]
    # UI structure: named sections, compact gradient brand header.
    s = once(s, "    className: 'border-b border-(--border) sticky top-0 bg-(--background) z-10 flex flex-col gap-1.5 px-4 py-2'", "    className: 'border-b border-(--border) sticky top-0 bg-(--background) z-10 flex flex-col gap-2 px-4 py-2'", 'toolbar container')
    s = once(s, "jsxs('div', { className: 'flex items-center gap-x-2.5 gap-y-1 flex-wrap min-w-0', children: [", "jsxs('div', { className: 'flex items-center gap-x-2.5 gap-y-1 flex-wrap min-w-0 rounded-lg border border-(--border) bg-(--card) px-2.5 py-2', children: [\n        jsx('span', { className: 'font-semibold text-xs whitespace-nowrap', children: t('selectionHead') }),", 'toolbar select')
    s = once(s, "jsxs('div', { className: 'flex items-center gap-x-2.5 gap-y-1 flex-wrap', children: [", "jsxs('div', { className: 'flex items-center gap-x-2.5 gap-y-1 flex-wrap rounded-lg border border-(--border) px-2.5 py-2', children: [\n        jsx('span', { className: 'font-semibold text-xs whitespace-nowrap', children: t('layoutHead') }),", 'toolbar layout')
    s = once(s, '''      jsxs('div', { className: 'flex items-center gap-3 flex-wrap', children: [
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
      ] }),''', '''      jsxs('div', { className: 'flex items-center gap-3 flex-wrap rounded-lg border border-(--border) px-2.5 py-2', children: [
        jsx('span', { className: 'font-semibold text-xs whitespace-nowrap', children: t('privacyHead') }),
        ...[
          ['vaultImagesPdf', 'vaultImagePdf'],
          ['vaultImagesHtml', 'vaultImageHtml'],
          ['vaultImagesPng', 'vaultImagePng'],
          ['vaultRedact', 'vaultRedactLabel']
        ].map(([key, label]) => jsx('label', {
          className: 'flex items-center gap-1.5 text-xs text-(--foreground) cursor-pointer select-none',
          children: [
            jsx('input', { type: 'checkbox', checked: key === 'vaultRedact' ? !!opt[key] : opt[key] !== false,
              onChange: () => setOpt({ [key]: !opt[key] }), className: 'size-3.5 accent-(--accent)' }),
            t(label)
          ]
        }, key)),
        jsxs('label', { className: 'flex items-center gap-1.5 text-xs', children: [
          jsx('span', { children: t('languageShort') }),
          jsx('select', { className: 'rounded-md border border-(--border) bg-(--background) text-(--foreground) px-1 py-1 text-xs',
            value: opt.vaultLanguage || 'auto', onChange: e => setOpt({ vaultLanguage: e.target.value }),
            children: [jsx('option', { value: 'auto', children: t('languageAuto') }),
              jsx('option', { value: 'ru', children: t('languageRussian') }),
              jsx('option', { value: 'en', children: t('languageEnglish') })] })
        ] })
      ] }),''', 'privacy controls')
    s = once(s, "jsxs('div', { className: 'flex items-center gap-2 flex-wrap', children: [\n        jsx(Button, { size: 'sm', onClick: () => void doDownloadMd()", "jsxs('div', { className: 'flex items-center gap-2 flex-wrap rounded-lg border border-(--border) bg-(--card) px-2.5 py-2', children: [\n        jsx('span', { className: 'font-semibold text-xs whitespace-nowrap', children: t('exportsHead') }),\n        jsx(Button, { size: 'sm', onClick: () => void doDownloadMd()", 'export controls')
    s = once(s, "    jsx(TitleHeader, { t, st }),\n    jsx(Toolbar, {}),", "    jsx(VaultBanner, { t }),\n    jsx(TitleHeader, { t, st }),\n    jsx(Toolbar, {}),", 'banner mount')
    s = once(s, "function SharePage () {", '''function VaultBanner({ t }) {
  return jsxs('div', { className: 'mx-4 mt-3 rounded-xl border border-(--border) px-4 py-3 flex items-center justify-between flex-wrap gap-2',
    style: { background: 'linear-gradient(100deg, rgba(37,99,235,.14), rgba(20,184,166,.075))' }, children: [
    jsxs('div', { className: 'flex flex-col gap-0.5', children: [
      jsx('span', { className: 'font-bold text-[11px] tracking-[.18em] text-(--muted-foreground)', children: 'HERMES / CHATVAULT' }),
      jsx('span', { className: 'text-sm text-(--foreground)', children: t('bannerLead') })
    ] }),
    jsx('span', { className: 'text-[11px] rounded-full px-3 py-1 border border-(--border) bg-(--background) font-medium', children: t('bannerBadge') })
  ] })
}

function SharePage () {''', 'banner component')
    # Unique identity: visible in sidebar, menus, titlebar and shortcut hint.
    s = once(s, "navLabel: 'Share chat'", "navLabel: 'ChatVault'", 'EN nav')
    s = once(s, "shareTitle: 'Share conversation'", "shareTitle: 'ChatVault — Export & Archive'", 'EN title')
    s = once(s, "navLabel: '分享对话'", "navLabel: 'ChatVault'", 'ZH nav')
    s = once(s, "shareTitle: '分享对话'", "shareTitle: 'ChatVault · 导出与归档'", 'ZH title')
    s = once(s, "name: 'ChatVault'", "name: 'Hermes ChatVault'", 'plugin display name')
    s = once(s, "codicon: 'share'", "codicon: 'archive'", 'sidebar icon')
    s = once(s, "icon: jsx(Codicon, { name: 'share' })", "icon: jsx(Codicon, { name: 'archive' })", 'titlebar icon')
    s = once(s, "category: 'Chat Share'", "category: 'ChatVault'", 'keybind category')
    # Name is brand, shared across languages; text of menu is generated dynamically by preference.
    for old, new in [
       ("label: 'Export chat to PDF'", "label: t('quickPdf')"),
       ("label: 'Export chat to HTML'", "label: t('quickHtml')"),
       ("label: 'Export chat to Markdown'", "label: t('quickMd')"),
       ("label: 'Export chat to JSON'", "label: t('quickJson')"),
       ("label: 'Archive chat as ZIP'", "label: t('quickZip')"),
       ("label: 'Export chat to TXT'", "label: t('quickTxt')")
    ]:
       s = once(s, old, new, 'context label')
    s = once(s, "keywords: ['share', 'export', 'png', 'screenshot', '分享', '截图', '长图']", "keywords: ['chatvault', 'archive', 'export', 'pdf', 'zip', 'архив', 'экспорт', '分享']", 'palette keywords')
    # Export notifications, output roles and privacy notes.
    s = once(s, "message: 'TXT saved'", "message: t('txtSaved')", 'TXT notification')
    s = once(s, "message: 'ZIP archive saved'", "message: t('zipSaved')", 'ZIP notification')
    s = once(s, "'[User' + (turn.user.ts", "'[' + t('labelUser') + (turn.user.ts", 'TXT user')
    s = once(s, "'[Assistant' + (a.ts", "'[' + t('labelAssistant') + (a.ts", 'TXT assistant')
    s = once(s, "'User:', turn.user.text", "t('labelUser') + ':', turn.user.text", 'ZIP txt user')
    s = once(s, "'Assistant:', a.text", "t('labelAssistant') + ':', a.text", 'ZIP txt assistant')
    s = once(s, "'User\\n\\n' + turn.user.text", """t('labelUser') + '\\n\\n' + turn.user.text""", 'Markdown user') if "'User\\n\\n' + turn.user.text" in s else s
    s = s.replace("'User\\n\\n' + turn.user.text", "t('labelUser') + '\\n\\n' + turn.user.text")
    s = s.replace("'Assistant\\n\\n' + a.text", "t('labelAssistant') + '\\n\\n' + a.text")
    s = once(s, "t('shareTitle')", "t('shareTitle')", 'noop') if False else s
    # Full bilingual registration in a separate appended merge, to keep inherited Chinese support.
    enkeys = '''    bannerLead: 'Export conversations with embedded images, privacy controls and one-click archives.',
    bannerBadge: 'LOCAL EXPORT',
    selectionHead: 'Selection', layoutHead: 'Appearance', privacyHead: 'Attachments & privacy', exportsHead: 'Save as',
    vaultImagePdf: 'Images in PDF', vaultImageHtml: 'Images in HTML', vaultImagePng: 'Images in PNG',
    vaultRedactLabel: 'Mask sensitive text',
    languageShort: 'Language', languageLabel: 'Interface language', languageAuto: 'System / Hermes',
    languageRussian: 'Русский', languageEnglish: 'English',
    languageHelp: 'Automatically follows the Hermes locale, or choose Russian or English.',
    settingsTitle: 'ChatVault preferences', settingsLead: 'These preferences apply to all exported sessions.',
    settingsPrivacy: 'Export options & privacy',
    vaultImagePdfHelp: 'Embed real local pictures into PDF pages.',
    vaultImageHtmlHelp: 'Create a self-contained HTML file with embedded pictures.',
    vaultImagePngHelp: 'Include pictures in PNG screenshots and the clipboard image.',
    vaultRedactHelp: 'Mask recognizable tokens, secrets, email addresses, IP addresses and local paths in all text exports.',
    privacyWarning: 'Text masking is best-effort. It does not remove text inside pictures. Review exports before publicly sharing. ZIP is supported; 7z is not.',
    quickPdf: 'Export chat to PDF', quickHtml: 'Export chat to HTML', quickMd: 'Export chat to Markdown',
    quickJson: 'Export chat to JSON', quickZip: 'Archive chat as ZIP', quickTxt: 'Export chat to TXT',
    txtSaved: 'TXT saved', zipSaved: 'ZIP archive saved',
'''
    s = once(s, "  en: {\n    navLabel:", "  en: {\n" + enkeys + "    navLabel:", 'English keys')
    rukeys = '''  ru: {
    navLabel: 'ChatVault', shareTitle: 'ChatVault — экспорт и архив',
    bannerLead: 'Сохраняйте переписку с изображениями, настройками приватности и архивами.',
    bannerBadge: 'ЛОКАЛЬНЫЙ ЭКСПОРТ',
    selectionHead: 'Выбор', layoutHead: 'Оформление', privacyHead: 'Вложения и приватность', exportsHead: 'Сохранить как',
    vaultImagePdf: 'Изображения в PDF', vaultImageHtml: 'Изображения в HTML', vaultImagePng: 'Изображения в PNG',
    vaultRedactLabel: 'Скрывать конфиденциальный текст',
    languageShort: 'Язык', languageLabel: 'Язык интерфейса', languageAuto: 'Авто / Hermes',
    languageRussian: 'Русский', languageEnglish: 'English',
    languageHelp: 'Автоматически использовать язык Hermes или выбрать русский/английский вручную.',
    settingsTitle: 'Настройки ChatVault', settingsLead: 'Параметры действуют для всех экспортируемых сессий.',
    settingsPrivacy: 'Экспорт и конфиденциальность',
    vaultImagePdfHelp: 'Встраивать оригинальные локальные изображения непосредственно в PDF.',
    vaultImageHtmlHelp: 'Создавать автономный HTML со встроенными изображениями.',
    vaultImagePngHelp: 'Добавлять изображения в снимки PNG и копируемое изображение.',
    vaultRedactHelp: 'Маскировать распознанные ключи, токены, адреса электронной почты, IP и локальные пути во всех текстовых форматах.',
    privacyWarning: 'Маскировка текста эвристическая. Текст внутри изображений не удаляется. Проверяйте документы перед публикацией. ZIP поддерживается, 7z — нет.',
    quickPdf: 'Экспортировать чат в PDF', quickHtml: 'Экспортировать чат в HTML', quickMd: 'Экспортировать чат в Markdown',
    quickJson: 'Экспортировать чат в JSON', quickZip: 'Архивировать чат в ZIP', quickTxt: 'Экспортировать чат в TXT',
    txtSaved: 'TXT сохранён', zipSaved: 'ZIP-архив сохранён',
    retry: 'Повторить', loadFail: 'Не удалось загрузить переписку',
    needSession: 'Сначала откройте нужный чат, затем вернитесь к экспорту.',
    empty: 'В этой сессии пока нет сообщений',
    labelUser: 'Вы', labelAssistant: 'Ассистент',
    selectAll: 'Все', clearSel: 'Ничего', invertSel: 'Инвертировать',
    selCount: (n, m) => n + ' / ' + m + ' сообщений',
    widthN: w => 'ширина ' + w + ' пкс', fontN: px => 'шрифт ' + px + ' пкс',
    toggleTools: 'вызовы инструментов', btnPng: 'Скачать PNG', btnCopyPng: 'Копировать изображение',
    copied: 'Изображение скопировано в буфер обмена',
    askTitle: 'Не удалось завершить экспорт',
    reasonTooTall: 'Переписка слишком длинная для одного изображения (ограничение браузера). Сохраните постраничные PNG или выберите HTML, Markdown либо PDF.',
    reasonBlocked: 'Политика безопасности Hermes запрещает плагину запись изображений в буфер обмена.',
    btnCancel: 'Отмена', btnDownload: 'Скачать PNG по страницам',
    saved: 'Сохранено', savedN: n => 'Сохранено файлов: ' + n + ' (единый PNG слишком велик)',
    exportFailed: 'Ошибка экспорта', turnsN: 'сообщений',
    searchPh: 'Поиск по сообщениям…', widthL: 'Ширина', fontL: 'Шрифт',
    expand: (a, b) => 'Развернуть (ещё ответов: ' + a + (b ? ', инструментов: ' + b : '') + ')',
    collapse: 'Свернуть', fullLabel: 'полная переписка',
    themeL: 'Тема', themeM: m => m === 'auto' ? 'как в Hermes' : (m === 'light' ? 'светлая' : 'тёмная'),
    toggleMeta: 'сведения о сессии', btnPdf: 'PDF',
    rangeTip: n => 'Выделены сообщения: ' + n, rangeClear: 'сбросить',
    editTitleTip: 'Изменить заголовок экспорта',
    verTip: 'Версия плагина. Если номер не изменился после обновления, полностью перезапустите Hermes.'
  },
'''
    s = once(s, "  'zh': {\n", rukeys + "  'zh': {\n", 'Russian dictionary')
    # UI-facing errors and metadata reflect explicit RU/EN preference.
    s = once(s, "    if (!['auto', 'light', 'dark'].includes(next.theme)) next.theme = 'auto'", "    if (!['auto', 'light', 'dark'].includes(next.theme)) next.theme = 'auto'\n    if (!['auto', 'ru', 'en'].includes(next.vaultLanguage)) next.vaultLanguage = 'auto'", 'language preference validation')
    s = once(s, "'thinking: ' + m.effort", "t('metaThinking') + ': ' + m.effort", 'metadata reasoning')
    s = once(s, "'cache hit: ' + m.cacheHitPct + '%'", "t('metaCache') + ': ' + m.cacheHitPct + '%'", 'metadata cache')
    s = once(s, "m.totalTokens.toLocaleString('en-US') + ' tokens'", "m.totalTokens.toLocaleString('en-US') + ' ' + t('metaTokens')", 'metadata tokens')
    s = once(s, "throw new Error('No active conversation')", "throw new Error(t('needSession'))", 'quick session error')
    s = once(s, "'<span class=\"chsh-ph\">Image link: '", "'<span class=\"chsh-ph\">' + t('imageLink') + ': '", 'image link placeholder')
    s = once(s, "throw new Error('Image export needs the Hermes Desktop local-file reader (not available in this window)')", "throw new Error(t('fileReaderUnavailable'))", 'file API missing')
    s = once(s, "throw new Error('Cannot read image: ' + ", "throw new Error(t('cannotReadImage') + ': ' + ", 'file read error')
    s = once(s, "throw new Error('Archive is too large for in-memory ZIP export (300 MB limit)')", "throw new Error(t('zipTooLarge'))", 'ZIP size error')
    en_extra = """    metaThinking: 'thinking', metaCache: 'cache hit', metaTokens: 'tokens',
    imageLink: 'Image link', fileReaderUnavailable: 'Cannot read local images in this Hermes window',
    cannotReadImage: 'Cannot read image', zipTooLarge: 'ZIP exceeds the 300 MB in-memory limit',
"""
    ru_extra = """    metaThinking: 'рассуждение', metaCache: 'попадание в кеш', metaTokens: 'токенов',
    imageLink: 'Ссылка на изображение', fileReaderUnavailable: 'В этом окне Hermes недоступно чтение локальных изображений',
    cannotReadImage: 'Не удалось прочитать изображение', zipTooLarge: 'Архив ZIP превышает лимит памяти 300 МБ',
"""
    s = once(s, "    bannerLead: 'Export conversations with embedded images, privacy controls and one-click archives.',", en_extra + "    bannerLead: 'Export conversations with embedded images, privacy controls and one-click archives.',", 'additional EN keys')
    s = once(s, "    bannerLead: 'Сохраняйте переписку с изображениями, настройками приватности и архивами.',", ru_extra + "    bannerLead: 'Сохраняйте переписку с изображениями, настройками приватности и архивами.',", 'additional RU keys')
    return s


if __name__ == '__main__':
    p = Path(sys.argv[1])
    out = Path(sys.argv[2])
    out.write_text(upgrade(p.read_text('utf-8-sig')), 'utf-8')
