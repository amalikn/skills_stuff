"""Diagnostic codes and collector.

Severity: info | warning | error | fatal. Strict mode fails on error/fatal.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import Diagnostic, Severity

# Machine-readable diagnostic codes (stable identifiers).
ARI001_UNRESOLVED_STATIC_INCLUDE = "ARI001_UNRESOLVED_STATIC_INCLUDE"
ARI002_DYNAMIC_INCLUDE = "ARI002_DYNAMIC_INCLUDE"
ARI003_UNRESOLVED_HANDLER = "ARI003_UNRESOLVED_HANDLER"
ARI004_DUPLICATE_HANDLER_NAME = "ARI004_DUPLICATE_HANDLER_NAME"
ARI005_VARIABLE_WITHOUT_DEFINITION = "ARI005_VARIABLE_WITHOUT_DEFINITION"
ARI006_POSSIBLE_VARIABLE_PRECEDENCE_CONFLICT = "ARI006_POSSIBLE_VARIABLE_PRECEDENCE_CONFLICT"
ARI007_EXTERNAL_SYMLINK_BLOCKED = "ARI007_EXTERNAL_SYMLINK_BLOCKED"
ARI008_UNSUPPORTED_YAML_CONSTRUCT = "ARI008_UNSUPPORTED_YAML_CONSTRUCT"
ARI009_SCHEMA_VALIDATION_FAILED = "ARI009_SCHEMA_VALIDATION_FAILED"
ARI010_SECRET_VALUE_REDACTED = "ARI010_SECRET_VALUE_REDACTED"
ARI011_REPOSITORY_MAP_LIMIT_EXCEEDED = "ARI011_REPOSITORY_MAP_LIMIT_EXCEEDED"
ARI012_QUERY_LIMIT_EXCEEDED = "ARI012_QUERY_LIMIT_EXCEEDED"
ARI013_GRAPH_REFERENCE_INVALID = "ARI013_GRAPH_REFERENCE_INVALID"
ARI014_DUPLICATE_PERSISTENT_INDEX = "ARI014_DUPLICATE_PERSISTENT_INDEX"
ARI015_VENDORED_COLLECTION_EXCLUDED = "ARI015_VENDORED_COLLECTION_EXCLUDED"
ARI016_COLLECTION_ORIGIN_UNKNOWN = "ARI016_COLLECTION_ORIGIN_UNKNOWN"
ARI017_CUSTOM_VARS_PLUGIN_DYNAMIC = "ARI017_CUSTOM_VARS_PLUGIN_DYNAMIC"
ARI018_ANSIBLE_CONFIG_UNRESOLVED_PATH = "ARI018_ANSIBLE_CONFIG_UNRESOLVED_PATH"
ARI019_INVENTORY_FLAVOR_COLLISION = "ARI019_INVENTORY_FLAVOR_COLLISION"
ARI020_CONTEXT_AUTHORITY_CONFLICT = "ARI020_CONTEXT_AUTHORITY_CONFLICT"
ARI021_MAP_SECTION_TRUNCATED = "ARI021_MAP_SECTION_TRUNCATED"
ARI022_INVENTORY_BACKUP_EXCLUDED = "ARI022_INVENTORY_BACKUP_EXCLUDED"
ARI023_YAML_PARSE_ERROR = "ARI023_YAML_PARSE_ERROR"
ARI024_GENERATED_CACHE_EXCLUDED = "ARI024_GENERATED_CACHE_EXCLUDED"
ARI025_JINJA_PARSE_ERROR = "ARI025_JINJA_PARSE_ERROR"


@dataclass
class Diagnostics:
    items: list[Diagnostic] = field(default_factory=list)

    def add(self, code: str, severity: Severity, message: str,
            path: str | None = None, node_id: str | None = None, **details) -> None:
        self.items.append(Diagnostic(
            code=code, severity=severity, message=message,
            path=path, node_id=node_id, details=details,
        ))

    def info(self, code, message, **kw) -> None:
        self.add(code, Severity.INFO, message, **kw)

    def warning(self, code, message, **kw) -> None:
        self.add(code, Severity.WARNING, message, **kw)

    def error(self, code, message, **kw) -> None:
        self.add(code, Severity.ERROR, message, **kw)

    def fatal(self, code, message, **kw) -> None:
        self.add(code, Severity.FATAL, message, **kw)

    def counts(self) -> dict[str, int]:
        c = {s.value: 0 for s in Severity}
        for d in self.items:
            c[d.severity.value] += 1
        return c

    def has_blocking(self) -> bool:
        return any(d.severity in (Severity.ERROR, Severity.FATAL) for d in self.items)

    def has_warnings(self) -> bool:
        return any(d.severity is Severity.WARNING for d in self.items)

    def sorted_items(self) -> list[Diagnostic]:
        return sorted(self.items, key=lambda d: d.sort_key())
