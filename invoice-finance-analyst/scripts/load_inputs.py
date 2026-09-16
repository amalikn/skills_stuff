"""
load_inputs.py — Phase 1B CSV loader: validate → normalise → write parquet.

Follows the vocus-profitability build_db.py pattern:
  - Load with dtype=str to prevent auto-coercion surprises
  - Apply mapping.yaml column renames dynamically
  - Cast types explicitly with errors="coerce"
  - Archive current parquet before overwriting (keep 2 most recent)
  - Write with snappy compression

Usage:
    python load_inputs.py --csv invoice.csv --mapping mapping_supplier_invoice.yaml
    python load_inputs.py --csv sales.csv   --mapping mapping_sales_billing.yaml
    python load_inputs.py --all             # loads all configured CSVs from a run config
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import yaml

# Allow direct CLI execution from project root or scripts/
_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.validate_inputs import validate, NUMERIC_FIELDS, DATE_FIELDS, REQUIRED_FIELDS

ROOT = Path(__file__).parent.parent
DB   = ROOT / "db"

# Low-cardinality string fields benefit from category encoding in parquet
CATEGORY_FIELDS = {"service_type", "description", "customer_name", "source_type",
                   "match_status", "exception_severity"}

# "mixed" format handles ISO, AU (DD/MM/YYYY), and US (MM/DD/YYYY) in one pass
DATE_PARSE_KWARGS: dict = {"format": "mixed", "dayfirst": True, "errors": "coerce"}


# ---------------------------------------------------------------------------
# Archive helpers (same pattern as vocus-profitability build_db.py)
# ---------------------------------------------------------------------------

def _archive(current: Path) -> None:
    """Copy current parquet to a dated archive; keep only the 2 most recent."""
    if not current.exists():
        return
    ts   = datetime.now().strftime("%Y%m%d_%H%M")
    stem = current.stem
    current.replace(DB / f"{stem}_{ts}.parquet")
    archives = sorted(
        DB.glob(f"{stem}_????????_????.parquet"),
        key=lambda p: p.name,
        reverse=True,
    )
    for old in archives[2:]:
        old.unlink()
        print(f"  pruned archive: {old.name}")


# ---------------------------------------------------------------------------
# Core loader
# ---------------------------------------------------------------------------

def load_csv(csv_path: Path, mapping_path: Path, *, verbose: bool = True) -> pd.DataFrame:
    """
    Validate, load, and normalise a source CSV to a canonical DataFrame.

    Steps:
      1. Pre-flight validate (calls validate_inputs.validate)
      2. Read CSV with dtype=str
      3. Rename source columns → canonical names via mapping.yaml
      4. Cast numeric canonical fields with pd.to_numeric(errors="coerce")
      5. Cast date canonical fields with pd.to_datetime(dayfirst=True, errors="coerce")
      6. Cast low-cardinality string fields to category
      7. Strip whitespace from all string columns
      8. Add _source_file metadata column

    Raises RuntimeError if validation fails.
    """
    # --- pre-flight ---
    result = validate(csv_path, mapping_path)
    if not result.passed:
        raise RuntimeError(
            f"Validation failed for {csv_path.name}:\n" +
            "\n".join(f"  ✗ {e}" for e in result.errors)
        )

    if verbose:
        print(f"  validated: {csv_path.name} ({result.row_count} rows, "
              f"{result.duplicate_row_count} duplicate(s), "
              f"source intact: {result.source_intact})")
        if result.warnings:
            for w in result.warnings:
                print(f"    ! {w}")

    # --- load mapping ---
    with mapping_path.open() as f:
        mapping_data = yaml.safe_load(f)
    source_type:   str        = mapping_data.get("source_type", "unknown")
    field_mappings: dict[str, str] = mapping_data.get("field_mappings", {})

    # Invert: source_col → canonical
    rename_map = {v: k for k, v in field_mappings.items()}

    # --- load CSV as strings ---
    df = pd.read_csv(csv_path, dtype=str, encoding="utf-8-sig")

    # --- strip whitespace from all string columns ---
    for col in df.columns:
        df[col] = df[col].str.strip()

    # --- rename to canonical ---
    df = df.rename(columns=rename_map)

    # --- cast numeric canonical fields ---
    for canonical in NUMERIC_FIELDS:
        if canonical in df.columns:
            # Strip currency symbols and thousand-separators before casting
            df[canonical] = (
                df[canonical]
                .str.replace(r"[$,]", "", regex=True)
                .pipe(pd.to_numeric, errors="coerce")
            )

    # --- cast date canonical fields ---
    for canonical in DATE_FIELDS:
        if canonical in df.columns:
            df[canonical] = pd.to_datetime(df[canonical], **DATE_PARSE_KWARGS)

    # --- cast category fields ---
    for canonical in CATEGORY_FIELDS:
        if canonical in df.columns:
            df[canonical] = df[canonical].astype("category")

    # --- metadata columns ---
    df["_source_file"]  = csv_path.name
    df["_source_type"]  = source_type
    df["_source_hash"]  = result.file_hash_before
    df["_loaded_at"]    = datetime.now().isoformat(timespec="seconds")

    return df


def write_parquet(df: pd.DataFrame, name: str, *, verbose: bool = True) -> Path:
    """
    Archive existing parquet if present, write new one with snappy compression.
    Returns the written path.
    """
    DB.mkdir(parents=True, exist_ok=True)
    dest = DB / f"{name}.parquet"
    _archive(dest)
    df.to_parquet(dest, index=False, compression="snappy")
    if verbose:
        size_kb = dest.stat().st_size / 1024
        print(f"  {len(df):,} rows → {dest.name}  ({size_kb:,.1f} KB)")
    return dest


def print_summary(name: str, df: pd.DataFrame) -> None:
    print(f"\n=== {name} ===")
    print(f"  Rows:       {len(df):>8,}")
    print(f"  Columns:    {list(df.columns)}")

    # Numeric column totals
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    for col in numeric_cols:
        if not col.startswith("_"):
            total = df[col].sum()
            nulls = df[col].isna().sum()
            print(f"  {col:<30} total={total:>12,.2f}  nulls={nulls}")

    # Duplicates (excluding metadata cols)
    data_cols = [c for c in df.columns if not c.startswith("_")]
    dupes = df.duplicated(subset=data_cols).sum()
    if dupes:
        print(f"  ! Duplicate rows: {dupes}")


# ---------------------------------------------------------------------------
# Convenience: load one CSV pair and write to db/
# ---------------------------------------------------------------------------

def ingest(csv_path: Path, mapping_path: Path, parquet_name: str | None = None) -> pd.DataFrame:
    """Load, normalise, and persist one CSV to db/. Returns the DataFrame."""
    if parquet_name is None:
        parquet_name = csv_path.stem
    print(f"\nLoading {csv_path.name}...")
    df = load_csv(csv_path, mapping_path)
    write_parquet(df, parquet_name)
    print_summary(parquet_name, df)
    return df


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Load invoice analysis CSVs to parquet.")
    parser.add_argument("--csv",        help="Path to source CSV")
    parser.add_argument("--mapping",    help="Path to mapping.yaml")
    parser.add_argument("--name",       help="Parquet stem name (default: CSV filename stem)")
    parser.add_argument("--db",         help="Override db/ directory path")
    parser.add_argument("--quiet",      action="store_true")
    args = parser.parse_args()

    if args.db:
        global DB
        DB = Path(args.db)

    if args.csv and args.mapping:
        try:
            df = ingest(
                Path(args.csv),
                Path(args.mapping),
                parquet_name=args.name,
            )
        except RuntimeError as exc:
            print(f"\nERROR: {exc}", file=sys.stderr)
            return 1
        print("\nDone.")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
