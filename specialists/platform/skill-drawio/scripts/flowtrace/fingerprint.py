"""Fingerprint what a `path[:symbol]` code reference points at, so only a change in behaviour marks a flow step suspect. Stdlib only.

A reference with a symbol covers that block alone: a Python def or class (by ast), a shell function, a YAML key's block, else one `NAME=` or
`NAME:` line. Moving code within a file therefore changes nothing, which a line-range anchor cannot do. Before hashing, what cannot change
behaviour is dropped: Python is reduced to its syntax tree without docstrings, other files lose blank lines, full-line comments and trailing
space. A file that will not parse falls back to that text form, so it still has a fingerprint.

Imported, not run: `from flowtrace.fingerprint import fingerprint` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

import ast
import hashlib
import re
from pathlib import Path

#: The comment marker of files reduced as text, by suffix; other suffixes keep every non-blank line.
COMMENT = {".py": "#", ".sh": "#", ".bash": "#", ".yml": "#", ".yaml": "#", ".toml": "#", ".j2": "{#", ".js": "//", ".ts": "//", ".go": "//", ".rs": "//"}


def strip_text(text: str, suffix: str) -> str:
    """A file's text without blank lines, trailing space or full-line comments.

    Args:
        text: the text.
        suffix: the file's suffix, for its comment marker.

    Returns:
        The reduced text.
    """
    mark = COMMENT.get(suffix)
    lines = [ln.rstrip() for ln in text.splitlines()]
    return "\n".join(ln for ln in lines if ln.strip() and not (mark and ln.lstrip().startswith(mark)))


def _no_docstrings(tree: ast.AST) -> ast.AST:
    """Remove docstrings from a syntax tree.

    Args:
        tree: the tree (changed in place).

    Returns:
        The tree.
    """
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and ast.get_docstring(node, clean=False) is not None:
            node.body = node.body[1:] or [ast.Pass()]
    return tree


def python_block(tree: ast.Module, symbol: str) -> ast.AST | None:
    """The def or class a dotted name points at.

    Args:
        tree: the module's tree.
        symbol: `name` or `Class.method`.

    Returns:
        The node, or None.
    """
    scope: ast.AST = tree
    for part in symbol.split("."):
        found = [n for n in getattr(scope, "body", []) if isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == part]
        if not found:
            return None
        scope = found[0]
    return scope


def shell_block(text: str, name: str) -> str | None:
    """A shell function's text, its braces counted.

    Args:
        text: the file's text.
        name: the function's name.

    Returns:
        The function, or None.
    """
    m = re.search(rf"(?m)^\s*(?:function\s+)?{re.escape(name)}\s*(?:\(\))?\s*\{{", text)
    if not m:
        return None
    depth = 0
    for i in range(m.end() - 1, len(text)):
        depth += (text[i] == "{") - (text[i] == "}")
        if depth == 0:
            return text[m.start():i + 1]
    return text[m.start():]


def _in_block(line: str, indent: int, is_item: bool) -> bool:
    """Whether a line still belongs to the YAML block that opened at `indent`.

    Args:
        line: the line.
        indent: the opening line's indent.
        is_item: the block opened on a list item, so a sibling `- ` ends it; under a plain key, `- ` at the same indent is its value.

    Returns:
        True when the block goes on.
    """
    depth = len(line) - len(line.lstrip())
    return not line.strip() or depth > indent or (depth == indent and line.lstrip().startswith("- ") and not is_item)


def yaml_block(text: str, key: str) -> str | None:
    """A YAML key's line and everything under it, or the line alone for `NAME=value`.

    Args:
        text: the file's text.
        key: the key's last dotted part.

    Returns:
        The block, or None.
    """
    lines = text.splitlines()
    for k, line in enumerate(lines):
        m = re.match(rf"^(\s*)(- )?\[?{re.escape(key)}\b[^\n]*?[:=]", line)
        if m:
            end = k + 1
            while end < len(lines) and _in_block(lines[end], len(m.group(1)), bool(m.group(2))):
                end += 1
            return "\n".join(lines[k:end])
    return None


def block_text(text: str, symbol: str, suffix: str) -> str | None:
    """The reduced text of a whole file, or of one symbol in it.

    Args:
        text: the file's text.
        symbol: the symbol, "" for the whole file.
        suffix: the file's suffix.

    Returns:
        The text hashed, or None when the symbol is not there.
    """
    last = symbol.rsplit(".", 1)[-1]
    if suffix == ".py":
        try:
            tree = ast.parse(text)
        except SyntaxError:
            tree = None
        if tree is not None:
            node = python_block(tree, symbol) if symbol else tree
            if node is not None:
                return ast.dump(_no_docstrings(node), annotate_fields=False)
            if not symbol:
                return strip_text(text, suffix)
    if not symbol:
        return strip_text(text, suffix)
    block = (shell_block(text, last) if suffix in (".sh", ".bash", "") else None) or yaml_block(text, last)
    return None if block is None else strip_text(block, suffix)


def source_text(text: str, symbol: str, suffix: str) -> str:
    """What a reviewer reads of a reference: the source itself, not the reduced form hashed.

    Args:
        text: the file's text.
        symbol: the symbol, "" for the whole file.
        suffix: the file's suffix.

    Returns:
        The block's source, or the whole file when it cannot be cut out.
    """
    if not symbol:
        return text
    if suffix == ".py":
        try:
            node = python_block(ast.parse(text), symbol)
        except SyntaxError:
            node = None
        if node is not None:
            return ast.get_source_segment(text, node) or text
    last = symbol.rsplit(".", 1)[-1]
    return shell_block(text, last) or yaml_block(text, last) or text


def fingerprint(root: Path, ref: str, cache: dict | None = None) -> tuple[str | None, str]:
    """A reference's fingerprint.

    Args:
        root: the project root.
        ref: `path` or `path:symbol`.
        cache: optional {path: text}, so a file named by many steps is read once.

    Returns:
        (first 16 hex digits of the SHA-256, source text); (None, "") when the file or symbol is gone.
    """
    cache = {} if cache is None else cache
    path, _, symbol = ref.partition(":")
    if path not in cache:
        p = root / path
        cache[path] = p.read_text(encoding="utf-8", errors="replace") if p.is_file() else None
    text = cache[path]
    if text is None:
        return None, ""
    suffix = Path(path).suffix
    reduced = block_text(text, symbol, suffix)
    if reduced is None:
        return None, ""
    return hashlib.sha256(reduced.encode()).hexdigest()[:16], source_text(text, symbol, suffix)
