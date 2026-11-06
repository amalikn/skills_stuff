"""A drift check without a redraw when nothing changed: the hash of what a map renders to, keyed by everything the render reads. Stdlib only.

A drawing is a pure function of the loaded map, the drawing profile (its look settings), this engine's source and the Python that runs it
(renders are byte-identical; the consumer check proves it). So when that key was rendered before, the drift check only needs to compare the
file on disk with the hash it rendered to, not to draw it again (2026-11-06: unified-network-controller's 42-page map took about 3 minutes
on every `just check` and every commit). A miss renders as before and records the key; the map is still loaded and validated every time.

The cache is per machine and never committed: `$SKILL_DRAWIO_CACHE`, else `$XDG_CACHE_HOME/skill-drawio`, else `~/.cache/skill-drawio`, one
small JSON file per key. `SKILL_DRAWIO_CACHE=off` turns it off. A cache that cannot be read or written is a miss, never an error.

Imported, not run: `from flowmap import render_cache` with the skill's scripts/ on sys.path.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

#: The engine's own packages and front end, hashed into every key so an engine change is always a miss.
ENGINE = Path(__file__).resolve().parents[1]
ENGINE_PARTS = ("drawio", "flowmap", "render_flowmap.py")


def cache_dir() -> Path | None:
    """Where the cache lives, or None when it is turned off.

    Returns:
        The folder (not created here), or None.
    """
    env = os.environ.get("SKILL_DRAWIO_CACHE")
    if env == "off":
        return None
    if env:
        return Path(env)
    base = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    return Path(base) / "skill-drawio"


def engine_hash() -> str:
    """A hash of every Python file of the engine, by path and content.

    Returns:
        The hex digest.
    """
    h = hashlib.sha256()
    for part in ENGINE_PARTS:
        path = ENGINE / part
        files = [path] if path.is_file() else sorted(path.rglob("*.py"))
        for f in files:
            h.update(str(f.relative_to(ENGINE)).encode())
            h.update(f.read_bytes())
    return h.hexdigest()


def key(data: dict, profile: object) -> str:
    """The render key: the loaded map (key order kept: order can change the drawing), the profile, the engine and the Python version.

    Args:
        data: the validated map.
        profile: the drawing profile.

    Returns:
        The hex digest.
    """
    h = hashlib.sha256()
    h.update(json.dumps(data, default=str, ensure_ascii=False).encode())
    h.update(repr(profile).encode())
    h.update(engine_hash().encode())
    h.update(sys.version.encode())
    return h.hexdigest()


def text_hash(text: str) -> str:
    """The hash a drawing's text is recorded under.

    Args:
        text: the drawing.

    Returns:
        The hex digest.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def lookup(k: str) -> str | None:
    """The drawing hash a key rendered to, if recorded.

    Args:
        k: the render key.

    Returns:
        The hash, or None on a miss (or when the cache is off or unreadable).
    """
    folder = cache_dir()
    if folder is None:
        return None
    try:
        return json.loads((folder / f"{k}.json").read_text(encoding="utf-8")).get("drawing")
    except (OSError, ValueError):
        return None


def record(k: str, text: str) -> None:
    """Record what a key rendered to (best effort: a write that fails leaves the next check a miss).

    Args:
        k: the render key.
        text: the rendered drawing.
    """
    folder = cache_dir()
    if folder is None:
        return
    try:
        folder.mkdir(parents=True, exist_ok=True)
        tmp = folder / f"{k}.json.tmp"
        tmp.write_text(json.dumps({"drawing": text_hash(text)}), encoding="utf-8")
        tmp.replace(folder / f"{k}.json")
    except OSError:
        pass
