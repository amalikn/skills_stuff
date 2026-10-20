#!/usr/bin/env python3
"""Print the skeleton of a new script and its test that already meets this pack's rules; the agent fills in the logic. Read-only: it prints to
stdout and writes nothing.

Why (operator, 2026-10-20: the project writes its code, the skill supplies the practice): boilerplate written from memory drifts (a missing
Args block, a write path without --apply, a subprocess without a timeout). The skeleton carries the purpose header (summary, why, how it is run,
what it touches), documented functions, the --apply gate when the script writes, timeouts on every call out, and an offline test of the plan.
The project's own rules still outrank it: adjust the skeleton to the project's layout, names and test runner before use.

Usage:
    scaffold.py --lang python --name sync_widgets --summary "Copy widgets from A to B" [--writes] [--run "just sync-widgets"]
    scaffold.py --lang shell --name backup_db --summary "Dump the database" --writes
Exit: 0 after printing, 2 on bad arguments.
"""

from __future__ import annotations

import argparse
import re
import sys
from string import Template

#: The oldest Python this script runs on: it runs with the target project's own interpreter (the pack's contract test parses it at this grammar).
REQUIRES_PYTHON = (3, 11)

NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")

PY_MODULE = Template('''#!/usr/bin/env python3
"""$summary. $safety

Why: <the problem this solves and who asked for it, with a date>.

Usage:
    $run
"""

from __future__ import annotations

import argparse
import subprocess
import sys

#: Seconds any one call out (subprocess, HTTP, socket) may take; every call states one.
CALL_TIMEOUT_S = 30


def plan(items: list[str]) -> list[str]:
    """What the run would do, one line per change; pure, so the test can check it.

    Args:
        items: <what the plan is built from>.

    Returns:
        One line per change.
    """
    return [f"would change {item}" for item in items]

$apply_func
def main(argv: list[str] | None = None) -> int:
    """Command line.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0 on success, 1 on a failure it reports, 2 on bad arguments.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\\n")[0])
$apply_arg    args = ap.parse_args(argv)
    lines = plan([])
    print("\\n".join(lines) or "nothing to do")
$apply_call    return 0


if __name__ == "__main__":
    sys.exit(main())
''')

PY_APPLY_FUNC = '''
def apply(lines: list[str]) -> int:
    """Make the planned changes; called only with --apply.

    Args:
        lines: the plan.

    Returns:
        The number of changes made.

    Raises:
        subprocess.TimeoutExpired: when a call out exceeds CALL_TIMEOUT_S (for a command that starts children, such as ssh or a shell, end
            the whole process group instead: see the pack's errors-and-timeouts reference).
    """
    for _line in lines:
        subprocess.run(["true"], check=True, timeout=CALL_TIMEOUT_S)   # <the change>
    return len(lines)

'''

PY_TEST = Template('''"""Offline tests for $name: the plan is right, and nothing is written without --apply.

Run: <the project's test runner>.
"""

import io
import unittest
from contextlib import redirect_stdout

import $name


class Plan(unittest.TestCase):
    """The plan names each change; a dry run changes nothing."""

    def test_plan_lists_each_change(self):
        self.assertEqual($name.plan(["a"]), ["would change a"])

    def test_dry_run_prints_and_exits_0(self):
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual($name.main([]), 0)
        self.assertIn("nothing to do", out.getvalue())


if __name__ == "__main__":
    unittest.main()
''')

SH_MODULE = Template('''#!/usr/bin/env bash
# $summary. $safety
# Why: <the problem this solves and who asked for it, with a date>.
# Usage: $run
set -euo pipefail

CALL_TIMEOUT_S=30   # every call out is bounded: `bounded <cmd>` (for ssh, see the pack's errors-and-timeouts reference)
SITE=""   # an example option with a value; replace with the script's own
$apply_var
# bounded
#   Run a command for at most CALL_TIMEOUT_S seconds: GNU timeout where installed, else perl's alarm (macOS ships perl, not timeout).
#   Args: $$@ the command and its arguments.
#   Returns: the command's status; 124 (timeout) or 142 (alarm) when it ran too long.
bounded() {
  if command -v timeout >/dev/null 2>&1; then timeout "$$CALL_TIMEOUT_S" "$$@"; else perl -e 'alarm shift; exec @ARGV' "$$CALL_TIMEOUT_S" "$$@"; fi
}

# plan
#   Print one line per change the run would make.
#   Args: none.
#   Returns: 0.
plan() {
  echo "would change <item> at $${SITE:-every site}"
}
$apply_func
# main
#   Parse arguments, print the plan$apply_doc.
#   Args: $$@ the command line.
#   Returns: 0 on success; exits 2 on bad arguments.
main() {
  while [ $$# -gt 0 ]; do
    case "$$1" in
      --site) SITE="$${2:?--site needs a value}"; shift ;;
$apply_case      -h|--help) sed -n '2,4p' "$$0"; exit 0 ;;
      *) echo "$name: unknown argument $$1" >&2; exit 2 ;;
    esac
    shift
  done
  plan
$apply_call}

main "$$@"
''')


def python_files(name: str, summary: str, writes: bool, run: str) -> dict[str, str]:
    """The Python module and its test.

    Args:
        name: the module name (snake_case).
        summary: one sentence saying what it does.
        writes: whether it changes anything (adds the --apply gate).
        run: how it is run.

    Returns:
        {file name: text}.
    """
    module = PY_MODULE.substitute(
        summary=summary.rstrip("."), run=run,
        safety="Writes only with --apply; without it, prints the plan." if writes else "Read-only.",
        apply_func=PY_APPLY_FUNC if writes else "",
        apply_arg='    ap.add_argument("--apply", action="store_true", help="make the changes; without it, print the plan")\n' if writes else "",
        apply_call="    if args.apply:\n        print(f\"changed {apply(lines)}\")\n" if writes else "")
    return {f"{name}.py": module, f"test_{name}.py": PY_TEST.substitute(name=name)}


def shell_files(name: str, summary: str, writes: bool, run: str) -> dict[str, str]:
    """The shell script.

    Args:
        name: the script name (snake_case).
        summary: one sentence saying what it does.
        writes: whether it changes anything (adds the --apply gate).
        run: how it is run.

    Returns:
        {file name: text}.
    """
    script = SH_MODULE.substitute(
        name=name, summary=summary.rstrip("."), run=run,
        safety="Writes only with --apply; without it, prints the plan." if writes else "Read-only.",
        apply_var="APPLY=0\n" if writes else "",
        apply_func=("\n# apply\n#   Make the planned changes; called only with --apply.\n#   Args: none.\n#   Returns: 0; exits non-zero on a failed change.\n"
                    "apply() {\n  bounded true   # <the change>\n}\n") if writes else "",
        apply_doc=" and, with --apply, make the changes" if writes else "",
        apply_case="      --apply) APPLY=1 ;;\n" if writes else "",
        apply_call='  [ "$APPLY" = 1 ] && apply\n  return 0\n' if writes else "")
    return {f"{name}.sh": script}


def main(argv: list[str] | None = None) -> int:
    """Command line.

    Args:
        argv: arguments (default sys.argv[1:]).

    Returns:
        0 after printing, 2 on bad arguments.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--lang", choices=["python", "shell"], required=True)
    ap.add_argument("--name", required=True, help="snake_case module or script name, no suffix")
    ap.add_argument("--summary", required=True, help="one sentence: what it does")
    ap.add_argument("--writes", action="store_true", help="it changes something: add the --apply gate")
    ap.add_argument("--run", help="how it is run (default: the script with its flags)")
    args = ap.parse_args(argv)
    if not NAME_RE.match(args.name):
        print(f"scaffold: --name {args.name!r} is not snake_case", file=sys.stderr)
        return 2
    suffix = ".py" if args.lang == "python" else ".sh"
    run = args.run or f"{args.name}{suffix}" + (" [--apply]" if args.writes else "")
    files = (python_files if args.lang == "python" else shell_files)(args.name, args.summary, args.writes, run)
    for fname, text in files.items():
        print(f"===== {fname}\n{text}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
