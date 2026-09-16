"""Cross-platform deterministic content hashing.

A repository cloned on a different operating system must produce identical
content hashes. To guarantee that, all source bytes are normalized before
hashing:

1. decode using UTF-8 with BOM handling
2. unsupported encodings are surfaced by the caller as a diagnostic
3. normalize CRLF and lone CR line endings to LF
4. all other whitespace and content is preserved exactly
5. hash the normalized UTF-8 byte sequence
6. the same normalization is used for full-file and source-region hashes

Hashes must never vary solely because a repository was cloned on a different
operating system.
"""

from __future__ import annotations

import hashlib


class EncodingError(ValueError):
    """Raised when file bytes cannot be decoded as UTF-8."""


def normalize_text(raw: bytes) -> str:
    """Decode raw bytes to a normalized ``str``.

    Raises :class:`EncodingError` for non-UTF-8 content so the caller can emit
    a diagnostic rather than silently corrupting the hash.
    """
    # UTF-8-SIG strips a leading BOM if present, otherwise behaves as UTF-8.
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise EncodingError(str(exc)) from exc
    # Normalize CRLF first, then any remaining lone CR, to LF.
    return text.replace("\r\n", "\n").replace("\r", "\n")


def hash_text(text: str) -> str:
    """Return ``sha256:<hex>`` for an already-normalized string."""
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def hash_bytes(raw: bytes) -> str:
    """Normalize raw bytes then return ``sha256:<hex>``."""
    return hash_text(normalize_text(raw))


def hash_region(lines: list[str], line_start: int | None, line_end: int | None) -> str:
    """Hash a 1-indexed inclusive line region of a normalized line list.

    ``lines`` must already be normalized (LF split). When line numbers are
    unavailable the whole content is hashed.
    """
    if line_start is None or line_end is None:
        return hash_text("\n".join(lines))
    start = max(1, line_start)
    end = min(len(lines), line_end)
    region = lines[start - 1 : end]
    return hash_text("\n".join(region))


def normalized_lines(text: str) -> list[str]:
    """Split already-normalized text into lines without keeping line endings."""
    return text.split("\n")
