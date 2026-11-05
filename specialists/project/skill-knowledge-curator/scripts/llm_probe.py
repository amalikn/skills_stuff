#!/usr/bin/env python3
"""Probe a local OpenAI-compatible model server before trusting it with kc verify: list its models, then time the control pairs.

A model that reads the verdict words backwards fails a control here, before any project is touched (references/conflicts-and-review.md,
Refuting verifier). Promoted from the 2026-11-05 oMLX probe.

Run: python scripts/llm_probe.py [--base URL] [--model ID]   (or `just llm-probe [ID]`, which loads the oMLX key).
  Without --model it lists the served models only. KC_LLM_API_KEY carries the key and is never printed.
Safety: read-only; sends the two fixed control texts (no project data) to the endpoint, which must be loopback unless --allow-remote.
Exit codes: 0 every control right (or listing only); 1 bad input or a non-loopback endpoint; 3 a control answered wrong; 6 the server failed.
"""

import argparse
import json
import sys
import time
import urllib.parse
from collections import Counter

from knowledge_curator_lib import llm, settings, verify
from knowledge_curator_lib.errors import InputError


def probe(base: str, model: str | None) -> dict:
  """List models and, for a model, answer the control pairs with timings.

  Args:
    base: endpoint base URL (…/v1).
    model: model ID to test, or None to list only.

  Returns:
    {"base", "models", "model", "controls": [{expected, got, seconds}], "passed", "usage"}.

  Raises:
    llm.ModelError: the server failed or returned no usable JSON.
  """
  out = {"base": base, "models": llm.list_models(base), "model": model, "controls": [], "passed": None, "usage": {}}
  if not model:
    return out
  usage = Counter()
  for control in verify.CONTROLS:
    start = time.perf_counter()
    got, used = llm.chat_json(base, model, verify.INSTRUCTIONS, verify.control_prompt(control), settings.DEFAULT_CONFIG["verify"]["max_tokens"])
    usage.update({k: v or 0 for k, v in used.items()})
    out["controls"].append({"expected": control["expected"], "got": got.get("verdict"), "seconds": round(time.perf_counter() - start, 2)})
  out["passed"] = all(c["expected"] == c["got"] for c in out["controls"])
  out["usage"] = dict(usage)
  return out


def main(argv: list[str] | None = None) -> int:
  """Run the probe and print JSON.

  Args:
    argv: arguments (sys.argv when None).

  Returns:
    Exit code.
  """
  p = argparse.ArgumentParser(description="Probe a local OpenAI-compatible model server (read-only).")
  p.add_argument("--base", default=settings.DEFAULT_CONFIG["verify"]["endpoint"], help="endpoint base URL, default the kc verify endpoint")
  p.add_argument("--model", help="model ID to answer the control pairs")
  p.add_argument("--allow-remote", action="store_true", help="permit a non-loopback endpoint")
  args = p.parse_args(argv)
  host = urllib.parse.urlparse(args.base).hostname
  if host not in llm.LOOPBACK and not args.allow_remote:
    print(f"llm_probe: {host!r} is not loopback; pass --allow-remote to send the control texts there", file=sys.stderr)
    return InputError.exit_code
  try:
    out = probe(args.base.rstrip("/"), args.model)
  except llm.ModelError as err:
    print(f"llm_probe: {err}", file=sys.stderr)
    return 6
  print(json.dumps(out, indent=2))
  return 3 if out["passed"] is False else 0


if __name__ == "__main__":
  sys.exit(main())
