---
name: add-project
description: >-
  Add one or more projects to the personal knowledge platform from a GitHub
  repository, an org/README project list, or an aka.ms/short link. Resolves
  redirects, reads live repo metadata (stars, description, language, topics,
  dates, archived state) from the GitHub REST API, normalizes to the projects
  schema, de-duplicates by repo, and appends to data/projects.json. Use for
  "add project <link>", "add this repo as a project", "import my 30DaysOf
  projects", or "add projects from <org> README with >N stars".
---

# Skill: add-project

Add project records to `data/projects.json`. The website is a pure view of
`data/`, so you only edit the JSON — the site rebuilds from it.

## What counts as a project

A **project** is a substantial, named body of work — not a one-off talk, demo, or
throwaway repo. Add something as a project only when it has all three of:

1. **A repo** (or an equivalent durable home) that backs the work.
2. **A non-trivial amount of content reuse** — curricula, samples, a website,
   media, or campaign assets that get reused/extended over time (often the same
   repo powering several initiatives).
3. **Alignment to a core priority** of the organization the work was done in
   (e.g. a product-group learning campaign, a flagship sample, a community
   program) — i.e. it maps to a real strategic theme, not a personal side hack.

Talks, patents, and papers have their own types (`add-talk`, `add-patent`,
`add-publication`) — don't duplicate them here.

## Naming conventions

- Prefer **`microsoft-foundry`** over `azure-ai-foundry` in `tech`/`tags`/prose —
  the product is Microsoft Foundry. Never emit `azure-ai-foundry`.

## Destination

Always `data/projects.json`. Schema (see `site/src/content.config.ts`):

```
{ id, name, description, role?|null, url?|null, repo?|null, tech[],
  startDate?|null, endDate?|null, status: active|archived|completed, tags[] }
```

- `id` = kebab-case, stable: `proj-<repo-name>` (e.g. `proj-model-mondays`).
- `name` (required): human-friendly project/campaign name (e.g. a `#hashtag`
  campaign name), not necessarily the raw repo slug.
- `description` (required): one clean sentence. Prefer the repo description,
  trimmed to a single crisp line.
- `repo`: full `https://github.com/<owner>/<name>` URL. `url`: the project's
  homepage/site if it has one, else fall back to the repo URL.
- `tech[]`: primary language + a few repo topics (dedup, cap ~6).
- `status`: `active` if maintained/current, `completed` if a finished
  campaign/sample, `archived` if the repo is archived (GitHub `archived: true`).
- `tags[]`: lowercase themes for filtering (e.g. `ai`, `iot`, `web`).

## Sources & parsing

### A. A single GitHub repo (or aka.ms / short link)
Resolve redirects first, then read metadata from the **unauthenticated** REST
API (works for public repos even when the local `gh` token is SAML-blocked for
orgs like `microsoft`, `Azure`, `Azure-Samples`):

```bash
# Resolve a short link to its final GitHub URL
curl -sL --max-time 20 -o /dev/null -w "%{url_effective}\n" "https://aka.ms/model-mondays" -H "User-Agent: Mozilla/5.0"

# Read repo metadata (unauthenticated avoids org SAML 403s)
curl -sL --max-time 20 "https://api.github.com/repos/<owner>/<repo>" \
  -H "Accept: application/vnd.github+json" -H "User-Agent: Mozilla/5.0" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print(json.dumps({k:d.get(k) for k in ['full_name','stargazers_count','description','language','topics','created_at','homepage','archived']},indent=2))"
```

Map: `homepage` → `url` (fallback to repo URL); `language` + `topics` → `tech`;
`created_at[:10]` → `startDate`; `archived` → `status`.

> Prefer the unauthenticated `https://api.github.com/...` endpoint over `gh api`.
> The local `gh` token is often SAML-blocked (HTTP 403) for enterprise orgs,
> whereas public star counts and metadata are readable without auth.

### B. An org / profile README project list
Some orgs (e.g. `30DaysOf`) keep a project table in
`https://raw.githubusercontent.com/<org>/.github/main/profile/README.md` or the
repo root `README.md`. Extract each unique `github.com/<owner>/<repo>` link, then
fetch live metadata per repo via source A.

- **Badges are dynamic** — never trust a star count shown as a shields.io badge in
  the README; always fetch the real `stargazers_count` from the API.
- **Apply star/other filters against live data.** For a request like "only repos
  with more than N stars", compare `stargazers_count > N` (strict) using the API
  value, and report which repos were included/excluded.
- **One row per unique repo.** A README may list a repo under several campaign
  hashtags; that's still one project (fold the hashtags into `name`/`tags`).

## De-duplication

1. **Same repo = same project.** Before adding, skip any item whose `repo` (or
   `id`) already exists in `data/projects.json`. Normalize the repo URL
   (lowercase owner/name, strip trailing slash/`.git`) before comparing — GitHub
   owners/names are case-insensitive.
2. If a repo is already present but stale, prefer `update-data-item` to refresh
   fields (stars-derived status, description, homepage) instead of adding a row.
3. One repo reused across multiple campaigns is still one project; capture the
   extra campaigns in `name`/`tags`, not as duplicate rows.

## Procedure

1. Resolve the link(s) to canonical `owner/repo`.
2. Fetch live metadata (source A) for each; apply any user filter (e.g. stars).
3. Read `data/projects.json`; drop any candidate that already exists (dedup).
4. Build normalized objects; append and write valid JSON.
5. Validate: `cd site && npm run build` must stay green (Zod schemas). Fix any
   validation error (e.g. `url` must be a valid URL; `status` must be one of the
   enum values) before finishing.
6. Report what was added/skipped and why (e.g. "excluded: 2 repos <= 5 stars").
