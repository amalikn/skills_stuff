"""Apply reviewed speech-to-text corrections to the dialogue section of a meeting transcript.

Automatic transcripts mishear names and terms. After a human or agent review produces a list of corrections, this script
applies them only below the dialogue marker (so summaries and correction tables above it are untouched), fails on any
pair that matches nothing, and can insert a table of every change so the original wording stays reconstructable.

Run:
    python ~/.agents/scripts/commtracker/apply_corrections.py <transcript.md> <corrections.tsv> [--table] [--dry-run]
        [--marker '^## Full']

Corrections file: one pair per line, `transcribed<TAB>corrected`. Blank lines and lines starting with `#` are ignored.
Prefix the left side with `?` to make a pair optional (no failure when it matches nothing), or with `re:` to treat it as a
regular expression. Use `\\n` in either side for a newline (for example to split a mis-attributed speaker turn). Pairs
apply in file order, so put specific phrases before the generic ones they contain.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def load_pairs(path: Path) -> list[tuple[str, str]]:
    """Read correction pairs from a TSV file.

    Args:
        path: corrections file, one `transcribed<TAB>corrected` pair per line.

    Returns:
        List of (transcribed, corrected) pairs with `\\n` escapes expanded, in file order.

    Raises:
        ValueError: a non-comment line has no tab separator.
    """
    pairs = []
    for number, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip() or line.startswith("#"):
            continue
        if "\t" not in line:
            raise ValueError(f"{path}:{number}: no tab between transcribed and corrected text")
        old, new = line.split("\t", 1)
        pairs.append((old.replace("\\n", "\n"), new.replace("\\n", "\n")))
    return pairs


def apply(body: str, pairs: list[tuple[str, str]]) -> tuple[str, list[tuple[str, str, int]], list[str]]:
    """Apply correction pairs to text in order.

    Args:
        body: the dialogue text to correct.
        pairs: (transcribed, corrected) pairs; `?` prefix marks optional, `re:` prefix marks a regex.

    Returns:
        (corrected body, applied rows as (shown transcribed, corrected, count), required pairs that matched nothing).
    """
    applied, missing = [], []
    for old, new in pairs:
        optional = old.startswith("?")
        old = old.removeprefix("?")
        if old.startswith("re:"):
            body, count = re.subn(old[3:], new, body)
            shown = old[3:]
        else:
            count = body.count(old)
            body = body.replace(old, new)
            shown = old
        if count:
            applied.append((shown, new, count))
        elif not optional:
            missing.append(old)
    return body, applied, missing


def table(applied: list[tuple[str, str, int]]) -> str:
    """Render the applied corrections as a markdown section.

    Args:
        applied: rows of (transcribed, corrected, count).

    Returns:
        A `## Transcription corrections` section ending in a blank line.
    """
    def cell(text: str) -> str:
        return text.replace("|", "\\|").replace("\n", " ").replace("*", "\\*")

    rows = "\n".join(f"| {cell(old)} | {cell(new)} | {count} |" for old, new, count in applied)
    return (
        "## Transcription corrections\n\nThe dialogue below was corrected on review. Each change is listed here so the original wording can be "
        "reconstructed. Guesses are marked inline as `[?: …]` and phrases that cannot be recovered as `[unclear]`.\n\n"
        "| Transcribed as | Corrected to | Times |\n|---|---|---|\n" + rows + "\n\n"
    )


def main(argv: list[str] | None = None) -> int:
    """Correct one transcript file in place.

    Args:
        argv: command-line arguments; defaults to sys.argv[1:].

    Returns:
        0 when every required pair matched, 1 otherwise (the file is still written unless --dry-run), 2 when the marker is missing.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("transcript", type=Path)
    parser.add_argument("corrections", type=Path)
    parser.add_argument("--marker", default=r"^## Full", help="regex for the heading that starts the dialogue (default: ^## Full)")
    parser.add_argument("--table", action="store_true", help="insert a corrections table above the dialogue marker")
    parser.add_argument("--dry-run", action="store_true", help="report what would change without writing")
    args = parser.parse_args(argv)

    text = args.transcript.read_text()
    match = re.search(args.marker, text, re.M)
    if match is None:
        print(f"marker {args.marker!r} not found in {args.transcript}", file=sys.stderr)
        return 2
    head, body = text[: match.start()], text[match.start():]
    body, applied, missing = apply(body, load_pairs(args.corrections))
    for old in missing:
        print(f"NO MATCH: {old[:70]!r}", file=sys.stderr)
    if args.table and applied:
        head += table(applied)
    print(f"pairs applied: {len(applied)}, replacements: {sum(count for *_, count in applied)}, unmatched: {len(missing)}")
    if not args.dry_run:
        args.transcript.write_text(head + body)
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
