"""Safe, line-aware YAML loading.

Uses ``ruamel.yaml`` in *safe* mode. Arbitrary Python tags / constructors are
never resolved. Ansible's ``!vault`` and ``!unsafe`` tags are recognised only
so the document can load without error — their payloads are never decrypted or
executed.

Every loaded mapping carries source line numbers (``lc.line`` is 0-indexed in
ruamel; callers convert to 1-indexed as needed).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML
from ruamel.yaml.constructor import RoundTripConstructor
from ruamel.yaml.error import YAMLError

from .hashing import EncodingError, hash_text, normalize_text, normalized_lines


class VaultTag:
    """Opaque placeholder for an ``!vault`` encrypted value. Never decrypted."""

    yaml_tag = "!vault"

    def __init__(self, ciphertext: str = "") -> None:
        # Store only a redacted marker, never the ciphertext body.
        self.present = True

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return "<vault>"


def _construct_vault(constructor: Any, node: Any) -> VaultTag:  # noqa: ARG001
    return VaultTag()


def _construct_unsafe(constructor: Any, node: Any) -> Any:
    # !unsafe simply marks a scalar as not-templatable; keep the scalar value.
    return constructor.construct_scalar(node)


def _make_yaml() -> YAML:
    # Round-trip mode preserves line/column info (``.lc``) needed for source
    # provenance while still avoiding arbitrary Python object construction.
    yaml = YAML(typ="rt")
    yaml.allow_duplicate_keys = True  # Ansible tolerates these; we diagnose them.
    # Register Ansible-specific tags so documents load without executing them.
    RoundTripConstructor.add_constructor("!vault", _construct_vault)
    RoundTripConstructor.add_constructor("!unsafe", _construct_unsafe)
    RoundTripConstructor.add_constructor("!vault-encrypted", _construct_vault)
    return yaml


@dataclass
class LoadedFile:
    """Result of loading a YAML file.

    ``documents`` is the list of top-level documents (Ansible multi-doc files
    are rare but supported). ``lines`` is the normalized line list used for
    region hashing. ``ok`` is False when the file could not be parsed.
    """

    path: str  # repository-relative
    documents: list[Any]
    lines: list[str]
    content_hash: str
    ok: bool = True
    error: str | None = None
    is_vault_file: bool = False


VAULT_HEADER = "$ANSIBLE_VAULT"


def load_yaml_file(abs_path: Path, rel_path: str, max_bytes: int) -> LoadedFile:
    """Load and normalize a YAML file. Never raises; errors are captured."""
    try:
        raw = abs_path.read_bytes()
    except OSError as exc:
        return LoadedFile(rel_path, [], [], "", ok=False, error=f"read error: {exc}")

    if len(raw) > max_bytes:
        return LoadedFile(
            rel_path, [], [], "", ok=False,
            error=f"file exceeds max-file-bytes ({len(raw)} > {max_bytes})",
        )

    try:
        text = normalize_text(raw)
    except EncodingError as exc:
        return LoadedFile(rel_path, [], [], "", ok=False, error=f"encoding: {exc}")

    content_hash = hash_text(text)
    lines = normalized_lines(text)

    # Detect whole-file vault encryption without attempting to decrypt.
    if text.lstrip().startswith(VAULT_HEADER):
        return LoadedFile(
            rel_path, [], lines, content_hash, ok=True, is_vault_file=True,
        )

    yaml = _make_yaml()
    try:
        documents = list(yaml.load_all(text))
    except YAMLError as exc:
        return LoadedFile(
            rel_path, [], lines, content_hash, ok=False,
            error=f"yaml parse error: {_short_yaml_error(exc)}",
        )
    except Exception as exc:  # ruamel can raise non-YAMLError on odd tags
        return LoadedFile(
            rel_path, [], lines, content_hash, ok=False,
            error=f"parse error: {type(exc).__name__}: {exc}",
        )

    documents = [d for d in documents if d is not None]
    return LoadedFile(rel_path, documents, lines, content_hash, ok=True)


def _short_yaml_error(exc: YAMLError) -> str:
    msg = str(exc).strip().replace("\n", " ")
    return msg[:300]


def node_line(obj: Any) -> int | None:
    """Return the 1-indexed source line of a ruamel node, if available."""
    lc = getattr(obj, "lc", None)
    if lc is not None and getattr(lc, "line", None) is not None:
        return int(lc.line) + 1
    return None


def key_line(mapping: Any, key: str) -> int | None:
    """Return the 1-indexed line where ``key`` is defined in a ruamel mapping."""
    lc = getattr(mapping, "lc", None)
    if lc is None:
        return None
    try:
        data = lc.data  # type: ignore[attr-defined]
    except AttributeError:
        return None
    if data and key in data:
        return int(data[key][0]) + 1
    return None
