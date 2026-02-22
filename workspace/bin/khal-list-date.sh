#!/usr/bin/env bash
# Usage: khal-list-date.sh <relative-date>
# Example: khal-list-date.sh tomorrow
set -euo pipefail
TZ="America/New_York"
REL=${1:-today}
# Resolve relative date to ISO YYYY-MM-DD in Boston time
TARGET=$(TZ="$TZ" date -d "$REL" +%F)
vdirsyncer sync
khal list "$TARGET" "$@"
