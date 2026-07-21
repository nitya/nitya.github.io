# Phase 1 — Data folder + Astro static site on GitHub Pages

## Problem & approach

Establish the Phase 1 foundation from the README: a **`data/`** folder that is the
source of truth (JSON, one file per source, array of items) and a **`site/`** folder
containing an **Astro** static website that maps those data sources into **content
collections** and renders them for humans. Deploy to **GitHub Pages** via GitHub Actions.

Because this repo is `nitya.github.io` (a user/organization Pages repo), the site
publishes at the domain root (`https://nitya.github.io/`), so `base` stays `/`.

The site ships three pages:
- **Home** — hero/intro pulled from profile data + highlights.
- **About** — rich profile page backed by `data/profile.json`.
- **Content** — a paginated gallery (one card per data item) aggregating Patents,
  Publications, Talks, and Projects, with client-side **search, sort, and filter**.

Theming: light + dark mode, modern palette in **purple / blue / gold** tones, driven
by CSS custom properties with a toggle that persists to `localStorage` and respects
`prefers-color-scheme`.

## Data model (`data/*.json`)

One JSON file per source, each an array of item objects. Schemas are designed to map
cleanly onto external canonical sources **and** onto schema.org types for SEO.

- **`data/profile.json`** (single object) → schema.org `Person`
  - `name`, `headline`, `bio`, `location`, `image`, `email?`,
    `sameAs[]` (LinkedIn/GitHub/Scholar/ORCID URLs), `worksFor?`.
- **`data/patents.json`** → schema.org `CreativeWork` (Google Patents / USPTO / Justia)
  - `id` (patent no.), `title`, `abstract`, `inventors[]`, `assignee`,
    `filingDate`, `grantDate`, `status`, `url`, `tags[]`.
- **`data/publications.json`** → schema.org `ScholarlyArticle` (Scholar / ACM / IEEE)
  - `id`, `title`, `authors[]`, `venue`, `year`, `type` (journal|conference|book),
    `doi?`, `url`, `abstract?`, `citationCount?`, `tags[]`.
- **`data/talks.json`** → schema.org `Event`/`PresentationDigitalDocument` (Sessionize / SpeakerDeck)
  - `id`, `title`, `event`, `date`, `location?`, `url`, `slidesUrl?`, `videoUrl?`,
    `description?`, `tags[]`.
- **`data/projects.json`** → schema.org `CreativeWork`/`SoftwareSourceCode` (LinkedIn / GitHub)
  - `id`, `name`, `description`, `role?`, `url?`, `repo?`, `tech[]`,
    `startDate?`, `endDate?`, `status`, `tags[]`.

Each collection is seeded with 2–3 realistic sample records so the gallery renders.

**Normalized card shape:** a helper maps every source item into a common
`ContentItem { type, title, description, date, url, tags, source }` so the gallery
treats all four sources uniformly while preserving the type badge/filter.

## Astro app (`site/`)

- Astro 5 with the **content layer** `file()` loader (from `astro/loaders`) reading the
  JSON arrays in `../data/`. Collections + Zod schemas defined in `src/content.config.ts`.
- Structure:
  - `src/layouts/BaseLayout.astro` — html shell, `<SEO>`, nav, theme toggle, footer.
  - `src/components/` — `Nav`, `ThemeToggle`, `SEO` (meta + OG/Twitter + JSON-LD),
    `Card`, `Filters` (search/sort/filter controls), `Pagination`.
  - `src/pages/index.astro` (Home), `src/pages/about.astro` (About),
    `src/pages/content/[...page].astro` (paginated gallery via `paginate()`).
  - `src/styles/theme.css` — palette tokens (purple/blue/gold), light+dark, base styles.
- **Content page interactivity:** all items are embedded on a single `/content`
  page; a small vanilla-JS island does search (title/description/tags), sort
  (date/title/type), type filter, and client-side pagination entirely in the
  browser. (Implemented as `src/pages/content/index.astro` rather than a
  server-paginated route, since filtering/sorting must operate over the full set
  and the data volume is small — no backend/search service needed in Phase 1.)

## SEO (build into the site from day one)

- `<SEO>` component: per-page `<title>`, meta description, canonical URL.
- OpenGraph + Twitter Card tags (title, description, type, image, url).
- **JSON-LD structured data** via schema.org: `Person` on Home/About, and per-item
  types (`ScholarlyArticle`, `CreativeWork`, `Event`, `SoftwareSourceCode`) on the gallery.
- `@astrojs/sitemap` integration + `robots.txt`.
- Semantic HTML, image `alt` text, descriptive link text.
- Seed a root **`llms.txt`** + `AGENTS.md` stub (nods to Phase 3 agent goals; low cost now).

## Agent skills (`.github/skills/`)

Ship repo-local **skills** a coding agent can run to keep `data/` current. Because the
website is a pure view of `data/`, a skill only has to update the right JSON file — the
site rebuilds from it automatically. Each skill is a folder with a `SKILL.md`
(name, description, when-to-use, step-by-step procedure, and the target schema) so
`"add patent <url>"` triggers the right one.

Skills to seed:
- **`add-data-item`** — given a URL and/or context (and an item type: patent /
  publication / talk / project), fetch + parse the source, normalize it to that
  source's schema, de-duplicate against existing ids, append to the correct
  `data/*.json`, and report what was added. Handles `"add patent <link>"`,
  `"add talk <link>"`, etc.
- **`update-data-item`** — given an existing item (id or matching URL) plus a URL or
  context, refresh/augment its fields in place (e.g. add a video link to a talk,
  update citation count).
- **`research-data`** — search the web for relevant new items for the profile
  (recent talks, publications, patents, projects), present candidates, and hand
  confirmed ones to `add-data-item`.

Each `SKILL.md` documents: the JSON schema + field mapping from the external canonical
source, id/dedupe convention, validation (must satisfy the collection's Zod schema so
`astro build` stays green), and a note that no manual website edit is needed. A short
`AGENTS.md` section points coding agents at these skills.

## Deployment

- `.github/workflows/deploy.yml` using the official `withastro/action` + GitHub Pages
  deploy actions (`actions/deploy-pages`), triggered on push to `main`.
- `astro.config.mjs`: `site: 'https://nitya.github.io'`, `@astrojs/sitemap`.
- Document the "enable Pages → GitHub Actions source" one-time repo setting in README.

## Todos

1. Scaffold `data/` with the five JSON files + sample records.
2. Scaffold the Astro app in `site/` (deps, config, tsconfig, gitignore).
3. Define content collections + Zod schemas (`src/content.config.ts`) with the `file()` loader.
4. Build the theme system (CSS tokens, light/dark, purple/blue/gold, toggle).
5. Build BaseLayout + Nav + SEO + ThemeToggle.
6. Build the Home page (profile-driven hero + highlights).
7. Build the About page (profile data + Person JSON-LD).
8. Build the Content gallery: Card, Filters, Pagination, client-side search/sort/filter.
9. Add SEO extras: sitemap integration, robots.txt, llms.txt, AGENTS.md stub.
10. Add repo-local agent skills (`add-data-item`, `update-data-item`, `research-data`).
11. Add the GitHub Pages deploy workflow; verify `astro build` succeeds locally.

## Notes / decisions

- Data format: **JSON, one file per source** (confirmed).
- Folders: **`data/` + `site/`** (confirmed).
- Gallery sources: **Patents, Publications, Talks, Projects**; Profile powers About (confirmed).
- Schemas intentionally mirror external canonical formats and map to schema.org for SEO.
- Agent skills live in `.github/skills/<name>/SKILL.md`; they update `data/` only (site is a view).
- No time/date estimates.
