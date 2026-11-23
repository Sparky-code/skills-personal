# Python toolchain

| Layer | Standard |
|---|---|
| Python | **3.14**, pinned in `.python-version` |
| Project + env manager | **uv**: installs Python, `uv.lock` committed, `.venv/` in the project |
| Layout | `src/<package>/` + `tests/`, console-script entry point |
| Build backend | `uv_build` |
| CLI | **Typer** |
| Lint + format | **ruff** (`ruff format`, `ruff check`) |
| Types | **mypy**, `strict = true` for new projects (start at basic when adopting in an old one) |
| Tests | **pytest**; network or real-service tests behind a `live` marker, off by default |
| HTTP | **httpx** |

## Why uv

It installs and pins the interpreter itself (no system Python by accident),
locks dependencies, creates `.venv`, runs commands (`uv run`), installs tools
(`uv tool`), and runs single-file scripts with inline dependencies. One tool
replaces pyenv, pip, venv, pip-tools and pipx.

## pyproject.toml essentials

```toml
[project]
name = "my-tool"
requires-python = ">=3.14"
dependencies = ["httpx>=0.28", "typer>=0.29"]

[project.scripts]
my-tool = "my_tool.cli:app"

[dependency-groups]
dev = ["mypy", "pytest", "ruff"]

[build-system]
requires = ["uv_build>=0.13,<0.14"]
build-backend = "uv_build"

[tool.ruff]
line-length = 100
target-version = "py314"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "UP", "B", "SIM", "RUF"]

[tool.mypy]
strict = true
files = ["src", "tests"]

[tool.pytest.ini_options]
addopts = "-m 'not live'"
markers = ["live: talks to real external services; run with `pytest -m live`"]
```

## Everyday commands

```bash
uv sync                      # create/refresh .venv from uv.lock
uv add httpx                 # runtime dependency
uv add --dev pytest          # dev dependency
uv run pytest                # tests (uv run pytest -m live for network tests)
uv run mypy                  # types
uv run ruff check --fix && uv run ruff format
uv run --env-file .env my-tool run
```

## Layout

```
src/my_tool/__init__.py
src/my_tool/cli.py       # Typer app
tests/test_*.py
pyproject.toml  uv.lock  .python-version
```

The `src/` layout means tests import the installed package, not stray files
in the working directory.

## Single-file scripts

For one-off automation, declare dependencies inline (PEP 723) and run with
`uv run script.py`, with no venv or requirements file:

```python
# /// script
# requires-python = ">=3.14"
# dependencies = ["httpx"]
# ///
```

Once a script grows a second module or tests, make it a `python-cli` project.

## Conventions

- `from __future__ import annotations` and type hints throughout.
- Settings from the environment: `os.environ` in small tools,
  `pydantic-settings` (with an env prefix) in services.
- Network tests are `@pytest.mark.live`; default runs, hooks and CI stay
  offline and deterministic. Use `httpx.MockTransport` for HTTP in unit tests.
