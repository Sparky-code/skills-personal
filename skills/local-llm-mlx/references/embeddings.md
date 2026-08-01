# Embeddings — STUB, and a live conflict

## The conflict, first

The standing rule in this workspace is that `trust_remote_code=True` is an
unacceptable security vector. `LocalLM/brainhole/models/config.py` sets:

```python
EMBED_MODEL = "nomic-ai/nomic-embed-text-v1.5"
EMBED_TRUST_REMOTE_CODE = True
```

This is not a hypothetical exposure. The consequence is already on disk:

```
~/.cache/huggingface/hub/models--nomic-ai--nomic-bert-2048/
    configuration_hf_nomic_bert.py
    modeling_hf_nomic_bert.py
```

That directory contains **only those two files** — no weights. It is
third-party Python, fetched via `auto_map` in the nomic model config, executed
in-process on every single embed call.

This template does not set the flag, and `LLMConfig.__post_init__` raises
`ConfigError` if anyone tries to turn it on. `verify_stack.py` check 3 scans
every selectable model's config for `auto_map` and fails if one appears — the
rule as an executable test rather than a promise.

**"Keep the model, change the loader" is not available.** `mlx-embeddings`
ships `bert`, `modernbert`, `xlm_roberta`, `qwen3`, `gemma3_text`, `lfm2`,
`llama_bidirec`, and `siglip`. Nomic's `model_type` is `nomic_bert`, which is
not among them.

## Why this is a stub rather than a fix

Nothing here is conceptually unresolved — it is unbuilt, and building it has a
cost that belongs to someone else. Changing the embedding model changes the
vector dimension, which **invalidates LocalLM's existing LanceDB index**. That
is a re-index nobody has scheduled, and this skill's scope is new work.

So: the conflict is flagged, the recommendation is written down, and
`local_llm/embeddings.py` raises `NotImplementedError` with the resolution steps
in the message.

## The three options

### 1. RECOMMENDED — `mlx-community/Qwen3-Embedding-0.6B-8bit`

MLX-native, same family as the chat tiers, `model_type: qwen3`, 28 layers,
32k context, ~645 MB, dim **1024**. **No `auto_map`, no remote code.** Loads
through `mlx-embeddings`, whose deps (`mlx>=0.31.1`, `transformers>=5.0.0`) are
already satisfied by the canonical env.

Costs:
- One download (~645 MB).
- `mlx-embeddings` pulls `mlx-vlm>=0.4.0` transitively — a wart, since nothing
  here does vision.
- 768 → 1024 forces a **full re-index** of any existing vector store.

**Its query format is asymmetric and differs from nomic's.** Queries get
`Instruct: {task}\nQuery: {q}`; documents get **no prefix at all**. Carrying
nomic's `search_document: ` / `search_query: ` prefixes across would degrade
retrieval quality silently, with nothing to error on. `local_llm.embeddings`
ships `format_query()` written correctly for exactly this reason.

### 2. ESCAPE HATCH — the ONNX snapshot already on disk

```
~/.cache/huggingface/hub/models--nomic-ai--nomic-embed-text-v1.5/snapshots/*/onnx/model.onnx
```

547 MB, already downloaded. ONNX Runtime executes a **graph, not Python**, so
remote code genuinely never runs — this is a real fix, not a containment. The
`nomic_bert` architecture is baked into the graph, dim stays 768, and the
existing index and prefixes stay valid.

Costs: adds `onnxruntime`, and mean pooling + L2 normalization + Matryoshka
truncation must be reimplemented by hand, because `sentence-transformers` was
doing them for you.

Take this when the re-index is not affordable *yet* and the rule needs
satisfying *now*.

### 3. REJECTED — pin a reviewed revision and document an exception

Reviewing and pinning a specific commit of someone else's
`modeling_hf_nomic_bert.py` does not make executing it acceptable, and it
converts a hard rule into a case-by-case judgement. That is how hard rules die.
Named here so it is not rediscovered as a shortcut.

## Resolution steps for option 1

1. `uv pip install mlx-embeddings` into the canonical env; confirm the
   `mlx-vlm` pull is tolerable.
2. `hf download mlx-community/Qwen3-Embedding-0.6B-8bit`.
3. Embed a fixed 20-sentence set with both models and compare retrieval rank
   agreement on a real query set, against LocalLM's existing
   `RETRIEVAL_MAX_DISTANCE = 0.7` baseline — so the re-index is a decision with
   a number behind it.

**Blocking dependency:** whoever owns LocalLM's LanceDB index has to agree to
re-index before option 1 lands there.

## Housekeeping

Six stale `.incomplete` blobs (some zero-byte) sit under
`models--nomic-ai--nomic-embed-text-v1.5/blobs/`, left by aborted downloads.
Harmless, but worth clearing whichever option wins.

## Not covered here

The vector store itself. LanceDB configuration, chunking strategy, and
`RETRIEVAL_MAX_DISTANCE` stay LocalLM's business; this file only governs which
embedder produces the vectors and under what security constraint.
