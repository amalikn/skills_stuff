"""
tests/test_validate_inputs.py — Phase 1A exit gate tests.

Covers all Phase 1A exit criteria:
- accepts valid CSV with mapping
- fails clearly on missing file
- fails clearly on non-CSV extension
- reports row count, columns, null counts, duplicate count
- detects numeric-looking and date-looking columns
- does not mutate source file (hash integrity)
- fails when required mapping entry is missing
- fails when mapped column is absent from CSV header
- suggest_mapping returns candidates for known patterns
"""

from __future__ import annotations

import csv
import hashlib
import textwrap
from pathlib import Path

import pytest
import yaml

from scripts.validate_inputs import validate, suggest_mapping, ValidationResult


# ---------------------------------------------------------------------------
# Paths to shared fixtures (read-only — tests must not modify these)
# ---------------------------------------------------------------------------

EXAMPLES = Path(__file__).parent.parent / "examples"
INVOICE_CSV = EXAMPLES / "supplier_invoice_sample.csv"
INVOICE_MAPPING = EXAMPLES / "mapping_supplier_invoice.yaml"
SALES_CSV = EXAMPLES / "sales_billing_sample.csv"
SALES_MAPPING = EXAMPLES / "mapping_sales_billing.yaml"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_mapping(path: Path, source_type: str, mappings: dict) -> None:
    data = {"version": "1", "source_type": source_type, "field_mappings": mappings}
    with path.open("w") as f:
        yaml.dump(data, f)


# ---------------------------------------------------------------------------
# Happy path — shared fixtures
# ---------------------------------------------------------------------------

class TestValidInvoiceCSV:
    def test_passes(self):
        result = validate(INVOICE_CSV, INVOICE_MAPPING)
        assert result.passed, f"Expected pass. Errors: {result.errors}"

    def test_row_count(self):
        result = validate(INVOICE_CSV, INVOICE_MAPPING)
        assert result.row_count == 5

    def test_source_type(self):
        result = validate(INVOICE_CSV, INVOICE_MAPPING)
        assert result.source_type == "supplier_invoice"

    def test_source_columns_present(self):
        result = validate(INVOICE_CSV, INVOICE_MAPPING)
        assert "AVC ID" in result.source_columns
        assert "Net Charge" in result.source_columns

    def test_canonical_columns_mapped(self):
        result = validate(INVOICE_CSV, INVOICE_MAPPING)
        assert "supplier_service_id" in result.canonical_columns
        assert "amount_ex_tax" in result.canonical_columns

    def test_null_count_detected(self):
        # Row 5 has empty description
        result = validate(INVOICE_CSV, INVOICE_MAPPING)
        assert result.null_counts.get("description", 0) >= 1

    def test_no_nulls_in_required_fields(self):
        result = validate(INVOICE_CSV, INVOICE_MAPPING)
        # No errors — required fields have no nulls (warnings ok, errors not)
        assert not any("null" in e.lower() for e in result.errors)

    def test_duplicate_row_count(self):
        # Rows 1 and 4 are identical (LOC000001)
        result = validate(INVOICE_CSV, INVOICE_MAPPING)
        assert result.duplicate_row_count == 1

    def test_numeric_columns_detected(self):
        result = validate(INVOICE_CSV, INVOICE_MAPPING)
        assert "Net Charge" in result.numeric_columns
        assert "GST" in result.numeric_columns

    def test_date_columns_detected(self):
        result = validate(INVOICE_CSV, INVOICE_MAPPING)
        assert "Period From" in result.date_columns
        assert "Period To" in result.date_columns

    def test_source_file_not_mutated(self):
        hash_before = sha256(INVOICE_CSV)
        validate(INVOICE_CSV, INVOICE_MAPPING)
        hash_after = sha256(INVOICE_CSV)
        assert hash_before == hash_after, "Source CSV was modified during validation"

    def test_source_intact_flag(self):
        result = validate(INVOICE_CSV, INVOICE_MAPPING)
        assert result.source_intact


class TestValidSalesCSV:
    def test_passes(self):
        result = validate(SALES_CSV, SALES_MAPPING)
        assert result.passed, f"Expected pass. Errors: {result.errors}"

    def test_row_count(self):
        result = validate(SALES_CSV, SALES_MAPPING)
        assert result.row_count == 4

    def test_null_cost_detected(self):
        # Row 2 (Beta Pty Ltd / LOC000005) has empty Cost ExGST
        result = validate(SALES_CSV, SALES_MAPPING)
        assert result.null_counts.get("cost_ex_tax", 0) >= 1

    def test_no_duplicates(self):
        result = validate(SALES_CSV, SALES_MAPPING)
        assert result.duplicate_row_count == 0

    def test_source_file_not_mutated(self):
        hash_before = sha256(SALES_CSV)
        validate(SALES_CSV, SALES_MAPPING)
        hash_after = sha256(SALES_CSV)
        assert hash_before == hash_after


# ---------------------------------------------------------------------------
# Failure paths — missing file, wrong extension
# ---------------------------------------------------------------------------

class TestMissingFile:
    def test_fails(self, tmp_path):
        result = validate(tmp_path / "nonexistent.csv", INVOICE_MAPPING)
        assert not result.passed

    def test_error_message_names_file(self, tmp_path):
        missing = tmp_path / "nonexistent.csv"
        result = validate(missing, INVOICE_MAPPING)
        assert any("not found" in e.lower() for e in result.errors)

    def test_no_crash(self, tmp_path):
        result = validate(tmp_path / "nonexistent.csv", INVOICE_MAPPING)
        assert isinstance(result, ValidationResult)


class TestNonCsvExtension:
    def test_fails(self, tmp_path):
        not_csv = tmp_path / "data.txt"
        not_csv.write_text("col1,col2\nval1,val2\n")
        result = validate(not_csv, INVOICE_MAPPING)
        assert not result.passed

    def test_error_mentions_extension(self, tmp_path):
        not_csv = tmp_path / "data.xlsx"
        not_csv.write_bytes(b"fake xlsx content")
        result = validate(not_csv, INVOICE_MAPPING)
        assert any(".xlsx" in e or "not a csv" in e.lower() for e in result.errors)


# ---------------------------------------------------------------------------
# Mapping validation failures
# ---------------------------------------------------------------------------

class TestMissingRequiredMapping:
    def test_fails_when_required_canonical_absent(self, tmp_path):
        csv_file = tmp_path / "inv.csv"
        write_csv(csv_file,
                  [{"Invoice #": "INV-001", "AVC ID": "LOC001", "Net Charge": "58.00"}],
                  ["Invoice #", "AVC ID", "Net Charge"])

        # Mapping omits invoice_number
        mapping_file = tmp_path / "mapping.yaml"
        write_mapping(mapping_file, "supplier_invoice", {
            "invoice_date":         "Invoice #",   # wrong but present
            "billing_period_start": "Invoice #",
            "billing_period_end":   "Invoice #",
            "supplier_service_id":  "AVC ID",
            "amount_ex_tax":        "Net Charge",
            # invoice_number deliberately omitted
        })

        result = validate(csv_file, mapping_file)
        assert not result.passed
        assert any("invoice_number" in e for e in result.errors)

    def test_error_names_missing_field(self, tmp_path):
        csv_file = tmp_path / "inv.csv"
        write_csv(csv_file, [{"Col A": "x"}], ["Col A"])

        mapping_file = tmp_path / "mapping.yaml"
        write_mapping(mapping_file, "supplier_invoice", {})  # no mappings at all

        result = validate(csv_file, mapping_file)
        assert any("missing required mapping" in e.lower() for e in result.errors)


class TestMappedColumnAbsent:
    def test_fails_when_source_column_not_in_csv(self, tmp_path):
        csv_file = tmp_path / "inv.csv"
        write_csv(csv_file,
                  [{"Invoice Number": "INV-001"}],
                  ["Invoice Number"])

        mapping_file = tmp_path / "mapping.yaml"
        write_mapping(mapping_file, "supplier_invoice", {
            "invoice_number":       "Invoice #",     # "Invoice #" not in CSV
            "invoice_date":         "Invoice Number",
            "billing_period_start": "Invoice Number",
            "billing_period_end":   "Invoice Number",
            "supplier_service_id":  "Invoice Number",
            "amount_ex_tax":        "Invoice Number",
        })

        result = validate(csv_file, mapping_file)
        assert not result.passed
        assert any("not found in csv" in e.lower() for e in result.errors)


# ---------------------------------------------------------------------------
# Numeric and date field validation
# ---------------------------------------------------------------------------

class TestBadNumericField:
    def test_fails_on_non_numeric_amount(self, tmp_path):
        csv_file = tmp_path / "inv.csv"
        write_csv(csv_file,
                  [{"Inv No": "INV-001", "Inv Date": "2026-03-31",
                    "From": "2026-03-01", "To": "2026-03-31",
                    "SVC": "LOC001", "Amount": "NOT_A_NUMBER"}],
                  ["Inv No", "Inv Date", "From", "To", "SVC", "Amount"])

        mapping_file = tmp_path / "mapping.yaml"
        write_mapping(mapping_file, "supplier_invoice", {
            "invoice_number":       "Inv No",
            "invoice_date":         "Inv Date",
            "billing_period_start": "From",
            "billing_period_end":   "To",
            "supplier_service_id":  "SVC",
            "amount_ex_tax":        "Amount",
        })

        result = validate(csv_file, mapping_file)
        assert not result.passed
        assert any("non-numeric" in e.lower() for e in result.errors)


class TestBadDateField:
    def test_fails_on_unparseable_date(self, tmp_path):
        csv_file = tmp_path / "inv.csv"
        write_csv(csv_file,
                  [{"Inv No": "INV-001", "Inv Date": "NOT-A-DATE",
                    "From": "2026-03-01", "To": "2026-03-31",
                    "SVC": "LOC001", "Amount": "58.00"}],
                  ["Inv No", "Inv Date", "From", "To", "SVC", "Amount"])

        mapping_file = tmp_path / "mapping.yaml"
        write_mapping(mapping_file, "supplier_invoice", {
            "invoice_number":       "Inv No",
            "invoice_date":         "Inv Date",
            "billing_period_start": "From",
            "billing_period_end":   "To",
            "supplier_service_id":  "SVC",
            "amount_ex_tax":        "Amount",
        })

        result = validate(csv_file, mapping_file)
        assert not result.passed
        assert any("unparseable date" in e.lower() for e in result.errors)


# ---------------------------------------------------------------------------
# Suggest mapping
# ---------------------------------------------------------------------------

class TestSuggestMapping:
    def test_finds_avc_id(self):
        headers = ["Invoice #", "AVC ID", "Net Charge", "Period From", "Period To", "Inv Date"]
        suggestions = suggest_mapping(headers, "supplier_invoice")
        assert suggestions.get("supplier_service_id") == "AVC ID"

    def test_finds_amount_ex_tax(self):
        headers = ["Invoice #", "AVC ID", "Net Charge", "Period From", "Period To", "Inv Date"]
        suggestions = suggest_mapping(headers, "supplier_invoice")
        assert suggestions.get("amount_ex_tax") == "Net Charge"

    def test_returns_none_for_no_candidate(self):
        headers = ["Col A", "Col B"]
        suggestions = suggest_mapping(headers, "supplier_invoice")
        assert suggestions.get("invoice_number") is None

    def test_returns_dict(self):
        suggestions = suggest_mapping(["X"], "supplier_invoice")
        assert isinstance(suggestions, dict)


# ---------------------------------------------------------------------------
# Duplicate detection
# ---------------------------------------------------------------------------

class TestDuplicateDetection:
    def test_counts_duplicates(self, tmp_path):
        csv_file = tmp_path / "inv.csv"
        row = {"Inv": "INV-001", "SVC": "LOC001", "Amt": "58.00",
               "Date": "2026-03-31", "From": "2026-03-01", "To": "2026-03-31"}
        write_csv(csv_file, [row, row, row], list(row.keys()))  # 3 identical rows = 2 duplicates

        mapping_file = tmp_path / "mapping.yaml"
        write_mapping(mapping_file, "supplier_invoice", {
            "invoice_number":       "Inv",
            "invoice_date":         "Date",
            "billing_period_start": "From",
            "billing_period_end":   "To",
            "supplier_service_id":  "SVC",
            "amount_ex_tax":        "Amt",
        })

        result = validate(csv_file, mapping_file)
        assert result.duplicate_row_count == 2

    def test_no_duplicates_when_rows_differ(self, tmp_path):
        csv_file = tmp_path / "inv.csv"
        rows = [
            {"Inv": "INV-001", "SVC": "LOC001", "Amt": "58.00",
             "Date": "2026-03-31", "From": "2026-03-01", "To": "2026-03-31"},
            {"Inv": "INV-001", "SVC": "LOC002", "Amt": "38.00",
             "Date": "2026-03-31", "From": "2026-03-01", "To": "2026-03-31"},
        ]
        write_csv(csv_file, rows, list(rows[0].keys()))

        mapping_file = tmp_path / "mapping.yaml"
        write_mapping(mapping_file, "supplier_invoice", {
            "invoice_number":       "Inv",
            "invoice_date":         "Date",
            "billing_period_start": "From",
            "billing_period_end":   "To",
            "supplier_service_id":  "SVC",
            "amount_ex_tax":        "Amt",
        })

        result = validate(csv_file, mapping_file)
        assert result.duplicate_row_count == 0
