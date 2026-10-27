"""GoalGuard's own error types; seams translate library and HTTP failures into these (skill-coder errors-and-timeouts).

Imported, not run. Front ends map them to exit codes: RecordError and ConfigError exit 2, everything else exits 1.
"""


class GoalGuardError(Exception):
  """Base class for every error GoalGuard raises on purpose."""


class ConfigError(GoalGuardError):
  """A setting or argument is missing or malformed (for example no Vikunja URL); the message names the setting."""


class RecordError(GoalGuardError):
  """A .gg/ record, proposal, snapshot or task file cannot be read or fails validation."""


class WriteRefused(GoalGuardError):
  """A write was requested but a precondition failed (not a clean instance, partial export, broken hash chain)."""


class VikunjaError(GoalGuardError):
  """A Vikunja call failed; carries the HTTP status (0 when no answer) and the path that was called.

  Args:
    message: what was being done and what went wrong.
    status: HTTP status code, or 0 when the server did not answer.
    path: API path that was called, without the base URL or token.
  """

  def __init__(self, message: str, status: int = 0, path: str = ""):
    """Store the status and path beside the message.

    Args:
      message: what was being done and what went wrong.
      status: HTTP status code, or 0 when the server did not answer.
      path: API path that was called.
    """
    super().__init__(message)
    self.status = status
    self.path = path


class VikunjaUnreachable(VikunjaError):
  """No answer within the timeout, or the connection was refused."""


class VikunjaAuthRejected(VikunjaError):
  """401 or 403: the token is missing, expired or lacks the permission."""


class VikunjaNotFound(VikunjaError):
  """404: the project or task does not exist, or the token cannot see it."""


class VikunjaConflict(VikunjaError):
  """409 or 412: a concurrent change; never retried as last-write-wins."""
