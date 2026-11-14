#!/bin/sh
set -eu
HOME_DIR=${HERMES_HOME:-"$HOME/.hermes"}
if [ "${1:-}" = '--hermes-home' ]; then [ "$#" -ge 2 ] || { echo 'Provide path for --hermes-home' >&2; exit 1; }; HOME_DIR=$2; fi
DEST_DIR="$HOME_DIR/desktop-plugins/hermes-chat-vault"
DEST="$DEST_DIR/plugin.js"
[ ! -L "$DEST_DIR" ] || { echo 'Refusing symlink destination' >&2; exit 1; }
[ ! -e "$DEST_DIR/.hermes-package.json" ] || { echo 'Managed plugin: use Hermes UI' >&2; exit 1; }
[ ! -e "$DEST_DIR/.git" ] || { echo 'Git-managed plugin: use Hermes UI' >&2; exit 1; }
if [ ! -f "$DEST" ]; then echo 'ChatVault not installed'; exit 0; fi
grep -Fq "const PLUGIN_ID = 'hermes-chat-vault'" "$DEST" || { echo 'Unexpected plugin identity; refusing remove' >&2; exit 1; }
grep -Fq 'HERMES_CHATVAULT_FORK_V1' "$DEST" || { echo 'Unexpected plugin identity; refusing remove' >&2; exit 1; }
rm -- "$DEST"
echo 'UNINSTALL SUCCESS: manual ChatVault removed.'
