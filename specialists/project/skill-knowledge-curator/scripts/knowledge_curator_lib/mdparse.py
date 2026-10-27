"""markdown-it-py seam: split a Markdown document into top-level blocks with 1-based line spans and their heading path.

Imported, not run. The only module that imports markdown_it. Front matter is cut off before parsing (markdown-it reads a leading
`---` block as a rule and a setext heading) and reported as its own block. Headings are structure, not blocks: they appear in each
block's heading_path. Line maps are aids for evidence spans, not immutable addresses (design doc 2.3). Upgrade test:
tests/test_seams.py. Safety: pure parsing.
"""

import re
from dataclasses import dataclass

from markdown_it import MarkdownIt

_MD = MarkdownIt("commonmark").enable("table")
_BLOCK_KIND = {
  "paragraph_open": "paragraph",
  "table_open": "table",
  "fence": "code",
  "code_block": "code",
  "bullet_list_open": "list",
  "ordered_list_open": "list",
  "blockquote_open": "blockquote",
  "html_block": "html",
}
_STATUS = re.compile(r"^\s*(?:\*\*)?Status:?(?:\*\*)?:?\s*(.+?)\s*$", re.IGNORECASE)


@dataclass(frozen=True)
class Block:
  """One top-level Markdown block.

  Attributes:
    kind: front_matter, paragraph, table, code, list, blockquote or html.
    heading_path: titles of the enclosing headings, outermost first.
    line_start: first line, 1-based.
    line_end: last line, inclusive.
    text: the block's source lines joined with newlines.
  """

  kind: str
  heading_path: tuple[str, ...]
  line_start: int
  line_end: int
  text: str


def front_matter_end(lines: list[str]) -> int:
  """Number of lines taken by a leading `---` front matter block.

  Args:
    lines: the document's lines.

  Returns:
    0 when there is no front matter, else the count including both fences.
  """
  if not lines or lines[0].strip() != "---":
    return 0
  for i in range(1, len(lines)):
    if lines[i].strip() == "---":
      return i + 1
  return 0


def _heading_title(tokens, index: int) -> str:
  """Inline text of the heading that opens at tokens[index].

  Args:
    tokens: markdown-it token stream.
    index: position of a heading_open token.

  Returns:
    The heading text, stripped.
  """
  nxt = tokens[index + 1] if index + 1 < len(tokens) else None
  return (nxt.content if nxt is not None and nxt.type == "inline" else "").strip()


def parse_blocks(text: str) -> list[Block]:
  """Split a document into top-level blocks.

  Args:
    text: the whole document.

  Returns:
    Blocks in document order.
  """
  lines = text.splitlines()
  offset = front_matter_end(lines)
  blocks = []
  if offset:
    blocks.append(Block("front_matter", (), 1, offset, "\n".join(lines[:offset])))
  tokens = _MD.parse("\n".join(lines[offset:]))
  path: list[str] = []
  for i, tok in enumerate(tokens):
    if tok.level != 0 or tok.map is None:
      continue
    if tok.type == "heading_open":
      depth = int(tok.tag[1])
      path = path[: depth - 1] + [""] * max(0, depth - 1 - len(path))
      path.append(_heading_title(tokens, i))
      continue
    kind = _BLOCK_KIND.get(tok.type)
    if kind is None:
      continue
    start, end = tok.map[0] + offset + 1, tok.map[1] + offset
    blocks.append(Block(kind, tuple(path), start, end, "\n".join(lines[start - 1 : end])))
  return blocks


def declared_status(text: str) -> str | None:
  """Status a document declares about itself: front matter `Status:` or a `Status:` line near the top.

  Args:
    text: the whole document.

  Returns:
    The declared status text, or None.
  """
  lines = text.splitlines()
  end = front_matter_end(lines)
  for line in lines[:end] if end else lines[:15]:
    match = _STATUS.match(line)
    if match and match.group(1).strip("*: "):
      return match.group(1).strip("*: ")
  return None
