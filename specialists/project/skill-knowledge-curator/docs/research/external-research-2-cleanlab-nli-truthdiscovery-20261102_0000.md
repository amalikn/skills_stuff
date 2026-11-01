---
Title: External research 2 - Cleanlab, NLI and truth discovery
Category: research
Status: unverified
Authority: external; operator-supplied output of a web-research assistant, 2026-11-01; not checked by this pack
Scope: Candidate tools, models and algorithms for kc, kept verbatim for later review
Last reviewed: 2026-11-02
Summary: Ranks cleanlab first, then cross-encoder NLI and status rules, and truthdiscovery for resolution; lists DocChecker.
---

Ranked candidates by expected noise removal first, then recall gain, per unit of effort. Evidence is drawn only from primary sources opened or cross-checked (GitHub, PyPI, arXiv/HTML papers, docs). Numbers are as published; no invented benchmarks.
1. Ranked table (noise removed / effort)
Rank
Candidate
Primary target
Expected noise impact (evidence)
Effort / risk
Evidence label
1
cleanlab (confident learning) + scikit-learn calibration
Noise probability / filtering candidates before human; precision of “is this a real conflict?” signal
High precision label-issue detection on classification tasks (paper reports exact identification under conditions; tutorial numbers e.g. precision ~0.72 / recall ~0.88 on example filter_by). Works with ~50 labels via cross-val pred_probs. Directly attacks the 27.5% precision and “more LLM reading adds noise” problem.
Low: pure Python, pip, offline, Apple Silicon native. Optional heavier models for embeddings.
VERIFIED_PRIMARY (GitHub cleanlab/cleanlab, v2.9.0 2026-01, Apache-2.0 post-acquisition; Python 3.10–3.14; docs + JAIR 2021 paper)
2
sentence-transformers CrossEncoder NLI (e.g. cross-encoder/nli-deberta-v3-, dleemiller/finecat-nli-)
Filtering candidate pairs + cross-doc contradiction signal
Strong published NLI accuracy (SNLI/MNLI ~90%+ range for DeBERTa-v3 variants; FineCat reports ~0.82 accuracy / calibrated probs). Filters “same topic different wording” and scope mismatches before human.
Medium: local torch/transformers; offline after download; Apple Silicon via MPS/CPU. Separate venv recommended for torch.
VERIFIED_PRIMARY (HF model cards, sbert.net docs)
3
Document-status / temporal heuristics + RapidFuzz / FTS5 signals (already in kc) + simple rules
Superseded / versioned / banner noise; time-evolution
Directly addresses the dominant measured noise (“superseded” banner, earlier-vs-later). No model needed. High precision possible with exact string / metadata matches.
Very low.
VERIFIED_SECONDARY (user-measured root cause; standard techniques)
4
truthdiscovery (Python library)
Automatic resolution via source reliability / truth finding
Implements classic algorithms (TruthFinder, Sums, Investment, etc.). Outputs trust + believed values with audit trail. Useful when multiple sources claim the same object.
Low–medium: pure Python, but last release 1.0.4 (2023), GPL-3.0, low activity.
VERIFIED_PRIMARY (PyPI + readthedocs)
5
ContractNLI-style document NLI / Span NLI BERT patterns
Cross-document + legal/audit-style conflicts
Original paper: Span NLI BERT ~0.875 Acc / F1(E) 0.834 on ContractNLI. Later open LLMs reach ~81% Acc zero-shot. Useful for long-form audit reports.
Medium–high (fine-tune or large local LLM). Code not always fully FOSS-ready.
VERIFIED_SECONDARY (arXiv 2110.01799 + follow-ups)
6
DocChecker (ACM PODS 2026 graph-based contradiction system)
Cross-document entity/relation conflicts
Reported average F1 0.900 (up to 0.935) on real documents; scales in parallel; beats GPT-4o on long-range.
High: graph extraction + rules; code link is anonymous/4open (not fully verified public FOSS package).
VERIFIED_SECONDARY (ACM abstract + arXiv-linked claims)
7
Stanford OpenIE / pure-Python ports (triplet-extract, stanford-openie-python)
Claim normalisation / canonicalisation
Produces (subject, relation, object) triples. Helps topic-key sharing problem (only 1/245 shared).
Medium: Java dependency for classic; pure-Python ports exist. Maintenance varies.
VERIFIED_PRIMARY (GitHub + CoreNLP docs)
8
scikit-learn CalibratedClassifierCV (Platt / isotonic)
Per-finding calibrated probabilities
Standard, well-documented. Platt better for small calibration sets (~50–100); isotonic needs more.
Very low.
VERIFIED_PRIMARY (scikit-learn docs)
Nothing in the search beat a carefully prompted local LLM reading the exact source excerpts at this corpus size (24 docs / 382 claims) for final adjudication of ambiguous scope or authority cases. All above are filters or signals with audit trails, not unlogged decisions.
2. Top 3 – concrete build details
1. cleanlab for noise filtering / confident “is-conflict” scores
	•	Script outline: Extract candidate pairs → obtain out-of-sample pred_probs from any classifier (or LLM-as-classifier with temperature sampling) that scores “real conflict vs noise” → cleanlab.filter.find_label_issues or Datalab → rank/prune high-noise candidates → log confident_joint + reason.
	•	Input: feature vectors or embeddings of claim pairs + binary/noisy labels (or soft scores).
	•	Output: ranked list of probable label issues + joint noise distribution; never auto-resolves P0.
	•	Package: cleanlab 2.9.0 (2026-01-13), Apache-2.0. Optional: scikit-learn for Platt.
	•	Smallest test: 40–50 of the blind-labelled conflicts + equal noise samples; measure precision of “issue” flag vs human.
	•	Runtime / tokens: CPU seconds–minutes for 400 claims; negligible extra tokens. Scales linearly to 3 500. Offline, Apple Silicon fine, no separate server.
	•	Likely gain: directly attacks the measured 27.5% precision and the 10/11 root-cause cluster.
2. Local CrossEncoder NLI filter
	•	Script: For every FTS5/RapidFuzz candidate pair, run CrossEncoder.predict([(claim_a, claim_b)]) → keep only high contradiction probability (or high contradiction + low entailment). Log scores + model version.
	•	Input/Output: claim text pairs → (contradiction, entailment, neutral) probs + decision threshold.
	•	Exact models: cross-encoder/nli-deberta-v3-base or dleemiller/finecat-nli-ultra-l / finecat-nli-l (Apache-2.0 / MIT variants; calibrated probs reported). sentence-transformers latest.
	•	Smallest test: same 40–50 labelled + noise sample; report precision/recall of contradiction class.
	•	Runtime: ~1 500 pairs/s on modern GPU; CPU/MPS acceptable for 400 claims (seconds–minutes). Tokens: 0 after model download. Offline. Separate venv for torch recommended.
	•	Gain: reduces “worded differently” and scope-mismatch noise; improves cross-file recall when paired with better retrieval.
3. Temporal / status + truthdiscovery hybrid for resolution
	•	Script: Parse Markdown for “superseded”, version headers, dates; mark historical claims. For multi-source objects use truthdiscovery.Dataset + TruthFinder / Sums → output most-believed value + source trust scores. Log everything; human overrides.
	•	Package: truthdiscovery 1.0.4 (2023-03, GPL-3.0). Pure Python.
	•	Test: the 45 real conflicts that are time/authority; measure how many are auto-resolved correctly and reversibly.
	•	Runtime: negligible. Tokens: 0.
	•	Gain: attacks the measured within-file / time-evolution / authority gaps and the dominant “superseded banner” noise.
3. Build order
Ready now (days–1 week)
	1	cleanlab + Platt/isotonic on existing agent classifications or a small supervised “conflict vs noise” head.
	2	CrossEncoder NLI filter on the current SQLite FTS5 / RapidFuzz candidate queue.
	3	Explicit superseded / version / date rules (regex + front-matter) before any model.
	4	Log every filter decision with model/version/threshold.
Not ready / higher cost
	•	Full DocChecker-style graph extraction + rule discovery (code availability incomplete).
	•	Heavy fine-tuning of document-level NLI on ContractNLI-style data unless you already have GPU time.
	•	OpenIE as core (helps normalisation but does not solve conflict precision by itself).
	•	Any cloud model (violates local-first).
4. What to leave alone
	•	Vector databases or daemons as core requirements (explicit constraint).
	•	Unlogged automatic resolution of P0 / safety claims.
	•	Heavy multi-agent adversarial review loops that multiply tokens (measured problem: more LLM reading adds noise faster than findings).
	•	Claiming “solved” cross-file recall without improving retrieval + NLI calibration first.
	•	Anything that treats agent-generated topic keys as canonical without normalisation (only 1/245 shared).
5. Negative findings & unverified items
	•	No FOSS package was found that simultaneously delivers high precision and high cross-file recall on a 24-document audit-style corpus out of the box.
	•	DocChecker (PODS 2026) reports excellent F1 but the public code link is anonymous/4open; full offline FOSS readiness not verified.
	•	truthdiscovery is correct and FOSS but essentially unmaintained since 2023.
	•	Many “knowledge-base guardian” / multi-agent GitHub repos exist; most are demos, use vector DBs, or call paid APIs.
	•	ContractNLI numbers are for legal contracts, not audit reports; transfer is plausible but unmeasured here.
	•	No published precision/recall on exactly “superseded banner vs real conflict” was located; the root-cause analysis is user-measured.
	•	At 382 claims, a strong local LLM that is forced to quote the exact source excerpt and abstain when scope differs remains competitive; none of the above replace it for the residual hard cases.
All recommendations produce only candidates or calibrated signals with full audit trails. Automatic resolution is limited to cases where a source explicitly settles the fact and the decision is reversible.
