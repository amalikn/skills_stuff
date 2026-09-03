#!/usr/bin/env python3
"""OpenAI-compatible chat adapter for the behavioural routing evaluator.

`scripts/evaluate_routing.py` owns the evaluation contract: it hands a prompt on **stdin** and reads a routing plan from **stdout**. It speaks to models only by
running a shell command, so reaching an HTTP API needs an adapter. This is that adapter.

It is deliberately a PROTOCOL adapter, not a provider adapter. ROUTING_EVALS.md states that Agent Stack does not hard-code any provider's CLI or API syntax,
because interfaces change and different operators use different frontends. So nothing here names a vendor: it speaks the OpenAI `/chat/completions` shape, which
Ollama, LiteLLM, DeepSeek, OpenRouter, Groq and others all expose. Point it somewhere with environment variables and it works; the vendor is configuration,
never code.

Usage — the evaluator supplies the prompt, so this is normally used as the `--command`:

    EVAL_BASE_URL=http://localhost:11434/v1 EVAL_MODEL=deepseek-r1:14b \\
        python scripts/evaluate_routing.py --command 'python scripts/eval_model_adapter.py' --limit 2

Environment:
    EVAL_BASE_URL   API root INCLUDING the version segment. Default http://localhost:11434/v1 (local Ollama).
    EVAL_MODEL      Model id as the endpoint names it. Required — there is no sensible default across providers.
    EVAL_API_KEY    Bearer token. Omit for local endpoints that do not authenticate.
    EVAL_TEMPERATURE  Default 0. Routing is a classification task; sampling only adds variance between runs.
    EVAL_TIMEOUT    Seconds, default 180. Reasoning models on local hardware are slow.
    EVAL_MAX_TOKENS Default 2048. Reasoning models spend a large share of the budget before emitting the answer.

Secrets are read from the environment and never written to disk or echoed. Keep the key in the gateway that already owns it rather than pasting it into a shell
command that lands in history.

Stdlib only, so it adds no dependency to the maintenance runtime.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request

# Reasoning models (the deepseek-r1 family, qwq, and others) emit their scratchpad inline before the answer. The evaluator tolerates surrounding noise only so
# far as it can still find a JSON object, and a think block frequently contains braces and draft JSON of its own — which is exactly what a naive extractor
# latches onto. Strip it here, where we know it is scratchpad, rather than hoping the extractor guesses right.
THINK_BLOCK = re.compile(r"<think\b[^>]*>.*?</think\s*>", re.DOTALL | re.IGNORECASE)
# An unterminated block means the model hit the token ceiling mid-reasoning; there is no answer after it to salvage.
UNCLOSED_THINK = re.compile(r"<think\b[^>]*>.*\Z", re.DOTALL | re.IGNORECASE)


def fail(message: str) -> None:
    print(f"eval_model_adapter: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    prompt = sys.stdin.read().strip()
    if not prompt:
        fail("no prompt on stdin")

    base_url = os.environ.get("EVAL_BASE_URL", "http://localhost:11434/v1").rstrip("/")
    model = os.environ.get("EVAL_MODEL")
    if not model:
        fail("EVAL_MODEL is not set — name the model exactly as the endpoint names it")

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": float(os.environ.get("EVAL_TEMPERATURE", "0")),
        "max_tokens": int(os.environ.get("EVAL_MAX_TOKENS", "2048")),
        "stream": False,
    }

    headers = {"Content-Type": "application/json"}
    api_key = os.environ.get("EVAL_API_KEY")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    timeout = int(os.environ.get("EVAL_TIMEOUT", "180"))
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        # The response body carries the provider's actual complaint (bad model id, no credit, bad key). Surfacing the status alone turns a five-second fix into
        # a debugging session.
        detail = exc.read().decode("utf-8", "replace")[:600]
        fail(f"HTTP {exc.code} from {base_url}: {detail}")
    except urllib.error.URLError as exc:
        fail(f"cannot reach {base_url}: {exc.reason}")
    except json.JSONDecodeError:
        fail(f"{base_url} returned a non-JSON response")

    try:
        content = body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        fail(f"unexpected response shape: {json.dumps(body)[:600]}")

    # Some endpoints split reasoning into its own field rather than inlining it; that half is never the answer.
    content = content or ""
    content = THINK_BLOCK.sub("", content)
    content = UNCLOSED_THINK.sub("", content)
    content = content.strip()

    if not content:
        fail(
            "model returned only reasoning and no answer — raise EVAL_MAX_TOKENS, or use a non-reasoning model for "
            "bulk runs"
        )

    print(content)
    return 0


if __name__ == "__main__":
    sys.exit(main())
