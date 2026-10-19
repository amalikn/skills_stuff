#!/usr/bin/env python3
"""Check `path[:symbol]` code references in a data map against the repository, so a rename breaks a check instead of the map going stale.

Promoted from unified-network-controller `scripts/render/flows_drawio.py` (2026-10-19). A reference is a repository-relative file, optionally
followed by `:symbol`; the symbol may be dotted (`Class.method`), and its last part must be defined in the file as a Python def or class, a
shell function, or a line that starts with the name followed by `=` or `:` (a constant, a YAML key, a just recipe). The match is textual and
deliberately loose: it proves the name still exists in that file, not that it means what the map says.

Imported, not run: `from code_refs import CodeRefs`.
"""

from __future__ import annotations

import re
from pathlib import Path


def symbol_defined(text: str, symbol: str) -> bool:
    """Whether a file defines a symbol.

    Args:
        text: the file's text.
        symbol: a name, or a dotted `Class.method`; the last part is looked for.

    Returns:
        True for a Python def or class, a shell function, or a line starting with the name followed by `=` or `:` (a constant, YAML key or
        just recipe).
    """
    name = re.escape(symbol.rsplit(".", 1)[-1])
    pattern = rf"(?m)(\b(?:async\s+def|def|class)\s+{name}\b|^\s*(?:function\s+)?{name}\s*\(\)|^\s*\[?{name}\b[^\n]*?[:=])"
    return re.search(pattern, text) is not None


class CodeRefs:
    """Checks code references under one root, reading each file once."""

    def __init__(self, root: Path) -> None:
        """Start with an empty file cache.

        Args:
            root: the repository root the references are relative to.
        """
        self.root = root
        self.cache: dict[str, str | None] = {}

    def problem(self, ref: str, where: str) -> str | None:
        """Check one reference.

        Args:
            ref: the reference as written in the map (`path` or `path:symbol`).
            where: its location, for the message.

        Returns:
            A message when the file is missing or does not define the symbol, else None.
        """
        path, _, symbol = ref.partition(":")
        if path not in self.cache:
            p = self.root / path
            self.cache[path] = p.read_text(encoding="utf-8", errors="replace") if p.is_file() else None
        if self.cache[path] is None:
            return f"{where}: code path `{path}` does not exist"
        if symbol and not symbol_defined(self.cache[path], symbol):
            return f"{where}: `{symbol}` is not defined in {path}"
        return None
