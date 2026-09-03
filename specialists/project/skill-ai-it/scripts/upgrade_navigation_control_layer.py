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
VERSION = "2026-08-11-governance-checks-layer-v1"

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

def build_navigation_block():
    """Build the managed AI_NAVIGATION.md navigation block content."""
    return f"""\
<!-- BEGIN MANAGED: skill-ai-it:navigation -->
<!-- skill-ai-it-version: {VERSION} -->

## Mandatory read order

Before answering, planning, editing, or creating files in this project, read in this order:

1. `AGENTS.md`
2. `AI_NAVIGATION.md`
3. `context-map.yaml`
4. `CHANGELOG.md`
5. Relevant `.archcore/` documents, if present
6. Relevant `memory-bank/` files, if present
7. Relevant project docs/code based on the task

If available, also consult:

- `graphify-out/GRAPH_REPORT.md`
- `.ai-context/governance-pack.md`

## Source priority

When sources conflict, use this priority:

1. `.archcore/` accepted ADRs, rules, specs, guides, and plans
2. `AGENTS.md` / `CLAUDE.md`
3. `AI_NAVIGATION.md`
4. `context-map.yaml`
5. `CHANGELOG.md`
6. `ARCHITECTURE.md` / `architecture.md`
7. `ROADMAP.md` / `roadmap.md`
8. `memory-bank/activeContext.md`
9. `memory-bank/progress.md`
10. `SCRATCHPAD.md` / `scratchpad.md`
11. old notes, drafts, archived files

`SCRATCHPAD.md` is temporary unless promoted into Archcore, roadmap, memory-bank, or explicitly marked `KEEP`.

## Project context files

| File / Path | Role | Authority |
|---|---|---|
| `AGENTS.md` | Universal agent instruction file | High |
| `CLAUDE.md` | Claude-specific bootstrap file | High |
| `AI_NAVIGATION.md` | Human-readable AI routing file | High |
| `context-map.yaml` | Machine-readable routing map | High |
| `CHANGELOG.md` | Durable project/governance change history | Medium-high |
| `.archcore/adr/` | Architecture decisions | Highest |
| `.archcore/rules/` | Durable project/agent rules | Highest |
| `.archcore/specs/` | Technical/design contracts | Highest |
| `.archcore/guides/` | Operational guides | High |
| `.archcore/plans/` | Approved implementation plans | High |
| `ARCHITECTURE.md` / `architecture.md` | Human-readable architecture overview | Medium-high |
| `ROADMAP.md` / `roadmap.md` | Human-readable roadmap | Medium-high |
| `memory-bank/activeContext.md` | Current working context | Medium |
| `memory-bank/progress.md` | Progress and current state | Medium |
| `memory-bank/decisionLog.md` | Decision notes before promotion | Medium |
| `SCRATCHPAD.md` / `scratchpad.md` | Temporary notes | Low |
| `scripts/check_governance.py` | Executable governance coherence checks — turns this project's claims into assertions | High |
| `docs/` | Supporting documentation | Depends on file |
| `graphify-out/` | Generated navigation graph | Generated support |
| `.ai-context/governance-pack.md` | Generated deterministic context pack | Generated support |

## Script and Task Navigation

For script, task, or automation questions, read in this order:

1. Existing canonical task runner if documented
2. `justfile`
3. `scripts/README.md`
4. `Taskfile.yml`
5. `Makefile`
6. `package.json`
7. Raw scripts under `scripts/` after inspection

Prefer `just --list` and `just <task>` when a `justfile` exists.

Do not run uncataloged scripts blindly. Treat uncataloged scripts as `unknown safety` until inspected.

If the catalog is stale, propose an update to `scripts/README.md` or the relevant task runner.

If a task is marked `destructive`, `review-required`, or `unknown`, stop and request review before execution.

## Governance coherence checks

If `scripts/check_governance.py` exists, run it before claiming any durable change is complete, and after any change that adds, moves, renames, or retires a file. It turns this project's governance
claims into assertions and exits non-zero on failure.

When it fails, fix the project — not the check. Broadening an ignore-list or exempting the failing file converts a real finding into a permanent blind spot.

The check count is a coverage signal, not a score, and is expected to rise as the project acquires structure. Adding a new class of artifact, a generated output, or a constant restated across files
requires extending the checker's registries in the same pass.

## Companion consistency

When changing governance files, update these companion files together:

| File | Companion files |
|---|---|
| `AGENTS.md` | `AI_NAVIGATION.md`, `context-map.yaml`, `scripts/README.md` |
| `AI_NAVIGATION.md` | `context-map.yaml` |
| `context-map.yaml` | `AI_NAVIGATION.md` |
| `scripts/README.md` | `AGENTS.md`, `context-map.yaml` |
| New script added | `scripts/README.md`, `AGENTS.md`, `justfile`, `scripts/check_governance.py` |
| New artifact class, generated output, or restated constant | `scripts/check_governance.py` registries |

## Generated context

Generated context files (`.ai-context/`, `graphify-out/`) are support-only if present.
Do not treat them as canonical truth.

Analysis outputs under `docs/reports/` are analysis records, not replacements for source references, source CSVs, database tables, or governed navigation files.

## Context compaction recovery

After context compaction, rebuild agent context in this order:

1. **Read `AI_NAVIGATION.md`** first — this file is the navigation map.
2. **Load `.archcore/`** — durable project truth (ADRs, rules, specs, guides, plans).
3. **Regenerate `graphify-out/`**: `graphify update .`
4. **Regenerate `.ai-context/`**: `repomix --config repomix.config.json`
5. **Verify `SCRATCHPAD.md`** — if empty, populate from memory-keeper / mcp-project-context.
6. **Verify `CHANGELOG.md`** is current.
7. **Verify `AI_NAVIGATION.md` and `context-map.yaml` companion consistency.**

Label recovered entries: `Context recovered via skill-ai-it context-recovery procedure`.

## Audit procedure

To verify project context coherence, run these checks:

1. Confirm `AGENTS.md` points to `AI_NAVIGATION.md`.
2. Confirm `AI_NAVIGATION.md` points to `context-map.yaml`.
3. Confirm `CHANGELOG.md` exists and recent governance/navigation changes are recorded.
4. Confirm `context-map.yaml` has routing for architecture, planning, governance, implementation, documentation, and scripts.
5. Confirm `.archcore/` is either present and routed, or absent and treated as optional.
6. Confirm generated context paths (`graphify-out/`, `.ai-context/`) are excluded from source-of-truth decisions.
7. Confirm `SCRATCHPAD.md` is marked transient.
8. Confirm repeat-run managed blocks exist where needed.
9. Confirm companion files in `update_rules` were updated when source files changed.
10. Confirm drift/conflict policy says stop-and-report.

<!-- END MANAGED: skill-ai-it:navigation -->"""


def build_agents_block():
    """Build managed AGENTS.md navigation block."""
    return f"""\
<!-- BEGIN MANAGED: skill-ai-it:navigation -->
<!-- skill-ai-it-version: {VERSION} -->

## AI navigation and context preflight

Before answering, planning, editing, or creating files in this project:

1. Read [AI_NAVIGATION.md](AI_NAVIGATION.md).
2. Read [context-map.yaml](context-map.yaml).
3. Read recent entries in [CHANGELOG.md](CHANGELOG.md).
4. Load relevant `.archcore/` context if present.
5. Load relevant `memory-bank/` files if present.
6. Consult generated context when available:
   - `graphify-out/GRAPH_REPORT.md`
   - `.ai-context/governance-pack.md`
7. Before making durable changes, inspect companion-file rules in `context-map.yaml update_rules`. Update all companion files when changing source files.
8. If sources conflict, stop and report the conflict instead of guessing.
9. Do not treat `SCRATCHPAD.md` as durable truth unless content is marked `KEEP` or promoted into `.archcore/`, ROADMAP, or memory-bank.
10. Do not treat Graphify (`graphify-out/`) or Repomix (`.ai-context/`) output as canonical truth. These are generated support artifacts only, always rebuildable.
11. Before running scripts or automation, inspect `justfile`, `scripts/README.md`, `Taskfile.yml`, `Makefile`, and `package.json` when present. Prefer `just --list` and `just <task>` when a `justfile` exists.
12. Treat uncataloged scripts as `unknown` safety until inspected.
13. When adding, modifying, or removing scripts or tasks, update `scripts/README.md` to reflect the change — purpose, inputs, outputs, safety label, and idempotency.
14. If `scripts/check_governance.py` exists, run it before claiming any durable change is complete. When it fails, fix the project, not the check. Adding a new artifact class, generated output, or a constant restated across files requires extending its registries in the same pass.
15. After making changes, update `CHANGELOG.md` for all durable governance/navigation changes.
16. Preserve user-authored content outside managed sections. Do not rewrite custom project notes.

<!-- END MANAGED: skill-ai-it:navigation -->"""


def build_scripts_block():
    """Build managed scripts/README.md block."""
    return f"""\
<!-- BEGIN MANAGED: skill-ai-it:scripts -->
<!-- skill-ai-it-version: {VERSION} -->

## Execution Policy

- Prefer the existing canonical task runner for this project.
- Prefer `just <task>` when a `justfile` is present.
- Do not run scripts marked `destructive`, `review-required`, or `unknown` without review.
- Do not assume arbitrary files under `scripts/` are safe.
- If a script is missing from this inventory, inspect it before use and update or propose an inventory entry.
- Secrets must not be documented here as values. Document only secret names and where they are expected to come from.

## Preferred Execution Order

1. Existing canonical task runner (whichever is established for this project)
2. `just --list` / `just <task>`
3. `scripts/README.md`
4. Other task runners: `Taskfile.yml`, `Makefile`, `package.json`
5. Raw scripts under `scripts/` after inspection

## Maintenance Rules

- Keep this file aligned with: `justfile`, `Taskfile.yml`, `Makefile`, `package.json`, actual files under `scripts/`
- Prefer managed block updates for generated sections.
- Preserve manually written notes unless explicitly replacing them.
- When removing a script, remove or mark its inventory entry stale.
- When adding a script, document purpose, inputs, outputs, safety, idempotency, and when to use it.

<!-- END MANAGED: skill-ai-it:scripts -->"""


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
