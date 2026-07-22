#!/usr/bin/env bash
#
# Codespaces / Dev Container post-create bootstrap.
# Installs site dependencies and validates that data/ satisfies the schemas
# by running a full production build.
#
set -euo pipefail

echo "▸ Installing site dependencies…"
cd "$(dirname "$0")/../site"
npm install

echo "▸ Building the site to validate data/ against the Zod schemas…"
npm run build

cat <<'EOF'

✅ Dev container ready.

Common commands (from the repo root):
  cd site && npm run dev            # local preview at http://localhost:4321
  cd site && npm run dev -- --host  # expose the dev server for Codespaces port forwarding
  cd site && npm run build          # production build + sitemap (validates data/)

Edit content by changing the JSON in data/ — the site rebuilds from it.
Or use the skills in .github/skills/ (e.g. "add patent <url>").
EOF
