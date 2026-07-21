# AGENTS.md

Guidance for coding agents working in this repository.

## What this repo is

A **data-first personal knowledge platform**. The structured data in **`data/`**
is the single source of truth. The **`site/`** folder is an [Astro](https://astro.build)
static website that is only a *view* of that data, deployed to GitHub Pages.

```
data/            ← source of truth (JSON, one file per source)
  profile.json     (single object → schema.org Person)
  patents.json     (array)
  publications.json
  talks.json
  projects.json
site/            ← Astro static site (a view of data/)
  src/content.config.ts   Zod schemas + content-layer loaders for data/*.json
  src/pages/              Home (/), About (/about), Content (/content)
.github/
  skills/        ← runnable skills to maintain the data (see below)
  workflows/     ← GitHub Pages deploy
  PLAN.md        ← phased build plan
```

## Golden rules

1. **`data/` is the source of truth.** To change site content, edit the JSON in
   `data/` — never hard-code content into `site/`. The site rebuilds from data.
2. **Keep the build green.** After changing `data/` or `site/`, run
   `cd site && npm run build`. Data must satisfy the Zod schemas in
   `site/src/content.config.ts`.
3. **Stable ids.** Every item has a unique, human-readable `id`. It is the dedupe
   key — do not change it once assigned.
4. **Schemas mirror external canonical sources** (USPTO/Google Patents,
   Scholar/ACM/IEEE, Sessionize/SpeakerDeck, GitHub) and map to schema.org types
   for SEO. Preserve that mapping when adding fields.

## Skills

Repo-local skills in `.github/skills/` automate data maintenance:

- **add-patent** — bulk-import patents via the Google Patents XHR API; splits
  issued vs filed and de-dupes patent families. → `data/patents.json`.
- **add-publication** — import papers from a Google Scholar profile or DOI,
  with citation counts. → `data/publications.json`.
- **add-talk** — import talks from a Speaker Deck RSS feed, Sessionize profile,
  or a conference archive; de-dupes across sources. → `data/talks.json`.
- **add-project** — import projects from a GitHub repo, aka.ms link, or org
  README (live star/metadata via the REST API); de-dupes by repo. →
  `data/projects.json`.
- **add-data-item** — generic single-item add for any type (incl. projects).
- **update-data-item** — update/enrich an existing item.
- **research-data** — search the web for new candidate items, then hand off to add.

A request like *"add patent &lt;link&gt;"* should trigger `add-patent` (or
`add-data-item` for a one-off): parse the source, append to the matching
`data/*.json`, and validate the build. No website edit needed.

## Local development

```bash
cd site
npm install
npm run dev      # local preview
npm run build    # production build + sitemap (use this to validate data)
```

## Deployment

Pushing to `main` triggers `.github/workflows/deploy.yml`, which builds `site/`
and publishes to GitHub Pages at https://nitya.github.io. Enable Pages once via
repo Settings → Pages → Source: **GitHub Actions**.
