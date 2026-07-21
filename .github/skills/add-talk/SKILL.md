---
name: add-talk
description: >-
  Add one or more talks to the personal knowledge platform from a Speaker Deck
  profile/deck, a Sessionize speaker profile, a conference page, or a talks
  archive. Parses the Speaker Deck RSS feed for titles/dates/links, Sessionize
  for canonical session URLs and abstracts, and conference listings for
  event/location/slides. De-duplicates across sources, normalizes to the talks
  schema, and appends to data/talks.json. Use for "add talk <link>", "import my
  Speaker Deck talks", "import my Sessionize sessions", or "dedup my talks".
---

# Skill: add-talk

Add talk records to `data/talks.json`. The website is a pure view of `data/`, so
you only edit the JSON — the site rebuilds from it.

## Destination

Always `data/talks.json`. Schema (see `site/src/content.config.ts`):

```
{ id, title, event, date, location?|null, url, slidesUrl?|null, videoUrl?|null,
  description?, tags[] }
```

- `id` = kebab-case, stable: `talk-<year>-<slug>` (e.g. `talk-2025-agent-factories`).
- `date` is ISO `YYYY-MM-DD` (required). If only a month/year is known, use the
  event's start date; if only a year, use `YYYY-01-01` and note the approximation.
- `event` (required): the conference/series name. `url` (required): the deck,
  session, or event page. `slidesUrl`/`videoUrl` when available.

## Sources & parsing

### A. Speaker Deck profile (bulk) — RSS feed
The profile HTML is JS-heavy; use the RSS feed instead — it's clean XML with one
`<item>` per deck:

```bash
curl -sL --max-time 25 "https://speakerdeck.com/nitya.rss" -o sd.rss
```

```python
import re, html
h = open("sd.rss", encoding="utf-8", errors="replace").read()
for it in re.findall(r"<item>(.*?)</item>", h, re.S):
    g = lambda tag: (re.search(rf"<{tag}>(.*?)</{tag}>", it, re.S) or [None, ""])[1]
    title = html.unescape(g("title")).strip()
    link  = g("link").strip()          # -> slidesUrl AND url
    pub   = g("pubDate").strip()       # RFC-822, e.g. "Tue, 30 Jun 2026 ..." -> date
    print(title, "|", pub, "|", link)
```

Convert `pubDate` (RFC-822) to ISO `YYYY-MM-DD`. For a Speaker Deck deck, set both
`url` and `slidesUrl` to the deck link. Infer `event` from the title where it's
embedded (e.g. "MSIgnite Lab 516 ..." → Microsoft Ignite; "[AITour 26] ..." →
Microsoft AI Tour; "Model Mondays S2E13 ..." → Model Mondays series).

### B. A single talk link
Fetch the Sessionize/SpeakerDeck/YouTube/conference page and read title, event,
date, location, and any slides/video links.

### C. Sessionize speaker profile — session catalog
A Sessionize profile (`https://sessionize.com/<handle>/`) is a catalog of
**reusable session abstracts**, not dated appearances. It's the best source for a
canonical talk `url`, a clean `title`, and a real `description`, but it usually
has **no date/event/location**.

```bash
curl -sL --max-time 20 "https://sessionize.com/nitya/" -H "User-Agent: Mozilla/5.0" -o sz.html
grep -oE '/s/nitya/[a-z0-9-]+/[0-9]+' sz.html | sort -u   # canonical session links
```

Each session link is `https://sessionize.com/s/<handle>/<slug>/<id>` — use it as
`url` and read the adjacent abstract as `description`. Because there's no date,
**do not fabricate one**: either (a) attach the abstract to a dated appearance you
already have from Speaker Deck / an event page (same title → enrich that item's
`description`/`url`), or (b) ask the user for the date+event before adding a new
talk. Prefer enriching over creating date-less duplicates.

### D. A talks archive page (older talks)
Conference listing pages (e.g. a Google Sites talks archive) render as markdown
with lines like:
`**Title** | Event, Mon DD, City, ST. (N attendees) | slides`.
Extract `title`, `event`, `location` (City, ST), `date` (from the "Mon DD" and the
page's year), and `slidesUrl`/`videoUrl` from the linked words. When only a month
is given, use the event's start date.

## Tags & description

- `tags`: lowercase kebab topic keywords from the title/event
  (`ai`, `agents`, `azure`, `microsoft-foundry`, `flutter`, `web`, `community`,
  `keynote`). Use **`microsoft-foundry`**, never `azure-ai-foundry`.
- `description`: one concise sentence; write it from the title if the source has
  no abstract. Never fabricate specifics.

## De-duplication

The same talk shows up across sources: a Speaker Deck deck, a Sessionize abstract,
and a conference listing can all describe one appearance — and a recurring talk
(same title given at several events) is a **separate** item per event/date.

Rules:
1. **Same appearance** = same normalized title **and** same event/date. Collapse to
   one item; merge fields (Speaker Deck → `slidesUrl`/`date`, Sessionize →
   `description`/`url`, event page → `event`/`location`/`videoUrl`).
2. **Same talk, different events** = keep one item per event with its own `date`
   (differentiate the `id`, e.g. `talk-2018-get-animated-flutter-droidcon` vs
   `-devfest`).
3. Normalize titles before comparing: lowercase, strip a leading
   `[AITour 26]` / `MSIgnite Lab 516:` / `Model Mondays S2E13:` prefix, and drop
   punctuation. A Sessionize abstract with no date should **enrich** the matching
   dated item, never add a second row.
4. Before writing, also skip any item whose `id` or `url` already exists in
   `data/talks.json` (use `update-data-item` to merge new fields into it).

## Procedure

1. Fetch via A, B, or C. For bulk, parse all items.
2. Map each to the schema; convert dates to ISO; infer `event` and `tags`.
3. Build a stable `id`. Read `data/talks.json`; skip any existing `id`/`url`
   (use `update-data-item` to add a video link or fix a field on an existing talk).
4. Append, 2-space indent, newest first.
5. Validate: `cd site && npm run build` must stay green.
6. Report added ids and count.

## Guardrails

- Never invent event names, dates, or attendance numbers.
- Prefer real slide/video URLs; omit (`null`) when unknown rather than guessing.
- `data/` is the only source of truth; never hand-edit `site/`.
