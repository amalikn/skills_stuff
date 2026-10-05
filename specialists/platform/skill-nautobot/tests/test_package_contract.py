"""Offline contract checks for the skill-nautobot guidance package."""

from __future__ import annotations

import hashlib
import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "SKILL.md", "CHANGELOG.md", "sources.yaml", "compatibility.yaml",
    "references/authority-and-modeling.md", "references/api-and-writers.md",
    "references/staged-onboarding.md", "references/lifecycle-and-replacement.md",
    "references/discovery-and-topology.md", "references/apps-jobs-validation.md",
    "references/config-backup-compliance.md", "references/capability-extension.md",
    "references/upgrade-and-troubleshooting.md", "references/evolution-and-write-back.md", "references/operations-cookbook.md",
    "documents/readme.md", "documents/nautobot-core-3.2.2-release-notes.html", "documents/nautobot-namespace-current-docs.html",
    "tests/requirements.txt", "tests/test_package_contract.py", "tests/scenarios.md",
    "tests/eval-procedure.md",
}
FORBIDDEN_NAMES = {
    "manifest.json", "RUNBOOK.md", "upstream-links.md", "paginate.py", "fingerprint.py",
    "netjson_mapping.py", "agents", "scripts",
}
CLAIM_FIELDS = {"id", "statement", "kind", "evidence_status", "lifecycle", "applies_to", "environment_id", "evidence", "source_type", "reference", "test"}
CLAIM_KINDS = {"generic_invariant", "tested_pattern", "worked_example"}
EVIDENCE = {"VERIFIED_PRIMARY", "VERIFIED_SECONDARY", "UNVERIFIED", "USER_STATED"}
SOURCE_TYPES = {"official_documentation", "observed_install", "implementation", "implementation_and_test", "implementation_and_design", "report_synthesis", "user_policy"}
LIFECYCLES = {"current", "superseded"}
LAYERS = {"observed_install", "official_documented", "implementation_inspected", "offline_contract", "api_accepted", "worker_processed", "metric_persisted", "recent_point", "operator_visible"}
RESULTS = {"pass", "fail", "pending_live_test", "stale", "incompatible"}
COMPAT_FIELDS = {"id", "product", "product_version", "components", "observed_at", "evidence_locator", "validation_layer", "result"}
LIVE_LAYERS = {"api_accepted", "worker_processed", "metric_persisted", "recent_point", "operator_visible"}


def _load(path: Path) -> dict:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{path.name} must contain a YAML mapping")
    return value


LEARNED = re.compile(
    r"^> \*\*(Learned|Disputed) (\d{4}-\d{2}-\d{2})\*\* · (?P<product>[^·]+?) · "
    r"(?P<evidence>VERIFIED_PRIMARY|VERIFIED_SECONDARY|UNVERIFIED|USER_STATED) · Source: (?P<source>[^·]+?) · Falsifier: (?P<falsifier>[^·]+?)"
    r"(?: · Conflicts: (?P<conflicts>.+))?$"
)


def _without_fences(text: str) -> str:
    return re.sub(r"(?ms)^```.*?^```", "", text)


def _learned_entries(text: str) -> list[tuple[str, str, str]]:
    """Return (kind, date, line) for every write-back entry outside code fences; raise on a malformed one."""
    entries = []
    for line in _without_fences(text).splitlines():
        if not re.match(r"^> \*\*(?:Learned|Disputed)\b", line):
            continue
        match = LEARNED.match(line)
        if not match:
            raise AssertionError(f"malformed write-back entry: {line[:80]}")
        if match.group(1) == "Disputed" and not match.group("conflicts"):
            raise AssertionError("a Disputed entry must name what it conflicts with")
        entries.append((match.group(1), match.group(2), line))
    return entries


def _snapshot_index(index: str) -> dict[str, str]:
    rows = re.findall(r"^\| \[([^\]]+)\]\([^)]+\) \|.*\| `([0-9a-f]{64})` \|$", index, re.M)
    return dict(rows)


def _scenario_relevant(scenarios: str, scenario_id: str, reference: str) -> bool:
    block = re.search(rf"(?ms)^## {re.escape(scenario_id)} \u2014.*?(?=^## |\Z)", scenarios)
    return bool(block and Path(reference).name in block.group(0))


def _assert_safe_text(text: str, path: str = "fixture") -> None:
    patterns = {
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----": "private key delimiter",
        r"(?im)^authorization:\s*(?!Bearer DUMMY_TOKEN_DO_NOT_USE$).+": "live authorization header",
        r"(?im)^(?:password|token|api[_-]?key)\s*[:=]\s*(?!DUMMY_TOKEN_DO_NOT_USE\s*$).+": "non-dummy credential assignment",
        r"(?i)\b(?:teleport|communitywifi|apn)\.(?:au|com)\b": "production domain",
        r"(?:captures/|/captures/|transcript|raw[-_ ]?capture)": "raw capture/transcript reference",
        r"\b(?:10\.\d{1,3}\.|172\.(?:1[6-9]|2\d|3[01])\.\d|192\.168\.\d)": "unsafe private-address example",
    }
    for pattern, reason in patterns.items():
        if re.search(pattern, text):
            raise AssertionError(f"{path}: {reason}")


def _validate_compatibility(document: dict) -> set[str]:
    rows = document.get("environments")
    if not isinstance(rows, list) or not rows:
        raise AssertionError("compatibility.yaml requires non-empty environments")
    ids: set[str] = set()
    for row in rows:
        if not isinstance(row, dict) or not COMPAT_FIELDS <= set(row):
            raise AssertionError("compatibility row missing required fields")
        if row["id"] in ids or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", str(row["id"])):
            raise AssertionError("compatibility IDs must be unique kebab-case")
        ids.add(row["id"])
        if row["validation_layer"] not in LAYERS or row["result"] not in RESULTS:
            raise AssertionError("invalid compatibility layer or result")
        if row["validation_layer"] in LIVE_LAYERS and not isinstance(row.get("test_id"), str):
            raise AssertionError("a live-evidence row requires a test_id")
        if row["validation_layer"] == "observed_install" and row["result"] == "pass" and "operator-visible" in str(row).lower():
            raise AssertionError("observed install cannot prove operator-visible behaviour")
    return ids


class PackageContractTests(unittest.TestCase):
    def test_required_tree_and_no_deferred_helpers(self) -> None:
        actual = {path.relative_to(ROOT).as_posix() for path in ROOT.rglob("*") if path.is_file()}
        self.assertTrue(REQUIRED <= actual, sorted(REQUIRED - actual))
        self.assertFalse({path.name for path in ROOT.rglob("*")} & FORBIDDEN_NAMES)

    def test_entrypoint_routes_every_reference(self) -> None:
        content = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = re.match(r"^---\n(.*?)\n---\n", content, re.S)
        self.assertIsNotNone(frontmatter)
        metadata = yaml.safe_load(frontmatter.group(1))
        self.assertEqual(set(metadata), {"name", "description"})
        self.assertEqual(metadata["name"], "skill-nautobot")
        self.assertTrue(metadata["description"].strip())
        self.assertNotIn("TODO", content.upper())
        for reference in sorted(path for path in REQUIRED if path.startswith("references/")):
            self.assertIn(reference, content)

    def test_claim_and_compatibility_schema(self) -> None:
        sources = _load(ROOT / "sources.yaml")
        environment_ids = _validate_compatibility(_load(ROOT / "compatibility.yaml"))
        claims = sources.get("claims")
        self.assertIsInstance(claims, list)
        self.assertTrue(claims)
        ids: set[str] = set()
        scenario_text = (ROOT / "tests/scenarios.md").read_text(encoding="utf-8")
        for claim in claims:
            self.assertTrue(CLAIM_FIELDS <= set(claim), claim)
            self.assertNotIn(claim["id"], ids)
            ids.add(claim["id"])
            self.assertIn(claim["kind"], CLAIM_KINDS)
            self.assertIn(claim["evidence_status"], EVIDENCE)
            self.assertIn(claim["source_type"], SOURCE_TYPES)
            self.assertIn(claim["lifecycle"], LIFECYCLES)
            self.assertTrue(set(claim["applies_to"]) <= environment_ids)
            if claim["evidence_status"] == "USER_STATED":
                self.assertIsNone(claim["environment_id"], claim["id"])
                self.assertEqual(claim["applies_to"], [], claim["id"])
                self.assertEqual(claim["source_type"], "user_policy")
            else:
                self.assertIn(claim["environment_id"], environment_ids)
                self.assertIn(claim["environment_id"], claim["applies_to"])
                self.assertNotEqual(claim["source_type"], "user_policy")
            if claim["evidence_status"] == "VERIFIED_PRIMARY":
                self.assertNotEqual(claim["source_type"], "report_synthesis", claim["id"])
            self.assertTrue((ROOT / claim["reference"]).is_file())
            self.assertIn(claim["test"], scenario_text)
            self.assertTrue(_scenario_relevant(scenario_text, claim["test"], claim["reference"]), f"{claim['id']} links to unrelated scenario")
            self.assertRegex(claim["statement"], r"\.$")
            self.assertNotRegex(claim["statement"].lower(), r"api acceptance.*(?:complete|working).*monitoring")
            if claim["lifecycle"] == "superseded":
                self.assertTrue(claim.get("superseded_by"))
        self.assertRegex((ROOT / "CHANGELOG.md").read_text(encoding="utf-8"), r"0\.\d+\.\d+")

    def test_content_is_redacted_and_routes_are_real(self) -> None:
        for path in ROOT.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".yaml", ".txt"}:
                _assert_safe_text(path.read_text(encoding="utf-8"), path.relative_to(ROOT).as_posix())

    def test_document_snapshot_index_covers_local_copies(self) -> None:
        index = _snapshot_index((ROOT / "documents/readme.md").read_text(encoding="utf-8"))
        local = {path.name for path in (ROOT / "documents").iterdir() if path.is_file() and path.name != "readme.md"}
        self.assertEqual(local, set(index), "documents/readme.md must list exactly the local snapshots")
        for name, expected_hash in index.items():
            snapshot = ROOT / "documents" / name
            self.assertGreater(snapshot.stat().st_size, 1_000, name)
            self.assertEqual(hashlib.sha256(snapshot.read_bytes()).hexdigest(), expected_hash, name)

    def test_write_back_entries_are_well_formed_and_logged(self) -> None:
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        for reference in sorted((ROOT / "references").glob("*.md")):
            for _kind, date, _line in _learned_entries(reference.read_text(encoding="utf-8")):
                logged = [line for line in changelog.splitlines() if date in line and reference.name in line]
                self.assertTrue(logged, f"{reference.name} entry {date} has no CHANGELOG line naming the file and date")

    def test_cookbook_names_a_recorded_version(self) -> None:
        cookbook = (ROOT / "references/operations-cookbook.md").read_text(encoding="utf-8")
        verified = re.search(r"^Verified against: (.+)$", cookbook, re.M)
        self.assertIsNotNone(verified, "operations-cookbook.md needs a 'Verified against:' line")
        self.assertRegex(verified.group(1), r"\d{4}-\d{2}-\d{2}")
        versions = {str(row["product_version"]) for row in _load(ROOT / "compatibility.yaml")["environments"]}
        self.assertTrue(any(v in verified.group(1) for v in versions if re.fullmatch(r"[\d.]+", v)),
                        "the cookbook's verified version must be a compatibility.yaml product_version")

    def test_negative_fixtures_prove_write_back_checks(self) -> None:
        good = "> **Learned 2026-10-05** · Product 1.2.3 · VERIFIED_PRIMARY · Source: https://example.org/doc · Falsifier: a 1.2.3 run that shows otherwise"
        self.assertEqual(len(_learned_entries(good)), 1)
        self.assertEqual(_learned_entries("```text\n> **Learned 2026-10-05** · x\n```\n"), [])
        for bad in ("> **Learned 2026-10-05** · Product 1.2.3 · VERIFIED · Source: x · Falsifier: y",
                    "> **Learned 2026-10-05** · Product 1.2.3 · UNVERIFIED · Source: x",
                    "> **Disputed 2026-10-05** · Product 1.2.3 · UNVERIFIED · Source: x · Falsifier: y"):
            with self.assertRaises(AssertionError):
                _learned_entries(bad)

    def test_negative_fixtures_prove_sensitive_content_checks(self) -> None:
        self.assertIsNone(_assert_safe_text("## 10. Management commands"))
        for unsafe in ("Authorization: Bearer real-token", "password=not-a-dummy", "-----BEGIN PRIVATE KEY-----", "host 10.1.2.3"):
            with self.assertRaises(AssertionError):
                _assert_safe_text(unsafe)

    def test_negative_fixture_proves_evidence_rung_check(self) -> None:
        bad = {"environments": [{"id": "bad", "product": "OpenWISP", "product_version": "1", "components": [], "observed_at": "2026-10-01", "evidence_locator": "x", "validation_layer": "observed_install", "result": "pass", "note": "operator-visible graph"}]}
        with self.assertRaises(AssertionError):
            _validate_compatibility(bad)

    def test_negative_fixture_proves_live_evidence_requires_test_id(self) -> None:
        bad = {"environments": [{"id": "bad", "product": "Nautobot", "product_version": "3", "components": [], "observed_at": "2026-10-01", "evidence_locator": "x", "validation_layer": "worker_processed", "result": "pass"}]}
        with self.assertRaises(AssertionError):
            _validate_compatibility(bad)

    def test_negative_fixture_rejects_irrelevant_claim_scenario(self) -> None:
        text = "## N-S13 \u2014 Unauthorized production mutation\nFirst reference: `api-and-writers.md`.\n"
        self.assertFalse(_scenario_relevant(text, "N-S13", "references/discovery-and-topology.md"))


if __name__ == "__main__":
    unittest.main()
