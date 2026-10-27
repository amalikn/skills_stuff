"""RapidFuzz seam: near-duplicate similarity scores for candidate generation (never for truth adjudication).

Imported, not run. The only module that imports rapidfuzz. Upgrade test: tests/test_seams.py. Safety: pure functions.
"""

from rapidfuzz import fuzz


def similarity(a: str, b: str) -> float:
  """Token-set similarity of two texts, order-insensitive.

  Args:
    a: first text.
    b: second text.

  Returns:
    Score from 0 to 100, rounded to one decimal so output is stable.
  """
  return round(fuzz.token_set_ratio(a, b), 1)
