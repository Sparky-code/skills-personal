# The server

OpenAI-compatible, one port workspace-wide: **8090**.

```bash
mlx_lm.server --model mlx-community/Qwen3-8B-8bit --port 8090 \
  --chat-template-args '{"enable_thinking":false}'
```

That is the invocation currently running on this machine. Note the CLI flag is
`--chat-template-args`; the *request body* field is `chat_template_kwargs`.
They are not the same name — see trap 3.

## Endpoints

```bash
curl -s http://127.0.0.1:8090/health
curl -s http://127.0.0.1:8090/v1/models        # lists every CACHED model, not just the loaded one
curl -s http://127.0.0.1:8090/v1/chat/completions -H 'Content-Type: application/json' -d '{
  "model": "mlx-community/Qwen3-8B-8bit",
  "messages": [{"role": "user", "content": "Say hello."}],
  "max_tokens": 40, "temperature": 0.0,
  "chat_template_kwargs": {"enable_thinking": false}
}'
```

`/v1/models` listing a model does **not** mean it is loaded — it means it is in
the HF cache and can be requested. Requesting a different one costs a full
reload (trap 2).

Send the resolved repo id as `model`, not `"default_model"`. The client does
this, so it works against a server started with either tier.

## Four verified traps

All four were read out of `/opt/homebrew/lib/python3.14/site-packages/mlx_lm/server.py`
at 0.31.3, and traps 1–3 were then confirmed by execution
(`templates/mlx-local-llm/verify_stack.py --full`, check 11). Re-verify after
any upgrade.

### 1. `--adapter-path` on the CLI is a no-op

`ModelProvider.load` (server.py:387–389):

```python
model_path   = self._model_map.get(model_path, model_path)      # "default_model" -> real repo id
adapter_path = self._adapter_map.get(model_path, adapter_path)  # looks up the RESOLVED id
```

`_adapter_map` is only ever keyed `"default_model"` (server.py:316), but by the
second line `model_path` has already been rewritten to the real repo id, so the
lookup always misses and the CLI adapter never reaches `_load()`. This is also
true at startup, which calls `load("default_model", None, "default_model")`.

**Confirmed by execution.** A server started with `--adapter-path` pointing at
an adapter trained to answer "Say hello." with exactly `"Hello!"` instead
returned the base model's `"Hello! How can I assist you today? 😊"`. The same
server, given the per-request field, returned `"Hello!"`.

**Therefore:** the only working ways to serve an adapter are the per-request
`"adapters"` field, or fusing (`lora-training.md`).

### 2. One model slot — every swap is a full reload

`self.model_key = (model_path, adapter_path, draft_model_path)` is a single
value (server.py:377, 393). Any change calls `_load()`, which re-reads the
weights. There is no multi-model cache.

Measured: ~3 s to swap in a LoRA adapter on the 8B tier.

**Therefore:** batch by adapter and by model. A mixed workload alternating base
and adapter, or `fast` and `capable`, per request will thrash. Adapter A/B
testing over HTTP is batch-by-adapter, not interleaved — and while iterating on
an adapter at all, the in-process backend is the right answer.

### 3. The request field is `chat_template_kwargs`, not `chat_template_args`

server.py:1192 reads `self.body.get("chat_template_kwargs")`; the CLI flag is
`--chat-template-args`. An unknown body key is **silently ignored**, so sending
the CLI spelling leaves thinking ON with no error and no warning.

Per-request kwargs are merged over the CLI defaults (server.py:544–547), so a
server started with thinking off can have it turned back on per request.

### 4. A response can have no `content` key at all

The server pre-splits thinking: it returns `reasoning` as its own field on the
message rather than inline `<think>` tags, and **omits `content` entirely** when
the whole token budget went to reasoning. Observed:

```json
{"choices": [{"finish_reason": "length",
  "message": {"role": "assistant",
              "reasoning": "\nOkay, the user said \"Say hello.\"..."}}]}
```

`message["content"]` raises `KeyError`. Read it as `.get("content") or ""` and
read `reasoning` separately — which is what `local_llm/_server.py` does. This
also means a small `max_tokens` with thinking on can return nothing usable;
either raise the cap or suppress thinking.

## Adapters over HTTP

```json
{"model": "mlx-community/Qwen3-8B-8bit",
 "messages": [...],
 "adapters": "/abs/path/to/data/state/adapters/v3"}
```

The field is `"adapters"` (plural) and takes a single absolute path. The client
sends it only when `allow_server_adapter = true`, and warns once about the
reload cost. Default is false, which routes adapter workloads in-process.

## Lifecycle

The server currently on 8090 was started by hand, has held ~1.2 GB since 08:56,
and **nothing in the workspace calls it** — grepping every `.py`, `.md`, `.sh`,
`.json`, and `.plist` under `/Users/sparky/Code` plus `~/Library/LaunchAgents`
for `8090` returns zero hits.

Resolve that one way or the other. Either register it —a launchd plist modelled
on the existing `com.sparky.dashboard.plist`, plus a `/health` entry in
`projects/dashboard/config/projects.json` alongside the other health checks —
or stop it. An unmanaged resident process that nothing calls is the third state
and the worst one.

Use a scratch port (e.g. 8399) for any experiment, so an already-running server
is never disturbed.

## Out of scope

Distributed/sharded serving (`--pipeline`, `mx.distributed`) is irrelevant on
one Mac, and adapters are explicitly unsupported in that mode
(server.py:329–331). Batching and concurrency tuning
(`--decode-concurrency`, `--prompt-concurrency`, `--prefill-step-size`) are
untuned and unmeasured here; `evaluation.md` carries them as open work.
