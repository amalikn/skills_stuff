#!/usr/bin/env python3
"""Check Pad items against the writing standard: bold section labels, a closing DONE comment on closed work, logs attached. Read-only.

Operator, 2026-11-18: "have proper updates for a task ... proper information specifying when it changes to done state ... if you're working on
things which have logs, attach the log files to the task ... add this in the skill pad so that when the skill is used it will enforce that rule".
Run from a project folder whose .pad.toml names the workspace (or pass --workspace). For each item named (or every plan, task and bug updated in
the last --days days) it reads the item, its comments and its attachments through the pad CLI and reports:

    labels   a plan, task or bug body whose section labels are not bold on their own lines (**Serves:**, **Why:**, ...)
    done     a closed item (done, fixed, resolved, shipped, cancelled, wont-fix, declined) with no comment starting `... DONE:` or `... CLOSED:`
    update   an item in progress with no note and no comment at all
    logs     an item whose body, notes or comments name a log file while the item has no attachment
    comments a comment from 2026-11-18 on, longer than 200 characters, with no `- **Label:**` bullet line (the update form)
    refs     an item ref (TASK-12) or decision id (DL-058) as plain text, not a `[[...]]` link, in the body or in a comment from 2026-11-20 on
             (operator, 2026-11-20: "why are these references not links"); `just links` fixes bodies

Usage:
    python3 pad_item_check.py TASK-57 BUG-66            # these items
    python3 pad_item_check.py --days 2                  # every plan, task and bug touched in the last two days
Options: --workspace SLUG, --pad PATH, --timeout SECONDS.
Exit: 0 clean, 1 findings, 2 a pad call failed or bad arguments. Writes nothing. Budget: three pad calls per item (about 0.2 s each; a rate-limited call is retried up to five times with a growing pause); prints its time.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone

LABELS = {  # required labels per collection: docs/pad-usage-guidelines-20261110_1628.md 3.3, Templates by collection (operator, 2026-11-20)
    "plans": ("Serves", "Goal", "Done when", "Out of scope", "Waits on"),
    "tasks": ("Serves", "Why", "Do", "Done when", "Writes", "Refs"),
    "bugs": ("Seen", "Evidence", "Effect", "Closure"),
    "tech-debt": ("Serves", "Why", "Do", "Done when"),
    "ideas": ("Serves", "Why", "Do"),
    "asks": ("Question",),
    "feature-requests": ("Serves", "Why"),
    "decisions": ("Serves", "Decision"),
    "conventions": ("Rule", "Source"),
}
WORK = {"plans", "tasks", "bugs", "tech-debt"}  # collections whose closed items need a DONE: or CLOSED: comment
CLOSED = {"done", "fixed", "resolved", "shipped", "cancelled", "wont-fix", "declined", "completed"}
CLOSING = re.compile(r"\b(DONE|CLOSED):")
RETRIES = 5
BACKOFF_S = 1.5
LOG_NAME = re.compile(r"[\w./-]+\.(log|jsonl|out)\b")
PREFIXES = ("TASK", "PLAN", "BUG", "ASK", "DECIS", "IDEA", "DOC", "FR", "TD", "PLAYB", "CONVE")  # Pad's collection prefixes (pad collection list)
BARE_REF = re.compile(r"\b(?:" + "|".join(PREFIXES) + r")-\d+\b|\bDL-\d{3}\b")
ITEM_REF = re.compile(r"\b(?:" + "|".join(PREFIXES) + r")-\d+\b")  # without decision ids, for a workspace with no Decisions collection
PROTECTED = re.compile(r"```.*?```|`[^`\n]*`|\[\[[^\]]*\]\]", re.S)
BULLET = re.compile(r"^- \*\*[^*]+:\*\*", re.M)
COMMENT_FORM_SINCE = "2026-11-18"  # the update form (bold-label bullets) is required from here
LINKS_SINCE = "2026-11-20"  # references as [[links]] are required from here
SKIP_REFS = {"decisions", "playbooks", "conventions"}  # generated or library text (pad_links skips them too)


def pad(args: list[str], timeout: int, binary: str = "pad") -> str:
    """Run one pad command and return its stdout.

    Args:
        args: the arguments after `pad`.
        timeout: seconds before the call is abandoned.
        binary: the pad binary.

    Returns:
        stdout.

    Raises:
        RuntimeError: pad failed, timed out, or stayed rate-limited after the retries.
    """
    for attempt in range(RETRIES):
        try:
            p = subprocess.run([binary, *args], capture_output=True, text=True, timeout=timeout)
        except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
            raise RuntimeError(f"pad {' '.join(args[:3])}: {exc}") from exc
        if p.returncode == 0:
            return p.stdout
        if "rate_limited" not in p.stderr or attempt == RETRIES - 1:
            break
        time.sleep(BACKOFF_S * (attempt + 1))  # the server asks for about a second; a run over many items meets the limit
    raise RuntimeError(f"pad {' '.join(args[:3])} exited {p.returncode}: {p.stderr.strip()[-300:]}")


def fields_of(item: dict) -> dict:
    """An item's fields as a dict (the CLI returns them as a JSON string).

    Args:
        item: one item as `pad item show --format json` gives it.

    Returns:
        The fields; empty when there are none.
    """
    raw = item.get("fields") or {}
    return json.loads(raw) if isinstance(raw, str) else raw


def missing_labels(collection: str, body: str) -> list[str]:
    """The standard labels a body lacks as a bold label at the start of a line.

    Args:
        collection: the item's collection slug.
        body: the item body.

    Returns:
        The missing labels, in the standard's order; empty for a collection without a standard.
    """
    return [lab for lab in LABELS.get(collection, ()) if not re.search(rf"^\*\*{re.escape(lab)}:\*\*", body, re.M)]


def one_line_request(item: dict) -> bool:
    """Whether an item is a feature request that is only the operator's own line, which keeps no labels (its title may be that line cut to 100 characters).

    Args:
        item: the item (collection_slug, content).

    Returns:
        True for a feature request whose body is one line.
    """
    return item.get("collection_slug") == "feature-requests" and "\n" not in (item.get("content") or "").strip()


def bare_refs(text: str, own: str = "", decision_ids: bool = True) -> list[str]:
    """Item refs and decision ids written as plain text, outside links, inline code and fenced blocks.

    Args:
      text: a body or a comment.
      own: the item's own ref, which may appear plain.

    Returns:
      The plain references, in order, without repeats.
    """
    plain = PROTECTED.sub(" ", text)
    seen = []
    for m in (BARE_REF if decision_ids else ITEM_REF).finditer(plain):
        if m.group(0) != own and m.group(0) not in seen:
            seen.append(m.group(0))
    return seen


def findings(item: dict, comments: list[dict], attachments: int, decision_ids: bool = True, known: set[str] | None = None) -> list[str]:
    """What one item breaks of the writing standard.

    Args:
        item: the item (collection_slug, content, fields, implementation_notes).
        comments: its comments, each with `body`.
        attachments: how many files are attached to it.
        decision_ids: report plain DL-nnn ids too (the workspace has a Decisions collection).
        known: the workspace's item refs; a plain ref not among them (another workspace's item, a typo) cannot be linked and is not reported.

    Returns:
        One line per finding; empty when the item meets the standard.
    """
    out = []
    body = item.get("content") or ""
    lacking = [] if one_line_request(item) else missing_labels(item.get("collection_slug", ""), body)
    if lacking:
        out.append(f"labels: no bold `**{lacking[0]}:**` line" + (f" (and {len(lacking) - 1} more)" if len(lacking) > 1 else ""))
    status = str(fields_of(item).get("status", "")).lower()
    texts = [c.get("body") or "" for c in comments]
    notes = [json.dumps(n) for n in item.get("implementation_notes") or []]
    if item.get("collection_slug") in WORK and status in CLOSED and not any(CLOSING.search(t) for t in texts):
        out.append(f"done: status {status} with no closing comment (`YYYY-MM-DD HH:MM AEDT DONE:` and what was done, the result, evidence, what stays open)")
    if status == "in-progress" and not texts and not notes:
        out.append("update: in progress with no note or comment")
    if item.get("collection_slug") in WORK and attachments == 0 and any(LOG_NAME.search(t) for t in [body, *texts, *notes]):
        out.append("logs: a log file is named but nothing is attached (`pad attachment upload <ref> <file>`)")
    unformed = [c for c in comments if str(c.get("created_at", "")) >= COMMENT_FORM_SINCE and len(c.get("body") or "") > 200 and not BULLET.search(c.get("body") or "")]
    if unformed:
        out.append(f"comments: {len(unformed)} long comment(s) not in the bullet form (`- **What:**`, `- **Result:**` ...), first {str(unformed[0].get('id', ''))[:8]}")
    if item.get("collection_slug") not in SKIP_REFS:
        own = item.get("ref", "")
        plain = bare_refs(body, own, decision_ids)
        for c in comments:
            if str(c.get("created_at", "")) >= LINKS_SINCE:
                plain += [r for r in bare_refs(c.get("body") or "", own, decision_ids) if r not in plain]
        if known is not None:
            plain = [r for r in plain if r.startswith("DL-") or r in known]
        if plain:
            out.append(f"refs: {', '.join(plain[:5])}{' ...' if len(plain) > 5 else ''} not written as [[links]] (`just links` fixes bodies)")
    return out


def recent_refs(days: int, timeout: int, binary: str, extra: list[str]) -> list[str]:
    """The refs of every item of a templated collection updated in the last `days` days.

    Args:
        days: the window.
        timeout: seconds per pad call.
        binary: the pad binary.
        extra: global pad flags (--workspace).

    Returns:
        The refs, plans first.

    Raises:
        RuntimeError: a pad call failed.
    """
    since = datetime.now(timezone.utc) - timedelta(days=days)
    refs = []
    for coll in LABELS:
        try:
            rows = json.loads(pad(["item", "list", coll, "--all", "--format", "json", *extra], timeout, binary) or "[]")
        except RuntimeError as error:
            if "not found" in str(error):  # a workspace without this collection (2026-11-20: enterprise-strategy has no bugs, ansible-wifi no asks)
                continue
            raise
        rows = rows if isinstance(rows, list) else rows.get("items", [])
        for r in rows:
            when = datetime.fromisoformat(str(r.get("updated_at", "1970-01-01T00:00:00Z")).replace("Z", "+00:00"))
            if when >= since:
                refs.append(r["ref"])
    return refs


def main(argv: list[str] | None = None) -> int:
    """Check the named or the recent items of one workspace and print the findings.

    Args:
        argv: the command line (default sys.argv).

    Returns:
        0 clean, 1 findings, 2 a pad call failed.
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("refs", nargs="*", help="item refs (TASK-5); none: every item of a templated collection updated in the last --days days")
    ap.add_argument("--days", type=int, default=2)
    ap.add_argument("--workspace", default=None)
    ap.add_argument("--pad", default="pad")
    ap.add_argument("--timeout", type=int, default=30)
    a = ap.parse_args(argv)
    extra = ["--workspace", a.workspace] if a.workspace else []
    started = time.monotonic()
    bad = 0
    try:
        refs = a.refs or recent_refs(a.days, a.timeout, a.pad, extra)
        colls = json.loads(pad(["collection", "list", "--format", "json", *extra], a.timeout, a.pad) or "[]")
        has_decisions = any(c.get("slug") == "decisions" for c in colls)
        listed = json.loads(pad(["item", "list", "--all", "--format", "json", *extra], a.timeout, a.pad) or "[]")
        known = {r["ref"] for r in (listed if isinstance(listed, list) else listed.get("items", []))}
        for ref in refs:
            item = json.loads(pad(["item", "show", ref, "--format", "json", *extra], a.timeout, a.pad))
            comments = json.loads(pad(["item", "comments", ref, "--format", "json", *extra], a.timeout, a.pad) or "[]")
            att = json.loads(pad(["attachment", "list", "--item", ref, "--format", "json", *extra], a.timeout, a.pad) or "{}")
            for line in findings(item, comments or [], int(att.get("total", 0)), has_decisions, known):
                bad += 1
                print(f"{ref}: {line}")
    except (RuntimeError, json.JSONDecodeError) as exc:
        print(f"pad_item_check: {exc}", file=sys.stderr)
        return 2
    print(f"{len(refs)} item(s) checked, {bad} finding(s); {time.monotonic() - started:.1f} s")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
