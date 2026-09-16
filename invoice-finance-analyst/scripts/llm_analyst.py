"""
LLM Analyst Layer — Phase 4

Reads Phase 1B/2/3 parquet outputs and calls an LLM to produce a structured
analyst report: executive summary, exception narrative, root-cause grouping,
evidence table, and open questions.

Provider-agnostic: uses the OpenAI-compatible API interface supported by
OpenAI, DeepSeek, Groq, Mistral, Ollama, LM Studio, Together AI, and others.

Evidence Rule: every LLM statement must cite [table | metric | value].
LLM is commentary only — all numeric values come from Python/pandas, not the model.

Configuration (env vars or CLI flags):
    OPENAI_API_KEY   — provider API key (or --api-key)
    OPENAI_BASE_URL  — provider endpoint (or --base-url); defaults to OpenAI
    INVOICE_MODEL    — model name override (or --model)

Usage:
    # OpenAI (default)
    python scripts/llm_analyst.py

    # DeepSeek
    OPENAI_BASE_URL=https://api.deepseek.com OPENAI_API_KEY=sk-... \\
        python scripts/llm_analyst.py --model deepseek-chat

    # Groq
    OPENAI_BASE_URL=https://api.groq.com/openai/v1 OPENAI_API_KEY=gsk_... \\
        python scripts/llm_analyst.py --model llama-3.3-70b-versatile

    # Ollama (local, no key needed)
    OPENAI_BASE_URL=http://localhost:11434/v1 OPENAI_API_KEY=ollama \\
        python scripts/llm_analyst.py --model llama3.2

    # Explicit flags
    python scripts/llm_analyst.py --base-url https://api.deepseek.com \\
        --api-key sk-... --model deepseek-chat

Inputs (from db/):
    Phase 1B: run_summary, reconciliation_summary, matched_lines,
              invoice_no_sales, sales_no_invoice, amount_mismatches,
              data_quality_issues, assumptions
    Phase 2:  rate_card_mismatches, low_margin_exceptions,
              margin_by_customer  (optional — skipped gracefully if absent)
    Phase 3:  usage_spikes, recurring_changes, margin_movement,
              new_services, removed_services  (optional)

Output:
    output/phase4_<run_id>/analyst_report.md
"""

from __future__ import annotations

import argparse
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path

import openai
import pandas as pd

ROOT = Path(__file__).parent.parent
DB = ROOT / "db"

DEFAULT_MODEL = os.environ.get("INVOICE_MODEL", "gpt-4o-mini")
MAX_ROWS_PER_TABLE = 50


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ts() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _load_parquet_optional(path: Path) -> pd.DataFrame | None:
    """Return DataFrame if file exists, None otherwise — missing phases are ok."""
    if path.exists():
        return pd.read_parquet(path)
    return None


def _df_to_markdown(df: pd.DataFrame | None, max_rows: int = MAX_ROWS_PER_TABLE) -> str:
    """Convert DataFrame to a markdown table string, capped at max_rows."""
    if df is None or df.empty:
        return "_no data_"
    subset = df.head(max_rows)
    header = "| " + " | ".join(str(c) for c in subset.columns) + " |"
    sep    = "| " + " | ".join("---" for _ in subset.columns) + " |"
    rows   = [
        "| " + " | ".join(str(v) for v in row) + " |"
        for row in subset.itertuples(index=False)
    ]
    md = "\n".join([header, sep] + rows)
    if len(df) > max_rows:
        md += f"\n\n_(showing {max_rows} of {len(df)} rows)_"
    return md


def _select_context_tables(
    tables: dict[str, pd.DataFrame | None],
) -> dict[str, pd.DataFrame | None]:
    """
    Return the subset of tables to include in the LLM context.

    TODO — implement this function.

    The full db/ parquet set spans 22 tables across Phases 1B–3. Passing all of them
    inflates the prompt without improving commentary quality — the LLM needs the
    *exception* tables, not every supporting aggregate.

    Design guidance:
    - Prioritise tables that answer "what is wrong and how much does it cost?"
    - Exception/anomaly tables are highest signal — include when non-None:
        invoice_no_sales, sales_no_invoice, amount_mismatches,
        rate_card_mismatches, low_margin_exceptions, usage_spikes, recurring_changes
    - Aggregate summaries add useful context selectively:
        reconciliation_summary, margin_by_customer, margin_movement
    - Assumption/metadata tables (assumptions, phase*_assumptions, run_summary,
      source_file_inventory) are serialised separately — EXCLUDE here.
    - None values are fine to include; they render as "_not available_" and the
      LLM will flag the missing phase in its Data Gaps section.

    Target: 6–10 tables. More than 12 is usually counter-productive.

    Args:
        tables: full dict of all loaded parquets, keyed by basename (no extension).

    Returns:
        Subset dict to pass to the LLM context serialiser.
    """
    priority = [
        "reconciliation_summary",
        "data_quality_issues",
        "invoice_no_sales",
        "sales_no_invoice",
        "amount_mismatches",
        "rate_card_mismatches",
        "low_margin_exceptions",
        "usage_spikes",
        "recurring_changes",
        "margin_movement",
    ]
    return {k: tables[k] for k in priority if k in tables}


def _serialize_context(tables: dict[str, pd.DataFrame | None]) -> str:
    """Render selected tables to labelled markdown blocks for the LLM prompt."""
    selected = _select_context_tables(tables)
    parts: list[str] = []
    for name, df in selected.items():
        if df is None:
            parts.append(f"## {name}\n_not available (phase skipped or file absent)_")
        else:
            parts.append(f"## {name} ({len(df)} rows)\n{_df_to_markdown(df)}")
    return "\n\n".join(parts)


def _serialize_assumptions(tables: dict[str, pd.DataFrame | None]) -> str:
    """Render all *_assumptions tables into a single block."""
    assumption_keys = [k for k in tables if "assumptions" in k]
    parts: list[str] = []
    for key in sorted(assumption_keys):
        df = tables.get(key)
        if df is not None and not df.empty:
            parts.append(f"### {key}\n{_df_to_markdown(df, max_rows=100)}")
    return "\n\n".join(parts) if parts else "_no assumption tables loaded_"


def _extract_period(tables: dict[str, pd.DataFrame | None]) -> str:
    """Derive the analysis billing period from matched_lines if available."""
    matched = tables.get("matched_lines")
    if matched is not None and not matched.empty and "billing_period_start" in matched.columns:
        periods = matched["billing_period_start"].dropna().unique()
        if len(periods):
            return ", ".join(sorted(str(p) for p in periods))
    return "unknown"


# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are a financial analyst reviewing an invoice reconciliation analysis produced \
by a Python data pipeline. All numeric values in the provided context are \
authoritative — calculated by Python/pandas. Do not re-compute, adjust, or invent values.

## Evidence Rule (mandatory)
Every statement in your response MUST include an inline citation in exactly this format:
  [table: <table_name> | metric: <column_or_aggregate> | value: <value>]

Example: "Three supplier charges had no matching revenue record \
[table: invoice_no_sales | metric: row_count | value: 3]."

Any statement without a citation is treated as unsupported and must be omitted.

## Hard Constraints
- Do not use external market data, CPI, inflation benchmarks, or industry averages.
- Do not invent service names, customer IDs, or dollar amounts.
- If a phase was skipped or a file is absent, state that explicitly — do not guess.
- Calculated findings (numeric tables) and LLM commentary must appear in separate sections.
  Never override or rephrase a calculated value.

## Root-Cause Categories (Step 12)
When grouping exceptions use only these categories:
  mapping_gap | billing_error | timing | rate_change |
  new_service | data_quality | requires_review

## Required Response Format
Produce exactly these 9 sections in this order (use ## headers):

1. **Summary** — ≤300 words. Files analyzed, period, total cost, total revenue, overall \
margin, top 3–5 exception categories by value impact, highest-severity items.
2. **Files Analyzed** — filenames, row counts, analysis period from run_summary.
3. **Assumptions** — column mappings, tolerances, thresholds declared by the pipeline.
4. **Calculated Findings** — key metrics table (totals, match rates, margin percentages).
5. **Variances** — top exceptions by $ value impact, grouped by root-cause category.
6. **Suspected Causes** — root-cause category per exception group with rationale.
7. **Recommended Checks** — specific, actionable next steps for each top exception.
8. **Data Gaps** — missing files, unmapped columns, unresolved duplicates, skipped phases.
9. **Confidence Rating** — Low / Medium / High with one-sentence justification.
"""


def build_user_prompt(
    context_md: str,
    assumptions_md: str,
    run_metadata: dict,
) -> str:
    run_id  = run_metadata.get("run_id", "unknown")
    period  = run_metadata.get("period", "unknown")
    loaded  = run_metadata.get("tables_loaded", [])
    missing = run_metadata.get("tables_missing", [])

    return (
        f"# Invoice Reconciliation Context\n\n"
        f"Run ID: {run_id}\n"
        f"Analysis period: {period}\n"
        f"Generated: {_ts()}\n"
        f"Tables loaded: {', '.join(loaded) if loaded else 'none'}\n"
        f"Tables absent: {', '.join(missing) if missing else 'none'}\n\n"
        f"---\n\n"
        f"## Pipeline Assumptions (declared by Python scripts)\n\n"
        f"{assumptions_md}\n\n"
        f"---\n\n"
        f"## Exception and Summary Data\n\n"
        f"{context_md}\n\n"
        f"---\n\n"
        f"Produce the 9-section analyst report. Cite every finding with "
        f"[table: <name> | metric: <column> | value: <value>].\n"
    )


# ---------------------------------------------------------------------------
# LLM call — OpenAI-compatible interface
# ---------------------------------------------------------------------------

def call_llm(
    user_prompt: str,
    model: str = DEFAULT_MODEL,
    base_url: str | None = None,
    api_key: str | None = None,
) -> str:
    """
    Call any OpenAI-compatible LLM endpoint.

    Resolves credentials in this order: explicit arg → env var → default.
    Works with OpenAI, DeepSeek, Groq, Mistral, Ollama, LM Studio, Together, etc.
    """
    resolved_key = (
        api_key
        or os.environ.get("OPENAI_API_KEY")
        or "no-key"  # some local providers (Ollama) don't need one
    )
    resolved_url = (
        base_url
        or os.environ.get("OPENAI_BASE_URL")
        # None → openai SDK uses its default (api.openai.com)
    )

    client = openai.OpenAI(
        api_key=resolved_key,
        base_url=resolved_url,
    )
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt},
        ],
        max_tokens=3000,
    )
    return response.choices[0].message.content or ""


# ---------------------------------------------------------------------------
# Output writer
# ---------------------------------------------------------------------------

def _write_analyst_report(
    text: str,
    output_dir: Path,
    run_id: str,
    model: str,
) -> Path:
    dest = output_dir / "analyst_report.md"
    header = (
        f"# Analyst Report\n\n"
        f"Run ID: `{run_id}`  \n"
        f"Generated: {_ts()}  \n"
        f"Model: `{model}`\n\n"
        f"---\n\n"
    )
    dest.write_text(header + text, encoding="utf-8")
    return dest


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def run_analyst(
    output_dir: Path | None = None,
    model: str = DEFAULT_MODEL,
    base_url: str | None = None,
    api_key: str | None = None,
) -> dict:
    run_id = str(uuid.uuid4())[:8]

    if output_dir is None:
        output_dir = ROOT / "output" / f"phase4_{run_id}"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n=== Invoice LLM Analyst Run: {run_id} ===")
    print(f"  model   : {model}")
    print(f"  output  : {output_dir}")

    # --- load all parquets ---
    all_table_names = [
        # Phase 1B
        "run_summary", "source_file_inventory", "data_quality_issues",
        "reconciliation_summary", "matched_lines", "invoice_no_sales",
        "sales_no_invoice", "amount_mismatches", "assumptions",
        # Phase 2
        "rate_variances", "rate_card_mismatches", "margin_by_customer",
        "margin_by_service_type", "low_margin_exceptions", "phase2_assumptions",
        # Phase 3
        "mom_variance", "new_services", "removed_services",
        "usage_spikes", "recurring_changes", "margin_movement", "phase3_assumptions",
    ]
    tables: dict[str, pd.DataFrame | None] = {
        name: _load_parquet_optional(DB / f"{name}.parquet")
        for name in all_table_names
    }

    loaded  = [n for n, df in tables.items() if df is not None]
    missing = [n for n, df in tables.items() if df is None]
    print(f"\nLoaded {len(loaded)}/{len(all_table_names)} tables")
    if missing:
        print(f"  absent : {', '.join(missing)}")

    run_metadata = {
        "run_id":         run_id,
        "period":         _extract_period(tables),
        "tables_loaded":  loaded,
        "tables_missing": missing,
    }

    context_md     = _serialize_context(tables)
    assumptions_md = _serialize_assumptions(tables)
    user_prompt    = build_user_prompt(context_md, assumptions_md, run_metadata)

    print("\nCalling LLM...")
    analyst_text = call_llm(user_prompt, model=model, base_url=base_url, api_key=api_key)
    print(f"  response : {len(analyst_text)} chars")

    report_path = _write_analyst_report(analyst_text, output_dir, run_id, model)
    print(f"\nWrote : {report_path}")
    print(f"Done.  Run ID: {run_id}")

    return {
        "run_id":         run_id,
        "output_dir":     str(output_dir),
        "report_path":    str(report_path),
        "tables_loaded":  loaded,
        "tables_missing": missing,
        "model":          model,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "LLM analyst layer — generates a 9-section structured report from "
            "Phase 1B/2/3 parquet outputs. Works with any OpenAI-compatible endpoint."
        )
    )
    parser.add_argument(
        "--model", default=DEFAULT_MODEL,
        help="Model name (e.g. gpt-4o-mini, deepseek-chat, llama3.2)"
    )
    parser.add_argument(
        "--base-url", default=None,
        help="Provider API base URL (overrides OPENAI_BASE_URL env var)"
    )
    parser.add_argument(
        "--api-key", default=None,
        help="Provider API key (overrides OPENAI_API_KEY env var)"
    )
    parser.add_argument(
        "--output-dir", default=None,
        help="Override output directory"
    )
    args = parser.parse_args()

    out_dir = Path(args.output_dir) if args.output_dir else None
    run_analyst(
        output_dir=out_dir,
        model=args.model,
        base_url=args.base_url,
        api_key=args.api_key,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
