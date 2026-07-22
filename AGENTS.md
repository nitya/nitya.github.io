# AGENTS.md

Best practices for coding agents working in this repository.

## What this repo is

A **data-first personal knowledge platform**. The structured data in **`data/`**
is the single source of truth. The **`site/`** folder is an
[Astro](https://astro.build) static website that is only a *view* of that data,
deployed to GitHub Pages.

```
data/            ← source of truth (JSON, one file per source)
  profile.json       (single object → schema.org Person)
  patents.json       (array)
  publications.json
  talks.json
  projects.json
  training.json      (curricula + 1P-event training content)
  notifications.json (data-driven site banners)
site/            ← Astro static site (a view of data/)
  src/content.config.ts   Zod schemas + content-layer loaders for data/*.json
  src/lib/content.ts      Normalizes every collection into one card shape
  src/pages/              Home (/), About (/about), Content (/content)
  src/components/         Card, Filters, Banner, Nav, …
.devcontainer/   ← Dev Container / Codespaces config + post-create bootstrap
.github/
  skills/        ← runnable skills to maintain the data (see below)
  scripts/       ← intake.py (issue-comment data intake parser)
  workflows/     ← deploy.yml (GitHub Pages) + intake.yml (issue-comment intake)
  PLAN.md        ← phased build plan
```

## Golden rules

1. **`data/` is the source of truth.** To change site content, edit the JSON in
   `data/` — never hard-code content into `site/`. The site rebuilds from data.
2. **Keep the build green.** After changing `data/` or `site/`, run
   `cd site && npm run build`. Data must satisfy the Zod schemas in
   `site/src/content.config.ts` or the build fails.
3. **Stable ids.** Every item has a unique, human-readable `id`. It is the dedupe
   key — do not change it once assigned.
4. **Schemas mirror external canonical sources** (USPTO/Google Patents,
   Scholar/ACM/IEEE, Sessionize/SpeakerDeck/SlideShare, GitHub) and map to
   schema.org types for SEO. Preserve that mapping when adding fields.

## Adding a new content *type* (collection)

A type like `training` touches several files — keep them in sync:

1. `data/<type>.json` — the data (array of items, each with a stable `id`).
2. `site/src/content.config.ts` — a Zod `defineCollection` + add it to the
   exported `collections` object.
3. `site/src/lib/content.ts` — extend the `ContentItem` union + `typeLabels`,
   load the collection in `getAllContentItems`, and normalize each item into the
   common card shape.
4. `site/src/components/Filters.astro` — add a type button.
5. `site/src/pages/content/index.astro` — add a `typeCopy` header entry and a
   `schemaType` mapping.

## Best practices for editing data

- **Never fabricate specifics.** Titles, dates, and contribution details must
  come from a real source (an API, page metadata/JSON-LD, or the user). If a
  source is bot-protected, use the `web_fetch` tool and read `<meta>` / JSON-LD;
  don't guess. Prefer enriching an existing item over inventing a duplicate.
- **De-duplicate.** The same item can appear across sources — match on normalized
  title + date (and `id`) and merge rather than creating a second row.
- **Tags are lowercase kebab-case** topic keywords used for search/filter. Reuse
  existing tags where possible (e.g. `for-beginners`, `msft-workshops`,
  `30DaysOf`, `model-mondays`).
- **Naming rule: always use `microsoft-foundry`, never `azure-ai-foundry`.**
  Normalize both tags and prose to `Microsoft Foundry`.
- **`url` fields must be valid URLs** (the schema enforces it). For a source with
  no per-item link, fall back to a stable canonical URL (profile/search page).
- **GitHub metadata:** read live values (stars, description, dates) from the
  unauthenticated REST API — `curl https://api.github.com/repos/<owner>/<repo>`.
  An authenticated `gh` token is SAML-blocked for `microsoft`/`Azure` orgs (403);
  anonymous access to the same public data works.

## Skills

Repo-local skills in `.github/skills/` automate data maintenance:

- **add-patent** — bulk-import patents via the Google Patents XHR API; splits
  issued vs filed and de-dupes patent families. → `data/patents.json`.
- **add-publication** — import papers from a Google Scholar profile or DOI,
  with citation counts. → `data/publications.json`.
- **add-talk** — import talks from a Speaker Deck RSS feed, Sessionize profile,
  SlideShare deck, or a conference archive; de-dupes across sources. →
  `data/talks.json`.
- **add-project** — import projects from a GitHub repo, aka.ms link, or org
  README (live star/metadata via the REST API); de-dupes by repo. →
  `data/projects.json`.
- **add-data-item** — generic single-item add for any type (incl. training).
- **update-data-item** — update/enrich an existing item.
- **research-data** — search the web for new candidate items, then hand off to add.

A request like *"add patent &lt;link&gt;"* should trigger `add-patent` (or
`add-data-item` for a one-off): parse the source, append to the matching
`data/*.json`, and validate the build. No website edit needed.

## Issue-comment data intake

`.github/workflows/intake.yml` turns a permanent issue (labelled `data-intake`)
into an inbox. When the owner comments `add <type> <url>` lines (one per line,
with an optional `| note`), `.github/scripts/intake.py` fetches metadata,
appends normalized records to the right `data/*.json`, validates the build,
commits to `main`, replies on the issue, and dispatches the deploy workflow.

- Supported types: `workshop`/`session`/`lab`/`training`/`curriculum`/`course`
  → `training.json`; `project` → `projects.json`; `talk` → `talks.json`.
- Patents/publications are intentionally **not** auto-added (they need the richer
  parsing in the CLI skills) — the script reports them as skipped.
- When editing the intake, keep the parser's normalization consistent with the
  rules above (stable ids, dedupe, `microsoft-foundry` naming, valid URLs) and
  keep the two builders' output valid against the Zod schemas.

## Local development

```bash
cd site
npm install
npm run dev      # local preview at http://localhost:4321
npm run build    # production build + sitemap (use this to validate data)
```

### Codespaces / Dev Container

Opening the repo in a Codespace runs `.devcontainer/post-create.sh`, which
installs `site/` dependencies and runs a validating build. Use
`npm run dev -- --host` so the dev server is reachable on the forwarded port 4321.

## Deployment

Pushing to `main` triggers `.github/workflows/deploy.yml`, which builds `site/`
and publishes to GitHub Pages at https://nitya.github.io. Enable Pages once via
repo Settings → Pages → Source: **GitHub Actions**.
