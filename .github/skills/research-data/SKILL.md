---
name: research-data
description: >-
  Search the web for relevant new items (talks, publications, patents, projects)
  for the profile, present them as candidates, and hand confirmed ones to the
  add-data-item skill. Use for "find my recent talks", "search for new
  publications", or "what should I add to my data?".
---

# Skill: research-data

Discover new candidate items for the personal knowledge platform and route
confirmed ones into `data/` via the `add-data-item` skill.

## When to use

Trigger phrases: "find new talks/publications/patents", "search the web for my
recent activity", "what's missing from my data?", "research and add".

## Procedure

1. **Read context**: load `data/profile.json` for identity/`sameAs` links and the
   existing `data/*.json` files to know what is already captured.
2. **Search** the web using the profile's name and known handles/`sameAs`
   profiles (Google Scholar, Sessionize, GitHub, LinkedIn, USPTO/Google Patents).
   Scope to the requested type if one was given.
3. **Filter out** anything already present (match on `url`/`doi`/title against the
   existing data). Only surface genuinely new items.
4. **Present candidates** as a concise list: type, title, source, date, URL.
   Do not write anything yet.
5. **Confirm** with the user which candidates to add.
6. **Hand off** each confirmed candidate to the **add-data-item** skill (which
   parses, normalizes, de-duplicates, appends, and validates the build).
7. **Summarize** what was added.

## Guardrails

- Verify each item actually belongs to this person before proposing it
  (name collisions are common) — prefer results reachable from `sameAs` links.
- Never add items without user confirmation.
- All writes go through `add-data-item`, which keeps the build green and
  edits only `data/`.
