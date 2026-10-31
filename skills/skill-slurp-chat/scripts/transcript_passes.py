#!/usr/bin/env python3
"""Build slurp Step 3's two passes from a Claude Code transcript or explicit Codex rollout JSONL, not a compaction summary.

A compaction summary is lossy: it drops mid-turn messages, question answers, exact commands and incidents. When a conversation was compacted since
its last slurp, the slurp reads the transcript itself. This prints, in order and with timestamps:

- compaction points (where the context was summarised);
- pass 1, every user message: typed turns, messages sent while the agent worked, and answers to AskUserQuestion;
- pass 2, every action that may have a side effect: Bash commands (by description and first line), files written or edited, and MCP writes;
  a sub-agent's own side effects are listed too, prefixed `sub-`;
- pass 3, every sub-agent the session spawned (`<session>/subagents/agent-*.jsonl`, operator 2026-10-29: "when you're slurping you need to
  slurp information from the sub agents as well"): its type and task, and the start of its final report, which the parent only summarised.

Run:
    transcript_passes.py                       # newest transcript of the current directory's project
    transcript_passes.py --transcript PATH.jsonl [--since 2026-10-09T01:53] [--pass 1|2|3]

Times are the transcript's own (UTC). Output is a working list for the slurp, not a record: it is never saved into a project.
For Codex, pass --transcript explicitly. Pass 2 lists tool-envelope and nested tool names without arguments; inspect relevant source inputs locally
to distinguish reads from writes. Mirrored response-item user messages are ignored, while repeated real user events are retained.
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


TAG_BLOCK = re.compile(r"^\s*<([a-z_-]+)>.*?</\1>\s*", re.S)
#: Text the operator pasted (`<pasted_content id="...">` ... `</pasted_content id="...">`): kept as operator input, marked `[pasted]`.
PASTED = re.compile(r"<pasted_content\b[^>]*>\s*(.*?)\s*</pasted_content\b[^>]*>", re.S)


COMMAND = re.compile(r"<command-name>\s*(/?[^<]+?)\s*</command-name>")
COMMAND_ARGS = re.compile(r"<command-args>(.*?)</command-args>", re.S)


def slash_command(text: str) -> str:
    """The slash command a turn invoked, as the user typed it.

    A `/skill args` turn reaches the transcript as `<command-name>` and `<command-args>` tags, which the "starts with <" filter drops, so pass 1
    missed every slash command (2026-10-27: four `/skill-ai-it` runs absent from a skill-goal-guard close).

    Args:
        text: the turn's text.

    Returns:
        "/name args", or "" when the turn holds no command tag.
    """
    m = COMMAND.search(text)
    if not m:
        return ""
    name = m.group(1) if m.group(1).startswith("/") else "/" + m.group(1)
    args = COMMAND_ARGS.search(text)
    return f"{name} {args.group(1).strip()}".strip() if args else name


def typed_text(content) -> str:
    """The operator's own text of a message, without the IDE and harness blocks the client puts before it.

    A typed turn often arrives as two text blocks: an `<ide_opened_file>` or `<ide_selection>` note, then the message. Joining the blocks first and
    then dropping text that starts with `<` lost every such message (found 2026-10-14: five of ten typed turns missing). A pasted block carries
    attributes (`<pasted_content id="...">`), so it is kept as `[pasted] <text>` rather than read as a harness tag; before 2026-10-21 the whole
    turn, the operator's typed words after the paste included, was dropped.

    Args:
        content: a string or a list of content blocks.

    Returns:
        The message text with leading tag blocks removed; empty when nothing but tags is left.
    """
    if isinstance(content, list):
        parts = [typed_text(b.get("text") or "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
        return "\n".join(x for x in parts if x)
    t = PASTED.sub(lambda m: "[pasted] " + m.group(1), content if isinstance(content, str) else "")
    while True:
        m = TAG_BLOCK.match(t)
        if not m:
            return t.strip()
        t = t[m.end():]


def _lines(path: pathlib.Path):
    """Stream transcript lines with a managed file handle.

    Args:
        path: The local transcript path.
    Yields:
        Each raw JSONL line.
    Raises:
        OSError: When the transcript cannot be read.
    """
    with path.open(encoding="utf-8") as stream:
        yield from stream


def events(path: pathlib.Path, since: str = ""):
    """Every pass-1, pass-2 and compaction event of a transcript, in order.

    Args:
        path: the transcript.
        since: ISO time prefix; earlier events are skipped.

    Yields:
        (timestamp, kind, text) with kind `compaction`, `user`, `mid`, `answer`, `bash`, `file`, `mcp` or Codex `tool`.
    """
    seen: set[str] = set()
    for line in _lines(path):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        ts = d.get("timestamp", "")
        if since and ts < since:
            continue
        payload = d.get("payload") or {}
        if d.get("type") == "event_msg" and payload.get("type") == "user_message":
            text = payload.get("message")
            if isinstance(text, str) and text.strip():
                yield ts, "user", text.strip()
            continue
        if d.get("type") == "compacted":
            yield ts, "compaction", "context summarised here; details before it come from this transcript, not the summary"
            continue
        if d.get("type") == "response_item":
            if payload.get("type") in ("custom_tool_call", "function_call"):
                name = str(payload.get("name") or "unknown tool")
                raw = payload.get("input", payload.get("arguments", ""))
                raw = raw if isinstance(raw, str) else json.dumps(raw)
                nested = sorted(set(re.findall(r"tools\.([A-Za-z0-9_]+)", raw)))
                yield ts, "tool", name + (" [" + ", ".join(nested) + "]" if nested else "")
            continue
        if d.get("type") == "queue-operation" and d.get("operation") == "enqueue":
            t = typed_text(str(d.get("content") or ""))
            if t and not t.startswith("<") and t not in seen:
                seen.add(t)
                yield ts, "mid", t
            continue
        att = d.get("attachment") or {}
        if att.get("type") == "queued_command" and (att.get("origin") or {}).get("kind") == "human":
            t = typed_text(att.get("prompt"))
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
            command = slash_command(text_of(content))
            if command and (ts, command) not in seen:   # a repeated command is a new run: key it by time, not by text
                seen.add((ts, command))
                yield ts, "user", command
                continue
            if isinstance(content, str) or (isinstance(content, list) and any(b.get("type") == "text" for b in content if isinstance(b, dict))):
                t = typed_text(content)
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


def subagent_events(path: pathlib.Path, since: str = ""):
    """The sub-agents a session spawned: one report line each, then their own side effects.

    Args:
        path: The session's transcript; its sub-agents are in `<path without .jsonl>/subagents/agent-*.jsonl`.
        since: ISO time prefix; earlier events are skipped.

    Yields:
        (timestamp, kind, text): kind `subagent` (type, task and the start of its final report) or `sub-<kind>` for its side effects.
    """
    folder = path.with_suffix("") / "subagents"
    for sub_path in sorted(folder.glob("agent-*.jsonl")) if folder.is_dir() else []:
        meta_path = sub_path.with_name(sub_path.stem + ".meta.json")
        meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
        first, report, handback = "", "", ""
        for line in _lines(sub_path):
            try:
                row = json.loads(line)
            except ValueError:
                continue
            first = first or row.get("timestamp", "")
            if row.get("type") == "assistant":
                content = (row.get("message") or {}).get("content")
                report = text_of(content) or report
                for block in content if isinstance(content, list) else []:
                    if isinstance(block, dict) and block.get("name") == "SubagentHandback":
                        handback = str((block.get("input") or {}).get("message", ""))
        if first and first >= since:
            yield first, "subagent", f"{meta.get('agentType', '?')}: {meta.get('description', sub_path.stem)} -> {handback or report}"
        for ts, kind, text in events(sub_path, since):
            if kind in ("bash", "file", "mcp", "tool"):
                yield ts, f"sub-{kind}", text


def subagent_reports(path: pathlib.Path) -> list[tuple[str, list[str]]]:
    """Every sub-agent's final reports, in full: its SubagentHandback messages, one per run when it was resumed.

    Args:
        path: The session's transcript.

    Returns:
        (agent label, reports) per sub-agent; with no hand-back, the last assistant text.
    """
    out = []
    folder = path.with_suffix("") / "subagents"
    for sub_path in sorted(folder.glob("agent-*.jsonl")) if folder.is_dir() else []:
        meta_path = sub_path.with_name(sub_path.stem + ".meta.json")
        meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
        reports, last = [], ""
        for line in _lines(sub_path):
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if row.get("type") != "assistant":
                continue
            content = (row.get("message") or {}).get("content")
            last = text_of(content) or last
            for block in content if isinstance(content, list) else []:
                if isinstance(block, dict) and block.get("name") == "SubagentHandback":
                    reports.append(str((block.get("input") or {}).get("message", "")))
        out.append((f"{meta.get('agentType', '?')}: {meta.get('description', sub_path.stem)}", reports or ([last] if last else [])))
    return out


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
    ap.add_argument("--reports", action="store_true", help="print every sub-agent's final reports in full, not the passes")
    ap.add_argument("--pass", dest="which", choices=["1", "2", "3"], help="only pass 1 (user), 2 (side effects) or 3 (sub-agents)")
    args = ap.parse_args(argv)
    path = args.transcript or default_transcript(pathlib.Path.cwd())
    keep = {"1": {"compaction", "user", "mid", "answer"},
            "2": {"compaction", "bash", "file", "mcp", "tool", "sub-bash", "sub-file", "sub-mcp", "sub-tool"},
            "3": {"subagent"}}.get(args.which)
    print(f"transcript: {path}")
    if args.reports:
        for label, reports in subagent_reports(path):
            for n, report in enumerate(reports, 1):
                print(f"\n===== {label} (report {n} of {len(reports)}) =====\n{report}")
        return 0
    counts: dict[str, int] = {}
    for ts, kind, text in sorted([*events(path, args.since), *subagent_events(path, args.since)], key=lambda e: e[0]):
        if keep and kind not in keep:
            continue
        counts[kind] = counts.get(kind, 0) + 1
        print(f"{ts} {kind:10} {' '.join(text.split())[:240]}")
    print("counts: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
