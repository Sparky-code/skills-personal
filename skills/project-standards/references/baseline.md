# Baseline (every repository)

The template's `baseline` layer produces all of this; apply it with
`bin/new-project <shape> <dir>` (or to an existing repo, see `templates.md`).

## Git and GitHub

- Every project lives in git with a GitHub remote, including sketches and
  infrastructure. Work that exists only on one disk is one accident from gone.
- The local folder name matches the GitHub repo name. Mismatched names
  (folder `foo`, repo `bar`) cost time in every session that has to work out
  which is which.
- Default branch `main`. Work on branches; merge through PRs so CI runs.

## Docs

- `README.md` (always): what it is, setup, how to run it, how to develop it.
- `CLAUDE.md` (when there is a build, tests or conventions): commands, layout,
  rules, and the stack choice with its reason. Keep it short and true: an
  agent trusts it, so a wrong line is worse than a missing one. Update it in
  the same commit as the change that makes it stale.
- `ROADMAP.md` when there is ongoing planned work; `CHANGELOG.md` for libraries.

## Settings and secrets

- Configuration comes from environment variables only.
- `.env` holds local values and is git-ignored; `.env.example` lists every
  variable with a safe placeholder and is committed. Add to both in the same
  commit.
- Never put credentials in code, compose files, CI files or commit history. If
  one lands in history, rotate or delete the credential; rewriting history is
  not enough because clones and caches keep it.
- Load `.env` with the runtime, not a library: `node --env-file-if-exists=.env`,
  `uv run --env-file .env`.

## Version pins

- Node projects: `.nvmrc` containing `24`, plus `"engines": {"node": ">=24"}`
  and `"packageManager": "pnpm@<version>"` in package.json.
- Python projects: `.python-version` containing `3.14` (uv installs it).

## Git hooks (lefthook)

One tool for every language: a single binary, configured in `lefthook.yml`,
installed per clone with `lefthook install`.

| Hook | Runs | Why there |
|---|---|---|
| pre-commit | formatter + linter on staged files, fixes re-staged (Biome, or ruff format + ruff check); shellcheck on staged `.sh` | Seconds; keeps formatting noise out of history |
| pre-push | typecheck + tests (`pnpm run typecheck` / `pnpm run test`, or `uv run mypy` / `uv run pytest`) | Slower checks without slowing every commit |
| commit-msg | `.lefthook/commit-msg/check-message.sh` | Enforces the convention below |

CI repeats everything, so a skipped hook (`--no-verify`) is caught there.

## Commit convention

```
type(scope)!: Imperative subject

Optional body: why the change was made, what it affects.
```

- `type`: `feat` (new behaviour), `fix` (bug fix), `refactor`, `docs`, `test`,
  `chore` (deps, tooling, housekeeping), `build`, `ci`.
- `(scope)` optional: the area touched (`fix(parser): …`). `!` marks a breaking
  change (`feat!: …`).
- Subject: capitalised, imperative ("Add", "Fix", "Remove"), no trailing
  period. The whole line, prefix included, at most 72 characters.
- Body optional; when present, after a blank line, explaining why.
- Never: `Co-Authored-By` trailers, "Generated with …" lines, session IDs or
  session links.
- Merge, revert, fixup and squash commits written by git are exempt.

Why this hybrid: it reads like plain imperative history, while the type prefix
makes changes machine-readable (filtering, changelogs, version bumps) without
the full Conventional Commits ceremony.

## CI

GitHub Actions, on push to `main` and on every PR: install (frozen lockfile),
lint, typecheck, test, and build where the project builds. TypeScript jobs use
`pnpm/action-setup` + `actions/setup-node` with `node-version-file: .nvmrc`;
Python jobs use `astral-sh/setup-uv` and `uv sync --locked`. Also shellcheck any
committed `.sh` files.

## Renovate

`renovate.json` in every repo: weekly schedule, minor and patch updates grouped
for packages past 1.0, `chore:` commit type. Pinned versions (including Docker
image tags) stay pinned without going stale.
