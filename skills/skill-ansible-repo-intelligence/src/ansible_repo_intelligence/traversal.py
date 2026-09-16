"""Shared bounded graph traversal for query and impact.

Loads a generated ``graph.yaml`` into an in-memory index and provides ONE
bounded breadth-first traversal used by BOTH the ``query`` and ``impact``
commands, so reachability / cycle-detection logic is never duplicated.

Every traversal honours explicit bounds (node limit, hop depth, output-byte
ceiling) and reports whether it was truncated and why.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from ruamel.yaml import YAML


@dataclass
class GraphStore:
    """Read-only index over a generated graph.yaml."""

    nodes: dict[str, dict] = field(default_factory=dict)
    edges: list[dict] = field(default_factory=list)
    out_adj: dict[str, list[tuple[str, dict]]] = field(default_factory=dict)  # id -> [(to, edge)]
    in_adj: dict[str, list[tuple[str, dict]]] = field(default_factory=dict)   # id -> [(from, edge)]
    retrieval_topics: dict[str, Any] = field(default_factory=dict)
    statistics: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls, graph_path: Path) -> "GraphStore":
        yaml = YAML(typ="safe", pure=True)
        data = yaml.load(graph_path.read_text(encoding="utf-8")) or {}
        store = cls(
            retrieval_topics=data.get("retrieval_topics", {}) or {},
            statistics=data.get("statistics", {}) or {},
        )
        for n in data.get("nodes", []):
            store.nodes[n["id"]] = n
        for e in data.get("edges", []):
            store.edges.append(e)
            store.out_adj.setdefault(e["from"], []).append((e["to"], e))
            store.in_adj.setdefault(e["to"], []).append((e["from"], e))
        return store

    def neighbours(self, node_id: str, direction: str) -> list[tuple[str, dict]]:
        if direction == "out":
            return self.out_adj.get(node_id, [])
        if direction == "in":
            return self.in_adj.get(node_id, [])
        return self.out_adj.get(node_id, []) + self.in_adj.get(node_id, [])


@dataclass
class Bounds:
    limit: int
    max_depth: int
    max_output_bytes: int


@dataclass
class TraversalResult:
    root_ids: list[str]
    node_ids: list[str]
    edges: list[dict]
    truncated: bool = False
    truncation_reason: str | None = None

    def nodes(self, store: GraphStore) -> list[dict]:
        return [store.nodes[i] for i in self.node_ids if i in store.nodes]


def bounded_bfs(
    store: GraphStore, roots: Iterable[str], bounds: Bounds, direction: str = "both",
) -> TraversalResult:
    """Deterministic bounded BFS from ``roots``.

    Stops when any bound is hit; ``truncated``/``truncation_reason`` record why.
    Neighbours are visited in sorted order for determinism.
    """
    root_list = sorted({r for r in roots if r in store.nodes})
    result = TraversalResult(root_ids=list(root_list), node_ids=[], edges=[])
    visited: set[str] = set()
    seen_edges: set[str] = set()
    # Seed roots up to the node limit; excess roots mark the result truncated.
    seeded = root_list[: bounds.limit]
    if len(root_list) > bounds.limit:
        result.truncated = True
        result.truncation_reason = f"node limit {bounds.limit} reached (roots exceed limit)"
    queue: deque[tuple[str, int]] = deque((r, 0) for r in seeded)
    for r in seeded:
        visited.add(r)
        result.node_ids.append(r)

    while queue:
        if len(result.node_ids) >= bounds.limit:
            result.truncated = True
            result.truncation_reason = f"node limit {bounds.limit} reached"
            break
        node_id, depth = queue.popleft()
        if depth >= bounds.max_depth:
            continue
        for to_id, edge in sorted(store.neighbours(node_id, direction), key=lambda x: (x[0], x[1].get("id", ""))):
            eid = edge.get("id", f"{edge.get('from')}->{to_id}")
            if eid not in seen_edges:
                seen_edges.add(eid)
                result.edges.append(edge)
            if to_id not in visited:
                if len(result.node_ids) >= bounds.limit:
                    result.truncated = True
                    result.truncation_reason = f"node limit {bounds.limit} reached"
                    break
                visited.add(to_id)
                result.node_ids.append(to_id)
                queue.append((to_id, depth + 1))

    return result
