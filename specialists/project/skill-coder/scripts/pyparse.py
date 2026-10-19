#!/usr/bin/env python3
"""Parse Python source the way every helper in this pack does: at the target project's grammar, with the parser's own warnings silenced.
Imported, not run; reads nothing. Stdlib only.

Why: the helpers parse other projects' code as data. `ast.parse` prints a SyntaxWarning for things like an invalid escape sequence in a
non-raw string; those are the project's linter's business, and printed here they bury the helper's own findings (first seen on a 1,125-file
Ansible repository, 2026-10-19). A file that does not parse at all still raises, so the caller reports it.
"""

from __future__ import annotations

import ast
import warnings

#: The oldest Python this script runs on: it runs with the target project's own interpreter (the pack's contract test parses it at this grammar).
REQUIRES_PYTHON = (3, 11)


def parse(text: str, grammar: tuple[int, int] | None = None) -> ast.Module:
    """Parse source quietly.

    Args:
        text: the source.
        grammar: (major, minor) for ast's feature_version (the project's Python), or None for this interpreter's grammar.

    Returns:
        The module's AST.

    Raises:
        SyntaxError: when the source does not parse at that grammar.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        return ast.parse(text, feature_version=grammar)
