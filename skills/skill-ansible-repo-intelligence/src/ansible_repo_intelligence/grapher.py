"""Optional adapter for `ansible-playbook-grapher`.

The external grapher is **supplementary evidence only**. A scan never depends on
it: if the CLI is absent, or invocation fails, or its output fails structural
validation, the scan still succeeds and records the outcome honestly in the
manifest's `external_tools` block. A successful process exit is never trusted on
its own — the output is structurally validated.

Invocation is OPT-IN (`--playbook-grapher`) because the grapher parses playbooks
through Ansible, which can load plugins.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

# Injectable runner so tests don't require the real CLI installed.
Runner = Callable[[list[str], Path], "RunResult"]

# The grapher is typically provided by the sibling `skill-ansible-grapher`,
# which installs it in its own managed venv rather than on the global PATH.
# Search these known locations before giving up. Override via env var.
_GRAPHER_CANDIDATES = (
    os.environ.get("ANSIBLE_PLAYBOOK_GRAPHER"),
    "/Volumes/Data/_ai/_skills/skills-working-cache/skill-ansible-grapher/.venv/bin/ansible-playbook-grapher",
    "/Volumes/Data/_ai/_skills/skills-working-cache/skill-ansible-grapher/venv/bin/ansible-playbook-grapher",
)


def resolve_binary() -> str | None:
    """Return a path to the grapher binary from PATH or the sibling skill venv."""
    onpath = shutil.which("ansible-playbook-grapher")
    if onpath:
        return onpath
    for cand in _GRAPHER_CANDIDATES:
        if cand and Path(cand).is_file() and os.access(cand, os.X_OK):
            return cand
    return None


@dataclass
class RunResult:
    exit_code: int
    stdout: str = ""
    stderr: str = ""


@dataclass
class GrapherProvenance:
    available: bool = False
    version: str | None = None
    invoked: bool = False
    command: list[str] = field(default_factory=list)
    exit_code: int | None = None
    output_path: str | None = None
    output_validated: bool = False
    note: str | None = None

    def to_dict(self) -> dict:
        return {
            "available": self.available,
            "version": self.version,
            "invoked": self.invoked,
            "command": self.command,
            "exit_code": self.exit_code,
            "output_path": self.output_path,
            "output_validated": self.output_validated,
            "note": self.note,
            "role": "supplementary evidence only; scan never depends on it",
        }


def _default_runner(cmd: list[str], cwd: Path) -> RunResult:
    try:
        p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=120)
        return RunResult(p.returncode, p.stdout, p.stderr)
    except (subprocess.TimeoutExpired, OSError) as exc:
        return RunResult(127, "", str(exc))


def detect(version_runner: Runner | None = None) -> GrapherProvenance:
    """Detect the grapher CLI without invoking a graph build."""
    prov = GrapherProvenance()
    if shutil.which("ansible-playbook-grapher") is None:
        prov.note = "ansible-playbook-grapher not on PATH"
        return prov
    prov.available = True
    runner = version_runner or _default_runner
    r = runner(["ansible-playbook-grapher", "--version"], Path.cwd())
    if r.exit_code == 0:
        prov.version = (r.stdout or r.stderr).strip().splitlines()[0] if (r.stdout or r.stderr) else "unknown"
    return prov


def run_grapher(
    repo: Path, playbook_rel: str, out_dir: Path, runner: Runner | None = None,
) -> GrapherProvenance:
    """Invoke the grapher on one playbook and structurally validate its output.

    Returns provenance regardless of success. Never raises.
    """
    prov = detect(runner)
    if not prov.available:
        return prov

    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "playbook-grapher.dot"
    # Use the DOT renderer + --save-dot-file; avoid opening a viewer.
    cmd = [
        "ansible-playbook-grapher", "--renderer", "graphviz",
        "--save-dot-file", "-o", str(out_file.with_suffix("")), playbook_rel,
    ]
    prov.invoked = True
    prov.command = cmd
    r = (runner or _default_runner)(cmd, repo)
    prov.exit_code = r.exit_code

    dot = _find_dot_output(out_dir)
    if r.exit_code != 0:
        prov.note = f"grapher exited {r.exit_code}: {(r.stderr or '')[:160]}"
        return prov
    if dot is None:
        prov.note = "grapher exited 0 but produced no .dot output (not trusting exit alone)"
        return prov
    prov.output_path = str(dot.relative_to(repo)) if _under(dot, repo) else str(dot)
    prov.output_validated = validate_dot(dot)
    if not prov.output_validated:
        prov.note = "grapher output failed structural validation"
    return prov


def validate_dot(path: Path) -> bool:
    """Structural validation of a Graphviz DOT graph (not just exit code)."""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False
    if "digraph" not in text and "graph" not in text:
        return False
    # Require at least one node/edge statement.
    return ("->" in text) or ("[label" in text) or ("[" in text and "]" in text)


def _find_dot_output(out_dir: Path) -> Path | None:
    dots = sorted(out_dir.glob("*.dot"))
    return dots[0] if dots else None


def _under(p: Path, root: Path) -> bool:
    try:
        p.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False
