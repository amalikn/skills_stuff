#!/usr/bin/env python3
"""Map whole-line comment blocks in a source file, so you can decide what becomes a note.

Reports runs of N or more consecutive whole-line comments, with their indent and first line of text,
plus the code line that follows each run (which is usually the right anchor for the note).

Trailing comments (`x = 1  # note`) are never reported: moving one detaches it from its statement.

Usage:
    map_comment_blocks.py FILE [--min 3] [--json]

Comment syntax is picked from the extension, or from a shebang when there is none.
"""
from __future__ import annotations
import argparse, json, pathlib, re, sys

# extension -> line-comment marker
MARKERS = {
    '.yml': '#', '.yaml': '#', '.py': '#', '.sh': '#', '.bash': '#', '.zsh': '#',
    '.rb': '#', '.pl': '#', '.tf': '#', '.toml': '#', '.cfg': '#', '.ini': '#',
    '.js': '//', '.ts': '//', '.tsx': '//', '.jsx': '//', '.go': '//', '.rs': '//',
    '.java': '//', '.c': '//', '.h': '//', '.cpp': '//', '.hpp': '//', '.cs': '//',
    '.php': '//', '.swift': '//', '.kt': '//', '.scala': '//',
}


def marker_for(path: pathlib.Path) -> str:
    ext = path.suffix.lower()
    if ext in MARKERS:
        return MARKERS[ext]
    try:
        first = path.read_text(errors='replace').split('\n', 1)[0]
    except OSError:
        first = ''
    if first.startswith('#!'):
        return '#'
    # justfiles, Makefiles and other extensionless config default to '#'
    return '#'


def block_scalar_lines(lines: list[str], marker: str) -> set[int]:
    """0-indexed line numbers that sit inside a YAML block scalar or a shell heredoc.

    A `#` in there is payload, not a comment, and must never be treated as one.
    """
    inside: set[int] = set()

    # YAML block scalars: `key: |` / `key: >` (with optional indicators), then a more-indented body.
    scalar_re = re.compile(r'^(\s*)(?:-\s+)?[^\s#][^:]*:\s*[|>][-+]?\d*\s*$')
    i = 0
    while i < len(lines):
        m = scalar_re.match(lines[i])
        if m:
            base = len(m.group(1))
            j = i + 1
            while j < len(lines):
                ln = lines[j]
                if ln.strip() == '':
                    inside.add(j); j += 1; continue
                if len(ln) - len(ln.lstrip()) > base:
                    inside.add(j); j += 1; continue
                break
            i = j
            continue
        i += 1

    # Shell heredocs: <<EOF / <<-'EOF' ... EOF
    here_re = re.compile(r'<<-?\s*[\'"]?([A-Za-z_][A-Za-z0-9_]*)[\'"]?')
    i = 0
    while i < len(lines):
        m = here_re.search(lines[i])
        if m:
            tag = m.group(1)
            j = i + 1
            while j < len(lines) and lines[j].strip() != tag:
                inside.add(j); j += 1
            i = j
        i += 1

    return inside


def find_blocks(path: pathlib.Path, min_len: int):
    text = path.read_text()
    lines = text.split('\n')
    marker = marker_for(path)
    masked = block_scalar_lines(lines, marker)

    def is_comment(idx: int) -> bool:
        if idx in masked:
            return False
        return lines[idx].lstrip().startswith(marker)

    blocks, i = [], 0
    while i < len(lines):
        if is_comment(i):
            start = i
            while i < len(lines) and is_comment(i):
                i += 1
            length = i - start
            if length >= min_len:
                nxt = next((k for k in range(i, len(lines)) if lines[k].strip()), None)
                blocks.append({
                    'start': start + 1,                     # 1-indexed, as humans read
                    'end': i,
                    'lines': length,
                    'indent': len(lines[start]) - len(lines[start].lstrip()),
                    'first': lines[start].strip(),
                    'anchor_line': (nxt + 1) if nxt is not None else None,
                    'anchor_text': lines[nxt].strip() if nxt is not None else None,
                })
        else:
            i += 1
    return blocks, len(lines), marker


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('file')
    ap.add_argument('--min', type=int, default=3, help='minimum consecutive comment lines (default 3)')
    ap.add_argument('--json', action='store_true', help='machine-readable output')
    args = ap.parse_args()

    path = pathlib.Path(args.file)
    if not path.is_file():
        print(f'not a file: {path}', file=sys.stderr)
        return 2

    blocks, total, marker = find_blocks(path, args.min)

    if args.json:
        print(json.dumps({'file': str(path), 'lines': total, 'marker': marker, 'blocks': blocks}, indent=2))
        return 0

    print(f'{path}  ({total} lines, comment marker {marker!r})')
    print(f'blocks of >= {args.min} consecutive comment lines: {len(blocks)}\n')
    if not blocks:
        return 0
    width = max(len(f"L{b['start']}-{b['end']}") for b in blocks)
    for b in blocks:
        rng = f"L{b['start']}-{b['end']}"
        anchor = f"  -> anchor L{b['anchor_line']}: {b['anchor_text'][:56]}" if b['anchor_line'] else ''
        print(f"{rng:<{width}}  ({b['lines']:>2} lines, indent {b['indent']})  {b['first'][:62]}")
        if anchor:
            print(' ' * (width + 2) + anchor.strip())
    total_comment = sum(b['lines'] for b in blocks)
    print(f'\n{total_comment} comment lines across {len(blocks)} blocks')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
