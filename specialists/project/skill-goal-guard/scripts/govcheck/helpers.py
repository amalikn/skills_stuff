"""Shared readers for skill-goal-guard's governance checks: the project root, file walking, markdown links and front matter.

Imported, not run. Read-only. Imported by checks/, never the reverse.
"""

import re
from pathlib import Path

from . import config

LINK = re.compile(r"\]\(([^)\s]+)\)")


def root() -> Path:
  """Return the project root the checks read.

  Returns:
    config.ROOT, read at call time so a test can point it elsewhere.
  """
  return config.ROOT


def files(pattern: str = "*") -> list[Path]:
  """List project files matching a glob, skipping config.SKIP_DIRS.

  Args:
    pattern: a glob relative to any folder, e.g. "*.md".

  Returns:
    Sorted file paths.
  """
  base = root()
  out = []
  for p in base.rglob(pattern):
    folders = p.relative_to(base).parts[:-1]
    # Dot-folders (.git, .remember, .code-context-notes, caches) are tool state, not pack content.
    if p.is_file() and p.name not in config.SKIP_FILES and not any(f.startswith(".") or f in config.SKIP_DIRS for f in folders):
      out.append(p)
  return sorted(out)


def rel(path: Path) -> str:
  """Return a path relative to the root, POSIX style.

  Args:
    path: a path under the root.

  Returns:
    The relative path text.
  """
  return path.relative_to(root()).as_posix()


def is_verbatim(path: Path) -> bool:
  """Say whether a file is a verbatim source.

  Args:
    path: a project file.

  Returns:
    True when it sits under one of config.VERBATIM.
  """
  text = rel(path)
  return any(text == v or text.startswith(v) for v in config.VERBATIM)


def strip_code(text: str) -> str:
  """Remove fenced code blocks and inline code so links inside them are not read as links.

  Args:
    text: markdown text.

  Returns:
    The text without code.
  """
  text = re.sub(r"```.*?```", "", text, flags=re.S)
  return re.sub(r"`[^`\n]*`", "", text)


def links(path: Path) -> list[str]:
  """Return the relative link targets in a markdown file, without anchors.

  Args:
    path: a markdown file.

  Returns:
    Targets that are not URLs, absolute paths or pure anchors.
  """
  out = []
  for target in LINK.findall(strip_code(path.read_text(encoding="utf-8"))):
    target = target.split("#", 1)[0]
    if target and "://" not in target and not target.startswith(("/", "mailto:")):
      out.append(target)
  return out


def front_matter(path: Path) -> tuple[dict[str, str], bool] | None:
  """Read a file's front matter keys and whether a blank line follows it.

  Args:
    path: a markdown file.

  Returns:
    (keys, blank_after) when the file opens with ---, or None when it has no front matter.
  """
  lines = path.read_text(encoding="utf-8").split("\n")
  if not lines or lines[0] != "---" or "---" not in lines[1:]:
    return None
  end = lines.index("---", 1)
  keys = {}
  for line in lines[1:end]:
    match = re.match(r"^([A-Z][A-Za-z ]*):", line)
    if match:
      keys[match.group(1)] = line
  return keys, end + 1 < len(lines) and lines[end + 1].strip() == ""
