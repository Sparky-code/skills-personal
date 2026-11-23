# Templates (Copier)

All shapes come from one public Copier repo, `gh:Sparky-code/templates`. Each
project gets two layers:

- **baseline**: hooks, CI, README/CLAUDE.md, `.env.example`, `.gitignore`,
  version pin, Renovate, LICENSE (MIT only), design tokens for UIs;
- **shape**: the code and tool config for `ts-library`, `ts-cli`,
  `python-cli`, `python-service` or `react-web`.

Each layer records its answers and template version in its own file
(`.copier-answers.baseline.yml`, `.copier-answers.shape.yml`). Never edit
those by hand.

## New project

Prerequisites: uv (Copier runs via `uvx`), lefthook, and for TS shapes Node 24
with `corepack enable pnpm`.

```bash
git clone https://github.com/Sparky-code/templates ~/code/templates   # once
~/code/templates/bin/new-project python-cli ~/code/my-tool
~/code/templates/bin/new-project ts-cli ~/code/my-job --data uses_claude=true
~/code/templates/bin/new-project react-web ~/code/my-app --data with_api=false
```

Options (`--data key=value`): `description`, `author` (name only, no email),
`license` (`MIT` or `UNLICENSED`), `uses_claude` and `is_job` (CLI shapes),
`with_api` (react-web).

`bin/new-project` applies both layers, runs `git init`, installs dependencies
(`pnpm install` / `uv sync`) and `lefthook install`. Review, then make the
first commit: `chore: Scaffold from templates`.

### Framework apps

Run the official generator, then apply the baseline only:

```bash
pnpm create expo-app ~/code/my-mobile   # or: pnpm create next-app ~/code/my-site
~/code/templates/bin/new-project expo ~/code/my-mobile   # or: next
```

### Without the script

```bash
uvx copier copy gh:Sparky-code/templates <dir> --data layer=shape --data shape=<shape> -a .copier-answers.shape.yml
uvx copier copy gh:Sparky-code/templates <dir> --data layer=baseline --data shape=<shape> -a .copier-answers.baseline.yml
```

## Updating a project

When the templates gain a fix (a new lint rule, a CI change, updated tokens):

```bash
uvx copier update -a .copier-answers.baseline.yml
uvx copier update -a .copier-answers.shape.yml
```

Copier merges the template's changes since the recorded version into the
project, keeping local edits; conflicts show as inline markers. Review the
diff, run the checks, commit (`chore: Update from templates v0.x`).

## Applying the baseline to an older project

1. On a branch, in a terminal, apply only the baseline with the shape that
   fits (or `other`):
   ```bash
   uvx copier copy gh:Sparky-code/templates . --data layer=baseline --data shape=<shape> -a .copier-answers.baseline.yml
   ```
   Copier asks before overwriting each existing file (without a terminal it
   stops, so an agent should ask the user to run it, or pass `--skip <file>`
   for files to keep). Keep the project's own README content; merge the rest.
2. Then move tooling one layer per commit: package manager (pnpm / uv), Biome
   or ruff, hooks, CI. Fix what each step surfaces before the next.

## Changing the templates

Work in the templates repo (see its CLAUDE.md): edit, generate the shape
(`TEMPLATES_SRC=$PWD TEMPLATES_REF=HEAD bin/new-project <shape> /tmp/x`), port
formatter output back into the template, run `uv run pytest` and
`uv run pytest -m slow`, then tag a release. Projects pick it up with
`copier update`.
