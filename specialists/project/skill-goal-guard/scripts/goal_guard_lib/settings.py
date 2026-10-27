"""Run-time settings for GoalGuard, read from the environment in one place (skill-coder configuration-and-literals).

Imported, not run. No deployment literal lives in code: the Vikunja URL and token come from the environment; the defaults below are
policy values (timeouts, windows), not addresses.

Inputs (environment):
  GG_VIKUNJA_URL         base URL of the Vikunja instance, e.g. http://localhost:3456 (the API path /api/v2 is added)
  GG_VIKUNJA_TOKEN       API token (tk_...), read from the secret store by the operator; never logged or printed
  GG_HTTP_TIMEOUT        seconds per HTTP call (default 10)
  GG_GIT_TIMEOUT         seconds per git subprocess (default 10)
  GG_PARTITION           the partition (apn or me) this session is authorised for; unset means the project's own
  GG_DEADLINE_DAYS       days ahead that count as deadline pressure (default 14)
  GG_VERDICT_MAX_HOURS   age after which a PROCEED verdict no longer covers edits in the hook (default 2)
  GG_DATA_DIR            durable data peer (default /Volumes/Data/_ai/_skills/skills-data/skill-goal-guard)
  GG_RUNTIME_DIR         runtime peer for hook captures and logs (default /Volumes/Data/_ai/_skills/skills-runtime/skill-goal-guard)
"""

import os
from dataclasses import dataclass
from pathlib import Path

from .errors import ConfigError

API_PATH = "/api/v2"
PARTITIONS = ("apn", "me")


@dataclass(frozen=True)
class Settings:
  """Resolved settings for one run.

  Args:
    vikunja_url: base URL without a trailing slash, or "" when unset.
    vikunja_token: API token, or "" when unset; never printed.
    http_timeout: seconds per HTTP call.
    git_timeout: seconds per git subprocess.
    partition: authorised partition, or "" for the project's own.
    deadline_days: days ahead that count as deadline pressure.
    verdict_max_hours: hours a PROCEED verdict covers edits in the hook.
    data_dir: durable data peer.
    runtime_dir: runtime peer.
  """

  vikunja_url: str
  vikunja_token: str
  http_timeout: float
  git_timeout: float
  partition: str
  deadline_days: int
  verdict_max_hours: float
  data_dir: Path
  runtime_dir: Path

  def require_vikunja(self) -> None:
    """Fail early when a Vikunja call is needed but the URL or token is not set.

    Raises:
      ConfigError: GG_VIKUNJA_URL or GG_VIKUNJA_TOKEN is unset, naming which.
    """
    if not self.vikunja_url:
      raise ConfigError("GG_VIKUNJA_URL is not set (for example http://localhost:3456)")
    if not self.vikunja_token:
      raise ConfigError("GG_VIKUNJA_TOKEN is not set: read a read-only token from KeePassXC into the environment for this shell")


def _number(env: dict, name: str, default: float) -> float:
  """Read a positive number from the environment.

  Args:
    env: the environment mapping.
    name: variable name.
    default: value when the variable is unset or empty.

  Returns:
    The parsed number.

  Raises:
    ConfigError: the value is not a positive number.
  """
  raw = env.get(name, "")
  if raw == "":
    return default
  try:
    value = float(raw)
  except ValueError as err:
    raise ConfigError(f"{name}={raw!r} is not a number") from err
  if value <= 0:
    raise ConfigError(f"{name} must be positive, got {raw}")
  return value


def load(env: dict | None = None) -> Settings:
  """Build Settings from the environment.

  Args:
    env: mapping to read instead of os.environ (tests pass a dict).

  Returns:
    The resolved Settings.

  Raises:
    ConfigError: a numeric setting is malformed or GG_PARTITION is not apn or me.
  """
  env = dict(os.environ) if env is None else env
  partition = env.get("GG_PARTITION", "")
  if partition and partition not in PARTITIONS:
    raise ConfigError(f"GG_PARTITION must be one of {PARTITIONS}, got {partition!r}")
  return Settings(
    vikunja_url=env.get("GG_VIKUNJA_URL", "").rstrip("/"),
    vikunja_token=env.get("GG_VIKUNJA_TOKEN", ""),
    http_timeout=_number(env, "GG_HTTP_TIMEOUT", 10),
    git_timeout=_number(env, "GG_GIT_TIMEOUT", 10),
    partition=partition,
    deadline_days=int(_number(env, "GG_DEADLINE_DAYS", 14)),
    verdict_max_hours=_number(env, "GG_VERDICT_MAX_HOURS", 2),
    data_dir=Path(env.get("GG_DATA_DIR", "/Volumes/Data/_ai/_skills/skills-data/skill-goal-guard")),
    runtime_dir=Path(env.get("GG_RUNTIME_DIR", "/Volumes/Data/_ai/_skills/skills-runtime/skill-goal-guard")),
  )
