#!/usr/bin/env python3
"""A small stdlib subset of JSON Schema (draft 2020-12) for validating data maps without the jsonschema package.

Promoted from unified-network-controller `scripts/render/flows_drawio.py` (2026-10-19). Supported keywords: type (one or a list), enum,
pattern, minLength, minItems, items, required, properties, additionalProperties (false or a schema), and `$ref` to `#/$defs/<name>`. Anything
else in a schema is ignored, so keep a map's schema to these keywords (the contract test of a project's map proves the subset suffices).

Imported, not run: `from schema_lite import schema_errors`.
"""

from __future__ import annotations

import re

_TYPES = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None)}


def type_ok(value: object, want: str) -> bool:
    """Whether a value has a JSON Schema type.

    Args:
        value: the loaded value.
        want: a JSON Schema type name.

    Returns:
        True when the value is of that type (booleans are not integers or numbers).
    """
    if want == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if want == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return isinstance(value, _TYPES[want])


def schema_errors(value: object, schema: dict, root: dict | None = None, where: str = "$") -> list[str]:
    """Validate a value against the supported JSON Schema subset.

    Args:
        value: the instance (the loaded map, or part of it).
        schema: the (sub)schema to apply.
        root: the whole schema document, for `$ref` lookups; defaults to `schema`.
        where: a JSONPath-like location for messages.

    Returns:
        One message per violation, in document order.
    """
    root = schema if root is None else root
    if "$ref" in schema:
        name = schema["$ref"].rsplit("/", 1)[-1]
        return schema_errors(value, root["$defs"][name], root, where)
    errs: list[str] = []
    types = schema.get("type")
    if types is not None:
        types = [types] if isinstance(types, str) else types
        if not any(type_ok(value, t) for t in types):
            return [f"{where}: expected {'/'.join(types)}, got {type(value).__name__}"]
    if "enum" in schema and value not in schema["enum"]:
        errs.append(f"{where}: {value!r} is not one of {schema['enum']}")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errs.append(f"{where}: shorter than {schema['minLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errs.append(f"{where}: {value!r} does not match {schema['pattern']}")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errs.append(f"{where}: needs at least {schema['minItems']} item(s)")
        if "items" in schema:
            for i, item in enumerate(value):
                errs += schema_errors(item, schema["items"], root, f"{where}[{i}]")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errs.append(f"{where}: missing required `{key}`")
        props = schema.get("properties", {})
        extra = schema.get("additionalProperties", True)
        for key, sub in value.items():
            if key in props:
                errs += schema_errors(sub, props[key], root, f"{where}.{key}")
            elif extra is False:
                errs.append(f"{where}: unknown key `{key}`")
            elif isinstance(extra, dict):
                errs += schema_errors(sub, extra, root, f"{where}.{key}")
    return errs
