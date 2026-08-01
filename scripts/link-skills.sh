#!/usr/bin/env bash
#
# Link every skill in this repo into the local harness skill directories.
#
# Each skill becomes a symlink pointing back into this repo, so the repo stays
# the single source of truth: edit here, and every harness sees the change on
# its next session. Re-run after adding, removing, or renaming a skill.
#
# Destinations:
#   ~/.claude/skills  — Claude Code
#   ~/.agents/skills  — Agent-Skills-standard harnesses (amp, cursor, codex, …)
#                       Disabled by default; pass --agents to include it.
#
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

DESTS=("$HOME/.claude/skills")
if [[ "${1:-}" == "--agents" ]]; then
  DESTS+=("$HOME/.agents/skills")
fi

linked=0
skipped=0

for dest in "${DESTS[@]}"; do
  mkdir -p "$dest"

  while IFS= read -r -d '' skill_md; do
    src="$(dirname "$skill_md")"
    name="$(basename "$src")"
    target="$dest/$name"

    # Refuse to clobber a real file or directory that isn't ours. A pre-existing
    # non-symlink here is hand-authored content, not something to overwrite.
    if [[ -e "$target" && ! -L "$target" ]]; then
      echo "SKIP  $target (exists and is not a symlink)" >&2
      skipped=$((skipped + 1))
      continue
    fi

    ln -sfn "$src" "$target"
    echo "link  $target -> $src"
    linked=$((linked + 1))
  done < <(find "$REPO/skills" -name SKILL.md -not -path '*/node_modules/*' -print0)
done

echo
echo "linked $linked, skipped $skipped"

# Prune symlinks pointing into this repo whose source is gone (renamed/deleted skills).
for dest in "${DESTS[@]}"; do
  [[ -d "$dest" ]] || continue
  for link in "$dest"/*; do
    [[ -L "$link" ]] || continue
    resolved="$(readlink "$link")"
    case "$resolved" in
      "$REPO"/*)
        if [[ ! -e "$link" ]]; then
          echo "prune $link (broken, source removed)"
          rm "$link"
        fi
        ;;
    esac
  done
done
