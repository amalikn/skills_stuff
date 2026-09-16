"""Collection origin classification and vendored-collection policy.

Vendored third-party collection trees (e.g. ``collections/ansible_collections/
community/general``) can contain thousands of YAML files. They must NOT be
indexed as repository-authored first-class graph nodes by default. Instead we
record only collection metadata required for resolution and track FQCN usage
from repository-authored content.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# A repository-authored collection under ``<root>/ansible_collections/<ns>/<name>``
# is heuristically distinguished from vendored ones by the presence of a
# ``.info`` sibling or a ``MANIFEST.json``/``FILES.json`` galaxy-install marker,
# and by whether the tree lives under a configured collections path.

GALAXY_INSTALL_MARKERS = ("MANIFEST.json", "FILES.json")


class CollectionOrigin(str, Enum):
    REPO_AUTHORED = "repo_authored"
    VENDORED_THIRD_PARTY = "vendored_third_party"
    UNKNOWN_ORIGIN = "unknown_origin"


@dataclass
class CollectionInfo:
    namespace: str
    name: str
    fqcn_prefix: str  # "<namespace>.<name>"
    root: str  # repository-relative path to collection dir
    origin: CollectionOrigin
    version: str | None = None


def discover_collections(repo: Path, collections_paths: tuple[str, ...]) -> list[CollectionInfo]:
    """Find installed collections under the configured collections paths."""
    found: dict[str, CollectionInfo] = {}
    for cpath in collections_paths:
        base = (repo / cpath / "ansible_collections")
        if not base.is_dir():
            continue
        for ns_dir in sorted(base.iterdir()):
            if not ns_dir.is_dir() or ns_dir.name.endswith(".info"):
                continue
            for coll_dir in sorted(ns_dir.iterdir()):
                if not coll_dir.is_dir():
                    continue
                info = _classify_collection(repo, ns_dir.name, coll_dir)
                found[info.fqcn_prefix] = info
    return sorted(found.values(), key=lambda c: c.fqcn_prefix)


def _classify_collection(repo: Path, namespace: str, coll_dir: Path) -> CollectionInfo:
    name = coll_dir.name
    fqcn = f"{namespace}.{name}"
    rel = str(coll_dir.relative_to(repo))

    version = _read_galaxy_version(coll_dir)
    has_install_marker = any((coll_dir / m).is_file() for m in GALAXY_INSTALL_MARKERS)
    has_info_sibling = (coll_dir.parent / f"{fqcn}-*.info").parent.glob(f"{fqcn}-*.info")

    # Galaxy-installed collections carry MANIFEST.json/FILES.json → vendored.
    if has_install_marker or any(coll_dir.parent.glob(f"{fqcn}-*.info")):
        origin = CollectionOrigin.VENDORED_THIRD_PARTY
    elif version is not None and (coll_dir / "galaxy.yml").is_file() and not has_install_marker:
        # A source galaxy.yml with no install marker suggests repo-authored.
        origin = CollectionOrigin.REPO_AUTHORED
    else:
        origin = CollectionOrigin.UNKNOWN_ORIGIN
    _ = has_info_sibling
    return CollectionInfo(namespace, name, fqcn, rel, origin, version)


def _read_galaxy_version(coll_dir: Path) -> str | None:
    """Read version from MANIFEST.json or galaxy.yml without executing anything."""
    manifest = coll_dir / "MANIFEST.json"
    if manifest.is_file():
        import json

        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            return str(data.get("collection_info", {}).get("version")) or None
        except (ValueError, OSError):
            return None
    galaxy = coll_dir / "galaxy.yml"
    if galaxy.is_file():
        try:
            for line in galaxy.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("version:"):
                    return line.split(":", 1)[1].strip().strip("'\"")
        except OSError:
            return None
    return None


def vendored_roots(collections: list[CollectionInfo]) -> list[str]:
    """Repository-relative roots that must be excluded from first-class walking."""
    return [
        c.root for c in collections
        if c.origin is CollectionOrigin.VENDORED_THIRD_PARTY
    ]


def fqcn_prefixes(collections: list[CollectionInfo]) -> dict[str, CollectionInfo]:
    return {c.fqcn_prefix: c for c in collections}
