"""Error types and their exit codes for the Knowledge Curator.

Imported, not run. Each class carries the process exit code the front end returns for it (references/invocation-contract.md,
Exit codes). Safety: no side effects.
"""


class KcError(Exception):
  """Base class for every curator failure; exit code 6 (I/O, lock or unexpected state)."""

  exit_code = 6


class InputError(KcError):
  """Bad arguments, unreadable input file or a schema violation in agent input; exit code 1."""

  exit_code = 1


class ReviewNeeded(KcError):
  """The run finished but a human decision is pending; nothing was changed; exit code 2."""

  exit_code = 2


class ValidationFailed(KcError):
  """A deterministic gate failed; nothing was published; exit code 3."""

  exit_code = 3


class ConflictBlocker(KcError):
  """An open P0/P1 conflict blocks the requested promotion or archive plan; exit code 4."""

  exit_code = 4


class SourceChanged(KcError):
  """A source file changed since it was inventoried or approved; re-run inventory; exit code 5."""

  exit_code = 5


class WriteFailed(KcError):
  """A write, lock or restore test failed; the last good state is kept; exit code 6."""

  exit_code = 6
