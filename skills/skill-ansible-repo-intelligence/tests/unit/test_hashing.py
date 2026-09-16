"""Cross-platform hash determinism gate."""

from ansible_repo_intelligence.hashing import hash_bytes, normalize_text


def test_crlf_and_lf_hash_identically():
    lf = b"line1\nline2\nline3\n"
    crlf = b"line1\r\nline2\r\nline3\r\n"
    cr = b"line1\rline2\rline3\r"
    assert hash_bytes(lf) == hash_bytes(crlf) == hash_bytes(cr)


def test_bom_is_stripped():
    with_bom = "﻿key: value\n".encode("utf-8")
    without = b"key: value\n"
    assert hash_bytes(with_bom) == hash_bytes(without)


def test_other_whitespace_preserved():
    a = b"key:  value\n"   # two spaces
    b = b"key: value\n"    # one space
    assert hash_bytes(a) != hash_bytes(b)


def test_hash_format():
    h = hash_bytes(b"x")
    assert h.startswith("sha256:") and len(h) == len("sha256:") + 64


def test_non_utf8_raises():
    import pytest

    from ansible_repo_intelligence.hashing import EncodingError
    with pytest.raises(EncodingError):
        normalize_text(b"\xff\xfe\x00invalid")
