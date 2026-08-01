# Adapters — the storage contract

`LoRA_Local` refuses to store adapters. `train.py:_assert_outside_repo` exits if
`--adapter-path` resolves inside its own repo:

> `--adapter-path (...) resolves inside LoRA_Local's own repo (...). This
> toolkit never stores adapters for you — point --adapter-path at the consuming
> project's own state directory.`

That refusal is load-bearing. It is the reason a trained adapter lives beside
the project's other versioned state, versioned the way that project already
versions things, instead of in a registry nobody maintains. `LoRA_Local`'s
non-goals say so explicitly: no experiment tracker, no adapter registry, no
auto-discovery, no automatic promote/rollback.

This file is the other half of that contract — the spec every project
implements identically, not an example.

## Layout

```
<project>/data/state/adapters/
  v{n}/            adapter_config.json + adapters.safetensors
                   + lora_local_run_report.json     (LoRA_Local writes these)
  v{n}.json        per-version manifest
  current.json     {"version": n, "path": "v{n}", "promoted_at": ..., ...}
```

Versions are immutable and never deleted. Promotion is the only mutation, and
it is a pointer write.

## `None` means base model

```python
from local_llm import AdapterStore
store = AdapterStore(project_root / "data" / "state" / "adapters")
store.current_path()        # -> "/abs/.../v3"  or  None
```

`None` is the normal, correct state — every project on this machine is in it
right now, because no adapter has ever been promoted anywhere. It feeds
straight through:

```python
from mlx_lm import load
model, tokenizer = load(MODEL_ID, adapter_path=store.current_path())
```

**That `None` is the seam.** Wire the store in at every load site *before* any
adapter exists, and a later promotion needs no code change. Retrofitting it
after the fact is how load sites get missed — which has already happened:
`self-evolve-agent` passes `adapter_path` in four of its five workers and
`agent/_export_type_namer_worker.py:32` calls `load(MODEL_ID)` without it. The
first promotion there will reach four workers and silently skip one, and the
symptom will be inconsistent output rather than an error.

`local_llm.LocalLLM` resolves this for you from `adapter_dir` in `llm.toml`;
`llm.refresh_adapter()` picks up a promotion without restarting the process.

## API

```python
store.current()          -> AdapterVersion | None
store.current_path()     -> str | None            # THE contract
store.versions()         -> list[AdapterVersion]
store.next_version()     -> int
store.reserve()          -> Path                  # creates v{n}/, writes nothing into it
store.promote(n, manifest=...)
store.rollback()         -> int | None            # None = back to base model
```

A pointer at a deleted version degrades to `None` rather than raising — a
broken promotion must not crash a worker mid-batch.

## Promotion needs a gate

```python
from local_llm import train_and_promote

result = train_and_promote(
    store,
    model_id="mlx-community/Qwen3-30B-A3B-4bit",
    data_dir=project / "data/state/lora_training_data",
    config_path=LORA_LOCAL / "configs/moe-30b-a3b.yaml",
    gate=my_held_out_check,        # REQUIRED, no default
)
```

`gate` is required and has no default. This is a **deliberate divergence** from
`self-evolve-agent/agent/adapters/lora.py`, which auto-promotes on exit code 0.

The reason: LoRA_Local's smoke test loads the adapter and generates once. It is
a crash check, not a quality gate — its own report calls it that. Promoting on
it makes an adapter that trained cleanly and learned *nothing* the default for
every consumer of `current.json`. A caller must state what "better" means before
that happens.

`smoke_gate` is provided and **always fails**, with an explanation, so that
"I have no gate yet" is a visible choice rather than a silent default.

Rollback is re-pointing `current.json`. Because versions are immutable, it is
always available and always instant.

## Adapters while iterating, fused models for serving

- **Iterating** → keep it an adapter, in-process. `mlx_lm.load` caches each
  `(model, adapter)` pair separately, so swapping is free.
- **Settled, and the server needs to serve it** → fuse it:
  `lora-local-train --fuse-to <path>`, or `mlx_lm.fuse` directly.

The reason is trap 2 in `server.md`: the server holds one
`(model, adapter, draft)` slot, so every adapter swap re-reads the full weights
(~3 s on the 8B). A fused model is just a model — no per-request adapter, no
reload thrash. Cost is disk: ~8 GB per fused 8B, ~16 GB per fused 30B. With
737 GB free that is affordable, but it is not free.

## Current state

`self-evolve-agent/data/state/adapters/` **does not exist**. No adapter has ever
been trained by any project here. The first one produced on this machine came
out of `verify_stack.py --full`, into a temp directory.

So this contract is currently unexercised in every one of its implementations —
treat the spec above as the thing to build against, not as something battle-worn.
