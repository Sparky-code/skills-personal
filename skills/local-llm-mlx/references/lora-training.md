# LoRA training

## Walk the ladder in order

1. **System-prompt instruction** — minutes, reversible.
2. **Few-shot exemplars** — minutes, reversible. This is what actually changes
   behaviour today in `self-evolve-agent` (`agent/policy.py`'s `promote()`).
3. **LoRA** — a training run plus a promotion decision you now own forever.

Skipping to 3 is the common error. The evidence that rung 3 is warranted looks
like LocalLM's record for `reason.*`: two rounds of prompt experiments, both
measuring *below* the no-prompt baseline. "The model keeps getting our format
wrong and I haven't tried a format instruction yet" is rung 1, not rung 3.

## The toolkit

`LoRA_Local` at `/Users/sparky/Code/LoRA_Local` — a thin wrapper over
`mlx_lm.lora` / `mlx_lm.fuse`. Invoked via `uv run --project`, never imported.
It provides exactly three things: reference configs, a dataset converter, and a
train → smoke-test → report script. It is explicitly not a registry, a tracker,
or an adapter store.

## 1. Convert

```bash
uv run --project /Users/sparky/Code/LoRA_Local lora-local-convert \
  --input  path/to/raw.jsonl \
  --output-dir path/to/data \
  --format completions \
  --field-map '{"prompt": "instruction", "completion": "response"}' \
  --valid-split 0.2
```

| `--format` | Record shape |
|---|---|
| `chat` | `{"messages": [{"role": ..., "content": ...}, ...]}` |
| `completions` | `{"prompt": "...", "completion": "..."}` |
| `text` | `{"text": "..."}` |

Writes `train.jsonl` (+ `valid.jsonl`) into `--output-dir`. Skip `--field-map`
if your data already uses those keys. Malformed records are dropped and
counted, never written, and never abort the batch.

**Minimum size:** at least ~2× `batch_size` records *after* the valid split, or
`mlx_lm.lora` errors out. Ten records is enough for the smoke-test tier.

## 2. Train

```bash
uv run --project /Users/sparky/Code/LoRA_Local lora-local-train \
  --model mlx-community/Qwen3-30B-A3B-4bit \
  --data  path/to/data \
  --adapter-path <YOUR PROJECT>/data/state/adapters/v4 \
  --config /Users/sparky/Code/LoRA_Local/configs/moe-30b-a3b.yaml \
  [--fuse-to path/to/merged-model]
```

`--adapter-path` is required, has no default, and is **rejected if it resolves
inside LoRA_Local**. See `adapters.md`.

Precedence: CLI flags > `--config` YAML > `mlx_lm.lora`'s own defaults.

Runs training (plus `--test` automatically if `test.jsonl` is present), then
loads the adapter and generates once as a crash check, then writes
`lora_local_run_report.json` into the adapter directory with the resolved
config, wall clock, captured output, and the smoke result.

Measured on this machine: the smoke-test config against a 10-record synthetic
set trains the 8B in **~11–14 s** and produces a working adapter.

## The three configs

| File | Target | Deviates from `mlx_lm.lora` defaults |
|---|---|---|
| `dense-8b.yaml` | Dense ~8B | `dropout: 0.05`, `iters: 500`, `mask_prompt: true`, `num_layers: 16` |
| `moe-30b-a3b.yaml` | MoE 30B-A3B | `num_layers: 8`, `keys` restricted to attention only, `grad_checkpoint: true` |
| `smoke-test.yaml` | Any model | `num_layers: 4`, `iters: 20` — correctness only |

**None of these are benchmarked.** `configs/README.md` says so plainly: they are
starting points, not validated hyperparameters, and none has been checked
against a real convergence curve.

## The MoE trap

Read `moe-30b-a3b.yaml`'s header before touching `lora_parameters.keys` on a
mixture-of-experts model.

MLX implements MoE LoRA as `LoRASwitchLinear` — **each targeted MoE block gets a
per-expert adapter**. `Qwen3-30B-A3B` has 128 experts per layer, so unrestricted
`keys` multiplies trainable parameters by up to 128 × 3 projections per block
and the memory cost explodes. The config therefore restricts `keys` to
attention (`q_proj`, `v_proj`) and halves rank to 8.

Peak memory for this config is **unmeasured** — nothing has ever been trained on
the 30B here. Measure it before trusting a long run: `evaluation.md`.

`LoRA_Local`'s own open question, carried forward unresolved: whether it is
worth deliberately targeting `mlp.experts.*` / `mlp.gate` to adapt *routing*
behaviour rather than just attention. That needs an A/B against a real
task-specific dataset, which does not exist yet.

## What the smoke test proves

That the adapter loads and generates without crashing. Nothing else. It is not
a quality gate and `adapters.md` explains why promoting on it is a defect.

## Not covered here

Full fine-tuning, DoRA, DPO/RLHF, dataset curation strategy, and
hyperparameter search. `--fine-tune-type {lora,dora,full}` exists on the CLI;
nothing in this workspace has used anything but `lora`.
