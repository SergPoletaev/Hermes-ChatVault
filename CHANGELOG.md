# Changelog

## 0.2.2 — 2026-11-14 · CI and Windows installation fixes

- Fix PowerShell `$HOME` read-only variable collision in install/uninstall scripts.
- Preserve `.gitignore` on GitHub, and make source rebuild tolerant if a browser upload omits that hidden file.
- Add regression checks for PowerShell variable use, hidden Git configuration and package completeness.
- No changes to the exporter, embedded-image handling, or Hermes runtime integrations.

## 0.2.1 — 2026-11-14 · Public / portable packaging

- Added root `plugin.js` for native Hermes **Install from Git** desktop-only installation.
- Removed root `plugin.yaml` to avoid unintended Agent component installation.
- Added portable Windows PowerShell and Unix shell installers with explicit `HERMES_HOME` handling.
- Removed original private-source checksum from public build manifest.
- Added public artifact privacy audit and conservative gitignore rules.
- Retained 0.2.0 export behavior; no changes to Gemma, vision or Gateway.

## 0.2.0 — 2026-11-14

- Unique navigation **ChatVault** and archive icon; no more two **Share chat** links when both plugins are enabled.
- Branded, compact banner and reorganized selection/appearance/privacy/export controls.
- Complete Russian and English UI strings, including settings, context menu, notifications and help text.
- Auto (Hermes locale), explicit Russian and English language selector. Preference persists across launches.
- Unified `README.md` with Russian first; internal language and top/end anchors. Removed standalone language README files.
- Fully installable source repository: `Install.cmd` uses the bundled compiled desktop plugin; no locally installed Chat Share or Python needed.
- Source builder remains reproducible from the original working upstream file.
- Existing embedded-image export, ZIP, privacy and per-turn selection retained.

## 0.1.0 — 2026-11-14

- Independent Chat Share fork with PDF/HTML/PNG embedded image controls, ZIP, TXT, JSON and Markdown.
- Opt-in heuristic sensitive-text redaction.
- Composer context-menu quick export.

## Known limits

- Manual RU/EN can localize UI, but actual chat content is not translated.
- Some native Hermes service error strings originate in the host and cannot be translated by a desktop plugin.
- PDF is raster-based, not searchable text.
- 7z is not supported; ZIP32 STORE currently stores files without compression.
- No arbitrary transcript right-click injection; only SDK-owned composer context menu.
- Redaction does not modify sensitive information visible inside image pixels.
