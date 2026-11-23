# Static sites, prototypes, homelab, shell scripts

## Static sites

- **Eleventy** for content sites and blogs: Markdown in, HTML out, no client
  JavaScript by default.
- **Astro** when pages need interactive parts (islands) or typed content collections.
- The toolchain rules still apply: ESM config, Node 24, pnpm, Biome, the
  shared `tokens.css`, baseline (`bin/new-project other <dir>`).
- Host on **GitHub Pages** (Actions deploy).

## Prototypes and sketches

- One HTML file, no build, importing the shared `tokens.css` (see
  `frontend-ui-stack`'s plain-HTML branch), so a sketch looks like the real apps.
- All sketches live in **one `sketches` repo**, a folder each, so they're in
  git without a repo per experiment.
- **Promotion rule:** once a sketch needs a build step, a second module of
  logic, or real data, it moves to a proper shape in its own repo. Sketches
  that quietly grow into apps are how unmaintained code happens.

## Homelab and infrastructure

- **One git repo** for the homelab, **one compose file per stack**. Changes are
  reviewable and reversible.
- Compose rules (firm):
  - **Pinned image tags**, never `:latest` (Renovate proposes updates).
  - **Secrets only through `.env`**, with a committed `.env.example`; use
    `${VAR:?message}` so a missing secret fails loudly. No passwords in the
    compose file.
  - A **healthcheck** on every service; `depends_on: condition: service_healthy`.
  - **Named volumes** for data.
  - **Ports bound to localhost** (`127.0.0.1:5432:5432`) unless the service
    must be reachable from the network; make host ports overridable
    (`${POSTGRES_PORT:-5432}`).
- **Compose until multi-node is actually needed**, then k3s. A single box
  doesn't need Kubernetes.

## Shell scripts

- `#!/usr/bin/env bash` and `set -euo pipefail`.
- **Compatible with bash 3.2**, which is macOS's `/bin/bash`: no `mapfile`,
  no associative arrays, no `${var,,}`. If a script needs bash 4+, check
  `BASH_VERSINFO` and fail with a clear message.
- shellcheck clean (pre-commit hook and CI).
- No hard-coded home paths: use `$HOME`, script-relative paths
  (`$(dirname "${BASH_SOURCE[0]}")`), or an environment variable.
- A script that outgrows a page becomes a Python CLI.
