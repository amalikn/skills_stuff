"""Integration with a repository's existing AI-context authority model.

If the target repo already has a ``context-map.yaml`` (as ansible-wifi does),
the scanner must:

1. Read the existing context map.
2. Detect its authority order, required-first-read and preferred bootstrap.
3. Register the generated artifacts as derived / non-authoritative.
4. Preserve higher-authority entries (``.archcore`` ADRs, governance packs).
5. Not create a competing first-read sequence.

This module only *reads* the existing map and computes an integration record
that is stored in the manifest. It never reorders or overwrites the existing
context authority; doing so requires an explicit user-approved migration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ruamel.yaml import YAML

DERIVED_ARTIFACTS = ("ANSIBLE_REPO_MAP.md", "manifest.yaml", "graph.yaml", "diagnostics.yaml")


@dataclass
class ContextIntegration:
    existing_context_map: str | None = None       # rel path if present
    authority_order_present: bool = False
    required_first_read: list[str] = field(default_factory=list)
    preferred_first_read: list[str] = field(default_factory=list)
    higher_authority_paths: list[str] = field(default_factory=list)
    registered_derived: list[str] = field(default_factory=list)
    conflict: bool = False
    conflict_reason: str | None = None
    output_inside_existing_context: bool = False

    def to_dict(self) -> dict:
        return {
            "existing_context_map": self.existing_context_map,
            "authority_order_present": self.authority_order_present,
            "required_first_read": self.required_first_read,
            "preferred_first_read": self.preferred_first_read,
            "higher_authority_paths": self.higher_authority_paths,
            "registered_derived_artifacts": self.registered_derived,
            "output_inside_existing_context": self.output_inside_existing_context,
            "authority_conflict": self.conflict,
            "authority_conflict_reason": self.conflict_reason,
            "policy": "generated artifacts are derived and non-authoritative; "
                      "existing .archcore and context-map authority outrank them",
        }


def integrate_context(repo: Path, output: Path) -> ContextIntegration:
    ci = ContextIntegration(registered_derived=list(DERIVED_ARTIFACTS))
    cmap = repo / "context-map.yaml"
    if not cmap.is_file():
        return ci

    ci.existing_context_map = "context-map.yaml"
    try:
        yaml = YAML(typ="safe", pure=True)
        data = yaml.load(cmap.read_text(encoding="utf-8")) or {}
    except Exception:  # noqa: BLE001 - never fail scan on a foreign map
        ci.conflict = True
        ci.conflict_reason = "existing context-map.yaml could not be parsed"
        return ci

    boot = data.get("bootstrap", {}) or {}
    ci.required_first_read = [str(x) for x in boot.get("required_first_read", [])]
    ci.preferred_first_read = [str(x) for x in boot.get("preferred_first_read", [])]

    authority = data.get("authority_order", [])
    if authority:
        ci.authority_order_present = True
        for entry in authority:
            p = entry.get("path") if isinstance(entry, dict) else str(entry)
            auth = entry.get("authority") if isinstance(entry, dict) else None
            if p and auth in ("highest", "high"):
                ci.higher_authority_paths.append(str(p))

    # Detect whether our output lands inside the governed .ai-context dir.
    try:
        rel_out = output.resolve().relative_to(repo.resolve())
        ci.output_inside_existing_context = str(rel_out).startswith(".ai-context")
    except ValueError:
        ci.output_inside_existing_context = False

    # Conflict only if a derived artifact name already appears as a required
    # first-read with authority — i.e. we'd be shadowing an authoritative file.
    for art in DERIVED_ARTIFACTS:
        if art in ci.required_first_read:
            ci.conflict = True
            ci.conflict_reason = (
                f"'{art}' already present in existing required_first_read; "
                "generated artifact must remain derived, not authoritative"
            )
            break
    return ci
