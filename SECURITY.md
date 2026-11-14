# Public release security / Публичная безопасность

This repository contains source code, synthetic tests, generic package metadata and a compiled ESM Desktop plugin. It must not contain real conversations, exports, images, model weights, API keys, machine-generated logs, `HERMES_HOME` configuration, user-specific absolute paths or private source provenance fingerprints.

**Code scanning:** run `python scripts/audit_public_release.py` before publishing. It checks the distributed ZIP/repository for common accidental personal data. Such checks are best-effort and do not prove absence of every possible secret.

**Plugin permissions:** Desktop plugins run with the authority of the Hermes renderer. Review code before installation. This fork uses a local file reader to embed image attachments. No network endpoint is intentionally used to upload chat contents.

**Redaction:** text masking is heuristic, and cannot remove metadata or sensitive pixels from photos. Review exports before public sharing.

**Installation:** prefer Hermes **Install from Git** for cross-platform support and managed uninstall. Manual scripts refuse unknown destinations and never modify other plugins, Hermes core, models or existing user chats.
