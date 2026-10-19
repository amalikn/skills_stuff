"""Export draw.io pages to images with the desktop app's command line, for self-review before a drawing is shown to anyone. Stdlib only.

Flags as checked on draw.io desktop 32.4.1 and 32.5.5 (references/export-and-self-review.md; documents/drawio-sources-20261019/
drawio-desktop-cli-help-32.5.5.txt): `-x` export, `-f` format, `-o` output, `-p` the page, counted from 1 (without it only the first page is
exported), `-l`/`--layers` comma-separated layer indexes (0 is the base layer), `-s` scale, `-b` border. Every run has a subprocess timeout
(the app can hang on a bad file) and the app's own per-file `--timeout`.

Imported, not run: `from drawio import export` with the skill's scripts/ on sys.path; the command line is scripts/drawio_export.py.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

#: Where the desktop app's binary usually is, tried in order after `drawio` and `draw.io` on PATH.
CANDIDATES = ("/Applications/draw.io.app/Contents/MacOS/draw.io", "/usr/bin/drawio", "/opt/drawio/drawio",
              "C:/Program Files/draw.io/draw.io.exe")
#: Seconds one export may take before it is killed (a 1-page PNG took 3.5 s on 32.5.5).
TIMEOUT_S = 120


def find_binary(explicit: str = "") -> str:
    """The draw.io desktop binary.

    Args:
        explicit: a path given by the caller, used when set.

    Returns:
        The binary's path.

    Raises:
        FileNotFoundError: no binary is found.
    """
    if explicit:
        if not Path(explicit).is_file():
            raise FileNotFoundError(f"draw.io binary not found at {explicit}")
        return explicit
    for name in ("drawio", "draw.io"):
        if found := shutil.which(name):
            return found
    for path in CANDIDATES:
        if Path(path).is_file():
            return path
    raise FileNotFoundError("draw.io desktop not found; install it or pass its path (--binary)")


def export_argv(binary: str, source: Path, out: Path, page: int = 1, layers: tuple = (), scale: float = 1.0, border: int = 0,
                app_timeout: int = 60) -> list[str]:
    """The argument list for one page export (format from the output's extension).

    Args:
        binary: the draw.io binary.
        source: the .drawio file.
        out: the image to write (.png, .svg, .jpg or .pdf).
        page: the page, counted from 1 as the CLI counts.
        layers: layer indexes to keep (empty for all); 0 is the base layer.
        scale: the scale factor.
        border: the border in pixels.
        app_timeout: the app's own per-file timeout in seconds.

    Returns:
        The argv, flags before the input file.

    Raises:
        ValueError: page below 1, or an unknown output format.
    """
    if page < 1:
        raise ValueError(f"page {page}: the draw.io CLI counts pages from 1")
    fmt = out.suffix.lstrip(".").lower()
    if fmt not in ("png", "svg", "jpg", "pdf"):
        raise ValueError(f"{out}: output must be .png, .svg, .jpg or .pdf")
    argv = [binary, "-x", "-f", fmt, "-p", str(page), "-o", str(out), "-s", f"{scale:g}", "-b", str(border), "--timeout", str(app_timeout)]
    if layers:
        argv += ["--layers", ",".join(str(i) for i in layers)]
    return argv + [str(source)]


def run(argv: list[str], timeout_s: int = TIMEOUT_S) -> Path:
    """Run one export and check the image exists.

    Args:
        argv: from export_argv().
        timeout_s: seconds before the app is killed.

    Returns:
        The image written.

    Raises:
        RuntimeError: the app failed, timed out, or wrote no file.
    """
    out = Path(argv[argv.index("-o") + 1])
    try:
        proc = subprocess.run(argv, capture_output=True, text=True, timeout=timeout_s, check=False)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"draw.io export timed out after {timeout_s} s") from exc
    if proc.returncode != 0 or not out.is_file():
        raise RuntimeError(f"draw.io export failed (exit {proc.returncode}): {(proc.stderr or proc.stdout).strip()[:400]}")
    return out
