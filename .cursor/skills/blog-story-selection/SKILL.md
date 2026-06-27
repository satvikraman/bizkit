---
name: blog-story-selection
description: >-
  Select a Finshots.in story for a Bizkit blog post by target Sunday date.
  Browses archive pages, maps weekly wrapups to date windows, avoids duplicate
  topics. Use when starting a new blog post, backfilling Sundays, or when the
  user asks to pick a story from Finshots.
disable-model-invocation: true
---

# Blog Story Selection

Pick one Finshots story for a target **publication Sunday** and hand off to Phase 1 (English draft).

## Inputs

| Input | Required | Example |
|-------|----------|---------|
| `target_sunday` | Yes | `2024-11-10` or `20241110` |
| `folder` | Derived | `20241110` |

## Date Window

For publication Sunday **S**, source stories must be published **Monday through Sunday of that same week** (inclusive):

- Monday = S − 6 days
- Sunday = S

Example: post for **10-Nov-2024 (Sun)** → stories from **04-Nov-2024 (Mon)** through **10-Nov-2024 (Sun)**.

## Step 1 — Check Existing Coverage

```bash
ls blog/ | grep -E '^[0-9]{8}$' | sort
```

Read titles from nearby `blog/YYYYMMDD/index-en.qmd` files to avoid repeating topics (e.g. BRICS, gold loans, Nobel institutions).

## Step 2 — Find Finshots Weekly Wrapup

Finshots publishes a **weekly wrapup** each Friday/Saturday covering Mon–Fri stories. The quiz deadline (Saturday noon) anchors the week.

1. Browse `https://finshots.in/archive/page/N/` (N ≈ 20–30 for late 2024; adjust for current dates).
2. Search for wrapups whose quiz deadline falls on the **Saturday before or on** the target Sunday.
3. Alternatively: `site:finshots.in weekly wrapup <month> <year>` via web search.

**Mapping rule:** Wrapup with quiz deadline **Sat D** covers stories from the Mon–Fri ending that Saturday. Use it for the blog post dated the **following Sunday** (or same week's Sunday per the date window above).

## Step 3 — Select One Story

From the wrapup's 4–6 stories, pick ONE using these criteria (in order):

1. **Narrative arc** — real people, companies, or events a high schooler can follow
2. **Concept teachability** — maps cleanly to Corporate Actions, Money & Markets, or Economy & Policy
3. **Freshness** — not covered in existing Bizkit posts
4. **Timeliness** — prefer the week's most consequential story

Avoid pure market-recap or quiz-only items.

## Step 4 — Fetch Full Article

Open the chosen story URL. Extract:

- Headline, date, key facts, named people/companies
- 2–3 paragraphs of source detail for the writer

## Step 5 — Handoff

Report to the orchestrator:

```
folder: YYYYMMDD
target_sunday: YYYY-MM-DD
story_url: https://finshots.in/...
story_title: ...
category_hint: Corporate Actions | Money & Markets | Economy & Policy
source_summary: |
  3–5 bullet points of facts the English draft must use
alternatives_considered: [optional short list]
```

Then return control to **Phase 1** in `.github/agents/blog-bot.agent.md`.

## Batch Mode

When backfilling multiple Sundays:

1. List all target Sundays chronologically.
2. Skip folders where `index-en.qmd` already exists (unless user asks to redo).
3. Process one Sunday at a time — do not parallelize story selection across dates.

## Failure Handling

| Problem | Action |
|---------|--------|
| No wrapup found for week | Search Finshots archive ±2 pages; try web search with date keywords |
| All stories already covered | Pick the best alternative angle or adjacent week's top story; tell user |
| Ambiguous dates | Prefer the story whose Finshots publish date falls inside the Mon–Sun window |
