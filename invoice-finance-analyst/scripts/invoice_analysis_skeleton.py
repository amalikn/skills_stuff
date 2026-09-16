"""
invoice_analysis_skeleton.py — Phase 1B minimal reconciliation skeleton.

Reads validated parquet files from db/, performs deterministic invoice-to-sales
reconciliation, and writes output tables to db/ (parquet) and output/<run_id>/
(markdown).

Output tables (column names locked in docs/output_schema.md):
  - run_summary
  - source_file_inventory
  - data_quality_issues
  - reconciliation_summary
  - matched_lines
  - invoice_no_sales
  - sales_no_invoice
  - amount_mismatches
  - assumptions

Usage:
    python invoice_analysis_skeleton.py
    python invoice_analysis_skeleton.py --invoice db/invoice.parquet --sales db/sales_billing.parquet
    python invoice_analysis_skeleton.py --output-dir output/custom_run
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd

_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# ---------------------------------------------------------------------------
# Thresholds — calibrated from vocus-profitability data (see SKILL.md)
# ---------------------------------------------------------------------------

AMOUNT_MATCH_TOLERANCE_ABS = 0.02   # $0.02 — mirrors house rounding standard
AMOUNT_MATCH_TOLERANCE_PCT = 0.001  # 0.1% — float drift

# Match key: join invoice to sales on these canonical fields
MATCH_KEY = ["supplier_service_id", "billing_period_start"]

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


def _md_summary(label: str, count: int, note: str = "") -> str:
    note_str = f" — {note}" if note else ""
    return f"| {label:<35} | {count:>6} |{note_str}"


# ---------------------------------------------------------------------------
# Source file inventory
# ---------------------------------------------------------------------------

def build_source_inventory(invoice_df: pd.DataFrame, sales_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for df, stype in [(invoice_df, "supplier_invoice"), (sales_df, "sales_billing")]:
        meta = df.iloc[0] if len(df) else {}
        data_cols = [c for c in df.columns if not c.startswith("_")]
        dupes = df.duplicated(subset=data_cols).sum()
        null_counts = {c: int(df[c].isna().sum()) for c in data_cols}
        rows.append({
            "source_type":        stype,
            "file_name":          str(meta.get("_source_file", "")),
            "file_hash":          str(meta.get("_source_hash", "")),
            "row_count":          len(df),
            "duplicate_row_count": int(dupes),
            "null_counts_json":   json.dumps(null_counts),
            "loaded_at":          str(meta.get("_loaded_at", "")),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Data quality issues
# ---------------------------------------------------------------------------

def build_quality_issues(invoice_df: pd.DataFrame, sales_df: pd.DataFrame,
                         inv_required: list[str], sales_required: list[str]) -> pd.DataFrame:
    rows = []

    def _check(df: pd.DataFrame, source_type: str, required: list[str]) -> None:
        data_cols = [c for c in df.columns if not c.startswith("_")]

        # Nulls
        for col in data_cols:
            if col not in df.columns:
                continue
            n = int(df[col].isna().sum())
            if n:
                sev = "high" if col in required else "medium"
                rows.append({
                    "source_type": source_type,
                    "field":       col,
                    "issue_type":  "null_in_required" if col in required else "null_in_optional",
                    "count":       n,
                    "severity":    sev,
                    "detail":      f"{n} null/empty value(s) in '{col}'",
                })

        # Duplicates
        dupes = int(df.duplicated(subset=data_cols).sum())
        if dupes:
            rows.append({
                "source_type": source_type,
                "field":       "(all)",
                "issue_type":  "duplicate_row",
                "count":       dupes,
                "severity":    "high",
                "detail":      f"{dupes} exact duplicate row(s) detected",
            })

    _check(invoice_df, "supplier_invoice", inv_required)
    _check(sales_df,   "sales_billing",    sales_required)
    return pd.DataFrame(rows) if rows else pd.DataFrame(
        columns=["source_type", "field", "issue_type", "count", "severity", "detail"])


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

def deduplicate(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Remove exact duplicate rows. Returns (clean_df, n_removed)."""
    data_cols = [c for c in df.columns if not c.startswith("_")]
    before = len(df)
    df = df.drop_duplicates(subset=data_cols).reset_index(drop=True)
    return df, before - len(df)


# ---------------------------------------------------------------------------
# Reconciliation
# ---------------------------------------------------------------------------

def reconcile(invoice_df: pd.DataFrame, sales_df: pd.DataFrame,
              tol_abs: float, tol_pct: float) -> dict[str, pd.DataFrame]:
    """
    Match invoice rows to sales rows on MATCH_KEY.
    sales uses our_service_id as the join partner to supplier_service_id.
    """
    # Rename sales join column to align with invoice
    sales = sales_df.copy()
    if "our_service_id" in sales.columns and "supplier_service_id" not in sales.columns:
        sales = sales.rename(columns={"our_service_id": "supplier_service_id"})

    # Ensure match key columns exist in both
    inv_key_ok   = all(k in invoice_df.columns for k in MATCH_KEY)
    sales_key_ok = all(k in sales.columns      for k in MATCH_KEY)

    if not (inv_key_ok and sales_key_ok):
        missing_inv   = [k for k in MATCH_KEY if k not in invoice_df.columns]
        missing_sales = [k for k in MATCH_KEY if k not in sales.columns]
        raise ValueError(
            f"Match key columns missing — invoice: {missing_inv}, sales: {missing_sales}"
        )

    # Outer join on match key
    merged = invoice_df.merge(
        sales,
        on=MATCH_KEY,
        how="outer",
        suffixes=("_inv", "_sales"),
        indicator=True,
    )

    left_only  = merged[merged["_merge"] == "left_only"].copy()
    right_only = merged[merged["_merge"] == "right_only"].copy()
    both       = merged[merged["_merge"] == "both"].copy()

    # ---- matched_lines ----
    matched = _build_matched(both, tol_abs, tol_pct)

    # ---- invoice_no_sales ----
    inv_only = _build_invoice_only(left_only)

    # ---- sales_no_invoice ----
    sales_only = _build_sales_only(right_only)

    # ---- amount_mismatches ----
    mismatches = matched[matched["amount_mismatch_flag"] == True].copy()
    amount_mismatch_tbl = _build_amount_mismatches(mismatches)

    return {
        "matched_lines":   matched,
        "invoice_no_sales": inv_only,
        "sales_no_invoice": sales_only,
        "amount_mismatches": amount_mismatch_tbl,
    }


def _build_matched(both: pd.DataFrame, tol_abs: float, tol_pct: float) -> pd.DataFrame:
    df = pd.DataFrame()
    df["supplier_service_id"]  = both["supplier_service_id"]
    df["billing_period_start"] = both["billing_period_start"]

    # billing_period_end may have suffix if both sides have it
    bpe_col = "billing_period_end_inv" if "billing_period_end_inv" in both.columns else "billing_period_end"
    df["billing_period_end"]   = both.get(bpe_col)

    inv_num_col = "invoice_number_inv" if "invoice_number_inv" in both.columns else "invoice_number"
    df["invoice_number"]       = both.get(inv_num_col)

    svc_col = "service_type_inv" if "service_type_inv" in both.columns else "service_type"
    df["service_type"]         = both.get(svc_col)

    df["invoice_amount_ex_tax"]  = pd.to_numeric(both.get("amount_ex_tax"), errors="coerce")
    df["sales_revenue_ex_tax"]   = pd.to_numeric(both.get("revenue_ex_tax"), errors="coerce")
    df["sales_cost_ex_tax"]      = pd.to_numeric(both.get("cost_ex_tax"), errors="coerce")

    df["variance_abs"] = (df["invoice_amount_ex_tax"] - df["sales_cost_ex_tax"]).round(4)
    df["variance_pct"] = (df["variance_abs"] / df["invoice_amount_ex_tax"]).round(6)

    df["direct_margin_ex_tax"] = (df["sales_revenue_ex_tax"] - df["invoice_amount_ex_tax"]).round(4)
    df["direct_margin_pct"]    = (df["direct_margin_ex_tax"] / df["sales_revenue_ex_tax"]).round(6)

    cust_col = "customer_id_sales" if "customer_id_sales" in both.columns else "customer_id"
    df["customer_id"] = both.get(cust_col)

    df["amount_mismatch_flag"] = (
        df["variance_abs"].abs() > tol_abs
    ) | (
        df["variance_pct"].abs() > tol_pct
    )

    return df.reset_index(drop=True)


def _build_invoice_only(left_only: pd.DataFrame) -> pd.DataFrame:
    cols = {
        "supplier_service_id": "supplier_service_id",
        "billing_period_start": "billing_period_start",
        "billing_period_end":   "billing_period_end_inv",
        "invoice_number":       "invoice_number",
        "service_type":         "service_type_inv",
        "amount_ex_tax":        "amount_ex_tax",
        "description":          "description",
    }
    df = pd.DataFrame()
    for out_col, src_col in cols.items():
        fallback = src_col.replace("_inv", "").replace("_sales", "")
        df[out_col] = left_only.get(src_col, left_only.get(fallback))
    return df.reset_index(drop=True)


def _build_sales_only(right_only: pd.DataFrame) -> pd.DataFrame:
    cols = {
        "our_service_id":       "supplier_service_id",
        "billing_period_start": "billing_period_start",
        "billing_period_end":   "billing_period_end_sales",
        "customer_id":          "customer_id",
        "customer_name":        "customer_name",
        "service_type":         "service_type_sales",
        "revenue_ex_tax":       "revenue_ex_tax",
        "cost_ex_tax":          "cost_ex_tax",
    }
    df = pd.DataFrame()
    for out_col, src_col in cols.items():
        fallback = src_col.replace("_inv", "").replace("_sales", "")
        df[out_col] = right_only.get(src_col, right_only.get(fallback))
    return df.reset_index(drop=True)


def _build_amount_mismatches(mismatches: pd.DataFrame) -> pd.DataFrame:
    if mismatches.empty:
        return pd.DataFrame(columns=[
            "supplier_service_id", "billing_period_start",
            "invoice_amount_ex_tax", "sales_cost_ex_tax",
            "variance_abs", "variance_pct",
            "exceeds_abs_tolerance", "exceeds_pct_tolerance", "customer_id",
        ])
    df = mismatches[[
        "supplier_service_id", "billing_period_start",
        "invoice_amount_ex_tax", "sales_cost_ex_tax",
        "variance_abs", "variance_pct", "customer_id",
    ]].copy()
    df["exceeds_abs_tolerance"] = mismatches["variance_abs"].abs() > AMOUNT_MATCH_TOLERANCE_ABS
    df["exceeds_pct_tolerance"] = mismatches["variance_pct"].abs() > AMOUNT_MATCH_TOLERANCE_PCT
    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# Reconciliation summary
# ---------------------------------------------------------------------------

def build_reconciliation_summary(tables: dict[str, pd.DataFrame],
                                 n_duplicates: int,
                                 total_invoice_rows: int) -> pd.DataFrame:
    rows = []

    def _row(status, df, inv_col=None, sales_col=None):
        inv_total   = df[inv_col].sum()   if inv_col   and inv_col   in df.columns else None
        sales_total = df[sales_col].sum() if sales_col and sales_col in df.columns else None
        pct = len(df) / total_invoice_rows if total_invoice_rows else 0
        rows.append({
            "match_status":         status,
            "row_count":            len(df),
            "invoice_amount_total": round(inv_total,   2) if inv_total   is not None else None,
            "sales_revenue_total":  round(sales_total, 2) if sales_total is not None else None,
            "pct_of_invoice_rows":  round(pct, 4),
        })

    matched   = tables["matched_lines"]
    inv_only  = tables["invoice_no_sales"]
    sal_only  = tables["sales_no_invoice"]
    mismatches = tables["amount_mismatches"]

    _row("matched",          matched,   "invoice_amount_ex_tax", "sales_revenue_ex_tax")
    _row("invoice_only",     inv_only,  "amount_ex_tax",         None)
    _row("sales_only",       sal_only,  None,                    "revenue_ex_tax")
    _row("amount_mismatch",  mismatches,"invoice_amount_ex_tax", None)

    # Duplicate rows removed pre-reconciliation
    rows.append({
        "match_status":         "duplicate_removed",
        "row_count":            n_duplicates,
        "invoice_amount_total": None,
        "sales_revenue_total":  None,
        "pct_of_invoice_rows":  round(n_duplicates / total_invoice_rows, 4) if total_invoice_rows else 0,
    })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Assumptions table
# ---------------------------------------------------------------------------

def build_assumptions() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "assumption_key": "tolerance.abs",
            "value":          str(AMOUNT_MATCH_TOLERANCE_ABS),
            "rationale":      "Mirrors APN house rounding standard (DISCOUNT_TOLERANCE=0.02)",
            "source":         "default",
        },
        {
            "assumption_key": "tolerance.pct",
            "value":          str(AMOUNT_MATCH_TOLERANCE_PCT),
            "rationale":      "Float/rounding drift threshold (0.1%)",
            "source":         "default",
        },
        {
            "assumption_key": "match_key",
            "value":          "+".join(MATCH_KEY),
            "rationale":      "Phase 1B exact join; service_map not yet implemented",
            "source":         "default",
        },
        {
            "assumption_key": "deduplication",
            "value":          "exact_row_match",
            "rationale":      "Duplicate invoice rows removed before reconciliation to prevent double-matching",
            "source":         "default",
        },
        {
            "assumption_key": "our_service_id_equals_supplier_service_id",
            "value":          "True",
            "rationale":      "Phase 1B simplification: no service_map yet; IDs assumed equal across systems",
            "source":         "default",
        },
    ])


# ---------------------------------------------------------------------------
# Run summary
# ---------------------------------------------------------------------------

def build_run_summary(run_id: str, run_ts: str,
                      inv_df: pd.DataFrame, sales_df: pd.DataFrame,
                      tables: dict[str, pd.DataFrame],
                      n_duplicates: int) -> pd.DataFrame:
    inv_meta   = inv_df.iloc[0]   if len(inv_df)   else {}
    sales_meta = sales_df.iloc[0] if len(sales_df) else {}
    return pd.DataFrame([{
        "run_id":                  run_id,
        "run_timestamp":           run_ts,
        "invoice_file":            str(inv_meta.get("_source_file", "")),
        "sales_file":              str(sales_meta.get("_source_file", "")),
        "invoice_hash":            str(inv_meta.get("_source_hash", "")),
        "sales_hash":              str(sales_meta.get("_source_hash", "")),
        "invoice_row_count":       len(inv_df),
        "sales_row_count":         len(sales_df),
        "matched_count":           len(tables["matched_lines"]),
        "invoice_only_count":      len(tables["invoice_no_sales"]),
        "sales_only_count":        len(tables["sales_no_invoice"]),
        "duplicate_invoice_count": n_duplicates,
        "amount_mismatch_count":   len(tables["amount_mismatches"]),
        "tolerance_abs":           AMOUNT_MATCH_TOLERANCE_ABS,
        "tolerance_pct":           AMOUNT_MATCH_TOLERANCE_PCT,
        "match_key":               "+".join(MATCH_KEY),
    }])


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_analysis(invoice_pq: Path, sales_pq: Path, output_dir: Path | None = None) -> dict:
    run_id = str(uuid.uuid4())[:8]
    run_ts = _now()

    if output_dir is None:
        output_dir = ROOT / "output" / run_id
    output_dir.mkdir(parents=True, exist_ok=True)
    DB.mkdir(parents=True, exist_ok=True)

    print(f"\n=== Invoice Analysis Run: {run_id} ===")
    print(f"  invoice : {invoice_pq.name}")
    print(f"  sales   : {sales_pq.name}")
    print(f"  output  : {output_dir}")

    # --- load ---
    inv_df   = pd.read_parquet(invoice_pq)
    sales_df = pd.read_parquet(sales_pq)
    total_invoice_rows = len(inv_df)

    # --- source inventory ---
    inventory = build_source_inventory(inv_df, sales_df)
    print(f"\n  Invoice rows : {len(inv_df)}")
    print(f"  Sales rows   : {len(sales_df)}")

    # --- quality issues ---
    from scripts.validate_inputs import REQUIRED_FIELDS
    issues = build_quality_issues(
        inv_df, sales_df,
        REQUIRED_FIELDS.get("supplier_invoice", []),
        REQUIRED_FIELDS.get("sales_billing", []),
    )
    if len(issues):
        print(f"\n  ! {len(issues)} data quality issue(s) detected")

    # --- deduplicate invoice ---
    inv_clean, n_dupes = deduplicate(inv_df)
    if n_dupes:
        print(f"  ! Removed {n_dupes} duplicate invoice row(s) before reconciliation")

    # --- reconcile ---
    print("\nReconciling...")
    tables = reconcile(inv_clean, sales_df, AMOUNT_MATCH_TOLERANCE_ABS, AMOUNT_MATCH_TOLERANCE_PCT)

    # --- summary tables ---
    recon_summary = build_reconciliation_summary(tables, n_dupes, total_invoice_rows)
    assumptions   = build_assumptions()
    run_summary   = build_run_summary(run_id, run_ts, inv_df, sales_df, tables, n_dupes)

    all_tables = {
        "run_summary":            run_summary,
        "source_file_inventory":  inventory,
        "data_quality_issues":    issues,
        "reconciliation_summary": recon_summary,
        "assumptions":            assumptions,
        **tables,
    }

    # --- write parquet ---
    print("\nWriting parquet...")
    for name, df in all_tables.items():
        _write_parquet(df, name)
        print(f"  db/{name}.parquet  ({len(df)} rows)")

    # --- write markdown ---
    print("\nWriting markdown...")
    titles = {
        "run_summary":            "Run Summary",
        "source_file_inventory":  "Source File Inventory",
        "data_quality_issues":    "Data Quality Issues",
        "reconciliation_summary": "Reconciliation Summary",
        "assumptions":            "Assumptions",
        "matched_lines":          "Matched Lines",
        "invoice_no_sales":       "Invoice Lines — No Sales Match",
        "sales_no_invoice":       "Sales Lines — No Invoice Match",
        "amount_mismatches":      "Amount Mismatches",
    }
    for name, df in all_tables.items():
        _write_markdown(df, name, output_dir, title=titles.get(name, name))
        print(f"  output/{run_id}/{name}.md")

    # --- print reconciliation summary ---
    print(f"\n{'='*50}")
    print(f"  {'Status':<35} | {'Rows':>6} |")
    print(f"  {'-'*44}")
    for _, r in recon_summary.iterrows():
        print(f"  {_md_summary(r['match_status'], r['row_count'])}")
    print(f"  {'-'*44}")
    print(f"  {'Total invoice rows':<35} | {total_invoice_rows:>6} |")

    if len(tables["amount_mismatches"]):
        print(f"\n  ! {len(tables['amount_mismatches'])} amount mismatch(es) exceed tolerance")
        for _, r in tables["amount_mismatches"].iterrows():
            print(f"    {r['supplier_service_id']}  invoice=${r['invoice_amount_ex_tax']:.2f}  "
                  f"cost=${r['sales_cost_ex_tax']:.2f}  "
                  f"variance=${r['variance_abs']:.2f} ({r['variance_pct']*100:.2f}%)")

    print(f"\nDone. Run ID: {run_id}")
    return {"run_id": run_id, "output_dir": str(output_dir), "tables": all_tables}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run invoice reconciliation analysis.")
    parser.add_argument("--invoice", default=str(DB / "invoice.parquet"),
                        help="Path to invoice parquet (default: db/invoice.parquet)")
    parser.add_argument("--sales",   default=str(DB / "sales_billing.parquet"),
                        help="Path to sales parquet (default: db/sales_billing.parquet)")
    parser.add_argument("--output-dir", help="Override output directory")
    args = parser.parse_args()

    invoice_pq = Path(args.invoice)
    sales_pq   = Path(args.sales)

    for p in [invoice_pq, sales_pq]:
        if not p.exists():
            print(f"ERROR: File not found: {p}", file=sys.stderr)
            print("Run load_inputs.py first to ingest CSVs to parquet.", file=sys.stderr)
            return 1

    out_dir = Path(args.output_dir) if args.output_dir else None
    run_analysis(invoice_pq, sales_pq, out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
