#!/usr/bin/env python3
"""Blind A/B comparison of two answer sets for the same eval cases: build a shuffled grading packet, then unblind and score it.

Usage:
  just blind-ab packet --cases a.json [b.json ...] --answers-a base.md --answers-b skill.md --out DIR [--seed N]
  just blind-ab score --grades DIR/grades.json --key DIR/key.json [--drop-criterion interfaces]
Standard library only. `packet` writes DIR/packet.md and DIR/key.json (the key stays with the coordinator, never the grader);
`score` reads the grader's per-criterion JSON and prints means, wins, acceptance counts and critical failures per side.
Answers files hold one `### <case id>` heading per answer; lines starting `Loaded:` are dropped so the grader cannot see which side
used the skill. Built from a skill-network-architect evaluation (2026-10-29), where a side review showed one criterion
(interfaces) rewarded knowledge the baseline could not have: `--drop-criterion` reports the comparison without it.
Exit 0: done, 2: invalid input.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path


def split_answers(path: Path) -> dict[str, str]:
    """Map case id to answer text from a `### <id>` file, dropping `Loaded:` lines.

    Args:
        path: Markdown file of answers.
    Returns:
        Dictionary of case id to answer body.
    """
    parts = re.split(r"^### +(\S+)\s*$", path.read_text(encoding="utf-8"), flags=re.M)
    return {parts[i].strip(): re.sub(r"^Loaded:.*$", "", parts[i + 1], flags=re.M).strip() for i in range(1, len(parts), 2)}


def build_packet(cases_files: list[Path], answers_a: Path, answers_b: Path, out: Path, seed: int) -> tuple[int, list[str]]:
    """Write a shuffled packet (X/Y per case) and its key.

    Args:
        cases_files: JSON files with a "cases" list of {id, prompt, expected, critical_failures}.
        answers_a: Answers for side A (e.g. baseline).
        answers_b: Answers for side B (e.g. with skill).
        out: Output directory.
        seed: Shuffle seed, recorded in the key.
    Returns:
        Pair of (cases written, case ids missing an answer on either side).
    """
    cases = [case for path in cases_files for case in json.loads(path.read_text(encoding="utf-8"))["cases"]]
    side_a, side_b = split_answers(answers_a), split_answers(answers_b)
    rng = random.Random(seed)
    key, doc = {"seed": seed, "cases": {}}, []
    for case in cases:
        pair = [("A", side_a.get(case["id"], "(missing)")), ("B", side_b.get(case["id"], "(missing)"))]
        rng.shuffle(pair)
        key["cases"][case["id"]] = {"X": pair[0][0], "Y": pair[1][0]}
        doc.append(f"## {case['id']}\n\n**Prompt:** {case['prompt']}\n\n**Expected:** " + "; ".join(case.get("expected", []))
                   + "\n\n**Critical failures:** " + "; ".join(case.get("critical_failures", []))
                   + f"\n\n#### Answer X\n\n{pair[0][1]}\n\n#### Answer Y\n\n{pair[1][1]}\n")
    out.mkdir(parents=True, exist_ok=True)
    (out / "packet.md").write_text("\n".join(doc), encoding="utf-8")
    (out / "key.json").write_text(json.dumps(key, indent=1) + "\n", encoding="utf-8")
    missing = [case["id"] for case in cases if case["id"] not in side_a or case["id"] not in side_b]
    return len(cases), missing


def normalised(criteria: dict[str, int | None], drop: set[str]) -> float:
    """Score out of 16 from 0/1/2 criteria, skipping not-applicable (None) and dropped ones.

    Args:
        criteria: Criterion name to score or None.
        drop: Criterion names to exclude.
    Returns:
        Normalised score on a 16-point scale (0 when nothing applies).
    """
    values = [value for name, value in criteria.items() if value is not None and name not in drop]
    return 16 * sum(values) / (2 * len(values)) if values else 0.0


def score(grades_path: Path, key_path: Path, drop: set[str], bar: float) -> dict:
    """Unblind graded answers and summarise each side.

    Args:
        grades_path: Grader output: list of {case, answer: X|Y, criteria: {...}, critical_failure}.
        key_path: Key written by build_packet.
        drop: Criteria to exclude from the score.
        bar: Acceptance threshold on the 16-point scale.
    Returns:
        Summary dictionary.
    Raises:
        ValueError: When a graded case or answer is not in the key.
    """
    key = json.loads(key_path.read_text(encoding="utf-8"))["cases"]
    by_case: dict[str, dict[str, dict]] = {}
    for row in json.loads(grades_path.read_text(encoding="utf-8")):
        if row["case"] not in key or row["answer"] not in key[row["case"]]:
            raise ValueError(f"grade for unknown case/answer: {row['case']}/{row['answer']}")
        by_case.setdefault(row["case"], {})[key[row["case"]][row["answer"]]] = row
    complete = {case: sides for case, sides in by_case.items() if {"A", "B"} <= set(sides)}
    summary: dict = {"cases": len(complete), "dropped_criteria": sorted(drop), "bar": bar}
    for side in ("A", "B"):
        scores = [normalised(complete[case][side]["criteria"], drop) for case in complete]
        summary[side] = {"mean": round(sum(scores) / len(scores), 2) if scores else None,
                         "at_or_above_bar": sum(1 for value in scores if value >= bar),
                         "critical_failures": sorted(case for case in complete if complete[case][side].get("critical_failure"))}
    wins = [normalised(complete[c]["B"]["criteria"], drop) - normalised(complete[c]["A"]["criteria"], drop) for c in complete]
    summary["b_wins"], summary["ties"], summary["a_wins"] = sum(d > 0 for d in wins), sum(d == 0 for d in wins), sum(d < 0 for d in wins)
    return summary


def main() -> int:
    """Run the packet or score subcommand.

    Args:
        None.
    Returns:
        Integer process exit code.
    """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    packet = sub.add_parser("packet")
    packet.add_argument("--cases", type=Path, nargs="+", required=True)
    packet.add_argument("--answers-a", type=Path, required=True)
    packet.add_argument("--answers-b", type=Path, required=True)
    packet.add_argument("--out", type=Path, required=True)
    packet.add_argument("--seed", type=int, default=20261029)
    scorer = sub.add_parser("score")
    scorer.add_argument("--grades", type=Path, required=True)
    scorer.add_argument("--key", type=Path, required=True)
    scorer.add_argument("--drop-criterion", action="append", default=[])
    scorer.add_argument("--bar", type=float, default=12.0)
    args = parser.parse_args()
    try:
        if args.command == "packet":
            count, missing = build_packet(args.cases, args.answers_a, args.answers_b, args.out, args.seed)
            print(json.dumps({"status": "written", "cases": count, "missing_answers": missing, "packet": str(args.out / "packet.md")}, indent=2))
        else:
            print(json.dumps(score(args.grades, args.key, set(args.drop_criterion), args.bar), indent=2))
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(json.dumps({"status": "invalid", "error": str(error)}))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
