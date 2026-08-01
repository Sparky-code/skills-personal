# skills-personal

Hand-authored Agent Skills. This repo is the **single source of truth** — the
copies your agent harnesses load are symlinks pointing back here.

Distinct from `../skills-sandbox/`, which is a clone of someone else's skill
collection managed by a lockfile. Nothing here comes from upstream.

## Skills

| Skill | Purpose |
|---|---|
| `frontend-ui-stack` | The default frontend stack for `/Users/sparky/Code` — Vite + React, Tailwind v4, shadcn/ui on Base UI, DTCG tokens via Style Dictionary, Material principles (not MUI). |
| `local-llm-mlx` | The default local-LLM stack — MLX via mlx-lm, two Qwen3 tiers behind one client, LoRA adapters with the `v{n}` / `current.json` promotion contract. |

## Install

```bash
./scripts/link-skills.sh            # → ~/.claude/skills
./scripts/link-skills.sh --agents   # → also ~/.agents/skills (amp, cursor, codex, …)
```

Symlinks, not copies. Edit a `SKILL.md` here and the change is live on the next
session — no sync step, no drift.

Skills are discovered at session start, so **restart Claude Code** after linking
a new one.

## Layout

```
skills/
  <skill-name>/
    SKILL.md          # frontmatter (name, description) + main instructions
    references/       # loaded on demand, not held in context
```

`name:` in the frontmatter must match the directory name — that name is what
becomes `/<skill-name>`.

## Why this shape

Skills beat single-file commands here for two reasons:

**Progressive disclosure.** Only `name` + `description` stay resident in
context. `SKILL.md` loads when the skill fires; `references/*.md` load only if
actually needed. `local-llm-mlx` is ~1,250 lines — as a command, all of it would
load on every invocation.

**Auto-trigger.** Both descriptions are written as "Use whenever…" so the model
invokes them when relevant work starts, not only when you remember to type a
slash. Commands can't do that.

## Rules

- One canonical copy, in this repo. Everything else is a symlink.
- Never store a skill somewhere that isn't linked — an unlinked copy is how
  two versions silently diverge.
- `~/.claude/skills/` holds only `<name>/SKILL.md` directories.
  `~/.claude/commands/` holds only single-file slash prompts. No mixing.
