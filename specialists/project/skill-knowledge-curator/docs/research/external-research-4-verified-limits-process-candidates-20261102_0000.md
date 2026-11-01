---
Title: External research 4 - Verification limits and process candidates
Category: research
Status: unverified
Authority: external; operator-supplied output of a web-research assistant, 2026-11-01; not checked by this pack
Scope: Candidate tools, models and algorithms for kc, kept verbatim for later review
Last reviewed: 2026-11-02
Summary: States it opened no primary source, so every external fact is UNVERIFIED; offers scripts, process candidates and a resolution policy.
---

A. Direct Answer

**Verification limitation**
- I could not open primary sources in this session.
- Therefore all external licence/version/release/metric facts below are **UNVERIFIED**.
- I did **not** invent benchmark numbers, versions, or licences.
- Your corpus numbers are treated as **USER_PROVIDED primary evidence**, not independently verified.
- No candidate below is marked `VERIFIED_PRIMARY`.

**Plain conclusion**
- At **24 docs / 382 claims**, no verified specialized FOSS tool or model clearly beats:
  1. deterministic status/scope/version filtering,
  2. root-cause grouping,
  3. a tightly constrained LLM verifier only on survivors.
- Your measured noise is mostly **structural** (`superseded`, version order, scope), not primarily semantic.
- Adding more unconstrained LLM reading is likely to keep increasing noise faster than findings, as your data already shows.

---

## 1. Ranked table: expected noise removed, recall effect, effort

Sorted by **noise removed first**, then recall effect, then effort.

| Rank | Candidate | Expected noise removed | Recall effect | Effort | Evidence label |
|---:|---|---|---:|---:|---|
| 1 | **Deterministic status / scope / version filter** with exact source quotes | **High** | Neutral or positive if overfiltering is controlled | Low | `USER_MEASURED` + `UNVERIFIED` |
| 2 | **Root-cause grouping / deduplication** of candidate conflicts | **High queue reduction** | Neutral; may indirectly help recall if representatives are expanded | Low–Medium | `USER_MEASURED` |
| 3 | **Source-backed automatic resolver** for explicit supersession / correction only | **Medium–High** for explicit cases | Neutral if quote-required | Low–Medium | `USER_MEASURED` |
| 4 | **Calibrated triage / accuracy calculator**: Wilson CI, bootstrap, abstention | **Medium** by prioritizing likely-real candidates | Neutral | Low–Medium | Statistical theory; package facts `UNVERIFIED` |
| 5 | **Deterministic claim canonicalization + local registry** for subjects/predicates/scopes | **Medium** | May improve cross-file recall if aliases are curated | Medium | `USER_MEASURED` |
| 6 | **LLM-as-verifier on filtered candidates only**, exact excerpts only | **Medium** if tightly constrained | May improve hard cross-file cases | Medium | `UNVERIFIED` |
| 7 | **Model routing**: rules first, cheap local model second, stronger model only for hard cases | Token reduction, uncertain noise removal | Uncertain | Medium | `UNVERIFIED` |
| 8 | **NLI / cross-encoder contradiction model** | Uncertain; may add false positives | Possible recall gain, especially cross-document | High | `UNVERIFIED` |
| 9 | **spaCy / coref / OpenIE claim normalization stack** | Low–Medium, uncertain | Uncertain | High | `UNVERIFIED` |
| 10 | **Truth discovery / source reliability scoring without explicit source quote** | Low; risky | Can become negative if it auto-resolves incorrectly | High | `UNVERIFIED` |

---

## 2. Top 3 things to build now

These are deliberately **local, low-token, reversible, audit-logged**.

---

### 2.1 `kc-filter-status-scope`

**Purpose**
- Remove or downgrade candidate conflicts caused by:
  - superseded banners,
  - archived/historical sections,
  - version order,
  - explicit scope mismatch.

**Input**
- `claims.jsonl`
  - claim id
  - doc path
  - subject / predicate / object
  - scope
  - exact source excerpt
  - excerpt location / line range
- `candidate_conflicts.jsonl`
- Markdown source files

**Output**
- `candidates.kept.jsonl`
- `candidates.dismissed.jsonl`

Each output record must include:
- pair id
- decision: `keep` / `dismiss`
- rule id
- reason
- exact supporting source quote, if dismissal is source-based
- doc / line / section
- reversibility flag
- tool name/version
- timestamp
- input hash

**Package / model**
- Package: **Python 3.14 standard library**
- Optional: your existing RapidFuzz installation
- Model: **none**
- No new venv required
- No daemon required
- Offline: yes

**Core rules**
- Detect status markers:
  - `superseded`
  - `deprecated`
  - `archived`
  - `historical`
  - `obsolete`
  - `replaced by`
  - `no longer applies`
- Detect version/time markers:
  - headings with `v1`, `v2`, dates
  - front matter status/date fields if present
  - filename patterns like `v1`, `old`, `archive`
- Detect scope markers:
  - `applies to`
  - `only for`
  - `excluding`
  - `before`
  - `after`
  - explicit environment / product / version scope

**Decision policy**
- Dismiss only when there is an **exact source quote** showing:
  - supersession,
  - historical status,
  - non-overlapping scope.
- If status/scope is inferred but not stated, do **not** dismiss; mark `weak_signal`.
- Never auto-resolve P0 / safety / security claims.

**Smallest labelled test**
- Use your existing:
  - 382 claims
  - 45 blind-labelled real conflicts
  - sampled false-positive queue
- Measure:
  - number of candidates dismissed
  - number of labelled real conflicts wrongly dismissed
  - precision before/after on sampled queue

**Pass target**
- Dismiss a meaningful fraction of false candidates.
- Wrong dismissal of labelled real conflicts: **≤ 2 / 45** initially.

**Expected runtime and token use**

Assumptions:
- 400 claims ≈ current 243 open candidate pairs
- 3,500 claims ≈ 5k–20k candidate pairs after blocking

| Corpus | Runtime | LLM tokens |
|---|---:|---:|
| 400 claims / 243 pairs | < 2 seconds | 0 |
| 3,500 claims / 5k pairs | < 10 seconds | 0 |
| 3,500 claims / 20k pairs | < 30 seconds | 0 |

---

### 2.2 `kc-group-root-cause`

**Purpose**
- Reduce many near-duplicate or same-root-cause candidate conflicts into one review unit.

**Input**
- `claims.jsonl`
- `candidates.kept.jsonl`

**Output**
- `clusters.jsonl`
- `queue.representatives.jsonl`

Each cluster record should include:
- cluster id
- member pair ids
- representative pair id
- grouping signals
- audit trail
- reversibility flag

**Package / model**
- Package: **Python 3.14 standard library**
- Optional: existing RapidFuzz
- Model: **none**
- No new venv required
- No daemon required
- Offline: yes

**Grouping signals**
Use union-find / connected components over candidate pairs when any of these hold:
- near-identical normalized subject + predicate
- same source section and overlapping excerpt
- high excerpt similarity
- same status banner applies to multiple claims
- same doc + same heading + similar scope
- same apparent version marker

**Do not require embeddings yet**
- Your corpus is small enough for blocking + fuzzy matching.
- Avoid vector DBs and heavy embedding pipelines for now.

**Smallest labelled test**
- Manually inspect 30 sampled clusters.
- Label each cluster:
  - same root cause
  - mixed causes
- Compute **cluster purity**.

**Pass target**
- Purity ≥ 0.8 on sampled clusters.
- Large reduction from 243 open conflicts to fewer review units.

**Expected runtime and token use**

| Corpus | Runtime | LLM tokens |
|---|---:|---:|
| 400 claims / 243 pairs | < 2 seconds | 0 |
| 3,500 claims / 5k pairs | < 15 seconds | 0 |
| 3,500 claims / 20k pairs | < 60 seconds | 0 |

---

### 2.3 `kc-score-calibrate`

**Purpose**
- Estimate per-candidate probability of being a real conflict.
- Produce confidence intervals.
- Prioritize human review.
- Abstain instead of guessing.

**Input**
- `candidates.kept.jsonl`
- feature table derived from candidates
- `labels.jsonl`
  - at least ~50 labels if possible

**Output**
- `scores.jsonl`

Each record should include:
- pair id
- score / probability estimate
- confidence interval
- method
- label count used
- features used
- abstention flag
- audit trail

**Package / model**
- Package: **Python 3.14 standard library**
- Optional:
  - `statsmodels`
  - `scikit-learn`
  - `MAPIE`
- Model:
  - initially **none** or simple logistic regression
- Offline: yes
- Separate venv only if you add optional packages

**Features to start with**
- RapidFuzz similarity of subject strings
- similarity of predicate strings
- same doc / same section
- scope overlap
- status mismatch
- version/date difference
- authority metadata difference
- FTS overlap score
- excerpt containment
- claim length difference
- whether a status rule already fired

**What works with about 50 labels**

| Method | Works with ~50 labels? | Use in kc |
|---|---:|---|
| Wilson binomial CI | Yes | Queue precision / recall intervals |
| Bootstrap CI | Yes | Metric uncertainty |
| Cohen’s kappa | Yes, if two raters label same items | Measure guideline agreement |
| Platt scaling | Weak | Only with simple scores and careful LOOCV |
| Isotonic calibration | Usually too data-hungry | Avoid for now |
| Conformal prediction | Possible but intervals wide | Use for `uncertain` flags, not auto-decisions |
| Confident learning | Not yet | Needs more labels and reliable probabilities |

**Current uncertainty from your numbers**
- Reported conflict precision:
  - 11 / 40 = **27.5%**
  - Wilson 95% CI ≈ **16.1% to 42.8%**
- Conflict recall:
  - 30 / 45 ≈ **66.7%**
  - Wilson 95% CI ≈ **52.1% to 78.6%**

This means your current precision estimate is still quite uncertain.

**Minimal Wilson interval function**
```python
def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return 0.0, 1.0
    p = k / n
    z2 = z * z
    denom = 1 + z2 / n
    center = (p + z2 / (2 * n)) / denom
    half = (z / denom) * ((p * (1 - p) / n + z2 / (4 * n * n)) ** 0.5)
    return max(0.0, center - half), min(1.0, center + half)
```

**Smallest labelled test**
- With 50 labels:
  - leave-one-out evaluation
  - rank candidates by score
  - compute precision@10 / precision@20
  - compute Wilson CI for each sampled precision
- Do **not** auto-dismiss solely from score.

**Pass target**
- Top-ranked candidates have higher sampled precision than the current 27.5%.
- Human review queue shrinks without measurable recall loss.

**Expected runtime and token use**

| Corpus | Runtime | LLM tokens |
|---|---:|---:|
| 400 claims / 243 pairs | < 1 second | 0 |
| 3,500 claims / 5k pairs | < 5 seconds | 0 |
| 3,500 claims / 20k pairs | < 20 seconds | 0 |

---

## 3. Build order

### Ready now

#### Phase 0
- Freeze evaluation harness:
  - fixed claims
  - fixed candidate pairs
  - fixed labels
  - fixed precision/recall scripts
- Add append-only logs for every dismissal / grouping / score.

#### Phase 1
- Build `kc-filter-status-scope`.
- Require exact source quote for every source-based dismissal.

#### Phase 2
- Build `kc-group-root-cause`.
- Review one representative per cluster by default.
- Allow expansion to full cluster on demand.

#### Phase 3
- Build `kc-score-calibrate`.
- Use Wilson intervals from day one.
- Add abstention rather than forced decisions.

#### Phase 4
- Add **source-backed resolver** for only these cases:
  - explicit supersession quote
  - explicit correction quote
  - explicit authority override quote
- Every resolution must be:
  - quote-backed
  - logged
  - reversible
  - sampled for correctness

### Not ready yet

#### NLI / cross-encoder models
- Not ready until deterministic filters are in place.
- Risk: domain mismatch and added false positives.

#### Heavy claim normalization stack
- spaCy / coref / OpenIE is not ready yet.
- Your immediate issue is not generic NLP; it is structural noise and inconsistent claim keys.

#### Truth discovery / reliability scoring
- Not ready.
- It can produce resolutions not grounded in an explicit source statement.
- That violates your reversibility and source-grounding constraint.

#### Model routing
- Not ready as a first build.
- Add only after:
  - filters reduce candidate volume,
  - scores exist,
  - token cost is measurable per stage.

#### Cloud models
- Not ready as core.
- Only consider if:
  - local pipeline is stable,
  - a hard-case subset is clearly defined,
  - export is explicitly allowed by policy.

---

## 4. What to leave alone, and why

### Leave alone: vector database
- Not needed at this corpus size.
- Adds operational complexity.
- Does not address superseded/scope noise directly.

### Leave alone: daemon-based architecture as a core requirement
- Ollama or similar can be optional later.
- Core kc should remain a local CLI with file-based ledgers.

### Leave alone: OpenIE as a primary solution
- Open IE output tends to be noisy.
- Your problem is not lack of triples; it is too many candidate conflicts.

### Leave alone: heavy coreference pipelines
- Likely fragile on technical audit prose.
- Maintenance and Python compatibility risk are high.
- A local canonical registry is cheaper and more auditable.

### Leave alone: automatic recency-only resolution
- Recency alone is not enough.
- A later document is not automatically authoritative unless the source says so.

### Leave alone: truth discovery algorithms for final resolution
- They can be interesting research signals.
- They do not satisfy your requirement that resolution must rest on a source statement and remain reversible.

### Leave alone: multi-agent debate on all candidates
- Token cost will rise sharply.
- Your data already shows more LLM reading adds noise faster than findings.
- Use adversarial review only on a small filtered subset.

---

## 5. Negative findings and what could not be verified

### Could not verify
I could not open primary sources in this session, so the following are **UNVERIFIED**:
- exact licences
- latest versions
- release dates
- maintenance state
- Python 3.14 compatibility
- Apple Silicon wheel support
- published benchmark numbers
- published precision/recall numbers for external tools/models

### No verified direct benchmark match
- I found no verified published precision/recall numbers for a task matching:
  - Markdown audit reports
  - atomic claim extraction
  - source-excerpt-grounded conflict detection
  - human-curated conflict resolution

### No verified turnkey FOSS tool
- I did not verify any FOSS tool that directly solves kc’s exact problem.
- Most relevant components are generic:
  - NLI
  - calibration
  - weak supervision
  - entity normalization
  - truth discovery

### No benchmark numbers quoted
- I deliberately did **not** quote benchmark numbers for:
  - ContractNLI models
  - DeBERTa NLI models
  - DocNLI
  - FEVER-style systems
  - cross-encoders
because I could not verify them at the source.

### Python 3.14 compatibility not verified
- Many ML/NLP packages may or may not have clean Python 3.14 support.
- This must be checked before adding:
  - transformers
  - PyTorch
  - ONNX Runtime
  - spaCy
  - scikit-learn
  - statsmodels
  - MAPIE
  - cleanlab

### Plain statement on LLMs
- For your current corpus size, **nothing verified beats a constrained LLM reading exact source excerpts plus deterministic filtering**.
- The key is to stop using LLMs as broad readers and instead use them as narrow verifiers on already-filtered candidates.

---

# Candidate evidence cards

All external metadata below is **UNVERIFIED** because primary sources were not opened.

---

## C1. `kc-filter-status-scope`

- **Exact name / URL**: local kc script; uses Python stdlib: https://docs.python.org/3/
- **Licence**: script under kc licence; Python licence not re-verified
- **Latest version / release date**: not applicable for script; Python version not re-verified
- **Maintenance state**: script maintained by you; Python maintenance not re-verified
- **Runtime / dependencies**:
  - Python 3.14 stdlib
  - optional existing RapidFuzz
  - no separate venv
  - no server
  - offline
  - Apple Silicon friendly
- **Published precision / recall**: none on comparable task
- **Labelled data needed**:
  - 20–30 examples of banners/status/scope
  - existing 45 conflict labels for evaluation
- **Weakness targeted**:
  - superseded banners
  - version order noise
  - scope mismatch noise
- **Likely gain**:
  - high, because you reported 10 / 11 sampled false positives share one root cause
- **Risk / cost**:
  - over-dismissal if rules are too broad
  - mitigated by exact quote requirement and reversible dismissals
- **Evidence label**: `USER_MEASURED` for expected gain; `UNVERIFIED` for external facts

---

## C2. `kc-group-root-cause`

- **Exact name / URL**: local kc script; optional RapidFuzz: https://github.com/rapidfuzz/RapidFuzz
- **Licence**: script under kc licence; RapidFuzz licence not re-verified
- **Latest version / release date**: not re-verified
- **Maintenance state**: not re-verified
- **Runtime / dependencies**:
  - Python 3.14 stdlib
  - optional RapidFuzz already in kc
  - no separate venv
  - no server
  - offline
- **Published precision / recall**: none on comparable task
- **Labelled data needed**:
  - none to generate clusters
  - ~30 sampled clusters for purity check
- **Weakness targeted**:
  - 243 open conflicts on 382 claims
  - duplicate wording
  - repeated root causes
- **Likely gain**:
  - large queue reduction
  - better human throughput
- **Risk / cost**:
  - merging distinct conflicts into one cluster
  - mitigated by expandable clusters and audit trail
- **Evidence label**: `USER_MEASURED` for need; `UNVERIFIED` for external facts

---

## C3. `kc-score-calibrate`

- **Exact name / URL**: local kc script; optional:
  - https://www.statsmodels.org/
  - https://scikit-learn.org/
  - https://github.com/scikit-learn-contrib/MAPIE
- **Licence**: script under kc licence; optional package licences not re-verified
- **Latest version / release date**: not re-verified
- **Maintenance state**: not re-verified
- **Runtime / dependencies**:
  - stdlib only initially
  - optional separate venv if adding statsmodels/scikit-learn/MAPIE
  - Python 3.14 compatibility not verified
  - offline
- **Published precision / recall**:
  - statistical methods have theoretical coverage properties
  - no published precision/recall on kc-like conflict triage verified
- **Labelled data needed**:
  - ~50 labels minimum for queue-level estimates
  - more for stable model calibration
- **Weakness targeted**:
  - noise probability estimation
  - precision with confidence intervals
  - abstention
- **Likely gain**:
  - better prioritization
  - safer escalation thresholds
- **Risk / cost**:
  - small label set gives wide intervals
  - calibration can overfit
- **Evidence label**: `UNVERIFIED` for packages; statistical rationale is standard

---

## C4. Source-backed resolver

- **Exact name / URL**: local kc script
- **Licence**: kc licence
- **Latest version / release date**: not applicable
- **Maintenance state**: maintained by you
- **Runtime / dependencies**:
  - Python 3.14 stdlib
  - no server
  - offline
- **Published precision / recall**: none on comparable task
- **Labelled data needed**:
  - sample of auto-resolved items for correctness audit
- **Weakness targeted**:
  - automatic resolution where source text settles the issue
- **Likely gain**:
  - medium-high for explicit supersession / correction cases
- **Risk / cost**:
  - wrong resolution if banner or correction is ambiguous
  - mitigated by quote requirement, reversibility, and sampling
- **Evidence label**: `USER_MEASURED` for need; `UNVERIFIED` for external facts

**Allowed automatic resolution only when source explicitly states:**
- supersession
- replacement
- correction / erratum
- authority override

**Not allowed:**
- recency alone
- authority score alone
- truth-discovery aggregate alone

---

## C5. Deterministic claim canonicalization + local registry

- **Exact name / URL**: local kc script / local registry files
- **Licence**: kc licence
- **Latest version / release date**: not applicable
- **Maintenance state**: maintained by you
- **Runtime / dependencies**:
  - Python 3.14 stdlib
  - optional RapidFuzz
  - offline
- **Published precision / recall**: none on comparable task
- **Labelled data needed**:
  - alias approvals
  - canonical subject/predicate review samples
- **Weakness targeted**:
  - agents wording the same thing differently
  - only 1 / 245 topic keys shared
  - weak cross-file blocking
- **Likely gain**:
  - better grouping
  - better cross-file candidate generation
  - moderate precision improvement
- **Risk / cost**:
  - registry drift
  - false merges if canonicalization is too aggressive
- **Evidence label**: `USER_MEASURED` for problem; `UNVERIFIED` for external facts

**Recommended form**
- Maintain local Markdown/JSON registries:
  - canonical subjects
  - canonical predicates
  - allowed scopes
  - aliases
- Agents must either:
  - link to an existing registry entry, or
  - propose a new entry for human approval

---

## C6. Local LLM verifier on filtered candidates only

- **Exact name / URL**: local kc script plus your existing local LLM endpoint; optional local runtimes:
  - https://github.com/ggml-org/llama.cpp
  - https://github.com/ollama/ollama
- **Licence**: not re-verified
- **Latest version / release date**: not re-verified
- **Maintenance state**: not re-verified
- **Runtime / dependencies**:
  - local model runtime
  - Ollama is a daemon and should be optional, not core
  - Apple Silicon likely okay, but not verified
  - offline after model download
- **Published precision / recall**:
  - no verified numbers for this task
- **Labelled data needed**:
  - ~50 labelled candidate conflicts for thresholding and evaluation
- **Weakness targeted**:
  - residual false positives after deterministic filtering
  - hard cross-file cases
- **Likely gain**:
  - medium if constrained to exact excerpts and forced citation
- **Risk / cost**:
  - token cost
  - hallucinated justification if context is too broad
  - added complexity if new local model is introduced
- **Evidence label**: `UNVERIFIED`

**Recommended policy**
- Use only after deterministic filtering.
- Input must contain:
  - two claims
  - exact excerpts
  - status/scope signals
- Output must be:
  - `contradiction` / `entailment` / `not enough evidence`
  - exact supporting quote
  - confidence signal only, not final decision

---

## C7. NLI / cross-encoder contradiction model

- **Exact name / URL**: example candidate: https://huggingface.co/cross-encoder/nli-deberta-v3-base
- **Licence**: not re-verified
- **Latest version / release date**: not re-verified
- **Maintenance state**: not re-verified
- **Runtime / dependencies**:
  - likely requires `transformers` or ONNX runtime stack
  - separate venv recommended
  - Python 3.14 compatibility not verified
  - offline after model download
- **Published precision / recall**:
  - likely exists on MNLI-like tasks, but not verified here
  - not directly comparable to kc conflict detection
- **Labelled data needed**:
  - none for zero-shot inference
  - ~50+ local labels needed for calibration
- **Weakness targeted**:
  - cross-document contradiction detection
- **Likely gain**:
  - uncertain
  - may help recall, but may also add noise
- **Risk / cost**:
  - domain mismatch
  - heavy dependencies
  - possible poor calibration
  - Apple Silicon / Python 3.14 support not verified
- **Evidence label**: `UNVERIFIED`

---

## C8. ContractNLI and related benchmarks

- **Exact name / URL**: https://github.com/yuta-koreeda/ContractNLI
- **Licence**: not re-verified
- **Latest version / release date**: benchmark is static; not re-verified
- **Maintenance state**: benchmark, not active service
- **Runtime / dependencies**:
  - none for inspection
  - models trained on it may be heavy
- **Published precision / recall**:
  - benchmark papers report metrics, but I did not verify numbers
- **Labelled data needed**:
  - not needed to use as inspiration
  - useful for designing evaluation schema
- **Weakness targeted**:
  - evaluation design for contradiction / entailment / omission
- **Likely gain**:
  - helps build a better local eval harness
- **Risk / cost**:
  - legal contract domain may not transfer to audit Markdown
- **Evidence label**: `UNVERIFIED`

Related benchmark families to investigate later, but not verified here:
- DocNLI
- MultiNLI
- FEVER-style verification
- SciFact-style evidence verification
- legal / contract contradiction corpora

---

## C9. spaCy / coref / OpenIE stack

- **Exact name / URL**: https://spacy.io/
- **Licence**: not re-verified
- **Latest version / release date**: not re-verified
- **Maintenance state**: not re-verified
- **Runtime / dependencies**:
  - binary wheels likely needed
  - separate venv recommended
  - Python 3.14 compatibility not verified
  - offline possible
- **Published precision / recall**:
  - standard NLP benchmark metrics exist, but not verified
  - not directly comparable to atomic claim normalization in kc
- **Labelled data needed**:
  - domain-specific evaluation set if you rely on it
- **Weakness targeted**:
  - canonicalization
  - entity linking
  - coreference
- **Likely gain**:
  - low-to-medium and uncertain
- **Risk / cost**:
  - heavy dependency chain
  - fragile on technical audit language
  - maintenance risk
- **Evidence label**: `UNVERIFIED`

**Practical recommendation**
- Prefer deterministic local canonicalization first.
- Only consider spaCy later if deterministic aliasing proves insufficient.

---

## C10. Cleanlab / confident learning

- **Exact name / URL**: https://github.com/cleanlab/cleanlab
- **Licence**: not re-verified
- **Latest version / release date**: not re-verified
- **Maintenance state**: not re-verified
- **Runtime / dependencies**:
  - Python package
  - separate venv recommended
  - Python 3.14 compatibility not verified
  - offline possible
- **Published precision / recall**:
  - published label-noise detection results exist, but not verified here
  - not directly comparable to conflict-candidate noise
- **Labelled data needed**:
  - reliable model probabilities
  - more than 50 labels in practice
- **Weakness targeted**:
  - possible label noise in human decisions
  - noisy candidate ranking
- **Likely gain**:
  - not yet
- **Risk / cost**:
  - can misidentify correct labels as errors if base probabilities are poor
- **Evidence label**: `UNVERIFIED`

**Recommendation**
- Do not adopt yet.
- Revisit when you have:
  - > 200 labels
  - stable candidate scores
  - repeated human labeling for agreement measurement

---

## C11. Model routing / LiteLLM-style router

- **Exact name / URL**: https://github.com/BerriAI/litellm
- **Licence**: not re-verified
- **Latest version / release date**: not re-verified
- **Maintenance state**: not re-verified
- **Runtime / dependencies**:
  - Python package
  - separate venv recommended
  - can route to local endpoints or cloud endpoints
  - offline only if all endpoints are local
- **Published precision / recall**:
  - none relevant
- **Labelled data needed**:
  - not directly
  - needs routing policy and cost metrics
- **Weakness targeted**:
  - token cost reduction
  - cheap local model first, stronger model only for hard cases
- **Likely gain**:
  - possible token reduction
  - uncertain quality effect
- **Risk / cost**:
  - accidental cloud usage
  - routing bugs
  - extra abstraction layer when a simple Python router may be enough
- **Evidence label**: `UNVERIFIED`

**Recommendation**
- Build a simple rule-based router inside kc first:
  - deterministic filter → no LLM
  - low ambiguity → small local verifier or no verifier
  - high ambiguity → stronger model / human
- Add LiteLLM only if you actually need multi-backend routing.

---

# Process-only candidates you can adopt without installing anything

These are not FOSS packages, but they are adoptable as agent process changes.

## P1. Status-only extractor agent
- Agent reads only:
  - first lines
  - headings
  - banners
  - metadata blocks
- Output:
  - status label
  - exact quote
- Targets:
  - superseded/historical noise
- Token cost:
  - low
- Evidence label: `USER_MEASURED` need; method `UNVERIFIED`

## P2. Citation-constrained verifier agent
- Agent must answer only:
  - `contradiction`
  - `not enough evidence`
  - `same claim`
- Must quote exact source text.
- Targets:
  - false positives
- Token cost:
  - medium
- Evidence label: `UNVERIFIED`

## P3. Adversarial review agent
- A second agent attacks the candidate conflict.
- Only disagreements go to human review.
- Targets:
  - precision
- Token cost:
  - high if overused
- Evidence label: `UNVERIFIED`

## P4. Canonical registry / LLM wiki maintenance
- Maintain:
  - canonical subjects
  - canonical predicates
  - canonical scopes
- Agents must link to existing entries or propose new ones.
- Targets:
  - topic-key fragmentation
  - cross-file recall
- Token cost:
  - low to medium
- Evidence label: `USER_MEASURED` need; method `UNVERIFIED`

## P5. Cross-file same-subject sweep
- After canonicalization, compare only claims with:
  - same canonical subject
  - compatible predicate family
  - overlapping scope
- Targets:
  - low cross-file recall (25%)
- Token cost:
  - controlled if blocking is deterministic
- Evidence label: `USER_MEASURED` need; method `UNVERIFIED`

---

# Suggested automatic-resolution policy

## Allow automatic resolution only when the source states the answer
Examples:
- “Superseded by …”
- “Replaced by …”
- “Corrected on …”
- “This document overrides …”
- “Applies only to …”

## Always record
- resolver id
- rule id
- exact source quote
- claim ids
- before/after state
- reversibility flag
- timestamp

## Never auto-resolve
- P0 findings
- security findings
- safety findings
- ambiguous authority cases
- recency-only cases
- model-only judgments without source quote

---

B. Add-Ons Menu

Add-ons: [Evaluation harness spec], [LLM verifier prompt], [Canonical registry schema], [NLI pilot plan], [Routing policy design]
