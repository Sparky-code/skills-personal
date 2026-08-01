# Agent integration

## No framework

The standing decision in this workspace, recorded in LocalLM's RFC-C3 and
reaffirmed in RFC-C8:

> No framework (no LangChain, no LlamaIndex). Direct `mlx_lm` calls + `mcp`
> client.

A tool loop is about twenty lines. A framework is a dependency, a second way to
describe the same functions, and a layer between you and the chat template you
will eventually need to debug. Keep the direct tool registry; MCP servers stay
available for *external* clients (Claude Code), which is a different consumer.

## Tool calling works — on both topologies

Verified, not assumed. `_infer_tool_parser` (`tokenizer_utils.py:548`) returns
the `json_tools` parser for any chat template containing both `<tool_call>` and
`tool_call.name`; the cached `Qwen3-8B-8bit` tokenizer_config has both, with no
`tool_parser_type` override. So `tokenizer.has_tool_calling` is `True` and
in-process tool calling works — it is not a server-only feature.

```python
from local_llm import LocalLLM, Message
from local_llm.tools import registry, tool_loop

def get_weather(city: str) -> str:
    """Return the current weather for a city."""
    return f"18C and clear in {city}"

with LocalLLM() as llm:
    completion, transcript = tool_loop(
        llm,
        [Message(role="user", content="What's the weather in Paris?")],
        registry(get_weather),
        max_rounds=6,
    )
```

`tool_schema()` builds the OpenAI function schema from the callable's signature
and docstring first line, so what the model reads and what a human reads cannot
drift apart. `execute()` captures exceptions into the tool result rather than
raising — a model that called a tool wrongly should get to see what went wrong
and retry.

`max_rounds` is a hard bound, not a suggestion: a local model that has decided
to call the same tool forever will do exactly that.

### The segmentation detail

mlx-lm's tool parsers take only the payload **between** the model's tool-call
markers, not the whole response — `json_tools.parse_tool_call` is literally
`json.loads(text.strip())`. Segmentation is the caller's job. Take the markers
from the tokenizer (`tool_call_start` / `tool_call_end`) rather than hardcoding
`<tool_call>`, so the code works for every model family mlx-lm supports.
`local_llm/_inprocess.py` does this; passing the raw response straight to the
parser silently yields no tool calls, which is the failure mode this note
exists to prevent.

On the server path, tool calls come back as OpenAI-shaped `tool_calls` with
`finish_reason: "tool_calls"`. The client normalizes both into
`Completion.tool_calls`.

## Structured output: there is no constrained decoding

**Firm finding, not an open question.** mlx-lm 0.31.3 has no `response_format`,
no JSON schema, and no grammar — none of it appears anywhere in `server.py` or
`sample_utils.py`. `SequenceStateMachine` handles stop words and tool tokens
only. `outlines` was named in an RFC here and never adopted.

So asking a local model for JSON and assuming you get it is a bug. The working
pattern is **prompt → validate → retry**, bounded:

```python
from local_llm import parse_json

for attempt in range(3):
    result = llm.chat(messages, task="write.short")     # thinking off
    try:
        return parse_json(result.text)
    except ValueError as exc:
        messages = [*messages,
                    Message(role="assistant", content=result.text),
                    Message(role="user", content=f"That did not parse: {exc}. Return only JSON.")]
raise RuntimeError("model never produced parseable JSON")
```

`parse_json` runs the salvage pass all four MLX projects here hand-rolled
separately: strip thinking → try as-is → unwrap a code fence → extract the first
brace-balanced value, ignoring braces inside strings. Pass `strict=True` when
you want to *measure* how often the model actually complies rather than how
often salvage works.

`logit_bias` is available on both topologies as a blunt secondary lever.

## Thinking control

`enable_thinking=False` skips deliberation — Qwen3's template emits an empty
`<think></think>` block instead. Use it for direct, format-matched output; that
is exactly the structured-output case.

- In-process: passed to `apply_chat_template`.
- Server: request body field **`chat_template_kwargs`** (not
  `chat_template_args`, which is the CLI flag name and is silently ignored as a
  body key — `server.md` trap 3).

The canonized suppression set is `{write.short, search.summarize}`.
`search.retrieve` was removed from it in M5f: suppressing thinking there
measured −0.15, because thinking helps the model assess context quality before
answering. Pass `task=` and the client applies this for you.

Beware the interaction with `max_tokens`: with thinking on, a small cap can be
entirely consumed by reasoning and the server will return **no `content` field
at all** (`server.md` trap 4).

## Where local honestly loses

Recorded so it is not rediscovered:

- Prompt engineering is **exhausted** for `reason.*` on these models — two
  rounds of rewrites both measured below the no-prompt baseline. Structure
  prompts caused shallow hedging: the model filled in the structure without
  committing.
- A blanket code-review checklist held the catch rate at 75% while raising
  false positives from 0/6 to 2/6.

Both are in `evaluation.md`.

## Not covered here

MCP server wiring, multi-agent orchestration, and cloud-model selection — for
the last, use the `claude-api` skill.
