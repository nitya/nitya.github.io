<!-- prettier-ignore -->
<div align="center">

<img src="./site/public/favicon.svg" alt="Nitya Narasimhan logo" width="110" />

# Nitya Narasimhan, PhD

*A data-first personal knowledge platform — structured data as source of truth, the website as human-first view, agents are first-class citizens.*

[![Deploy to GitHub Pages](https://img.shields.io/github/actions/workflow/status/nitya/nitya.github.io/deploy.yml?branch=main&label=deploy&style=flat-square)](https://github.com/nitya/nitya.github.io/actions/workflows/deploy.yml) &nbsp;
[![Live site](https://img.shields.io/website?url=https%3A%2F%2Fnitya.github.io&label=website&style=flat-square)](https://nitya.github.io) &nbsp;
[![Built with Astro](https://img.shields.io/badge/built%20with-Astro-ff5d01?style=flat-square&logo=astro&logoColor=white)](https://astro.build) &nbsp;
[![Open in Codespaces](https://img.shields.io/badge/Codespaces-open-24292e?style=flat-square&logo=github&logoColor=white)](https://codespaces.new/nitya/nitya.github.io)

---

[Live site](https://nitya.github.io) • [Overview](#overview) • [Data model](#data-model) • [Website](#human-experience--the-website) • [Agents](#agent-experience) • [Getting started](#getting-started)

</div>

<br/>

## Overview

Structured data in [`data/`](./data) is the single source of truth for my
personal and professional content; everything else — the website, the SEO
metadata, the agent tooling — is a *view* of it.

### Outcomes 
1. **Personal knowledge platform** — a centralized, structured, queryable record
   of my content and profile (patents, publications, talks, projects, training,
   and more), each backed by a schema aligned to a canonical external source.
2. **A static website** powered by that data, where **the data is the source of
   truth and the website is the view for humans** — deployed to GitHub Pages.
3. **Agent-friendly by design** — skills, `AGENTS.md`, `llms.txt` (planned), and
   structured data that make it easy for **remote agents** to work with the
   platform (e.g. to power a chatbot) and **coding agents** to maintain it.

### Roadmap

- **Phase 1** — Establish data files and the skills/workflows to populate them. ✅
- **Phase 2** — Build the static website from the data, on GitHub Pages. ✅
- **Phase 3** — Add a dynamic experience with a chatbot, in the cloud. ⏳

## Data model

Every activity or credential is backed by a structured data source with a defined
schema. Where possible the schema mirrors a canonical source for that *class* of
information, and maps to a [schema.org](https://schema.org) type for SEO.

| File | What it holds | Canonical reference |
| --- | --- | --- |
| `data/profile.json` | Profile, bio, and "find me online" links | LinkedIn / GitHub → `Person` |
| `data/patents.json` | Issued & filed patents | USPTO / Google Patents → `CreativeWork` |
| `data/publications.json` | Papers, thesis, citation counts | Google Scholar / ACM / IEEE → `ScholarlyArticle` |
| `data/talks.json` | Conference talks & sessions | Sessionize / Speaker Deck / SlideShare → `Event` |
| `data/projects.json` | Open-source projects & campaigns | GitHub / LinkedIn → `SoftwareSourceCode` |
| `data/training.json` | Curricula & 1P-event training content | GitHub repos → `Course` |
| `data/notifications.json` | Data-driven site banners (e.g. WIP notice) | — |

> The [Astro content-layer schemas](./site/src/content.config.ts) (Zod) validate
every file at build time — **an invalid `data/*.json` fails the build.**

<br/>

## Human experience — the website

[`site/`](./site) is an [Astro](https://astro.build) static site that renders the
data with meaningful routes and rich [OpenGraph](https://ogp.me/) metadata so each
page becomes a first-class object in the social graph.

- `/` — home
- `/about` — profile + a visual, badge-based "find me online" section
- `/content` — a searchable, sortable, filterable gallery with one card per item,
  filterable by type (Patents, Publications, Talks, Projects, Training) and by tag

Reusable pieces of note: a **data-driven notification banner** (backed by
`data/notifications.json`, dismissible per-flag) and **per-type page headers**.

## Agent experience

- **`AGENTS.md`** — best practices for coding agents maintaining this repo.
- **`.github/skills/`** — runnable skills that automate data maintenance:

  | Skill | Purpose |
  | --- | --- |
  | `add-patent` | Import patents via the Google Patents XHR API; split issued vs filed, de-dupe families |
  | `add-publication` | Import papers from a Scholar profile or DOI, with citation counts |
  | `add-talk` | Import talks from Speaker Deck RSS, Sessionize, SlideShare, or a conference archive |
  | `add-project` | Import projects from a GitHub repo, aka.ms link, or org README (live REST metadata) |
  | `add-data-item` | Generic single-item add for any type |
  | `update-data-item` | Update / enrich an existing item |
  | `research-data` | Search the web for new candidate items, then hand off to an `add-*` skill |

- The structured data is also reachable over a generic GitHub MCP connection, and
  `llms.txt` (for search agents) is planned.

A request like *"add patent &lt;link&gt;"* triggers the matching skill: parse the
source, append to the right `data/*.json`, and validate the build — no site edit.

### Add data by commenting on an issue

There's a permanent **“Data intake”** issue (labelled `data-intake`). Comment one
or more lines and a workflow does the rest — no local checkout needed:

```
add workshop https://github.com/microsoft/Build26-LAB540-...
add project  https://github.com/owner/repo | optional note
add talk     https://www.slideshare.net/slideshow/<slug>/<id>
```

[`.github/workflows/intake.yml`](./.github/workflows/intake.yml) runs
[`.github/scripts/intake.py`](./.github/scripts/intake.py), which parses each
`add <type> <url>` line, fetches metadata from the source, appends to the right
`data/*.json`, validates the build, commits, replies on the issue, and redeploys.
Supported types: `workshop`/`session`/`lab`/`training`/`curriculum`/`course` →
training, `project`, and `talk`. Patents & publications still use the CLI skills.

## Repository layout

```
data/                 Source of truth — JSON, one file per source
  profile.json  patents.json  publications.json  talks.json
  projects.json  training.json  notifications.json
site/                 Astro static site (a view of data/), deployed to GitHub Pages
  src/content.config.ts   Zod schemas + content-layer loaders for data/*.json
  src/pages/              Home (/), About (/about), Content (/content)
  src/components/         Card, Filters, Banner, Nav, …
.devcontainer/        Dev Container / Codespaces config + post-create bootstrap
.github/
  skills/             Runnable skills to maintain the data (add/update/research)
  scripts/            intake.py — issue-comment data intake parser
  workflows/          deploy.yml (GitHub Pages) + intake.yml (issue-comment intake)
  PLAN.md             Phased build plan
AGENTS.md             Best practices for coding agents
```

## Getting started

### GitHub Codespaces (one click)

Click **[Open in Codespaces](https://codespaces.new/nitya/nitya.github.io)**. The
dev container installs dependencies and runs a validating build automatically
(see [`.devcontainer/post-create.sh`](./.devcontainer/post-create.sh)). Then:

```bash
cd site && npm run dev -- --host   # preview on the forwarded port 4321
```

### Local development

```bash
cd site
npm install
npm run dev      # local preview at http://localhost:4321
npm run build    # production build + sitemap (also validates data schemas)
```

Edit content by changing the JSON in `data/` — the site rebuilds from it. Or use
the skills in `.github/skills/` (e.g. *"add patent &lt;url&gt;"*).

## Deployment

Pushes to `main` build `site/` and publish to GitHub Pages via
[`.github/workflows/deploy.yml`](./.github/workflows/deploy.yml). One-time setup:
repo **Settings → Pages → Source: GitHub Actions**.
