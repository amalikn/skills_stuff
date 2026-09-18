#!/usr/bin/env python3
"""Sole sanctioned writer for skill-walk-before-run's ledger.jsonl.

Enforces the schema in ../schemas/ledger-entry.md and performs the
"Project write-back" steps from ../SKILL.md (project mirror + SCRATCHPAD
pointer) in the same call, so a RED/RESOLVED entry can't be written to the
canonical ledger without also reaching the mirror. An OPA policy rule
hard-blocks any Bash/Write/Edit call that touches ledger.jsonl or a
.wbr-ledger.jsonl mirror directly -- this script is the one path around it.

Usage:
    python3 append_entry.py --entry-json '<json>' [--project-root <path>]

The JSON object uses the exact field names from schemas/ledger-entry.md.
`ts` and `branch` are filled in automatically if omitted (ts = now, local
offset; branch = git branch --show-current in --project-root or cwd).
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
LEDGER_PATH = SKILL_DIR / "ledger.jsonl"

REQUIRED_ALL = ["project", "branch", "verdict", "assumption"]
REQUIRED_RED = ["reason", "next_test", "waiver"]
REQUIRED_RESOLVED = ["result", "killed"]


def die(msg: str) -> None:
    print(f"append_entry.py: {msg}", file=sys.stderr)
    sys.exit(1)


def git_branch(cwd: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=cwd, capture_output=True, text=True, timeout=5,
        )
        branch = out.stdout.strip()
        return branch if branch else "n/a"
    except Exception:
        return "n/a"


def validate(entry: dict) -> None:
    for field in REQUIRED_ALL:
        if not entry.get(field):
            die(f"missing required field '{field}'")

    verdict = entry["verdict"]
    if verdict not in ("RED", "RESOLVED"):
        die(f"verdict must be 'RED' or 'RESOLVED', got {verdict!r}")

    if verdict == "RED":
        for field in REQUIRED_RED:
            if field not in entry:
                die(f"RED entry missing required field '{field}'")
        if not isinstance(entry["waiver"], bool):
            die("'waiver' must be a boolean")
    else:
        for field in REQUIRED_RESOLVED:
            if not entry.get(field):
                die(f"RESOLVED entry missing required field '{field}'")
        if entry["result"] not in ("PASS", "FAIL"):
            die(f"'result' must be 'PASS' or 'FAIL', got {entry['result']!r}")

    entry.setdefault("learned", None)


FIELD_ORDER = [
    "ts", "project", "branch", "verdict", "assumption",
    "reason", "next_test", "waiver",
    "result", "killed",
    "learned",
]


def ordered(entry: dict) -> dict:
    return {k: entry[k] for k in FIELD_ORDER if k in entry}


def append_jsonl(path: Path, line: str) -> None:
    with path.open("a") as f:
        f.write(line + "\n")


def prior_project_lines(project: str) -> list:
    """Entries for `project` already in the canonical ledger, read BEFORE the
    current entry is appended -- callers append the current line separately
    so it's never double-counted when seeding a missing mirror."""
    lines = []
    if LEDGER_PATH.exists():
        with LEDGER_PATH.open() as f:
            for raw in f:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    if json.loads(raw).get("project") == project:
                        lines.append(raw)
                except json.JSONDecodeError:
                    continue
    return lines


def seed_and_append_mirror(mirror_path: Path, prior_lines: list, new_line: str) -> None:
    if mirror_path.exists():
        append_jsonl(mirror_path, new_line)
        return
    # Missing (never created, or deleted since) -- self-heal: seed with every
    # prior entry for this project, then the current one.
    with mirror_path.open("w") as f:
        for line in prior_lines:
            f.write(line + "\n")
        f.write(new_line + "\n")


def write_scratchpad_pointer(scratchpad_path: Path, entry: dict) -> None:
    if not scratchpad_path.exists():
        return
    date = entry["ts"][:10]
    ledger_ref = f"`{SKILL_DIR}/ledger.jsonl`"
    if entry["verdict"] == "RED":
        pointer = (
            f"- [ ] **skill-walk-before-run RED, {date}** — {entry['assumption']}. "
            f"Next test: {entry['next_test']}. Full entry: {ledger_ref}."
        )
    else:
        pointer = (
            f"- [x] **skill-walk-before-run RESOLVED, {date}** — {entry['assumption']}, "
            f"result: {entry['result']}. Full entry: {ledger_ref}."
        )

    lines = scratchpad_path.read_text().splitlines()
    heading_idx = next(
        (i for i, l in enumerate(lines) if l.strip() == "## Open items"), None
    )
    if heading_idx is None:
        return  # No such section -- skip silently, per SKILL.md.

    insert_at = len(lines)
    for i in range(heading_idx + 1, len(lines)):
        if lines[i].startswith("## "):
            insert_at = i
            break
    lines.insert(insert_at, pointer)
    scratchpad_path.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entry-json", required=True, help="JSON object matching schemas/ledger-entry.md")
    parser.add_argument("--project-root", help="Target project's root directory, for mirror + SCRATCHPAD write-back")
    args = parser.parse_args()

    try:
        entry = json.loads(args.entry_json)
    except json.JSONDecodeError as e:
        die(f"--entry-json is not valid JSON: {e}")

    project_root = Path(args.project_root).resolve() if args.project_root else None

    entry.setdefault("ts", datetime.now().astimezone().isoformat(timespec="seconds"))
    entry.setdefault("branch", git_branch(project_root or Path.cwd()))

    validate(entry)

    line = json.dumps(ordered(entry), sort_keys=False)
    prior_lines = prior_project_lines(entry["project"])  # snapshot before append
    append_jsonl(LEDGER_PATH, line)
    print(f"appended to {LEDGER_PATH}")

    if project_root is None:
        print("no --project-root given -- skipping mirror + SCRATCHPAD write-back", file=sys.stderr)
        return

    mirror_path = project_root / ".wbr-ledger.jsonl"
    seed_and_append_mirror(mirror_path, prior_lines, line)
    print(f"mirrored to {mirror_path}")

    scratchpad_path = project_root / "SCRATCHPAD.md"
    before = scratchpad_path.read_text() if scratchpad_path.exists() else None
    write_scratchpad_pointer(scratchpad_path, entry)
    if before is not None and scratchpad_path.read_text() != before:
        print(f"pointer appended to {scratchpad_path}")
    elif scratchpad_path.exists():
        print(f"'## Open items' section not found in {scratchpad_path} -- pointer skipped", file=sys.stderr)
    else:
        print(f"{scratchpad_path} does not exist -- pointer skipped (never created per SKILL.md)", file=sys.stderr)


if __name__ == "__main__":
    main()
