"""Offline contract checks for the skill-vagrant guidance package (adapted from skill-nautobot's contract, 2026-11-07).

Run: just test (or python -m unittest discover -s tests -p 'test_*.py' with the pack's venv).
"""

from __future__ import annotations

import ast
import hashlib
import re
import sys
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = "documents/research-sources-20261107"
REQUIRED = {
  "SKILL.md",
  "CHANGELOG.md",
  "sources.yaml",
  "compatibility.yaml",
  "references/operations-cookbook.md",
  "references/boxes-and-pinning.md",
  "references/vagrantfile-and-provisioning.md",
  "references/networking-and-synced-folders.md",
  "references/parallels-prlctl.md",
  "references/clones-snapshots-and-identity.md",
  "references/lab-safety-and-guards.md",
  "references/tool-choice-and-lab-symmetry.md",
  "references/licensing-and-editions.md",
  "references/upgrade-and-troubleshooting.md",
  "references/evolution-and-write-back.md",
  "documents/readme.md",
  f"{RESEARCH}/readme.md",
  "tests/requirements.txt",
  "tests/test_package_contract.py",
  "tests/test_helpers.py",
  "tests/scenarios.md",
  "tests/eval-procedure.md",
  "scripts/vagrant_lab_inventory.py",
  "scripts/vagrantfile_lint.py",
  "scripts/vagrant_copy_check.py",
  "scripts/check_governance.py",
}
FORBIDDEN_NAMES = {"manifest.json", "RUNBOOK.md", "agents", "Vagrantfile"}
CLAIM_FIELDS = {"id", "statement", "kind", "evidence_status", "lifecycle", "applies_to", "environment_id", "evidence", "source_type", "reference", "test"}
CLAIM_KINDS = {"generic_invariant", "tested_pattern", "worked_example"}
EVIDENCE = {"VERIFIED_PRIMARY", "VERIFIED_SECONDARY", "UNVERIFIED", "USER_STATED"}
SOURCE_TYPES = {"official_documentation", "vendor_issue_tracker", "observed_install", "implementation", "report_synthesis", "user_policy"}
LIFECYCLES = {"current", "superseded"}
LAYERS = {"observed_install", "official_documented", "implementation_inspected", "offline_contract", "lab_run", "operator_visible"}
RESULTS = {"pass", "fail", "pending_live_test", "stale", "incompatible"}
COMPAT_FIELDS = {"id", "product", "product_version", "components", "observed_at", "evidence_locator", "validation_layer", "result"}
LIVE_LAYERS = {"lab_run", "operator_visible"}


def _load(path: Path) -> dict:
  value = yaml.safe_load(path.read_text(encoding="utf-8"))
  match value:
    case dict():
      return value
    case _:
      raise AssertionError(f"{path.name} must contain a YAML mapping")


LEARNED = re.compile(
  r"^> \*\*(Learned|Disputed) (\d{4}-\d{2}-\d{2})(?: \([a-z]\))?\*\* · (?P<product>[^·]+?) · "
  r"(?P<evidence>VERIFIED_PRIMARY|VERIFIED_SECONDARY|UNVERIFIED|USER_STATED|CANDIDATE)(?: \([^·]*\))? · Source: (?P<source>[^·]+?) · Falsifier: (?P<falsifier>[^·]+?)"
  r"(?: · Conflicts: (?P<conflicts>.+))?$"
)


def _without_fences(text: str) -> str:
  return re.sub(r"(?ms)^```.*?^```", "", text)


def _learned_entries(text: str) -> list[tuple[str, str, str]]:
  """Return (kind, date, header) for every write-back entry outside code fences; raise on a malformed one.

  The Markdown wrap hook folds a long header over several "> " lines; continuation lines are joined until the header parses, so a header whose
  Conflicts field was folded onto the next line still parses whole.
  """
  entries = []
  lines = _without_fences(text).splitlines()
  for index, line in enumerate(lines):
    if not re.match(r"^> \*\*(?:Learned|Disputed)\b", line):
      continue
    following = lines[index + 1 : index + 6]
    joined = line

    def complete(text: str) -> bool:
      found = LEARNED.match(text)
      return bool(found and (found.group(1) == "Learned" or found.group("conflicts")))

    while not complete(joined) and following and following[0].startswith("> ") and not re.match(r"^> \*\*", following[0]):
      joined = joined + " " + following.pop(0)[2:]
    match = LEARNED.match(joined)
    if not match:
      raise AssertionError(f"malformed write-back entry: {line[:80]}")
    if match.group(1) == "Disputed" and not match.group("conflicts"):
      raise AssertionError("a Disputed entry must name what it conflicts with")
    entries.append((match.group(1), match.group(2), joined))
  return entries


def _research_index(index: str) -> dict[str, str]:
  rows = re.findall(r"^\| \[([^\]]+)\]\([^)]+\) \|.*\| `([0-9a-f]{64})` \|$", index, re.MULTILINE)
  return dict(rows)


def _scenario_relevant(scenarios: str, scenario_id: str, reference: str) -> bool:
  block = re.search(rf"(?ms)^## {re.escape(scenario_id)} —.*?(?=^## |\Z)", scenarios)
  return bool(block and Path(reference).name in block.group(0))


AUTHORED_RULES = {
  r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----": "private key delimiter",
  r"(?im)^authorization:\s*(?!Bearer DUMMY_TOKEN_DO_NOT_USE$).+": "live authorization header",
  r"(?im)^(?:password|token|api[_-]?key)\s*[:=]\s*(?!DUMMY_TOKEN_DO_NOT_USE\s*$).+": "non-dummy credential assignment",
  r"(?i)\b(?:teleport|communitywifi|apn)\.(?:au|com)\b": "production domain",
  r"\b(?:10\.\d{1,3}\.|172\.(?:1[6-9]|2\d|3[01])\.\d|192\.168\.\d)": "unsafe private-address example",
}
# Verbatim third-party captures keep the publisher's own examples (private addresses in Vagrant's networking docs, for instance); only a key
# or a live credential is refused there.
CAPTURE_RULES = {k: v for k, v in AUTHORED_RULES.items() if v in {"private key delimiter", "live authorization header"}}


def _assert_safe_text(text: str, path: str = "fixture", rules: dict[str, str] = AUTHORED_RULES) -> None:
  for pattern, reason in rules.items():
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
  def test_required_tree_and_forbidden_names(self) -> None:
    actual = {path.relative_to(ROOT).as_posix() for path in ROOT.rglob("*") if path.is_file()}
    self.assertTrue(REQUIRED <= actual, sorted(REQUIRED - actual))
    self.assertFalse({path.name for path in ROOT.rglob("*")} & FORBIDDEN_NAMES, "no Vagrantfile, manifest or agents dir in the pack")

  def test_entrypoint_routes_every_reference(self) -> None:
    content = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    frontmatter = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    self.assertIsNotNone(frontmatter)
    metadata = yaml.safe_load(frontmatter.group(1))
    self.assertEqual(set(metadata), {"name", "description"})
    self.assertEqual(metadata["name"], "skill-vagrant")
    self.assertTrue(metadata["description"].strip())
    self.assertLessEqual(len(metadata["description"]), 1024, "description over the 1024-character skill limit")
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
      self.assertRegex(claim["id"], r"^V-C\d{2}$")
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
      self.assertTrue((ROOT / claim["reference"]).is_file(), claim["id"])
      capture = re.findall(r"research-sources-\d{8}/[\w.-]*\w", str(claim["evidence"]))
      for cap in capture:
        self.assertTrue((ROOT / "documents" / cap).is_file(), f"{claim['id']} cites missing capture {cap}")
      self.assertIn(claim["test"], scenario_text)
      self.assertTrue(_scenario_relevant(scenario_text, claim["test"], claim["reference"]), f"{claim['id']} links to unrelated scenario")
      self.assertRegex(claim["statement"], r"\.$")
      if claim["lifecycle"] == "superseded":
        self.assertTrue(claim.get("superseded_by"))
    self.assertRegex((ROOT / "CHANGELOG.md").read_text(encoding="utf-8"), r"## 0\.\d+\.\d+")

  def test_content_is_redacted(self) -> None:
    for path in ROOT.rglob("*"):
      if not path.is_file() or path.suffix not in {".md", ".yaml", ".txt"}:
        continue
      rel = path.relative_to(ROOT).as_posix()
      capture = rel.startswith("documents/research-sources-") and path.name != "readme.md"
      _assert_safe_text(path.read_text(encoding="utf-8"), rel, CAPTURE_RULES if capture else AUTHORED_RULES)

  def test_research_index_covers_every_capture_with_its_hash(self) -> None:
    folders = sorted(p for p in (ROOT / "documents").glob("research-sources-*") if p.is_dir())
    self.assertTrue(folders)
    top = (ROOT / "documents/readme.md").read_text(encoding="utf-8")
    for folder in folders:
      self.assertIn(folder.name, top, "documents/readme.md must route every research folder")
      index = _research_index((folder / "readme.md").read_text(encoding="utf-8"))
      local = {p.name for p in folder.iterdir() if p.is_file() and p.name != "readme.md" and not p.name.startswith(".")}
      self.assertEqual(local, set(index), f"{folder.name}/readme.md must list exactly the captures")
      for name, expected in index.items():
        data = (folder / name).read_bytes()
        self.assertGreater(len(data), 300, name)
        self.assertEqual(hashlib.sha256(data).hexdigest(), expected, name)
        if name.endswith(".md"):
          head = data[:600].decode("utf-8", "replace")
          for field in ("**Canonical URL**", "**Retrieved**", "**HTTP status**"):
            self.assertIn(field, head, f"{name} lacks {field}")

  def test_write_back_entries_are_well_formed_and_logged(self) -> None:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    for reference in sorted((ROOT / "references").glob("*.md")):
      for _kind, date, _line in _learned_entries(reference.read_text(encoding="utf-8")):
        logged = [line for line in changelog.splitlines() if date in line and reference.name in line]
        self.assertTrue(logged, f"{reference.name} entry {date} has no CHANGELOG line naming the file and date")

  def test_cookbook_names_a_recorded_version(self) -> None:
    cookbook = (ROOT / "references/operations-cookbook.md").read_text(encoding="utf-8")
    verified = re.search(r"^Verified against: (.+)$", cookbook, re.MULTILINE)
    self.assertIsNotNone(verified, "operations-cookbook.md needs a 'Verified against:' line")
    self.assertRegex(verified.group(1), r"\d{4}-\d{2}-\d{2}")
    versions = {str(row["product_version"]) for row in _load(ROOT / "compatibility.yaml")["environments"]}
    self.assertTrue(
      any(v in verified.group(1) for v in versions if re.fullmatch(r"[\d.]+", v)),
      "the cookbook's verified version must be a compatibility.yaml product_version",
    )

  def test_negative_fixtures_prove_write_back_checks(self) -> None:
    good = "> **Learned 2026-11-07** · Vagrant 2.4.9 · VERIFIED_PRIMARY · Source: https://example.org/doc · Falsifier: a 2.4.9 run that shows otherwise"
    self.assertEqual(len(_learned_entries(good)), 1)
    folded = "> **Disputed 2026-11-07** · Product 1 · VERIFIED_PRIMARY · Source: x · Falsifier: y ·\n> Conflicts: an earlier statement\n> The fact."
    self.assertEqual(len(_learned_entries(folded)), 1)
    self.assertEqual(_learned_entries("```text\n> **Learned 2026-11-07** · x\n```\n"), [])
    for bad in (
      "> **Learned 2026-11-07** · Vagrant 2.4.9 · VERIFIED · Source: x · Falsifier: y",
      "> **Learned 2026-11-07** · Vagrant 2.4.9 · UNVERIFIED · Source: x",
      "> **Disputed 2026-11-07** · Vagrant 2.4.9 · UNVERIFIED · Source: x · Falsifier: y",
    ):
      with self.assertRaises(AssertionError):
        _learned_entries(bad)

  def test_every_helper_is_tested_and_stdlib_only(self) -> None:
    tests = (ROOT / "tests/test_helpers.py").read_text(encoding="utf-8")
    allowed = set(sys.stdlib_module_names) | {p.stem for p in (ROOT / "scripts").glob("*.py")}
    for helper in sorted((ROOT / "scripts").glob("*.py")):
      self.assertIn(f'"{helper.stem}"', tests, f"{helper.name} has no tests in tests/test_helpers.py")
      for node in ast.walk(ast.parse(helper.read_text(encoding="utf-8"))):
        names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""] if isinstance(node, ast.ImportFrom) else []
        for name in names:
          self.assertIn(name.split(".")[0], allowed | {"__future__"}, f"{helper.name} imports {name}: helpers stay stdlib-only")

  def test_every_subprocess_call_in_helpers_has_a_timeout(self) -> None:
    for helper in sorted((ROOT / "scripts").glob("*.py")):
      for node in ast.walk(ast.parse(helper.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in {"run", "check_output", "urlopen"}:
          owner = getattr(node.func.value, "id", "")
          if owner in {"subprocess", "request"} or node.func.attr == "urlopen":
            self.assertIn("timeout", {k.arg for k in node.keywords}, f"{helper.name}:{node.lineno} call without timeout")

  def test_negative_fixtures_prove_sensitive_content_checks(self) -> None:
    self.assertIsNone(_assert_safe_text("## 10. Management commands"))
    for unsafe in ("Authorization: Bearer real-token", "password=not-a-dummy", "-----BEGIN PRIVATE KEY-----", "host 10.1.2.3", "ip 192.168.50.4"):
      with self.assertRaises(AssertionError):
        _assert_safe_text(unsafe)
    self.assertIsNone(_assert_safe_text("ip 192.168.50.4", "capture", CAPTURE_RULES))
    with self.assertRaises(AssertionError):
      _assert_safe_text("-----BEGIN OPENSSH PRIVATE KEY-----", "capture", CAPTURE_RULES)

  def test_negative_fixture_proves_evidence_rung_check(self) -> None:
    bad = {
      "environments": [
        {
          "id": "bad",
          "product": "Vagrant",
          "product_version": "1",
          "components": [],
          "observed_at": "2026-11-07",
          "evidence_locator": "x",
          "validation_layer": "observed_install",
          "result": "pass",
          "note": "operator-visible console",
        }
      ]
    }
    with self.assertRaises(AssertionError):
      _validate_compatibility(bad)

  def test_negative_fixture_proves_live_evidence_requires_test_id(self) -> None:
    bad = {
      "environments": [
        {
          "id": "bad",
          "product": "Vagrant",
          "product_version": "2",
          "components": [],
          "observed_at": "2026-11-07",
          "evidence_locator": "x",
          "validation_layer": "lab_run",
          "result": "pass",
        }
      ]
    }
    with self.assertRaises(AssertionError):
      _validate_compatibility(bad)

  def test_negative_fixture_rejects_irrelevant_claim_scenario(self) -> None:
    text = "## V-S03 — Wrong VM answers\nFirst reference: `lab-safety-and-guards.md`.\n"
    self.assertFalse(_scenario_relevant(text, "V-S03", "references/boxes-and-pinning.md"))


if __name__ == "__main__":
  unittest.main()
