#!/usr/bin/env bash
set -euo pipefail

SHEET_ID="${1:-1JZafCoPUILYq3R3E5lJkJAhnevvj2UkQWZkrlML55hM}"
RANGE="${2:-'8) Overview'!A1:B5}"

# Quick check that gog has a valid account + can read a small range.

echo "== gog auth list =="
gog auth list --no-input

echo

echo "== sheets read test =="
echo "Sheet: $SHEET_ID"
echo "Range: $RANGE"
gog sheets get "$SHEET_ID" "$RANGE" --plain --no-input | sed -n '1,10p'

echo

echo "OK: Sheets connection looks good."
