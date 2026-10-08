#!/usr/bin/env python3
"""Build slurp Step 3's two passes from a Claude Code session transcript (the raw `.jsonl`), not from a compaction summary.

A compaction summary is lossy: it drops mid-turn messages, question answers, exact commands and incidents. When a conversation was compacted since
its last slurp, the slurp reads the transcript itself. This prints, in order and with timestamps:

- compaction points (where the context was summarised);
- pass 1, every user message: typed turns, messages sent while the agent worked, and answers to AskUserQuestion;
- pass 2, every action that may have a side effect: Bash commands (by description and first line), files written or edited, and MCP writes.

Run:
    transcript_passes.py                       # newest transcript of the current directory's project
    transcript_passes.py --transcript PATH.jsonl [--since 2026-10-09T01:53] [--pass 1|2]

Times are the transcript's own (UTC). Output is a working list for the slurp, not a record: it is never saved into a project.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

MID = re.compile(r"The user sent a new message while you were working:\n(.*?)(?:\n\nThis is how|\Z)", re.S)
WRITE_TOOLS = {"Write", "Edit", "NotebookEdit"}
MCP_WRITE = re.compile(r"save|record|add_|create|update|delete|push|commit|write|checkpoint", re.I)


def default_transcript(cwd: pathlib.Path) -> pathlib.Path:
    """The newest transcript of the project Claude Code keys by this directory.

    Args:
        cwd: the working directory the session ran in.

    Returns:
        Path of the most recently modified `.jsonl` in that project's folder.

    Raises:
        SystemExit: when no transcript exists for the directory.
    """
    folder = pathlib.Path.home() / ".claude/projects" / re.sub(r"[^A-Za-z0-9]", "-", str(cwd))
    found = sorted(folder.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
    if not found:
        raise SystemExit(f"no transcript under {folder}")
    return found[-1]


def text_of(content) -> str:
    """The plain text of a message or tool-result content.

    Args:
        content: a string or a list of content blocks.

    Returns:
        The joined text.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(text_of(b.get("text") or b.get("content") or "") for b in content if isinstance(b, dict))
    return ""


def events(path: pathlib.Path, since: str = ""):
    """Every pass-1, pass-2 and compaction event of a transcript, in order.

    Args:
        path: the transcript.
        since: ISO time prefix; earlier events are skipped.

    Yields:
        (timestamp, kind, text) with kind `compaction`, `user`, `mid`, `answer`, `bash`, `file` or `mcp`.
    """
    seen: set[str] = set()
    for line in path.open(encoding="utf-8"):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        ts = d.get("timestamp", "")[:16]
        if since and ts < since:
            continue
        if d.get("type") == "queue-operation" and d.get("operation") == "enqueue":
            t = str(d.get("content") or "").strip()
            if t and not t.startswith("<") and t not in seen:
                seen.add(t)
                yield ts, "mid", t
            continue
        att = d.get("attachment") or {}
        if att.get("type") == "queued_command" and (att.get("origin") or {}).get("kind") == "human":
            t = text_of(att.get("prompt")).strip()
            if t and not t.startswith("<") and t not in seen:
                seen.add(t)
                yield ts, "mid", t
            continue
        msg = d.get("message") or {}
        content = msg.get("content")
        if d.get("isCompactSummary") or (d.get("type") == "user" and text_of(content).startswith("This session is being continued")):
            yield ts, "compaction", "context summarised here; details before it come from this transcript, not the summary"
            continue
        if d.get("type") == "user":
            if isinstance(content, str) or (isinstance(content, list) and any(b.get("type") == "text" for b in content if isinstance(b, dict))):
                t = text_of(content).strip()
                if t and not t.startswith(("<", "Base directory for this skill", "(Re-invocation of")) and t not in seen:
                    seen.add(t)   # a typed turn is also queued as a mid-turn message: keep one (2026-10-09)
                    yield ts, "user", t
            for b in content if isinstance(content, list) else []:
                if isinstance(b, dict) and b.get("type") == "tool_result":
                    r = text_of(b.get("content"))
                    for m in MID.findall(r):
                        if m not in seen:
                            seen.add(m)
                            yield ts, "mid", m.strip()
        tur = d.get("toolUseResult")
        if isinstance(tur, dict) and isinstance(tur.get("answers"), dict):
            for q, a in tur["answers"].items():
                yield ts, "answer", f"{q} -> {a}"
        for m in MID.findall(json.dumps(d.get("attachment") or {}, ensure_ascii=False).replace("\\n", "\n")):
            if m not in seen:
                seen.add(m)
                yield ts, "mid", m.strip()
        if d.get("type") == "assistant" and isinstance(content, list):
            for b in content:
                if not isinstance(b, dict) or b.get("type") != "tool_use":
                    continue
                name, inp = b.get("name", ""), b.get("input") or {}
                if name == "Bash":
                    first = (inp.get("command") or "").strip().splitlines()[:1]
                    yield ts, "bash", f"{inp.get('description', '')} | {first[0][:120] if first else ''}"
                elif name in WRITE_TOOLS:
                    yield ts, "file", f"{name} {inp.get('file_path', '')}"
                elif name.startswith("mcp__") and MCP_WRITE.search(name.split("__")[-1]):
                    yield ts, "mcp", name


def main(argv: list[str] | None = None) -> int:
    """Print the passes.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--transcript", type=pathlib.Path)
    ap.add_argument("--since", default="", help="ISO time prefix, e.g. 2026-10-09T01:53 (UTC, as the transcript stores it)")
    ap.add_argument("--pass", dest="which", choices=["1", "2"], help="only pass 1 (user) or pass 2 (side effects)")
    args = ap.parse_args(argv)
    path = args.transcript or default_transcript(pathlib.Path.cwd())
    keep = {"1": {"compaction", "user", "mid", "answer"}, "2": {"compaction", "bash", "file", "mcp"}}.get(args.which)
    print(f"transcript: {path}")
    counts: dict[str, int] = {}
    for ts, kind, text in events(path, args.since):
        if keep and kind not in keep:
            continue
        counts[kind] = counts.get(kind, 0) + 1
        print(f"{ts} {kind:10} {' '.join(text.split())[:240]}")
    print("counts: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
