"""Shared readers for this project's checks: file and table reads, path resolution, catalog parsing, docstring counting."""

from __future__ import annotations

import csv
import re
from pathlib import Path

from .config import (
    CAPABILITY_ROW,
    ROOT,
)

def read(rel: str) -> str | None:
    """The text of a repo file.

    Args:
        rel: repo-relative path.

    Returns:
        Its text, or None when the file does not exist.
    """
    path = ROOT / rel
    return path.read_text(encoding="utf-8") if path.is_file() else None


def without_code(text: str) -> str:
    """Strip fenced code blocks. Their contents are examples, not claims about this repo.

    Args:
        text: markdown.

    Returns:
        The text without its fenced code blocks.
    """
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


def table_rows(rel: str) -> list[dict[str, str]]:
    """Read a CSV as dicts, or an empty list when it does not exist — an absent table contributes zero assertions.

    Args:
        rel: repo-relative CSV path.

    Returns:
        One dict per row, keyed by the header; empty when the file does not exist.
    """
    path = ROOT / rel
    if not path.is_file():
        return []
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def members(folder: str, glob: str) -> list[Path]:
    """Files directly matching a glob under a folder, hidden files excluded.

    Args:
        folder: repo-relative folder.
        glob: pattern inside it.

    Returns:
        Sorted paths; empty when the folder does not exist.
    """
    base = ROOT / folder
    if not base.is_dir():
        return []
    return sorted(p for p in base.glob(glob) if p.is_file() and not p.name.startswith("."))


def manifest_capabilities() -> list[dict[str, str]]:
    text = read("manifest.yaml")
    if text is None:
        return []
    return [m.groupdict() for m in CAPABILITY_ROW.finditer(text)]
