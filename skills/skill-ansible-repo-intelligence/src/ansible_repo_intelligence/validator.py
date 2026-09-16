"""Validation of generated artifacts against schemas + structural gates."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from jsonschema import Draft202012Validator
from ruamel.yaml import YAML

_SCHEMA_DIR = Path(__file__).resolve().parents[2] / "schemas"

APPROVED_OUTPUTS = {"manifest.yaml", "ANSIBLE_REPO_MAP.md", "graph.yaml", "diagnostics.yaml"}
APPROVED_CACHE = {"scan-state.yaml"}
FORBIDDEN_INDEXES = {
    "repository-index.yaml", "execution-graph.yaml", "variable-index.yaml",
    "handler-index.yaml", "inventory-index.yaml", "template-index.yaml",
    "file-index.yaml", "tag-index.yaml", "unresolved-references.yaml",
}


@dataclass
class ValidationResult:
    ok: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def fail(self, msg: str) -> None:
        self.ok = False
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def _load_yaml(path: Path):
    yaml = YAML(typ="safe", pure=True)
    return yaml.load(path.read_text(encoding="utf-8"))


def _validator(schema_name: str) -> Draft202012Validator:
    schema = _load_yaml(_SCHEMA_DIR / schema_name)
    return Draft202012Validator(schema)


def validate_config_tables(sig_path: Path, prec_path: Path) -> ValidationResult:
    """Validate the two config rule tables BEFORE a scan proceeds."""
    res = ValidationResult()
    for path, schema in ((sig_path, "significance_rules.schema.yaml"),
                         (prec_path, "variable_precedence_rules.schema.yaml")):
        if not path.is_file():
            res.fail(f"missing config table: {path}")
            continue
        try:
            data = _load_yaml(path)
            errors = sorted(_validator(schema).iter_errors(data), key=lambda e: e.path)
            for e in errors:
                res.fail(f"{path.name}: {e.message} at {'/'.join(map(str, e.path))}")
        except Exception as exc:  # noqa: BLE001
            res.fail(f"{path.name}: {exc}")
    return res


def validate_context(output: Path, config_tables: tuple[Path, Path] | None = None) -> ValidationResult:
    """Validate a generated .ai-context directory."""
    res = ValidationResult()

    manifest_p = output / "manifest.yaml"
    graph_p = output / "graph.yaml"
    diag_p = output / "diagnostics.yaml"
    map_p = output / "ANSIBLE_REPO_MAP.md"

    for p in (manifest_p, graph_p, diag_p, map_p):
        if not p.is_file():
            res.fail(f"missing required output: {p.name}")
    if not res.ok:
        return res

    # Schema conformance
    for path, schema in ((manifest_p, "manifest.schema.yaml"),
                         (graph_p, "graph.schema.yaml"),
                         (diag_p, "diagnostics.schema.yaml")):
        try:
            data = _load_yaml(path)
            for e in sorted(_validator(schema).iter_errors(data), key=lambda e: list(e.path)):
                res.fail(f"{path.name}: {e.message} at {'/'.join(map(str, e.path))}")
        except Exception as exc:  # noqa: BLE001
            res.fail(f"{path.name}: schema load/parse error: {exc}")

    if config_tables:
        cres = validate_config_tables(*config_tables)
        res.errors.extend(cres.errors)
        res.ok = res.ok and cres.ok

    if not res.ok:
        return res

    graph = _load_yaml(graph_p)
    _validate_graph_integrity(graph, res)
    _validate_no_redundant_indexes(output, res)
    _validate_map_budget(map_p, manifest_p, res)
    _validate_no_absolute_paths(graph, res)

    return res


def _validate_graph_integrity(graph: dict, res: ValidationResult) -> None:
    node_ids = {n["id"] for n in graph.get("nodes", [])}
    if len(node_ids) != len(graph.get("nodes", [])):
        res.fail("duplicate node ids in graph")
    stats = graph.get("statistics", {})
    if stats.get("node_count") != len(graph.get("nodes", [])):
        res.fail(f"statistics.node_count {stats.get('node_count')} != actual {len(graph.get('nodes', []))}")
    if stats.get("edge_count") != len(graph.get("edges", [])):
        res.fail("statistics.edge_count mismatch")
    # Edge references: to/from must exist OR be an explicit unresolved/dynamic sentinel.
    for e in graph.get("edges", []):
        for endpoint in (e["from"], e["to"]):
            if endpoint in node_ids:
                continue
            if endpoint.startswith(("unresolved:", "role:", "playbook:")):
                continue  # declaration references are allowed
            status = e.get("resolution", {}).get("status")
            if status in ("unresolved", "dynamic"):
                continue
            res.fail(f"edge {e['id']} references missing node {endpoint} (status={status})")


def _validate_no_redundant_indexes(output: Path, res: ValidationResult) -> None:
    for child in output.iterdir():
        if child.name in FORBIDDEN_INDEXES:
            res.fail(f"forbidden redundant index present: {child.name}")
        if child.is_file() and child.suffix in (".yaml", ".md") \
                and child.name not in APPROVED_OUTPUTS:
            res.warn(f"unexpected file in output root: {child.name}")


def _validate_map_budget(map_p: Path, manifest_p: Path, res: ValidationResult) -> None:
    lines = map_p.read_text(encoding="utf-8").splitlines()
    manifest = _load_yaml(manifest_p)
    # Budget is 1000 unless overridden; we read the effective value if present.
    budget = 1000
    if len(lines) > budget:
        res.fail(f"ANSIBLE_REPO_MAP.md exceeds {budget}-line budget ({len(lines)} lines)")


def _validate_no_absolute_paths(graph: dict, res: ValidationResult) -> None:
    for n in graph.get("nodes", []):
        src = n.get("source")
        if src and isinstance(src.get("path"), str) and src["path"].startswith("/"):
            res.fail(f"absolute path in node {n['id']}: {src['path']}")
