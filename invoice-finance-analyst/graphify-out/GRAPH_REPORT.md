# Graph Report - invoice-finance-analyst  (2026-05-23)

## Corpus Check
- 12 files · ~61,739 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 428 nodes · 632 edges · 19 communities detected
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 130 edges (avg confidence: 0.77)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]

## God Nodes (most connected - your core abstractions)
1. `validate()` - 38 edges
2. `run_analyst()` - 16 edges
3. `TestValidInvoiceCSV` - 14 edges
4. `run_analysis()` - 14 edges
5. `TestReconciliation` - 13 edges
6. `ValidationResult` - 13 edges
7. `run_trend_analysis()` - 13 edges
8. `run_rate_card_analysis()` - 12 edges
9. `TestEndToEndPhase3` - 10 edges
10. `TestEndToEnd` - 10 edges

## Surprising Connections (you probably didn't know these)
- `ensure_phase3_db()` --calls--> `ingest()`  [INFERRED]
  tests/test_trend_analysis.py → scripts/load_inputs.py
- `mom_variance()` --calls--> `build_mom_variance()`  [INFERRED]
  tests/test_trend_analysis.py → scripts/trend_analysis.py
- `new_services()` --calls--> `build_new_services()`  [INFERRED]
  tests/test_trend_analysis.py → scripts/trend_analysis.py
- `removed_services()` --calls--> `build_removed_services()`  [INFERRED]
  tests/test_trend_analysis.py → scripts/trend_analysis.py
- `run_result()` --calls--> `run_trend_analysis()`  [INFERRED]
  tests/test_trend_analysis.py → scripts/trend_analysis.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.07
Nodes (27): tests/test_validate_inputs.py — Phase 1A exit gate tests.  Covers all Phase 1A e, sha256(), TestBadDateField, TestBadNumericField, TestDuplicateDetection, TestMappedColumnAbsent, TestMissingFile, TestMissingRequiredMapping (+19 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (30): _build_amount_mismatches(), build_assumptions(), _build_invoice_only(), _build_matched(), build_quality_issues(), build_reconciliation_summary(), build_run_summary(), _build_sales_only() (+22 more)

### Community 2 - "Community 2"
Cohesion: 0.05
Nodes (37): margin_movement(), mom_variance(), new_services(), tests/test_trend_analysis.py — Phase 3 trend detection tests.  Prior period fixt, Verify spike detection fires at just above 2× threshold., Verify exactly 2× is not flagged (strict greater-than)., recurring_changes(), removed_services() (+29 more)

### Community 3 - "Community 3"
Cohesion: 0.05
Nodes (32): build_low_margin_exceptions(), build_margin_by_customer(), build_margin_by_service_type(), build_phase2_assumptions(), build_rate_card_mismatches(), build_rate_variances(), main(), _now() (+24 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (31): build_user_prompt(), call_llm(), _load_parquet_optional(), main(), LLM Analyst Layer — Phase 4  Reads Phase 1B/2/3 parquet outputs and calls an LLM, Render all *_assumptions tables into a single block., Call any OpenAI-compatible LLM endpoint.      Resolves credentials in this order, Return DataFrame if file exists, None otherwise — missing phases are ok. (+23 more)

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (3): TestMarginByCustomer, TestMarginByServiceType, TestRateCardInput

### Community 6 - "Community 6"
Cohesion: 0.18
Nodes (14): _archive(), ingest(), load_csv(), main(), print_summary(), load_inputs.py — Phase 1B CSV loader: validate → normalise → write parquet.  Fol, Archive existing parquet if present, write new one with snappy compression., Load, normalise, and persist one CSV to db/. Returns the DataFrame. (+6 more)

### Community 7 - "Community 7"
Cohesion: 0.21
Nodes (6): Return the subset of tables to include in the LLM context.      TODO — implement, Render selected tables to labelled markdown blocks for the LLM prompt., _select_context_tables(), _serialize_context(), TestSelectContextTables, TestSerializeContext

### Community 8 - "Community 8"
Cohesion: 0.2
Nodes (1): TestEndToEndPhase3

### Community 9 - "Community 9"
Cohesion: 0.2
Nodes (1): TestEndToEnd

### Community 10 - "Community 10"
Cohesion: 0.36
Nodes (3): _df_to_markdown(), Convert DataFrame to a markdown table string, capped at max_rows., TestDfToMarkdown

### Community 11 - "Community 11"
Cohesion: 0.22
Nodes (1): TestEndToEndPhase2

### Community 12 - "Community 12"
Cohesion: 0.25
Nodes (1): TestMomVariance

### Community 13 - "Community 13"
Cohesion: 0.29
Nodes (1): TestPriorInput

### Community 14 - "Community 14"
Cohesion: 0.29
Nodes (1): TestRecurringChanges

### Community 15 - "Community 15"
Cohesion: 0.43
Nodes (3): _extract_period(), Derive the analysis billing period from matched_lines if available., TestExtractPeriod

### Community 16 - "Community 16"
Cohesion: 0.29
Nodes (1): TestSourceData

### Community 17 - "Community 17"
Cohesion: 0.33
Nodes (1): TestMarginMovement

### Community 18 - "Community 18"
Cohesion: 0.33
Nodes (1): TestSystemPrompt

## Knowledge Gaps
- **45 isolated node(s):** `tests/test_trend_analysis.py — Phase 3 trend detection tests.  Prior period fixt`, `Verify spike detection fires at just above 2× threshold.`, `Verify exactly 2× is not flagged (strict greater-than).`, `TestCallLlm`, `TestRunAnalyst` (+40 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 8`** (10 nodes): `TestEndToEndPhase3`, `.test_all_tables_present()`, `.test_margin_movement_count()`, `.test_new_services_count()`, `.test_output_markdown_written()`, `.test_output_parquets_written()`, `.test_recurring_changes_count()`, `.test_removed_services_count()`, `.test_run_completes()`, `.test_usage_spikes_count()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 9`** (10 nodes): `TestEndToEnd`, `.test_all_tables_present()`, `.test_amount_mismatch_row_count()`, `.test_invoice_only_row_count()`, `.test_matched_lines_row_count()`, `.test_output_markdown_written()`, `.test_output_parquets_written()`, `.test_run_completes()`, `.test_run_summary_counts()`, `.test_sales_only_row_count()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 11`** (9 nodes): `TestEndToEndPhase2`, `.test_all_tables_present()`, `.test_low_margin_exceptions_count()`, `.test_margin_by_customer_count()`, `.test_margin_by_service_type_count()`, `.test_output_markdown_written()`, `.test_output_parquets_written()`, `.test_rate_card_mismatches_count()`, `.test_run_completes()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 12`** (8 nodes): `TestMomVariance`, `.test_has_required_columns()`, `.test_loc000001_not_tracked()`, `.test_loc000002_change()`, `.test_loc000003_spike()`, `.test_loc000004_stable()`, `.test_loc000006_not_tracked()`, `.test_three_tracked_services()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 13`** (7 nodes): `TestPriorInput`, `.test_prior_has_amount_col()`, `.test_prior_has_service_id()`, `.test_prior_invoice_excludes_loc000001()`, `.test_prior_invoice_includes_loc000006()`, `.test_prior_invoice_row_count()`, `.test_prior_sales_row_count()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 14`** (7 nodes): `TestRecurringChanges`, `.test_all_exceed_threshold()`, `.test_loc000002_flagged()`, `.test_loc000003_flagged()`, `.test_loc000004_not_flagged()`, `.test_threshold_value()`, `.test_two_recurring_changes()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 16`** (7 nodes): `TestSourceData`, `.test_invoice_amount_total()`, `.test_invoice_has_canonical_amount_col()`, `.test_invoice_row_count()`, `.test_sales_has_canonical_revenue_col()`, `.test_sales_revenue_total()`, `.test_sales_row_count()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 17`** (6 nodes): `TestMarginMovement`, `.test_has_required_columns()`, `.test_loc000001_excluded_new_service()`, `.test_loc000003_margin_declined()`, `.test_loc000004_margin_improved()`, `.test_two_services_tracked()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 18`** (6 nodes): `TestSystemPrompt`, `.test_citation_format_shown()`, `.test_evidence_rule_present()`, `.test_nine_sections_present()`, `.test_no_external_data_constraint()`, `.test_root_cause_categories_listed()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ensure_phase3_db()` connect `Community 6` to `Community 2`?**
  _High betweenness centrality (0.176) - this node is a cross-community bridge._
- **Why does `ensure_phase2_db()` connect `Community 6` to `Community 3`?**
  _High betweenness centrality (0.169) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `validate()` (e.g. with `.test_passes()` and `.test_row_count()`) actually correct?**
  _`validate()` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `run_analyst()` (e.g. with `test_creates_output_dir()` and `test_creates_analyst_report_md()`) actually correct?**
  _`run_analyst()` has 7 INFERRED edges - model-reasoned connections that need verification._
- **What connects `tests/test_trend_analysis.py — Phase 3 trend detection tests.  Prior period fixt`, `Verify spike detection fires at just above 2× threshold.`, `Verify exactly 2× is not flagged (strict greater-than).` to the rest of the system?**
  _45 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.07 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.05 - nodes in this community are weakly interconnected._