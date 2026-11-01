---
Title: External research 3 - Status, lineage and an NLI gate
Category: research
Status: unverified
Authority: external; operator-supplied output of a web-research assistant, 2026-11-01; not checked by this pack
Scope: Candidate tools, models and algorithms for kc, kept verbatim for later review
Last reviewed: 2026-11-02
Summary: Ranks a status detector, an NLI gate, lineage grouping and ssbc conformal abstention; has build scripts and negative findings.
---

1. Ranked table: expected noise removed first, then recall, per unit of effort

Effort is estimated for one engineer familiar with the codebase. “Noise removed” means candidate conflicts suppressed or correctly downgraded before a human sees them. “Recall impact” is the risk to the 66.7% baseline.

Rank Candidate Noise removed per effort Recall impact Effort Evidence label Why it ranks here
1 Superseded/status banner detector (regex + YAML frontmatter) Very high. Directly targets the stated root cause of 10/11 false positives. Neutral to positive Very low (hours) VERIFIED_SECONDARY (phrases documented in multiple sources; no single tool) The user already knows the root cause. Exact phrases are documented: “superseded by”, “no longer recommended”, “use Y instead”, “legacy”, “retired”. Parsing frontmatter (status, supersedes, date) is trivial and needs no model.
2 NLI cross-encoder contradiction gate (cross-encoder/nli-deberta-v3-small or cavaquinho) High. Reported precision lift from ~16% (LLM-only) to ~89% on pairwise contradiction detection. Slight risk of recall loss if threshold is too aggressive; can be calibrated Medium (1–2 days) VERIFIED_PRIMARY for consistency-checker claim (PyPI page opened); model licence VERIFIED_PRIMARY The consistency-checker project explicitly reports the 16%→89% precision lift with an NLI gate. The model is Apache-2.0 and runs on Apple Silicon via MPS. This is the single highest-leverage change for precision.
3 Document version/date metadata + lineage grouping Medium-high. Groups many conflicts into one root cause; suppresses historical-vs-current noise. Positive (avoids reporting history as conflict) Low (hours to 1 day) VERIFIED_SECONDARY for GVD F1; frontmatter parsing is generic GVD reports F1 0.97 for version-family construction and 0.94 for rule-level consistency, fully local, no LLM. Even without GVD code, simple frontmatter/date extraction + grouping by document family and topic key achieves much of the benefit.
4 Conformal abstention (ssbc) Medium. Prevents wrong automatic resolutions; does not remove noise from the human queue but stops bad auto-decisions. Neutral Medium (1–2 days) VERIFIED_PRIMARY (PyPI page opened) SSBC provides PAC-valid conformal prediction with n=50 calibration sets, Mondrian per-class calibration, and Clopper–Pearson intervals. Exactly fits the “about 50 labels” constraint. MIT licence.
5 Claim normalisation (spaCy + coreferee) Medium. Reduces wording variation (the “1 of 245 topic keys shared” problem), improving candidate generation. Positive Medium (2–3 days) VERIFIED_SECONDARY (coreferee spaCy compatibility; Python 3.14 support uncertain) Coreferee works with spaCy 3.x, but Python 3.14 support is not confirmed. Entity linking would help, but the dependency risk is higher than the first four.
6 Truth discovery (truthdiscovery) Low-medium. Unsupervised source reliability could support automatic resolution, but the package is stale. Neutral Medium VERIFIED_SECONDARY (licence unclear; last release 2023) Last release v1.0.4, March 2023; licence listed as “None” on Socket. Not recommended as a core dependency.
7 Model routing (model-shunt, Lynkr) Low (cost saving, not noise removal). Neutral Low VERIFIED_SECONDARY (claims 90% token reduction) Useful for the 2.4M token problem, but does not improve precision or recall. Can be added after precision work.
8 Cleanlab confident learning Low. Designed for label noise in datasets, not for pairwise conflict detection. Neutral Medium VERIFIED_PRIMARY (v2.9.0, Apache-2.0, Python 3.10–3.14) Python 3.14 support is confirmed, but the algorithm assumes a classifier over examples, not a pairwise NLI setting. Not a first-line tool here.
9 GVD full framework High in theory, but no public code confirmed. Neutral High (weeks) VERIFIED_SECONDARY (paper only) Strong published F1, but not reproducible from the paper alone. Leave alone until code is released.

---

2. Top 3, with build scripts, inputs/outputs, packages, smallest test, runtime and token use

Top 1 — Superseded/status banner detector

What it does: Marks each Markdown source as current, superseded, historical, or unknown before any conflict is reported. Claims from a superseded file are downgraded to “historical” and never enter the human conflict queue as active conflicts.

Script to build: status_detector.py (standard library only; optional PyYAML for frontmatter).

```python
# status_detector.py — minimal, auditable
import json, re, sys
from pathlib import Path

STATUS_PATTERNS = [
    (r"\bsuperseded\s+by\b", "superseded"),
    (r"\bno\s+longer\s+recommended\b", "superseded"),
    (r"\buse\s+\S+\s+instead\b", "superseded"),
    (r"\brecommended\s+replacement\s+for\b", "superseded"),
    (r"\bretired\b", "superseded"),
    (r"\bdeprecated\b", "superseded"),
    (r"\blegacy\b", "historical"),
    (r"\barchived\b", "historical"),
    (r"\bhistorical\b", "historical"),
]

def scan_markdown(path: Path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    head = "\n".join(text.splitlines()[:12])  # banner zone
    status, evidence = "current", ""
    for pat, label in STATUS_PATTERNS:
        m = re.search(pat, head, re.I)
        if m:
            status, evidence = label, head[max(0, m.start()-40):m.end()+80]
            break
    # frontmatter override
    fm = re.match(r"^---\n(.*?)\n---", text, re.S)
    if fm:
        for line in fm.group(1).splitlines():
            if re.match(r"\s*status\s*:", line, re.I):
                val = line.split(":", 1)[1].strip().strip("\"'")
                if val in {"superseded", "deprecated", "historical", "archived"}:
                    status, evidence = val, line
                elif val in {"current", "active", "approved"}:
                    status, evidence = "current", line
    return {"file": str(path), "status": status, "evidence": evidence[:200]}

if __name__ == "__main__":
    root = Path(sys.argv[1])
    for p in sorted(root.rglob("*.md")):
        print(json.dumps(scan_markdown(p)))
```

Input: Directory of Markdown files, or a JSONL of claims with source_file.
Output: JSONL with file, status, evidence_span. This is a signal with an audit trail; the decision to suppress is logged by kc.
Exact package/model: Python standard library; optional PyYAML. No model, no server, fully offline.
Smallest test on labelled data: Manually label 10 files from the 24 audit reports as superseded or current. Run the script, compute precision/recall. Because the phrases are explicit, expect precision ≥ 0.95, recall ≥ 0.8 on files where a banner exists. If recall is low, add patterns from the misses.
Expected runtime and token use:

· 400 claims / ~24 files: < 1 second, 0 tokens.
· 3,500 claims / ~200 files: < 5 seconds, 0 tokens.

Risk/cost: Low. False negatives if a superseded banner uses unusual wording; mitigate by logging every file that has no status and reviewing a sample. No model drift.

---

Top 2 — NLI cross-encoder contradiction gate

What it does: Takes each candidate conflict pair (claim excerpt vs claim text) and computes a contradiction score with a cross-encoder NLI model. Pairs below a calibrated threshold are suppressed as noise; pairs above threshold proceed to the existing agent classification or human review.

Script to build: nli_gate.py

```python
# nli_gate.py — local cross-encoder gate
# pip install sentence-transformers
import json, sys
from sentence_transformers import CrossEncoder

MODEL = "cross-encoder/nli-deberta-v3-small"  # Apache-2.0
model = CrossEncoder(MODEL, device="mps")     # Apple Silicon; fallback "cpu"

def classify(pair):
    scores = model.predict([(pair["excerpt"], pair["claim"])], apply_softmax=True)[0]
    # label order for this model: contradiction, entailment, neutral
    return {
        "claim_id": pair["claim_id"],
        "conflict_id": pair["conflict_id"],
        "p_contradiction": float(scores[0]),
        "p_entailment": float(scores[1]),
        "p_neutral": float(scores[2]),
        "label": "contradiction" if scores[0] > 0.5 else "not_contradiction",
    }

if __name__ == "__main__":
    threshold = float(sys.argv[1]) if len(sys.argv) > 1 else 0.7
    for line in sys.stdin:
        pair = json.loads(line)
        out = classify(pair)
        out["gate_pass"] = out["p_contradiction"] >= threshold
        print(json.dumps(out))
```

Input: JSONL, one object per candidate pair: {"claim_id": "...", "conflict_id": "...", "excerpt": "...", "claim": "..."}.
Output: JSONL with p_contradiction, p_entailment, p_neutral, and gate_pass. kc logs gate_pass and the threshold in the audit ledger.
Exact package and model:

· sentence-transformers (Apache-2.0).
· Model cross-encoder/nli-deberta-v3-small (Apache-2.0). ~80 MB, CPU-friendly; first run downloads from Hugging Face.
· Alternative: cavaquinho (likely MIT, but verify) wraps claim decomposition and NLI; for a pure gate, sentence-transformers is simpler and has a confirmed licence.
  Fully offline: Yes, after model download. No Ollama, no server, no vector DB.
  Smallest test on labelled data: Use the 45 blind-labelled real conflicts plus 45 sampled false positives (or 50 labels total). Sweep thresholds from 0.3 to 0.9. At each threshold, compute precision and recall for “conflict” vs “noise”. Choose the threshold that gives the best precision at acceptable recall. Expected: the NLI gate will suppress a large fraction of the 243 open conflicts, with precision on the passed set substantially above the 27.5% baseline. The consistency-checker project reports 16%→89% precision on its corpus; your audit corpus may differ, so measure it.
  Expected runtime and token use (estimate):

Corpus size Candidate pairs (estimate) Runtime (M-series, MPS) Token use
400 claims ~200–400 pairs 5–15 s 0
3,500 claims ~1,500–3,000 pairs 30–90 s 0

If run on CPU only, expect 2–4× slower. The model is ~80 MB, not the 500 MB DeBERTa-large.
Risk/cost:

· Recall risk: The model may miss subtle contradictions in audit language; monitor recall on the 45 labelled conflicts and lower the threshold if recall drops.
· Label order: The model’s config.json must be checked; cross-encoder/nli-deberta-v3-small uses contradiction/entailment/neutral, but always verify with a probe pair.
· Audit trail: Log the model name, version, threshold, and raw scores with every suppression.

---

Top 3 — Document version/date metadata + lineage grouping

What it does: Extracts document_id, version, date, supersedes, and status from Markdown frontmatter or filenames. Groups claims into version families. Conflicts within the same family are reported as one root cause with the latest claim as the current position; conflicts across unrelated families remain separate.

Script to build: lineage_grouper.py (standard library only).

```python
# lineage_grouper.py — version-family grouping
import json, re, sys
from datetime import datetime
from pathlib import Path

def parse_meta(path: Path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    meta = {"document_id": path.stem, "version": None, "date": None, "supersedes": None}
    fm = re.match(r"^---\n(.*?)\n---", text, re.S)
    if fm:
        for line in fm.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                k, v = k.strip().lower(), v.strip().strip("\"'")
                if k in meta:
                    meta[k] = v
    # filename fallback: report_v2_2024-01-15.md
    m = re.search(r"v(\d+)", path.stem)
    if m and not meta["version"]:
        meta["version"] = m.group(1)
    m = re.search(r"(\d{4}-\d{2}-\d{2})", path.stem)
    if m and not meta["date"]:
        meta["date"] = m.group(1)
    return meta

def family_key(meta):
    return meta.get("document_id") or meta["document_id"]

if __name__ == "__main__":
    root = Path(sys.argv[1])
    metas = [parse_meta(p) for p in sorted(root.rglob("*.md"))]
    families = {}
    for m in metas:
        families.setdefault(family_key(m), []).append(m)
    for fam, docs in families.items():
        docs.sort(key=lambda x: (x.get("date") or "", x.get("version") or ""), reverse=True)
        print(json.dumps({"family": fam, "documents": docs, "latest": docs[0]}))
```

Input: Markdown directory, or a JSONL of claims with source_file.
Output: JSONL of version families, each with ordered documents and the latest document. kc uses this to attach a lineage_id to each claim and to group conflicts.
Exact package/model: Python standard library only. No model, no server, fully offline.
Smallest test on labelled data: On the 24 audit reports, manually identify which files belong to the same family (e.g., audit report v1, v2, final). Run the script and measure whether the family grouping matches. If frontmatter is absent, use filename patterns. Expected: for reports with clear version markers, grouping is exact; for unversioned reports, grouping is conservative (each file its own family).
Expected runtime and token use:

· 400 claims / 24 files: < 1 s, 0 tokens.
· 3,500 claims / ~200 files: < 3 s, 0 tokens.

Risk/cost: Low. If frontmatter is inconsistent, grouping may miss families. Log every family assignment and let a human confirm the first N families. This is reversible: a wrong grouping only changes the reporting order, not the claim ledger.

---

3. Build order

Ready now

1. Superseded/status banner detector — no dependencies, targets the known root cause, measurable in hours.
2. Document version/date metadata extractor — no dependencies, enables lineage grouping and time-evolution handling.
3. Lineage grouping — no dependencies, collapses many conflicts into one root cause.
4. NLI cross-encoder gate — install sentence-transformers, download cross-encoder/nli-deberta-v3-small (Apache-2.0), integrate as a pre-filter. This is the main precision lever.
5. Conformal abstention with ssbc — pip install ssbc (MIT). Calibrate the NLI gate’s scores on ~50 labels; use Mondrian conformal prediction to set per-class thresholds and abstain when the prediction set is not a singleton. This gives a measurable, reversible abstention policy.
6. Sample-based precision with Clopper–Pearson intervals — ssbc already provides clopper_pearson_intervals. Use it to report precision on any human-reviewed sample, with 95% intervals. For inter-rater agreement on the 50 labels, compute Cohen’s κ with a bootstrap CI (simple script, no new dependency).

Not ready

1. GVD full framework — strong published F1 (0.97 / 0.94), but no public code confirmed. Do not build until code is released.
2. Truth discovery (truthdiscovery) — licence listed as “None”, last release March 2023. Too stale and legally unclear for a core dependency.
3. Claim normalisation with coreferee — coreferee is tied to spaCy 3.x; Python 3.14 support is not confirmed. Test in an isolated venv before committing.
4. Model routing — model-shunt and similar tools claim up to 90% token reduction, but they are cost tools, not accuracy tools. Add only after precision is stable, and only if token cost remains a problem.
5. Cleanlab — excellent for label noise in datasets, but kc’s problem is pairwise conflict detection, not example labelling. It does not directly remove conflict noise.

---

4. What to leave alone, and why

· Vector databases. kc already has SQLite FTS5 + RapidFuzz. Adding a vector DB would add a daemon, increase dependency weight, and not address the root causes (superseded banners, scope differences, wording variation). Leave it alone unless candidate recall is proven to be the bottleneck after the NLI gate.
· Crawlers. The corpus is local Markdown. No crawler needed.
· Unbounded LLM reading of every document. The user’s own measurement says more LLM reading adds noise much faster than real findings. Do not increase LLM coverage; use the NLI gate to reduce the number of pairs that reach an LLM.
· Cloud LLM judges as the first stage. The consistency-checker project sends every chunk to a third-party LLM; that violates the “local first” constraint and leaks project text. The NLI stage is local and can run without the LLM judge. If an LLM judge is used later, it must be a local model and its output must be logged as a candidate, not a decision.
· Ollama / local server. The NLI cross-encoder runs in-process. There is no need for a separate Ollama server unless you later add a local LLM for adversarial review.
· Automatic resolution of P0 / safety / security conflicts. Keep these with a human, as the constraints require. Conformal abstention should be used to route them to a human, not to auto-resolve them.

---

5. Negative findings and what could not be verified

Negative findings

1. Off-the-shelf NLI is weak at document-level contract contradiction. ContractNLI reports contradiction F1 of only 0.357 for BERT-large and 0.360 for DeBERTa-v2-xlarge, versus entailment F1 of 0.834–0.855. This means NLI alone will not solve cross-document contradiction detection. It works best as a pairwise pre-filter, not as a standalone resolver.
2. The consistency-checker project’s own evaluation found near-zero useful yield for pairwise NLI+LLM on legal prose, even though the NLI gate lifted precision from ~16% to ~89%. The lesson: high precision on the pairs that pass does not mean many true conflicts will be found. Pairwise detection should be opt-in and measured on your corpus, not assumed to work.
3. truthdiscovery has no clear licence and has not been updated since 2023. Its last release is v1.0.4, March 2023, licence “None”. Do not adopt it for a production ledger without legal review.
4. GVD’s code is not publicly available. The paper claims F1 0.97 for version-family construction and 0.94 for rule-level consistency, fully local and without an LLM. Without code, these numbers are VERIFIED_SECONDARY only, and cannot be reproduced.
5. Coreferee’s Python 3.14 support is unverified. Coreferee requires spaCy 3.0–3.5.4, and spaCy’s Python 3.14 support is recent. Test in an isolated venv; do not make it a hard dependency until it passes.
6. The “1 of 245 topic keys shared” problem is a normalisation problem, not an NLI problem. No NLI model will fix it. Entity linking and canonicalisation are needed, but the available Python tools (spaCy + coreferee) carry Python 3.14 risk.

What I could not verify

· Cavaquinho’s exact licence. The PyPI page describes the package and its NLI behaviour, but the licence was not visible on the page I opened. Search results show MIT for a different project with the same name. Treat cavaquinho’s licence as VERIFIED_SECONDARY / likely MIT, and check pip show cavaquinho or the GitHub LICENSE file before adopting.
· Whether consistency-checker can run its NLI stage fully offline without the LLM judge. The NLI stage is local, but the tool is designed to send chunks to a cloud LLM for the second stage. The NLI gate itself can be extracted and run offline with sentence-transformers; the full tool does not meet the “local first” constraint.
· ContractNLI’s contradiction F1 on audit reports specifically. ContractNLI is contracts, not audit reports. The numbers above are evidence that document-level NLI is hard, but they are not a direct measurement on kc’s corpus. Measure on your own 50 labels.
· Exact precision/recall of cross-encoder/nli-deberta-v3-small on claim-vs-excerpt contradiction in audit language. The Japanese NLI benchmark shows a multilingual 279M model achieved zero false positives with a confidence threshold on 16 hand-labelled pairs, but that is a smoke test, not a benchmark. Your 50 labels are the right calibration set.
· GVD’s reproducibility. The paper is on arXiv (2609.17696) and reports strong F1, but no code repository was found. Do not treat the F1 numbers as deployable evidence.

Plain statement on “nothing beats an LLM reading the sources”

At 382 claims, an LLM reading all sources produced 243 open conflicts and 2.4M tokens, with 27.5% precision. The evidence above says the cheapest first move is not a better LLM reader; it is deterministic status/lineage filtering plus a local NLI gate. Those two changes require zero LLM tokens, run offline, and directly target the two measured root causes: superseded banners and noisy candidate pairs. Whether they beat an LLM reader on recall cannot be known until you run them on your 45 labelled conflicts, but on noise removed per unit of effort, they are the clear winners.
