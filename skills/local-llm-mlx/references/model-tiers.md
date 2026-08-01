# Model tiers

## The tier rule, first, because it is counterintuitive

**`capable` is both the better AND the faster tier. `fast` is the *smaller*
model, not the quicker one.** Pick `fast` only when memory is the binding
constraint — never for speed.

`Qwen3-30B-A3B` is a mixture-of-experts model: 30B total parameters, but only
~3B active per token. It therefore beats the dense 8B on both measured prefill
breakpoints while costing twice the resident memory.

The names come from `LocalLM/brainhole/models/config.py` (`FAST_MODEL`,
`CAPABLE_MODEL`) and are kept for compatibility with the four projects already
using them. Renaming them to `SMALL`/`LARGE` would be a strict improvement and
is LocalLM's decision to make, not this skill's.

## The tiers

| Tier | Model | Arch | Resident | Notes |
|---|---|---|---|---|
| `capable` | `mlx-community/Qwen3-30B-A3B-4bit` | `qwen3_moe`, 48 layers, 128 experts | **16 GB** | The default |
| `fast` | `mlx-community/Qwen3-8B-8bit` | `qwen3`, 36 layers, dense | **8.1 GB** | Memory-constrained fallback |
| `embed` | `mlx-community/Qwen3-Embedding-0.6B-8bit` | `qwen3`, dim 1024 | ~0.7 GB | **Not downloaded — see `embeddings.md`** |

Both chat tiers have a 40960-token context window. Both are already cached; the
embed tier is not.

## Measured prefill

From `LocalLM/brainhole/models/config.py` (RFC-C1, resolved 2026-06-02):

| Prompt tokens | `capable` | `fast` | Verdict |
|---|---|---|---|
| 512 | 0.63 s | 1.15 s | Interactive budget |
| 4096 | 5.01 s | 9.33 s | Background budget |
| 16384 | 31 s | 46 s | **Outside every budget** |

Throughput, from the vault's `01 Projects/LocalLM/Architecture.md`:
8B Q8 ≈ 30 tok/s at 8.8 GB; 30B-A3B Q4 ≈ 92 tok/s at 17.3 GB.

**Provenance caveat.** These were measured under mlx-lm 0.29.1 in
`~/.venvs/brainhole-ai-312`. The canonical runtime is 0.31.3 / mlx 0.32.0.
They are the best numbers in existence for this machine and should be used;
the tier rule they imply is architectural (active-parameter count) and is safe
regardless. The specific breakpoints may have moved — `evaluation.md` carries
the standing re-measure task.

## Budgets

Prefill is the entire latency story here, and it degrades **silently**: nothing
errors at 16k, the model just stops feeling usable.

```python
MAX_INTERACTIVE_TOKENS = 512   # a human is waiting
MAX_BACKGROUND_TOKENS  = 4096  # nobody is waiting
```

`LocalLLM.assert_budget(messages, interactive=True)` turns exceeding these into
a `PromptBudgetExceeded` carrying the actual count and the limit. Check the
count; don't estimate it.

Generation caps (M5a, exp-v3 validated 2026-07-04) — raising them was neutral
to positive, lowering them measurably hurt:

```python
MAX_TOKENS_DEFAULT = 1000
MAX_TOKENS_BY_TASK = {
    "write.long": 2000, "reason.plan": 1500,
    "code.write": 2000, "code.explain": 2000,
    "code.review": 2000, "code.debug": 2000,
}
```

Thinking suppression (M5d/M5f) — `enable_thinking=False` for direct,
format-matched tasks:

```python
SUPPRESS_THINKING_TASKS = frozenset({"write.short", "search.summarize"})
```

`search.retrieve` was in this set and was **removed** in M5f: suppressing
thinking there measured −0.15. Thinking helps the model evaluate context
quality before answering. Don't add it back without a measurement.

Pass `task="code.write"` to `LocalLLM.chat()` and both the token cap and the
thinking decision are applied from these tables — that is the whole point of
the parameter.

## Memory arithmetic on 48 GB

| Combination | Total | Verdict |
|---|---|---|
| `capable` alone | 16 GB | Comfortable |
| `fast` alone | 8.1 GB | Trivial |
| `capable` + `fast` | 24.1 GB | Fits, but leaves little for anything else |
| `capable` × 2 processes | 32 GB | **Starts swapping — this is what the server prevents** |
| `capable` + a LoRA training run | — | **Not a combination.** Train, then serve |

Two resident copies of `capable` is the specific failure the server topology
exists to prevent. See `inference.md`.

## Models not on disk

Only the two chat models and the nomic embedder are cached. Anything else is a
download decision with a real cost (16 GB is not a rounding error), so **stop
and ask** rather than letting `mlx_lm.load` silently pull a new repo. The
benchmark harness for evaluating a candidate already exists at
`LocalLM/brainhole/tools/bench_context.py`.
