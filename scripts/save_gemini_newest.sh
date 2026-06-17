#!/bin/bash
# Copy newest Gemini download (newer than baseline) to blog title image and resize.
# Usage: save_gemini_newest.sh YYYYMMDD [baseline_file]
set -euo pipefail
FOLDER="$1"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$REPO/blog/$FOLDER/title_${FOLDER}.png"
BASELINE="${2:-$(cat /tmp/gemini_baseline.txt 2>/dev/null || true)}"

for i in $(seq 1 15); do
  NEWEST=$(ls -t ~/Downloads/Gemini_Generated_Image*.png 2>/dev/null | head -1)
  if [ -n "$NEWEST" ] && [ "$NEWEST" != "$BASELINE" ]; then
    cp "$NEWEST" "$DEST"
    "$REPO/.venv/bin/python" "$REPO/scripts/resize_image.py" "blog/$FOLDER"
    echo "$NEWEST" > /tmp/gemini_baseline.txt
    file "$DEST"
    exit 0
  fi
  sleep 2
done
echo "ERROR: no new Gemini download for $FOLDER (baseline: $BASELINE)" >&2
exit 1
