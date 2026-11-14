<a id="top"></a>

# Hermes ChatVault

**Версия 0.2.2 · Hermes Desktop · независимый форк Chat Share · MIT**

**Навигация / Navigation / 导航 / नेविगेशन:** [Русский](#ru) · [English](#en) · [简体中文](#zh) · [हिन्दी](#hi) · [Конец / End](#end)

---

<a id="ru"></a>

## 🇷🇺 Русский

**Hermes ChatVault** — плагин для локального экспорта и архивации переписок Hermes Desktop. Основан на открытом [Hermes Chat Share](https://github.com/smallmj/hermes-chat-share) (MIT), сохраняет его возможности и добавляет работу с оригинальными локальными изображениями, настройки приватности и архивы. Устанавливается **рядом** с Chat Share и не изменяет Hermes, Gateway, модели, MTP или исправление vision v8.

### Возможности

- Экспорт выбранных сообщений в **PDF, HTML, PNG, Markdown, JSON, TXT и ZIP**.
- Реальные вложенные изображения в PDF/PNG и автономный HTML с изображениями внутри файла (PNG/JPEG/WebP/GIF/BMP, если исходники ещё доступны в локальном кэше).
- Отдельные переключатели изображений для PDF, HTML и PNG.
- Опциональная эвристическая маскировка конфиденциального **текста**: ключи API, токены, почта, адреса IP и локальные пути. Действует на текстовые данные всех форматов; **не удаляет информацию с самих изображений**.
- ZIP с `conversation.html`, `.md`, `.txt`, `.json` и `manifest.json`.
- Выбор отдельных сообщений, поиск, варианты оформления, сведения о сессии и быстрый экспорт через поддерживаемое контекстное меню **поля ввода**.
- Отдельная ссылка **ChatVault** с иконкой архива: она не совпадает с исходной **Share chat**.
- Русский и английский интерфейс: автоматически по языку Hermes или вручную в ChatVault (на панели или в настройках).

### Установка и обновление

**Установка из GitHub (рекомендуется на Windows/macOS/Linux):** в Hermes откройте **Возможности → Plugins → Install from Git**, вставьте адрес репозитория ChatVault, подтвердите **Desktop**. Плагин содержит корневой `plugin.js`, не требует Agent-компонента, сборки или оригинального Chat Share. Для удаления используйте **Возможности → Plugins → Uninstall**. При обновлениях, установленных из GitHub, используйте интерфейс Hermes.

**Ручная установка:** Windows — `Install.cmd` или `Install.ps1` (находит `%LOCALAPPDATA%\hermes`, учитывает `HERMES_HOME`; нестандартный путь задаётся параметром `-HermesHome`). macOS/Linux — `sh Install.sh`, по умолчанию `$HOME/.hermes`, либо `HERMES_HOME=/путь sh Install.sh`. Установщики останавливаются, если не могут определить каталог установленного Hermes. Для обновлений, установленных через Git, используйте интерфейс Hermes, а не ручной скрипт.

1. Скачайте архив релиза, распакуйте целиком.
2. Полностью закройте **Hermes Desktop, включая трей**.
3. Запустите `Install.cmd` из корня распакованного репозитория (Windows).
4. Убедитесь, что появилось **`INSTALL SUCCESS: Hermes ChatVault 0.2.2`**.
5. Запустите Hermes. В левой панели найдите **ChatVault**, а в настройках плагинов — ChatVault preferences.

При ручной установке скрипт копирует готовый корневой `plugin.js` в `$HERMES_HOME/desktop-plugins/hermes-chat-vault/plugin.js`. Для установки **не нужны Python, Node.js, рабочий Chat Share или сборка из исходников**. Если ChatVault установлен, перед обновлением создаётся резервная копия `plugin.js.backup-*.bak`. Оригинальный Chat Share не изменяется.

**Удаление:** закройте Hermes, запустите `Uninstall.cmd`, затем перезапустите Hermes. Удаляется только ChatVault; ссылка навигации и элементы контекстного меню, зарегистрированные через SDK, перестают показываться после выгрузки плагина. Исходники и резервные копии сохраняются.

### Экспорт и настройки

Откройте нужную беседу и нажмите **ChatVault** слева. Выберите реплики и формат. Для быстрого экспорта используйте пункт ChatVault в **контекстном меню поля ввода** (если эта область SDK доступна в вашей сборке Hermes). В панели «Вложения и приватность» доступны включение изображений по форматам, маскировка текста и выбор языка. Изображения обрабатываются локально; плагин не содержит заданного адреса сервера разработчика. Для встраивания нужен файловый мост `readFileDataUrl`, наличие которого зависит от версии Hermes Desktop.

**Ограничения:** PDF сейчас растровый: текст на страницах может быть недоступен для выделения и поиска. ZIP создаётся без сжатия (формат ZIP32 STORE), с лимитом около 300 МиБ данных; настоящий 7z не реализован. Не все служебные ошибки ядра Hermes можно локализовать. Для общей области переписки Hermes не предоставляет поддерживаемого SDK-пункта правого клика; реализовано меню редактора ввода. Исчезнувший из кэша файл не может быть встроен. Перед публикацией проверяйте конфиденциальность готового документа.

### Исходники и воспроизводимость

`plugin.js` (а также совместимая копия `desktop/plugin.js`) — полный готовый к установке ESM-плагин. `upstream/working-chat-share-1.1.8.js` содержит исходную рабочую базу с исправлением изображений. `src/vault-extra.js` — слой ChatVault 0.1; `scripts/build.py` и `scripts/upgrade_v02.py` воспроизводят текущую сборку; `tests/` — автоматические тесты. Для пересборки (не требуется при обычной установке) выполните `python scripts/build.py upstream/working-chat-share-1.1.8.js <пустая_папка_результата>`; скрипт создаст новый полный репозиторий. Смотрите также `docs/ARCHITECTURE.md` и `BUILD-MANIFEST.json`.

**Происхождение:** форк `smallmj/hermes-chat-share`, лицензия MIT. Сохраняйте атрибуцию и текст `LICENSE`. Этот релиз проверен статическими и автоматическими тестами, но требует отдельной проверки UI на каждой версии Hermes.

[↑ К началу](#top) · [English →](#en) · [简体中文 →](#zh) · [हिन्दी →](#hi) · [↓ В конец](#end)

---

<a id="en"></a>

## 🇬🇧 English

**Hermes ChatVault** is a local conversation export and archive plugin for Hermes Desktop, independently installed alongside [Hermes Chat Share](https://github.com/smallmj/hermes-chat-share) (MIT). It preserves the base exporter and adds local embedded-image handling, privacy controls and ZIP bundles without altering the Hermes Gateway, models, MTP or vision fixes.

### Features

- Export selected messages as **PDF, HTML, PNG, Markdown, JSON, TXT and ZIP**.
- Embed local PNG/JPEG/WebP/GIF/BMP attachments into PDF/PNG pages and self-contained HTML when the source image files remain available.
- Separate image toggles for PDF, HTML and PNG; optional heuristic sensitive-text masking across export formats.
- ZIP containing `conversation.html`, `.md`, `.txt`, `.json` and `manifest.json`.
- Per-turn selection, search, layout/theme options, session metadata and quick export from the supported **composer context menu**.
- Distinct **ChatVault** sidebar entry with an archive icon, so it never appears as a second “Share chat”.
- Full English and Russian UI; automatically follow the Hermes locale or choose a language explicitly.

### Install / update / remove

**Install directly from GitHub (recommended on Windows/macOS/Linux):** in Hermes open **Capabilities → Plugins → Install from Git**, paste this repository URL and select **Desktop**. The repo contains a root `plugin.js`; there is no Agent half, build step or prerequisite original Chat Share. Remove using **Capabilities → Plugins → Uninstall**.

**Manual fallback:** Windows: `Install.cmd` / `Install.ps1`; it detects `%LOCALAPPDATA%\hermes` and honors `HERMES_HOME` (or `-HermesHome` for custom roots). macOS/Linux: `sh Install.sh` targeting `$HOME/.hermes` or `HERMES_HOME=/custom/path sh Install.sh`. Scripts refuse missing or ambiguous Hermes roots. For Git-managed installs use the Hermes UI to update/uninstall.

Close Hermes Desktop completely, including the tray, extract the release archive, and run `Install.cmd` on Windows (or `sh Install.sh` on macOS/Linux). Expect **`INSTALL SUCCESS: Hermes ChatVault 0.2.2`**, then reopen Hermes. Manual installation copies the prebuilt root `plugin.js` into `$HERMES_HOME/desktop-plugins/hermes-chat-vault/plugin.js`; it **does not require Python, Node.js or an installed original plugin**. Existing ChatVault installations are backed up before replacement. Original Chat Share stays untouched.

To remove: fully exit Hermes, run `Uninstall.cmd`, then restart. Only ChatVault is removed; its SDK-controlled navigation and composer menu contributions disappear on unload. Backups and repository source files are preserved.

### Using the plugin

Open a conversation, select **ChatVault** in the sidebar, choose turns and an export format. Adjust “Attachments & privacy” for embedded images and text masking. Language is selectable in the toolbar or plugin settings. Images are resolved locally; no developer-operated backend is involved. Embedded images require the Hermes Desktop `readFileDataUrl` bridge, which may not exist in all versions.

**Limitations:** PDF uses raster pages rather than selectable text. ZIP32 STORE does not compress and has an approximately 300 MiB in-memory limit. Native 7z is not included. Redaction is heuristic and **does not redact pixels inside images**. The Hermes SDK only exposes the composer context menu, not a right-click on an arbitrary message area. Missing cache files cannot be reconstructed. Always inspect sensitive exports before publishing.

### Source and attribution

`plugin.js` (also mirrored as `desktop/plugin.js`) is the complete installable ESM plugin. `upstream/working-chat-share-1.1.8.js` is the working upstream with the verified embedded-image fix. `src/vault-extra.js` includes the feature layer. `scripts/build.py` and `scripts/upgrade_v02.py` produce the current plugin deterministically; `tests/` holds automated tests. Rebuilding is optional: `python scripts/build.py upstream/working-chat-share-1.1.8.js <empty_output_directory>`. See `docs/ARCHITECTURE.md` and `BUILD-MANIFEST.json`.

Based on `smallmj/hermes-chat-share` under MIT; retain the original attribution and `LICENSE`. Automated tests do not replace real-desktop integration tests.

[↑ Top](#top) · [Русский](#ru) · [简体中文 →](#zh) · [हिन्दी →](#hi) · [↓ End](#end)

---

<a id="zh"></a>

## 🇨🇳 简体中文

**Hermes ChatVault** 是专为 Hermes Desktop 开发的本地聊天导出与归档插件，基于采用 MIT 许可证的 [Hermes Chat Share](https://github.com/smallmj/hermes-chat-share)。它作为**独立插件**安装，不会修改原版 Chat Share、Hermes Gateway、模型、MTP 或视觉修复。

### 功能

- 可将选中的消息导出为 **PDF、HTML、PNG、Markdown、JSON、TXT 和 ZIP**。
- 若本地缓存中的原图仍然存在，可将 PNG、JPEG、WebP、GIF 和 BMP 图片直接嵌入 PDF/PNG 页面与独立 HTML 文件。
- 分别控制 PDF、HTML 和 PNG 是否包含图片；可选的敏感**文本**遮盖适用于所有导出格式。
- ZIP 包括 `conversation.html`、`.md`、`.txt`、`.json` 和 `manifest.json`。
- 支持消息选择、搜索、页面样式、会话信息，以及通过**输入框右键菜单**快速导出。
- 左侧菜单显示独立名称 **ChatVault** 和归档图标，不再与原版 “Share chat” 重名。
- 界面完整支持俄语和英语；可跟随 Hermes 的语言，或手动指定。

### 安装与卸载

**推荐通过 GitHub 安装（Windows/macOS/Linux）：** 在 Hermes 中进入 **Capabilities → Plugins → Install from Git**，输入本项目仓库地址，选择 **Desktop**。仓库根目录提供 `plugin.js`，无需 Agent 组件、编译或原始 Chat Share。卸载请使用 **Capabilities → Plugins → Uninstall**。

**手动安装：** Windows 运行 `Install.cmd` / `Install.ps1`，自动检测 `%LOCALAPPDATA%\hermes`，也支持 `HERMES_HOME` 或 `-HermesHome`。macOS/Linux 使用 `sh Install.sh`，默认 `$HOME/.hermes`，或设置 `HERMES_HOME`。找不到 Hermes 目录会安全退出。通过 Git 安装时请使用 Hermes 界面管理升级与删除。

完全退出 Hermes Desktop（包括系统托盘），解压完整发布包，在 Windows 运行 `Install.cmd`（macOS/Linux 使用 `sh Install.sh`），看到 **`INSTALL SUCCESS: Hermes ChatVault 0.2.2`** 后重新启动 Hermes。手动安装程序将根目录的 `plugin.js` 复制到 `$HERMES_HOME/desktop-plugins/hermes-chat-vault/plugin.js`。**不需要 Python、Node.js 或原版插件**。升级时会备份原有 ChatVault 文件，不改动原版 Chat Share。

卸载时完全退出 Hermes，运行 `Uninstall.cmd` 并重新启动。插件的导航项与输入框菜单项随 SDK 卸载而消失。源码和备份不会删除。

### 使用与限制

打开会话，在左侧点击 **ChatVault**，选择消息与输出格式。可在“附件与隐私”设置中控制图片、文本遮盖和界面语言。图片由本地文件解析，不上传到开发者服务器。嵌入图片需要 Hermes Desktop 提供 `readFileDataUrl`，并非所有版本都保证支持。

PDF 当前以位图页面保存，文字未必可选中；ZIP32 STORE **不压缩**，内存导出上限约 300 MiB，暂无真正的 7z。遮盖是启发式的，**不会隐藏图片像素中的敏感内容**。Hermes SDK 仅支持输入框的右键菜单扩展，而不是消息区域的任意右键菜单。缓存中已丢失的图片无法恢复，公开分享前请检查内容。

### 源码和许可证

`plugin.js`（以及兼容副本 `desktop/plugin.js`）是可直接安装的完整插件。`upstream/working-chat-share-1.1.8.js` 是含图片修复的原版基础源码，`src/vault-extra.js` 为功能层，`scripts/build.py` 与 `scripts/upgrade_v02.py` 用于可复现构建，`tests/` 包含测试。重新构建是可选步骤：`python scripts/build.py upstream/working-chat-share-1.1.8.js <empty_output_directory>`。详情见 `docs/ARCHITECTURE.md`。

本项目基于 MIT 许可的 `smallmj/hermes-chat-share`，请保留 `LICENSE` 与原作者署名。自动测试不等同于 Hermes 桌面端的实际测试。

[↑ 返回顶部](#top) · [Русский](#ru) · [English](#en) · [हिन्दी →](#hi) · [↓ 文末](#end)

---

<a id="hi"></a>

## 🇮🇳 हिन्दी

**Hermes ChatVault** Hermes Desktop की चैट को स्थानीय रूप से निर्यात और संग्रहित करने वाला स्वतंत्र प्लगइन है। यह MIT लाइसेंस वाले [Hermes Chat Share](https://github.com/smallmj/hermes-chat-share) पर आधारित है। इसे मूल Chat Share के साथ अलग से इंस्टॉल किया जाता है; यह Hermes Gateway, मॉडल, MTP या विज़न फ़िक्स को नहीं बदलता।

### सुविधाएँ

- चुने गए संदेशों को **PDF, HTML, PNG, Markdown, JSON, TXT और ZIP** में निर्यात करें।
- मूल स्थानीय PNG/JPEG/WebP/GIF/BMP चित्र उपलब्ध हों तो उन्हें PDF/PNG में और एकल ऑफ़लाइन HTML फ़ाइल में सीधे एम्बेड करें।
- PDF, HTML और PNG के लिए अलग चित्र स्विच, सभी फ़ॉर्मेट में संवेदनशील **पाठ** छिपाने का वैकल्पिक प्रयास।
- ZIP में `conversation.html`, `.md`, `.txt`, `.json` और `manifest.json`।
- संदेश चुनना, खोज, थीम/लेआउट, सत्र की जानकारी और **संदेश लिखने वाले बॉक्स** के संदर्भ मेनू से त्वरित निर्यात।
- साइडबार में अलग **ChatVault** नाम और आर्काइव चिह्न — मूल “Share chat” से अलग।
- पूरा प्लगइन इंटरफ़ेस रूसी और अंग्रेज़ी में; Hermes की भाषा अपनाएँ या स्वयं चुनें।

### इंस्टॉल / अपडेट / हटाना

**GitHub से इंस्टॉल करें (Windows/macOS/Linux, अनुशंसित):** Hermes में **Capabilities → Plugins → Install from Git** खोलें, इस रिपॉज़िटरी का URL दें और **Desktop** चुनें। रूट में `plugin.js` मौजूद है; Agent घटक, बिल्ड और मूल Chat Share ज़रूरी नहीं हैं। हटाने के लिए Hermes **Capabilities → Plugins → Uninstall** उपयोग करें।

**मैनुअल विकल्प:** Windows पर `Install.cmd` / `Install.ps1` (`%LOCALAPPDATA%\hermes` या `HERMES_HOME`, कस्टम के लिए `-HermesHome`)। macOS/Linux पर `sh Install.sh`, डिफ़ॉल्ट `$HOME/.hermes` या `HERMES_HOME=/path`। यदि Hermes का सही होम नहीं मिला तो स्क्रिप्ट बदलाव किए बिना रुक जाती है। Git इंस्टॉल को Hermes UI से अपडेट या हटाएँ।

Hermes Desktop को ट्रे सहित पूरी तरह बंद करें। रिलीज़ ZIP को अनज़िप कर Windows पर `Install.cmd` (macOS/Linux पर `sh Install.sh`) चलाएँ। **`INSTALL SUCCESS: Hermes ChatVault 0.2.2`** दिखाई देने पर Hermes फिर खोलें। मैनुअल इंस्टॉलर रूट `plugin.js` को `$HERMES_HOME/desktop-plugins/hermes-chat-vault/plugin.js` में कॉपी करता है। **Python, Node.js या मूल प्लगइन आवश्यक नहीं हैं**। मौजूदा ChatVault अपडेट होने से पहले बैकअप बनता है; मूल Chat Share नहीं बदला जाता।

हटाने के लिए Hermes बंद करें, `Uninstall.cmd` चलाएँ और Hermes पुनः शुरू करें। केवल ChatVault हटता है; SDK के अंतर्गत पंजीकृत साइडबार और इनपुट मेनू अपने-आप हट जाते हैं। स्रोत और बैकअप सुरक्षित रहते हैं।

### उपयोग और सीमाएँ

चैट खोलें, बाईं ओर **ChatVault** चुनें, संदेश और फ़ॉर्मेट चुनें। “Attachments & privacy” में चित्र और टेक्स्ट मास्किंग नियंत्रित करें। भाषा भी वहीं या टूलबार में चुन सकते हैं। चित्र स्थानीय रूप से पढ़े जाते हैं; उन्हें डेवलपर के सर्वर पर नहीं भेजा जाता। चित्र एम्बेडिंग के लिए Hermes Desktop में `readFileDataUrl` होना ज़रूरी है, जो हर संस्करण में उपलब्ध नहीं हो सकता।

PDF अभी रास्टर पृष्ठों का उपयोग करता है, इसलिए उसका पाठ खोजने/चुनने योग्य नहीं भी हो सकता। ZIP32 STORE **संपीड़न नहीं करता**; लगभग 300 MiB का इन-मेमरी सीमा है। वास्तविक 7z उपलब्ध नहीं है। संवेदनशील पाठ छिपाना अनुमान-आधारित है; **चित्र के पिक्सल में मौजूद जानकारी नहीं छिपती**। Hermes SDK केवल इनपुट बॉक्स का संदर्भ मेनू उपलब्ध कराता है, पूरे संदेश क्षेत्र का नहीं। हट चुकी कैश फ़ाइलों से चित्र पुनः नहीं बनाए जा सकते। साझा करने से पहले निर्यात जाँचें।

### स्रोत और लाइसेंस

`plugin.js` पूर्ण इंस्टॉल योग्य ESM प्लगइन है। `upstream/working-chat-share-1.1.8.js` चित्र सुधार सहित मूल कार्यशील संस्करण है। `src/vault-extra.js` सुविधाएँ जोड़ता है; `scripts/build.py` और `scripts/upgrade_v02.py` दोहराने योग्य बिल्ड बनाते हैं। `tests/` में स्वचालित जाँच हैं। वैकल्पिक रीबिल्ड: `python scripts/build.py upstream/working-chat-share-1.1.8.js <empty_output_directory>`। आगे `docs/ARCHITECTURE.md` पढ़ें।

मूल परियोजना `smallmj/hermes-chat-share` का MIT लाइसेंस और श्रेय बनाए रखें। स्वचालित परीक्षण वास्तविक Windows/Hermes परीक्षण का स्थान नहीं लेते।

[↑ शुरुआत](#top) · [Русский](#ru) · [English](#en) · [简体中文](#zh) · [↓ अंत](#end)

---

<a id="end"></a>

**Конец документа / End of document / 文档结束 / दस्तावेज़ समाप्त**

[↑ К началу / Back to top / 返回顶部 / ऊपर जाएँ](#top) · [Русский](#ru) · [English](#en) · [简体中文](#zh) · [हिन्दी](#hi)
