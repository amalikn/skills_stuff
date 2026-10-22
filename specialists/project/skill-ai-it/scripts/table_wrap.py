"""Wrap a generated markdown table the way the workspace markdown hook does, so a generated block and the hook agree.

A generated block (the plan tracker's Timeline, a target map's embedded summary) is checked byte for byte against a fresh render, so a table
the hook would wrap differently can never stay wrapped: the hook wraps it on the next edit and the next render unwraps it. This module runs
the hook's own formatter, table-reflow, over the table with the hook's flags (`--width N --measure-rendered`), so the render is what the
hook would leave. Operator, 2026-10-22 (unified-network-controller): "why cant the timeline table be wrapped".

Imported, not run: `from table_wrap import wrap_table` with this scripts folder on sys.path. Runtime: one Node process per table, about 0.3 s.
Without Node or the tool (`TABLE_REFLOW_CLI` overrides its path) a table stays one line per row.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

#: The table formatter the markdown hook runs; overridable for another machine.
TABLE_REFLOW = os.environ.get("TABLE_REFLOW_CLI", "/Volumes/Data/_ai/_scripts/scripts_stuff/vscode_extensions/shared/table-reflow/cli.mjs")
#: Default wrap width, the global markdown table budget; 0 keeps one line per row.
WRAP_WIDTH = 200
#: Seconds the formatter may take.
REFLOW_TIMEOUT_S = 30


def wrap_table(table: str, width: int, runner=subprocess.run) -> str:
    """Wrap a markdown table the way the markdown hook does: table-reflow on a temporary file, `--width N --measure-rendered`. A file, not
    stdin: the tool reads stdin with readFileSync, which fails with EAGAIN on a pipe once a table outgrows the pipe buffer (2026-10-22, a
    target-map summary of 14 long rows).

    Args:
        table: the table's lines, header and separator first, joined by newlines.
        width: the column budget; 0 or less returns the table as it is.
        runner: subprocess.run, or a fake in tests.

    Returns:
        The wrapped table, or the table unchanged when wrapping is off, Node or the tool is missing, or the tool fails or times out.
    """
    if width <= 0 or not Path(TABLE_REFLOW).is_file() or not shutil.which("node"):
        return table
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "table.md"
        src.write_text(table + "\n", encoding="utf-8")
        try:
            done = runner(["node", TABLE_REFLOW, str(src), "--width", str(width), "--measure-rendered"], capture_output=True, text=True,
                          timeout=REFLOW_TIMEOUT_S, check=False)
        except (OSError, subprocess.TimeoutExpired):
            return table
    out = done.stdout.rstrip("\n")
    return out if done.returncode == 0 and out.startswith("|") else table
