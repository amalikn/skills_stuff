#!/usr/bin/env python3
"""Static Agent Stack contract validator. Uses only Python stdlib."""
from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_PERSONA_SECTIONS = {
    "## Mandate",
    "## Use When",
    "## Do Not Use As Primary Owner",
    "## Decision Lens",
    "## Operating Method",
    "## Boundaries",
    "## Output Contract",
}
ORCHESTRATOR_REQUIRED = {
    "## Mandate",
    "## Routing Principles",
    "## Persona Selection Heuristics",
    "## Skill Selection Heuristics",
    "## Disagreement Protocol",
    "## Output Contract",
}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def manifest_entries() -> dict[str, tuple[str, str]]:
    text = (ROOT / "manifest.yaml").read_text()
    out: dict[str, tuple[str, str]] = {}
    pat = re.compile(r"- \{id: ([^,]+), kind: ([^,]+), path: ([^,}]+)")
    for cap_id, kind, path in pat.findall(text):
        out[cap_id.strip()] = (kind.strip(), path.strip())
    return out


def main() -> int:
    errors: list[str] = []
    manifest = manifest_entries()
    if not manifest:
        fail(errors, "manifest.yaml: no capabilities parsed")

    for cap_id, (_, rel) in manifest.items():
        if not (ROOT / rel).exists():
            fail(errors, f"manifest capability {cap_id!r} points to missing {rel}")

    routing = tomllib.loads((ROOT / "routing.toml").read_text())
    routed_personas = {x["id"] for x in routing.get("personas", [])}
    routed_skills = {x["id"] for x in routing.get("skills", [])}
    manifest_personas = {k for k, (kind, _) in manifest.items() if kind == "persona"}
    manifest_skills = set(manifest) - manifest_personas

    for missing in sorted(manifest_personas - routed_personas):
        fail(errors, f"routing.toml missing persona: {missing}")
    for extra in sorted(routed_personas - manifest_personas):
        fail(errors, f"routing.toml unknown persona: {extra}")
    for missing in sorted(manifest_skills - routed_skills):
        fail(errors, f"routing.toml missing skill: {missing}")
    for extra in sorted(routed_skills - manifest_skills):
        fail(errors, f"routing.toml unknown skill: {extra}")

    for rec in routing.get("skills", []):
        if not rec.get("intents"):
            fail(errors, f"routing skill {rec['id']} has no intents")
        if rec.get("execution") not in {"analysis", "tool"}:
            fail(errors, f"routing skill {rec['id']} has invalid execution class")
        for persona in rec.get("personas", []):
            if persona not in manifest_personas:
                fail(errors, f"routing skill {rec['id']} references unknown persona {persona}")

    for p in sorted((ROOT / "personas").glob("*.md")):
        text = p.read_text()
        required = ORCHESTRATOR_REQUIRED if p.name == "orchestrator-follett.md" else REQUIRED_PERSONA_SECTIONS
        for section in required:
            if section not in text:
                fail(errors, f"{p.relative_to(ROOT)} missing {section}")
        if len(text.splitlines()) < 60:
            fail(errors, f"{p.relative_to(ROOT)} is too thin (<60 lines)")

    for p in sorted((ROOT / "skills").glob("*/SKILL.md")):
        text = p.read_text()
        if not text.startswith("---\n"):
            fail(errors, f"{p.relative_to(ROOT)} missing YAML frontmatter")
        if "name:" not in text[:1500] or "description:" not in text[:2500]:
            fail(errors, f"{p.relative_to(ROOT)} missing name/description metadata")

    # Validate only concrete local resource links outside fenced code. URLs and example placeholders are ignored.
    concrete_skills = {"startup-business-models", "deep-research"}
    for skill in concrete_skills:
        p = ROOT / "skills" / skill / "SKILL.md"
        text = re.sub(r"```.*?```", "", p.read_text(), flags=re.S)
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            bare = target.split("#", 1)[0]
            if bare and not (p.parent / bare).resolve().exists():
                fail(errors, f"{p.relative_to(ROOT)} broken local link: {target}")

    if errors:
        print("Agent Stack validation: FAIL")
        for e in errors:
            print(f"- {e}")
        return 1
    print(f"Agent Stack validation: PASS ({len(manifest)} capabilities; {len(routed_personas)} personas; {len(routed_skills)} skills)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
