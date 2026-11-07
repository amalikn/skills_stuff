#!/usr/bin/env python3
"""Read a Proxmox VE node in one SSH round trip: run several read-only commands (pvesh GETs, systemctl show) and split the
output by key. Read-only: every command it builds is a GET or a status read; it never runs apt update or changes state.

Why: the node report and the token audit (2026-11-07, skill-proxmox) both read the same API paths; one SSH session per host
instead of one per path keeps a report near one second on a lab node, and the parser is pure so tests need no node.

Usage (as a library):
  run = ssh_runner("pve.example.internal")           # or dir_runner("saved/")
  data = read_all(run, {"version": pvesh("/version")})
"""

from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path
from typing import Callable

#: Seconds the whole SSH round trip may take; every call states one.
CALL_TIMEOUT_S = 120
#: Seconds to wait for the TCP connection before giving up.
CONNECT_TIMEOUT_S = 10
#: Line that separates one command's output from the next in the batched round trip.
MARK = "@@pve-read@@"

Runner = Callable[[str], str]


class PveReadError(RuntimeError):
  """A read failed: SSH could not connect, a command timed out, or a key's output was not the JSON it should be."""


def pvesh(path: str) -> str:
  """The read-only pvesh command for one API path.

  Args:
    path: API path such as /nodes/localhost/storage; `localhost` resolves to the node the command runs on.

  Returns:
    The shell command line (a GET, JSON output).
  """
  return f"pvesh get {shlex.quote(path)} --output-format json"


def batch_script(commands: dict[str, str]) -> str:
  """One shell script that runs every command and prints a marker line naming each key before its output.

  Args:
    commands: key -> read-only shell command.

  Returns:
    The script text; stderr of each command is folded into its output so a failure is visible under its key.
  """
  parts = [f"echo {shlex.quote(MARK + ' ' + key)}; {cmd} 2>&1" for key, cmd in commands.items()]
  return "; ".join(parts)


def split_batch(text: str) -> dict[str, str]:
  """Split the batched output back into key -> output.

  Args:
    text: stdout of the batch script.

  Returns:
    key -> that command's output, stripped.
  """
  out: dict[str, str] = {}
  key = None
  for line in text.splitlines():
    if line.startswith(MARK + " "):
      key = line[len(MARK) + 1:].strip()
      out[key] = ""
    elif key is not None:
      out[key] += line + "\n"
  return {k: v.strip() for k, v in out.items()}


def ssh_runner(host: str, user: str = "root", timeout: float = CALL_TIMEOUT_S) -> Runner:
  """A runner that executes one shell script on the node over SSH (key auth only, no prompt).

  Args:
    host: node name or address.
    user: SSH user; root reads everything, a less privileged user sees less.
    timeout: seconds for the whole round trip.

  Returns:
    run(script) -> stdout.
  """
  def run(script: str) -> str:
    """Run the script on the node.

    Args:
      script: shell text.

    Returns:
      stdout.

    Raises:
      PveReadError: connection failure, timeout or non-zero exit of ssh itself.
    """
    argv = ["ssh", "-o", "BatchMode=yes", "-o", f"ConnectTimeout={CONNECT_TIMEOUT_S}", f"{user}@{host}", script]
    try:
      done = subprocess.run(argv, capture_output=True, text=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired as exc:
      raise PveReadError(f"ssh {host}: no answer within {timeout:.0f} s") from exc
    if done.returncode == 255:
      raise PveReadError(f"ssh {host}: {done.stderr.strip() or 'connection failed'}")
    return done.stdout
  return run


def dir_runner(folder: str | Path) -> Callable[[dict[str, str]], dict[str, str]]:
  """An offline reader: each key is read from <folder>/<key>.json or <key>.txt (captures saved earlier, or test fixtures).

  Args:
    folder: directory of captures.

  Returns:
    read(commands) -> key -> text; a missing file gives an empty string.
  """
  base = Path(folder)

  def read(commands: dict[str, str]) -> dict[str, str]:
    """Read each key's capture.

    Args:
      commands: key -> command (only the keys are used).

    Returns:
      key -> captured text.
    """
    out = {}
    for key in commands:
      hits = [base / f"{key}{ext}" for ext in (".json", ".txt") if (base / f"{key}{ext}").is_file()]
      out[key] = hits[0].read_text(encoding="utf-8").strip() if hits else ""
    return out
  return read


def read_all(run: Runner, commands: dict[str, str]) -> dict[str, str]:
  """Run every command in one round trip.

  Args:
    run: a runner from ssh_runner.
    commands: key -> read-only command.

  Returns:
    key -> output text.
  """
  return split_batch(run(batch_script(commands)))


def as_json(raw: dict[str, str], key: str, default: object = None) -> object:
  """Parse one key's output as JSON.

  Args:
    raw: key -> text from read_all or a dir reader.
    key: which output.
    default: returned when the output is empty (the capture or command is absent).

  Returns:
    The parsed value.

  Raises:
    PveReadError: the output is present but not JSON (for example a permission error printed by pvesh).
  """
  text = raw.get(key, "")
  if not text:
    return default
  try:
    return json.loads(text)
  except json.JSONDecodeError as exc:
    raise PveReadError(f"{key}: not JSON: {text[:160]}") from exc
