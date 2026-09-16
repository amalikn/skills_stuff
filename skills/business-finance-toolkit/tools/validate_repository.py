"""Structural validation with no network or provider dependency."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ["README.md", "AGENTS.md", "pyproject.toml", "LICENSE", "docs/roadmap.md", "third_party/conceptual-provenance.md"]


def main() -> int:
    issues: list[str] = []
    for relative_path in REQUIRED:
        if not (ROOT / relative_path).is_file():
            issues.append(f"missing required file: {relative_path}")
    for manifest in sorted((ROOT / "skills").glob("*/manifest.yaml")):
        try:
            data = yaml.safe_load(manifest.read_text())
            for key in ("id", "name", "lifecycle", "inputs", "outputs", "human_approval"):
                if not data.get(key):
                    issues.append(f"{manifest.relative_to(ROOT)} missing {key}")
            if not manifest.with_name("SKILL.md").is_file():
                issues.append(f"{manifest.parent.relative_to(ROOT)} missing SKILL.md")
        except yaml.YAMLError as error:
            issues.append(f"invalid YAML {manifest.relative_to(ROOT)}: {error}")
    for schema in sorted((ROOT / "schemas").glob("*.json")):
        try:
            json.loads(schema.read_text())
        except json.JSONDecodeError as error:
            issues.append(f"invalid JSON {schema.relative_to(ROOT)}: {error}")
    if issues:
        print("Repository validation failed:")
        print("\n".join(f"- {issue}" for issue in issues))
        return 1
    print(f"Repository validation passed: {len(list((ROOT / 'skills').glob('*/manifest.yaml')))} skill manifests, {len(list((ROOT / 'schemas').glob('*.json')))} JSON schemas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
