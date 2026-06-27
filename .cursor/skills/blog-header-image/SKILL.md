---
name: blog-header-image
description: >-
  Generate and resize Bizkit blog header images via Gemini Images (browser MCP).
  Finds folders missing PNG/JPG, builds prompt from index-en.qmd, submits to
  Gemini, downloads, saves as title_YYYYMMDD.png, resizes to 664x548. Use when
  the user asks for blog images, title images, or Phase 2 of the blog pipeline.
disable-model-invocation: true
---

# Blog Header Image

Generate `title_YYYYMMDD.png` (664×548) for a blog folder using Gemini Images + local scripts.

## Prerequisites

- `blog/YYYYMMDD/index-en.qmd` exists
- Chrome tab available for **user-browsermcp**
- Python venv at `.venv/` with Pillow installed

## Find Target Folder

**Single folder:** user provides `YYYYMMDD`.

**Next missing image** (batch mode):

```bash
for dir in $(ls -1 blog/ | grep -E '^[0-9]{8}$' | sort); do
  has=$(find "blog/$dir" -maxdepth 1 \( -iname '*.jpg' -o -iname '*.png' \) | head -1)
  qmd="blog/$dir/index-en.qmd"
  if [ -z "$has" ] && [ -f "$qmd" ]; then echo "$dir"; break; fi
done
```

Or:

```bash
.venv/bin/python scripts/blog_header_helpers.py needs-image YYYYMMDD
```

## Workflow (one folder at a time)

Process folders **sequentially**. Do not batch browser submissions.

### 1. Build prompt

```bash
.venv/bin/python scripts/blog_header_helpers.py copy-prompt YYYYMMDD
```

This writes `/tmp/blog_prompt_YYYYMMDD.txt` and copies to clipboard.

The helper builds a **single-line** prompt (no newlines) with:
- Standard header-image instructions
- **No public figures** clause (avoids Gemini policy blocks)
- Blog body from `index-en.qmd` (excludes YAML front matter and Pageviews HTML)

### 2. Record download baseline

```bash
ls -t ~/Downloads/Gemini_Generated_Image*.png 2>/dev/null | head -1 \
  > /tmp/gemini_baseline.txt
```

### 3. Submit to Gemini Images

1. Navigate: `https://gemini.google.com/images`
2. Snapshot → find "Describe your image" textbox ref
3. `browser_type` with **`submit: true`** and the single-line prompt text
   - Read prompt from `/tmp/blog_prompt_YYYYMMDD.txt` if needed
   - Do **not** use multi-line text (triggers early send)
   - Clipboard paste is unreliable — prefer `browser_type`

### 4. Wait for generation

Poll with `browser_wait` (15–30s intervals) until:
- Generated image visible, OR
- "Download full size image" / lightbox available

If blocked for public figures: retry — prompt already includes abstract-only instruction.

### 5. Download

1. Click generated image → open lightbox (more reliable than inline download)
2. Click **Download full size image** (top-right of image)
3. Wait 3–5s for file in `~/Downloads/Gemini_Generated_Image*.png`

### 6. Move, rename, resize

```bash
scripts/save_gemini_newest.sh YYYYMMDD "$(cat /tmp/gemini_baseline.txt)"
```

Or manually:

```bash
.venv/bin/python scripts/blog_header_helpers.py finalize YYYYMMDD
```

Or fallback:

```bash
LATEST=$(ls -t ~/Downloads/Gemini_Generated_Image*.png | head -1)
mv "$LATEST" "blog/YYYYMMDD/title_YYYYMMDD.png"
.venv/bin/python scripts/resize_image.py "blog/YYYYMMDD"
```

### 7. Verify

```bash
file "blog/YYYYMMDD/title_YYYYMMDD.png"
# Expect: PNG image data, 664 x 548
```

Confirm front matter already references `./title_YYYYMMDD.png` (set in Phase 1).

## Batch Mode

Repeat workflow for each folder missing an image. Report progress:

```
Done: YYYYMMDD (664×548)
Next: YYYYMMDD
Remaining: N folders
Failed: [list with reason]
```

## Failure Handling

| Problem | Action |
|---------|--------|
| Early submit / truncated prompt | Rebuild with helper (single-line) |
| Policy block (politician/celebrity) | Prompt includes abstract-only clause; retry |
| No download after click | Open lightbox first; check `~/Downloads` |
| Wrong dimensions after resize | Re-run `scripts/resize_image.py blog/YYYYMMDD` |

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `scripts/blog_header_helpers.py` | `copy-prompt`, `finalize`, `needs-image` |
| `scripts/save_gemini_newest.sh` | Move newest download + resize |
| `scripts/resize_image.py` | Scale to 664×548, rename to `title_YYYYMMDD.*` |
