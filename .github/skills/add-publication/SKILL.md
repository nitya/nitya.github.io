---
name: add-publication
description: >-
  Add one or more publications to the personal knowledge platform from a Google
  Scholar profile, a DOI, or a paper link. Parses the Scholar profile HTML for
  titles, authors, venues, years, and citation counts, filters out patent
  entries, normalizes to the publications schema, and appends to
  data/publications.json. Use for "add publication <doi>", "import my Scholar
  papers", or "refresh citation counts".
---

# Skill: add-publication

Add publication records to `data/publications.json`. The website is a pure view
of `data/`, so you only edit the JSON — the site rebuilds from it.

## Destination

Always `data/publications.json`. Schema (see `site/src/content.config.ts`):

```
{ id, title, authors[], venue?, year:int, type: journal|conference|book|preprint,
  doi?|null, url, abstract?, citationCount?|null, tags[] }
```

- `id` = kebab-case, stable: `pub-<year>-<slug>` (e.g. `pub-2006-poi-recommendations`).
- `year` is an integer; `citationCount` an integer or null.
- `url` is required and must be a valid URL. Prefer the DOI/paper page; if none is
  known, use a Scholar search URL:
  `https://scholar.google.com/scholar?q=<url-encoded-title>`.
- `type`: map conference proceedings/workshops → `conference`, journals/transactions
  → `journal`, a thesis/dissertation or book chapter → `book`, arXiv/unpublished →
  `preprint`.

## Sources & parsing

### A. A single DOI or paper link
Fetch the DOI (`https://doi.org/<doi>`) or publisher/arXiv page. Read title,
authors, venue, year, and abstract. Set `doi` when present.

### B. Google Scholar profile (bulk)
Fetch up to 100 entries in one request:

```bash
curl -sL --max-time 25 \
  "https://scholar.google.com/citations?user=3CuE1VAAAAAJ&hl=en&cstart=0&pagesize=100" \
  -o scholar.html
```

The rows are static HTML (no JS needed). Parse each `<tr class="gsc_a_tr">`:
- title: `<a class="gsc_a_at">...</a>`
- authors then venue: the two `<div class="gs_gray">...</div>` blocks (first =
  authors, second = venue/year string)
- year: `<span class="gsc_a_h...">YYYY`
- citations: `<span class="gsc_a_ac...">N`

```python
import re, html
h = open("scholar.html", encoding="latin-1").read()  # may not be valid UTF-8
for r in re.findall(r'<tr class="gsc_a_tr">(.*?)</tr>', h, re.S):
    strip = lambda s: html.unescape(re.sub("<.*?>", "", s)).strip()
    title = strip(re.search(r'class="gsc_a_at"[^>]*>(.*?)</a>', r, re.S).group(1))
    grays = re.findall(r'class="gs_gray">(.*?)</div>', r, re.S)
    year  = re.search(r'class="gsc_a_h[^"]*"[^>]*>(\d{4})', r)
    cites = re.search(r'class="gsc_a_ac[^"]*"[^>]*>(\d+)', r)
    print(title, "|", year.group(1) if year else "", "|",
          cites.group(1) if cites else "0", "|", strip(grays[0]) if grays else "")
```

Notes:
- Read the file as `latin-1` — Scholar HTML often isn't clean UTF-8.
- Per-item deep links are JS-injected and won't appear in the static HTML; use the
  Scholar-search `url` fallback above (or match a DOI you already know).
- Split the venue string on the trailing year to get a clean `venue`.

### Filter out non-papers
A Scholar profile mixes in **patents** ("US Patent 7,613,156") and sometimes
patent applications. **Do not** add those here — route them to the `add-patent`
skill. Entries with no year (e.g. an unpublished manuscript) should be skipped
unless the user supplies a year.

## Procedure

1. Fetch via A or B. For bulk, parse all rows.
2. Drop patent entries and yearless entries. Classify `type`.
3. Build `id`, `tags` (topic keywords, lowercase kebab), and the `url` (DOI or
   Scholar search). Carry `citationCount` from Scholar when present.
4. Read `data/publications.json`; skip any existing `id`/`doi`/title (use
   `update-data-item` to refresh citation counts on an existing paper).
5. Append, 2-space indent, newest first.
6. Validate: `cd site && npm run build` must stay green.
7. Report added ids and count.

## Guardrails

- Never invent authors, venues, or citation counts.
- Patents go to `add-patent`, not here.
- `data/` is the only source of truth; never hand-edit `site/`.
