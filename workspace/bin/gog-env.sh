#!/usr/bin/env bash
set -euo pipefail

# Source this file:
#   source /home/odominguez7/.openclaw/workspace/bin/gog-env.sh
#
# Provides a ready-to-use gog CLI environment for Omar's Google account.

export PATH="/home/odominguez7/.local/bin:${PATH}"

# Default Google account for gog commands
export GOG_ACCOUNT="omar.dominguez7@gmail.com"

# Keyring password for headless token storage (avoids TTY prompts)
_PASS_FILE="/home/odominguez7/.openclaw/workspace/secrets/gog-keyring-password.txt"
if [[ -f "$_PASS_FILE" ]]; then
  export GOG_KEYRING_PASSWORD="$(cat "$_PASS_FILE")"
else
  echo "Missing keyring password file: $_PASS_FILE" 1>&2
  echo "Fix: create it with:" 1>&2
  echo "  mkdir -p /home/odominguez7/.openclaw/workspace/secrets" 1>&2
  echo "  head -c 48 /dev/urandom | base64 > $_PASS_FILE" 1>&2
  echo "  chmod 600 $_PASS_FILE" 1>&2
  return 1 2>/dev/null || exit 1
fi

# Optional: point at our stored OAuth client JSON (helpful if re-auth is needed)
export GOG_OAUTH_CLIENT_JSON="/home/odominguez7/.openclaw/workspace/secrets/gog-client-secret.json"
