# Environment

## The canonical interpreter

`/opt/homebrew/bin/python3` — Homebrew Python 3.14.6, holding:

| Package | Version |
|---|---|
| `mlx` | 0.32.0 |
| `mlx-lm` | 0.31.3 |
| `mlx-metal` | 0.32.0 |
| `transformers` | 5.14.1 |

Every measured number in this skill came from this interpreter. Run against it,
or pin the same versions in the project's own environment and say why in that
project's config.

All six CLIs live beside it on the global PATH:
`mlx_lm.generate`, `mlx_lm.server`, `mlx_lm.lora`, `mlx_lm.fuse`,
`mlx_lm.convert`, `mlx_lm.chat`.

Version check that does not initialize Metal:

```python
import importlib.metadata as m
m.version("mlx"), m.version("mlx-lm")   # ("0.32.0", "0.31.3")
```

`mlx` exposes `__version__` only on `mlx.core`, and reading it imports Metal —
use `importlib.metadata` in any preflight.

## The fragmentation map

Four virtualenvs on this machine run MLX, on three different versions. Know
which one you are in.

| Environment | Python | mlx / mlx-lm | Verdict |
|---|---|---|---|
| `/opt/homebrew/bin/python3` | 3.14.6 | 0.32.0 / 0.31.3 | **Canonical. Use this.** |
| `LoRA_Local/.venv` | 3.12.13 | 0.32.0 / 0.31.3 | Fine — uv-managed, pinned, leave it |
| `hackathons/self-evolve-agent/venv` | 3.14.6 | 0.32.0 / 0.31.3 | Fine — also the only place `mlx-vlm`, `mlx-audio`, `mlx-embeddings` exist |
| `projects/InstaGone/venv` | 3.14.6 | 0.32.0 / 0.31.3 | Fine |
| `~/.venvs/brainhole-ai-312` | 3.12.13 | **0.29.3 / 0.29.1** | **Stale by two minor versions** |

The stale one matters more than it looks: `LocalLM/README.md`,
`docs/RUNBOOK.md`, and two files under `docs/artifacts/` all instruct you to
activate `~/.venvs/brainhole-ai-312` — and the latency numbers those same docs
quote were measured in it. Do not adopt it for new work. Migrating LocalLM off
it is that project's decision, outside this skill's scope.

## Declaring the dependency in a new project

Follow `LoRA_Local` — the newest and cleanest precedent in the workspace:

```bash
brew install uv          # if needed
uv python pin 3.12
uv sync
```

```toml
[project]
requires-python = ">=3.12"
dependencies = ["mlx==0.32.0", "mlx-lm==0.31.3", "mlx-metal==0.32.0", "transformers==5.14.1"]

[tool.pytest.ini_options]
markers = ["mlx: requires mlx-lm and cached weights on Apple Silicon (opt-in)"]
addopts = "-m 'not mlx'"
```

Exact pins, not ranges. A silent minor bump changes generation behaviour and
invalidates every number the project recorded.

## Subprocess isolation

The strongest convention in this workspace: MLX work runs in a sibling venv via
subprocess, so the caller carries no hard ML dependency. Two established shapes:

```python
# Worker: JSON file in, JSON file out, via tempfile.TemporaryDirectory
VENV_PYTHON = config.ROOT / "venv" / "bin" / "python"
WORKER = Path(__file__).parent / "_tag_worker.py"
TIMEOUT_SECONDS = 300
```

```bash
# Cross-project tool: uv run --project, never an import
uv run --project /Users/sparky/Code/LoRA_Local lora-local-train ...
```

Both degrade rather than raise — on `CalledProcessError`, `TimeoutExpired`, or
`JSONDecodeError` they return the inputs unchanged. A retrain or tagging pass
must not be able to take down its caller.

Amortize the load: batch **per pass**, never per item. A cold load is 10–20s
and paying it 400 times turns a two-minute job into an hour.

## Lazy imports

Never import `mlx_lm` at module top level — it initializes Metal and costs real
time and memory in a process that may only need config. Guard at the point of
use with `require_mlx()` (`local_llm/_mlx_check.py`, copied from
`LoRA_Local/src/lora_local/_mlx_check.py`).

Set these before anything imports transformers, with `setdefault` so an
explicit override still wins:

```python
os.environ.setdefault("HF_HUB_OFFLINE", "1")       # weights are cached; a surprise
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")  # network call is a stall
```

## The weight cache

`~/.cache/huggingface/hub`, 25 GB. **No `HF_HOME` override is set — do not
introduce one.** A second cache root means a second copy of 16 GB.

| Repo | Size |
|---|---|
| `models--mlx-community--Qwen3-30B-A3B-4bit` | 16 GB |
| `models--mlx-community--Qwen3-8B-8bit` | 8.1 GB |
| `models--nomic-ai--nomic-embed-text-v1.5` | 1.1 GB |
| `models--nomic-ai--nomic-bert-2048` | 112 KB — **remote code only, see `embeddings.md`** |

737 GB free, so disk is not the constraint; the 48 GB of unified memory is.

**Known sediment:** six stale `.incomplete` blobs (some zero-byte) under
`models--nomic-ai--nomic-embed-text-v1.5/blobs/`. Harmless, but they make
cache-size questions unanswerable later. `hf cache scan` lists them.
