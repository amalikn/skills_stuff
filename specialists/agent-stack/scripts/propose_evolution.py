#!/usr/bin/env python3
"""Turn field evidence into dated PROPOSALS for the operator. Never edits the catalogue.

WHY THIS EXISTS. Retiring the upstream sync on 2026-09-03 removed the only mechanism that ever added to this stack. Without a replacement the library is frozen at whatever it happened to contain, and
the field log accumulates evidence nobody acts on. This is the replacement, and it is deliberately the weaker of the two possible designs.

WHY IT PROPOSES INSTEAD OF APPLYING. Rule 0001 excludes unattended agents, implicit persistent state, and material change without explicit operator authority — that exclusion is the reason this
project exists as a fork rather than a copy. A tool that rewrote `routing.toml` from observational data would breach it, and would do so using the weakest evidence in the project: self-reported,
confounded, small-n. The retired sync had exactly the right shape and it is worth keeping after the tool itself is gone — apply the safe classes automatically, write everything else as a review
proposal. Here, NOTHING is safe enough to apply automatically, so everything is a proposal.

WHAT IT WILL NOT DO. It will not invent a skill, write a persona, or rank its own suggestions as urgent. It reports what the evidence shows and what that would imply, and stops. Authoring is
`skill-creator`'s job and the decision is yours.
"""
from __future__ import annotations

import argparse
import json
import tomllib
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FIELD_LOG = ROOT / "evals" / "field-log.jsonl"
ROUTING = ROOT / "routing.toml"

# Below these counts a pattern is an anecdote. Stated as constants so the thresholds are arguable rather than buried.
REPEATED_OVERRIDE = 3   # same owner overridden this many times before it is worth a precedence question
REPEATED_GAP = 2        # the same skill called inadequate this many times before it is worth acting on
UNUSED_AFTER = 20       # field uses before "never selected" means anything at all
MIN_ENTRIES = 10        # below this the tool reports the shortfall and proposes nothing

# Agent Stack's own copy of what personas said the library was missing, written at declaration time by scripts/persona_note.py and tracked here in git.
GAP_LOG = ROOT / "evals" / "capability-gaps.jsonl"


def load_rows() -> list[dict[str, Any]]:
    if not FIELD_LOG.is_file():
        return []
    return [json.loads(l) for l in FIELD_LOG.read_text().splitlines() if l.strip()]


def declared_gaps(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Every gap a persona declared while working.

    DECLARED, never inferred. A persona knows at the moment it works whether it needed a procedure that does not exist, or reached for one that did not deliver.
    That judgement cannot be recovered from its prose afterwards, and pretending to recover it by matching words would manufacture findings.

    READ FROM AGENT STACK'S OWN LOG FIRST. The manifests live in consuming projects, and a project can move, be deleted, or be one this library must not read —
    at which point a gap recorded only there is gone, and the library's growth signal with it. 39 of 40 indexed runs already stamp a corpus hash that no longer
    resolves; a pointer to evidence elsewhere is not a record. The manifests are still read when reachable, because a run captured before this log existed is
    still evidence, and because a project may hold gaps from a run whose field-log entry was never written. Duplicates collapse on identity.
    """
    seen: set[tuple] = set()
    out: list[dict[str, Any]] = []

    def take(g: dict[str, Any], project: str, run_dir: str) -> None:
        key = (g.get("kind"), g.get("persona"), g.get("text"), g.get("at"))
        if key in seen:
            return
        seen.add(key)
        out.append({**g, "project": g.get("project") or project, "run_dir": g.get("run_dir") or run_dir})

    if GAP_LOG.is_file():
        for line in GAP_LOG.read_text().splitlines():
            if line.strip():
                try:
                    g = json.loads(line)
                except json.JSONDecodeError:
                    continue
                take(g, g.get("project", "?"), g.get("run_dir", ""))

    for r in rows:
        d = r.get("run_dir")
        if not d:
            continue
        manifest = Path(d) / "MANIFEST.json"
        if not manifest.is_file():
            continue
        try:
            m = json.loads(manifest.read_text())
        except json.JSONDecodeError:
            continue
        for g in m.get("gaps", []):
            take(g, r.get("project", "?"), d)
    return out


def propose(rows: list[dict[str, Any]], routing: dict[str, Any]) -> list[dict[str, str]]:
    """Every proposal names the evidence that produced it, so a reader can disagree with the inference rather than the conclusion."""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from field_log import is_override

    out: list[dict[str, str]] = []
    overrides = [r for r in rows if is_override(r.get("overrode"))]

    # 1. A repeatedly overridden owner is an ownership boundary the precedence table does not settle.
    for owner, n in Counter(r.get("owner") for r in overrides if r.get("owner")).most_common():
        if n >= REPEATED_OVERRIDE:
            examples = [r["overrode"][:120] for r in overrides if r.get("owner") == owner][:3]
            out.append({"kind": "precedence", "subject": owner,
                        "evidence": f"overridden {n} times as primary owner",
                        "implication": "an ownership boundary the [[precedence]] table does not settle; the fix is a rule naming the discriminating question and BOTH answers",
                        "examples": "; ".join(examples)})

    # 2. Routes rated worse are the only direct evidence that a correct route can still be the wrong one.
    worse = [r for r in rows if r.get("helped") == "worse"]
    if worse:
        out.append({"kind": "harm", "subject": f"{len(worse)} route(s)",
                    "evidence": "operator rated the outcome worse",
                    "implication": "the only evidence class that can show a corpus-correct route making work worse; read these before any other proposal",
                    "examples": "; ".join(r.get("task", "")[:90] for r in worse[:3])})

    # 3. Capability the field asked for and the catalogue does not name.
    known = {s["id"] for s in routing.get("skills", [])} | {p["id"] for p in routing.get("personas", [])}
    if len(rows) >= UNUSED_AFTER:
        used = {x for r in rows for x in (r.get("skills") or []) + (r.get("personas") or []) + ([r["owner"]] if r.get("owner") else [])}
        never = sorted(known - used)
        if never:
            out.append({"kind": "unused", "subject": f"{len(never)} capabilities",
                        "evidence": f"never selected across {len(rows)} field uses",
                        "implication": "either the catalogue describes them badly enough that routing never reaches them, or they do not earn their place. Check the description before retiring anything",
                        "examples": ", ".join(never[:12])})

    # 4/5. What the personas said they lacked while working. This is the library's growth signal and the reason the raw notes are kept.
    gaps = declared_gaps(rows)
    inadequate = [g for g in gaps if g["kind"] == "inadequate"]
    # `inadequate` gaps name a skill before the colon, so they group EXACTLY. That is a real aggregation rather than a guess at what two sentences have in common.
    by_skill: dict[str, list[dict[str, Any]]] = {}
    for g in inadequate:
        skill = g["text"].split(":", 1)[0].strip()
        by_skill.setdefault(skill, []).append(g)
    for skill, items in sorted(by_skill.items(), key=lambda kv: -len(kv[1])):
        if len(items) >= REPEATED_GAP:
            out.append({"kind": "skill-inadequate", "subject": skill,
                        "evidence": f"declared inadequate {len(items)} times by {len(({i['persona'] for i in items}))} persona(s) across {len({i['project'] for i in items})} project(s)",
                        "implication": "the skill was reached for and did not do the job. Read the reasons before rewriting it — they may describe different jobs rather than one defect",
                        "examples": "; ".join(i["text"].split(":", 1)[-1].strip()[:110] for i in items[:3])})

    missing = [g for g in gaps if g["kind"] == "missing"]
    if missing:
        # NOT clustered. Two personas describing the same absent capability in different words is a judgement, and a tool that guessed at it would invent a
        # skill nobody asked for. Listed for the operator; `skill-creator` authors it when the operator decides the cluster is real.
        out.append({"kind": "capability-absent", "subject": f"{len(missing)} declaration(s)",
                    "evidence": f"personas reported needing a procedure the library does not have, across {len({g['project'] for g in missing})} project(s)",
                    "implication": "candidate NEW skills. Deliberately NOT clustered — deciding that two differently-worded needs are the same capability is your judgement, and authoring is `skill-creator`'s job",
                    "examples": " | ".join(f"{g['persona']}: {g['text'][:100]}" for g in missing[:6])})

    # 6. Cost, which is the argument against the stack rather than for it.
    costed = [r for r in rows if isinstance(r.get("tokens_estimated"), int)]
    team = [r for r in costed if r.get("dispatched")]
    if len(team) >= REPEATED_OVERRIDE:
        helped = Counter(r.get("helped") for r in team if r.get("helped"))
        if helped and helped.get("better", 0) == 0:
            out.append({"kind": "cost", "subject": f"{len(team)} dispatching route(s)",
                        "evidence": f"none rated better; ratings {dict(helped)}",
                        "implication": "dispatch is being paid for and not yet shown to buy anything. This proposal argues AGAINST the stack and is included for that reason",
                        "examples": ""})
    return out


def render(rows: list[dict[str, Any]], proposals: list[dict[str, str]]) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    lines = [f"Title: Evolution proposals — {stamp}", "Category: evaluation-record", "Status: proposed",
             f"Source: evals/field-log.jsonl ({len(rows)} entries)", f"Last reviewed: {stamp}",
             "Summary: Proposals derived from field evidence. Nothing here has been applied; every item is a question for the operator.", "",
             f"# Evolution proposals — {stamp}", "",
             f"Derived from **{len(rows)} field entries** and the persona notes they point at. **Nothing in this file has been applied.** Each item names the evidence that produced it so you can disagree with the inference rather than",
             "the conclusion. Authoring a new skill is `skill-creator`'s job; changing the catalogue is yours.", ""]
    if len(rows) < MIN_ENTRIES:
        lines += [f"## Insufficient evidence", "",
                  f"**{len(rows)} entries, below the {MIN_ENTRIES} this tool will draw from.** No proposals. This is the correct output, not a failure: a pattern in a handful of self-reported",
                  "entries is an anecdote, and acting on it would put the weakest evidence in the project in charge of the catalogue.", ""]
        return "\n".join(lines) + "\n"
    if not proposals:
        lines += ["## No proposals", "", "The thresholds were met and nothing crossed them. Recorded so the run is distinguishable from one that never happened.", ""]
    for i, p in enumerate(proposals, 1):
        lines += [f"## {i}. {p['kind']} — {p['subject']}", "",
                  f"- **Evidence:** {p['evidence']}", f"- **What it would imply:** {p['implication']}"]
        if p["examples"]:
            lines.append(f"- **From the log:** {p['examples']}")
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Propose catalogue changes from field evidence. Writes a review document; changes nothing.")
    ap.add_argument("--output", type=Path, help="write the proposal document here instead of stdout")
    args = ap.parse_args()
    rows = load_rows()
    routing = tomllib.loads(ROUTING.read_text())
    doc = render(rows, propose(rows, routing) if len(rows) >= MIN_ENTRIES else [])
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(doc)
        print(f"wrote {args.output}")
    else:
        print(doc, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
