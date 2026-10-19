#!/usr/bin/env python3
"""Add values to flow-style lists inside the items of a YAML map, editing the text so comments, order and inline style survive. Plan by default.

Why: a data-first diagram's map (references/data-first-diagrams.md) is hand-kept YAML with comments; loading and dumping it with PyYAML would
drop every comment and reflow every line. Generalised from the unified-network-controller one-off that added reviewed dependencies to its flow
map (2026-10-19). Supported shapes, which is what such maps use:

    - id: collector                       # an item of a top-level list, found by its key field
      depends_on: [nautobot-web, smc]     # FIELD: a flow-style list on one line
      dependencies: {components: [a, b]}  # PARENT.CHILD: a list inside a one-line flow mapping

A value already present is not added again; a missing field is inserted after the line named by --after (default: the item's key line).
Without --apply the script prints the plan (a unified diff) and changes nothing; with --apply it writes the file. When PyYAML is installed the
result is parsed before writing, so a patch never leaves invalid YAML.

Usage:
    yaml_list_patch.py FILE --list components --field depends_on --spec adds.json [--key id] [--after health] [--apply]
    (adds.json: {"<item id>": ["value", ...], ...})
Exit: 0 on success (plan printed or file written), 1 when an item is not found or the result does not parse, 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path

#: The oldest Python this script runs on (stdlib only; PyYAML optional, for the parse check).
REQUIRES_PYTHON = (3, 11)


def item_span(text: str, list_key: str, key: str, item_id: str) -> tuple[int, int, str]:
    """Where one item of a top-level list sits in the text.

    Args:
        text: the YAML text.
        list_key: the top-level list (for example "components").
        key: the field that names an item (for example "id").
        item_id: the item's value of that field.

    Returns:
        (start offset, end offset, the indentation of the item's fields).

    Raises:
        KeyError: the list or the item is not found.
    """
    head = re.search(rf"(?m)^{re.escape(list_key)}:\s*(#.*)?$", text)
    if head is None:
        raise KeyError(f"top-level list `{list_key}` not found")
    body_end = m.start() if (m := re.compile(r"(?m)^\S").search(text, head.end() + 1)) else len(text)
    item = re.compile(rf"(?m)^(\s*)- {re.escape(key)}: ['\"]?{re.escape(item_id)}['\"]?\s*(#.*)?$").search(text, head.end(), body_end)
    if item is None:
        raise KeyError(f"{list_key}: no item with {key}: {item_id}")
    dash = item.group(1)
    nxt = re.compile(rf"(?m)^{re.escape(dash)}- ").search(text, item.end(), body_end)
    return item.start(), (nxt.start() if nxt else body_end), dash + "  "


def _merge(have: str, add: list[str]) -> str:
    """A flow list's inside with new values appended (existing ones kept, in order).

    Args:
        have: the text between the brackets.
        add: values to add.

    Returns:
        The new text between the brackets.
    """
    items = [x.strip() for x in have.split(",") if x.strip()]
    return ", ".join(items + [x for x in add if x not in items])


def patch_item(block: str, field: str, add: list[str], indent: str, after: str) -> str:
    """One item's text with values added to a field's flow list (or the field inserted).

    Args:
        block: the item's text.
        field: `name` or `parent.child` (a list inside a one-line flow mapping).
        add: values to add.
        indent: the item's field indentation.
        after: the field after which a missing field is inserted ("" for the item's first line).

    Returns:
        The new text.
    """
    parent, _, child = field.rpartition(".")
    if not parent:
        if (m := re.search(rf"(?m)^{indent}{re.escape(field)}: \[([^\]]*)\]", block)) is not None:
            return block[:m.start(1)] + _merge(m.group(1), add) + block[m.end(1):]
        line = f"{indent}{field}: [{', '.join(add)}]"
    elif (m := re.search(rf"(?m)^{indent}{re.escape(parent)}: \{{(.*)\}}", block)) is not None:
        if (cm := re.search(rf"\b{re.escape(child)}: \[([^\]]*)\]", m.group(1))) is not None:
            s = m.start(1) + cm.start(1)
            return block[:s] + _merge(cm.group(1), add) + block[m.start(1) + cm.end(1):]
        inner = m.group(1).strip()
        return block[:m.start(1)] + (f"{inner}, " if inner else "") + f"{child}: [{', '.join(add)}]" + block[m.end(1):]
    else:
        line = f"{indent}{parent}: {{{child}: [{', '.join(add)}]}}"
    anchor = re.search(rf"(?m)^{indent}{re.escape(after)}:.*$", block) if after else None
    cut = anchor.end() if anchor else block.index("\n") if "\n" in block else len(block)
    return block[:cut] + "\n" + line + block[cut:]


def patch(text: str, list_key: str, key: str, field: str, adds: dict, after: str = "") -> str:
    """The whole text with every item's additions applied.

    Args:
        text: the YAML text.
        list_key: the top-level list.
        key: the field naming an item.
        field: the list field (`name` or `parent.child`).
        adds: {item id: [values]}.
        after: the field after which a missing field is inserted.

    Returns:
        The new text.

    Raises:
        KeyError: an item is not found.
    """
    for item_id, values in adds.items():
        i, j, indent = item_span(text, list_key, key, item_id)
        text = text[:i] + patch_item(text[i:j], field, list(values), indent, after) + text[j:]
    return text


def parses(text: str) -> str | None:
    """Whether the text is valid YAML, when PyYAML is installed (imported here, at the edge).

    Args:
        text: the YAML text.

    Returns:
        None when it parses or PyYAML is absent; else the parser's message.
    """
    try:
        import yaml
    except ImportError:
        return None
    try:
        yaml.safe_load(text)
    except yaml.YAMLError as exc:
        return str(exc)
    return None


def main(argv: list[str] | None = None) -> int:
    """Command line: print the plan, or write it with --apply.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0 on success, 1 when an item is missing or the result does not parse, 2 on bad arguments.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("file", type=Path)
    ap.add_argument("--list", required=True, dest="list_key", help="the top-level list, e.g. components")
    ap.add_argument("--key", default="id", help="the field naming an item (default id)")
    ap.add_argument("--field", required=True, help="the list field: name, or parent.child for a list inside a flow mapping")
    ap.add_argument("--spec", required=True, type=Path, help='JSON file: {"<item id>": ["value", ...]}')
    ap.add_argument("--after", default="", help="insert a missing field after this field (default: after the key line)")
    ap.add_argument("--apply", action="store_true", help="write the file (default: print the plan only)")
    args = ap.parse_args(argv)
    try:
        text, adds = args.file.read_text(encoding="utf-8"), json.loads(args.spec.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"yaml_list_patch: {exc}", file=sys.stderr)
        return 2
    try:
        new = patch(text, args.list_key, args.key, args.field, adds, args.after)
    except KeyError as exc:
        print(f"yaml_list_patch: {exc.args[0]}", file=sys.stderr)
        return 1
    if (err := parses(new)) is not None:
        print(f"yaml_list_patch: the result would not parse, nothing written: {err}", file=sys.stderr)
        return 1
    if not args.apply:
        sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), str(args.file), f"{args.file} (planned)"))
        print(f"plan only: {len(adds)} item(s); rerun with --apply to write")
        return 0
    args.file.write_text(new, encoding="utf-8")
    print(f"wrote {args.file}: {len(adds)} item(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
