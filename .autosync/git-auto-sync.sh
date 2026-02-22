#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="/home/odominguez7/.openclaw"
LOG_FILE="${REPO_DIR}/.autosync/autosync.log"

mkdir -p "${REPO_DIR}/.autosync"
cd "${REPO_DIR}"

if [[ ! -d ".git" ]]; then
  exit 0
fi

exec 9>"${REPO_DIR}/.git/autosync.lock"
if ! flock -n 9; then
  exit 0
fi

git add -A
if git diff --cached --quiet; then
  exit 0
fi

STAMP="$(date -u +"%Y-%m-%d %H:%M:%SZ")"
if git commit -m "auto-sync: ${STAMP}" >>"${LOG_FILE}" 2>&1; then
  git push origin HEAD >>"${LOG_FILE}" 2>&1 || true
fi
