"""Optional local-model seam: one chat call to an OpenAI-compatible server (oMLX, LM Studio, Ollama's /v1), for kc verify only.

Imported, not run. Standard library only (urllib), so nothing is installed. The endpoint must be loopback unless the project config sets
verify.allow_remote, so claims stay on the machine by default; the model must be on verify.model_allowlist. The key comes from
KC_LLM_API_KEY and is never logged or returned. Every call has a timeout; any failure raises ModelError, and the caller records the pair
as uncertain, never as "no conflict" (research readme: report 1's fallback hid errors). Safety: sends claim text to the endpoint named.
"""

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

from . import settings
from .errors import InputError

LOOPBACK = ("127.0.0.1", "localhost", "::1")
_OBJECT = re.compile(r"\{.*\}", re.DOTALL)


class ModelError(Exception):
  """A model call failed or returned no usable JSON."""


def check_target(cfg: dict, model: str) -> str:
  """Endpoint for a model, after the allowlist and loopback checks.

  Args:
    cfg: the project config's verify block.
    model: model ID asked for.

  Returns:
    The endpoint base URL.

  Raises:
    InputError: the model is not allowlisted, or the endpoint is remote while allow_remote is off.
  """
  if model not in cfg["model_allowlist"]:
    raise InputError(f"model {model!r} is not on verify.model_allowlist in .kc/config.yaml")
  base = os.environ.get("KC_LLM_BASE_URL", cfg["endpoint"]).rstrip("/")
  host = urllib.parse.urlparse(base).hostname
  if host not in LOOPBACK and not cfg["allow_remote"]:
    raise InputError(f"endpoint host {host!r} is not loopback; set verify.allow_remote in .kc/config.yaml to send claims there")
  return base


def parse_object(text: str) -> dict:
  """The JSON object in a model reply, tolerating a code fence or leading words.

  Args:
    text: reply content.

  Returns:
    The object.

  Raises:
    ModelError: no JSON object in the text.
  """
  found = _OBJECT.search(text or "")
  try:
    obj = json.loads(found.group(0)) if found else None
  except json.JSONDecodeError as err:
    raise ModelError(f"reply is not JSON: {err}") from err
  if not isinstance(obj, dict):
    raise ModelError("reply holds no JSON object")
  return obj


def _headers() -> dict:
  """Request headers, with the bearer key when KC_LLM_API_KEY is set.

  Returns:
    Header dict (the key is never logged).
  """
  headers = {"Content-Type": "application/json"}
  key = os.environ.get("KC_LLM_API_KEY")
  if key:
    headers["Authorization"] = f"Bearer {key}"
  return headers


def list_models(base: str) -> list[str]:
  """Model IDs the server serves.

  Args:
    base: endpoint base URL (…/v1).

  Returns:
    IDs in server order.

  Raises:
    ModelError: transport error, timeout, HTTP error (401 without a key) or an unexpected body.
  """
  req = urllib.request.Request(f"{base}/models", headers=_headers())
  try:
    with urllib.request.urlopen(req, timeout=settings.LLM_LIST_TIMEOUT_S) as resp:
      return [m["id"] for m in json.load(resp)["data"]]
  except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError, KeyError, TypeError) as err:
    raise ModelError(f"model list failed: {type(err).__name__}: {getattr(err, 'reason', err)}") from err


def chat_json(base: str, model: str, system: str, user: str, max_tokens: int) -> tuple[dict, dict]:
  """One deterministic chat call that must answer with a JSON object.

  Args:
    base: endpoint base URL (…/v1).
    model: model ID.
    system: system prompt.
    user: user prompt.
    max_tokens: completion cap.

  Returns:
    (parsed object, usage dict from the server).

  Raises:
    ModelError: transport error, timeout, HTTP error or unusable reply.
  """
  body = {
    "model": model,
    "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
    "temperature": 0,
    "max_tokens": max_tokens,
    "response_format": {"type": "json_object"},
    "chat_template_kwargs": {"enable_thinking": False},
  }
  req = urllib.request.Request(f"{base}/chat/completions", data=json.dumps(body).encode(), headers=_headers())
  try:
    with urllib.request.urlopen(req, timeout=settings.LLM_TIMEOUT_S) as resp:
      out = json.load(resp)
  except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as err:
    raise ModelError(f"model call failed: {type(err).__name__}: {getattr(err, 'reason', err)}") from err
  try:
    content = out["choices"][0]["message"]["content"]
  except (KeyError, IndexError, TypeError) as err:
    raise ModelError("reply has no message content") from err
  usage = {k: out.get("usage", {}).get(k) for k in ("prompt_tokens", "completion_tokens")}
  return parse_object(content), usage
