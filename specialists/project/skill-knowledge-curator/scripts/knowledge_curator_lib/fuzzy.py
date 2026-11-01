"""RapidFuzz seam: near-duplicate similarity scores for candidate generation (never for truth adjudication).

Imported, not run. The only module that imports rapidfuzz. Upgrade test: tests/test_seams.py. Safety: pure functions.
"""

from rapidfuzz import fuzz, process


def similarity(a: str, b: str) -> float:
  """Token-set similarity of two texts, order-insensitive.

  Args:
    a: first text.
    b: second text.

  Returns:
    Score from 0 to 100, rounded to one decimal so output is stable.
  """
  return round(fuzz.token_set_ratio(a, b), 1)


def nearest(term: str, known: list[str], cutoff: float, subset: bool = False) -> str | None:
  """Closest known term at or above a similarity cutoff.

  Args:
    term: the term.
    known: terms to search.
    cutoff: minimum score, 0 to 100.
    subset: score by shared words, so a part of a line matches it; False compares whole terms, so "continuum" is not near "continuum portal".

  Returns:
    The best match, or None.
  """
  found = process.extractOne(term, known, scorer=fuzz.token_set_ratio if subset else fuzz.ratio, score_cutoff=cutoff)
  return found[0] if found else None
