"""Runtime isolation: the venv lives outside the repo and recipes address the pinned interpreter."""

from __future__ import annotations

import re
from pathlib import Path

from ..core import counted, fail
from ..config import (
    ROOT,
)
from ..helpers import (
    read,
)

def check_venv_outside_repo() -> None:
    """The maintenance venv is not created inside this repo.

    Rule: skills_stuff/AGENTS.md, "venv + ephemeral runtime placement" (2026-04-23) — a skill's venv belongs at skills-working-cache/<skill>/venv and "never
    inside skills_stuff/<skill>/". Regression guard: on 2026-09-01 the root .mise.toml declared `path = ".venv"`, so every `mise run` silently built a venv in
    the source tree. .gitignore hid it, which is what let it survive — the violation was invisible to git status and to every existing check.
    """
    text = read(".mise.toml")
    if text is None:
        return
    for match in re.finditer(r"_\.python\.venv\s*=\s*\{[^}]*path\s*=\s*\"([^\"]+)\"", text):
        counted()
        declared = match.group(1)
        if not declared.startswith("/") or Path(declared).is_relative_to(ROOT):
            fail(
                "storage-routing",
                f".mise.toml puts the venv at `{declared}` — it must be an absolute path outside the repo, "
                f"under skills-working-cache/agent-stack/",
            )


def check_interpreter_pinning() -> None:
    """No task recipe reaches an interpreter implicitly.

    Two defects, one root cause — the recipe does not say which interpreter it means:

    1. A BARE `python3`/`npx`/`ruby` resolves to whatever is on PATH, not to what .mise.toml pins.
    2. `mise exec -- python` resolves to the venv only while `_.python.venv` activation applies. It tests clean, reads
       as pinned, and degrades SILENTLY to the host interpreter when that activation stops holding. Observed here on
       2026-09-01: every recipe used `mise exec -- python` and resolved correctly, while .mise.toml simultaneously
       pointed the venv INSIDE the repo — the implicit form made both the pinning and the violation invisible.

    Recipes must address {{py}} by path and depend on `_require-venv`. Node has no venv layer, so `mise exec -- node` is the legitimate explicit form for it.

    Rule: the runtime-isolation section of skill-ai-it's SKILL.md, and the Runtime placement section of AGENTS.md.
    """
    text = read("justfile")
    if text is None:
        return
    for lineno, line in enumerate(text.splitlines(), 1):
        if not line.startswith((" ", "\t")):
            continue  # recipe bodies are indented; the header line is not a command
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        # Blank out quoted literals before scanning. An interpreter NAME inside a string is a label being printed, not a command being run — `printf 'python  '`
        # in the `runtimes` recipe is the case that found this. Blanking rather than deleting keeps every offset intact, so the reported column still points at
        # real source.
        stripped = re.sub(r"'[^']*'|\"[^\"]*\"", lambda m: " " * len(m.group(0)), stripped)
        counted()
        if re.search(r"mise\s+exec\b[^|;]*--\s+python", stripped):
            fail(
                "runtime",
                f"justfile:{lineno} reaches Python through an implicit `mise exec -- python` — address the venv "
                f"interpreter by path via {{{{py}}}} and guard it with _require-venv",
            )
        for match in re.finditer(r"(?<![-\w/])(python3?|npx|ruby)\b", stripped):
            if re.search(r"mise\s+(exec\b[^|;]*--|run)\s*$", stripped[: match.start()]):
                continue
            fail(
                "runtime",
                f"justfile:{lineno} calls bare `{match.group(1)}` — route it through the pinned interpreter",
            )
