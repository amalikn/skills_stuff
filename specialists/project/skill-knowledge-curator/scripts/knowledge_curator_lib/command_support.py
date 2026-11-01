"""Helpers shared by the command modules: decision time, batch rejection and the no-lock context for dry runs.

Imported, not run. Safety: writes nothing.
"""

import datetime as dt

from .errors import InputError, SourceChanged


def now() -> dt.datetime:
  """Current local time, timezone-aware.

  Returns:
    The time.
  """
  return dt.datetime.now().astimezone()


def reject(errors: list[str], changed: bool) -> None:
  """Fail an intake batch.

  Args:
    errors: messages.
    changed: a source changed under the batch.

  Raises:
    SourceChanged: when changed.
    InputError: otherwise.
  """
  msg = "batch rejected, nothing written:\n  " + "\n  ".join(errors)
  raise SourceChanged(msg) if changed else InputError(msg)


class Noop:
  """Context manager that does nothing (dry runs take no lock)."""

  def __enter__(self):
    """Enter.

    Returns:
      None.
    """
    return None

  def __exit__(self, *exc):
    """Exit without suppressing errors.

    Args:
      *exc: exception info.

    Returns:
      False.
    """
    return False
