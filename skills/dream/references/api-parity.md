# Dreams API vs. local `/dream`

Researched 2026-10-02 from:
- https://platform.claude.com/docs/en/managed-agents/dreams
- https://platform.claude.com/docs/en/api/beta/dreams/create
- https://platform.claude.com/docs/en/managed-agents/memory
- https://platform.claude.com/docs/en/api/beta/memory_stores/memory_versions/list
- https://claude.com/blog/new-in-claude-managed-agents

At that date the API was in research preview (`dreaming-2026-04-21` beta header, shapes "volatile"). Re-check these pages before changing the skill to match.

## Mapping

| API concept | API behaviour (documented) | Local equivalent |
|---|---|---|
| `memory_store` input | Exactly one store; "the store Claude verifies, deduplicates, and reorganizes" | One `~/.claude/projects/<slug>/memory/` dir |
| `sessions` input | 1–100 caller-chosen ids; "past transcripts Claude mines for patterns" | `--sessions N\|id,id` → `<slug>/<id>.jsonl`, condensed by `extract_sessions.py` |
| `instructions` | ≤4096 chars; focus, preserve, output conventions; "a synthesis pass, … not an editor"; line-level imperatives "generally produce no change" | `--instructions`, same cap, passed verbatim to every agent as steering |
| `model` | One model for all work | Opus orchestrates and verifies; Sonnet mines, consolidates and applies |
| `create_new` output | Clone of input made first, then edited; input "never modified" | `input/store` (frozen) + `output/store` (edited clone) in the run dir |
| `update_existing` | Edits input in place; 409 while another run is active | Not in v1 (roadmap: low-risk rules only) |
| Status | `pending → running → completed \| failed \| canceled` | `status.json`, same values |
| Partial output | Kept on failure or cancel | `output/store` kept; status `failed` |
| Dream session | An archived agent session you can stream | The Claude Code session that ran `/dream` (its JSONL) + the run dir |
| Promote / discard | Attach the output store instead of the input / archive or delete it | `dreamctl.py promote` (swap dirs, archive old) / `discard` |
| Memory versions | Immutable per-write versions, 30-day retention | `~/.claude/dream/archive/<slug>/<ts>/`, kept until you delete it |
| `content_sha256` precondition | Optimistic concurrency on writes | `input/manifest.json`; promote refuses on any drift |
| `input_memory_store_too_large` | Undisclosed size limit | >10k files or any file >100 kB (the API's per-store and per-memory caps) |
| Store guidance | "Many small focused files, not a few large ones"; "condense or prune before the store fills up" | Rules O1 and I1 |

## Documented goal (the one sentence everything else is built from)

> "A dream reads an existing memory store alongside past session transcripts, then produces a new, reorganized memory store: duplicates merged, stale or contradicted entries replaced with the latest value, and new insights surfaced."

Rules D1 (merged), S1/C1 (stale/contradicted → latest), N1 (new insights) come straight from this sentence. O1/I1/F1/L1 come from the store guidance and the local format. P1/X1 are local additions: the API has one store per agent and no user-level CLAUDE.md, and the memory docs warn that a prompt injection can poison a store.

## What is reconstructed, not copied

Anthropic does not publish the dream's prompt, its phase breakdown, whether it uses sub-agents, or its size and time budgets. The phases in SKILL.md (snapshot → mine → consolidate → verify → stage → promote) are inferred from documented behaviour (the clone happens first; the run is an agent session with file tools; there is partial output on failure) and from the patterns in `brainhole-morning` and `test-audit`. Third-party write-ups that describe a "Review → Extract → Update → Prune" cycle cite no Anthropic source.

## Shortfalls

1. **No parity guarantee.** Different prompt, phases and tuning, so quality and coverage will differ, and there is no reference output to compare against. The eval harness on the roadmap is the only way to measure it.
2. **No real versions.** One archive per promote, not one immutable version per write. There is no per-memory history.
3. **Different store format.** Claude Code memory is a flat dir plus a `MEMORY.md` index that loads into every session (a context budget the API store doesn't have). It has no hierarchical paths and no store `description` shown to the agent.
4. **Thin transcript history.** Claude Code prunes old transcripts (here, nothing before about early September 2026), so many stores have no sessions to mine. The digests drop tool results and thinking blocks, which loses signal the API's direct read keeps.
5. **Not a managed job.** The run uses the invoking session's context window and subscription rate limits. There is no server-side timeout or recovery, no event stream (only `status.json`), and no usage or cost accounting.
6. **Self-contamination.** The `/dream` session writes its own transcript into the target project. `snapshot` skips any transcript modified in the last 120 s, but a later dream may mine an earlier dream's session. Pass `--exclude` if that shows up.
7. **Weak concurrency.** The lock is local to this machine and advisory. Claude Code's own memory writes during a run are not blocked; the manifest check only catches them at promote, and the fix is to re-run.
8. **No scheduling.** Manual only in v1. The API has no scheduler either, despite the blog framing.
9. **Heuristic injection defence.** X1 plus "untrusted data" framing. Nothing is sandboxed.
