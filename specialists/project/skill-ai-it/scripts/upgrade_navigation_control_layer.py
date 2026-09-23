#!/usr/bin/env python3
"""Deterministic upgrade script for skill-ai-it navigation control layer.

Idempotently upgrades an existing project's AI navigation/control files
to the current managed-block schema with version stamping.

Usage:
    python scripts/upgrade_navigation_control_layer.py --project-root /path/to/project
    python scripts/upgrade_navigation_control_layer.py --project-root /path/to/project --dry-run
    python scripts/upgrade_navigation_control_layer.py --project-root /path/to/project --report-json /path/to/report.json
    python scripts/upgrade_navigation_control_layer.py --project-root /path/to/project --dry-run --repair-claude-wrapper
"""

import argparse
import json
import os
import sys
import re
from datetime import date

# Bumping this stamps re-emitted managed blocks and makes validate_navigation_control_layer.py flag projects still carrying the previous block content. Keep it identical to the VERSION constant
# in validate_navigation_control_layer.py — the two are a deliberate restatement, and drift between them silently disables the staleness signal.
VERSION = "2026-09-23-template-sourced-blocks-v1"

# Managed block constants
BEGIN_OLD = "<!-- BEGIN skill-ai-it:navigation -->"
END_OLD = "<!-- END skill-ai-it:navigation -->"
BEGIN_MANAGED = "<!-- BEGIN MANAGED: skill-ai-it:navigation -->"
END_MANAGED = "<!-- END MANAGED: skill-ai-it:navigation -->"
VERSION_LINE = f"<!-- skill-ai-it-version: {VERSION} -->"

# Provenance fingerprint — version-agnostic, so a block written by ANY release of this skill is
# recognised as skill-authored rather than being mistaken for project content.
VERSION_MARKER = "skill-ai-it-version:"

# Explicit, permanent opt-out. A project that has authored real content inside a managed block puts
# this anywhere in the block and the upgrader will never touch it again. The validator treats a
# block carrying it as correctly managed rather than as a missing/old-style-marker failure.
#     <!-- skill-ai-it:manual reason="project-authored routing rules" -->
MANUAL_TOKEN = "skill-ai-it:manual"

CHANGELOG_MARKER = f"<!-- skill-ai-it-upgrade: {VERSION} -->"

BEGIN_SCRIPTS_OLD = "<!-- BEGIN skill-ai-it:scripts -->"
END_SCRIPTS_OLD = "<!-- END skill-ai-it:scripts -->"
BEGIN_SCRIPTS_MANAGED = "<!-- BEGIN MANAGED: skill-ai-it:scripts -->"
END_SCRIPTS_MANAGED = "<!-- END MANAGED: skill-ai-it:scripts -->"


def parse_args():
    p = argparse.ArgumentParser(description="Upgrade navigation control layer")
    p.add_argument("--project-root", required=True, help="Path to project root")
    p.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    p.add_argument("--report-json", help="Write report JSON to file")
    p.add_argument("--repair-claude-wrapper", action="store_true",
                   help="Overwrite CLAUDE.md to fix wrapper if broken")
    p.add_argument("--force", action="store_true",
                   help="Replace managed blocks even when they look project-authored. This DISCARDS "
                        "whatever is currently in the block. Only use after reading the .proposed "
                        "file a normal run leaves behind.")
    return p.parse_args()


def report(args, data):
    print(f"Project root: {data['project_root']}")
    print(f"Version: {data['version']}")
    print(f"Dry run: {data['dry_run']}")
    if data["changed_files"]:
        print(f"Changed files: {', '.join(data['changed_files'])}")
    if data["skipped_files"]:
        print(f"Skipped files: {', '.join(data['skipped_files'])}")
    if data["proposed_files"]:
        print(f"Proposed files: {', '.join(data['proposed_files'])}")
    if data["warnings"]:
        for w in data["warnings"]:
            print(f"WARNING: {w}")
    if data.get("requires_manual_review"):
        print("REQUIRES MANUAL REVIEW")
    if args.report_json:
        with open(args.report_json, "w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")


# ---------------------------------------------------------------------------
# Upgrade helpers (additional utilities)
# ---------------------------------------------------------------------------

def relpath(path: str, root: str) -> str:
    """Return project-relative path for reports."""
    try:
        return os.path.relpath(path, root)
    except ValueError:
        return path


def load_yaml_module():
    """Load PyYAML with a clear error message."""
    try:
        import yaml
        return yaml
    except ImportError:
        print("ERROR: PyYAML is required. Install with: python -m pip install pyyaml", file=sys.stderr)
        sys.exit(1)


def count_managed_blocks(text: str, section_name: str) -> int:
    """Count current managed blocks for a section."""
    begin = f"<!-- BEGIN MANAGED: skill-ai-it:{section_name} -->"
    return text.count(begin)


def has_duplicate_managed_block(text: str, section_name: str) -> bool:
    return count_managed_blocks(text, section_name) > 1


def write_or_propose(path: str, root: str, text: str, dry_run: bool, report_data: dict, section_name: str | None = None) -> None:
    """Write text unless duplicate managed blocks require a .proposed file."""
    target = path
    proposed = False
    if section_name and has_duplicate_managed_block(text, section_name):
        target = f"{path}.proposed"
        proposed = True
        report_data["requires_manual_review"] = True
        report_data["warnings"].append(f"{relpath(path, root)}: duplicate managed blocks detected; wrote proposed file")
        report_data["proposed_files"].append(relpath(target, root))

    if dry_run:
        report_data["changed_files"].append(f"{relpath(target, root)} (would {'write proposed' if proposed else 'update'})")
        return

    with open(target, "w") as f:
        f.write(text)
    report_data["changed_files"].append(relpath(target, root))


def _block_body(text: str, begin: str, end: str) -> str | None:
    """The current contents between a block's markers, or None if absent."""
    m = re.search(re.escape(begin) + r"(.*?)" + re.escape(end), text, re.DOTALL)
    return m.group(1) if m else None


def block_is_replaceable(body: str | None) -> tuple[bool, str]:
    """May this block be overwritten? Returns (ok_to_replace, reason).

    THE DEFECT THIS EXISTS FOR (added 2026-08-12). `upsert_managed_block` replaced ANY block whose
    markers matched, unconditionally. That is correct only while the block still contains what this
    skill put there. Once a project authors real content inside one — which is the normal end state
    for a mature project, not an edge case — the "upgrade" is a silent, lossy overwrite.

    Found on the jdm project: a dry run against a scratch copy would have removed 222 lines from
    AI_NAVIGATION.md (every supersession chain, every gate reference, the whole domain-routing
    table) and dropped three load-bearing rules from AGENTS.md. Nothing warned; the status line
    said `replaced-old-block`, which reads like a successful migration.

    Two gates, cheapest first:

    1. An explicit opt-out token anywhere in the block. A project that has deliberately taken
       ownership says so, and this skill leaves it alone forever.
    2. Provenance. A block this skill wrote carries a `skill-ai-it-version:` line as its first inner
       comment — that is the managed-block contract in SKILL.md. A block WITHOUT one was either
       never written by the skill or has been hand-edited since. Either way its contents are not
       ours to discard, so we write a .proposed file and leave the original alone.

    Deliberately conservative: it can only ever refuse to overwrite. The failure mode of a false
    positive is a .proposed file nobody wanted; the failure mode of a false negative is the 222
    lines.
    """
    if body is None:
        return True, "no-existing-block"
    if MANUAL_TOKEN in body:
        return False, "manual"
    if VERSION_MARKER not in body:
        return False, "no-provenance"
    return True, "skill-authored"


def upsert_managed_block(
    text: str,
    section_name: str,
    new_block: str,
    old_begin: str | None = None,
    old_end: str | None = None,
    insert_after_heading: str | None = None,
    insert_after_pattern: str | None = None,
    force: bool = False,
) -> tuple[str, bool, str]:
    """Insert or replace a skill-ai-it managed block idempotently.

    Never replaces a block that carries the manual opt-out token or that lacks this skill's own
    version marker — see `block_is_replaceable`. Pass force=True (CLI `--force`) to override, which
    is an explicit decision to discard whatever is currently in the block.
    """
    current_begin = f"<!-- BEGIN MANAGED: skill-ai-it:{section_name} -->"
    current_end = f"<!-- END MANAGED: skill-ai-it:{section_name} -->"

    # Provenance is checked against whichever marker pair is actually present, and BEFORE any
    # substitution — the old-marker branch below is the one that caused the jdm near-miss, because
    # it is tested first and matches preferentially.
    present = False
    for begin, end in ((old_begin, old_end), (current_begin, current_end)):
        if not (begin and end and begin in text and end in text):
            continue
        present = True
        ok, reason = block_is_replaceable(_block_body(text, begin, end))
        if not ok and not force:
            return text, False, f"refused-{reason}"
        break

    # The opt-out also suppresses INSERTION. A file that declares itself project-managed and simply
    # does not have this section has decided it does not want it — inserting the generic block
    # anyway is the same disregard for the project's intent as overwriting one, just additive
    # instead of lossy. jdm's scripts/README.md is the case: it deliberately carries a `task-safety`
    # block instead of the generic `scripts` one.
    if not present and MANUAL_TOKEN in text and not force:
        return text, False, "refused-manual"

    if old_begin and old_end and old_begin in text and old_end in text:
        pattern = re.compile(re.escape(old_begin) + r".*?" + re.escape(old_end), re.DOTALL)
        updated, n = pattern.subn(new_block.rstrip(), text, count=1)
        return updated, n > 0 and updated != text, "replaced-old-block"

    if current_begin in text and current_end in text:
        pattern = re.compile(re.escape(current_begin) + r".*?" + re.escape(current_end), re.DOTALL)
        updated, n = pattern.subn(new_block.rstrip(), text, count=1)
        return updated, n > 0 and updated != text, "replaced-managed-block" if updated != text else "unchanged"

    block = new_block.rstrip()

    if insert_after_pattern:
        match = re.search(insert_after_pattern, text, re.MULTILINE | re.DOTALL)
        if match:
            insert_at = match.end()
            updated = text[:insert_at].rstrip() + "\n\n" + block + "\n\n" + text[insert_at:].lstrip()
            return updated, True, "inserted-managed-block"

    if insert_after_heading and insert_after_heading in text:
        idx = text.find(insert_after_heading) + len(insert_after_heading)
        updated = text[:idx].rstrip() + "\n\n" + block + "\n\n" + text[idx:].lstrip()
        return updated, True, "inserted-managed-block"

    h1 = re.search(r"^# .*$", text, re.MULTILINE)
    if h1:
        insert_at = h1.end()
        updated = text[:insert_at].rstrip() + "\n\n" + block + "\n\n" + text[insert_at:].lstrip()
        return updated, True, "inserted-managed-block"

    updated = block + "\n\n" + text.lstrip()
    return updated, True, "inserted-managed-block"


def merge_governance_update_rules(data: dict) -> bool:
    """Merge default governance_navigation update rules without overwriting custom rules."""
    defaults = get_context_map_keys()["update_rules"]["governance_navigation"]
    changed = False

    update_rules = data.setdefault("update_rules", {})
    if not isinstance(update_rules, dict):
        data["update_rules"] = {}
        update_rules = data["update_rules"]
        changed = True

    gov = update_rules.setdefault("governance_navigation", {})
    if not isinstance(gov, dict):
        update_rules["governance_navigation"] = {}
        gov = update_rules["governance_navigation"]
        changed = True

    for key, value in defaults.items():
        if key not in gov:
            gov[key] = value
            changed = True
        elif isinstance(gov[key], dict) and isinstance(value, dict):
            existing_companions = gov[key].setdefault("companions", [])
            if not isinstance(existing_companions, list):
                gov[key]["companions"] = []
                existing_companions = gov[key]["companions"]
                changed = True
            for companion in value.get("companions", []):
                if companion not in existing_companions:
                    existing_companions.append(companion)
                    changed = True

    return changed


# ---------------------------------------------------------------------------
# Upgrade helpers
# ---------------------------------------------------------------------------

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates")

NAVIGATION_TEMPLATE = os.path.join(TEMPLATES_DIR, "AI_NAVIGATION.md")
AGENTS_BLOCK_TEMPLATE = os.path.join(TEMPLATES_DIR, "AGENTS-navigation-block.md")
SCRIPTS_TEMPLATE = os.path.join(TEMPLATES_DIR, "scripts-README.md")


def _read_template(path: str) -> str:
    """Read a template file, or fail loudly.

    There is deliberately NO embedded fallback copy of any block. An embedded copy is a second source
    of truth, and a second source of truth drifts silently: on 2026-09-23 this script's inlined
    navigation block had fallen nine sections behind `templates/AI_NAVIGATION.md`, so a project
    bootstrapped from the template and then upgraded by this script LOST task routing, drift
    handling, update rules and the answer contract — reported only as `replaced-managed-block`,
    which reads like a successful migration. A missing template is a broken install; say so and stop.
    """
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError as exc:
        raise SystemExit(
            f"skill-ai-it: cannot read required template {path}: {exc}\n"
            "The managed blocks are generated FROM the templates in this skill package. "
            "Restore the package's templates/ directory before running the upgrade."
        )


def _extract_block(text: str, begin: str, end: str, source: str) -> str:
    """Return the body BETWEEN a template's managed markers, markers excluded."""
    start = text.find(begin)
    stop = text.find(end, start + 1) if start != -1 else -1
    if start == -1 or stop == -1:
        raise SystemExit(
            f"skill-ai-it: template {source} is missing its managed markers "
            f"({begin} ... {end}). The template is the source of truth for this block; repair it."
        )
    body = text[start + len(begin):stop]
    # The template's own version marker is not authoritative — VERSION in this script is. Drop any
    # marker comment the template carries (the wrap hook may have folded it onto the BEGIN line).
    body = re.sub(r"<!--\s*skill-ai-it-version:[^>]*-->", "", body)
    # Stripping a folded version marker leaves a trailing space and a blank run behind it, which the
    # target project's markdown lint then reports against a block it is not allowed to hand-edit.
    body = "\n".join(line.rstrip() for line in body.split("\n"))
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body.strip("\n")


def _managed(body: str, begin: str, end: str) -> str:
    """Wrap a block body in canonical markers with the current VERSION."""
    return f"{begin}\n<!-- skill-ai-it-version: {VERSION} -->\n\n{body}\n\n{end}"


def build_navigation_block():
    """Build the managed AI_NAVIGATION.md block from templates/AI_NAVIGATION.md."""
    body = _extract_block(
        _read_template(NAVIGATION_TEMPLATE), BEGIN_MANAGED, END_MANAGED, "AI_NAVIGATION.md"
    )
    return _managed(body, BEGIN_MANAGED, END_MANAGED)


def build_agents_block():
    """Build the managed AGENTS.md navigation block from templates/AGENTS-navigation-block.md.

    That template IS the block — markers included — so it is read whole rather than sliced.
    """
    text = _read_template(AGENTS_BLOCK_TEMPLATE)
    body = _extract_block(text, BEGIN_MANAGED, END_MANAGED, "AGENTS-navigation-block.md")
    return _managed(body, BEGIN_MANAGED, END_MANAGED)


def build_scripts_block():
    """Build the managed scripts/README.md block from templates/scripts-README.md.

    Only Execution Policy / Preferred Execution Order / Maintenance Rules live inside the markers.
    Runtimes, inventories, safety labels and notes sit OUTSIDE them in the template, because this
    function regenerates everything between the markers and would otherwise discard them.
    """
    body = _extract_block(
        _read_template(SCRIPTS_TEMPLATE), BEGIN_SCRIPTS_MANAGED, END_SCRIPTS_MANAGED, "scripts-README.md"
    )
    return _managed(body, BEGIN_SCRIPTS_MANAGED, END_SCRIPTS_MANAGED)


def get_context_map_keys():
    """Return default context-map.yaml top-level keys."""
    return {
        "version": 1,
        "skill_ai_it_version": VERSION,
        "project": {"name": "{{PROJECT_SLUG}}", "context_policy": "AI_NAVIGATION.md is the human-readable router; this file is the machine-readable routing map."},
        "bootstrap": {"required_first_read": ["AGENTS.md", "AI_NAVIGATION.md", "context-map.yaml", "CHANGELOG.md"]},
        "audit_checks": {
            "governance_file_presence": ["README.md", "AGENTS.md", "CLAUDE.md", "AI_NAVIGATION.md", "context-map.yaml", "CHANGELOG.md"],
            "version_consistency": {"description": "Verify managed block version strings match current skill version.", "action": "report_mismatch"},
            "companion_update_completeness": {"description": "Verify companion files in update_rules were updated together.", "action": "report_missing"},
            "generated_output_policy": {"description": "Verify Graphify and Repomix outputs are classified as generated support.", "action": "report_violation"},
            "task_runner_consistency": {"description": "Verify cataloged tasks match actual script files.", "action": "report_drift"},
            "no_stale_references": {"description": "Detect references to removed tools or superseded governance assumptions.", "action": "report_stale"},
        },
        "promotion_rules": {
            "archcore": {
                "allowed_init_modes": ["bootstrap", "navigation-add", "refresh"],
                "content_write_modes": ["promote"],
                "required_authorization": True,
                "candidates_report": "ARCHCORE_PROMOTION_CANDIDATES.md",
                "extract_heuristics_source": "patterns/archcore-routing.md",
                "exclusion": ["CHANGELOG.md (history only)", "generated files (.ai-context/, graphify-out/)", "unmarked SCRATCHPAD sections", "draft/obsolete roadmap items"],
            }
        },
        "context_recovery": {
            "procedure": [
                "Read AI_NAVIGATION.md first for navigation map.",
                "Load .archcore/ context if present (durable truth).",
                "Regenerate graphify-out/ with: graphify update .",
                "Regenerate .ai-context/ with: repomix --config repomix.config.json",
                "Verify SCRATCHPAD.md has current state. If empty, populate from memory-keeper / mcp-project-context.",
                "Verify CHANGELOG.md is current.",
                "Verify AI_NAVIGATION.md and context-map.yaml companion consistency.",
            ],
            "evidence_label": f"Context recovered at <timestamp> via skill-ai-it context-recovery procedure.",
        },
        "update_rules": {
            "governance_navigation": {
                "AGENTS.md": {"companions": ["AI_NAVIGATION.md", "context-map.yaml", "scripts/README.md"]},
                "AI_NAVIGATION.md": {"companions": ["context-map.yaml"]},
                "context-map.yaml": {"companions": ["AI_NAVIGATION.md"]},
                "scripts/README.md": {"companions": ["AGENTS.md", "context-map.yaml"]},
                "new_script_added": {"companions": ["scripts/README.md", "AGENTS.md", "justfile"]},
            },
        },
    }


# ---------------------------------------------------------------------------
# File upgrade functions
# ---------------------------------------------------------------------------

def handle_block_result(path, root, updated, changed, action, block, dry_run, report_data, section):
    """Common post-processing for an upsert, including the refusal path.

    A refusal must be LOUD. Landing it in `skipped_files` would make "I did not touch your
    project-authored content" indistinguishable from "nothing needed doing", and the whole point of
    the guard is that the operator finds out the generic block was withheld and why.
    """
    if action.startswith("refused-"):
        # Two different situations, and telling a project that has ALREADY opted out to "add the
        # opt-out token" is the kind of instruction that teaches people the tool is not paying
        # attention. Keep the advice specific to which gate fired.
        if action == "refused-manual":
            reason = ("carries the skill-ai-it:manual opt-out token — project-owned, and this "
                      "skill will never auto-replace it")
            advice = ("Nothing to do; this is the declared state. The .proposed file is there only "
                      "if you ever want to see what the generic block would have said.")
            # An intentional opt-out is not an exception needing review — saying so every run is
            # how a review flag stops meaning anything.
            needs_review = False
        else:
            reason = ("has no skill-ai-it-version: marker, so it was either never written by this "
                      "skill or has been hand-edited since. Its contents are not ours to discard")
            advice = ("Merge the .proposed block by hand if you want it, or add "
                      "`<!-- skill-ai-it:manual reason=\"...\" -->` inside the block to declare it "
                      "project-owned and silence this permanently.")
            needs_review = True

        if needs_review:
            report_data["requires_manual_review"] = True
        report_data["warnings"].append(
            f"{relpath(path, root)}: REFUSED to replace the '{section}' block — {reason}. {advice}"
        )
        proposed = f"{path}.proposed-{section}-block"
        if dry_run:
            report_data["changed_files"].append(f"{relpath(proposed, root)} (would write proposed block)")
        else:
            with open(proposed, "w") as f:
                f.write(block.rstrip() + "\n")
            report_data["proposed_files"].append(relpath(proposed, root))
        return

    if changed:
        write_or_propose(path, root, updated, dry_run, report_data, section)
        report_data["warnings"].append(f"{relpath(path, root)}: {action}")
    else:
        report_data["skipped_files"].append(relpath(path, root))


def upgrade_ai_navigation(path, dry_run, report_data):
    """Upgrade AI_NAVIGATION.md managed block."""
    root = report_data["project_root"]
    block = build_navigation_block()

    if not os.path.exists(path):
        text = f"# AI Navigation — {os.path.basename(root)}\n\nPurpose: this file is the project context entrypoint for AI agents.\n\n{block}\n"
        write_or_propose(path, root, text, dry_run, report_data, "navigation")
        return

    with open(path) as f:
        text = f.read()

    updated, changed, action = upsert_managed_block(
        text,
        "navigation",
        block,
        old_begin=BEGIN_OLD,
        old_end=END_OLD,
        insert_after_pattern=r"This file is a router[^\n]*\.\s*",
        force=report_data.get("force", False),
    )

    handle_block_result(path, root, updated, changed, action, block, dry_run, report_data, "navigation")


def upgrade_context_map_yaml(path, dry_run, report_data):
    """Upgrade context-map.yaml with missing top-level keys."""
    root = report_data["project_root"]
    yaml = load_yaml_module()

    if not os.path.exists(path):
        data = get_context_map_keys()
        data["project"]["name"] = os.path.basename(root)
        text = yaml.dump(data, default_flow_style=False, sort_keys=False)
        if dry_run:
            report_data["changed_files"].append(f"{relpath(path, root)} (would create)")
        else:
            with open(path, "w") as f:
                f.write(text)
            report_data["changed_files"].append(relpath(path, root))
        return

    try:
        with open(path) as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        proposed = f"{path}.proposed"
        report_data["warnings"].append(f"{relpath(path, root)}: YAML parse error: {e}")
        report_data["proposed_files"].append(relpath(proposed, root))
        report_data["requires_manual_review"] = True
        if not dry_run:
            defaults = get_context_map_keys()
            with open(proposed, "w") as f:
                yaml.dump(defaults, f, default_flow_style=False, sort_keys=False)
            report_data["changed_files"].append(relpath(proposed, root))
        return

    if not isinstance(data, dict):
        report_data["warnings"].append(f"{relpath(path, root)}: not a dict; skipping")
        report_data["requires_manual_review"] = True
        return

    defaults = get_context_map_keys()
    added = []

    if data.get("skill_ai_it_version") != VERSION:
        data["skill_ai_it_version"] = VERSION
        added.append("skill_ai_it_version")

    for key in ["audit_checks", "promotion_rules", "context_recovery"]:
        if key not in data:
            data[key] = defaults[key]
            added.append(key)

    if merge_governance_update_rules(data):
        added.append("update_rules")

    if not added:
        report_data["skipped_files"].append(relpath(path, root))
        return

    if dry_run:
        report_data["changed_files"].append(f"{relpath(path, root)} (would add/update: {', '.join(sorted(set(added)))})")
        return

    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    report_data["changed_files"].append(relpath(path, root))


def upgrade_agents_md(path, dry_run, report_data):
    """Upgrade AGENTS.md managed block."""
    root = report_data["project_root"]
    block = build_agents_block()

    if not os.path.exists(path):
        text = "Title: Agent Policy\nCategory: agent-governance-guide\nStatus: current\n\n# AGENTS.md\n\n" + block + "\n"
        write_or_propose(path, root, text, dry_run, report_data, "navigation")
        return

    with open(path) as f:
        text = f.read()

    updated, changed, action = upsert_managed_block(
        text,
        "navigation",
        block,
        old_begin=BEGIN_OLD,
        old_end=END_OLD,
        insert_after_heading="# AGENTS.md",
        force=report_data.get("force", False),
    )

    handle_block_result(path, root, updated, changed, action, block, dry_run, report_data, "navigation")


def upgrade_claude_md(path, dry_run, report_data, repair=False):
    """Check CLAUDE.md is a thin wrapper."""
    root = report_data["project_root"]
    expected = "@AGENTS.md"
    if not os.path.exists(path):
        report_data["skipped_files"].append(relpath(path, root))
        return

    with open(path) as f:
        first_line = f.readline().strip()

    if first_line == expected:
        report_data["skipped_files"].append(relpath(path, root))
        return

    report_data["warnings"].append(f"{relpath(path, root)}: not a thin wrapper (expected '{expected}', got '{first_line}')")
    if repair:
        if dry_run:
            report_data["changed_files"].append(f"{relpath(path, root)} (would repair wrapper)")
        else:
            with open(path, "w") as f:
                f.write(f"{expected}\n")
            report_data["changed_files"].append(relpath(path, root))


def upgrade_scripts_readme(scripts_dir, path, dry_run, report_data):
    """Ensure scripts/README.md has managed block when scripts/ exists."""
    root = report_data["project_root"]
    if not os.path.isdir(scripts_dir):
        report_data["skipped_files"].append(f"{relpath(path, root)} (scripts/ absent)")
        return

    block = build_scripts_block()

    if not os.path.exists(path):
        text = "# Script Inventory\n\nThis file describes runnable scripts, task runners, and automation entrypoints.\n\n" + block + "\n"
        write_or_propose(path, root, text, dry_run, report_data, "scripts")
        return

    with open(path) as f:
        text = f.read()

    updated, changed, action = upsert_managed_block(
        text,
        "scripts",
        block,
        old_begin=BEGIN_SCRIPTS_OLD,
        old_end=END_SCRIPTS_OLD,
        insert_after_pattern=r"^# .*$",
        force=report_data.get("force", False),
    )

    handle_block_result(path, root, updated, changed, action, block, dry_run, report_data, "scripts")


def append_changelog(path, dry_run, report_data, upgrades_text):
    """Append an idempotent changelog entry."""
    root = report_data["project_root"]
    if not os.path.exists(path):
        report_data["skipped_files"].append(relpath(path, root))
        return

    with open(path) as f:
        text = f.read()

    if CHANGELOG_MARKER in text:
        report_data["skipped_files"].append(relpath(path, root))
        return

    entry = f"""
## {date.today().isoformat()} — deterministic navigation-control upgrade

{CHANGELOG_MARKER}

- Applied `skill-ai-it` deterministic navigation-control upgrade.
- Upgraded managed navigation/scripts blocks to version `{VERSION}`.
- Ensured `context-map.yaml` contains `skill_ai_it_version`, `audit_checks`, `promotion_rules`, `context_recovery`, and `update_rules`.
- Preserved user-authored content outside managed blocks.
- Generated outputs remain support-only; no `.archcore/` promotion was performed.

{upgrades_text}
"""

    if dry_run:
        report_data["changed_files"].append(f"{relpath(path, root)} (would append changelog entry)")
        return

    with open(path, "a") as f:
        f.write(entry)
    report_data["changed_files"].append(relpath(path, root))


def main():
    args = parse_args()
    root = os.path.abspath(args.project_root)
    if not os.path.isdir(root):
        print(f"ERROR: {root} is not a directory", file=sys.stderr)
        sys.exit(1)

    dry_run = args.dry_run

    report_data = {
        "project_root": root,
        "version": VERSION,
        "dry_run": dry_run,
        "changed_files": [],
        "skipped_files": [],
        "proposed_files": [],
        "warnings": [],
        "requires_manual_review": False,
        "force": getattr(args, "force", False),
    }

    # Process files
    upgrade_ai_navigation(os.path.join(root, "AI_NAVIGATION.md"), dry_run, report_data)
    upgrade_context_map_yaml(os.path.join(root, "context-map.yaml"), dry_run, report_data)
    upgrade_agents_md(os.path.join(root, "AGENTS.md"), dry_run, report_data)
    upgrade_claude_md(os.path.join(root, "CLAUDE.md"), dry_run, report_data, args.repair_claude_wrapper)
    upgrade_scripts_readme(os.path.join(root, "scripts"), os.path.join(root, "scripts/README.md"), dry_run, report_data)

    # Build upgrade summary for changelog from non-changelog changes only.
    non_changelog_changes = [
        item for item in report_data["changed_files"]
        if not item.startswith("CHANGELOG.md")
    ]
    upgrades_text = f"Applied to: {', '.join(non_changelog_changes) if non_changelog_changes else 'none'}"

    if non_changelog_changes:
        append_changelog(os.path.join(root, "CHANGELOG.md"), dry_run, report_data, upgrades_text)

    # Print report
    report(args, report_data)

    # Exit code
    final_changed = bool(report_data["changed_files"])
    if report_data.get("requires_manual_review"):
        sys.exit(3)
    elif final_changed:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
