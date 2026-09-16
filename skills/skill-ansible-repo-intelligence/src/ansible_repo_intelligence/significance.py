"""Configuration-driven significance classification.

Rules live in ``config/significance_rules.yaml`` and are schema-validated
before use. Classification is deterministic: the highest-priority matching
rule wins; ties break by rule order then id. Every classified node records the
winning ``significance_rule_id`` for auditability.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

from .models import Significance


@dataclass
class SignificanceRule:
    id: str
    priority: int
    significance: Significance
    reason: str
    modules: list[str]
    module_res: list[re.Pattern]
    patterns: list[re.Pattern]


@dataclass
class SignificanceEngine:
    rules: list[SignificanceRule]
    default: Significance
    default_rule_id: str = "default"

    def classify(self, module: str, text: str = "") -> tuple[Significance, str]:
        """Return (significance, rule_id) for a module + optional arg text."""
        best: SignificanceRule | None = None
        for rule in self.rules:
            if self._matches(rule, module, text):
                if best is None or rule.priority > best.priority:
                    best = rule
        if best is None:
            return self.default, self.default_rule_id
        return best.significance, best.id

    @staticmethod
    def _matches(rule: SignificanceRule, module: str, text: str) -> bool:
        mod = module or ""
        if mod in rule.modules:
            return True
        for rx in rule.module_res:
            if rx.match(mod):
                return True
        if text:
            for rx in rule.patterns:
                if rx.search(text):
                    return True
        return False


def load_significance_engine(config_path: Path) -> SignificanceEngine:
    yaml = YAML(typ="safe", pure=True)
    data = yaml.load(config_path.read_text(encoding="utf-8")) or {}
    default = Significance(data.get("default_significance", "normal"))
    rules: list[SignificanceRule] = []
    for raw in data.get("rules", []):
        match = raw.get("match", {}) or {}
        modules_raw = [str(m) for m in match.get("modules", [])]
        exact = [m for m in modules_raw if not m.endswith(".*") and "*" not in m]
        globs = [m for m in modules_raw if m.endswith(".*") or "*" in m]
        module_res = [re.compile("^" + re.escape(g).replace(r"\*", ".*") + "$") for g in globs]
        patterns = [re.compile(p) for p in match.get("patterns", [])]
        rules.append(
            SignificanceRule(
                id=str(raw["id"]),
                priority=int(raw.get("priority", 0)),
                significance=Significance(raw["significance"]),
                reason=str(raw.get("reason", "")),
                modules=exact,
                module_res=module_res,
                patterns=patterns,
            )
        )
    # Stable order: priority desc, then id, so ties are deterministic.
    rules.sort(key=lambda r: (-r.priority, r.id))
    return SignificanceEngine(rules=rules, default=default)


def arg_text(attributes: dict[str, Any]) -> str:
    """Flatten task args to a searchable string for regex significance rules."""
    parts: list[str] = []
    for key in ("free_form", "cmd", "command", "dest", "path", "name", "src"):
        val = attributes.get(key)
        if isinstance(val, str):
            parts.append(val)
    raw = attributes.get("raw_args")
    if isinstance(raw, str):
        parts.append(raw)
    return "\n".join(parts)
