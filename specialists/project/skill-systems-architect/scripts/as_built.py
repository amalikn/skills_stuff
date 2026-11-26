#!/usr/bin/env python3
"""As-built capture engine: read-only capture of a project's declared targets into stable, masked, diffable files (shared standard, continuum DL-264/265).

Run: python3 -I scripts/as_built.py --manifest <project>/as-built.toml [--apply] [--twice] [--only name,...] [--root <project>] [--out <folder>]   (just as-built <manifest> [...])
Plan (default): captures every target read-only and prints, per file, same / new / changed against what is on disk; writes nothing.
--apply: writes the changed and new files (git is the version store; `git diff` is the drift report). Files of targets not captured are left alone.
--twice: captures twice and fails when any file differs between the runs: the acceptance test for a target's churn filters; writes nothing.
Manifest (TOML): [capture] out, ssh_options, identity, known_hosts, secrets ("kp", the default, or "file:<path>" for a root-only KEY=VALUE file on a
host without KeePassXC), mask (extra regexes), drop (regexes of churn lines, all targets); [[target]] with
name, type (see as_built_probes.PROBES) and the type's options, plus its own `drop` list. Every probe only reads; secrets are never read except an API
token held in memory for a call; output is masked (secret-shaped values, tokens, email addresses) and churn lines removed before comparison.
Runtime budget: under 120 s for about ten targets on a LAN (each command times out after 120 s).
Exit codes: 0 done or planned (all targets answered); 1 a target failed or --twice found churn; 2 bad manifest or arguments.
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import shlex
import sys
import time
from pathlib import Path

import tomllib

# scripts/ is not a package: load the sibling probe library by path.
_spec = importlib.util.spec_from_file_location("as_built_probes", Path(__file__).with_name("as_built_probes.py"))
probes = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(probes)

MASKS = [
  (re.compile(r"(?i)((?:password|passwd|secret|token|api[_-]?key|private[_-]?key|passphrase|cipassword)[\"']?\s*[:=]\s*)(\S+)"), r"\1<redacted>"),
  (re.compile(r"\b(?:hvs\.|s\.)[A-Za-z0-9]{20,}\b"), "<redacted-token>"),
  (re.compile(r"\bnbp_[A-Za-z0-9]{20,}\b"), "<redacted-token>"),
  (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "<email>"),
]


def load_manifest(path: Path) -> tuple[dict, list[dict]]:
  """Read and check a manifest.

  Args:
    path: the TOML file.

  Returns:
    ([capture] block, targets).

  Raises:
    ValueError: a target lacks a name or type, a type is unknown, two targets share a name, a drop or mask regex does not compile, or secrets is
      neither "kp" nor "file:<path>".
  """
  data = tomllib.loads(path.read_text())
  cfg = data.get("capture", {})
  secrets = cfg.get("secrets", "kp")
  if secrets != "kp" and not (secrets.startswith("file:") and len(secrets) > len("file:")):
    raise ValueError(f'capture: secrets must be "kp" or "file:<path>", not {secrets!r}')
  targets = data.get("target", [])
  names = set()
  for t in targets:
    if not t.get("name") or not t.get("type"):
      raise ValueError(f"target without name or type: {t}")
    if t["type"] not in probes.PROBES:
      raise ValueError(f"target {t['name']}: unknown type {t['type']} (known: {', '.join(sorted(probes.PROBES))})")
    if t["name"] in names:
      raise ValueError(f"two targets named {t['name']}")
    names.add(t["name"])
  for where, pats in [("capture", cfg.get("drop", []) + cfg.get("mask", [])), *[(t["name"], t.get("drop", [])) for t in targets]]:
    for pat in pats:
      try:
        re.compile(pat)
      except re.error as e:
        raise ValueError(f"{where}: bad regex {pat!r}: {e}") from e
  return cfg, targets


def mask(text: str, extra: list[str]) -> str:
  """Mask secret-shaped values, tokens and email addresses.

  Args:
    text: captured text.
    extra: project regexes; each whole match becomes <redacted>.

  Returns:
    The masked text.
  """
  for pattern, repl in MASKS:
    text = pattern.sub(repl, text)
  for p in extra:
    text = re.sub(p, "<redacted>", text)
  return text


def drop_churn(text: str, patterns: list[str], strip: bool = True) -> str:
  """Remove lines that change on every run, and trailing whitespace, so two runs of an unchanged system are byte-identical.

  Args:
    text: masked text.
    patterns: regexes; a line matching any is dropped.
    strip: remove trailing whitespace from each line; a target sets `strip = false` when its files must stay byte-identical to an earlier
      writer's (pve-tenants defaults to false).

  Returns:
    The filtered text, ending in one newline.
  """
  regs = [re.compile(p) for p in patterns]
  lines = [ln.rstrip() if strip else ln for ln in text.splitlines() if not any(r.search(ln) for r in regs)]
  return "\n".join(lines).rstrip("\n") + "\n"


PLACEHOLDER = re.compile(r"\{(\w+):([\w.-]+)\}")


def resolve(value: object, cfg: dict, base: Path, run: probes.Runner, cache: dict) -> object:
  """Replace {resolver:key} placeholders in a target's strings, so a manifest holds no addresses (NAS DL-066).

  Args:
    value: a target value (string, list or table, walked recursively).
    cfg: [capture] block; [capture.resolvers] maps a resolver name to a command with {key}, run in the manifest's folder.
    base: the manifest's folder.
    run: runner.
    cache: resolved values, shared across targets.

  Returns:
    The value with every placeholder replaced.

  Raises:
    ValueError: an unknown resolver, or its command failed or printed nothing.
  """
  if isinstance(value, list):
    return [resolve(v, cfg, base, run, cache) for v in value]
  if isinstance(value, dict):
    return {k: resolve(v, cfg, base, run, cache) for k, v in value.items()}
  if not isinstance(value, str) or "{" not in value:
    return value

  def one(m: re.Match) -> str:
    """Resolve one placeholder, once per (resolver, key).

    Args:
      m: the placeholder match.
    Returns:
      The resolved text.
    Raises:
      ValueError: unknown resolver or empty answer.
    """
    name, key = m.group(1), m.group(2)
    if (name, key) not in cache:
      cmd = cfg.get("resolvers", {}).get(name)
      if not cmd:
        raise ValueError(f"unknown resolver {name} in {m.group(0)}")
      rc, out = run(["bash", "-c", f"cd {shlex.quote(str(base))} && " + cmd.replace("{key}", shlex.quote(key))], None, 30)
      if rc != 0 or not out.strip():
        raise ValueError(f"resolver {name} gave nothing for {key} (rc {rc})")
      cache[(name, key)] = out.strip().splitlines()[0]
    return cache[(name, key)]

  return PLACEHOLDER.sub(one, value)


def capture(cfg: dict, targets: list[dict], run: probes.Runner = probes.run_command) -> tuple[dict[str, str], list[str]]:
  """Capture every target, masked and churn-filtered.

  Args:
    cfg: [capture] block.
    targets: the targets to capture.
    run: command runner (tests pass a fake).

  Returns:
    ({relative file: text}, names of targets that failed).
  """
  files: dict[str, str] = {}
  failed = []
  for t in targets:
    try:
      raw = probes.PROBES[t["type"]](t, cfg, run)
    except (OSError, KeyError, ValueError) as e:
      raw = {f"{t['name']}.txt": f"== error\n{type(e).__name__}: {e}\n"}
    if t.get("file") and len(raw) == 1:
      raw = {t["file"]: next(iter(raw.values()))}
    for rel, text in raw.items():
      if "== error" in text or re.search(r"^== .* \(rc (?:124|255)\)$", text, re.M):
        failed.append(t["name"])
      strip = t.get("strip", t["type"] != "pve-tenants")
      files[rel] = drop_churn(mask(text, cfg.get("mask", [])), [*cfg.get("drop", []), *t.get("drop", [])], strip)
  return files, sorted(set(failed))


def compare(out: Path, files: dict[str, str]) -> dict[str, str]:
  """State of each file against disk.

  Args:
    out: capture folder.
    files: {relative file: text}.

  Returns:
    {relative file: same | new | changed}.
  """
  state = {}
  for rel, text in files.items():
    p = out / rel
    state[rel] = "new" if not p.exists() else ("same" if p.read_text() == text else "changed")
  return state


def main(argv: list[str] | None = None) -> int:
  """Plan, apply or test a capture.

  Args:
    argv: arguments; None uses sys.argv.

  Returns:
    Exit code.
  """
  ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
  ap.add_argument("--manifest", required=True, type=Path)
  ap.add_argument("--apply", action="store_true")
  ap.add_argument("--twice", action="store_true")
  ap.add_argument("--only", default="")
  ap.add_argument("--root", type=Path, help="project folder for resolvers, scripts and out (default: the manifest's folder)")
  ap.add_argument("--out", type=Path, help="write here instead of [capture] out (dry runs against a copy)")
  a = ap.parse_args(argv)
  try:
    cfg, targets = load_manifest(a.manifest)
  except (OSError, ValueError, tomllib.TOMLDecodeError) as e:
    print(f"as-built: {e}", file=sys.stderr)
    return 2
  if a.only:
    want = {x.strip() for x in a.only.split(",")}
    if unknown := want - {t["name"] for t in targets}:
      print(f"as-built: unknown target(s) {', '.join(sorted(unknown))}", file=sys.stderr)
      return 2
    targets = [t for t in targets if t["name"] in want]
  try:
    cache: dict = {}
    root = (a.root or a.manifest.parent).resolve()
    targets = [resolve(t, cfg, root, probes.run_command, cache) for t in targets]
    for t in targets:
      if t["type"] == "pve-tenants":
        t.setdefault("registry", "config/tenants.conf")
        t.setdefault("budgets", "config/guest-budgets.conf")
      for key in ("script", "registry", "budgets"):
        if t.get(key) and not Path(t[key]).is_absolute():
          t[key] = str(root / t[key])
  except ValueError as e:
    print(f"as-built: {e}", file=sys.stderr)
    return 2
  out = (a.out or (root / cfg.get("out", "as-built/captures"))).resolve()
  t0 = time.time()
  files, failed = capture(cfg, targets)
  if a.twice:
    second, _ = capture(cfg, targets)
    churn = sorted(rel for rel in files if files[rel] != second.get(rel))
    print(f"as-built: twice in {time.time() - t0:.0f} s; " + (f"differs: {', '.join(churn)}" if churn else "identical"))
    return 1 if churn or failed else 0
  for rel, state in sorted(compare(out, files).items()):
    print(f"{state:<8} {rel} ({len(files[rel].splitlines())} lines)")
    if a.apply and state != "same":
      (out / rel).parent.mkdir(parents=True, exist_ok=True)
      (out / rel).write_text(files[rel])
  print(
    f"as-built: {len(files)} file(s) in {time.time() - t0:.0f} s"
    + (f"; failed: {', '.join(failed)}" if failed else "")
    + ("" if a.apply else "; plan only, --apply writes")
  )
  return 1 if failed else 0


if __name__ == "__main__":
  sys.exit(main())
