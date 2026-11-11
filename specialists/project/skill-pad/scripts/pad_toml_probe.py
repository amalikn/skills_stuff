#!/usr/bin/env python3
"""Pad upgrade test: rewrite a scratch `.pad.toml` through Pad and report what Pad kept.

Why (operator, 2026-11-11): Pad owns `.pad.toml` and a future release may change how it rewrites it. Tested by hand on pad 0.19.2: `pad
workspace link` on a linked folder writes nothing ("Already linked"); `pad workspace switch` rewrites the file, keeps unknown tables' data,
deletes every comment and reformats it; both write Pad's skill copies into `.claude/skills/pad` and `.agents/skills/pad`. Projects therefore
keep their own settings in a file Pad never writes (`tracker-map.toml`). This probe repeats the test before a new Pad version is used anywhere
(skill-ai-it `docs/central-project-tooling-plan-20261111_1141.md`, sections 4.4 and 7.8).

Run: `just pad-toml-probe <slug> <other-slug>` from any folder. Both slugs must be existing workspaces; `switch` changes only the scratch
folder's file. Writes only inside a temporary folder it deletes. Exit 0 = no change from the known behaviour, 1 = a difference to read before
upgrading, 2 = pad failed or timed out. Runtime: about 2 s (two pad calls).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

TIMEOUT_S = 30
SIDE_FILE = "tracker-map.toml"
SIDE_TEXT = (
    '# a file Pad does not own; must stay byte-identical\n[tracker]\ntool = "pad"\n'
)


def probe(
    slug: str, other: str, pad: str = "pad", timeout: int = TIMEOUT_S
) -> list[str]:
    """Rewrite a scratch `.pad.toml` by switching to another workspace and back, then compare.

    Args:
        slug: the workspace the scratch file starts on and returns to.
        other: a second existing workspace; switching to it forces a real rewrite (`link` on a linked folder writes nothing).
        pad: the pad binary.
        timeout: seconds per pad call.
    Returns:
        Differences from the known 0.19.2 behaviour; empty means Pad still keeps the workspace parseable, keeps unknown tables and ignores
        files it does not own. Comment loss is known and is reported as a note, not a difference.
    Raises:
        subprocess.CalledProcessError: a pad call failed.
        subprocess.TimeoutExpired: a pad call took longer than `timeout`.
    """
    with tempfile.TemporaryDirectory() as d:
        folder = Path(d)
        (folder / ".pad.toml").write_text(
            f'# probe comment\nworkspace = "{slug}"\n\n[probe]\nkept = true\n',
            encoding="utf-8",
        )
        (folder / SIDE_FILE).write_text(SIDE_TEXT, encoding="utf-8")
        for target in (other, slug):
            subprocess.run(
                [pad, "workspace", "switch", target],
                cwd=folder,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=True,
            )
        return compare(folder, slug)


def compare(folder: Path, slug: str) -> list[str]:
    """What Pad left in a scratch folder, against the known 0.19.2 behaviour.

    Args:
        folder: the scratch folder after Pad rewrote its `.pad.toml`.
        slug: the workspace the file should name again.
    Returns:
        Differences from the known behaviour; empty when Pad behaves as known.
    """
    text = (folder / ".pad.toml").read_text(encoding="utf-8")
    data = tomllib.loads(text)
    differences = []
    if data.get("workspace") != slug:
        differences.append(
            f"workspace is {data.get('workspace')!r} after switching back, expected {slug!r}"
        )
    if data.get("probe") != {"kept": True}:
        differences.append(
            "an unknown table was dropped or changed ([probe] kept = true)"
        )
    if (folder / SIDE_FILE).read_text(encoding="utf-8") != SIDE_TEXT:
        differences.append(f"Pad wrote {SIDE_FILE}, a file it does not own")
    if "# probe comment" in text:
        differences.append(
            "comments are now kept (known behaviour was to delete them): good news, update skill-pad"
        )
    return differences


def main(argv: list[str] | None = None) -> int:
    """Command line entry.

    Args:
        argv: arguments (default: sys.argv[1:]).
    Returns:
        0 when Pad behaves as known, 1 on a difference, 2 when pad failed or timed out.
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("slug", help="workspace the scratch file starts on and returns to")
    ap.add_argument(
        "other", help="a second existing workspace, to force a real rewrite"
    )
    ap.add_argument(
        "--pad", default="pad", help="the pad binary (default: pad on PATH)"
    )
    ap.add_argument("--timeout", type=int, default=TIMEOUT_S)
    args = ap.parse_args(argv)
    try:
        differences = probe(args.slug, args.other, args.pad, args.timeout)
    except (
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        FileNotFoundError,
    ) as exc:
        print(f"pad failed: {exc}")
        return 2
    for line in differences:
        print(f"difference: {line}")
    print(
        "OK: .pad.toml rewrite behaves as known (comments deleted, data and other files kept)"
        if not differences
        else "FAIL: read the differences before upgrading Pad"
    )
    return 1 if differences else 0


if __name__ == "__main__":
    sys.exit(main())
