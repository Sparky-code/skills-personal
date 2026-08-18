---
name: interview-mode
description: Use when starting a timed coding interview, take-home exercise, live pairing evaluation, or any session where someone is watching or grading how you steer an agentic coding tool. Enforces plan-first, checkpointed, scope-fenced execution instead of open-ended autonomous building. Trigger phrases — "interview mode", "timed exercise", "coding interview", "take-home", "live coding session", "pairing exercise", "graded exercise".
---

# Interview Mode

## Why this exists

The failure mode this guards against: given an open-ended prompt, the scope of work quietly expands past the stated requirement — extra files, unrequested polish, multi-step autonomous builds — with no checkpoint to catch it. In an interview or timed exercise, what's being evaluated is usually the operator's judgment and control loop, not raw code-generation throughput. This skill trades autonomy for legibility on purpose: smaller, slower, and constantly reviewable beats fast and unsupervised.

This is the session-scoped enforcement layer. The standing, always-on default ("smallest change that satisfies the requirement") lives in global CLAUDE.md under "Agentic Session Discipline" — this skill adds the stricter checkpoint/plan machinery on top, deliberately, only when invoked.

## The contract

1. **Plan before code.** Every task starts with a short plan (files touched, approach, explicit non-goals) — no Edit/Write before it's been read back and approved.
2. **Scope fence every ask.** Definition of done comes from what was stated, not from what would be nice to have. No tests, error handling, retries, or refactors unless asked for.
3. **Checkpoint cadence.** Work proceeds in small increments — one file or one function — then stops and shows the diff. Default to pausing more often than feels necessary; the interviewer's ability to redirect cheaply is the point.
4. **Narrate steering.** When trimming something not requested, say so out loud ("skipping error handling here, wasn't asked for") rather than silently doing the minimal thing.
5. **Ask, don't assume, on ambiguity.** If the requirement is underspecified, surface the ambiguity and propose the narrowest reasonable interpretation rather than picking silently and building on top of the guess.

## Session start checklist

- [ ] State the requirement back in one sentence before writing any code.
- [ ] Produce a plan: files touched, approach, explicit non-goals.
- [ ] Get a go-ahead on the plan before the first Edit/Write.
- [ ] Agree on checkpoint size ("pause after each function", "pause after each file").
- [ ] If the harness supports it, set permission mode so edits require approval rather than auto-accepting (see "Backing this with harness controls" below) — the contract above works better enforced than merely stated.

## Prompt template

Use this shape for each ask within the session:

```
Goal: <one sentence>
Non-goals: <what NOT to build — tests, error handling, refactors, extra files>
Definition of done: <how you'll know this increment is finished>
Stop condition: <where to pause — e.g. "after this file, show the diff and wait">
```

## During execution

- One checkpoint at a time; stop and show the diff before continuing.
- If a change is about to exceed the stated non-goals, stop mid-step and flag it — don't finish and clean up after.
- Default to editing the fewest files that satisfy the requirement.
- Prefer a question over a guess when two reasonable interpretations of the ask diverge.

## Anti-patterns (drift to watch for)

- Building infrastructure or abstractions "for correctness" that weren't asked for.
- Adding tests, error handling, retries, or logging when not requested.
- A multi-file autonomous sweep before the first checkpoint.
- Silently finishing a large change instead of pausing partway to check in.
- Treating an ambiguous requirement as license to build the more impressive version.

## Backing this with harness controls

Prompt-level discipline can slip under time pressure. Where possible, pair it with an actual permission-mode change rather than relying on instructions alone:

- **Per-session (fastest, no config needed):** switch to Plan Mode at the start of the session (shift+tab, or `/plan`), or set the permission mode to `default` (ask before edits) rather than `acceptEdits`/`auto`, so Edit/Write cannot proceed without a stop.
- **Persistent default:** `permissions.defaultMode` in settings.json accepts `"plan"` (require an approved plan before any tool that changes state) or `"default"` (ask before edits, don't auto-accept). This is a manual settings.json edit — see the user's global CLAUDE.md rule on protected config files; propose the exact change, don't apply it directly.

## Debrief (end of session)

After the exercise, capture 3-5 bullets: where did scope actually drift, why, and what plan/prompt step would have caught it earlier. This isn't a retrospective essay — it's tuning input for this skill and for the global CLAUDE.md scope-discipline section. Worth saving as feedback memory if a pattern repeats across sessions.

## Related

- Global CLAUDE.md, "Agentic Session Discipline" — the standing default this skill tightens for graded sessions specifically.
