---
name: local-llm-mlx
description: Use whenever running a model locally or offline on this Mac, loading a model with mlx_lm, choosing between the local model tiers, starting or calling mlx_lm.server, LoRA fine-tuning a local model, wiring a trained adapter into a project, embedding text for local retrieval, or giving a local model tools. Defines the one default local-LLM stack for /Users/sparky/Code.
---

# Local LLM MLX Stack

This is the default, non-negotiable stack for local model work anywhere under `/Users/sparky/Code`, unless a project explicitly overrides it.

The stack: **MLX** via **mlx-lm** on the Homebrew interpreter, two chat tiers — **Qwen3-30B-A3B-4bit** (`capable`, the default) and **Qwen3-8B-8bit** (`fast`, the memory-constrained fallback) — reached through **one client** that runs either in-process or against **`mlx_lm.server`** on port 8090, **LoRA_Local** for training adapters and the **`v{n}` / `current.json` promotion contract** for storing them, and an **MLX-native embedder with remote code execution off, always**.

Every project reaches the models through the same client, so a tier change, an adapter promotion, or a topology switch is one edit instead of thirty. This isn't a stylistic preference — it's the fix for a real, already-observed failure mode: this workspace has a local-inference *ecosystem* and no local-inference *client*. `from mlx_lm import load` appears at roughly thirty call sites across four projects; `mlx-community/Qwen3-30B-A3B-4bit` is re-declared as a bare string in six files inside `self-evolve-agent` alone, none of which import LocalLM's `CAPABLE_MODEL`; five of those six pass an adapter path and the sixth silently doesn't, so the first promoted adapter will reach four workers and skip one; three virtualenvs run three different mlx-lm versions, and the one LocalLM's own README tells you to activate is two minor versions behind the interpreter whose latency numbers that README quotes; and an `mlx_lm.server` has sat resident on port 8090 holding 1.2 GB while zero files in the workspace mention that port. One client, one config, one adapter contract is what stops all of that from being re-derived a fifth time, and it's why the checklist below treats a literal model ID in project code as a defect rather than a shortcut.

## Why each layer was picked

- **MLX + mlx-lm, not Ollama / llama.cpp / LM Studio** — none of those are installed and no GGUF exists on this machine; unified memory removes the host-to-device copy entirely; and `mlx_lm.lora` means training and inference share one runtime instead of being two stacks that can disagree. Both alternatives were formally evaluated and rejected here already.
- **Qwen3-30B-A3B-4bit as the default tier** — a 3B-active MoE that beats the dense 8B at *both* prefill and generation on this box. "Capable" costs memory (16 GB resident vs 8.1 GB), not latency.
- **Qwen3-8B-8bit as the fallback tier** — 8 bits of a dense 8B is the highest-fidelity thing that still fits when something else already owns half the 48 GB.
- **One client over two topologies** — in-process owns the weights and pays the load once per process; the server pays it once for everyone. Which is correct changes as a project grows from a script into a service, and the call site must not have to change with it.
- **`mlx_lm.server` on a fixed port, OpenAI-compatible** — the only way a second process, a second language, or a shell one-liner reaches these weights without loading a second 16 GB copy.
- **LoRA_Local trains, the consuming project stores** — the trainer refuses to write adapters into itself, which is the only reason adapter versions can live beside a project's other versioned state instead of in a registry nobody maintains.
- **MLX-native embeddings with remote code off** — the incumbent nomic path has already deposited third-party Python in the weight cache to be executed on every embed call.

## Canonical paths

- `/opt/homebrew/bin/python3` — the canonical interpreter: mlx 0.32.0, mlx-lm 0.31.3, transformers 5.14.1. All `mlx_lm.*` CLIs sit beside it on the global PATH.
- `~/.cache/huggingface/hub` — the only weight cache. No `HF_HOME` override is set; don't introduce one.
- `/Users/sparky/Code/templates/mlx-local-llm/` — the template. Copy `src/local_llm/` into the project and `llm.toml.example` to `llm.toml`.
- `/Users/sparky/Code/LoRA_Local/` — the trainer. Invoked as `uv run --project`, never imported.
- `/Users/sparky/Code/LoRA_Local/configs/` — `dense-8b.yaml`, `moe-30b-a3b.yaml`, `smoke-test.yaml`.
- `<project>/data/state/adapters/` — where a project's own adapters live: `v{n}/`, `v{n}.json`, `current.json`.
- `http://127.0.0.1:8090` — the workspace's one server port.
- `/Users/sparky/Code/LocalLM/brainhole/models/config.py` — the source of every measured latency and token-budget number this skill canonizes.

If a path doesn't exist yet, treat the values documented in `references/` as the spec to implement against, not as an optional detail to improvise.

## Measured defaults

- **Prompt budget** — 512 tokens for anything a human is waiting on (prefill 0.63s capable / 1.15s fast), 4096 for background work (5.01s / 9.33s). A 16k prompt costs 31s and 46s of prefill *before the first token* and is outside both budgets.
- **Generation cap** — 1000 tokens by default; 2000 for long-form writing and all four `code.*` categories; 1500 for planning. Raising these was validated; lowering them measurably hurt quality.
- **Thinking** — `enable_thinking=False` for direct, format-matched tasks (short writing, summarization); leave it on for reasoning and long-form. Suppressing it on retrieval measured worse and was reverted.
- **Provenance** — these were measured under mlx-lm 0.29.1 in June. They are the best numbers in existence for this machine and should be used; `references/evaluation.md` carries the re-measure task.

## Decision tree

- **A human is waiting on the answer** → `capable` tier, server topology, prompt under 512 tokens.
  The bigger model is the lower-latency one here, and the server means its 16 GB is already resident so the turn starts immediately instead of after a cold load.
  Triggers: "ask the local model", "chat with it", a TUI/REPL/interactive loop, "what does the local LLM say about…", anything with a person at a keyboard.

- **A batch or one-shot worker process owns the weights for its whole life** → in-process `load()`, tier by memory headroom, prompt under 4096 tokens.
  The process pays one load and amortizes it across the loop; routing through HTTP adds a hop and a second copy of the weights for nothing.
  Triggers: "tag/classify/extract over these N items", "run it across the whole vault", a subprocess worker, a cron or launchd job, "score every row".

- **A second process, a second language, or a repeated run needs the same weights** → the server, always.
  Two resident copies of the capable tier is 32 GB of 48 and the machine starts swapping; this is the branch the orphaned server on 8090 was started for and never got used by.
  Triggers: "call it from the shell / from Node / from the dashboard", "two things need the model", "I don't want to wait for it to load every time", curl, any OpenAI-compatible client library.

- **The model keeps making the same mistake and prompting has stopped helping** → LoRA, via LoRA_Local, stored under the project's own `adapters/`.
  Walk the ladder in order — prompt, then few-shot exemplars, then LoRA — because the first two are minutes and reversible and the third is a training run plus a promotion decision you own forever.
  Triggers: "fine-tune it", "train it on our data", "make it better at X", "it always gets our format wrong", "teach it our taxonomy".

- **Retrieval, semantic search, clustering, or "find things like this"** → the embed tier, MLX-native, remote code off.
  Not the chat tiers, and not the currently-configured nomic path, which requires executing downloaded Python — read `references/embeddings.md` before writing any embedding code.
  Triggers: "semantic search", "find similar", "RAG", "index these notes", "vector store", "embeddings", "nearest neighbours".

- **A project already has its own model layer** → do not impose this skill.
  Flag the conflict and ask, rather than adding a second competing way to reach the same weights into a codebase that already picked one — that is precisely the failure this skill exists to stop.
  Triggers: the project already defines its own `MODEL_ID`, its own loader, or its own adapter convention; or the user names an existing local-model setup.

Full topology selection rule and the tier matrix: `references/inference.md` and `references/model-tiers.md`.

## Mandatory checklist for every local-model task

- [ ] Resolve the model ID and tier from the shared config — never write a `mlx-community/…` string literal into project code.
  Six files in `self-evolve-agent` already carry that literal; changing tier there is a six-file edit, and six-file edits get done five-sixths of the way.

- [ ] Resolve the adapter through the store at every load site, even before any adapter exists — `None` means base model and is a valid answer.
  Four of those six workers pass an adapter path and `_export_type_namer_worker.py` doesn't; the first promotion will silently apply to four of five workers, and the symptom will be inconsistent output rather than an error.

- [ ] Run against the canonical interpreter, or pin the same mlx/mlx-lm versions and say why in the project's own config.
  `~/.venvs/brainhole-ai-312` runs mlx-lm 0.29.1 while the CLIs on PATH are 0.31.3 — same code, same weights, different runtime than the one every measured number here came from.

- [ ] Keep `trust_remote_code` off, and decline any model whose config carries an `auto_map`.
  It has already put `modeling_hf_nomic_bert.py` in the weight cache to be executed on every embedding call; the fix is a different model, not a code review of someone else's file.

- [ ] Check the prompt token count rather than estimating it, and keep interactive prompts under 512 and background prompts under 4096.
  Prefill is the whole latency story here: 16k of context is 31–46 seconds before a single token appears, and it degrades silently — nothing errors, the model just stops feeling usable.

- [ ] Construct the client once, outside the loop.
  A cold load is 10–20 seconds; paying it per item is how a two-minute batch becomes an hour.

- [ ] Promote a trained adapter only after a held-out check passes — the trainer's smoke test is a crash check, not a quality gate.
  Promoting on exit code 0 makes an adapter that trained cleanly and learned nothing the default for every consumer of `current.json`.

## Scaffolding

Copy `src/local_llm/` out of `/Users/sparky/Code/templates/mlx-local-llm/` into the project, and `llm.toml.example` to `llm.toml`. It is vendored, not depended on — the same ownership model `frontend-ui-stack` uses for shadcn components, and the only one that survives the four different virtualenvs on this machine.

Verify before building on it: `verify_stack.py` runs eleven checks against real weights, and `--full` additionally trains an adapter end to end. Both pass on this machine today.

## Reference index

- `references/environment.md` — the canonical interpreter, the version-drift map across four virtualenvs, how a project declares its MLX dependency, subprocess isolation, and cache hygiene. Open before running anything, and before adding a local-model dependency to a project.
  Includes the exact version matrix per venv and which repo's docs will wrongly tell you to use the stale one.
- `references/model-tiers.md` — the two chat tiers, the embed tier, resident sizes, measured prefill and throughput, and the token and thinking policy. Open before choosing a model or a token limit.
  Leads with why `fast` is the *smaller* model and not the quicker one.
- `references/inference.md` — the two topologies, the selection rule, and the client's full API. Open before writing any code that calls a model.
  States the topology decision as a resolvable rule rather than a judgement call.
- `references/server.md` — port convention, lifecycle, `/health`, `/v1/models`, per-request model and adapter selection, and reload cost. Open before starting, stopping, or calling the server.
  Documents four verified traps, including a CLI flag that silently does nothing and a response shape that can omit `content` entirely.
- `references/lora-training.md` — the prompt → few-shot → LoRA ladder, dataset shapes, the three configs, and the MoE per-expert memory trap. Open before any fine-tuning work.
  Explains why `moe-30b-a3b.yaml` restricts `keys` to attention and what happens if you don't.
- `references/adapters.md` — the `v{n}` / `current.json` storage and promotion contract, rollback, and adapters versus fusing. Open before storing, loading, promoting, or serving a trained adapter.
  This is the one contract every project implements identically; it is written as the spec, not as an example.
- `references/agent-integration.md` — tool calling on both topologies, structured output without constrained decoding, thinking control, and the agent-loop shape. Open before giving a local model tools or expecting it to emit JSON.
  Confirms which tool parser Qwen3 gets, and that there is no grammar or schema enforcement to fall back on.
- `references/embeddings.md` — the `trust_remote_code` conflict, the recommended MLX-native embedder, and the migration off nomic. Open before writing any embedding or retrieval code.
  States what breaks when the dimension changes from 768 to 1024, and the escape hatch when re-indexing isn't affordable yet.
- `references/evaluation.md` — the smoke ladder, what a promotion gate must contain, and the standing open measurements. Open before claiming a model, prompt, or adapter change helped.
  Carries the negative results already recorded in LocalLM, so the same prompt experiments aren't re-run.

## Scope

This skill governs new local-model work under `/Users/sparky/Code` only. It does not retroactively migrate `LocalLM`, `self-evolve-agent`, or `InstaGone` — their version drift, their duplicated model IDs, and LocalLM's `EMBED_TRUST_REMOTE_CODE = True` are recorded here as known deviations, and migrating them is a separate, larger decision than anything this skill should trigger on its own. Also out of scope: cloud model selection (that's the `claude-api` skill), vision and audio work via `mlx-vlm` / `mlx-audio`, and any model not already in the cache without an explicit download decision. Within scope, treat this file as the index: it holds only what every branch needs, and anything deeper lives in `references/` and is loaded when a branch actually reaches it.

## Worked examples

**"Have the local model tag these 400 notes."**
1. Branch 2 — a batch job that owns the weights for its whole life, so in-process, and `capable` unless something else is already resident (`references/inference.md`).
2. Vendor `src/local_llm/` and declare tier and adapter dir in `llm.toml`; don't write the repo id into the worker.
3. Construct the client once outside the loop — the load is 10–20 seconds and must not be paid 400 times.
4. Cap each note's prompt at 4096 tokens with `assert_budget(..., interactive=False)`. 400 items times an unbudgeted prefill is where a two-minute job becomes an hour.
5. Pass `task="write.short"` so the token cap and thinking suppression both come from the measured table rather than being invented.
6. Done when: every `Completion.topology` reads `inproc`, no model ID appears anywhere in the worker, and re-running it after promoting an adapter picks the adapter up with no code change.

**"Fine-tune it so it stops getting our tag format wrong."**
The checklist stops a training run here. Walk the ladder first (`references/lora-training.md`): a format instruction in the system prompt, then few-shot exemplars — both are minutes and reversible. If those have genuinely been tried and failed, then convert the data with `lora-local-convert`, train with `lora-local-train` pointed at *your project's* `data/state/adapters/v{n}/`, gate on a held-out set, and only then update `current.json`. Keep it an adapter while iterating; fuse only once one has settled and the server needs to serve it (`references/adapters.md`).

## Anti-patterns

- Don't write a `mlx-community/…` string into project code — resolve the tier from config.
- Don't pick the 8B because it's called "fast" — it's the smaller model, not the quicker one.
- Don't call `mlx_lm.load` directly from application code — go through the client so topology stays swappable.
- Don't load the same weights in two processes — that's what the server is for.
- Don't construct the client inside a loop — the load cost is seconds, not milliseconds.
- Don't pass `trust_remote_code=True`, and don't adopt a model that needs it.
- Don't rely on `mlx_lm.server --adapter-path` — it's a no-op in 0.31.3; send `"adapters"` per request, or fuse.
- Don't send `chat_template_args` in a request body — the request field is `chat_template_kwargs`, and the wrong key is ignored silently.
- Don't swap adapters per request on a hot server — every swap re-reads the full weights.
- Don't store adapters inside LoRA_Local — it refuses, on purpose, and the refusal is the contract.
- Don't promote an adapter on a green smoke test — that only proves it loads.
- Don't ask for JSON and assume you'll get it — there's no constrained decoding; validate and retry.
- Don't activate `~/.venvs/brainhole-ai-312` for new work — it's two mlx minor versions stale.
