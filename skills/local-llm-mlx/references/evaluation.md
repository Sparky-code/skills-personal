# Evaluation

## The three-rung ladder

1. **Does it load?** — `verify_stack.py` checks 1–3.
2. **Does it generate coherently?** — checks 4–7. This is where LoRA_Local's
   smoke test sits, and it is where it stops.
3. **Does it beat the previous thing on held-out data?** — nothing automated
   exists for this rung. It is the rung that gates promotion.

Conflating rung 2 with rung 3 is the specific defect `adapters.md` guards
against: `lora_local_run_report.json`'s `smoke_test.ok` answers rung 2 and says
nothing about rung 3.

## The harness

```bash
cd /Users/sparky/Code/templates/mlx-local-llm
/opt/homebrew/bin/python3 verify_stack.py          # read-only
/opt/homebrew/bin/python3 verify_stack.py --full   # also trains an adapter
```

Eleven checks; every SKIP prints the exact command that would unskip it. `--full`
trains a real (tiny) LoRA adapter and starts a throwaway server on port 8399, so
an already-running server on 8090 is never disturbed.

Unit tests (no MLX, no weights, sub-second):

```bash
uv run --python 3.12 --with pytest python -m pytest tests -q
```

## What a promotion gate must look like

Not the smoke test. At minimum:

- A held-out set the adapter never trained on. `train_and_promote` writes
  `valid.jsonl`; a real gate needs `test.jsonl` too, which makes
  `lora-local-train` run `--test` automatically and record test loss in the run
  report.
- A comparison against the *currently promoted* adapter (or the base model when
  `current.json` is absent), not against nothing.
- A number recorded in the version manifest, so the decision is auditable after
  the fact.

`smoke_gate` deliberately always fails, so "no gate yet" is visible rather than
silent.

Watch the data-size floor: `self-evolve-agent` retrains at
`RETRAIN_BATCH_SIZE = 5`, which is too few rows to hold out anything
meaningful — its `lora.py` reuses the training rows as `valid.jsonl` and says
so in a comment. At that scale you have a loss-sanity check, not a
generalization measure. Say which one you have.

## Recorded negative results — do not re-run these

From LocalLM's experiment log:

| Change | Result |
|---|---|
| Token caps on `write.short` / `search.summarize` | **−0.54 / −0.37** — reverted; truncation hurt quality |
| Prompt rewrites for `reason.compare` / `reason.plan` (two rounds) | Both **below** the no-prompt baseline; structure prompts caused shallow hedging — the model filled in structure without committing |
| Suppressing thinking on `search.retrieve` | **−0.15** — removed from the suppression set in M5f |
| Code-pitfalls review checklist | Catch rate unchanged at 75%, false positives up **0/6 → 2/6** |

The general lesson those encode: on these models, verbosity and quality problems
are not fixed by caps or by more prompt structure. That is the evidence base for
reaching for LoRA on `reason.*` — and the reason not to reach for it elsewhere
before rungs 1 and 2 of the ladder in `lora-training.md` have actually been tried.

## Standing open work

Each is a stub with a concrete resolving step, not an unknown.

1. **Re-measure latency under the current runtime.** Every canonized number came
   from mlx-lm 0.29.1 in June; the canonical runtime is 0.31.3 / mlx 0.32.0.
   The tier rule is architectural and safe regardless, but the breakpoints may
   have moved.
   → `/opt/homebrew/bin/python3 LocalLM/brainhole/tools/bench_context.py`
   against both tiers at 512 / 4096 / 16384, then update `model-tiers.md`.

2. **MoE LoRA peak memory.** Nothing has ever been trained on the 30B here, and
   `configs/README.md` states plainly that none of the configs are benchmarked.
   → `lora-local-train --model mlx-community/Qwen3-30B-A3B-4bit --config
   configs/smoke-test.yaml` against a 10-record synthetic set; read peak memory
   out of the run report. Minutes.

3. **Adapter reload cost on the server, at the capable tier.** Measured at ~3 s
   on the 8B (`verify_stack.py` check 11). The 30B is unmeasured.

4. **Batching and concurrency.** `--decode-concurrency`,
   `--prompt-concurrency`, `--prefill-step-size` are all at defaults, and
   `is_batchable` additionally requires every prompt-cache entry to expose
   `merge` — unverified for `qwen3_moe`.
   → Inspect `ModelProvider.is_batchable` for both tiers, then compare
   aggregate throughput for 4 concurrent requests against serial.

5. **Speculative decoding.** The server accepts `--draft-model`, but no small
   Qwen3 is cached, and loading a draft model forces `is_batchable` False — so
   speculation and batching are mutually exclusive and it is unknown which wins
   here.
   → Download `mlx-community/Qwen3-0.6B-8bit` (~700 MB; vocab 151936 matches,
   so the server's mismatch warning should not fire) and measure both ways.

6. **Prompt caching across turns.** `--prompt-cache-bytes`, `mlx_lm.cache_prompt`,
   and in-process `make_prompt_cache` all exist. Whether reuse across turns is
   worth the complexity at a 512-token interactive budget is unmeasured, so it
   is left out of the client's API entirely rather than half-wired.
   → Measure TTFT on turn 2 of a 10-turn conversation, with and without.

7. **Structured output without constrained decoding.** No local schema
   enforcement exists (`agent-integration.md`). The interim is
   prompt → validate → retry.
   → Evaluate `outlines` and mlx-lm logit processors against InstaGone's
   existing classification set, which is a real labelled corpus.

8. **Embeddings migration.** See `embeddings.md` — blocked on a re-index
   decision that belongs to LocalLM.
