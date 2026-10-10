#!/usr/bin/env python3
"""Lint a Claude Code auto-memory store (a MEMORY.md index plus topic files).

Errors (exit 1) are things that break how Claude Code loads memory:
missing MEMORY.md, index links to missing files, topic files without the
required frontmatter, files over the 100 kB per-memory cap the Dreams API uses.

Warnings are consolidation signals that map to rubric IDs in rules.md
(F1 frontmatter drift, I1 index bloat/orphans, O1 oversized, L1 dangling [[links]]).

Usage: validate_store.py <store_dir> [--json]
"""
import json
import re
import sys
from pathlib import Path

INDEX = "MEMORY.md"
MAX_BYTES = 100 * 1024          # Dreams API per-memory cap
OVERSIZE_WARN = 8 * 1024         # O1 threshold
HOOK_WARN = 150                  # I1 threshold, chars per index line
TYPES = {"user", "feedback", "project", "reference"}
INDEX_LINK = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
WIKI_LINK = re.compile(r"\[\[([^\]|#]+)")


def parse_frontmatter(text):
    """Return (dict of flat + metadata.* keys, body) or (None, text) if absent."""
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end == -1:
        return None, text
    fm, body = text[3:end], text[end + 4:]
    keys, section = {}, None
    for line in fm.splitlines():
        if not line.strip():
            continue
        m = re.match(r"^(\s*)([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not m:
            continue
        indent, key, val = m.groups()
        if indent and section:
            keys[f"{section}.{key}"] = val.strip()
        else:
            section = key if not val.strip() else None
            keys[key] = val.strip()
    return keys, body


def validate(store):
    store = Path(store)
    errors, warnings = [], []
    files = sorted(p for p in store.glob("*.md") if p.name != INDEX)
    index = store / INDEX
    stats = {"files": len(files), "bytes": sum(p.stat().st_size for p in store.glob("*.md")),
             "index_lines": 0, "index_bytes": 0}

    if not index.exists():
        if files:
            errors.append({"rule": "I1", "file": INDEX, "issue": "MEMORY.md missing but topic files exist"})
        return {"store": str(store), "errors": errors, "warnings": warnings, "stats": stats}

    itext = index.read_text(encoding="utf-8")
    stats["index_lines"] = len(itext.splitlines())
    stats["index_bytes"] = len(itext.encode())
    linked = set()
    for n, line in enumerate(itext.splitlines(), 1):
        for _, target in INDEX_LINK.findall(line):
            linked.add(target)
            if not (store / target).exists():
                errors.append({"rule": "L1", "file": INDEX, "line": n, "issue": f"index links to missing file {target}"})
        if line.startswith("- ") and len(line) > HOOK_WARN:
            warnings.append({"rule": "I1", "file": INDEX, "line": n, "issue": f"index hook is {len(line)} chars (> {HOOK_WARN})"})

    names = {p.stem for p in files}   # [[links]] may use the file stem or the name: slug
    for p in files:
        if p.name not in linked:
            warnings.append({"rule": "I1", "file": p.name, "issue": "topic file not listed in MEMORY.md (orphan)"})
        size = p.stat().st_size
        if size > MAX_BYTES:
            errors.append({"rule": "O1", "file": p.name, "issue": f"{size} bytes exceeds {MAX_BYTES}"})
        elif size > OVERSIZE_WARN:
            warnings.append({"rule": "O1", "file": p.name, "issue": f"{size} bytes (> {OVERSIZE_WARN}); likely log-like"})
        fm, body = parse_frontmatter(p.read_text(encoding="utf-8"))
        if fm is None:
            errors.append({"rule": "F1", "file": p.name, "issue": "no frontmatter"})
            continue
        for key in ("name", "description"):
            if not fm.get(key):
                errors.append({"rule": "F1", "file": p.name, "issue": f"frontmatter missing {key}"})
        mtype = fm.get("metadata.type") or fm.get("type")
        if mtype not in TYPES:
            errors.append({"rule": "F1", "file": p.name, "issue": f"metadata.type is {mtype!r}, expected one of {sorted(TYPES)}"})
        for key in ("metadata.node_type", "metadata.originSessionId"):
            if key not in fm:
                warnings.append({"rule": "F1", "file": p.name, "issue": f"frontmatter lacks {key}"})
        if fm.get("name"):
            names.add(fm["name"])

    for p in files:
        _, body = parse_frontmatter(p.read_text(encoding="utf-8"))
        for target in WIKI_LINK.findall(body):
            if target.strip() not in names:
                warnings.append({"rule": "L1", "file": p.name, "issue": f"[[{target.strip()}]] has no matching memory (may be intentional)"})

    return {"store": str(store), "errors": errors, "warnings": warnings, "stats": stats}


def main(argv):
    if len(argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2
    result = validate(argv[1])
    if "--json" in argv:
        print(json.dumps(result, indent=2))
    else:
        s = result["stats"]
        print(f"{result['store']}: {s['files']} files, {s['bytes']} bytes, MEMORY.md {s['index_lines']} lines / {s['index_bytes']} bytes")
        for level in ("errors", "warnings"):
            for f in result[level]:
                loc = f"{f['file']}:{f['line']}" if "line" in f else f["file"]
                print(f"  {level[:-1].upper():7} {f['rule']}  {loc}  {f['issue']}")
        print(f"  {len(result['errors'])} errors, {len(result['warnings'])} warnings")
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
