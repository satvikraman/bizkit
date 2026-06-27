---
name: blog-whatsapp-post
description: >-
  Post Bizkit blog announcements to WhatsApp Channels via browser MCP.
  Opens each language channel, pastes the title image and approved caption,
  sends the post. Use for Phase 7 after WhatsApp templates are approved, or
  when the user asks to post blog messages to WhatsApp.
disable-model-invocation: true
---

# Blog WhatsApp Posting

Post image + caption to each BizKit WhatsApp Channel using **user-browsermcp** on an logged-in `web.whatsapp.com` tab.

## Accepted Workflow (human + agent)

1. Agent opens channel URL via browser MCP
2. Agent runs `copy-image` → **user Cmd+V** in compose box
3. Agent runs `copy-caption` (auto-formats spacing) → **user Cmd+V** in "Type an update"
4. User reviews preview → says **"send"** → agent clicks **Send 1 selected**

Browser MCP cannot reliably inject Cmd+V into Chrome; the two paste steps stay manual by design.

- Chrome tab on `https://web.whatsapp.com/` with user logged in
- User is **admin** of all six BizKit channels (compose box visible)
- Approved messages from Phase 5/6 (or saved to `/tmp/whatsapp_YYYYMMDD/`)
- Title image exists: `blog/YYYYMMDD/title_YYYYMMDD.png`

## Channel Map

| Lang | Channel name | Direct URL |
|------|--------------|------------|
| en | BizKit - English | `https://web.whatsapp.com/accept?channel_invite_code=0029VbAwFip59PwKCh7Wwi1F` |
| hi | BizKit - हिंदी | `https://web.whatsapp.com/accept?channel_invite_code=0029VbAl8ug4o7qMtawhPL30` |
| ta | BizKit - தமிழ் | `https://web.whatsapp.com/accept?channel_invite_code=0029VbASzeEAu3aWiQPlHp04` |
| te | BizKit - తెలుగు | `https://web.whatsapp.com/accept?channel_invite_code=0029VbB6WYg4tRropQUeJ02D` |
| kn | BizKit - ಕನ್ನಡ | `https://web.whatsapp.com/accept?channel_invite_code=0029Vb6AO5kICVfpNSqdmB2l` |
| de | BizKit - Deutsch | `https://web.whatsapp.com/accept?channel_invite_code=0029VbBNPJ384Om4uNmKLF1r` |

Post in order: **en → hi → ta → te → kn → de**.

Helper script:

```bash
.venv/bin/python scripts/whatsapp_post_helpers.py list-channels
.venv/bin/python scripts/whatsapp_post_helpers.py channel-url --lang en
.venv/bin/python scripts/whatsapp_post_helpers.py copy-image YYYYMMDD
.venv/bin/python scripts/whatsapp_post_helpers.py handoff YYYYMMDD
```

## Inputs

```
folder: YYYYMMDD
messages:
  en: "⭐ *Title* ..."
  hi: "..."
  ta: "..."
  te: "..."
  kn: "..."
  de: "..."
```

Save messages before posting (optional but recommended):

```bash
.venv/bin/python scripts/whatsapp_post_helpers.py save-message YYYYMMDD --lang en --text "$(cat <<'EOF'
<approved English message>
EOF
)"
```

## Post Format (matches live channels)

Each post is **one image message with caption**. Use this spacing (blank line before section headers):

```
⭐ *<TITLE>*
_<SUBTITLE>_

📌 *Main Points*
* <bullet 1>
* <bullet 2>
...

📜 Read the full story
https://bizkit.co.in/blog/YYYYMMDD/index-<lang>.html
```

WhatsApp renders `*bold*`, `_italic_`, and emoji. Use the exact approved text from Phase 5/6.

**All six languages** (en, hi, ta, te, kn, de) use the same spacing rules. The `format_whatsapp_message` helper keys off the `📌` and `📜` emoji prefixes, which are identical across languages.

Before posting, run `format-message` (or `save-message` / `copy-caption`) to enforce blank lines before `📌` and `📜`.

## Workflow (per language)

Process **one channel at a time**. Never post without explicit user approval.

### 1. Open channel

```text
browser_navigate → channel URL for this language
browser_wait → 8–10s (WhatsApp sync)
browser_snapshot
```

Verify banner shows correct channel name (e.g. `BizKit - English 32 followers`) and compose box:

```text
textbox "Type a message to BizKit - English"
button "Attach"
```

Alternative navigation: click **Channels** sidebar → click channel button by name.

### 2. Copy image to clipboard

```bash
.venv/bin/python scripts/whatsapp_post_helpers.py copy-image YYYYMMDD
```

Uses macOS `osascript` to put `title_YYYYMMDD.png` on the clipboard.

### 3. Paste image into compose box

1. Copy image to clipboard:

```bash
.venv/bin/python scripts/whatsapp_post_helpers.py copy-image YYYYMMDD
```

2. `browser_snapshot` → click compose textbox (or inner `paragraph` ref)
3. `browser_press_key` → `Meta+v`

4. Wait 3s and snapshot. Look for image preview above compose area and **Send** button replacing Voice message.

**If Meta+v does not show a thumbnail** (common browser MCP limitation — the extension cannot always inject clipboard paste into Chrome):

- Tell user: *"Image is on your clipboard — please click the compose box and press Cmd+V once."*
- Wait for user confirmation before continuing.

Do **not** use Attach → Photos & videos unless the user prefers the file picker (browser MCP cannot drive it).

### 4. Paste caption (after image preview is visible)

**CRITICAL:** WhatsApp Web sends on **Enter**. Never use multi-line `browser_type`.

1. Copy caption to clipboard:

```bash
.venv/bin/python scripts/whatsapp_post_helpers.py copy-caption YYYYMMDD --lang de
```

2. Click compose/caption area below the image preview
3. `browser_press_key` → `Meta+v` (paste full caption in one shot)

If Meta+v fails for text too, ask user to Cmd+V the caption.

Do **not** click Send until user explicitly approves.

### 5. Send

1. `browser_snapshot` → find **Send** button (replaces "Voice message" when content exists)
2. `browser_click` Send

If no Send button visible, try `browser_press_key` → `Enter` (only when caption box is focused).

### 6. Verify

Snapshot the channel feed. Confirm new post shows:
- Title image thumbnail
- Caption with ⭐ title, 📌 Main Points, and blog link

Wait 3s before opening next channel.

## Batch: All Six Languages

```
For lang in [en, hi, ta, te, kn, de]:
  1. Open channel URL
  2. copy-image YYYYMMDD
  3. Paste image (Meta+v)
  4. Type messages[lang] caption
  5. Send
  6. Verify
  Report: "Posted en ✓, hi ✓, ..."
```

Stop immediately on failure and report which language failed.

## Safety Rules

- **Never post without explicit user approval** of all six templates
- Default: post one language, confirm with user, continue
- If user says **"post all"**, run all six sequentially without pauses
- Do not post test/draft content to live channels
- Same `title_YYYYMMDD.png` is reused for all languages (only caption differs)

## Failure Handling

| Problem | Action |
|---------|--------|
| WhatsApp still loading | Wait 10s, snapshot again |
| Not logged in / QR screen | Stop — ask user to log in |
| Compose box missing | User may not be channel admin; stop |
| Clipboard paste fails | Ask user to paste image manually (Cmd+V), continue with caption |
| Attach file picker opens | Cannot automate — use clipboard paste instead |
| Caption sent line-by-line | Never use `\n` in `browser_type` — paste via `copy-caption` + Meta+v |
| Image paste fails | User Cmd+V manually, or Attach → Photos & videos |
| Send button not found | Snapshot; look for Send vs Voice message button |

## Integration

Called from **Phase 7** in `.github/agents/blog-bot.agent.md` after Phase 6 templates are approved.

Handoff from orchestrator:

```json
{
  "folder": "YYYYMMDD",
  "messages": { "en": "...", "hi": "...", ... }
}
```
