---
Title: External research 5 - Source context and root cause
Category: research
Status: unverified
Authority: external; operator-supplied output of a web-research assistant, 2026-11-02; not checked by this pack
Scope: Candidate tools, models and algorithms for kc, kept verbatim for later review
Last reviewed: 2026-11-02
Summary: Source-context and root-cause gates first, a measuring harness and retrieval shadow next, NLI in shadow mode only; the most detailed of the five, with a source register and test fixtures.
---

kc Knowledge Curator — Evidence-Based FOSS Research and Implementation Report

Research cut-off: 2026-11-01
Target: Local Python 3.14 CLI on Apple Silicon (M2 Max, 64 GB); Markdown evidence; append-only JSONL; SQLite FTS5; RapidFuzz
Decision: Build deterministic source-context and conservative root-cause gates first; evaluate local NLI only in shadow mode.
Evidence discipline: Primary references are linked inline; results from other domains are never represented as measured kc performance.

Executive decision

At 382 claims, 24 short audit reports and 45 blind-labelled real conflicts, no reviewed tool has demonstrated that it will outperform a strong LLM given the right source passages and status context. The strongest immediate proposition is to fix what the system asks the LLM to judge, not increase the amount of text consumed or install a new knowledge database.

Build now:

1. kc_source_context.py: record source status, applicable section, valid time, scope, explicit supersession/authority evidence; classify obvious history/scope noise without destroying the original finding.
2. kc_root_cause_rollup.py: group repeated findings with shared proven cause so one human decision can cover a reviewed group, with independent member records and reversibility.
3. kc_eval.py: sample, stratify, track pair-level versus root-level metrics, Wilson intervals, miss accounting and reviewer agreement.
4. kc_retrieval_shadow.py: compare controlled aliases and character n-gram TF–IDF against current FTS5/RapidFuzz for the missed cross-file and authority cases.

Shadow-test later: kc_nli_shadow.py, with MiniLM NLI and an optional stronger DeBERTa FEVER/ANLI model, after source-context handling is stable. Only enable a model filter if held-out, root-disjoint review shows it is safe.

Do not adopt as a core requirement: vector DB, daemon, crawler, LangChain agent, graph database, heavyweight knowledge-graph platform, self-training truth-discovery engine, or cloud LLM. Optional local models must use a separate environment. Cloud verification would transmit project source text and is not justified by current evidence.

1. Measured problem and measurement traps

|Reported observation         |Value                        |Interpretation                                                                                        |
|-----------------------------|----------------------------:|------------------------------------------------------------------------------------------------------|
|Corpus                       |24 Markdown audit reports    |Small enough for exact, local source-context parsing.                                                 |
|Extracted claims             |382                          |A claim-count metric, not independent samples for statistical evaluation.                             |
|Blind-labelled real conflicts|45                           |Approximately 30 found at 66.7% recall, assuming the reported recall denominator is all 45.           |
|Overall conflict recall      |66.7%                        |About 15 missed.                                                                                      |
|Within-file recall           |87.5%                        |Relatively stronger; do not prioritise another broad within-file scan.                                |
|Time-evolution recall        |73%                          |Dates and version transitions still require evidence checks.                                          |
|Authority recall             |50%                          |Two separate problems: candidate discovery and source precedence.                                     |
|Cross-file recall            |25%                          |Primary *recall* gap; likely retrieval/identity issue.                                                |
|Earlier reported precision   |11/40 = 27.5%                |**Not** proven precision of the current 243-item queue.                                               |
|Dependence among true results|10 of 11 share one root cause|Human decision count must be measured separately from positive pair count.                            |
|Open conflict records        |243                          |Pair count may overstate independent unresolved issues.                                               |
|LLM usage                    |~2.4 million tokens          |~6,283 tokens per extracted claim, averaged across the entire workflow, **not** per conflict judgment.|
|Topic-key overlap            |1 shared key among 245       |Keys generated independently by agents are not a reliable join key.                                   |

Precision uncertainty. The Wilson 95% interval for 11/40 is approximately 16.1–42.8%, if the 40 sampled findings are independent observations from a defensible sampling design. Root-cause correlation violates that simplistic independence assumption; the interval is only an illustrative baseline. Future estimates should sample independent root groups (or use cluster bootstrap and disclose its limits).

Recall uncertainty. The set of 45 labelled positives may be reusable for regression; that does not make it a trustworthy training/test split if prompts, heuristics or thresholds are repeatedly tuned on it. Preserve an untouched or prospectively labelled evaluation group.

Do not multiply a published benchmark percentage by 243 to predict removed noise. Published benchmark accuracy is not expected kc precision, and a source-context rule’s effect must be observed in kc’s own labels.

Concrete audit-document failure mode

The supplied audit reports show the reason to prioritise document interpretation:

• step4-post-fix-compliance-audit.md begins with an explicit Superseded Notice and then preserves statements from a historical point in the migration, including a then-present legacy compatibility symlink.
• step12-optional-hardening-final-state.md identifies itself as CURRENT AUTHORITATIVE and states that /Volumes/Data/_ai/mcp-data is retired/absent, and Step11 is superseded.
• audit-report-index.md provides the chronology, historical/current taxonomy, and supporting-document statuses; step13-audit-source-hygiene-and-publishable-pack.md confirms the authoritative reader path.

These are not necessarily contradictions. If one report truthfully described an earlier state and another describes a later state, the pair can represent documented evolution. If Step4 and Step12 both asserted mutually exclusive facts for the same effective time and scope, a genuine contradiction could remain. This distinction is determined by evidence spans and applicability, not by the word “superseded” alone.

The file evidence is a worked example of the reported failure class, not an independently rerun or labelled kc benchmark.

2. Ranking — expected noise removed first, then recall per unit of effort

Ranks are engineering priorities, not measured effect sizes. “Expected” means evidence-aligned mechanism and expected usefulness, not a claimed percentage reduction.

|Rank|Candidate                                                              |First objective                               |Relative effort                             |Evidence for benefit                                                                              |Main risk                                                    |Action                           |
|---:|-----------------------------------------------------------------------|----------------------------------------------|--------------------------------------------|--------------------------------------------------------------------------------------------------|-------------------------------------------------------------|---------------------------------|
|1   |Document/section status + effective-time/scope gate                    |Remove false *unresolved* conflicts           |Low–medium                                  |Direct match to observed banners, history and scope noise; Markdown examples confirm the structure|Incorrectly treating valid historical conflicts as irrelevant|Build; reversible dispositions   |
|2   |Root-cause grouping with validated cause signatures                    |Reduce **human decisions**                    |Low–medium                                  |10/11 sampled positives share a root; graph/group primitives are simple                           |Transitive overmerging                                       |Build conservative groups        |
|3   |Evaluation and sample-precision calculator                             |Make gains/misses measurable                  |Low                                         |Wilson/binomial calculations; established agreement metrics                                       |Misleading certainty on tiny clustered sample                |Build in parallel                |
|4   |Controlled claim alias map + character n-gram TF–IDF reranking         |Cross-file/authority recall                   |Low–medium                                  |FTS5/lexical gap and 1/245 topic-key agreement; classic IR method                                 |More low-quality candidates                                  |Shadow compare against baseline  |
|5   |Source-backed explicit supersession/authority resolution suggestions   |Safely resolve source-settled cases           |Medium                                      |Documents declare their own authoritative status in the supplied corpus                           |Wrong authority or stale policy                              |Build after context gate         |
|6   |Local NLI (MiniLM; optional DeBERTa)                                   |Cheap candidate verification                  |Medium–high                                 |NLI benchmark accuracy on other corpora; FEVER-style evidence model                               |Domain shift; temporal/scope errors                          |Shadow only                      |
|7   |CLAIRE/WikiCollide process and challenge labels                        |Cross-document method and trace quality       |Low for process, very high for full software|EMNLP 2025 corpus-level study                                                                     |Published implementation uses external retrieval/LLM         |Adopt **process**, not full stack|
|8   |MiniCheck support verification                                         |Detect claim unsupported by its cited evidence|High                                        |EMNLP 2024 grounded fact-checking results                                                         |Not pairwise conflict resolution; model size                 |Optional experiment              |
|9   |SummaC segmentation method                                             |Localising relevant evidence for NLI          |Low method / medium implementation          |74.4% *balanced accuracy* in summarisation benchmark                                              |Task mismatch, older package                                 |Borrow segmentation only         |
|10  |AlignScore                                                             |Support/consistency score comparator          |High                                        |22 factual-alignment datasets                                                                     |Old dependency constraints; not contradiction-specific       |Defer                            |
|11  |spaCy / GLiNER / coreference / OpenIE                                  |More robust cross-agent claim identity        |Medium–high                                 |General entity-extraction research                                                                |Incorrect entity merges and extra dependencies               |Defer until alias rules measured |
|12  |Learned truth discovery, Cleanlab, isotonic/Platt, conformal abstention|Automatic reliability score/decision          |High relative to label data                 |Research exists, but assumptions not met with ~50 labels                                          |Overconfidence, provenance laundering                        |Do **not** deploy                |

The immediate objective is not “suppress as many pairs as possible.” It is “minimise human decisions on non-issues subject to preserving genuine, discoverable conflicts.”

3. Source-checked FOSS and model inventory

The following inventory records licence, exact public version/release date where verified, runtime, offline behaviour, fit, labels, published accuracy and weakness. “No comparable result” is a deliberate result: kc is not a standard NLI, summarisation, Wikipedia or contract-classification benchmark.

Evidence label rules:

• VERIFIED_PRIMARY: author/maintainer PyPI page, code repository, model card, or primary paper accessed during this research.
• VERIFIED_SECONDARY: credible third-party report, but no direct primary confirmation. No critical recommendation below relies solely on this tier.
• UNVERIFIED: no defensible verification of the stated claim. Unverified components cannot be promoted automatically.
• For a method rather than distributed software, version is N/A; the paper’s publication year is not a package release.
• Python 3.14 support claimed by a package is not equivalent to passing an end-to-end Apple Silicon test of that model.

3.1 Lightweight, core-compatible libraries

|Exact name / source                                               |Latest checked version, release                   |Licence (primary)|Dependencies and local fit                                                                                                                                   |Published comparable precision/recall|Labels; cost/risk; target                                                                                              |Evidence        |
|------------------------------------------------------------------|--------------------------------------------------|-----------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------|-----------------------------------------------------------------------------------------------------------------------|----------------|
|[markdown-it-py](https://pypi.org/project/markdown-it-py/)        |**4.2.0**, 2026-05-07                             |MIT              |Python >=3.10; platform-independent wheel, CommonMark tokens; offline; no daemon; 3.14 classification absent but source/wheel suitable for compatibility test|**None** for status interpretation   |0 to parse, ~24 status labels for evaluation; headings and banner regions; parser output line-mapping must be validated|VERIFIED_PRIMARY|
|[python-frontmatter](https://pypi.org/project/python-frontmatter/)|**1.3.0**, 2026-05-20                             |MIT              |Python >=3.10; pure Python wheel; offline, no server                                                                                                         |None                                 |0 if frontmatter is explicitly present; unknown content cannot be “inferred” from package                              |VERIFIED_PRIMARY|
|[dateparser](https://pypi.org/project/dateparser/1.4.3/)          |**1.4.3**, 2026-09-03 (**corrects earlier 1.4.2**)|BSD-3-Clause     |Python >=3.10, explicitly classifies 3.14; small Python dependencies; offline; reference date must be supplied                                               |None                                 |0 to parse; annotate ambiguous dates; timezone and relative-date mistakes are consequential                            |VERIFIED_PRIMARY|
|[NetworkX](https://pypi.org/project/networkx/3.7/)                |**3.7**, 2026-09-21                               |BSD-3-Clause     |Python >=3.12 **except 3.14.1**; pure Python; offline; optional because DSU in stdlib is enough                                                              |None                                 |0; verified graph groupings; bad edge semantics cause wrong merges                                                     |VERIFIED_PRIMARY|
|[RapidFuzz](https://pypi.org/project/RapidFuzz/)                  |**3.14.6**, 2026-08-30                            |MIT              |C++ Python extension, macOS wheels; offline; already in kc                                                                                                   |None for contradictions              |0; use to discover aliases, **not** assert identity or contradiction                                                   |VERIFIED_PRIMARY|
|[scikit-learn](https://pypi.org/project/scikit-learn/1.9.1/)      |**1.9.1**, 2026-09-10                             |BSD-3-Clause     |Python >=3.11; CPython 3.14, macOS ARM64 wheels; NumPy/SciPy/joblib/threadpoolctl; offline; **optional venv**                                                |None for audit conflicts             |0 for TF–IDF; labelled positives/negatives to tune retrieval thresholds; risk is recall/precision trade-off            |VERIFIED_PRIMARY|
|[statsmodels](https://pypi.org/project/statsmodels/0.15.0/)       |**0.15.0**, 2026-08-27                            |BSD-3-Clause     |Compiled statistics stack, macOS ARM64/3.14 support; offline; **not needed** to compute Wilson interval                                                      |Not applicable                       |40+ independent samples preferred for estimates, more for narrow uncertainty; core uses `math`                         |VERIFIED_PRIMARY|
|[Pydantic](https://pypi.org/project/pydantic/2.14.2/)             |**2.14.2**, 2026-10-29                            |MIT              |Python 3.14 support; native `pydantic-core`; offline                                                                                                         |Not applicable                       |Schema validation only; no gain in semantic consistency if kc already validates events                                 |VERIFIED_PRIMARY|

Maintenance status: markdown-it-py, python-frontmatter, dateparser, NetworkX, RapidFuzz, scikit-learn, statsmodels and Pydantic all have verified 2026 releases. They are maintained; maintained does not mean appropriate for kc.

3.2 Inference libraries and local NLI models

|Exact name / URL                                                                                                   |Version, date or checkpoint                                  |Licence                                                                              |Runtime, deps, offline and local fit                                                                                                           |Published measurements **and what they mean**                                                                                   |Required kc labels; risk                                                                                                         |Evidence                                                                            |
|-------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------|-------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
|[Transformers](https://pypi.org/project/transformers/5.22.1/)                                                      |**5.22.1**, 2026-10-30                                       |Apache-2.0                                                                           |Python >=3.11, 3.14 declared; tokenizers and optional Torch/SentencePiece; offline after cache; optional venv; no Ollama                       |Library; no benchmark                                                                                                           |None for loading; risk: old checkpoint/model implementation compatibility                                                        |VERIFIED_PRIMARY                                                                    |
|[PyTorch](https://pypi.org/project/torch/2.15.0/)                                                                  |**2.15.0**, 2026-10-28                                       |BSD-style upstream; PyPI composite SPDX expression includes Apache/BSD/MIT and others|Python >=3.11; **CPython 3.14/macOS ARM64 wheel confirmed**; CPU/MPS trial required; offline; ~139 MB wheel, plus deps; no daemon              |Library; no benchmark                                                                                                           |None; memory and MPS operator compatibility                                                                                      |VERIFIED_PRIMARY                                                                    |
|[ONNX Runtime](https://pypi.org/project/onnxruntime/1.31.1/)                                                       |**1.31.1**, 2026-10-26                                       |MIT                                                                                  |Python >=3.11, 3.14/macOS ARM64 supported; offline; optional alternative inference backend                                                     |No kc benchmark                                                                                                                 |Need compatible model ONNX artefacts, export accuracy test, optional venv; not a daemon                                          |VERIFIED_PRIMARY                                                                    |
|[cross-encoder/nli-MiniLM2-L6-H768](https://huggingface.co/cross-encoder/nli-MiniLM2-L6-H768/tree/main)            |**Model revision `b95119c`** (short SHA; no semantic release)|Apache-2.0 model card                                                                |~82M parameters; 328 MB safetensors; Torch or published ONNX alternatives; offline after local snapshot; MPS execution not measured            |**No comparable kc precision or recall.** SNLI/MultiNLI classification training is only task-adjacent                           |45 positives plus independently labelled negatives to compare; domain/time/scope transfer risk; freeze full SHA before deployment|VERIFIED_PRIMARY                                                                    |
|[MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli](https://huggingface.co/MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli)|Unnumbered checkpoint; **immutable full SHA not yet checked**|MIT model card                                                                       |~base-scale Transformer; PyTorch, Transformers, SentencePiece; offline after snapshot; Python 3.14 integration and MPS behaviour **unverified**|Model card: **90.3% MNLI-m accuracy; 77.7% FEVER-NLI accuracy; 57.9% ANLI-all accuracy**—**not** audit conflict precision/recall|kc-specific labels needed for threshold; risk: logical contradiction with incompatible time/scope                                |VERIFIED_PRIMARY (model, figures); UNVERIFIED (full checkpoint SHA and 3.14 runtime)|

Critical implementation detail: use each model’s config.id2label rather than assuming a shared numeric label order. The DeBERTa model card documents entailment / neutral / contradiction in its example. Evaluate premise/hypothesis in both directions; append raw logits and normalised label scores, never convert softmax directly into “probability of an actionable kc conflict.”

Separate venv recommendation: a locked kc-nli environment on Python 3.14 with Transformers 5.22.1, PyTorch 2.15.0 and SentencePiece; download model files once into a checksum-addressed cache, then use local_files_only=True. This is a proposed compatibility trial, not a verified working installation. ONNX Runtime can be tested in a second separate environment if the PyTorch trial is slow.

3.3 Evidence verification and corpus-level research systems

|Exact project / primary references                                                                                                                                                          |Release, licence, maintenance                                                                                          |Offline, Python 3.14 fit                                                                                                                                                                                     |Published result (metric, task)                                                                                                                                                         |Labels, benefit, risk                                                                                                                                                                             |Evidence                                                             |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------|
|**CLAIRE / WikiCollide** — [code](https://github.com/stanford-oval/inconsistency-detection), [EMNLP 2025 paper](https://aclanthology.org/2025.emnlp-main.1765/)                             |No verified numbered release; code Apache-2.0, dataset CC BY 4.0; small research repository active around paper release|Published implementation uses **Python 3.12 via Pixi**, retrieval and an LLM provider; no verified offline/no-provider mode or 3.14 integration                                                              |Wikipedia editor study: **64.7% more inconsistencies found in equal time**; best automated **75.1% AUROC** on WikiCollide; **neither is precision or recall**                           |Published annotated WikiCollide: **955 facts; 34.7% inconsistent** (paper); reuse discrepancy categories and retrieval/agent trace design; web search/provider stack conflicts with kc constraints|VERIFIED_PRIMARY                                                     |
|**MiniCheck** — [code](https://github.com/Liyan06/MiniCheck), [paper](https://aclanthology.org/2024.emnlp-main.499/), [Flan-T5 model](https://huggingface.co/lytang/MiniCheck-Flan-T5-Large)|Code `pyproject.toml` **0.1.0**, research-era; Apache-2.0; checkpoint model card **MIT**, no semantic model release    |Python >=3.8 declared; Torch, Transformers, NLTK, datasets/pandas/NumPy and an OpenAI package dependency; local checkpoint inference can run without cloud; 3.14 end-to-end **not verified**, isolate in venv|**770M-parameter** best model reaches GPT-4-level benchmark performance at reported **400× lower cost** on LLM-AggreFact; not 400× faster on M2 Max; no transferable kc precision/recall|No labels for pretrained use; need project negatives and unsupported claim examples for selection; evaluates **document→claim support**, not **claim↔claim contradiction**                        |VERIFIED_PRIMARY                                                     |
|**SummaC** — [code](https://github.com/tingofurro/summac), [PyPI](https://pypi.org/project/summac/), [TACL paper](https://aclanthology.org/2022.tacl-1.10/)                                 |**0.0.4**, 2023-10-06; Apache-2.0; older research release                                                              |Torch/Transformers and NLI pipeline, no verified 3.14 fit; offline after downloads; optional research venv                                                                                                   |**74.4% balanced accuracy** over six *summarisation consistency* datasets; not precision/recall of corpus-level conflicts                                                               |Zero labels to run; local labels needed for thresholds; copy **sentence segmentation + score aggregation** idea, not installation                                                                 |VERIFIED_PRIMARY                                                     |
|**AlignScore** — [code](https://github.com/yuh-zha/AlignScore), [ACL paper](https://aclanthology.org/2023.acl-long.634/)                                                                    |Repository declares **0.1.3** in `pyproject.toml`; date/latest release **not verified**; MIT code; research-oriented   |Dependency constraints include **torch <2, transformers <5, NumPy <2, old Lightning**; incompatible with *proposed new model venv pins*; offline checkpoints possible; 3.14 **not verified**                 |Paper evaluated **22 datasets** using **4.7M training pairs**; no verified kc-comparable P/R                                                                                            |Evidence alignment comparator; complex dependency work; **defer**                                                                                                                                 |VERIFIED_PRIMARY for repo constraints; UNVERIFIED latest release date|
|**TruthFinder** — [IBM/KDD 2007 paper](https://research.ibm.com/publications/truth-discovery-with-multiple-conflicting-information-providers-on-the-web)                                    |**Algorithm/paper, N/A software release and licence**                                                                  |Can be reimplemented, but no verified modern FOSS package recommended here                                                                                                                                   |Paper reports qualitative improvement in identifying truths among conflicting websites; no comparable P/R extracted                                                                     |Needs **independent sources**, calibrated priors and many repeated objects; duplicates/copy chains in audit reports violate assumptions; **do not use for source-backed resolution**              |VERIFIED_PRIMARY (method)                                            |
|**TRUE benchmark** — [NAACL 2022](https://aclanthology.org/2022.naacl-main.287/)                                                                                                            |**Research benchmark, N/A package release/licence verification**                                                       |Optional downloaded dataset; not core                                                                                                                                                                        |Compares factual-consistency measures at the **example level across 11 datasets**, finding NLI and QA approaches complementary                                                          |Useful as evaluation design, not automatic decision logic; benchmark licence and download details not fully checked                                                                               |VERIFIED_PRIMARY paper; UNVERIFIED dataset licence                   |

Special licence rule: Research paper availability does not prove that every released checkpoint, data file or derivative is FOSS. Verify code, model weights and dataset separately before redistribution or automation. No cloud-provider text transfer is implicit in any recommended core path.

3.4 Canonicalisation, entity linking and label-quality tools

|Tool / URL                                       |Checked version and date; licence                                                                                        |Local runtime and maintenance                                                                                                                        |P/R, labels, likely gain and risks                                                                                                                                                                             |Evidence                                                        |
|-------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------|
|[spaCy](https://pypi.org/project/spacy/)         |**3.8.18**, 2026-10-26; MIT; active                                                                                      |Native compiled wheels for macOS ARM64/Python 3.14; language model separately downloaded; offline; optional venv                                     |General NER/tokenisation; **no domain P/R** for paths, component names or firmware versions in kc; needs few reviewed aliases for evaluation, many annotations for custom training; may merge distinct entities|VERIFIED_PRIMARY                                                |
|[GLiNER](https://pypi.org/project/gliner/0.2.30/)|**0.2.30**, **2026-10-31**; Apache-2.0 library; active                                                                   |Python >=3.10; Torch/Transformers/optional ONNX; model weights have **separate licences**; offline after download; Python 3.14 integration unverified|Configurable entity extraction; **no kc-comparable P/R**; risk of inventing domain aliases; **not required** when controlled explicit aliases suffice                                                          |VERIFIED_PRIMARY library, UNVERIFIED selected checkpoint licence|
|[cleanlab](https://pypi.org/project/cleanlab/)   |**2.9.0**, 2026-01-13; Apache-2.0; maintained                                                                            |NumPy/SciPy/scikit-learn-oriented Python; offline; Python 3.14 integration needs checking                                                            |Confident learning can identify suspicious **labels**, not verify source truth. Needs out-of-sample class probabilities and enough independent labels; with ~50 examples likely unstable                       |VERIFIED_PRIMARY                                                |
|[SciFact](https://github.com/allenai/scifact)    |**Dataset/project; version/date not established**; code Apache-2.0, claim/evidence labels CC BY 4.0, abstracts ODC-By 1.0|Downloaded evaluation corpus; separate scientific-language domain; offline possible                                                                  |Supports/refutes evidence and rationale testing; **no transferable kc P/R**; nontrivial data-rights split; do not install as core                                                                              |VERIFIED_PRIMARY                                                |

Practical normalisation recommendation: maintain a small, explicit, versioned alias registry keyed by canonical entity type and full semantic identity, not by fuzzy wording. Preserve the original agent claim and exact source excerpt. Candidate canonicalisations must be logged before they affect joins.

4. External benchmarks: what transfers and what does not

|Benchmark / source                                                                                            |Published corpus/evidence                                                     |Useful design lesson for kc                                                                                  |What it cannot establish                                                                                                  |
|--------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------|
|[WikiCollide (EMNLP 2025)](https://aclanthology.org/2025.emnlp-main.1765/)                                    |955 facts, 34.7% inconsistent; 75.1% best AUROC                               |Cross-page finding, retrieval trace, discrepancy taxonomy, human-reviewed interpretations                    |Precision/recall on software-audit Markdown                                                                               |
|[ContractNLI (EMNLP 2021)](https://aclanthology.org/2021.findings-emnlp.164/)                                 |**607 annotated NDAs**, evidence spans, entailment/contradiction/not-mentioned|Require **span evidence** and distinguish “not mentioned” from “contradicted”; handle longer document context|Generalisation to ops reports; its 17 fixed hypotheses are unlike arbitrary kc claims                                     |
|[ContractNLI dataset repository](https://github.com/ShubhamKathiriya/Contract_NLI/blob/main/Dataset/README.md)|Dataset documentation reports **CC BY 4.0**, initial release 2021-10-05       |Potential offline benchmark adaptation, with licence attribution                                             |**Secondary repository relative to the paper**; confirm rights against original dataset distribution before redistributing|
|[FEVER](https://fever.ai/dataset/fever.html)                                                                  |**185,445** Wikipedia claims, support/refute/NEI, evidence sentences          |Never turn **not enough information** into false or true                                                     |Different document and ambiguity distribution                                                                             |
|[FEVEROUS](https://fever.ai/dataset/feverous.html)                                                            |**87,026** verified claims, including table-cell evidence                     |Evidence may be structured, not just adjacent prose                                                          |No kc-style version precedence or audit authority logic                                                                   |
|[TRUE (NAACL 2022)](https://aclanthology.org/2022.naacl-main.287/)                                            |11 cross-task datasets, example-level consistency                             |Evaluate each example and report within-group metrics                                                        |A single transferable operating threshold                                                                                 |
|[SummaC (TACL 2022)](https://aclanthology.org/2022.tacl-1.10/)                                                |Six summary-consistency datasets; **74.4% balanced accuracy**                 |Segment long evidence rather than truncate blindly                                                           |74.4% precision or recall on kc                                                                                           |
|[MiniCheck (EMNLP 2024)](https://aclanthology.org/2024.emnlp-main.499/)                                       |LLM-AggreFact supported/unsupported claims from 11 datasets                   |A support checker can be smaller than a general LLM                                                          |Pairwise contradiction detection or resolved current truth                                                                |
|[AlignScore (ACL 2023)](https://aclanthology.org/2023.acl-long.634/)                                          |22 factual-consistency datasets                                               |Model architecture can generalise across support/alignment tasks                                             |Safe conflict suppression from uncalibrated score                                                                         |

One especially important lesson from ContractNLI: an evidence-annotated neutral/not-mentioned result is not a contradiction. The same distinction is essential to kc, including when two documents discuss different versions, host scopes or dates.

5. Top-three scripts: precise build and acceptance tests

The scripts below are implementation specifications. Their runtime projections are not observed timings: they require measurement on the target Mac. All three are readers of existing ledgers and emit new append-only events; none rewrites historical JSONL.

5.1 Priority 1 — kc_source_context.py

Function: attach structural/source provenance to each claim and establish whether a pair is comparable as to subject, scope and effective time. Distinguish current-state contradiction, valid evolution, unknown evidence and historical inconsistency.

Pin/requirements: Python 3.14 stdlib + markdown-it-py==4.2.0; optionally python-frontmatter==1.3.0 and dateparser==1.4.3. Model: none. No server or venv required if dependencies already fit kc’s constraints. Offline.

CLI contract (proposed):

python -m kc_source_context \
  --claims path/to/claims.jsonl \
  --pairs path/to/candidate_pairs.jsonl \
  --sources path/to/markdown-root \
  --out path/to/source_context_events.jsonl \
  --gate-out path/to/context_gate_events.jsonl \
  --policy-version context-v1 \
  --dry-run

Input: immutable claim ID, (subject,predicate,object,scope), exact excerpt, source file and offset/line anchors, source hash, candidate pair IDs, existing human/agent event IDs. Input schema adapters must map existing kc fields; do not replace ledger layouts merely to use this script.

Processing:

1. Verify each source file’s current hash and excerpt match; if stale, emit SOURCE_DRIFT and abstain. Prefer byte/line offsets and original excerpt, not fuzzy matching.
2. Parse Markdown to token/heading spans; locate frontmatter, top-of-file status banners, explicit authority matrix, supersession pointers, and relevant enclosing section.
3. Build a source-status assertion, with its own verbatim evidence excerpt, line span, hash and declared applicability. Distinguish an unqualified heading # Historical from a sourced claim Status: SUPERSEDED by Step12.
4. Parse unambiguous effective dates and versions; record date_source, timezone, granularity, reference_date and uncertainty. Do not equate report creation date with fact effective date without explicit evidence.
5. Interpret scope as typed dimensions: component, host/site, environment, software version, actor/owner and any domain-specific qualifier. A missing qualifier is UNKNOWN, not automatically the global/default scope.
6. Construct explicit supersedes directed edges between document IDs, with exact citation. Detect cycles/inconsistent declarations and abstain.
7. For every candidate pair, evaluate applicability and produce a suggested queue routing, not a final truth statement.

Routing rules:

|Evidence condition                                                      |Suggested disposition                |Human-queue behaviour                                                                |
|------------------------------------------------------------------------|-------------------------------------|-------------------------------------------------------------------------------------|
|Explicitly non-overlapping valid-time intervals and same entity         |`DOCUMENTED_EVOLUTION`               |Move to low-priority history section, audit kept                                     |
|Explicit supersession, newer text directly answers same issue           |`SOURCE_SETTLED_RESOLUTION_CANDIDATE`|Present source quote and candidate current answer; never silently resolve security/P0|
|Strong proof two claims refer to distinct site/environment/version scope|`SCOPE_INCOMPARABLE`                 |Log reason and reduce priority; retain discoverability                               |
|Temporal/scope status contradictory or missing                          |`CONTEXT_UNKNOWN`                    |Leave active; ask verifier/human                                                     |
|Compatible scopes and same overlapping time with opposite claim         |`POSSIBLE_CONFLICT`                  |Continue NLI/agent review                                                            |
|Superseded source contains a *within-its-own-time* contradiction        |`HISTORICAL_CONFLICT`                |Preserve as real historical finding                                                  |

A candidate cannot be automatically classified as harmless merely because its document is superseded. A superseded document can still contain a substantive historical error, and there may be a current fact that materially depends on that history.

Append-only event example:

{
  "event_type": "kc.source_context_gate.v1",
  "event_id": "sha256:<canonical-event-digest>",
  "pair_id": "pair-001",
  "claim_ids": ["claim-a", "claim-b"],
  "source_sha256": ["<a>", "<b>"],
  "context_assertion_ids": ["ctx-a", "ctx-b"],
  "policy_version": "context-v1",
  "evidence_spans": [
    {"document_id": "step4", "line_start": 1, "line_end": 3,
     "exact_excerpt": "Status: SUPERSEDED by `step8-finalization-closure.md`, `step11-final-authoritative-state.md`, and `step12-optional-hardening-final-state.md`"}
  ],
  "suggested_disposition": "DOCUMENTED_EVOLUTION",
  "decision_status": "CANDIDATE_ONLY",
  "requires_human_approval": false,
  "reverses_event_id": null
}

The example event ID, pair IDs and hashes are illustrations, not live kc records. The status exact_excerpt text is transcribed from the provided Step4 source; the production span matcher must verify its exact bytes and associated line coordinates before use.

Smallest test:

• Hand-label the status/authority relationship of all 24 reports independently of kc’s proposed result (a 24-file structural test is feasible).
• Use the 45 original blind positives as a recall-protection suite; explicitly add at least one CURRENT↔HISTORICAL, SUPERSEDED↔CURRENT, SAME-TIME-CONFLICT, SCOPE-DIFFERENT, SCOPE-UNKNOWN and SOURCE-DRIFT negative/edge test.
• Test the supplied Step4→Step12→Step13 hierarchy: Step4 body facts remain historical; Step12’s current observations are not overwritten by Step4’s earlier values.
• Assertion: every auto-routed finding retains queryable IDs and original evidence. Every claimed status/effective date has a source span; absence yields abstention.
• Gate: no newly missed real conflict in replay; fewer unhelpful unresolved human actions than baseline. A 45-item positive set alone cannot provide a high-confidence guarantee of zero real-world misses.

Runtime and token estimates:

|Scale       |Work                                                                              |Expected on M2 Max                                                                                                        |LLM tokens|Confidence                       |
|------------|----------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------|---------:|---------------------------------|
|400 claims  |24 similar short Markdown docs + ~hundreds of pair comparisons                    |Seconds-scale after startup, contingent on file bytes                                                                     |**0**     |Algorithmic only, not benchmarked|
|3,500 claims|O(total source bytes + claims + evaluated pairs); incremental cache by source hash|Seconds to potentially tens of seconds if sources remain short; actual corpus bytes and pairs matter more than claim count|**0**     |Algorithmic only                 |

Potential gain: high match to measured false-positive types; unknown magnitude until tested. A defensible target is reduced active nonissues with unchanged recall, not a speculative “remove 60%”.

5.2 Priority 2 — kc_root_cause_rollup.py

Function: compress repeated review actions without collapsing distinct evidential claims or claiming that related symptoms prove the same cause.

Pin/requirements: Python 3.14 stdlib. Optional networkx==3.7 only if target interpreter is not 3.14.1; prefer a 30-line disjoint-set/union-find implementation. Model: none. No daemon or external venv.

CLI contract (proposed):

python -m kc_root_cause_rollup \
  --pairs path/to/candidate_pairs.jsonl \
  --context-events path/to/context_gate_events.jsonl \
  --decisions path/to/human_decisions.jsonl \
  --out path/to/root_cause_events.jsonl \
  --report path/to/rollup_report.json \
  --strict

Input: candidate pair IDs; provenance and source span IDs; claim IDs; cause_type proposals, human decisions and contextual relation edges. The rollup should use verified cause identity such as an exact supersession edge or same faulty source-status assertion, not merely a matching filename or similar summary.

Proposed cause signature:

cause_key = HASH(
    cause_type,
    canonical_affected_entity_or_exact_scope,
    authoritative_evidence_anchor,
    source_relation_edge_id,
    applicable_time_or_version
)

Algorithm:

1. Derive candidate SAME_ROOT_CAUSE links from source-context events only when backed by the same explicit source evidence or reviewed decision.
2. Keep RELATED and POSSIBLE_SAME_CAUSE in separate ledgers; they are hints, not union edges.
3. Form disjoint sets over validated edges, but enforce compatibility of cause signature for every member; otherwise split/reject the proposed union.
4. Select a representative finding based on evidence completeness, not an LLM-written headline.
5. Store all member pair IDs, original excerpts, root evidence, link rationale and the exact algorithm/policy version.
6. Human decisions operate on the group only with an explicit option to disagree for a member, split the group, and record a superseding event. A group edit never mutates previous events.

Avoid single-linkage overmerging: A≈B, B≈C does not establish that A/C have the same root cause. A lexical near-duplicate score cannot create a verified group edge.

Append-only event example:

{
  "event_type": "kc.root_cause_group.v1",
  "group_id": "sha256:<stable-cause-signature>",
  "members": ["pair-001", "pair-004", "pair-009"],
  "relation": "SAME_ROOT_CAUSE",
  "cause_type": "SUPERSESSION_NOT_APPLIED",
  "anchor_context_event": "ctx-55",
  "policy_version": "rollup-v1",
  "suggested_human_actions": 1,
  "original_member_count": 3,
  "decision_status": "CANDIDATE_ONLY"
}

Smallest test:

• Use the sampled 10 positive findings that reportedly share one root cause as a reviewed positive grouping control; preserve the eleventh as separate unless evidence proves otherwise.
• Include at least 5 adversarial pairs of findings that share words/documents but have different causes (a small targeted label expansion; do not assume these negatives already exist).
• Assert: group purity = correct members / all grouped members; group overmerge rate; affected real conflicts preserved; action count before/after; audit trace coverage 100%.
• Conditional illustration: if the 10 shared-cause findings would otherwise each require a human decision, grouping the 11 real positives into two groups reduces 11 decisions to 2 (81.8%) for that subset. This is not an estimate for the 243-record queue.

Runtime and tokens:

|Scale                                        |Work                                                                             |Expected on M2 Max                                                |LLM tokens|
|---------------------------------------------|---------------------------------------------------------------------------------|------------------------------------------------------------------|---------:|
|400 claims / up to ~243 existing open records|O(records + validated cause edges)                                               |Sub-second to a few seconds for bounded edges                     |**0**     |
|3,500 claims                                 |Still O(findings + verified group edges); group count, not claim count, dominates|Seconds-scale under similarly sparse relations; measure worst-case|**0**     |

Potential gain: high in review-action compression due to the measured repeated-root pattern, but zero guaranteed reduction in underlying genuine-pair count. Do not optimise a group-size metric at the expense of purity.

5.3 Priority 3 — kc_nli_shadow.py

Function: cheaply test pairwise semantic contradiction versus neutral/entailment on source-supported claim excerpts, using a local 82M-parameter cross-encoder first; only expensive cases go to stronger model/agent review. It must not auto-dismiss a pair yet.

Pins/model snapshot:

Python               3.14 (separate kc-nli venv)
transformers         5.22.1 (2026-10-30)
torch                2.15.0 (2026-10-28)
sentencepiece        exact installed version to be locked at trial (not verified here)
MiniLM NLI           cross-encoder/nli-MiniLM2-L6-H768
MiniLM checkpoint    model revision b95119c (short SHA; obtain complete immutable SHA)
Stronger NLI model   MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli
Stronger checkpoint  full immutable SHA to resolve and lock before first run
Ollama               not required
External API         not required

Important: The package pins above were individually verified as published, not jointly runtime-tested. The model loading/SentencePiece/MPS interactions may fail or require version adjustment. Such a change must be recorded as a compatibility decision, not silently asserted successful.

CLI contract (proposed):

python -m kc_nli_shadow \
  --pairs path/to/candidate_pairs.jsonl \
  --claims path/to/claims.jsonl \
  --context-events path/to/context_gate_events.jsonl \
  --model local/path/to/minilm-snapshot \
  --escalation-model local/path/to/deberta-snapshot \
  --out path/to/nli_shadow_events.jsonl \
  --mode shadow \
  --batch-size 8

Stages:

1. Refuse unverified excerpts, ambiguous source drift or unresolved text truncation.
2. Work from atomic claim plus minimal relevant source context (status/scope must already have been attached). Preserve the full source link; never let token truncation masquerade as evidence absence.
3. Optionally check source→claim entailment; mark unsupported extraction separately (MiniCheck is a later comparator).
4. Run NLI on A→B and B→A, mapping labels using config.id2label; log both results.
5. Produce routing suggestions: LIKELY_CONTRADICTION, LIKELY_NEUTRAL, LIKELY_ENTAILMENT, MODEL_DISAGREEMENT, INSUFFICIENT_CONTEXT, TRUNCATED.
6. On uncertain cases, optionally run DeBERTa; on disagreement, route to existing higher-quality source-reading agent/human.
7. Emit immutable logits/class scores, model hashes, text hashes, context IDs, threshold/policy version, CPU/MPS device, runtime and tokenisation/truncation observations.
8. Do not treat a high contradiction softmax as a calibrated probability of an actionable current conflict. Do not use model agreement as independent-source confirmation.

Proposed event:

{
  "event_type": "kc.nli_shadow.v1",
  "pair_id": "pair-001",
  "model_repository": "cross-encoder/nli-MiniLM2-L6-H768",
  "model_revision": "<full-sha>",
  "input_hashes": ["sha256:<a>", "sha256:<b>"],
  "source_context_event_ids": ["ctx-a", "ctx-b"],
  "directions": [
    {"from": "a", "to": "b", "scores": {"entailment": 0.10, "neutral": 0.70, "contradiction": 0.20}},
    {"from": "b", "to": "a", "scores": {"entailment": 0.12, "neutral": 0.68, "contradiction": 0.20}}
  ],
  "truncated": false,
  "suggested_route": "LIKELY_NEUTRAL",
  "decision_status": "SHADOW_ONLY"
}

Numbers are illustrative dummy outputs, not model predictions or calibrated probabilities.

Smallest meaningful test:

• Score the 45 blind positives and all independently labelled negatives available from the earlier sample; deduplicate exact pair IDs if the sets overlap.
• Build a small prospective root-disjoint negative test set specifically enriched for scope differences, supersession and time evolution; the 40-item sample alone is insufficient to validate a filter.
• Report per-type confusion matrices. Every TRUNCATED or INSUFFICIENT_CONTEXT case is an abstention, not a “no conflict”.
• Compare baseline LLM-only versus (a) context-gated LLM and (b) context + NLI shadow routing, with identical candidate sets, evidence budget and blind labels.
• Log LLM tokens actually used in each trial. The existing 2.4M tokens include more than pair verification, so do not attribute all of them to the filterable stage.

Workload estimation: let Q be candidate pairs scored, H be those sent to DeBERTa, t_small and t_large be measured time per directed inference, and T_load the model-load time:

T ≈ T_load + (2 × Q × t_small) + (2 × H × t_large)

Batching and device effects make this a planning formula, not a benchmark. Under an illustrative 256-input-token cap per direction:

|Scale       |Candidate-pair assumption                                              |Local first-stage model input token cap|External LLM tokens                                                        |Runtime assertion       |
|------------|----------------------------------------------------------------------:|--------------------------------------:|--------------------------------------------------------------------------:|------------------------|
|~400 claims |**243** current open candidate records (not proven all are unique)     |243 × 2 × 256 = **124,416**            |**0** for NLI-only pass; escalations consume separately measured LLM tokens|**Unverified** on M2 Max|
|3,500 claims|**2,000** hypothetical candidate pairs for planning, **not** a forecast|2,000 × 2 × 256 = **1,024,000**        |**0** for NLI-only pass; escalation tokens unproven                        |**Unverified** on M2 Max|

Those are local inference input tokens, not paid/API tokens. A 256-token cap is a chosen experimental limit, not proof that all needed context fits. If the evidence does not fit, segment/retrieve appropriate spans or abstain. A second-stage model adds its own local token work; the stated totals are first stage only.

Promotion gate: show improved human-visible precision or cost at equal or better root-level recall on fresh blinded material. Given 45 positives, zero observed new false negatives still has an approximate 6.4% one-sided 95% upper bound for a per-positive miss probability under iid assumptions (1 − 0.05^(1/45)). That is far too weak for a broad, unattended suppression policy. This is why model score ≠ automatic safety assurance.

6. Cross-document recall: the best next deterministic experiment

The measured 25% cross-file recall deserves a separate retrieval study once the source-context gate is in place. If candidate pairs are not retrieved, a better NLI model cannot recover them.

kc_retrieval_shadow.py: candidate-generation experiment

Baseline: current FTS5 + RapidFuzz + simple signals. Freeze it as baseline-v1; do not reimplement FTS5 to make results look better.

Candidate alternatives, tested independently and combined:

• Explicit alias table: {alias, canonical_id, entity_type, evidence, approved_by, alias_version}; no auto-merge by LLM. Good for paths, application names, site IDs, firmware branches, Step12/step12-optional-hardening-final-state.md etc.
• Character n-gram TF–IDF using TfidfVectorizer(analyzer='char_wb', ngram_range=(3,5)) from scikit-learn==1.9.1; optional venv. Cross-file query each claim against other claims, with candidate caps.
• BM25/FTS5 term expansions with typed entity and predicate terms, but retain simple SQLite as core. If using SQLite FTS5 bm25(), verify ranking direction and query-plan cost.
• Shared terms across differing claims: dissimilar object values under a common subject/predicate are potential conflicts, but cannot be established on string similarity alone.
• Targeted cross-file adjacency: supersession references, same canonical component/site, explicit report hierarchy. These can rescue same-entity pairs even when agent topic keys differ.

Controlled test: keep a 45-positive retrieval oracle with pair IDs. Report Recall@K for K=5/10/20 per claim, candidates/claim, positive recall by category, and downstream false-positive growth after verifier. Evaluate 400 and 3,500 claims under explicit caps; avoid unrestricted O(n²) pair creation.

Expected gain: possible improvement in missed cross-file/authority categories, unquantified. Character n-grams are not semantic embeddings; they will miss paraphrases and overmatch similarly named but distinct entities. There is no evidence that a vector DB is needed at 3,500 claims.

7. Source authority and safe, reversible automatic resolution

Truth discovery is not the same as source-settled resolution. TruthFinder and similar multi-source reliability algorithms were designed for cases with repeated, partly independent sources. Audit reports generated by the same workflow are often copied, paraphrased and superseded: counting agreement creates false independence. A newer report may be authoritative about the current state, but not necessarily correct about an unrelated historical event.

Required proof model

A resolution candidate should require all of the following:

1. Exact verified excerpt for the disputed claim(s).
2. Exact verified source declaring the relevant authority, effective state or supersession relation.
3. Scope/time compatibility and a demonstrable answer to the same proposition.
4. Citation for the winning answer in the source, not inferred from confidence, vote counts or LLM general knowledge.
5. Explicit reason why the losing source does not govern the questioned time/scope.
6. Immutable event linking to the specific affected finding IDs; reversible supersession mechanism.
7. Fail-closed behaviour for P0, safety, security and ambiguous authority: human decision mandatory.

Suggested reason taxonomy:

EXPLICIT_SUPERSESSION
DOCUMENTED_EVOLUTION
NON_OVERLAPPING_EFFECTIVE_TIME
INCOMPARABLE_SCOPE
SOURCE_EXPLICITLY_SETTLES_VALUE
CONTEXT_AMBIGUOUS_ABSTAIN
SOURCE_DRIFT_ABSTAIN
AUTHORITY_CONFLICT_HUMAN
SAFETY_P0_HUMAN

Reversible sequence:

claim/event ledger (immutable)
     |
     +--> source-context evidence event
     +--> proposed resolution event (candidate)
     +--> rule-gated accepted disposition (if policy permits)
     +--> human override / reversal event
     +--> materialised current view replayed from all events

Every accepted auto disposition must specify its policy version and reversal target. Changing the policy or replacing a source triggers re-evaluation events; it must not erase the old rationale. Use existing JSONL as authority and SQLite tables strictly as rebuildable indexes/materialised views.

Examples using the supplied documents:

• Step4 says a legacy path existed in a historical state; Step12 says it is currently absent. Evolution, if the respective dates/time scopes are corroborated.
• Step12 says two Voicemode compatibility shims remain necessary after a failed no-shim test. A new model should not resolve this as “remove shims” based on a generic preference for cleaner repositories; the primary source documents an explicit test failure and decision.
• A claim in a historical report that a specific 2026 test passed could contradict another record that it failed at that same test/time. Status alone does not dismiss the discrepancy.

A numerical or weighted authority model may rank human review (for example, explicit final closure > interim note for current operations), but it must not manufacture source-settled truth from a ranking score.

8. Calibration, noise probabilities, intervals and reviewer agreement

8.1 What can be reported with ~50 labels

Ready now:

• Pair-level confusion matrices and TP/(TP+FP), TP/(TP+FN) with denominators.
• Wilson binomial intervals for carefully sampled, roughly independent observations.
• Stratified reporting (same-file / time evolution / authority / cross-file), with explicit small-n warning.
• Distinct-root issue yield and review-action counts.
• Paired before/after decision audit with explicit list of regressions.
• Two-reviewer disagreement table and Cohen’s κ if the label scheme and independent reviewers support it; report raw agreement and class prevalence too.
• UNKNOWN/ABSTAIN rate as a first-class outcome.
• Unit and metamorphic tests (examples below).

Not ready: meaningful well-calibrated per-finding probabilities, reliable subgroup confidence, auto-dismiss thresholds claimed safe from ~50 labels, evidence-independent truth probabilities, or a learned ranking system trained and evaluated on repeatedly reused root-correlated examples.

8.2 Wilson interval — exact calculation

For k successes in n sampled, approximately independent trials and standard normal z=1.96:

[
\hat p=k/n,\quad
\mathrm{CI}_{Wilson}=\frac{\hat p+z^2/(2n)\pm z\sqrt{\hat p(1-\hat p)/n+z^2/(4n^2)}}{1+z^2/n}
]

For k=11, n=40: 0.1611–0.4284. This interval describes the earlier sample under the binomial approximation. If the 40 rows include many copies of the same root issue, the effective independent sample size is smaller and the interval is optimistic.

Sampling recommendation: define the target population (all new candidate pairs versus unique root groups); draw randomly within file/status/type strata; weight strata to compute an overall estimate only if their population proportions are known. Never select only easy or confidence-ranked candidates and call the resulting precision representative.

8.3 Platt, isotonic and conformal

• Platt scaling: fit logistic map from model score to observed label. With ~50 heterogeneous, correlated examples this risks extreme parameter uncertainty. If used, treat as a diagnostic only, use grouped cross-validation and report calibration reliability curves with caution.
• Isotonic regression: nonparametric monotone calibration; particularly unstable in small samples with few distinct score/label points. Do not use for auto-resolution at present.
• Conformal prediction: finite-sample marginal coverage requires exchangeability and a predefined score and calibration procedure. With n=50 calibration points, quantile granularity is approximately 1/(n+1)=1.96 percentage points; subgroup risk is even harder to bound. Root-related pairs and evolution over time violate naïve exchangeability. Could be evaluated as abstention/risk reporting, not as an independent fact-checking oracle.
• Cleanlab/confident learning: finds likely annotation errors given adequate out-of-sample class probability estimates; it does not decide if a source truthfully resolves another. Do not train on these same 50 examples and interpret the resulting label-quality score as evidence.

8.4 Noise probability versus routing score

Keep three concepts separate:

model_score         = raw classifier score, not calibrated for kc
noise_routing_score = priority signal for review/workflow ordering
estimated_P_noise   = statistical estimate requiring validated calibration

At current label volume, use model_score and source-backed reason codes. Prefer the notation not_calibrated to fabricated confidence such as 0.97 probability this is noise.

8.5 Inter-rater agreement

Use two reviewers blind to the model suggestion on a deliberately mixed sample; define a four- or five-way label scheme before scoring:

CURRENT_TRUE_CONFLICT
HISTORICAL_TRUE_CONFLICT
DOCUMENTED_EVOLUTION
SCOPE_INCOMPARABLE
INSUFFICIENT_EVIDENCE

Calculate raw agreement and Cohen’s κ for two raters. κ adjusts chance agreement but can behave unexpectedly under skewed prevalence; include the full confusion matrix. Record adjudication rationale and exact source evidence; adjudication must not overwrite initial reviewer labels. For more raters or missing ratings, consider Krippendorff’s α in a separately validated statistics module, not as a reason to add more infrastructure.

9. Agent routing and reusable, no-install research processes

9.1 Local-first decision cascade

exact excerpt verification (existing kc)
       |
       v
source-context & scope gate --------------> documented evolution/history candidates
       |
       v
candidate discovery (FTS5 + RapidFuzz + alias/TF-IDF shadow)
       |
       v
root-cause grouping -----------------------> one review action; all pair IDs preserved
       |
       v
optional MiniLM pairwise NLI (shadow)
       |               |
  clear signal       unknown/disagree/truncated
       |               |
       +---------------+----> optional DeBERTa source-aware NLI (shadow)
                              |
                              v
                         existing stronger LLM agent
                              |
                              v
                    human for unresolved/P0/security

The NLI models may rank, but the source must resolve the proposition before any automatic resolution. Do not run NLI on all 382×381/2 = 72,771 possible unordered pairs or at 3,500 claims on 6,123,250 pairs. Retrieval caps and typed candidate routing are essential; a larger context window does not fix quadratic candidate generation.

9.2 Which steps cost LLM tokens

|Step                                                          |LLM tokens         |Comment                                                   |
|--------------------------------------------------------------|------------------:|----------------------------------------------------------|
|Excerpt/source integrity, status, time, scope and reason codes|0                  |Source parsing and rules                                  |
|Root-cause grouping, exact signatures, graph operations       |0                  |Human may optionally name an otherwise cryptic cause      |
|Existing FTS5/RapidFuzz; optional TF–IDF                      |0                  |CPU work only                                             |
|MiniLM/DeBERTa local inference                                |0 *paid* LLM tokens|Uses local model input tokens/compute; not free in CPU/RAM|
|Existing source-reading LLM on hard cases                     |Variable           |Must measure from logs, not assume from total 2.4M        |
|Human review                                                  |0 LLM tokens       |Decision time is a cost measured separately               |

A cheap local model’s principal benefit is reducing how many uncertain pairs reach an expensive reasoning agent, but only if it preserves recall. It cannot be credited with saving 2.4M tokens if much of that was used on extraction, re-reading, or repeated corpus exploration.

9.3 Published process ideas usable without installation

1. CLAIRE / WikiCollide three-stage discipline: atomic extraction → targeted evidence retrieval → cited inconsistency report; save retrieval action trace, search hits, last-edit/status evidence and contradiction type. Do not reuse its Wikipedia crawler/provider architecture. Primary.
2. ContractNLI span evidence discipline: every finding names the evidence spans, distinguishes entailment / contradiction / not mentioned. Primary.
3. SummaC segmentation: compare specific relevant sentences rather than whole reports; aggregate or escalate when important clauses are omitted. Primary.
4. MiniCheck claim grounding: test whether a proposed extracted claim is actually supported by its own excerpt. Report unsupported extraction as an independent failure, not a conflict. Primary.
5. Adversarial review as an agent skill (proposed kc procedure, not a validated package): give a second reviewer the exact pair, sources, scope, time and provisional reason; ask it to construct a non-conflict reading and a true-conflict reading citing each, then abstain when neither can be disproved. Log the two hypotheses and adjudication. No claim of measured accuracy gain.
6. Wiki-maintenance policy as a skill (proposed): check canonical entrypoint/status banner/index; never interpret superseded detail as current state; preserve historical provenance; show explicit lineage of changes. This is appropriate to the supplied audit pack. No installation.

Do not confuse multiple agents agreeing with independent evidence. They may share the same retrieval miss, prompt, model bias or stale source. Independence must be demonstrated or the vote is only a confidence signal.

10. Build order and exact gates

Ready now — no new model, no external daemon

|Phase|Deliverable                                                                                                                                            |Minimal test                                                                                                    |Promotion gate                                                                                   |Rollback                                                    |
|----:|-------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|------------------------------------------------------------|
|0    |Freeze and export baseline: 24 documents, claim/pair/event ledger hashes, 45 positives, 40-sample provenance, prompts/tokens and current policy version|Rebuild/read index; verify source hashes and all claim IDs                                                      |Deterministic baseline replay matches current counts; discrepancy explained                      |Previous executable/policy remains untouched                |
|1    |`kc_eval.py`: blind labels and root-aware metrics                                                                                                      |11/40 reproduces 27.5%; Wilson 95% approx 16.1–42.8; 45-labelled recall calculation reproduces 66.7% to rounding|Count denominators and data leakage documented                                                   |Evaluation module read-only                                 |
|2    |`kc_source_context.py` and 24-report status fixture                                                                                                    |Step4→Step12 history; unknown effective time; two scopes; source drift; contradictory banners                   |No new lost real positives in the full regression replay; every disposition has exact source span|Append reversal/routing-policy event, not destructive delete|
|3    |`kc_root_cause_rollup.py`                                                                                                                              |10 shared-root positives + unrelated-root adversarial controls                                                  |Zero known overmerges in reviewed acceptance fixture; preserve all member IDs                    |Split/reversal event                                        |
|4    |Source-declared `RESOLUTION_CANDIDATE` suggestion, governed by explicit source                                                                         |Same entity/time/scope; cite exact winning source; P0/security forced human                                     |All source-settled suggestions have direct answer, authoritativeness and lineage proof           |Reversal event + rebuild view                               |
|5    |`kc_retrieval_shadow.py`: aliases + char TF–IDF                                                                                                        |Known missed cross-file positives, K=5/10/20; measure added candidates                                          |Higher verified recall at bounded candidate volume and acceptable false-positive review rate     |Toggle shadow query path off                                |

Phase 0 is essential because the “earlier 40” sample and the 45 positives have different collection windows. Treat them as distinct sets until their IDs and overlap have been established.

Not ready for production

|Workstream                          |Reason it is not ready                                                          |Evidence required to reconsider                                                                        |
|------------------------------------|--------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------|
|NLI model filtering                 |No kc-specific prospective validation; local package/model compatibility not run|Root-disjoint held-out data, latency/memory test, safer recall and precision than context-only baseline|
|NLI automatic dismissal             |~50 labels cannot bound rare false negatives tightly enough                     |Large independently adjudicated, future-domain sample and explicit per-class risk policy               |
|Model probability calibration       |Tiny correlated set; unstable subgroup calibration                              |Independent calibration and test sets, reliability/Brier/ECE measures with intervals                   |
|Learned truth discovery             |Documents are dependent and precedence is source-specific                       |Separate independent sources and demonstrably reliable source independence model                       |
|Heavy entity linking / coreference  |Ambiguous technical identifiers, unmeasured alias errors                        |Labelled failure cases showing simple alias+lexical methods insufficient                               |
|MiniCheck support verifier          |May improve extraction validation but is not central conflict gate              |Tested package/model on Python 3.14/M2 Max and exact-source support labels                             |
|AlignScore/SummaC full packages     |Older dependencies and input/task mismatch                                      |Strong head-to-head results on kc against lightweight alternatives                                     |
|Dedicated vector DB/graph DB/crawler|No evidence at 382–3,500 claims                                                 |Profiling proves SQLite/textual indexes cannot meet measured recall/latency                            |
|Cloud verifier                      |Project text would leave machine; no verified net advantage at this size        |Security approval, data-exfiltration constraints and blinded accuracy/cost superiority                 |

Immutable decision contract

The following are mandatory properties for every candidate plugin/model/process:

- Never edit/delete prior source, claim, pair, classifier or human ledger events.
- Every suggested dismissal has a reason code and matching exact evidence span(s).
- Every model signal records full model revision/hash, run ID and input hashes.
- Every automatic acceptance is replayable, explicable and reversible.
- Unknown time, status, scope, source drift or truncation => abstain / human.
- P0 / safety / security => human, regardless of model confidence.
- A source must state the resolution; an LLM cannot invent the missing authority.
- The current materialised view is reconstructible from immutable ledger events.
- Any change that improves headline precision while hiding known positives fails.

11. Quantitative experiment plan: 400 and 3,500 claims

These projections are transparent workload scenarios, not runtime benchmarks on the user’s Mac.

11.1 Candidate generation scaling

|Claims|All unordered pairs (worst case)|Consequence                                                |
|-----:|-------------------------------:|-----------------------------------------------------------|
|400   |79,800                          |Still enough to overwhelm an unconstrained LLM pass.       |
|3,500 |6,123,250                       |**Not viable** as default all-pair NLI or LLM verification.|

Use exact scope/entity gates and retrieval caps. Scaling becomes proportional to candidate set Q rather than all pairs. At 400, Q=243 is the reported current open record count, not proof of all previous candidates. At 3,500, Q=2,000 is a deliberate illustrative capacity-planning scenario; run sensitivity cases Q=1,000, Q=5,000, Q=15,000 to avoid assuming constant sparsity.

11.2 End-to-end budget accounting

Record separately:

source_bytes_read
claims_ingested
candidate_pairs_generated
pairs_after_context_routing
unique_root_groups
pairs_forwarded_to_NLI
pairs_escalated_to_strong_LLM
LLM_prompt_tokens / LLM_completion_tokens per stage
local_model_input_tokens and CPU/MPS inference time
human_review_actions
human_review_minutes
confirmed_true_conflict_roots
missed_true_conflict_roots

In particular, do not compare local NLI input tokens to paid LLM tokens as though they were the same cost. Local inference consumes compute, memory and electricity; cold starts can dominate at this corpus size. The total ~2.4M LLM tokens is not a verified forecast for future 3,500-claim runs.

11.3 Minimum timing study on Apple Silicon

1. Hardware record: M2 Max GPU/CPU/memory, macOS version, Python 3.14 patch version, storage location, device mode and thermal state.
2. Measure kc_source_context.py with warm file cache and cold run; repeat 5 times. Report median, p95 and peak RSS.
3. Measure root rollup separately for Q=243, then synthetic Q=2,000/5,000 with honest synthetic labels; report O(E + V) behaviour and hash/index overhead.
4. Test MiniLM CPU versus MPS at batch sizes 1/8/16, recording startup time, pair/s, input length and peak unified RAM. Test DeBERTa separately; do not assume it is faster on MPS without measuring.
5. Include input-length truncation counts and failure types. A fast but truncated model score is not a valid quality improvement.
6. Report baseline LLM stage tokens in the exact same trial rather than estimating a percentage saving from claim count alone.

No verified M2 Max latency figures were found for the exact pinned model+library+kc input combination. Publishing “200 ms per pair” or “X-fold cheaper” would be speculative.

12. Focused test taxonomy and acceptance fixtures

Create small explicit labelled fixtures, distinct from the blind set, with at least the following situations:

|ID |Fixture                                                                                               |Expected safe action                                                                                                |
|---|------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------|
|F01|Old report with top-of-file `SUPERSEDED` banner, historical body preserved                            |Record supersession; do not treat old body as current                                                               |
|F02|New report states replacement state, with exact earlier timestamp                                     |Suggest documented evolution, link both facts                                                                       |
|F03|Newer report appears without explicit authority or effective date                                     |Abstain, do not choose newest automatically                                                                         |
|F04|Contradictory statements for **same** host/version/effective time                                     |Preserve real conflict despite being in historical docs                                                             |
|F05|Same wording but staging versus production                                                            |Scope-incomparable suggestion with exact qualifiers                                                                 |
|F06|Same hostname but differing version qualifiers                                                        |Version-aware routing; avoid false current conflict                                                                 |
|F07|One claim global and one claim scoped, globality not explicit                                         |Scope unknown, abstain                                                                                              |
|F08|`Step11` report contains “currently authoritative” inside superseded body while header says superseded|Check later authoritative index and explicit source-status evidence; abstain if chronology/authority is inconsistent|
|F09|Source excerpt changed since agent extraction                                                         |Source-drift event, no auto judgment                                                                                |
|F10|Same bad banner causes ten reported findings                                                          |Conservative single root group with all ten members                                                                 |
|F11|Two distinct causes share a document and similar terms                                                |Do not merge                                                                                                        |
|F12|Cross-file paraphrases with different agent topic keys                                                |Retrieval shadow attempts rescue with canonical entity/TF–IDF                                                       |
|F13|Source contains a sentence that is *not enough information* to resolve claim                          |`INSUFFICIENT_EVIDENCE`, not contradiction or truth                                                                 |
|F14|Security/P0 conflict with explicit later source                                                       |Candidate may be suggested, but final human approval mandatory                                                      |
|F15|NLI model input exceeds token limit                                                                   |`TRUNCATED`/abstain, never benign dismissal                                                                         |
|F16|Source index and report banner disagree                                                               |Record both evidence spans; human resolves authority policy                                                         |
|F17|Same root cause description generated by two agents using different words                             |Merge only by source-evidenced cause key, not cosine/fuzzy text                                                     |
|F18|Source has relative date “last week” without stable reference date                                    |Date unknown; no silent current-date interpretation                                                                 |

Metamorphic tests: Adding irrelevant Markdown comments cannot alter decisions; switching report filenames without changing status evidence cannot silently promote authority; permuting claim ingestion order cannot change group identity; changing only the source hash must invalidate cached context; replacing “production” with “staging” must change comparability without rewriting the original evidence; removing a status banner must increase abstention, not automatically increase confident resolution.

13. What to leave alone

|Existing subsystem / proposed expansion     |Recommendation                                                  |Reason                                                                                                                                    |
|--------------------------------------------|----------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------|
|**Exact excerpt verification**              |**Keep unchanged** except source-drift reporting                |It is the strongest anti-hallucination invariant: every claim must be attributable to real source bytes.                                  |
|**Append-only JSONL event architecture**    |**Keep**                                                        |Perfect fit for reversible, auditable candidate signals and human decisions.                                                              |
|**SQLite FTS5**                             |**Keep as primary index**                                       |Local, simple, well matched to corpus scale; assess retrieval *recall* first before replacing.                                            |
|**RapidFuzz**                               |**Keep for alias candidate discovery**                          |High speed, already present; do not mistake fuzzy matching for entity equivalence.                                                        |
|**Human decision gate**                     |**Keep, strengthen reason-code evidence**                       |A small inaccurate learned model cannot safely replace authoritative judgement.                                                           |
|**Existing LLM extraction path**            |**Do not redesign yet**                                         |Task specifies already extracted atomic claims and exact excerpts; major loss is downstream status, grouping and cross-file matching.     |
|**Agent-assigned topic keys**               |Keep raw for provenance but **stop using as canonical join IDs**|One common key in 245 makes them demonstrably unsuitable as global identity.                                                              |
|**Global knowledge graph / Neo4j**          |**Do not add**                                                  |A small directed `supersedes`/cause-edge graph can live in JSONL+SQLite or a simple in-memory graph.                                      |
|**Vector database / crawler**               |**Do not add**                                                  |No evidence it improves these document-status failures; considerable operational and embedding-drift overhead.                            |
|**Ollama server**                           |**Not required for NLI**                                        |Cross-encoder Torch or ONNX can load directly; server only if a future multi-client use case demonstrates value.                          |
|**OpenIE/coreference pipeline**             |**Defer**                                                       |Adds another fallible extraction layer on top of already atomic agent claims. Build explicit aliases and measured recall experiment first.|
|**Automatic model-majority truth discovery**|**Do not use**                                                  |Non-independent models or repeated reports do not create independent factual evidence.                                                    |

14. Negative findings and verification limits

What research did not substantiate

1. No evaluated FOSS model was found that demonstrates a better precision/recall trade-off than a high-quality source-reading LLM on kc’s 24-report audit corpus. This is not a proof that no such model exists; it is the limit of available comparative evidence.
2. No published package/research result directly justifies an automatic “superseded banner means false conflict” rule. It is a domain-specific evidence-conditioned policy, not a published universal truth rule.
3. 74.4% SummaC means balanced accuracy on its six benchmark datasets, not kc precision or recall; 75.1% WikiCollide is AUROC, not accuracy or recall; 64.7% CLAIRE measures assisted-editor improvement, not model recall; 400× MiniCheck is the authors’ benchmarked relative cost, not M2 Max latency or kcal savings.
4. The 45 blind-labelled real conflicts and earlier 40 queue samples were not provided as machine-readable pair IDs. We could not directly verify their intersection, compute a root-cause-aware confusion matrix, or estimate achievable noise removal from raw labels.
5. The 243 open conflict records are not proven to be independently actionable or unique pair IDs; group compression benefits cannot be extrapolated from 10/11 positives.
6. No paired baseline/staged runtime and token logs from kc were available, so projected seconds and token savings remain unbenchmarked.
7. No exact full model weight commit SHA was verified for the stronger DeBERTa model, nor was the short MiniLM revision expanded into a full immutable snapshot ID. Pin both before installing or benchmarking.
8. Transformers 5.22.1 + Torch 2.15.0 were individually verified with compatible Python classifiers/wheels, but not executed jointly on Apple Silicon using these exact checkpoints; full application compatibility is unverified.
9. The AlignScore repository’s pyproject.toml (declared 0.1.3) imposes old torch<2, transformers<5, NumPy/Lightning restrictions, making it a bad fit for the suggested modern NLI venv; latest tagged release date was not confirmed.
10. GLiNER 0.2.30 (31 October 2026) is newer than 0.2.29; the specific model checkpoint’s independent licence, revision and performance were not checked. Do not install an unspecified model.
11. ContractNLI and SciFact dataset and code licensing differ; do not treat paper citations or repo-level code licence as automatically granting redistribution rights to every document and model.
12. CLAIRE’s released workflow is provider/retrieval oriented and Python 3.12-based; not verified as offline or Python 3.14 compatible. Its method is more appropriate than installing it.
13. Research on truth discovery does not validate treating replicated auditor statements as independent votes, or equating recency with correctness.
14. None of the published NLI, NER, coreference or calibration tools has verified precision/recall on technical audit-report pair classification and root-level resolution. Any percentage gain claimed before a local blinded evaluation is a hypothesis.
15. We did not find evidence supporting a cloud LLM over a locally prompted existing LLM sufficient to override confidentiality concerns. Cloud would transfer project text and requires explicit user/security permission.

Access and verification disclosure

• Primary PyPI listings, model cards, GitHub repository metadata and ACL/EMNLP/TACL paper pages were accessed via web search/open tools; this is source inspection, not a local package installation or execution.
• Dateparser had a stale cached page view for 1.4.2; the newer 1.4.3, 2026-09-03 entry was independently located and is used in this report.
• GLiNER likewise had older cached listings; the exact 0.2.30 PyPI record was located.
• No full PDF paper was required to establish the summary-level published metrics used here; methods/figures not present in the opened source should remain unverified rather than reconstructed from memory.
• The supplied audit files are treated as source evidence for examples, not as ground truth labels of a completed kc benchmark.

15. Recommended sign-off criteria

A change should be accepted only if the evidence ledger and blind evaluation support a statement of this form:

> “Relative to kc baseline `X`, source-context policy `Y` reduced sampled **independent-root human review actions** from A to B, with a documented 95% uncertainty interval; all 45 existing labelled positives remained accessible, K previously missed positives were recovered by the retrieval experiment, and no new miss was observed in the separate prospective test set. The model path was shadow-only and consumed M local tokens plus N LLM tokens, versus baseline P.”

Until actual values A/B/K/M/N/P are measured, do not fill them in. Prefer a modest verified improvement over an invented large one.

Final call

Implement a disciplined context and issue-identity layer within the existing kc architecture. This is the best-supported approach for the failure pattern reported: it uses explicit source declarations, preserves histories, groups duplicate decisions and keeps real conflicts visible. Next, test better cross-document retrieval. Evaluate MiniLM/DeBERTa only as an optional local signal, and let the result determine whether they belong in production. It is entirely plausible that at this corpus size, a strong LLM reading the right small excerpts will outperform the small NLI models; the research provides no basis to claim otherwise.

────────

16. Primary source register (verifiable URLs)

Core libraries and releases

• markdown-it-py — https://pypi.org/project/markdown-it-py/ — MIT; 4.2.0, 2026-05-07.
• python-frontmatter — https://pypi.org/project/python-frontmatter/ — MIT; 1.3.0, 2026-05-20.
• dateparser — https://pypi.org/project/dateparser/1.4.3/ — BSD-3-Clause; 1.4.3, 2026-09-03.
• NetworkX — https://pypi.org/project/networkx/3.7/ — BSD-3-Clause; 3.7, 2026-09-21; excludes Python 3.14.1.
• RapidFuzz — https://pypi.org/project/RapidFuzz/ — MIT; 3.14.6, 2026-08-30.
• scikit-learn — https://pypi.org/project/scikit-learn/1.9.1/ — BSD-3-Clause; 1.9.1, 2026-09-10.
• statsmodels — https://pypi.org/project/statsmodels/0.15.0/ — BSD-3-Clause; 0.15.0, 2026-08-27.
• Pydantic — https://pypi.org/project/pydantic/2.14.2/ — MIT; 2.14.2, 2026-10-29.
• spaCy — https://pypi.org/project/spacy/ — MIT; 3.8.18, 2026-10-26.
• GLiNER — https://pypi.org/project/gliner/0.2.30/ — Apache-2.0; 0.2.30, 2026-10-31.
• cleanlab — https://pypi.org/project/cleanlab/ — Apache-2.0; 2.9.0, 2026-01-13.

Inference runtime, models and checkpoints

• Transformers — https://pypi.org/project/transformers/5.22.1/ — Apache-2.0; 5.22.1, 2026-10-30.
• PyTorch — https://pypi.org/project/torch/2.15.0/ — BSD-style/multiple SPDX components; 2.15.0, 2026-10-28; macOS ARM64/CPython 3.14 wheel.
• ONNX Runtime — https://pypi.org/project/onnxruntime/1.31.1/ — MIT; 1.31.1, 2026-10-26.
• nli-MiniLM2-L6-H768 — https://huggingface.co/cross-encoder/nli-MiniLM2-L6-H768/tree/main — Apache-2.0 model card; revision prefix b95119c.
• DeBERTa-v3-base-mnli-fever-anli — https://huggingface.co/MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli — MIT model card; see Eval results for MNLI/FEVER/ANLI accuracy.
• MiniCheck-Flan-T5-Large — https://huggingface.co/lytang/MiniCheck-Flan-T5-Large — MIT model card.

Research and benchmark methods

• CLAIRE/WikiCollide (2025): https://aclanthology.org/2025.emnlp-main.1765/ ; code https://github.com/stanford-oval/inconsistency-detection (Apache-2.0); dataset CC BY 4.0.
• MiniCheck (2024): https://aclanthology.org/2024.emnlp-main.499/ ; code https://github.com/Liyan06/MiniCheck (Apache-2.0; pyproject.toml 0.1.0).
• SummaC (2022): https://aclanthology.org/2022.tacl-1.10/ ; code https://github.com/tingofurro/summac (Apache-2.0); package https://pypi.org/project/summac/ (0.0.4, 2023-10-06).
• AlignScore (2023): https://aclanthology.org/2023.acl-long.634/ ; code https://github.com/yuh-zha/AlignScore (MIT; pyproject.toml declares 0.1.3 and old dependencies).
• ContractNLI (2021): https://aclanthology.org/2021.findings-emnlp.164/ ; dataset description/licence https://github.com/ShubhamKathiriya/Contract_NLI/blob/main/Dataset/README.md (CC BY 4.0).
• FEVER (2018): https://fever.ai/dataset/fever.html ; paper https://aclanthology.org/N18-1074/.
• FEVEROUS (2021): https://fever.ai/dataset/feverous.html.
• TRUE (2022): https://aclanthology.org/2022.naacl-main.287/.
• SciFact: https://github.com/allenai/scifact ; licence split https://github.com/allenai/scifact/blob/master/LICENSE.md.
• TruthFinder/veracity (KDD 2007): https://research.ibm.com/publications/truth-discovery-with-multiple-conflicting-information-providers-on-the-web.
• Confident learning (2021): https://research.google/pubs/confident-learning-estimating-uncertainty-in-dataset-labels/.

Supplied, local worked examples

• step4-post-fix-compliance-audit.md — explicitly superseded source with historically retained statements.
• step12-optional-hardening-final-state.md — current authoritative source with later decisions.
• audit-report-index.md, step13-audit-source-hygiene-and-publishable-pack.md — provenance hierarchy, current/historical report taxonomy.

End of report. No new kc script has been run and no precision/recall gains or Mac inference speeds have been measured as part of this research.
