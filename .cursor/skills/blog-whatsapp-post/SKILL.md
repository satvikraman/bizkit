---
name: blog-whatsapp-post
description: >-
  Show Bizkit blog announcements for WhatsApp Channels so the user can post
  them manually in WhatsApp Web. Use for Phase 7 after WhatsApp templates are
  approved, or when the user asks to post blog messages to WhatsApp.
disable-model-invocation: true
---

# Blog WhatsApp Posting

Show the WhatsApp channel post for each BizKit language, then let the user post it manually in WhatsApp Web.

## Accepted Workflow (human + agent)

1. Agent cats the previously saved WhatsApp message text for that language
2. User copies the message from the terminal and pastes it into WhatsApp Web manually
3. User sends the post in WhatsApp Web

No browser integration is required in Phase 7; posting stays manual by design.

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

When posting manually, use `cat` to display each previously saved message before copying it into WhatsApp Web.

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

### 1. Show the saved message

Use `cat` on the previously stored WhatsApp message for that language so the user can copy it manually.

### 2. User posts manually

The user opens WhatsApp Web, pastes the image and caption manually, and sends the post.

## Batch: All Six Languages

```
For lang in [en, hi, ta, te, kn, de]:
  1. cat the saved message for lang
  2. User copies and pastes the image and caption in WhatsApp Web
  Report: "Prepared en ✓, hi ✓, ..."
```

Stop immediately on failure and report which language failed.

## Safety Rules

- **Never post without explicit user approval** of all six templates
- Default: prepare one language, confirm with user, continue
- If user says **"post all"**, prepare all six sequentially without pauses; the user still posts them manually
- Do not post test/draft content to live channels
- Same `title_YYYYMMDD.png` is reused for all languages (only caption differs)

## Failure Handling

| Problem | Action |
|---------|--------|
| User wants a pasted message | Show the stored text with `cat`, then let the user paste manually |
| User wants channel details | Use `list-channels` or `channel-url` to find the right channel name or URL |

## Integration

Called from **Phase 7** in `.github/agents/blog-bot.agent.md` after Phase 6 templates are approved.

Handoff from orchestrator:

```json
{
  "folder": "YYYYMMDD",
  "messages": { "en": "...", "hi": "...", ... }
}
```
