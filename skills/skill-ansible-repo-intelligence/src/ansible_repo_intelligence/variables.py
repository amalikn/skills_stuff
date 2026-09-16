"""Repository variable definitions, references and precedence analysis.

Collects variable *definitions* from every static source and assigns each a
precedence class (from ``config/variable_precedence_rules.yaml``). Detects
potential precedence conflicts per the documented overlap algorithm. Never
claims a winning runtime value unless all higher-precedence inputs are
statically known — which, in the presence of custom vars plugins / extra vars,
they generally are not.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

from .hashing import hash_bytes
from .models import SourceRef
from .yaml_loader import load_yaml_file


@dataclass
class PrecedenceClass:
    name: str
    rank: int


@dataclass
class PrecedenceConfig:
    classes: dict[str, PrecedenceClass]
    flag_cross_class: bool
    flag_same_class_overlap: bool
    ignore_disjoint_scopes: bool
    runtime_classes: set[str]


@dataclass
class VarDefinition:
    name: str
    precedence_class: str
    scope: str            # e.g. "role:dns", "flavor:rct:group:all", "play:..."
    source: SourceRef
    is_secret_name: bool = False


@dataclass
class VarConflict:
    name: str
    classes: list[str]
    scopes: list[str]
    sources: list[SourceRef]
    runtime_only: bool
    reason: str


@dataclass
class VariableIndex:
    definitions: list[VarDefinition] = field(default_factory=list)
    conflicts: list[VarConflict] = field(default_factory=list)

    def names(self) -> set[str]:
        return {d.name for d in self.definitions}


def load_precedence_config(path: Path) -> PrecedenceConfig:
    yaml = YAML(typ="safe", pure=True)
    data = yaml.load(path.read_text(encoding="utf-8")) or {}
    classes = {
        c["name"]: PrecedenceClass(c["name"], int(c["rank"]))
        for c in data.get("classes", [])
    }
    cp = data.get("conflict_policy", {}) or {}
    return PrecedenceConfig(
        classes=classes,
        flag_cross_class=bool(cp.get("flag_cross_class", True)),
        flag_same_class_overlap=bool(cp.get("flag_same_class_overlap", True)),
        ignore_disjoint_scopes=bool(cp.get("ignore_disjoint_scopes", True)),
        runtime_classes=set(cp.get("runtime_classes", [])),
    )


def is_secret_name(name: str, patterns: tuple[str, ...]) -> bool:
    low = name.lower()
    return any(p in low for p in patterns)


def collect_yaml_vars(
    abs_path: Path, rel_path: str, precedence_class: str, scope: str,
    secret_patterns: tuple[str, ...], max_bytes: int,
) -> list[VarDefinition]:
    """Collect top-level variable names defined in a YAML vars file."""
    loaded = load_yaml_file(abs_path, rel_path, max_bytes)
    if not loaded.ok or loaded.is_vault_file:
        return []
    out: list[VarDefinition] = []
    for doc in loaded.documents:
        if not isinstance(doc, dict):
            continue
        for key in doc:
            name = str(key)
            src = SourceRef(path=rel_path, document=0, content_hash=loaded.content_hash)
            out.append(VarDefinition(
                name=name, precedence_class=precedence_class, scope=scope, source=src,
                is_secret_name=is_secret_name(name, secret_patterns),
            ))
    return out


def add_definitions(index: VariableIndex, defs: list[VarDefinition]) -> None:
    index.definitions.extend(defs)


def compute_conflicts(index: VariableIndex, pcfg: PrecedenceConfig) -> None:
    """Populate index.conflicts using the documented overlap algorithm.

    Flags ARI006 when a variable is defined in >=2 distinct precedence classes
    that can apply to the same reachable path, or multiple times within one
    class for overlapping scope. Disjoint scopes are excluded.
    """
    by_name: dict[str, list[VarDefinition]] = {}
    for d in index.definitions:
        by_name.setdefault(d.name, []).append(d)

    for name, defs in sorted(by_name.items()):
        classes = sorted({d.precedence_class for d in defs})
        scopes = [d.scope for d in defs]

        cross_class = len(classes) >= 2
        same_class_overlap = False
        if not cross_class and len(defs) >= 2:
            # Same class, multiple definitions: overlap unless scopes disjoint.
            same_class_overlap = _scopes_overlap(scopes) if pcfg.ignore_disjoint_scopes else True

        if pcfg.flag_cross_class and cross_class:
            trigger = True
            reason = f"Defined in {len(classes)} precedence classes on potentially reachable paths"
        elif pcfg.flag_same_class_overlap and same_class_overlap:
            trigger = True
            reason = f"Defined {len(defs)} times within class '{classes[0]}' with overlapping scope"
        else:
            trigger = False
            reason = ""

        if not trigger:
            continue
        # Disjoint-scope suppression for cross-class too.
        if pcfg.ignore_disjoint_scopes and cross_class and not _scopes_overlap(scopes):
            continue

        runtime_only = all(c in pcfg.runtime_classes for c in classes)
        index.conflicts.append(VarConflict(
            name=name, classes=classes, scopes=sorted(set(scopes)),
            sources=[d.source for d in defs], runtime_only=runtime_only, reason=reason,
        ))


def _scopes_overlap(scopes: list[str]) -> bool:
    """Heuristic overlap test.

    Scopes are considered disjoint only when they are clearly partitioned by a
    differing flavor or role qualifier. When we cannot prove disjointness we
    conservatively treat them as overlapping (they may apply to the same path).
    """
    flavors = {_qualifier(s, "flavor") for s in scopes}
    roles = {_qualifier(s, "role") for s in scopes}
    # If every scope names a *different* flavor, they are disjoint.
    named_flavors = [f for f in flavors if f is not None]
    if len(named_flavors) == len(scopes) and len(set(named_flavors)) == len(scopes):
        return False
    # If every scope names a *different* role, they are disjoint.
    named_roles = [r for r in roles if r is not None]
    if len(named_roles) == len(scopes) and len(set(named_roles)) == len(scopes):
        return False
    return True


def _qualifier(scope: str, key: str) -> str | None:
    # scope format examples: "role:dns", "flavor:rct:group:all"
    tokens = scope.split(":")
    if key in tokens:
        i = tokens.index(key)
        if i + 1 < len(tokens):
            return tokens[i + 1]
    return None
