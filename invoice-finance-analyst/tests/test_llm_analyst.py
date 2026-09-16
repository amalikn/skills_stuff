"""
Tests for scripts/llm_analyst.py — Phase 4 LLM analyst layer.

All tests are offline: the LLM call (call_llm) is mocked via unittest.mock.patch
so no OPENAI_API_KEY or real API connection is required.
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from scripts.llm_analyst import (
    DEFAULT_MODEL,
    SYSTEM_PROMPT,
    _df_to_markdown,
    _extract_period,
    _load_parquet_optional,
    _select_context_tables,
    _serialize_assumptions,
    _serialize_context,
    _write_analyst_report,
    build_user_prompt,
    call_llm,
    run_analyst,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def small_df() -> pd.DataFrame:
    return pd.DataFrame({
        "supplier_service_id": ["LOC000001", "LOC000002"],
        "amount":              [100.00, 200.00],
        "status":              ["matched", "invoice_only"],
    })


@pytest.fixture
def assumptions_df() -> pd.DataFrame:
    return pd.DataFrame({
        "parameter": ["AMOUNT_MATCH_TOLERANCE_ABS", "LOW_MARGIN_PCT_THRESHOLD"],
        "value":     [0.02, 0.05],
        "rationale": ["rounding standard", "target margin floor"],
    })


@pytest.fixture
def full_tables(small_df, assumptions_df) -> dict:
    return {
        "reconciliation_summary":  small_df.copy(),
        "invoice_no_sales":        small_df.copy(),
        "sales_no_invoice":        None,
        "amount_mismatches":       small_df.copy(),
        "assumptions":             assumptions_df.copy(),
        "phase2_assumptions":      None,
        "matched_lines":           pd.DataFrame({
            "supplier_service_id": ["LOC000001"],
            "billing_period_start": ["2026-03-01"],
            "inv_amount": [100.0],
        }),
    }


# ---------------------------------------------------------------------------
# TestDfToMarkdown
# ---------------------------------------------------------------------------

class TestDfToMarkdown:
    def test_none_returns_no_data(self):
        assert _df_to_markdown(None) == "_no data_"

    def test_empty_df_returns_no_data(self):
        assert _df_to_markdown(pd.DataFrame()) == "_no data_"

    def test_small_df_contains_headers(self, small_df):
        md = _df_to_markdown(small_df)
        assert "supplier_service_id" in md
        assert "amount" in md
        assert "LOC000001" in md

    def test_truncation_message_shown(self, small_df):
        # max_rows=1 on a 2-row df should show truncation note
        md = _df_to_markdown(small_df, max_rows=1)
        assert "showing 1 of 2 rows" in md

    def test_no_truncation_message_when_under_limit(self, small_df):
        md = _df_to_markdown(small_df, max_rows=10)
        assert "showing" not in md

    def test_separator_row_present(self, small_df):
        md = _df_to_markdown(small_df)
        lines = md.splitlines()
        assert any("---" in line for line in lines)


# ---------------------------------------------------------------------------
# TestLoadParquetOptional
# ---------------------------------------------------------------------------

class TestLoadParquetOptional:
    def test_returns_none_for_missing_file(self, tmp_path):
        result = _load_parquet_optional(tmp_path / "nonexistent.parquet")
        assert result is None

    def test_returns_dataframe_for_existing_file(self, tmp_path, small_df):
        path = tmp_path / "test.parquet"
        small_df.to_parquet(path, index=False)
        result = _load_parquet_optional(path)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2

    def test_loaded_dataframe_matches_original(self, tmp_path, small_df):
        path = tmp_path / "test.parquet"
        small_df.to_parquet(path, index=False)
        result = _load_parquet_optional(path)
        assert list(result.columns) == list(small_df.columns)


# ---------------------------------------------------------------------------
# TestSelectContextTables
# ---------------------------------------------------------------------------

class TestSelectContextTables:
    def test_returns_dict(self, full_tables):
        result = _select_context_tables(full_tables)
        assert isinstance(result, dict)

    def test_all_returned_keys_are_subset_of_input(self, full_tables):
        result = _select_context_tables(full_tables)
        assert set(result.keys()).issubset(set(full_tables.keys()))

    def test_returns_non_empty_result(self, full_tables):
        result = _select_context_tables(full_tables)
        assert len(result) > 0

    def test_none_values_preserved(self, full_tables):
        result = _select_context_tables(full_tables)
        # sales_no_invoice is None in full_tables
        if "sales_no_invoice" in result:
            assert result["sales_no_invoice"] is None


# ---------------------------------------------------------------------------
# TestSerializeContext
# ---------------------------------------------------------------------------

class TestSerializeContext:
    def test_none_table_renders_not_available(self, full_tables):
        full_tables["sales_no_invoice"] = None
        ctx = _serialize_context({"sales_no_invoice": None})
        assert "not available" in ctx

    def test_dataframe_table_renders_header(self, small_df):
        ctx = _serialize_context({"invoice_no_sales": small_df})
        assert "invoice_no_sales" in ctx
        assert "supplier_service_id" in ctx

    def test_row_count_shown_in_section_header(self, small_df):
        ctx = _serialize_context({"invoice_no_sales": small_df})
        assert "2 rows" in ctx

    def test_multiple_tables_all_present(self, small_df):
        ctx = _serialize_context({
            "invoice_no_sales": small_df,
            "amount_mismatches": small_df,
        })
        assert "invoice_no_sales" in ctx
        assert "amount_mismatches" in ctx


# ---------------------------------------------------------------------------
# TestSerializeAssumptions
# ---------------------------------------------------------------------------

class TestSerializeAssumptions:
    def test_no_assumption_tables_returns_fallback(self):
        tables = {"matched_lines": pd.DataFrame({"a": [1]})}
        result = _serialize_assumptions(tables)
        assert "no assumption tables" in result

    def test_assumptions_table_rendered(self, assumptions_df):
        tables = {"assumptions": assumptions_df}
        result = _serialize_assumptions(tables)
        assert "assumptions" in result
        assert "AMOUNT_MATCH_TOLERANCE_ABS" in result

    def test_none_assumption_table_skipped(self, assumptions_df):
        tables = {"assumptions": assumptions_df, "phase2_assumptions": None}
        result = _serialize_assumptions(tables)
        assert "assumptions" in result
        # None table should not appear as a header with empty content
        assert "AMOUNT_MATCH_TOLERANCE_ABS" in result


# ---------------------------------------------------------------------------
# TestExtractPeriod
# ---------------------------------------------------------------------------

class TestExtractPeriod:
    def test_extracts_period_from_matched_lines(self):
        df = pd.DataFrame({"billing_period_start": ["2026-03-01", "2026-03-01"]})
        tables = {"matched_lines": df}
        result = _extract_period(tables)
        assert "2026-03-01" in result

    def test_returns_unknown_when_matched_lines_absent(self):
        result = _extract_period({"matched_lines": None})
        assert result == "unknown"

    def test_returns_unknown_when_column_missing(self):
        df = pd.DataFrame({"amount": [100.0]})
        result = _extract_period({"matched_lines": df})
        assert result == "unknown"

    def test_multiple_periods_joined(self):
        df = pd.DataFrame({"billing_period_start": ["2026-02-01", "2026-03-01"]})
        result = _extract_period({"matched_lines": df})
        assert "2026-02-01" in result
        assert "2026-03-01" in result


# ---------------------------------------------------------------------------
# TestBuildUserPrompt
# ---------------------------------------------------------------------------

class TestBuildUserPrompt:
    def test_run_id_in_output(self):
        prompt = build_user_prompt("ctx", "assume", {"run_id": "abc12345"})
        assert "abc12345" in prompt

    def test_period_in_output(self):
        prompt = build_user_prompt("ctx", "assume", {"period": "2026-03-01"})
        assert "2026-03-01" in prompt

    def test_context_included(self):
        prompt = build_user_prompt("MY_CONTEXT_BLOCK", "assume", {})
        assert "MY_CONTEXT_BLOCK" in prompt

    def test_assumptions_included(self):
        prompt = build_user_prompt("ctx", "MY_ASSUMPTIONS_BLOCK", {})
        assert "MY_ASSUMPTIONS_BLOCK" in prompt

    def test_missing_tables_listed(self):
        prompt = build_user_prompt(
            "ctx", "assume",
            {"tables_missing": ["rate_variances", "usage_spikes"]}
        )
        assert "rate_variances" in prompt
        assert "usage_spikes" in prompt


# ---------------------------------------------------------------------------
# TestSystemPrompt
# ---------------------------------------------------------------------------

class TestSystemPrompt:
    def test_evidence_rule_present(self):
        assert "Evidence Rule" in SYSTEM_PROMPT

    def test_citation_format_shown(self):
        assert "table:" in SYSTEM_PROMPT
        assert "metric:" in SYSTEM_PROMPT
        assert "value:" in SYSTEM_PROMPT

    def test_nine_sections_present(self):
        # All 9 required section names present
        for section in [
            "Summary", "Files Analyzed", "Assumptions", "Calculated Findings",
            "Variances", "Suspected Causes", "Recommended Checks",
            "Data Gaps", "Confidence Rating",
        ]:
            assert section in SYSTEM_PROMPT

    def test_no_external_data_constraint(self):
        assert "external" in SYSTEM_PROMPT.lower()

    def test_root_cause_categories_listed(self):
        for cat in ["mapping_gap", "billing_error", "timing", "rate_change"]:
            assert cat in SYSTEM_PROMPT


# ---------------------------------------------------------------------------
# TestCallLlm
# ---------------------------------------------------------------------------

class TestCallLlm:
    @patch("scripts.llm_analyst.openai.OpenAI")
    def test_returns_response_text(self, mock_cls):
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value.choices[0].message.content = (
            "## Summary\n\nTest report content."
        )
        result = call_llm("test prompt", model="test-model")
        assert "Test report content" in result

    @patch("scripts.llm_analyst.openai.OpenAI")
    def test_uses_system_prompt(self, mock_cls):
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value.choices[0].message.content = "ok"
        call_llm("test prompt", model="test-model")
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args.kwargs["messages"]
        system_msgs = [m for m in messages if m["role"] == "system"]
        assert len(system_msgs) == 1
        assert "Evidence Rule" in system_msgs[0]["content"]

    @patch("scripts.llm_analyst.openai.OpenAI")
    def test_custom_base_url_passed(self, mock_cls):
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value.choices[0].message.content = "ok"
        call_llm("prompt", model="deepseek-chat", base_url="https://api.deepseek.com")
        mock_cls.assert_called_once()
        init_kwargs = mock_cls.call_args.kwargs
        assert init_kwargs.get("base_url") == "https://api.deepseek.com"

    @patch("scripts.llm_analyst.openai.OpenAI")
    def test_explicit_api_key_used(self, mock_cls):
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value.choices[0].message.content = "ok"
        call_llm("prompt", model="m", api_key="sk-test-key")
        init_kwargs = mock_cls.call_args.kwargs
        assert init_kwargs.get("api_key") == "sk-test-key"

    @patch("scripts.llm_analyst.openai.OpenAI")
    def test_empty_response_returns_empty_string(self, mock_cls):
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value.choices[0].message.content = None
        result = call_llm("prompt", model="m")
        assert result == ""


# ---------------------------------------------------------------------------
# TestWriteAnalystReport
# ---------------------------------------------------------------------------

class TestWriteAnalystReport:
    def test_file_created(self, tmp_path):
        _write_analyst_report("# Report\n\nContent.", tmp_path, "abc12345", "test-model")
        assert (tmp_path / "analyst_report.md").exists()

    def test_run_id_in_file(self, tmp_path):
        _write_analyst_report("body", tmp_path, "abc12345", "test-model")
        content = (tmp_path / "analyst_report.md").read_text()
        assert "abc12345" in content

    def test_model_in_header(self, tmp_path):
        _write_analyst_report("body", tmp_path, "run1", "deepseek-chat")
        content = (tmp_path / "analyst_report.md").read_text()
        assert "deepseek-chat" in content

    def test_analyst_content_present(self, tmp_path):
        _write_analyst_report("## Summary\n\nTest finding.", tmp_path, "r1", "m")
        content = (tmp_path / "analyst_report.md").read_text()
        assert "Test finding." in content


# ---------------------------------------------------------------------------
# TestRunAnalyst
# ---------------------------------------------------------------------------

MOCK_REPORT = (
    "## Summary\n\nMock summary [table: reconciliation_summary | metric: row_count | value: 2].\n\n"
    "## Files Analyzed\n\nMock files.\n\n"
    "## Assumptions\n\nMock assumptions.\n\n"
    "## Calculated Findings\n\nMock findings.\n\n"
    "## Variances\n\nMock variances.\n\n"
    "## Suspected Causes\n\nMock causes.\n\n"
    "## Recommended Checks\n\nMock checks.\n\n"
    "## Data Gaps\n\nMock gaps.\n\n"
    "## Confidence Rating\n\nMedium.\n"
)


class TestRunAnalyst:
    @patch("scripts.llm_analyst.call_llm", return_value=MOCK_REPORT)
    def test_creates_output_dir(self, _mock, tmp_path):
        out = tmp_path / "analyst_out"
        run_analyst(output_dir=out)
        assert out.exists()

    @patch("scripts.llm_analyst.call_llm", return_value=MOCK_REPORT)
    def test_creates_analyst_report_md(self, _mock, tmp_path):
        out = tmp_path / "out"
        run_analyst(output_dir=out)
        assert (out / "analyst_report.md").exists()

    @patch("scripts.llm_analyst.call_llm", return_value=MOCK_REPORT)
    def test_returns_dict_with_run_id(self, _mock, tmp_path):
        result = run_analyst(output_dir=tmp_path / "out")
        assert "run_id" in result
        assert len(result["run_id"]) == 8

    @patch("scripts.llm_analyst.call_llm", return_value=MOCK_REPORT)
    def test_returns_dict_with_report_path(self, _mock, tmp_path):
        result = run_analyst(output_dir=tmp_path / "out")
        assert "report_path" in result
        assert Path(result["report_path"]).exists()

    @patch("scripts.llm_analyst.call_llm", return_value=MOCK_REPORT)
    def test_missing_parquets_listed_in_tables_missing(self, _mock, tmp_path):
        # No db/ files exist in tmp_path so all tables should be missing
        import scripts.llm_analyst as mod
        orig_db = mod.DB
        mod.DB = tmp_path / "db"  # point to empty dir
        try:
            result = run_analyst(output_dir=tmp_path / "out")
            assert len(result["tables_missing"]) > 0
            assert len(result["tables_loaded"]) == 0
        finally:
            mod.DB = orig_db

    @patch("scripts.llm_analyst.call_llm", return_value=MOCK_REPORT)
    def test_report_content_written_to_file(self, _mock, tmp_path):
        out = tmp_path / "out"
        run_analyst(output_dir=out)
        content = (out / "analyst_report.md").read_text()
        assert "Mock summary" in content

    @patch("scripts.llm_analyst.call_llm", return_value=MOCK_REPORT)
    def test_model_passed_to_call_llm(self, mock_call, tmp_path):
        run_analyst(output_dir=tmp_path / "out", model="deepseek-chat")
        call_kwargs = mock_call.call_args.kwargs
        assert call_kwargs.get("model") == "deepseek-chat"
