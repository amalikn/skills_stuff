"""
validate_inputs.py — Phase 1A CSV input validator.

Loads a source CSV and its mapping.yaml, translates to canonical field names,
profiles the data, and confirms the source file was not modified.

Usage:
    python validate_inputs.py --csv path/to/file.csv --mapping path/to/mapping.yaml
    python validate_inputs.py --csv path/to/file.csv --suggest-mapping   # heuristic draft only
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


# ---------------------------------------------------------------------------
# Heuristic patterns — data_contract.md §"Heuristic detection patterns"
# ---------------------------------------------------------------------------

HEURISTIC_PATTERNS: dict[str, list[str]] = {
    # supplier_invoice
    "invoice_number":       ["invoice no", "invoice number", "invoice#", "inv no", "inv_no"],
    "invoice_date":         ["invoice date", "inv date", "date issued", "issue date"],
    "billing_period_start": ["period start", "period from", "service start", "from date", "start date", "billing from"],
    "billing_period_end":   ["period end", "period to", "service end", "to date", "end date", "billing to"],
    "supplier_service_id":  ["avc id", "avc", "cvc id", "circuit id", "service id", "nbn id", "port id"],
    "amount_ex_tax":        ["amount ex", "ex gst", "ex tax", "net amount", "charge ex", "subtotal", "net charge"],
    "service_type":         ["product type", "service type", "product", "plan", "technology type"],
    "description":          ["description", "charge description", "line item", "detail", "line description"],
    "quantity":             ["qty", "quantity", "units", "count"],
    "unit_price_ex_tax":    ["unit price", "rate", "unit cost", "price ex"],
    "tax_amount":           ["gst", "tax", "vat", "gst amount"],
    "amount_inc_tax":       ["amount inc", "inc gst", "total", "gross amount"],
    # sales_billing
    "customer_id":          ["customer id", "client id", "account id", "cust id", "cust_id", "account no"],
    "customer_name":        ["customer name", "client name", "account name", "customer"],
    "our_service_id":       ["service id", "our service", "internal id", "product id", "service ref"],
    "revenue_ex_tax":       ["revenue ex", "revenue exgst", "ex gst", "charge ex", "amount ex", "net revenue", "sale ex"],
    "cost_ex_tax":          ["cost ex", "cost exgst", "cogs", "cost ex gst", "wholesale", "supplier cost"],
    # rate_card
    "expected_cost_ex_tax": ["expected cost", "expected charge", "rate ex", "wholesale rate", "wsp", "contract rate",
                             "expected cost exgst", "rate exgst"],
    "effective_date":       ["effective date", "valid from", "rate date", "rate start"],
    "expiry_date":          ["expiry date", "valid to", "expires", "rate end"],
    "speed_pack":           ["speed", "speed tier", "plan speed", "bandwidth"],
    # service_map
    "active":               ["active", "status", "enabled", "is active"],
}

REQUIRED_FIELDS: dict[str, list[str]] = {
    "supplier_invoice": ["invoice_number", "invoice_date", "billing_period_start",
                         "billing_period_end", "supplier_service_id", "amount_ex_tax"],
    "sales_billing":    ["customer_id", "billing_period_start", "billing_period_end",
                         "our_service_id", "revenue_ex_tax"],
    "rate_card":        ["service_type", "expected_cost_ex_tax", "effective_date"],
    "service_map":      ["supplier_service_id", "our_service_id"],
}

NUMERIC_FIELDS = {"amount_ex_tax", "tax_amount", "amount_inc_tax", "unit_price_ex_tax",
                  "quantity", "revenue_ex_tax", "cost_ex_tax", "expected_cost_ex_tax"}

DATE_FIELDS = {"invoice_date", "billing_period_start", "billing_period_end",
               "effective_date", "expiry_date"}

DATE_PATTERNS = [
    r"^\d{4}-\d{2}-\d{2}$",           # ISO: 2026-03-01
    r"^\d{2}/\d{2}/\d{4}$",           # AU: 31/03/2026
    r"^\d{2}-\d{2}-\d{4}$",           # AU dash: 31-03-2026
    r"^\d{1,2}/\d{1,2}/\d{4}$",       # US or AU short: 3/1/2026
]


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ValidationResult:
    csv_path: str
    source_type: str
    row_count: int = 0
    source_columns: list[str] = field(default_factory=list)
    canonical_columns: list[str] = field(default_factory=list)
    null_counts: dict[str, int] = field(default_factory=dict)
    duplicate_row_count: int = 0
    numeric_columns: list[str] = field(default_factory=list)
    date_columns: list[str] = field(default_factory=list)
    file_hash_before: str = ""
    file_hash_after: str = ""
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0

    @property
    def source_intact(self) -> bool:
        return self.file_hash_before == self.file_hash_after


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_mapping(mapping_path: Path) -> dict:
    with mapping_path.open() as f:
        return yaml.safe_load(f)


def suggest_mapping(headers: list[str], source_type: str) -> dict[str, Optional[str]]:
    """Return heuristic-suggested canonical→source mapping. None means no candidate found."""
    suggestions: dict[str, Optional[str]] = {}
    headers_lower = {h.lower(): h for h in headers}

    for canonical, patterns in HEURISTIC_PATTERNS.items():
        match = None
        for pattern in patterns:
            for h_lower, h_orig in headers_lower.items():
                if pattern in h_lower:
                    match = h_orig
                    break
            if match:
                break
        suggestions[canonical] = match

    return suggestions


def _strip_numeric(value: str) -> str:
    return value.replace("$", "").replace(",", "").strip()


def _looks_numeric(values: list[str]) -> bool:
    non_empty = [v for v in values if v.strip()]
    if not non_empty:
        return False
    parseable = 0
    for v in non_empty:
        try:
            float(_strip_numeric(v))
            parseable += 1
        except ValueError:
            pass
    return parseable / len(non_empty) >= 0.8


def _looks_date(values: list[str]) -> bool:
    non_empty = [v for v in values if v.strip()]
    if not non_empty:
        return False
    matched = sum(
        1 for v in non_empty
        if any(re.match(p, v.strip()) for p in DATE_PATTERNS)
    )
    return matched / len(non_empty) >= 0.8


def validate(csv_path: Path, mapping_path: Path) -> ValidationResult:
    result = ValidationResult(
        csv_path=str(csv_path),
        source_type="unknown",
    )

    # --- existence checks ---
    if not csv_path.exists():
        result.errors.append(f"CSV file not found: {csv_path}")
        return result

    if csv_path.suffix.lower() != ".csv":
        result.errors.append(f"File is not a CSV (extension: {csv_path.suffix}): {csv_path}")
        return result

    if not mapping_path.exists():
        result.errors.append(f"Mapping file not found: {mapping_path}")
        return result

    # --- hash before load ---
    result.file_hash_before = sha256(csv_path)

    # --- load mapping ---
    mapping_data = load_mapping(mapping_path)
    source_type = mapping_data.get("source_type", "unknown")
    result.source_type = source_type
    field_mappings: dict[str, str] = mapping_data.get("field_mappings", {})

    # --- load CSV ---
    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = list(reader.fieldnames or [])
        rows = list(reader)

    result.source_columns = headers
    result.row_count = len(rows)

    # --- validate required field mappings exist ---
    required = REQUIRED_FIELDS.get(source_type, [])
    for canonical in required:
        if canonical not in field_mappings:
            result.errors.append(f"Missing required mapping: {canonical} (source_type: {source_type})")
        else:
            source_col = field_mappings[canonical]
            if source_col not in headers:
                result.errors.append(
                    f"Mapped column not found in CSV: '{source_col}' (for canonical field: {canonical})"
                )

    if result.errors:
        return result

    # --- build canonical column list ---
    result.canonical_columns = [
        canonical for canonical, source_col in field_mappings.items()
        if source_col in headers
    ]

    # --- null counts per canonical field ---
    for canonical, source_col in field_mappings.items():
        if source_col in headers:
            null_count = sum(1 for row in rows if not row.get(source_col, "").strip())
            result.null_counts[canonical] = null_count

    # --- check required fields for nulls ---
    for canonical in required:
        if canonical in result.null_counts and result.null_counts[canonical] > 0:
            result.warnings.append(
                f"Required field '{canonical}' has {result.null_counts[canonical]} null/empty value(s)"
            )

    # --- validate numeric fields parse as decimal ---
    for canonical in NUMERIC_FIELDS:
        source_col = field_mappings.get(canonical)
        if source_col and source_col in headers:
            values = [row.get(source_col, "") for row in rows if row.get(source_col, "").strip()]
            bad = []
            for v in values:
                try:
                    float(_strip_numeric(v))
                except ValueError:
                    bad.append(v)
            if bad:
                result.errors.append(
                    f"Non-numeric values in required decimal field '{canonical}': {bad[:5]}"
                )

    # --- validate date fields parse ---
    for canonical in DATE_FIELDS:
        source_col = field_mappings.get(canonical)
        if source_col and source_col in headers:
            values = [row.get(source_col, "").strip() for row in rows if row.get(source_col, "").strip()]
            bad = [
                v for v in values
                if not any(re.match(p, v) for p in DATE_PATTERNS)
            ]
            if bad:
                result.errors.append(
                    f"Unparseable date values in required date field '{canonical}': {bad[:5]}"
                )

    # --- duplicate row count ---
    seen: set[tuple] = set()
    duplicate_count = 0
    for row in rows:
        key = tuple(row.get(h, "") for h in headers)
        if key in seen:
            duplicate_count += 1
        seen.add(key)
    result.duplicate_row_count = duplicate_count

    # --- detect numeric-looking and date-looking source columns ---
    col_values: dict[str, list[str]] = {h: [] for h in headers}
    for row in rows:
        for h in headers:
            col_values[h].append(row.get(h, ""))

    result.numeric_columns = [h for h in headers if _looks_numeric(col_values[h])]
    result.date_columns = [h for h in headers if _looks_date(col_values[h])]

    # --- hash after (must match before) ---
    result.file_hash_after = sha256(csv_path)
    if not result.source_intact:
        result.errors.append("Source file hash changed during validation — file was mutated.")

    return result


def print_result(result: ValidationResult) -> None:
    status = "PASS" if result.passed else "FAIL"
    print(f"\n=== Validation {status}: {result.csv_path} ===")
    print(f"  Source type  : {result.source_type}")
    print(f"  Rows         : {result.row_count}")
    print(f"  Columns      : {result.source_columns}")
    print(f"  Canonical    : {result.canonical_columns}")
    print(f"  Nulls        : {result.null_counts}")
    print(f"  Duplicates   : {result.duplicate_row_count} duplicate row(s)")
    print(f"  Numeric cols : {result.numeric_columns}")
    print(f"  Date cols    : {result.date_columns}")
    print(f"  File hash    : {result.file_hash_before}")
    print(f"  Source intact: {result.source_intact}")
    if result.warnings:
        print("  Warnings:")
        for w in result.warnings:
            print(f"    ! {w}")
    if result.errors:
        print("  Errors:")
        for e in result.errors:
            print(f"    ✗ {e}")
    else:
        print("  No errors.")


def print_suggested_mapping(headers: list[str], source_type: str, csv_path: Path) -> None:
    suggestions = suggest_mapping(headers, source_type)
    print(f"\n# Suggested mapping for: {csv_path.name}")
    print(f"# Review and correct, then save as mapping_<source_type>.yaml\n")
    print(f"version: \"1\"")
    print(f"created: \"2026-05-21\"")
    print(f"source_type: {source_type}\n")
    print("field_mappings:")
    for canonical, source_col in suggestions.items():
        if source_col:
            print(f"  {canonical:<28} \"{source_col}\"")
        else:
            print(f"  # {canonical:<26} # NO CANDIDATE FOUND — add manually")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Validate invoice analysis CSV inputs.")
    parser.add_argument("--csv", required=True, help="Path to source CSV file")
    parser.add_argument("--mapping", help="Path to mapping.yaml")
    parser.add_argument("--suggest-mapping", action="store_true",
                        help="Print heuristic mapping suggestion and exit")
    parser.add_argument("--source-type", default="supplier_invoice",
                        help="Source type for suggest-mapping mode (default: supplier_invoice)")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    csv_path = Path(args.csv)

    if args.suggest_mapping:
        if not csv_path.exists():
            print(f"Error: CSV not found: {csv_path}", file=sys.stderr)
            return 1
        with csv_path.open(newline="", encoding="utf-8-sig") as f:
            headers = list(csv.DictReader(f).fieldnames or [])
        print_suggested_mapping(headers, args.source_type, csv_path)
        return 0

    if not args.mapping:
        print("Error: --mapping is required unless --suggest-mapping is used.", file=sys.stderr)
        return 1

    result = validate(csv_path, Path(args.mapping))

    if args.json:
        import dataclasses
        print(json.dumps(dataclasses.asdict(result), indent=2))
    else:
        print_result(result)

    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
