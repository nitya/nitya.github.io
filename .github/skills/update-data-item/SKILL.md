---
name: update-data-item
description: >-
  Update or enrich an existing item in the personal knowledge platform. Given an
  item id (or a matching URL/title) plus a URL or context, refresh its fields in
  place in the correct data/*.json file. Use for "update this talk with the video
  link", "refresh citation count", or "fix the assignee on this patent".
---

# Skill: update-data-item

Update an existing structured data item in `data/`. The website is a view of the
data, so editing the JSON is all that is required.

## When to use

Trigger phrases: "update <item> with …", "add the video/slides link to this talk",
"refresh the citation count", "correct this field", "this item changed".

## Inputs

- An **identifier**: the item `id`, or a `url`/`doi`/title that matches one item.
- New information as a **URL** and/or **context**.

## Procedure

1. **Locate** the item: determine the type/file from the identifier, read the
   target `data/*.json`, and find the object by `id` (fallback: exact `url`/`doi`,
   then fuzzy title match — confirm with the user if uncertain).
2. If no match is found, offer to use the **add-data-item** skill instead.
3. **Fetch/parse** the new source if a URL was provided.
4. **Merge** changes onto the existing object: update only the fields that
   changed; keep the `id` stable; do not drop existing fields unless asked.
5. **Write** the file back with 2-space indent.
6. **Validate**: `cd site && npm run build` must stay green against the Zod schema
   in `site/src/content.config.ts`.
7. **Report** a concise before/after of the changed fields.

## Schemas

Identical to `add-data-item` / `site/src/content.config.ts`. Do not introduce
fields the schema does not allow.

## Guardrails

- Never change an item's `id` (it is the stable key and dedupe anchor).
- Never invent values; only apply information you can source or the user provides.
- Edit `data/` only — never hand-edit `site/`. Leave the build green.
