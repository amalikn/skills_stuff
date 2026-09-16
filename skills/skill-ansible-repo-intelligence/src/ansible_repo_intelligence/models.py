"""Canonical data models for the repository graph and diagnostics.

These dataclasses are the in-memory representation. Serialization to the
lean YAML artifacts is handled in ``graph.py`` / ``renderer.py``. All models
serialize deterministically: field order is fixed, and any collection that is
emitted is sorted by a stable key before writing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ResolutionStatus(str, Enum):
    RESOLVED = "resolved"
    PARTIALLY_RESOLVED = "partially_resolved"
    UNRESOLVED = "unresolved"
    DYNAMIC = "dynamic"


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Significance(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    FATAL = "fatal"


# Ordering weights for deterministic sorting / "most severe first" reporting.
SEVERITY_ORDER = {
    Severity.FATAL: 0,
    Severity.ERROR: 1,
    Severity.WARNING: 2,
    Severity.INFO: 3,
}
SIGNIFICANCE_ORDER = {
    Significance.CRITICAL: 0,
    Significance.HIGH: 1,
    Significance.NORMAL: 2,
    Significance.LOW: 3,
}


@dataclass(frozen=True)
class SourceRef:
    """Provenance for a source-derived node or edge.

    ``path`` is always repository-relative and mandatory. ``content_hash`` is a
    normalization-invariant sha256 (see ``hashing.py``) and mandatory for
    source-derived nodes. Line numbers may be ``None`` when unavailable.
    """

    path: str
    document: int | None = None
    line_start: int | None = None
    line_end: int | None = None
    content_hash: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "document": self.document,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "content_hash": self.content_hash,
        }


@dataclass(frozen=True)
class Resolution:
    status: ResolutionStatus
    confidence: Confidence
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "confidence": self.confidence.value,
            "reason": self.reason,
        }


@dataclass
class Node:
    id: str
    kind: str
    name: str
    significance: Significance
    resolution: Resolution
    source: SourceRef | None = None
    significance_rule_id: str | None = None
    attributes: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "id": self.id,
            "kind": self.kind,
            "name": self.name,
            "significance": self.significance.value,
        }
        if self.significance_rule_id is not None:
            d["significance_rule_id"] = self.significance_rule_id
        d["source"] = self.source.to_dict() if self.source else None
        d["resolution"] = self.resolution.to_dict()
        d["attributes"] = _sorted_attributes(self.attributes)
        return d


@dataclass
class Edge:
    id: str
    type: str
    from_id: str
    to_id: str
    resolution: Resolution
    source: SourceRef | None = None
    attributes: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "from": self.from_id,
            "to": self.to_id,
            "source": self.source.to_dict() if self.source else None,
            "resolution": self.resolution.to_dict(),
            "attributes": _sorted_attributes(self.attributes),
        }


@dataclass
class Diagnostic:
    code: str
    severity: Severity
    message: str
    path: str | None = None
    node_id: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "severity": self.severity.value,
            "message": self.message,
            "path": self.path,
            "node_id": self.node_id,
            "details": _sorted_attributes(self.details),
        }

    def sort_key(self) -> tuple:
        return (
            SEVERITY_ORDER[self.severity],
            self.code,
            self.path or "",
            self.node_id or "",
            self.message,
        )


def _sorted_attributes(attrs: dict[str, Any]) -> dict[str, Any]:
    """Return attributes with keys sorted for deterministic serialization."""
    if not attrs:
        return {}
    out: dict[str, Any] = {}
    for k in sorted(attrs.keys()):
        v = attrs[k]
        out[k] = sorted(v) if isinstance(v, set) else v
    return out
