#!/usr/bin/env python3
"""Validate the navigation control layer in a project.

Checks governance file presence, managed block integrity, version stamps,
context-map.yaml schema, generated-output policy, and companion consistency.

Usage:
    python scripts/validate_navigation_control_layer.py --project-root /path/to/project
    python scripts/validate_navigation_control_layer.py --project-root /path/to/project --report-json /path/to/report.json
"""

import argparse
import json
import os
import re
import sys

# Must stay identical to the VERSION constant in upgrade_navigation_control_layer.py. A project whose managed block carries an older stamp is reported as missing the current version stamp, which is
# the intended signal to re-run the upgrade — not a defect in the project.
VERSION = "2026-08-11-governance-checks-layer-v1"
MANAGED_VERSION_LINE = f"<!-- skill-ai-it-version: {VERSION} -->"

# Explicit project opt-out, honoured by upgrade_navigation_control_layer.py too. Kept identical in
# both scripts on purpose — drift between them would let the upgrader skip a block the validator
# still fails, which is the worst of both.
MANUAL_TOKEN = "skill-ai-it:manual"
BEGIN_MANAGED = re.compile(r"<!--\s*BEGIN\s+MANAGED:\s*skill-ai-it:([A-Za-z0-9_-]+)\s*-->")
END_MANAGED = re.compile(r"<!--\s*END\s+MANAGED:\s*skill-ai-it:([A-Za-z0-9_-]+)\s*-->")
OLD_BEGIN = re.compile(r"<!--\s*BEGIN\s+skill-ai-it:([A-Za-z0-9_-]+)\s*-->")

OLD_END = re.compile(r"<!--\s*END\s+skill-ai-it:([A-Za-z0-9_-]+)\s*-->")
REQUIRED_GOVERNANCE_FILES = ["AI_NAVIGATION.md", "context-map.yaml", "AGENTS.md", "CHANGELOG.md"]
OPTIONAL_TASK_RUNNERS = ["justfile", "Makefile", "Taskfile.yml", "package.json"]
REQUIRED_CONTEXT_MAP_KEYS = ["audit_checks", "promotion_rules", "context_recovery", "update_rules"]


def relpath(path: str, root: str) -> str:
    try:
        return os.path.relpath(path, root)
    except ValueError:
        return path


def load_yaml_module():
    try:
        import yaml
        return yaml
    except ImportError:
        print("ERROR: PyYAML is required. Install with: python -m pip install pyyaml", file=sys.stderr)
        sys.exit(1)


def add_result(results: dict, severity: str, message: str) -> None:
    if severity == "pass":
        results["passed"].append(message)
    elif severity == "warn":
        results["warnings"].append(message)
    elif severity == "fail":
        results["failures"].append(message)
    else:
        raise ValueError(f"unknown severity: {severity}")


def get_nested(mapping: dict, path: list[str]):
    cur = mapping
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return None
        cur = cur[key]
    return cur


def parse_args():
    p = argparse.ArgumentParser(description="Validate navigation control layer")
    p.add_argument("--project-root", required=True, help="Path to project root")
    p.add_argument("--report-json", help="Write report JSON to file")
    return p.parse_args()


def green(s):
    return f"\033[92m{s}\033[0m"


def yellow(s):
    return f"\033[93m{s}\033[0m"


def red(s):
    return f"\033[91m{s}\033[0m"


def check_file_exists(path, label, root=None):
    display = relpath(path, root) if root else label
    if os.path.isfile(path):
        return (True, f"{display}: present")
    return (False, f"{display}: MISSING")


def read_file_content(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return None
    except UnicodeDecodeError as e:
        return f"__READ_ERROR__:{e}"


def check_managed_block_integrity(text, file_label, results, required_sections=None, allow_old_markers=False):
    """Check managed block integrity in a file."""
    if not text:
        return
    if text.startswith("__READ_ERROR__:"):
        add_result(results, "fail", f"{file_label}: read error: {text}")
        return

    # Placeholder examples such as `skill-ai-it:...` are intentionally ignored
    # by the section regex constants. Only concrete section names like
    # `navigation` and `scripts` are treated as managed blocks.

    required_sections = required_sections or []
    begins = BEGIN_MANAGED.findall(text)
    ends = END_MANAGED.findall(text)

    for section in sorted(set(begins)):
        if begins.count(section) > 1:
            add_result(results, "fail", f"{file_label}: duplicate managed block section '{section}'")
    for section in sorted(set(ends)):
        if ends.count(section) > 1:
            add_result(results, "fail", f"{file_label}: duplicate END managed block section '{section}'")

    for section in begins:
        if section not in ends:
            add_result(results, "fail", f"{file_label}: BEGIN MANAGED:{section} has no matching END")
    for section in ends:
        if section not in begins:
            add_result(results, "fail", f"{file_label}: END MANAGED:{section} has no matching BEGIN")

    # A project that has taken explicit ownership of its blocks is not missing them. Without this,
    # an opted-out project is permanently red, which is worse than being unmanaged: a validator that
    # always fails is a validator nobody reads, and the next real failure goes unnoticed with it.
    manual = MANUAL_TOKEN in text
    for section in required_sections:
        if section not in begins:
            if manual:
                add_result(results, "pass",
                           f"{file_label}: '{section}' block is project-managed "
                           f"({MANUAL_TOKEN} declared) — skill-ai-it will not replace it")
            else:
                add_result(results, "fail", f"{file_label}: required managed block '{section}' MISSING")

    for m in BEGIN_MANAGED.finditer(text):
        section = m.group(1)
        end_match = END_MANAGED.search(text, m.end())
        block_text = text[m.end():end_match.start()] if end_match else text[m.end():]
        if MANAGED_VERSION_LINE not in block_text:
            add_result(results, "fail", f"{file_label}: managed block '{section}' missing current version stamp")

    old_begin = OLD_BEGIN.search(text)
    old_end = OLD_END.search(text)
    if old_begin or old_end:
        msg = f"{file_label}: old-style skill-ai-it marker detected"
        if manual:
            add_result(results, "pass",
                       f"{file_label}: old-style marker retained under {MANUAL_TOKEN} — "
                       f"project-managed, not a defect")
        elif allow_old_markers:
            add_result(results, "warn", f"{msg} (legacy text/reference only)")
        else:
            add_result(results, "fail", msg)
    elif begins:
        add_result(results, "pass", f"{file_label}: managed block integrity passed")


def check_yaml(path, results, root):
    display = relpath(path, root)
    if not os.path.exists(path):
        add_result(results, "fail", f"{display}: MISSING")
        return None
    yaml = load_yaml_module()
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            add_result(results, "fail", f"{display}: not a valid YAML mapping")
            return None
        add_result(results, "pass", f"{display}: YAML parse passed")
        return data
    except Exception as e:
        add_result(results, "fail", f"{display}: YAML parse error: {e}")
        return None


def validate_context_map(data, results):
    for key in REQUIRED_CONTEXT_MAP_KEYS:
        if key in data:
            add_result(results, "pass", f"context-map.yaml: '{key}' present")
        else:
            add_result(results, "fail", f"context-map.yaml: '{key}' MISSING")

    version = data.get("skill_ai_it_version")
    if version == VERSION:
        add_result(results, "pass", "context-map.yaml: skill_ai_it_version current")
    elif version is None:
        add_result(results, "warn", "context-map.yaml: skill_ai_it_version missing")
    else:
        add_result(results, "warn", f"context-map.yaml: skill_ai_it_version mismatch ({version})")

    comp = get_nested(data, ["audit_checks", "companion_update_completeness"])
    if isinstance(comp, dict):
        comp_text = json.dumps(comp).lower()
        if "update_rules" in comp_text:
            add_result(results, "pass", "context-map.yaml: companion audit references update_rules")
        else:
            add_result(results, "warn", "context-map.yaml: companion audit does not reference update_rules")

    up = data.get("update_rules")
    if isinstance(up, dict):
        gov = up.get("governance_navigation")
        if isinstance(gov, dict):
            required_entries = ["AGENTS.md", "AI_NAVIGATION.md", "context-map.yaml", "scripts/README.md", "new_script_added"]
            missing = [entry for entry in required_entries if entry not in gov]
            if missing:
                add_result(results, "fail", f"context-map.yaml: update_rules.governance_navigation missing {', '.join(missing)}")
            else:
                add_result(results, "pass", "context-map.yaml: update_rules.governance_navigation complete")
        elif any(k in up for k in ["new_mode", "durable_decision"]):
            add_result(results, "warn", "context-map.yaml: update_rules uses legacy structure; governance_navigation not found")
        else:
            add_result(results, "fail", "context-map.yaml: update_rules present but unrecognized")
    else:
        add_result(results, "fail", "context-map.yaml: update_rules is not a mapping")

    arch = get_nested(data, ["promotion_rules", "archcore"])
    if isinstance(arch, dict) and arch.get("required_authorization") is True:
        add_result(results, "pass", "context-map.yaml: .archcore/ promotion gate enforced")
    elif arch:
        add_result(results, "fail", "context-map.yaml: .archcore/ promotion required_authorization is not True")
    else:
        add_result(results, "warn", "context-map.yaml: promotion_rules.archcore.required_authorization not found")

    if data.get("context_recovery"):
        add_result(results, "pass", "context-map.yaml: context_recovery present")
    else:
        add_result(results, "fail", "context-map.yaml: context_recovery MISSING")


def validate_ai_navigation(ai_nav, results):
    if not ai_nav:
        return
    if ai_nav.startswith("__READ_ERROR__:"):
        add_result(results, "fail", f"AI_NAVIGATION.md: read error: {ai_nav}")
        return

    stale_patterns = [
        r"\.ai-context/[^\n]{0,80}are not present",
        r"graphify-out/[^\n]{0,80}are not present",
        r"do not create (`?\.ai-context/`?|`?graphify-out/`?)",
    ]
    for pattern in stale_patterns:
        if re.search(pattern, ai_nav, re.IGNORECASE):
            add_result(results, "warn", f"AI_NAVIGATION.md: potentially stale generated-output claim matching /{pattern}/")

    lowered = ai_nav.lower()
    if "support-only" in lowered or "support only" in lowered or "generated support" in lowered:
        add_result(results, "pass", "AI_NAVIGATION.md: generated-output support-only policy present")
    else:
        add_result(results, "fail", "AI_NAVIGATION.md: missing generated-output support-only policy")

    if "compaction recovery" in lowered:
        add_result(results, "pass", "AI_NAVIGATION.md: context compaction recovery present")
    else:
        add_result(results, "fail", "AI_NAVIGATION.md: context compaction recovery MISSING")

    if "companion" in lowered:
        add_result(results, "pass", "AI_NAVIGATION.md: companion consistency section present")
    else:
        add_result(results, "warn", "AI_NAVIGATION.md: companion consistency section not found")


def validate_scripts_governance(root, data, results):
    scripts_dir = os.path.join(root, "scripts")
    scripts_readme = os.path.join(scripts_dir, "README.md")
    if os.path.isdir(scripts_dir):
        if os.path.exists(scripts_readme):
            add_result(results, "pass", "scripts/README.md: present (scripts/ exists)")
            text = read_file_content(scripts_readme)
            check_managed_block_integrity(text, "scripts/README.md", results, required_sections=["scripts"])
        else:
            add_result(results, "fail", "scripts/README.md: MISSING (scripts/ exists)")

    present_runners = []
    for runner in OPTIONAL_TASK_RUNNERS:
        if os.path.exists(os.path.join(root, runner)):
            present_runners.append(runner)
            add_result(results, "pass", f"{runner}: present")

    if present_runners:
        scripts_text = read_file_content(scripts_readme) or ""
        context_text = json.dumps(data or {}).lower()
        missing_refs = [runner for runner in present_runners if runner.lower() not in scripts_text.lower() and runner.lower() not in context_text]
        if missing_refs:
            add_result(results, "warn", f"Task runner references not found in scripts/README.md or context-map.yaml: {', '.join(missing_refs)}")
        else:
            add_result(results, "pass", "Task runner references documented")

    validate_governance_checker(root, present_runners, results)


def validate_governance_checker(root, present_runners, results):
    """Report on the project's executable governance checker.

    Advisory only. Absence is reported as a warning rather than a failure because the checker is a capability projects adopt during a refresh, not a precondition of the navigation control layer —
    failing here would mark every project bootstrapped before the capability existed as broken. Once a checker is present, being unwired IS a defect worth flagging: a checker nothing runs is a
    document with a .py extension.
    """
    checker = os.path.join(root, "scripts", "check_governance.py")
    if not os.path.exists(checker):
        add_result(results, "warn", "scripts/check_governance.py: not present (run /skill-ai-it refresh to add executable governance checks)")
        return

    add_result(results, "pass", "scripts/check_governance.py: present")

    wired = False
    for runner in present_runners:
        runner_text = read_file_content(os.path.join(root, runner)) or ""
        if "check_governance" in runner_text:
            wired = True
            break
    if wired:
        add_result(results, "pass", "scripts/check_governance.py: wired into a task runner")
    elif present_runners:
        add_result(results, "warn", f"scripts/check_governance.py: present but not referenced by {', '.join(present_runners)} — a checker nothing runs does not run")

    agents_text = read_file_content(os.path.join(root, "AGENTS.md")) or ""
    if "check_governance" in agents_text:
        add_result(results, "pass", "AGENTS.md: states the governance-checks maintenance obligation")
    else:
        add_result(results, "warn", "AGENTS.md: does not reference scripts/check_governance.py — the extend-the-checker obligation is unstated")


def validate_companion_consistency(data, ai_nav, results):
    if not data or not ai_nav:
        return
    up = data.get("update_rules", {})
    if isinstance(up, dict) and "governance_navigation" in up and "companion" in ai_nav.lower():
        add_result(results, "pass", "Companion consistency: update_rules and AI_NAVIGATION companion section present")
    elif isinstance(up, dict) and "governance_navigation" in up:
        add_result(results, "warn", "Companion consistency: update_rules present but AI_NAVIGATION companion section not found")
    else:
        add_result(results, "warn", "Companion consistency: governance_navigation update_rules missing")


def main():
    args = parse_args()
    root = os.path.abspath(args.project_root)
    if not os.path.isdir(root):
        print(f"ERROR: {root} is not a directory", file=sys.stderr)
        sys.exit(1)

    results = {"project_root": root, "passed": [], "warnings": [], "failures": []}

    # 1. Required governance files
    paths = {name: os.path.join(root, name) for name in REQUIRED_GOVERNANCE_FILES}
    for label, p in paths.items():
        ok, msg = check_file_exists(p, label, root)
        add_result(results, "pass" if ok else "fail", msg)

    # 2. CLAUDE.md check
    claude_path = os.path.join(root, "CLAUDE.md")
    if os.path.exists(claude_path):
        content = read_file_content(claude_path)
        if content and not content.strip().startswith("@AGENTS.md"):
            add_result(results, "warn", f"CLAUDE.md: not a thin wrapper to AGENTS.md (first line: {content.split(chr(10))[0]})")
        else:
            add_result(results, "pass", "CLAUDE.md: thin wrapper check passed")
    else:
        add_result(results, "pass", "CLAUDE.md: absent (optional)")

    # 3. Managed block integrity
    for label, p in paths.items():
        text = read_file_content(p)
        if text:
            # Skip CHANGELOG.md -- it contains text references to managed blocks
            # in changelog entries, not actual blocks
            if label == "CHANGELOG.md":
                continue
            check_managed_block_integrity(text, label, results, required_sections=["navigation"] if label in ["AI_NAVIGATION.md", "AGENTS.md"] else [])

    # 4. YAML validity + required keys
    yaml_path = os.path.join(root, "context-map.yaml")
    data = check_yaml(yaml_path, results, root)
    if data:
        validate_context_map(data, results)

    # 9. Generated-output policy + context recovery
    ai_nav = read_file_content(paths["AI_NAVIGATION.md"])
    validate_ai_navigation(ai_nav, results)

    # 10. Script/task governance
    validate_scripts_governance(root, data, results)

    # 11. Companion consistency
    validate_companion_consistency(data, ai_nav, results)

    # Determine verdict
    num_fail = len(results["failures"])
    num_warn = len(results["warnings"])
    num_pass = len(results["passed"])

    if num_fail == 0 and num_warn == 0:
        verdict = "PASS"
    elif num_fail == 0:
        verdict = "WARN"
    else:
        verdict = "FAIL"

    results["verdict"] = verdict

    # Print report
    print(f"Verdict: {verdict}")
    print(f"\nChecks passed ({num_pass}):")
    for msg in results["passed"]:
        print(f"  {green('✓')} {msg}")
    print(f"\nWarnings ({num_warn}):")
    for msg in results["warnings"]:
        print(f"  {yellow('!')} {msg}")
    print(f"\nFailures ({num_fail}):")
    for msg in results["failures"]:
        print(f"  {red('✗')} {msg}")

    if args.report_json:
        with open(args.report_json, "w") as f:
            json.dump(results, f, indent=2)
            f.write("\n")

    if num_fail > 0:
        sys.exit(1)
    elif num_warn > 0:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
