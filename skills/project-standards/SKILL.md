---
name: project-standards
description: Use whenever starting a new project or repo, scaffolding an app/CLI/library/service, adding or changing tooling (package manager, linter, formatter, type checker, test runner, CI, git hooks), choosing a stack layer (framework, database, ORM, auth, hosting, scheduling), writing a commit message, wiring an LLM call, or bringing an existing project in line with the standards. Defines the standard project shapes, the baseline every repo gets, and the Copier templates that scaffold them.
---

# Project Standards

The standard shapes for new projects, the baseline every repository gets, and
the templates that produce them (`gh:Sparky-code/templates`, Copier).

These standards came from surveying a couple of dozen real projects that had
drifted: five package managers, five test runners, CI in a handful, formatting
configured in one, two Expo apps on different SDKs, three full-stack apps with
no layer in common, secrets in compose files. Every rule below fixes something
that actually went wrong.

## How firm is each rule?

- **Firm (do it)** where the choice is cheap and interchangeable: toolchains,
  formatters, hooks, CI, commit format, secrets handling, migrations, job
  safety. Picking one and never re-deciding is the whole value.
- **Guide (default, record deviations)** where the right answer depends on the
  app: web frameworks, auth libraries, hosting, state libraries. Pick by need,
  stay close to standard, well-known packages, and write the choice and the
  reason in the project's `CLAUDE.md`.

Versions named here are majors that were current when the standard was set.
Before pinning, check the current release (`npm view <pkg> version`, PyPI,
Expo changelog) and use the latest stable within the standard.

## Decision tree: which shape?

| You are building | Shape | Start with |
|---|---|---|
| A reusable TypeScript module used by several apps | TS library | `bin/new-project ts-library <dir>` |
| A command-line tool or scheduled job sharing code with a TS app | TS CLI / job | `bin/new-project ts-cli <dir>` |
| Scraping, data work, ML/NLP, macOS automation, or a job with no TS code to share | Python CLI / job | `bin/new-project python-cli <dir>` |
| An HTTP API on Postgres in Python | Python service | `bin/new-project python-service <dir>` |
| A web app with no SEO need (client-only or with a small API) | React web | `bin/new-project react-web <dir>` (`--data with_api=false` for client-only) |
| A web app that must be crawlable / server-rendered from day one | Next.js | `pnpm create next-app`, then `bin/new-project next <dir>` |
| A mobile app | Expo | `pnpm create expo-app`, then `bin/new-project expo <dir>` |
| A content site or blog | Static site | Eleventy (Astro if pages need interactive parts) + baseline (`other`) |
| A throwaway sketch or demo | Prototype | One HTML file in the `sketches` repo, importing `tokens.css` |
| Self-hosted services | Homelab stack | One compose file per stack in the homelab repo |

Not sure between two? Read the matching reference: `web-apps.md`,
`jobs-and-clis.md`, `libraries.md`.

## The baseline (every repo)

- [ ] In git with a GitHub repo; the folder name matches the repo name (sketches are the one exception: one repo, a folder each).
- [ ] `README.md` always. `CLAUDE.md` when the project has a build, tests or conventions: commands, layout, rules, stack choice. Short and accurate beats long and stale.
- [ ] Settings only from environment variables; `.env` git-ignored, `.env.example` committed and current. No credentials in compose files, code, or history.
- [ ] Version pinned: `.nvmrc` (Node 24) or `.python-version` (3.14).
- [ ] lefthook: pre-commit formats and lints staged files; pre-push runs typecheck and tests; commit-msg enforces the convention.
- [ ] CI on every PR: install, lint, typecheck, test (and build where there is one).
- [ ] Renovate config for dependency and image updates.
- [ ] UI projects use the shared design tokens (see `frontend-ui-stack`).

Details and the exact commit convention: `references/baseline.md`.

## Commit messages (firm)

```
type(scope)!: Imperative subject

Optional body saying why, after a blank line.
```

Types: `feat fix refactor docs test chore build ci`. Scope and `!` (breaking)
optional. Subject capitalised, imperative ("Add", not "Added"), no trailing
period, whole line at most 72 characters. Never add `Co-Authored-By` trailers,
"Generated with" lines, or session IDs/links. The template's commit-msg hook
enforces all of this.

## Firm rules at a glance

| Area | Rule | Reference |
|---|---|---|
| TypeScript | pnpm, Node 24, TS 7 strict (`noUncheckedIndexedAccess`, `verbatimModuleSyntax`, `erasableSyntaxOnly`), ESM only, `.ts` import extensions, Biome, Vitest | `typescript.md` |
| Running TS | Node runs `.ts` directly (type stripping); tsc builds only libraries; tsx only as a fallback | `typescript.md` |
| Python | uv, 3.14, `src/<pkg>` + `tests/`, Typer, ruff, mypy strict, pytest with an opt-in `live` marker, httpx | `python.md` |
| Data | SQLite first; Postgres when concurrency/instances/PostGIS demand; no MySQL; numbered migrations always; DB files in git-ignored `data/` | `data.md` |
| ORM | Prisma for TS servers/CLIs; Drizzle + expo-sqlite on device; raw sqlite3 for Python tools; SQLAlchemy 2 + Alembic for Python services | `data.md` |
| Web | zod at every boundary; a maintained auth library (never hand-rolled sessions); Resend for email; a pnpm workspace once there are two apps | `web-apps.md` |
| Mobile | Expo, within one SDK of latest; expo-router; StyleSheet + `tokens.ts` with a drift check | `mobile.md` |
| Jobs | Safe to re-run, SQLite state, run lock, `--dry-run` and per-run caps, non-zero exit on failure, run records, ntfy alert; launchd plist in `ops/launchd/` | `jobs-and-clis.md` |
| LLM calls | Only through the Claude CLI (`claude -p`) in one tested wrapper module per project; never an API SDK | `jobs-and-clis.md` |
| Libraries | ESM, subpath exports, no runtime deps (inject fetch/clock), vendored while private, npm with provenance when public, every export tested and documented | `libraries.md` |
| Infra | Pinned image tags, secrets via `.env`, healthchecks, named volumes, localhost-bound ports; compose before k3s | `static-prototypes-homelab.md` |
| Shell | `#!/usr/bin/env bash`, `set -euo pipefail`, shellcheck, bash 3.2-compatible on macOS, no hard-coded home paths | `static-prototypes-homelab.md` |

## Scaffolding and updating

Use the templates rather than assembling a project by hand; that is how drift
starts. `references/templates.md` has the commands. In short:

```bash
git clone https://github.com/Sparky-code/templates ~/code/templates   # once
~/code/templates/bin/new-project <shape> <dir> [--data key=value ...]
```

Existing projects pull template improvements with
`uvx copier update -a .copier-answers.baseline.yml` (and `.shape.yml`).

## Existing projects

These standards apply to new work. Don't migrate an existing project's tooling
as a side effect of an unrelated task; when the user asks to bring a project in
line, or a project is being restructured anyway, apply the baseline and move one
layer at a time (package manager, then lint/format, then hooks, then CI), each
in its own commit.

## Anti-patterns

- Choosing a tool per project for a layer that has a firm standard ("this one uses Jest").
- Hand-copying config from another project instead of using the template.
- Credentials in compose files, code, or commits; a `.env` without `.env.example`.
- Schema changes without a numbered migration.
- A scheduled job without a lock, a dry run, or a failure signal.
- Calling an LLM API SDK, or calling the Claude CLI from more than one place.
- A `CLAUDE.md` that describes a stack the project doesn't use. Update it or delete the line.
- Leftover scaffolding (template READMEs, package metadata from a starter kit, `counter.ts`).

## Reference index

- `references/baseline.md` — git, docs, env/secrets, version pins, lefthook, commit convention, CI, Renovate.
- `references/typescript.md` — pnpm, Node, TS config, type stripping, Biome, Vitest, builds.
- `references/python.md` — uv, layout, Typer, ruff, mypy, pytest, httpx, single-file scripts.
- `references/web-apps.md` — the web decision guide and its firm rules.
- `references/mobile.md` — Expo shape.
- `references/data.md` — engines, ORMs, migrations, files and blobs, backups.
- `references/jobs-and-clis.md` — job rules, scheduling, config, logs, alerts, the Claude CLI wrapper.
- `references/libraries.md` — package shape, distribution, versioning, quality bar.
- `references/static-prototypes-homelab.md` — static sites, sketches, compose rules, shell scripts.
- `references/templates.md` — using and maintaining the Copier templates.
