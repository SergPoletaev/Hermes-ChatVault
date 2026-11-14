# ChatVault architecture / Архитектура

- Hermes ChatVault v0.2.2 is a separate desktop plugin, `hermes-chat-vault`, route `/chat-vault`.
- Base rendering core: smallmj/hermes-chat-share 1.1.8 (MIT). Local verified image fix: `HERMES_CHAT_SHARE_EMBED_MEDIA_V1`.
- `upstream/working-chat-share-1.1.8.js`: reference copy with image fix.
- `src/vault-extra.js`: additional export/storage/ZIP/privacy functionality from v0.1.0.
- `scripts/build.py`: combines base with v0.1.0 layer.
- `scripts/upgrade_v02.py`: deterministic v0.2.2 UI/i18n upgrade.
- `desktop/plugin.js`: distributable compiled single-file ESM plugin. No build required to install.
- Languages: host locale (auto) plus manual Russian/English preference, persisted in `optAtom`.
- SDK-owned navigation and composer context-menu contributions are removed upon plugin disable/unload. The host does not expose the general transcript-context menu.
- Never modify Hermes Gateway, local-runtime, original Chat Share, vision fix v8, model settings, or external caches.
- Secrets redaction is heuristic and does not inspect pixels of embedded images.
- PDF remains image/raster-based (text search/copy within a page not guaranteed).
- ZIP is ZIP32 STORE (no compression); a 300 MiB in-memory limit applies. No 7z.
- Locale override affects UI strings, not user-supplied message content.

## Public distribution
- `plugin.js` at repository root: one-click **Install from Git** (standalone desktop plugin; intentionally no `plugin.yaml`).
- `desktop/plugin.js`: byte-identical compatibility copy and rebuild output.
- `Install.ps1` / `Uninstall.ps1`: Windows manual installer with `HERMES_HOME` and local root discovery; no fixed user paths.
- `Install.sh` / `Uninstall.sh`: manual macOS/Linux fallback, default `$HOME/.hermes`.
- No private source fingerprints or user session files are included in this repository.
- Embedded images require `window.hermesDesktop.readFileDataUrl`; verify presence of bridge on target Desktop version.
