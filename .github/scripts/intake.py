#!/usr/bin/env python3
"""Data-intake parser for the personal knowledge platform.

Reads a GitHub issue comment (env COMMENT_BODY) containing one or more lines
like:

    add workshop https://github.com/microsoft/Build26-LAB540-...
    add project  https://github.com/nitya/some-repo | short note
    add talk     https://www.slideshare.net/slideshow/<slug>/<id>

For each recognised line it fetches metadata from the source, normalises it to
the matching `data/*.json` schema, de-duplicates, and appends the record. It
never fabricates specifics: titles/dates/descriptions come from the fetched
source (or the optional inline note).

Outputs:
  * mutates the relevant data/*.json files in place
  * writes a Markdown summary to $INTAKE_RESULT (default: intake_result.md)
  * prints the summary to stdout
  * sets `changed=true|false` on $GITHUB_OUTPUT when present

Supported types:
  training  : workshop | session | lab | training | curriculum | course
              -> data/training.json   (GitHub repo URL)
  project   : project -> data/projects.json                 (GitHub repo URL)
  talk      : talk    -> data/talks.json          (SlideShare / Speaker Deck /
              any page exposing JSON-LD or OpenGraph metadata)

Patents and publications are intentionally NOT auto-added here — they need the
richer parsing in the CLI add-patent / add-publication skills.
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA = ROOT / "data"

UA = {"User-Agent": "Mozilla/5.0 (compatible; nitya-intake-bot/1.0)"}

TRAINING_KINDS = {"workshop", "session", "lab", "training", "curriculum", "course"}
ALIASES = {k: "training" for k in TRAINING_KINDS}
ALIASES.update({"project": "project", "talk": "talk"})

MANUAL_ONLY = {"patent", "publication", "paper"}


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def http_json(url: str):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)


def http_text(url: str) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", "replace")


def load(name: str):
    p = DATA / f"{name}.json"
    return json.loads(p.read_text()) if p.exists() else []


def save(name: str, items) -> None:
    (DATA / f"{name}.json").write_text(json.dumps(items, indent=2) + "\n")


def slugify(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return re.sub(r"-+", "-", s)[:70]


def pretty(s: str) -> str:
    s = s.replace("-", " ").replace("_", " ").strip()
    return re.sub(r"\s+", " ", s).title()


def normalize_foundry(text: str) -> str:
    if not text:
        return text
    text = re.sub(r"Azure AI Foundry", "Microsoft Foundry", text, flags=re.I)
    text = re.sub(r"Azure AI Studio", "Microsoft Foundry", text, flags=re.I)
    return text


def clean_tags(raw) -> list[str]:
    out: list[str] = []
    for t in raw or []:
        if not t:
            continue
        t = t.strip().lower().replace("_", "-")
        if not t:
            continue
        if t in ("azure-ai-foundry", "azure-ai-studio", "ai-foundry"):
            t = "microsoft-foundry"
        if t not in out:
            out.append(t)
    return out


def meta_content(html: str, key: str) -> str | None:
    for attr in ("property", "name"):
        m = re.search(
            rf'<meta[^>]+{attr}=["\']{re.escape(key)}["\'][^>]+content=["\']([^"\']+)["\']',
            html,
            flags=re.I,
        )
        if m:
            return m.group(1).strip()
        m = re.search(
            rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+{attr}=["\']{re.escape(key)}["\']',
            html,
            flags=re.I,
        )
        if m:
            return m.group(1).strip()
    return None


def jsonld_blocks(html: str):
    for m in re.finditer(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        flags=re.I | re.S,
    ):
        try:
            data = json.loads(m.group(1).strip())
        except Exception:
            continue
        if isinstance(data, list):
            for d in data:
                yield d
        else:
            yield data


def program_from_repo(repo: str) -> str:
    r = repo.lower()
    table = [
        ("build26", "Microsoft Build 2026"),
        ("build25", "Microsoft Build 2025"),
        ("aitour26", "Microsoft AI Tour 2026"),
        ("aitour25", "Microsoft AI Tour 2025"),
        ("ignite26", "Microsoft Ignite 2026"),
        ("ignite25", "Microsoft Ignite 2025"),
    ]
    for prefix, label in table:
        if r.startswith(prefix):
            return label
    return "Curriculum"


def repo_title(repo: str) -> str:
    name = re.sub(r"^(build|aitour|ignite)2[0-9]-", "", repo, flags=re.I)
    name = re.sub(r"^(lab|brk|dem|ltg|prel|wrk|od|keynote)\d+-", "", name, flags=re.I)
    return pretty(name)


def parse_github(url: str):
    m = re.search(r"github\.com/([^/\s]+)/([^/\s#?]+)", url)
    if not m:
        raise ValueError("not a GitHub repo URL")
    owner, repo = m.group(1), m.group(2).replace(".git", "")
    try:
        d = http_json(f"https://api.github.com/repos/{owner}/{repo}")
    except urllib.error.HTTPError as e:
        raise ValueError(f"GitHub API returned HTTP {e.code} for {owner}/{repo}")
    return owner, repo, d


# --------------------------------------------------------------------------- #
# builders  (return (collection, item))
# --------------------------------------------------------------------------- #
def build_training(url: str, note: str | None):
    owner, repo, d = parse_github(url)
    program = program_from_repo(repo)
    is_beginners = "for-beginners" in repo.lower() or program == "Curriculum"
    title = repo_title(repo)
    repo_desc = normalize_foundry((d.get("description") or "").strip())
    if note:
        description = normalize_foundry(note)
    elif repo_desc:
        description = repo_desc
    else:
        description = f"{program} content: {title}."
    base_tags = ["for-beginners", "curriculum"] if is_beginners else ["msft-workshops"]
    tags = clean_tags(base_tags + (d.get("topics") or []))
    item = {
        "id": f"training-{slugify(repo)}",
        "title": title,
        "program": program,
        "description": description,
        "url": d.get("html_url") or url,
        "date": None,
        "tags": tags,
    }
    return "training", item


def build_project(url: str, note: str | None):
    owner, repo, d = parse_github(url)
    name = d.get("name") or pretty(repo)
    repo_desc = normalize_foundry((d.get("description") or "").strip())
    description = normalize_foundry(note) if note else (repo_desc or name)
    tech = clean_tags(([d.get("language")] if d.get("language") else []) + (d.get("topics") or []))
    homepage = (d.get("homepage") or "").strip()
    item = {
        "id": f"proj-{slugify(repo)}",
        "name": name,
        "description": description,
        "role": None,
        "url": homepage or d.get("html_url") or url,
        "repo": d.get("html_url") or url,
        "tech": tech,
        "startDate": None,
        "endDate": None,
        "status": "archived" if d.get("archived") else "active",
        "tags": clean_tags(d.get("topics") or []),
    }
    return "project", item


def build_talk(url: str, note: str | None):
    html = http_text(url)
    name = None
    date = None
    for d in jsonld_blocks(html):
        if not isinstance(d, dict):
            continue
        name = name or d.get("name") or d.get("headline")
        date = date or d.get("datePublished") or d.get("startDate")
    name = name or meta_content(html, "og:title") or meta_content(html, "twitter:title")
    if not name:
        raise ValueError("could not extract a title (site may block automated fetch). Use the CLI add-talk skill.")
    if date:
        dm = re.search(r"(\d{4})-(\d{2})-(\d{2})", str(date))
        date = dm.group(0) if dm else None
    if not date:
        raise ValueError("could not extract a publish date (talks require one). Use the CLI add-talk skill.")
    event = meta_content(html, "og:site_name") or "Presentation"
    if "slideshare" in url.lower():
        event = "SlideShare"
    elif "speakerdeck" in url.lower():
        event = "Speaker Deck"
    description = normalize_foundry(note) if note else (meta_content(html, "og:description") or "")
    year = date[:4]
    item = {
        "id": f"talk-{year}-{slugify(name)}",
        "title": name.strip(),
        "event": event,
        "date": date,
        "location": None,
        "url": url,
        "slidesUrl": url,
        "videoUrl": None,
        "description": description.strip(),
        "tags": [],
    }
    return "talk", item


BUILDERS = {"training": build_training, "project": build_project, "talk": build_talk}


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
LINE_RE = re.compile(
    r"^\s*(?:[-*]\s*)?add\s+(?P<type>[a-z]+)\s+(?P<url>https?://\S+)\s*(?:[|]\s*|[-\u2013\u2014]{1,2}\s+)?(?P<note>.*?)\s*$",
    re.I,
)


def process(body: str):
    results = []
    changed = False
    caches: dict[str, list] = {}
    seen_this_run: set[str] = set()

    for raw in body.splitlines():
        m = LINE_RE.match(raw)
        if not m:
            continue
        typ = m.group("type").lower()
        url = m.group("url").rstrip(".,);")
        note = (m.group("note") or "").strip() or None

        if typ in MANUAL_ONLY:
            results.append(("skip", raw.strip(), f"`{typ}` items need the CLI add-{typ} skill (richer parsing); not auto-added."))
            continue
        collection = ALIASES.get(typ)
        if not collection:
            results.append(("skip", raw.strip(), f"unknown type `{typ}` — use one of: {', '.join(sorted(ALIASES))}."))
            continue

        try:
            name, item = BUILDERS[collection](url, note)
        except Exception as e:  # noqa: BLE001
            results.append(("fail", raw.strip(), str(e)))
            continue

        items = caches.setdefault(name, load(name))
        key = item["id"]
        existing_ids = {i.get("id") for i in items}
        existing_urls = {str(i.get("url", "")).rstrip("/") for i in items}
        if key in existing_ids or key in seen_this_run:
            results.append(("dup", raw.strip(), f"already present as `{key}` — skipped."))
            continue
        if str(item.get("url", "")).rstrip("/") in existing_urls:
            results.append(("dup", raw.strip(), f"URL already in `{name}.json` — skipped."))
            continue

        items.append(item)
        seen_this_run.add(key)
        changed = True
        label = item.get("title") or item.get("name")
        results.append(("ok", raw.strip(), f"added **{label}** to `data/{name}.json` (id `{key}`)."))

    if changed:
        for name, items in caches.items():
            save(name, items)

    return changed, results


def render(results) -> str:
    icon = {"ok": "✅", "dup": "🔁", "skip": "⏭️", "fail": "❌"}
    if not results:
        return (
            "🤔 I didn't find any `add <type> <url>` lines in that comment.\n\n"
            "Try, one per line:\n\n"
            "```\nadd workshop https://github.com/microsoft/Build26-LAB540-...\n"
            "add project https://github.com/owner/repo\n"
            "add talk https://www.slideshare.net/slideshow/<slug>/<id>\n```"
        )
    lines = ["Here's what I did with that comment:", ""]
    for status, src, msg in results:
        lines.append(f"- {icon.get(status, '•')} {msg}")
    return "\n".join(lines)


def main() -> int:
    body = os.environ.get("COMMENT_BODY", "")
    if not body and len(sys.argv) > 1:
        body = pathlib.Path(sys.argv[1]).read_text()

    changed, results = process(body)
    summary = render(results)

    out_path = os.environ.get("INTAKE_RESULT", "intake_result.md")
    pathlib.Path(out_path).write_text(summary + "\n")
    print(summary)

    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a") as f:
            f.write(f"changed={'true' if changed else 'false'}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
