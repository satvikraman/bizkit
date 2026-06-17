#!/bin/bash
# Save latest Gemini download to blog title image and resize.
# Usage: save_gemini_title.sh YYYYMMDD
set -euo pipefail
FOLDER="$1"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$REPO/blog/$FOLDER/title_${FOLDER}.png"
for i in $(seq 1 15); do
  LATEST=$(find ~/Downloads -name 'Gemini_Generated_Image*.png' -mmin -2 2>/dev/null | head -1)
  if [ -n "$LATEST" ]; then
    cp "$LATEST" "$DEST"
    "$REPO/.venv/bin/python" "$REPO/scripts/resize_image.py" "blog/$FOLDER"
    file "$DEST"
    exit 0
  fi
  sleep 2
done
echo "ERROR: no recent Gemini download for $FOLDER" >&2
exit 1
