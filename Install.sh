#!/bin/sh
# Portable manual install for macOS/Linux. Preferred: Hermes Install from Git.
set -eu
ROOT=$(CDPATH= cd "$(dirname "$0")" && pwd)
SRC="$ROOT/plugin.js"
if [ ! -f "$SRC" ]; then echo 'ERROR: missing root plugin.js' >&2; exit 1; fi
case "$(cat "$SRC")" in *"const PLUGIN_ID = 'hermes-chat-vault'"*"const PLUGIN_VERSION = '0.2.2-vault'"*) ;; *) echo 'ERROR: unexpected plugin source' >&2; exit 1;; esac
HOME_DIR=${HERMES_HOME:-"$HOME/.hermes"}
if [ "${1:-}" = '--hermes-home' ]; then [ "$#" -ge 2 ] || { echo 'Provide path for --hermes-home' >&2; exit 1; }; HOME_DIR=$2; fi
[ -d "$HOME_DIR" ] || { echo "Hermes root not found: $HOME_DIR" >&2; exit 1; }
DEST_DIR="$HOME_DIR/desktop-plugins/hermes-chat-vault"
[ ! -L "$DEST_DIR" ] || { echo 'Refusing symlink destination' >&2; exit 1; }
mkdir -p "$DEST_DIR"
[ ! -e "$DEST_DIR/.hermes-package.json" ] || { echo 'Managed plugin: update via Hermes UI' >&2; exit 1; }
[ ! -e "$DEST_DIR/.git" ] || { echo 'Git-managed plugin: update via Hermes UI' >&2; exit 1; }
DEST="$DEST_DIR/plugin.js"
if [ -f "$DEST" ]; then
  grep -Fq "const PLUGIN_ID = 'hermes-chat-vault'" "$DEST" || { echo 'Different plugin in destination' >&2; exit 1; }
  cp "$DEST" "$DEST.backup-$(date +%Y%m%d-%H%M%S).bak"
fi
TMP="$DEST_DIR/plugin.js.new.$$"
trap 'rm -f "$TMP"' EXIT HUP INT TERM
cp "$SRC" "$TMP"
cmp -s "$SRC" "$TMP" || { echo 'Copy verification failed' >&2; exit 1; }
mv -f "$TMP" "$DEST"
trap - EXIT HUP INT TERM
printf 'INSTALL SUCCESS: Hermes ChatVault 0.2.2\nInstalled: %s\n' "$DEST"
