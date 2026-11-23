# CLIs, scheduled jobs and bots

## Which language

- **Python** for scraping, data processing, ML/NLP, and macOS automation (PyObjC). Template: `python-cli`.
- **TypeScript** when the tool shares code with a TS web app or library. Template: `ts-cli`.

It's a guide: pick the language whose ecosystem does the hard part.

## Command-line parsing

- Python: **Typer**.
- TypeScript: **commander**; `node:util` `parseArgs` is fine for a one-command script.

## Job rules (firm)

Every scheduled job:

1. **Is safe to re-run.** Running twice, or after a crash, must not double-post
   or double-send. Diff against stored state; use idempotency keys with APIs
   that support them.
2. **Keeps its state in SQLite** (`data/<project>.db`, git-ignored), with
   numbered migrations.
3. **Holds a run lock** (a lock file with the pid; a lock left by a dead
   process is taken over), so overlapping runs can't happen.
4. **Has `--dry-run`** (show what would happen, change nothing) and a
   **per-run cap** (`--max N`) on anything that posts, sends or deletes. The
   first run against existing data **seeds silently**: record what's there,
   act on nothing.
5. **Exits non-zero on failure**, so schedulers and wrappers see it.
6. **Records each run** (start, end, ok, detail, dry run) in the database;
   a `status` command prints recent runs.
7. **Alerts on failure** with an ntfy push (`NTFY_URL`; a one-line HTTP POST,
   self-hostable). No URL configured means no alert, not an error.

The `ts-cli` and `python-cli` templates implement all of this in
`job.ts` / `job.py`; put the real work in the `run` command.

## Scheduling

| Where it runs | Scheduler |
|---|---|
| On the Mac | **launchd**. The plist lives in the repo at `ops/launchd/`; `ops/launchd/install.sh` installs it. launchd runs a missed job when the Mac wakes. |
| Always-on homelab services | Docker Compose (`restart: unless-stopped`) |
| Stateless jobs that can run in the cloud | GitHub Actions `schedule:` (no local state, nothing to persist) |

Never leave a scheduler definition only in `~/Library/LaunchAgents` or a
crontab: if it isn't in the repo, it isn't versioned.

## Configuration and logs

- Environment only. Node: `node --env-file-if-exists=.env`. Python:
  `uv run --env-file .env`. The launchd job runs the same command from the
  repo directory, so it reads the same `.env`.
- Log to stdout/stderr only. launchd routes them to
  `~/Library/Logs/<project>/`; compose to `docker logs`. Jobs never manage
  log files themselves.

## Calling Claude (firm)

All LLM access goes through the **Claude CLI** (`claude -p`), the
subscription CLI, never an API SDK or a direct API call. One small wrapper
module per project is the only place that calls it (`claude.py` /
`claude.ts`; templates: `--data uses_claude=true`). The wrapper:

- runs `claude -p <prompt> --model <model> --output-format text`, adding
  `--append-system-prompt <text>` for extra instructions;
- takes the binary from `CLAUDE_BIN` (default `claude` on PATH) and the model
  from `CLAUDE_MODEL`;
- has a timeout and raises a clear error on a non-zero exit or empty output;
- caches responses in the database by a hash of model + system prompt + prompt;
- is tested against a fake binary (a shell script that echoes its arguments
  and counts calls), so tests never call the real CLI and the flags are
  checked.

Check the flags against `claude --help` when changing the wrapper; a wrapper
using flags that don't exist fails only at run time, which is what the
fake-binary test is there to prevent.

Python sketch:

```python
def ask_claude(prompt, *, conn, model=None, system=None, timeout=120, binary=None, fresh=False):
    model = model or os.environ.get("CLAUDE_MODEL") or "sonnet"
    binary = binary or os.environ.get("CLAUDE_BIN") or "claude"
    key = hashlib.sha256(f"{model}\n{system or ''}\n{prompt}".encode()).hexdigest()
    if not fresh and (row := conn.execute("SELECT response FROM claude_cache WHERE key = ?", (key,)).fetchone()):
        return row[0]
    args = [binary, "-p", prompt, "--model", model, "--output-format", "text"]
    if system:
        args += ["--append-system-prompt", system]
    out = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=True).stdout.strip()
    ...  # store in claude_cache, return out
```

Deterministic code beats an LLM step when a rule can do the job: use the CLI
for judgement and language, not for parsing or arithmetic.
