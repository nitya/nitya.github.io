---
name: add-data-item
description: >-
  Add a new item (patent, publication, talk, or project) to the personal
  knowledge platform from a URL and/or context. Fetches and parses the source,
  normalizes it to the correct schema, de-duplicates, and appends it to the
  right data/*.json file. Use for requests like "add patent <link>",
  "add this talk", or "add a publication from this DOI".
---

# Skill: add-data-item

Add a structured data item to `data/` from a URL or free-form context.

Because the website is a **pure view** of `data/`, you only edit the JSON file.
The site rebuilds from it — no manual website change is ever needed.

## When to use

Trigger phrases: "add patent <url>", "add talk <link>", "add this publication",
"add project <repo url>", "capture this to my data".

## Inputs

- A **URL** (patent page, DOI, Sessionize/SpeakerDeck page, GitHub repo, etc.), and/or
- **Context** text describing the item.
- Optionally an explicit **type**. If not given, infer it (see Type detection).

## Type detection → target file

| Type        | Signals                                                        | File                     |
| ----------- | ------------------------------------------------------------- | ------------------------ |
| patent      | patents.google.com, USPTO, "patent", patent number            | `data/patents.json`      |
| publication | doi.org, ACM/IEEE, Google Scholar, "paper"/"journal"          | `data/publications.json` |
| talk        | sessionize.com, speakerdeck.com, youtube talk, conference     | `data/talks.json`        |
| project     | github.com repo, project/portfolio link                       | `data/projects.json`     |

If ambiguous, ask the user which type.

## Procedure

1. **Fetch** the URL (use the available web-fetch/search tools). If only context
   was given, work from that.
2. **Extract** fields and map them to the target schema (see below). Preserve the
   canonical source URL in `url`.
3. **Generate an `id`**: lowercase, kebab-case, stable and human-readable
   (e.g. `pub-2024-edge-caching`, `talk-2024-agentic-workflows`,
   patent number for patents). Must be unique within the file.
4. **De-duplicate**: read the target JSON; if an item with the same `id` or same
   `url`/`doi` already exists, switch to the `update-data-item` skill instead of
   adding a duplicate.
5. **Append** the new object to the array and write the file with 2-space indent.
6. **Validate**: run `cd site && npm run build`. The Zod schema in
   `site/src/content.config.ts` must accept the item (green build). Fix any
   schema violations before finishing.
7. **Report** what was added (type, id, title) and remind that the site will
   rebuild from the data on the next deploy.

## Schemas (mirror external canonical sources)

Match `site/src/content.config.ts`. Required fields must be present; unknown
optional fields may be omitted or set to `null`.

**patents.json** — `{ id, title, abstract?, inventors[], assignee?, filingDate?, grantDate?|null, status: granted|pending|expired, url, tags[] }`

**publications.json** — `{ id, title, authors[], venue?, year:int, type: journal|conference|book|preprint, doi?|null, url, abstract?, citationCount?|null, tags[] }`

**talks.json** — `{ id, title, event, date, location?|null, url, slidesUrl?|null, videoUrl?|null, description?, tags[] }`

**projects.json** — `{ id, name, description, role?|null, url?|null, repo?|null, tech[], startDate?|null, endDate?|null, status: active|archived|completed, tags[] }`

Dates are ISO strings (`YYYY-MM-DD`); publication `year` is an integer.

## Guardrails

- Never invent facts. If a required field can't be determined, ask the user.
- Keep `data/` as the only source of truth — do not hand-edit files under `site/`.
- Always leave the build green.
