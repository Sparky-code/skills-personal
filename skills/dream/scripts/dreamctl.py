#!/usr/bin/env python3
"""Deterministic plumbing for the /dream skill: run state, snapshots, diffs, promote.

The LLM phases (mining, consolidation, verification) are driven by SKILL.md.
Everything that touches the live memory store or must be exact lives here.

Subcommands:
  resolve [path|slug]                         -> slug + memory dir (default: cwd)
  snapshot <slug> [--sessions N|id,id] [--instructions TEXT] [--exclude ID,ID] [--dry-run]
  set-status <run_dir> <status> [--phase P] [--error E]
  status [slug]
  diff <run_dir>
  check-removals <run_dir>
  promote <slug> <run_id|latest>
  discard <slug> <run_id>
  unlock <slug> [--force]

Run state lives under ~/.claude/dream/. Only `promote` writes the live store.
"""
import argparse
import difflib
import hashlib
import json
import os
import re
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True  # keep __pycache__ out of the skills repo
sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_store import validate  # noqa: E402

PROJECTS = Path(os.environ.get("DREAM_PROJECTS", Path.home() / ".claude" / "projects"))
HOME = Path(os.environ.get("DREAM_HOME", Path.home() / ".claude" / "dream"))
TERMINAL = {"completed", "failed", "canceled"}
STATUSES = {"pending", "running"} | TERMINAL
MAX_SESSIONS = 100           # Dreams API: 1-100 session ids
MAX_INSTRUCTIONS = 4096      # Dreams API: instructions <= 4096 chars
MAX_FILES = 10_000           # Dreams API: memories per store
MAX_FILE_BYTES = 100 * 1024  # Dreams API: bytes per memory
DEFAULT_SESSIONS = 20
LIVE_SESSION_SECONDS = 120   # a transcript written this recently is the session running /dream
STALE_LOCK_SECONDS = 6 * 3600


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def die(msg, code=1):
    print(f"dreamctl: {msg}", file=sys.stderr)
    sys.exit(code)


def write_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


# --- resolution -------------------------------------------------------------

def to_slug(target):
    """Claude Code names project dirs by replacing every non-alphanumeric char of the cwd with '-'."""
    if target.startswith("-") and (PROJECTS / target).is_dir():
        return target
    return re.sub(r"[^A-Za-z0-9]", "-", str(Path(target).expanduser().resolve()))


def project_dir(slug):
    d = PROJECTS / slug
    if not d.is_dir():
        die(f"no Claude Code project dir {d}")
    return d


def memory_dir(slug):
    return project_dir(slug) / "memory"


def runs_dir(slug):
    return HOME / "runs" / slug


def find_run(slug, run_id):
    base = runs_dir(slug)
    if run_id == "latest":
        runs = sorted(p for p in base.glob("*") if p.is_dir()) if base.exists() else []
        if not runs:
            die(f"no runs for {slug}")
        return runs[-1]
    run = base / run_id
    if not run.is_dir():
        die(f"no run {run}")
    return run


# --- hashing ---------------------------------------------------------------

def manifest(store):
    store = Path(store)
    out = []
    for p in sorted(store.rglob("*")):
        if p.is_file():
            out.append({"path": str(p.relative_to(store)),
                        "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                        "bytes": p.stat().st_size})
    return out


def manifest_drift(expected, store):
    want = {m["path"]: m["sha256"] for m in expected}
    have = {m["path"]: m["sha256"] for m in manifest(store)} if Path(store).exists() else {}
    changed = sorted(p for p in want.keys() & have.keys() if want[p] != have[p])
    return {"changed": changed, "added": sorted(have.keys() - want.keys()),
            "removed": sorted(want.keys() - have.keys())}


# --- locking ---------------------------------------------------------------
# A Claude session has no stable pid the script can see (each Bash call is a
# fresh shell), so a lock is stale when its run is terminal or it is too old.

def lock_path(slug):
    return HOME / "locks" / slug


def acquire_lock(slug, run_id):
    lp = lock_path(slug)
    lp.parent.mkdir(parents=True, exist_ok=True)
    try:
        lp.mkdir()
    except FileExistsError:
        info = lp / "owner.json"
        owner = read_json(info) if info.exists() else {}
        held = owner.get("run_id", "?")
        run = runs_dir(slug) / held
        status = read_json(run / "status.json").get("status") if (run / "status.json").exists() else None
        age = time.time() - owner.get("since", 0)
        if status in TERMINAL or age > STALE_LOCK_SECONDS:
            shutil.rmtree(lp)
            lp.mkdir()
        else:
            die(f"{slug} is locked by run {held} (status {status}, {int(age)}s old); "
                f"wait, or `dreamctl.py unlock {slug} --force` if that run is dead")
    write_json(lp / "owner.json", {"run_id": run_id, "since": time.time()})


def release_lock(slug, run_id=None):
    lp = lock_path(slug)
    if not lp.exists():
        return
    info = lp / "owner.json"
    if run_id and info.exists() and read_json(info).get("run_id") != run_id:
        return
    shutil.rmtree(lp)


# --- sessions --------------------------------------------------------------

def select_sessions(slug, spec, exclude):
    proj = project_dir(slug)
    all_sessions = sorted(proj.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    cutoff = time.time() - LIVE_SESSION_SECONDS
    candidates = [p for p in all_sessions
                  if p.stem not in exclude and p.stat().st_mtime < cutoff]
    if spec and not spec.isdigit():
        ids = [s.strip() for s in spec.split(",") if s.strip()]
        if len(set(ids)) != len(ids):
            die("duplicate session ids")
        missing = [i for i in ids if not (proj / f"{i}.jsonl").exists()]
        if missing:
            die(f"input_session_unavailable: {', '.join(missing)}")
        chosen = ids
    else:
        n = int(spec) if spec else DEFAULT_SESSIONS
        chosen = [p.stem for p in candidates[:n]]
    if len(chosen) > MAX_SESSIONS:
        die(f"{len(chosen)} sessions > {MAX_SESSIONS} (Dreams API limit)")
    return sorted(chosen)


# --- commands --------------------------------------------------------------

def cmd_resolve(a):
    slug = to_slug(a.target or os.getcwd())
    mem = memory_dir(slug)
    print(json.dumps({"slug": slug, "memory_dir": str(mem), "exists": mem.is_dir(),
                      "sessions": len(list(project_dir(slug).glob('*.jsonl')))}))


def cmd_snapshot(a):
    mem = memory_dir(a.slug)
    if not mem.is_dir() or not any(mem.iterdir()):
        die(f"{mem} is missing or empty; nothing to dream over")
    if a.instructions and len(a.instructions) > MAX_INSTRUCTIONS:
        die(f"instructions are {len(a.instructions)} chars > {MAX_INSTRUCTIONS}")
    files = [p for p in mem.rglob("*") if p.is_file()]
    big = [p.name for p in files if p.stat().st_size > MAX_FILE_BYTES]
    if len(files) > MAX_FILES or big:
        die(f"input_memory_store_too_large: {len(files)} files; over {MAX_FILE_BYTES} bytes: {big}")

    exclude = set(filter(None, (a.exclude or "").split(",")))
    sessions = select_sessions(a.slug, a.sessions, exclude)

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run = runs_dir(a.slug) / run_id
    acquire_lock(a.slug, run_id)
    try:
        for sub in ("input", "sessions", "findings", "output"):
            (run / sub).mkdir(parents=True, exist_ok=True)
        shutil.copytree(mem, run / "input" / "store")
        shutil.copytree(mem, run / "output" / "store")
        write_json(run / "input" / "manifest.json", manifest(mem))
        write_json(run / "input" / "baseline.json", validate(mem))
        write_json(run / "request.json", {
            "run_id": run_id, "slug": a.slug, "memory_dir": str(mem),
            "session_ids": sessions, "instructions": a.instructions or "",
            "dry_run": a.dry_run, "created_at": now_iso()})
        write_json(run / "status.json", {"status": "running", "phase": "snapshot",
                                         "started": now_iso(), "ended": None, "error": None})
    except Exception as e:
        release_lock(a.slug, run_id)
        die(f"snapshot failed: {e}")
    print(json.dumps({"run_dir": str(run), "run_id": run_id, "sessions": sessions}))


def cmd_set_status(a):
    run = Path(a.run_dir)
    if a.status not in STATUSES:
        die(f"status must be one of {sorted(STATUSES)}")
    st = read_json(run / "status.json")
    if st["status"] in TERMINAL:
        die(f"run already {st['status']}")
    if a.status == "completed" and not read_json(run / "request.json").get("dry_run"):
        # completed is gated on a clean removal check and a valid output store
        problems = removal_problems(run)
        if problems:
            die(f"refusing completed: {len(problems)} unexplained removals (run check-removals)")
        result = validate(run / "output" / "store")
        if result["errors"]:
            die(f"refusing completed: output store has {len(result['errors'])} validation errors")
    st.update(status=a.status, phase=a.phase or st.get("phase"), error=a.error)
    if a.status in TERMINAL:
        st["ended"] = now_iso()
    write_json(run / "status.json", st)
    if a.status in TERMINAL:
        release_lock(read_json(run / "request.json")["slug"], run.name)
    print(json.dumps(st))


def cmd_status(a):
    slugs = [a.slug] if a.slug else sorted(p.name for p in (HOME / "runs").glob("*")) if (HOME / "runs").exists() else []
    for slug in slugs:
        print(slug)
        for run in sorted(p for p in runs_dir(slug).glob("*") if p.is_dir()):
            st = read_json(run / "status.json") if (run / "status.json").exists() else {}
            mark = "promoted" if (run / "promoted.json").exists() else "discarded" if (run / "discarded.json").exists() else ""
            note = ""
            if st.get("status") == "completed" and not mark:
                drift = manifest_drift(read_json(run / "input" / "manifest.json"), memory_dir(slug))
                n = sum(len(v) for v in drift.values())
                note = "promotable" if n == 0 else f"stale: live store changed ({n} files)"
            print(f"  {run.name}  {st.get('status', '?'):9} {st.get('phase') or '':12} {mark or note}")


def cmd_diff(a):
    run = Path(a.run_dir)
    before, after = run / "input" / "store", run / "output" / "store"
    names = sorted({p.name for p in before.glob("*.md")} | {p.name for p in after.glob("*.md")})
    out = []
    for n in names:
        b = (before / n).read_text(encoding="utf-8").splitlines(keepends=True) if (before / n).exists() else []
        c = (after / n).read_text(encoding="utf-8").splitlines(keepends=True) if (after / n).exists() else []
        out.extend(difflib.unified_diff(b, c, f"a/{n}" if b else "/dev/null", f"b/{n}" if c else "/dev/null"))
    (run / "diff.patch").write_text("".join(out), encoding="utf-8")
    print(json.dumps({"diff": str(run / "diff.patch"), "files_changed": sum(1 for line in out if line.startswith("+++ "))}))


def _norm(s):
    return re.sub(r"\s+", " ", re.sub(r"[*_`>#\-]", " ", s)).strip().lower()


def _units(text, is_index):
    """Index files compare line by line; topic files compare by paragraph, frontmatter excluded."""
    if is_index:
        return [l for l in text.splitlines() if l.strip()]
    if text.startswith("---"):
        end = text.find("\n---", 3)
        text = text[end + 4:] if end != -1 else text
    return [p for p in re.split(r"\n\s*\n", text) if p.strip()]


def removal_problems(run):
    """Every paragraph that vanished from the store must be explained by a verified change."""
    run = Path(run)
    changes_path = run / "changes.json"
    changes = read_json(changes_path) if changes_path.exists() else []
    excerpts = [_norm(c.get("before_excerpt", "")) for c in changes
                if c.get("verdict") in ("confirmed", "corrected") and c.get("reason")]
    excerpts = [e for e in excerpts if len(e) >= 20]
    after_text = _norm(" ".join(p.read_text(encoding="utf-8") for p in (run / "output" / "store").glob("*.md")))
    problems = []
    for p in sorted((run / "input" / "store").glob("*.md")):
        for unit in _units(p.read_text(encoding="utf-8"), p.name == "MEMORY.md"):
            u = _norm(unit)
            if len(u) < 20 or u in after_text:
                continue
            if any(u in e or e in u for e in excerpts):
                continue
            problems.append({"file": p.name, "text": unit.strip()[:200]})
    return problems


def cmd_check_removals(a):
    problems = removal_problems(a.run_dir)
    print(json.dumps({"unexplained": len(problems), "items": problems}, indent=2))
    sys.exit(1 if problems else 0)


def cmd_promote(a):
    run = find_run(a.slug, a.run_id)
    st = read_json(run / "status.json")
    if st["status"] != "completed":
        die(f"run {run.name} is {st['status']}, not completed")
    if read_json(run / "request.json").get("dry_run"):
        die("dry-run runs have no output to promote")
    for marker in ("promoted.json", "discarded.json"):
        if (run / marker).exists():
            die(f"run {run.name} already {marker.split('.')[0]}")
    mem = memory_dir(a.slug)
    drift = manifest_drift(read_json(run / "input" / "manifest.json"), mem)
    if any(drift.values()):
        die("live store changed since snapshot; re-run /dream.\n" + json.dumps(drift, indent=2))
    out_store = run / "output" / "store"
    if validate(out_store)["errors"]:
        die("output store fails validation; not promoting")

    acquire_lock(a.slug, f"promote-{run.name}")
    archive = HOME / "archive" / a.slug / datetime.now().strftime("%Y%m%d-%H%M%S")
    staged = mem.with_name("memory.dream-new")
    try:
        archive.parent.mkdir(parents=True, exist_ok=True)
        if staged.exists():
            shutil.rmtree(staged)
        shutil.copytree(out_store, staged)
        shutil.move(str(mem), str(archive))   # same volume -> rename
        staged.rename(mem)
        result = validate(mem)
        if result["errors"]:
            shutil.rmtree(mem)
            shutil.copytree(archive, mem)
            die(f"live store failed validation after swap; restored from {archive}")
        write_json(run / "promoted.json", {"at": now_iso(), "archive": str(archive),
                                           "live_manifest": manifest(mem)})
    finally:
        release_lock(a.slug)
    print(json.dumps({"promoted": run.name, "archive": str(archive),
                      "rollback": f"rm -rf '{mem}' && cp -R '{archive}' '{mem}'"}))


def cmd_discard(a):
    run = find_run(a.slug, a.run_id)
    if (run / "promoted.json").exists():
        die("run already promoted; roll back from its archive instead")
    write_json(run / "discarded.json", {"at": now_iso()})
    st = read_json(run / "status.json")
    if st["status"] not in TERMINAL:
        st.update(status="canceled", ended=now_iso())
        write_json(run / "status.json", st)
    release_lock(a.slug, run.name)
    print(json.dumps({"discarded": run.name}))


def cmd_unlock(a):
    if not lock_path(a.slug).exists():
        print("not locked")
        return
    if not a.force:
        die("pass --force to remove a lock you have confirmed is dead")
    release_lock(a.slug)
    print("unlocked")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("resolve"); s.add_argument("target", nargs="?")
    s = sub.add_parser("snapshot"); s.add_argument("slug"); s.add_argument("--sessions")
    s.add_argument("--instructions"); s.add_argument("--exclude"); s.add_argument("--dry-run", action="store_true")
    s = sub.add_parser("set-status"); s.add_argument("run_dir"); s.add_argument("status")
    s.add_argument("--phase"); s.add_argument("--error")
    s = sub.add_parser("status"); s.add_argument("slug", nargs="?")
    s = sub.add_parser("diff"); s.add_argument("run_dir")
    s = sub.add_parser("check-removals"); s.add_argument("run_dir")
    s = sub.add_parser("promote"); s.add_argument("slug"); s.add_argument("run_id")
    s = sub.add_parser("discard"); s.add_argument("slug"); s.add_argument("run_id")
    s = sub.add_parser("unlock"); s.add_argument("slug"); s.add_argument("--force", action="store_true")
    # Project slugs start with '-' (e.g. -Users-sparky-Code), which argparse would
    # read as flags. Shield single-dash args, then unshield after parsing.
    argv = ["\0" + x if x.startswith("-") and not x.startswith("--") and x != "-h" else x
            for x in sys.argv[1:]]
    a = p.parse_args(argv)
    for k, v in vars(a).items():
        if isinstance(v, str):
            setattr(a, k, v.lstrip("\0"))
    globals()["cmd_" + a.cmd.replace("-", "_")](a)


if __name__ == "__main__":
    main()
