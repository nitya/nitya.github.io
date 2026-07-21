---
name: add-patent
description: >-
  Add one or more patents to the personal knowledge platform from a Google
  Patents link, a patent number, or an inventor search. Uses the Google Patents
  XHR query API to fetch structured records, distinguishes ISSUED (granted) from
  FILED (application) patents, de-duplicates patent families across
  jurisdictions, normalizes to the patents schema, and appends to
  data/patents.json. Use for "add patent <link>", "add my latest patents", or
  "refresh patents for inventor <name>".
---

# Skill: add-patent

Add patent records to `data/patents.json`. The website is a pure view of
`data/`, so you only ever edit the JSON — the site rebuilds from it.

## Destination

Always `data/patents.json`. Schema (see `site/src/content.config.ts`):

```
{ id, title, abstract?, inventors[], assignee?, filingDate?, grantDate?|null,
  status: granted|pending|expired, url, tags[] }
```

- `id` = the publication number (e.g. `US10728618B2`). Stable and unique.
- `status`: `granted` when the record has a grant date; otherwise `pending`
  (the user calls these "filed"). Use `expired` only if explicitly known.
- `url` = `https://patents.google.com/patent/<id>/en`.
- Dates are ISO `YYYY-MM-DD`.

## Sources & parsing

### A. A single patent link or number
Fetch `https://patents.google.com/patent/<NUMBER>/en`. Read title, inventors,
assignee, filing/priority date, and grant/publication date. If a grant date is
present → `status: granted`.

### B. Inventor search (bulk) — Google Patents XHR API
This is JS-rendered in the browser; use the JSON XHR endpoint instead. The `url`
query param is the URL-encoded inner query string:

```bash
# One page of up to 100 results. Loop page=0,1,2,... until you have them all.
curl -sL --max-time 25 \
  "https://patents.google.com/xhr/query?url=inventor%3DNitya%2BNarasimhan%26num%3D100%26page%3D0&exp=" \
  -H "User-Agent: Mozilla/5.0" -o page0.json
```

Also run the query for **known misspellings** of the inventor name (e.g.
`Nitya Narsimhan`) — Google indexes them separately and each surfaces different
patents.

Parse each result at `results.cluster[].result[]`:
- `id` → `patent/US10728618B2/en` (take the middle segment as the number).
- `patent.title` (strip HTML tags and `&hellip;` truncation — refetch the patent
  page for the full title if truncated).
- `patent.grant_date` — **present ⇒ issued/granted; absent ⇒ filed/pending.**
- `patent.filing_date`, `patent.priority_date`, `patent.assignee`.

```python
import json, re
d = json.load(open("page0.json"))
for c in d["results"]["cluster"]:
    for r in c["result"]:
        p = r["patent"]; num = r["id"].split("/")[1]
        issued = bool(p.get("grant_date"))
        title = re.sub("<.*?>", "", p.get("title", "")).strip()
        print(num, "granted" if issued else "filed", p.get("grant_date") or p.get("filing_date"), p.get("assignee"), title)
```

Note: the XHR response can be latin-1; if a `curl` output fails to decode as
UTF-8, read it with `encoding="latin-1"`. The plain
`inventor=<name>` search sometimes omits patents that Google Scholar lists under
the inventor (e.g. `US7613156B2`) — cross-check the Scholar profile and look up
any missing numbers directly via the single-patent path.

## De-duplication of patent families

The same invention appears as multiple records across jurisdictions
(`US...`, `EP...B1`, `WO...`, `JP...`, `BR...`, `AU...B2`) and as an application
(`US2013...A1`) plus its later grant (`US...B2`). Collapse each family to **one**
item:

1. Group by shared `priority_date` + near-identical title.
2. Prefer the **granted US** member (a `B1`/`B2` number). If no US grant, prefer
   any granted member (`B1`/`B2`), else the earliest application.
3. For a family that is still only an application, keep the **latest filing** and
   set `status: pending`.

When the user asks for "N issued patents", count distinct granted families
(not per-jurisdiction records).

## Procedure

1. Fetch via A or B above. For bulk, page through all results and run every name
   spelling.
2. De-duplicate families to a clean set; split into issued vs filed.
3. Map to the schema. Write a concise one-sentence `abstract` from the title if
   the full abstract isn't fetched. Add lowercase kebab `tags` from the topic
   (e.g. `ad-hoc-networks`, `context-aware`, `advertising`, `mobile`).
4. Read `data/patents.json`; skip any `id` already present (switch to
   `update-data-item` to refresh an existing one).
5. Append, write with 2-space indent, newest first.
6. Validate: `cd site && npm run build` must stay green.
7. Report added ids, and the issued/filed split.

## Guardrails

- Never invent a patent number, date, or assignee. Verify from the source.
- One family = one item. Don't inflate counts with foreign counterparts.
- `data/` is the only source of truth; never hand-edit `site/`.
