# Inference

## The two topologies

| | in-process | server |
|---|---|---|
| Who owns the weights | this process | one `mlx_lm.server`, for everyone |
| Cold load | 10–20 s, paid per process | paid once, globally |
| Overhead per call | none | one HTTP hop |
| Concurrency | serialized (Metal is not thread-safe) | server-managed |
| Sampling control | full (`make_sampler`, `make_logits_processors`) | what the HTTP API exposes |
| Adapter swap | free — a separate cached `(model, adapter)` pair | **full weight reload** |

## The selection rule

Written to be *resolvable* rather than judged:

> Use the **server** when the weights would otherwise be loaded more than once
> — a second process, a repeated run of the same script, a non-Python caller,
> or a long-lived interactive session.
>
> Use **in-process** when one process owns the weights for its entire life and
> nothing else needs them — a one-shot worker, a batch job that loops
> internally, or a script that must control memory precisely.
>
> When both descriptions fit, the server wins.
>
> When it isn't decidable at write time, leave `topology = "auto"`: the client
> probes `/health` with a 250 ms timeout and falls back to in-process.
>
> **One exception overrides all of the above:** a workload using a LoRA adapter
> defaults to in-process, because a server adapter swap re-reads the full
> weights (`server.md`).

Topology is resolved **once at construction** and recorded on every
`Completion`. It is deliberately not re-probed per call — a long batch that
silently split itself across two backends halfway through would be
untraceable. Call `llm.reprobe()` explicitly if a long-lived process should
pick up a server that came up later.

## The client

Same call site, either topology:

```python
from local_llm import LocalLLM, Message

llm = LocalLLM()                                  # llm.toml + env
result = llm.chat(
    [Message(role="user", content="Summarize this."), ],
    task="search.summarize",     # applies the token cap AND thinking policy
)
print(result.text, result.topology)               # "inproc" | "server"
```

Explicit construction, ignoring config:

```python
from local_llm import LLMConfig, Tier
llm = LocalLLM(LLMConfig(tier=Tier.FAST, topology="inproc"))
llm = LocalLLM.for_tier("capable", topology="server")
```

### API

```
chat(messages, *, task=None, max_tokens=None, temperature=0.7, top_p=0.95,
     tools=None, enable_thinking=None, stop=None, seed=None) -> Completion
stream(messages, ...) -> Iterator[Chunk]
complete(prompt, ...) -> Completion          # single-turn convenience

count_prompt_tokens(messages) -> int
assert_budget(messages, *, interactive: bool) -> int   # raises PromptBudgetExceeded

topology / tier / model_id / adapter_path    # introspection
refresh_adapter() -> str | None              # pick up a promotion without restarting
reprobe() -> "inproc" | "server"
health() -> dict
close()                                       # also a context manager
```

`Completion` carries `text`, `tool_calls`, `finish_reason`, `prompt_tokens`,
`completion_tokens`, `topology`, `model`, `adapter`, `reasoning`. Every result
records which backend served it, so a run is auditable rather than assumed.

`task=` is the parameter that matters most: it applies `MAX_TOKENS_BY_TASK` and
`SUPPRESS_THINKING_TASKS` from one place, so the two topologies cannot drift
apart on policy. Tier resolution, adapter resolution, token policy, and budget
enforcement all live in `LocalLLM`; a backend only does chat, stream, count,
close.

## Batching

Construct the client **once, outside the loop**:

```python
with LocalLLM(LLMConfig(tier=Tier.CAPABLE, topology="inproc")) as llm:
    for note in notes:                        # load paid once, not len(notes) times
        llm.assert_budget(msgs(note), interactive=False)
        results.append(llm.chat(msgs(note), task="write.short"))
```

Loaded `(model_id, adapter_path)` pairs are cached at module level and shared
across `LocalLLM` instances in the process, so a second client for the same
pair is free. `close()` deliberately does not evict that cache — call
`local_llm._inprocess.clear_cache()` to actually release the memory.

## Metal is not thread-safe

Every in-process generation is serialized through a module-level lock. Threads
will not give you parallel generation; they will give you contention. For real
parallelism, use the server (which manages its own concurrency) or separate
processes — and remember two resident copies of `capable` is 32 GB of 48.

## Where the topologies genuinely differ

- **Sampling.** In-process exposes `make_logits_processors` knobs
  (`repetition_penalty`) that the HTTP API does not. Both support
  `logit_bias`, `temperature`, `top_p`, `seed`.
- **Token counting.** The server has no count endpoint, so
  `count_prompt_tokens` loads the tokenizer locally — tokenizer only, ~10 MB,
  no weights. It is the one place the server topology touches the HF cache.
- **Thinking.** In-process passes `enable_thinking` to `apply_chat_template`
  directly. The server takes it in the request body as **`chat_template_kwargs`**
  — see the naming trap in `server.md`.
