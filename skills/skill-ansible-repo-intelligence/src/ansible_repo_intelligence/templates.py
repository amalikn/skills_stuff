"""Template relationship extraction and parse-only Jinja variable analysis.

Jinja handling is strictly parse-only:

- use ``jinja2.Environment().parse()`` with only the repository-configured
  safe parse-time extensions
- walk the AST to extract undeclared variables and literal references
- never call ``render()``
- never execute filters, tests, lookups or custom extensions
- record parse failures as diagnostics

Enabling a parse-time extension never permits rendering or code execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from jinja2 import Environment, meta
from jinja2.exceptions import TemplateError

from .hashing import EncodingError, hash_bytes, normalize_text


def _identity(*args, **kwargs):  # pragma: no cover - never executed
    return args[0] if args else ""


class _TolerantMap(dict):
    """Returns an identity callable for any unknown filter/test name.

    Ansible ships hundreds of custom filters/tests (``dict2items``, ``ipaddr``,
    ``combine`` ...) that plain Jinja2 does not know. ``find_undeclared_variables``
    runs a codegen pass that rejects unknown filters, so we make lookups
    tolerant. The identity callable is never invoked — we only parse and walk
    the AST, never render — so this stays strictly parse-only.
    """

    def __missing__(self, key):  # noqa: D401
        return _identity


@dataclass
class TemplateInfo:
    rel_path: str
    content_hash: str
    variables: list[str] = field(default_factory=list)
    parse_ok: bool = True
    parse_error: str | None = None


def _make_env(safe_extensions: list[str]) -> Environment:
    # autoescape irrelevant for parse-only; keep default. Only safe, declared
    # parse-time extensions are loaded. Any failure to load falls back to none.
    try:
        env = Environment(extensions=list(safe_extensions))
    except (ImportError, TemplateError):
        env = Environment()
    # Tolerate unknown Ansible filters/tests during the AST walk.
    env.filters = _TolerantMap(env.filters)
    env.tests = _TolerantMap(env.tests)
    return env


def find_template_variables(text: str, safe_extensions: list[str]) -> tuple[list[str], str | None]:
    """Return (sorted undeclared variables, error) via parse-only AST walk."""
    env = _make_env(safe_extensions)
    try:
        ast = env.parse(text)
        variables = sorted(meta.find_undeclared_variables(ast))
    except TemplateError as exc:
        return [], f"jinja parse error: {str(exc)[:200]}"
    except Exception as exc:  # noqa: BLE001 - defensive: never crash a scan
        return [], f"jinja analysis error: {type(exc).__name__}: {str(exc)[:160]}"
    return variables, None


def analyze_template(abs_path: Path, rel_path: str, safe_extensions: list[str], max_bytes: int) -> TemplateInfo:
    try:
        raw = abs_path.read_bytes()
    except OSError as exc:
        return TemplateInfo(rel_path, "", parse_ok=False, parse_error=str(exc))
    if len(raw) > max_bytes:
        return TemplateInfo(rel_path, "", parse_ok=False, parse_error="exceeds max-file-bytes")
    try:
        text = normalize_text(raw)
    except EncodingError as exc:
        return TemplateInfo(rel_path, "", parse_ok=False, parse_error=f"encoding: {exc}")
    content_hash = hash_bytes(raw)
    variables, err = find_template_variables(text, safe_extensions)
    return TemplateInfo(
        rel_path=rel_path, content_hash=content_hash, variables=variables,
        parse_ok=err is None, parse_error=err,
    )
