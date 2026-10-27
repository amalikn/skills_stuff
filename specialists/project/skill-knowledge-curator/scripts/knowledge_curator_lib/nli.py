"""Optional sentence-transformers seam: a natural-language-inference contradiction score used only to rank candidate pairs.

Imported, not run. sentence-transformers (and torch) are not in requirements.txt; install requirements-nli.txt to enable this.
When the package or model is missing, available() is False and callers skip the signal. NLI labels are heuristics, weak on time,
version and environment scope; a score never selects a truth (design doc 2.3, 7.1 step 6). Safety: the first use downloads the
model named in KC_NLI_MODEL from Hugging Face; nothing else leaves the machine.
"""

import functools
import importlib.util
import os

DEFAULT_MODEL = "cross-encoder/nli-deberta-v3-small"
LABELS = ("contradiction", "entailment", "neutral")


def available() -> bool:
  """Whether sentence-transformers is importable.

  Returns:
    True when the optional dependency is installed.
  """
  return importlib.util.find_spec("sentence_transformers") is not None


@functools.cache
def _model():
  """Load the cross-encoder once.

  Returns:
    A sentence_transformers.CrossEncoder.
  """
  from sentence_transformers import CrossEncoder

  return CrossEncoder(os.environ.get("KC_NLI_MODEL", DEFAULT_MODEL))


def contradiction_scores(pairs: list[tuple[str, str]]) -> list[float] | None:
  """Contradiction probability for each text pair.

  Args:
    pairs: (premise, hypothesis) texts.

  Returns:
    One score in [0, 1] per pair (rounded to 3 places), or None when the optional dependency is absent.
  """
  if not pairs or not available():
    return None
  import numpy as np

  logits = np.asarray(_model().predict(pairs))
  probs = np.exp(logits) / np.exp(logits).sum(axis=1, keepdims=True)
  return [round(float(p[LABELS.index("contradiction")]), 3) for p in probs]
