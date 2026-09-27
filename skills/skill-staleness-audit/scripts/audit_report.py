#!/usr/bin/env python3
"""Write the audit report into the project, with the audit's evidence embedded, BEFORE the gate deletes the scratch.

WHY THIS EXISTS
---------------
On PASS the Phase 7 gate deletes `.staleness-audit/` — the receipts, the defect register and the Phase 4 worksheet, which
are the audit's main evidence. Nothing required them to be kept anywhere first. The sixth audit of
unified-network-controller (2026-09-26) left no report at all, and the seventh (2026-09-27) kept its register and
worksheet only because the agent copied them out by hand before running the gate.

So the report is now a product of the scratch, not of memory:

  * this script writes `staleness-audit-<YYYYMMDD_hhmm>.md` into the project's audit folder: the narrative skeleton from
    templates/audit-report.md (for the agent to fill), plus a MANAGED evidence block holding the receipts, every
    negative-test excerpt, and each filled working file from `.staleness-audit/` verbatim (headings demoted two levels);
  * the evidence block carries a sha256 of the files it embeds, and `verify_completeness.py` refuses to delete anything
    unless the report exists, its sha matches the scratch it is about to delete, and no template placeholder is left in
    the narrative. On PASS the gate then writes its own result into the report and only then cleans up.

Re-running replaces only the managed block (and the Contents list); the narrative the agent wrote is kept.

Usage:
    audit_report.py [--root .] [--out-dir DIR] [--stamp YYYYMMDD_hhmm]

    --out-dir  the project's audit folder. Default: the folder holding the newest existing staleness-audit-*.md report.
               With no earlier report, it must be given.

Exit codes: 0 written · 2 error
"""
# claim-scan:examples — paths in this docstring are runtime artifacts and illustrative examples.
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATES = HERE.parent / "templates"
STATE_DIR = ".staleness-audit"
EVIDENCE_BEGIN = "<!-- BEGIN staleness-audit:evidence"
EVIDENCE_END = "<!-- END staleness-audit:evidence -->"
GATE_BEGIN = "<!-- BEGIN staleness-audit:gate -->"
GATE_END = "<!-- END staleness-audit:gate -->"
# Working files first in this order; any other filled .md in the scratch dir follows alphabetically.
ORDER = ("defect-register.md", "phase4-worksheet.md", "residual-risk-register.md")
# The report skeleton itself is never embedded as evidence.
NOT_EVIDENCE = {"audit-report.md"}
PLACEHOLDER = re.compile(r"`<[^`>\n]+>`|<N>")


def evidence_files(root: Path) -> list[Path]:
    """Filled working files in the scratch dir. A template copied in and never touched is not evidence, it is noise."""
    d = root / STATE_DIR
    if not d.is_dir():
        return []
    found = []
    for p in sorted(d.glob("*.md")):
        if p.name in NOT_EVIDENCE:
            continue
        tpl = TEMPLATES / p.name
        if tpl.is_file() and tpl.read_bytes() == p.read_bytes():
            continue
        found.append(p)
    rank = {n: i for i, n in enumerate(ORDER)}
    return sorted(found, key=lambda p: (rank.get(p.name, len(ORDER)), p.name))


def evidence_sha(root: Path) -> str:
    h = hashlib.sha256()
    for p in evidence_files(root):
        h.update(p.name.encode() + b"\0" + p.read_bytes() + b"\0")
    return h.hexdigest()


def demote(text: str, by: int = 2) -> str:
    """Push every heading down `by` levels so an embedded file nests under its section. Code fences are left alone."""
    out, fence = [], False
    for line in text.splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            fence = not fence
        if not fence and re.match(r"#{1,6} ", line):
            line = "#" * by + line
        out.append(line)
    return "\n".join(out)


def receipts_block(state: dict) -> list[str]:
    lines = ["### Receipts", "", "| Phase | Key | Value |", "|---|---|---|"]
    for n in sorted(state.get("phases", {}), key=int):
        entry = state["phases"][n]
        for k, v in entry.get("data", {}).items():
            lines.append(f"| {n} | `{k}` | {str(v).replace('|', '/')} |")
        for note in entry.get("notes", []):
            lines.append(f"| {n} | note | {str(note).replace('|', '/')} |")
    if state.get("since"):
        lines += ["", f"Focus: files changed since `{state['since']['ref']}` (`{state['since']['sha'][:12]}`)."]
    tests = state.get("phases", {}).get("5", {}).get("negtests", {})
    if tests:
        lines += ["", "### Negative tests", ""]
        for cid, ev in sorted(tests.items()):
            for leg in ("red", "green"):
                if leg not in ev:
                    continue
                e = ev[leg]
                lines.append(f"- **{cid}** {leg} — {'accepted' if e['ok'] else 'REFUSED'}; exit {e['exit']}; "
                             f"`{e['cmd']}`; expect `{e['expect']}`; output sha256 `{e['output_sha256'][:16]}`; "
                             f"{e['at']}")
                lines += ["", "  ```text"] + [f"  {x}" for x in e.get("excerpt", [])] + ["  ```", ""]
    return lines


def evidence_block(root: Path, state: dict) -> str:
    body = [f"{EVIDENCE_BEGIN} sha256={evidence_sha(root)} -->",
            "## Audit evidence",
            "",
            "Generated by `audit_report.py` from `.staleness-audit/` before the gate deleted it. Do not edit by hand; re-run the",
            "script instead.",
            ""]
    body += receipts_block(state)
    for p in evidence_files(root):
        body += ["", f"### `{p.name}`", "", demote(p.read_text(encoding="utf-8")).rstrip(), ""]
    body.append(EVIDENCE_END)
    return "\n".join(body)


def slug(heading: str) -> str:
    """GitHub/VS Code anchor: lowercase, drop punctuation except - and _, spaces to hyphens."""
    h = heading.strip().lower().replace("`", "")
    h = re.sub(r"[^\w\- ]", "", h)
    return h.replace(" ", "-")


def refresh_contents(text: str) -> str:
    """Keep a `## Contents` list of the H2 sections once the report passes 100 lines (the markdown-guide rule)."""
    lines = text.splitlines()
    fence, h2 = False, []
    for ln in lines:
        if ln.lstrip().startswith(("```", "~~~")):
            fence = not fence
        if not fence and ln.startswith("## ") and ln[3:].strip() != "Contents":
            h2.append(ln[3:].strip())
    toc = ["## Contents", ""] + [f"- [{h.replace('`', '')}](#{slug(h)})" for h in h2] + [""]
    if "## Contents" in lines:
        i = lines.index("## Contents")
        j = i + 1
        while j < len(lines) and not lines[j].startswith(("## ", "---")):
            j += 1
        lines[i:j] = toc
    elif len(lines) > 100:
        first_h2 = next((i for i, ln in enumerate(lines) if ln.startswith("## ")), len(lines))
        lines[first_h2:first_h2] = toc
    return "\n".join(lines) + "\n"


def replace_block(text: str, begin: str, end: str, block: str) -> str:
    i = text.find(begin)
    if i >= 0:
        j = text.find(end, i)
        if j < 0:
            raise ValueError(f"report has {begin!r} with no matching end marker")
        return text[:i] + block + text[j + len(end):]
    return text.rstrip("\n") + "\n\n" + block + "\n"


def report_problems(root: Path, state: dict) -> list[str]:
    """Why the gate must NOT delete the scratch yet. Empty list = the report holds the evidence."""
    rep = state.get("report", {}).get("path")
    if not rep:
        return ["no audit report written — run audit_report.py so the register, worksheet and receipts survive the "
                "cleanup"]
    p = root / rep
    if not p.is_file():
        return [f"audit report {rep} is recorded but missing"]
    text = p.read_text(encoding="utf-8")
    m = re.search(re.escape(EVIDENCE_BEGIN) + r" sha256=([0-9a-f]+) -->", text)
    if not m:
        return [f"audit report {rep} has no evidence block — re-run audit_report.py"]
    if m.group(1) != evidence_sha(root):
        return [f"audit report {rep} is stale: the scratch changed after it was written — re-run audit_report.py"]
    narrative = text[:m.start()]
    tpl = TEMPLATES / "audit-report.md"
    template_tokens = set(PLACEHOLDER.findall(tpl.read_text(encoding="utf-8"))) if tpl.is_file() else set()
    left = sorted({t for t in PLACEHOLDER.findall(narrative) if t in template_tokens})
    if left:
        return [f"audit report {rep} still has {len(left)} unfilled template placeholder(s): {', '.join(left[:6])}"]
    return []


def write_gate_block(root: Path, rel: str, lines: list[str]) -> None:
    p = root / rel
    block = "\n".join([GATE_BEGIN, "## Gate result", "", "```text", *lines, "```", GATE_END])
    p.write_text(refresh_contents(replace_block(p.read_text(encoding="utf-8"), GATE_BEGIN, GATE_END, block)),
                 encoding="utf-8")


def discover_out_dir(root: Path) -> Path | None:
    reports = [p for p in root.rglob("staleness-audit-*.md")
               if not any(part.startswith(".staleness-audit") or part == "archive"
                          for part in p.relative_to(root).parts)]
    return max(reports, key=lambda p: p.name).parent if reports else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--stamp", default=None, help="YYYYMMDD_hhmm; default is the local clock now")
    a = ap.parse_args()

    root = Path(a.root).resolve()
    sp = root / STATE_DIR / "state.json"
    if not sp.is_file():
        sys.stderr.write("ERROR: no audit in progress — nothing to report\n")
        return 2
    state = json.loads(sp.read_text(encoding="utf-8"))

    existing = state.get("report", {}).get("path")
    if existing and (root / existing).is_file() and not a.out_dir and not a.stamp:
        target = root / existing
    else:
        out = (root / a.out_dir) if a.out_dir else discover_out_dir(root)
        if out is None:
            sys.stderr.write("ERROR: no earlier staleness-audit-*.md report to locate the audit folder from — pass "
                             "--out-dir\n")
            return 2
        stamp = a.stamp or datetime.now().strftime("%Y%m%d_%H%M")
        if not re.fullmatch(r"\d{8}_\d{4}", stamp):
            sys.stderr.write(f"ERROR: --stamp must be YYYYMMDD_hhmm, got {stamp!r}\n")
            return 2
        out.mkdir(parents=True, exist_ok=True)
        target = out / f"staleness-audit-{stamp}.md"

    if target.is_file():
        text = target.read_text(encoding="utf-8")
    else:
        skel = root / STATE_DIR / "audit-report.md"
        src = skel if skel.is_file() else TEMPLATES / "audit-report.md"
        text = src.read_text(encoding="utf-8")
    text = replace_block(text, EVIDENCE_BEGIN, EVIDENCE_END, evidence_block(root, state))
    target.write_text(refresh_contents(text), encoding="utf-8")

    rel = target.relative_to(root).as_posix()
    state["report"] = {"path": rel}
    sp.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    n = len(evidence_files(root))
    print(f"wrote {rel} — receipts + {n} working file(s) embedded")
    left = report_problems(root, state)
    if left:
        print(f"  still to do before the gate: {left[0]}")
    print("  Index it in its folder readme, fill the narrative, then run verify_completeness.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
