"""
rate_card_analysis.py — Phase 2: rate card comparison and margin reporting.

Reads Phase 1B reconciliation outputs from db/, joins to rate card and service map
parquets, and produces margin and rate-variance output tables.

Required inputs (from Phase 1B + load_inputs.py):
  db/matched_lines.parquet      — Phase 1B reconciliation output
  db/rate_card.parquet          — loaded via: load_inputs.py --csv rate_card.csv ...

Optional inputs:
  db/service_map.parquet        — loaded via: load_inputs.py --csv service_map.csv ...

Output tables:
  rate_variances           — actual vs expected cost per matched service line
  rate_card_mismatches     — lines where rate variance exceeds tolerance
  margin_by_customer       — direct margin grouped by customer
  margin_by_service_type   — direct margin grouped by service type
  low_margin_exceptions    — lines below LOW_MARGIN_PCT_THRESHOLD

Each table written to:
  db/<table>.parquet              — machine-readable audit trail
  output/<run_id>/<table>.md      — human-readable / LLM-consumable

Usage:
    python scripts/rate_card_analysis.py
    python scripts/rate_card_analysis.py --matched db/matched_lines.parquet \\
        --rate-card db/rate_card.parquet
"""

from __future__ import annotations

import argparse
import sys
import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd

_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# ---------------------------------------------------------------------------
# Thresholds — Phase 2 additions (calibrated from vocus-profitability data)
# ---------------------------------------------------------------------------

LOW_MARGIN_PCT_THRESHOLD    = 0.05   # 5% — below APN ~8.4% adjusted target
RATE_VARIANCE_TOLERANCE_ABS = 0.02   # $0.02 — mirrors amount matching standard
RATE_VARIANCE_TOLERANCE_PCT = 0.001  # 0.1%

ROOT = Path(__file__).parent.parent
DB   = ROOT / "db"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _write_parquet(df: pd.DataFrame, name: str) -> Path:
    dest = DB / f"{name}.parquet"
    df.to_parquet(dest, index=False, compression="snappy")
    return dest


def _write_markdown(df: pd.DataFrame, name: str, run_dir: Path, title: str = "") -> Path:
    dest = run_dir / f"{name}.md"
    lines = []
    if title:
        lines.append(f"# {title}\n")
    lines.append(f"_Rows: {len(df)}_\n")
    lines.append(df.to_markdown(index=False))
    lines.append("")
    dest.write_text("\n".join(lines))
    return dest


# ---------------------------------------------------------------------------
# Rate card — resolve to one rate per service_type (most recent effective_date)
# ---------------------------------------------------------------------------

def _resolve_rate_card(rate_card: pd.DataFrame) -> pd.DataFrame:
    """Return one row per service_type: the most recently effective rate."""
    rc = rate_card.copy()
    # Ensure effective_date is datetime so sort is correct
    if not pd.api.types.is_datetime64_any_dtype(rc["effective_date"]):
        rc["effective_date"] = pd.to_datetime(rc["effective_date"], errors="coerce")
    return (
        rc.sort_values("effective_date", ascending=False)
          .drop_duplicates(subset=["service_type"])
          .reset_index(drop=True)
    )


# ---------------------------------------------------------------------------
# Rate variances
# ---------------------------------------------------------------------------

def build_rate_variances(matched: pd.DataFrame, rate_card: pd.DataFrame) -> pd.DataFrame:
    """
    Join matched lines to rate card on service_type.
    Compute rate_variance_abs = invoice_amount - expected_cost.
    """
    rc = _resolve_rate_card(rate_card)[["service_type", "expected_cost_ex_tax"]]

    # Cast to str before merge — matched_lines may have service_type as category
    m = matched.copy()
    m["service_type"] = m["service_type"].astype(str)
    rc = rc.copy()
    rc["service_type"] = rc["service_type"].astype(str)

    merged = m.merge(rc, on="service_type", how="left")

    merged["rate_variance_abs"] = (
        merged["invoice_amount_ex_tax"] - merged["expected_cost_ex_tax"]
    ).round(4)
    merged["rate_variance_pct"] = (
        merged["rate_variance_abs"] / merged["expected_cost_ex_tax"]
    ).round(6)
    merged["rate_card_mismatch_flag"] = (
        (merged["rate_variance_abs"].abs() > RATE_VARIANCE_TOLERANCE_ABS) |
        (merged["rate_variance_pct"].abs() > RATE_VARIANCE_TOLERANCE_PCT)
    )
    merged["no_rate_card_entry"] = merged["expected_cost_ex_tax"].isna()

    cols = [
        "supplier_service_id", "billing_period_start", "service_type",
        "customer_id", "invoice_amount_ex_tax", "expected_cost_ex_tax",
        "rate_variance_abs", "rate_variance_pct",
        "rate_card_mismatch_flag", "no_rate_card_entry",
    ]
    return merged[[c for c in cols if c in merged.columns]].reset_index(drop=True)


def build_rate_card_mismatches(rate_variances: pd.DataFrame) -> pd.DataFrame:
    """Subset of rate_variances where the rate card mismatch flag is True."""
    return (
        rate_variances[rate_variances["rate_card_mismatch_flag"] == True]
        .copy()
        .reset_index(drop=True)
    )


# ---------------------------------------------------------------------------
# Margin tables
# ---------------------------------------------------------------------------

def build_margin_by_customer(matched: pd.DataFrame) -> pd.DataFrame:
    """Aggregate direct margin per customer from matched lines."""
    grp = (
        matched
        .groupby("customer_id", observed=True)
        .agg(
            service_count  =("supplier_service_id", "count"),
            revenue_total  =("sales_revenue_ex_tax", "sum"),
            cost_total     =("invoice_amount_ex_tax", "sum"),
        )
        .reset_index()
    )
    grp["margin_total"]    = (grp["revenue_total"] - grp["cost_total"]).round(4)
    grp["margin_pct"]      = (grp["margin_total"] / grp["revenue_total"]).round(6)
    grp["low_margin_flag"] = grp["margin_pct"] < LOW_MARGIN_PCT_THRESHOLD
    return grp.sort_values("margin_pct").reset_index(drop=True)


def build_margin_by_service_type(matched: pd.DataFrame) -> pd.DataFrame:
    """Aggregate direct margin per service type from matched lines."""
    m = matched.copy()
    m["service_type"] = m["service_type"].astype(str)
    grp = (
        m
        .groupby("service_type", observed=True)
        .agg(
            service_count  =("supplier_service_id", "count"),
            revenue_total  =("sales_revenue_ex_tax", "sum"),
            cost_total     =("invoice_amount_ex_tax", "sum"),
        )
        .reset_index()
    )
    grp["margin_total"]    = (grp["revenue_total"] - grp["cost_total"]).round(4)
    grp["margin_pct"]      = (grp["margin_total"] / grp["revenue_total"]).round(6)
    grp["low_margin_flag"] = grp["margin_pct"] < LOW_MARGIN_PCT_THRESHOLD
    return grp.sort_values("margin_pct").reset_index(drop=True)


def build_low_margin_exceptions(matched: pd.DataFrame) -> pd.DataFrame:
    """Matched lines where direct_margin_pct is below the low-margin threshold."""
    low = matched[matched["direct_margin_pct"] < LOW_MARGIN_PCT_THRESHOLD].copy()
    cols = [
        "supplier_service_id", "billing_period_start", "service_type",
        "customer_id", "invoice_amount_ex_tax", "sales_revenue_ex_tax",
        "direct_margin_ex_tax", "direct_margin_pct",
    ]
    return low[[c for c in cols if c in low.columns]].reset_index(drop=True)


# ---------------------------------------------------------------------------
# Phase 2 assumptions
# ---------------------------------------------------------------------------

def build_phase2_assumptions() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "assumption_key": "low_margin_threshold",
            "value":          str(LOW_MARGIN_PCT_THRESHOLD),
            "rationale":      "Below APN ~8.4% adjusted target; flags services needing pricing review",
            "source":         "default",
        },
        {
            "assumption_key": "rate_variance_tolerance_abs",
            "value":          str(RATE_VARIANCE_TOLERANCE_ABS),
            "rationale":      "Same rounding standard as amount matching ($0.02)",
            "source":         "default",
        },
        {
            "assumption_key": "rate_variance_tolerance_pct",
            "value":          str(RATE_VARIANCE_TOLERANCE_PCT),
            "rationale":      "Same float-drift threshold as amount matching (0.1%)",
            "source":         "default",
        },
        {
            "assumption_key": "rate_card_temporal",
            "value":          "most_recent_effective_date_per_service_type",
            "rationale":      "Multiple effective dates allowed; most recent wins. Period-aware selection deferred to Phase 3.",
            "source":         "default",
        },
    ])


# ---------------------------------------------------------------------------
# Main analysis entry point
# ---------------------------------------------------------------------------

def run_rate_card_analysis(
    matched_pq:   Path,
    rate_card_pq: Path,
    output_dir:   Path | None = None,
) -> dict:
    run_id = str(uuid.uuid4())[:8]
    run_ts = _now()

    if output_dir is None:
        output_dir = ROOT / "output" / f"phase2_{run_id}"
    output_dir.mkdir(parents=True, exist_ok=True)
    DB.mkdir(parents=True, exist_ok=True)

    print(f"\n=== Phase 2 Rate Card Analysis: {run_id} ===")
    print(f"  matched_lines : {matched_pq.name}")
    print(f"  rate_card     : {rate_card_pq.name}")
    print(f"  output        : {output_dir}")

    # --- load inputs ---
    matched   = pd.read_parquet(matched_pq)
    rate_card = pd.read_parquet(rate_card_pq)

    print(f"\n  Matched lines  : {len(matched)}")
    print(f"  Rate card rows : {len(rate_card)}")

    # --- build tables ---
    print("\nBuilding Phase 2 tables...")
    rate_variances         = build_rate_variances(matched, rate_card)
    rate_card_mismatches   = build_rate_card_mismatches(rate_variances)
    margin_by_customer     = build_margin_by_customer(matched)
    margin_by_service_type = build_margin_by_service_type(matched)
    low_margin_exceptions  = build_low_margin_exceptions(matched)
    phase2_assumptions     = build_phase2_assumptions()

    all_tables = {
        "rate_variances":         rate_variances,
        "rate_card_mismatches":   rate_card_mismatches,
        "margin_by_customer":     margin_by_customer,
        "margin_by_service_type": margin_by_service_type,
        "low_margin_exceptions":  low_margin_exceptions,
        "phase2_assumptions":     phase2_assumptions,
    }

    # --- write parquet ---
    print("\nWriting parquet...")
    for name, df in all_tables.items():
        _write_parquet(df, name)
        print(f"  db/{name}.parquet  ({len(df)} rows)")

    # --- write markdown ---
    print("\nWriting markdown...")
    titles = {
        "rate_variances":         "Rate Variances — Actual vs Expected Cost",
        "rate_card_mismatches":   "Rate Card Mismatches",
        "margin_by_customer":     "Margin by Customer",
        "margin_by_service_type": "Margin by Service Type",
        "low_margin_exceptions":  f"Low Margin Exceptions (threshold: {LOW_MARGIN_PCT_THRESHOLD:.0%})",
        "phase2_assumptions":     "Phase 2 Assumptions",
    }
    for name, df in all_tables.items():
        _write_markdown(df, name, output_dir, title=titles.get(name, name))
        print(f"  output/phase2_{run_id}/{name}.md")

    # --- summary output ---
    n_mismatches = len(rate_card_mismatches)
    n_low_margin = len(low_margin_exceptions)
    print(f"\n{'='*52}")
    print(f"  Rate card mismatches    : {n_mismatches}")
    print(f"  Low margin exceptions   : {n_low_margin}")
    print(f"  Customers in scope      : {len(margin_by_customer)}")
    print(f"  Service types in scope  : {len(margin_by_service_type)}")

    if n_mismatches:
        print(f"\n  Rate card mismatches (invoice vs expected):")
        for _, r in rate_card_mismatches.iterrows():
            print(f"    {r['supplier_service_id']}  actual=${r['invoice_amount_ex_tax']:.2f}  "
                  f"expected=${r['expected_cost_ex_tax']:.2f}  "
                  f"variance=${r['rate_variance_abs']:.2f} ({r['rate_variance_pct']*100:.2f}%)")

    if n_low_margin:
        print(f"\n  Low margin exceptions (<{LOW_MARGIN_PCT_THRESHOLD:.0%}):")
        for _, r in low_margin_exceptions.iterrows():
            print(f"    {r['supplier_service_id']}  margin={r['direct_margin_pct']*100:.2f}%")

    print(f"\nDone. Run ID: {run_id}")
    return {
        "run_id":     run_id,
        "run_ts":     run_ts,
        "output_dir": str(output_dir),
        "tables":     all_tables,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Run Phase 2 rate card and margin analysis.")
    parser.add_argument("--matched",   default=str(DB / "matched_lines.parquet"))
    parser.add_argument("--rate-card", default=str(DB / "rate_card.parquet"))
    parser.add_argument("--output-dir")
    args = parser.parse_args()

    matched_pq   = Path(args.matched)
    rate_card_pq = Path(args.rate_card)

    for p in [matched_pq, rate_card_pq]:
        if not p.exists():
            print(f"ERROR: File not found: {p}", file=sys.stderr)
            print("Run invoice_analysis_skeleton.py and load_inputs.py first.", file=sys.stderr)
            return 1

    out_dir = Path(args.output_dir) if args.output_dir else None
    run_rate_card_analysis(matched_pq, rate_card_pq, out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
