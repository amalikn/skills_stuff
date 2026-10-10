"""This project's governance data: roots, registries, path policy and exemptions with their reasons. No checks here; checks read it."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

#: The checker's own files, excluded from the scans that would otherwise report its own pattern definitions (the split of
#: 2026-10-10 turned one file into a package).
SELF_FILES = frozenset({"scripts/check_governance.py", *(p.relative_to(ROOT).as_posix() for p in (ROOT / "scripts/govcheck").rglob("*.py"))})

# Governance surfaces whose path references must resolve.
SURFACES: tuple[str, ...] = (
    "README.md",
    "AGENTS.md",
    "SCRATCHPAD.md",
    "CHANGELOG.md",
    "MEMORY.md",
    "AI_NAVIGATION.md",
    "RUNTIME.md",
    "SKILL_STANDARD.md",
    "REVISION_NOTES.md",
    "ROUTING_EVALS.md",
    "ARCHITECTURE.md",
)

# Index file -> (folder it indexes, glob). Enforces BOTH directions: links resolve, and members are linked.
CATALOGS: dict[str, tuple[str, str]] = {
    "scripts/README.md": ("scripts", "*.py"),
    # The durable-truth index. `**/*.md` is deliberate: .archcore/ documents live in adr/rules/specs/guides/plans subfolders, and a non-recursive glob would
    # report full coverage while checking nothing. Points at the INDEX rather than at the candidate queue, which /skill-ai-it promote deletes by contract.
    ".archcore/README.md": (".archcore", "**/*.md"),
    # Working documents — audits, proposals, classifications, evaluation records. Registered when the root was cleared of them on 2026-09-02: the root now
    # carries governance and contract entrypoints only, and an unindexed document in docs/ would otherwise be invisible to every reader and every check.
    # `**/*.md` since 2026-09-04: docs/ grew subfolders (audits/, routing-evaluation/, reliability-adaptation/, off-topic/) once the flat list passed a dozen
    # files, and a non-recursive glob would report full coverage while checking nothing inside them — the same reasoning already applied to .archcore/ above.
    "docs/README.md": ("docs", "**/*.md"),
    # The persona library. Registered 20260903 after the inverse sweep found personas/ was the one library layer with no index at all — 15 documents and no way
    # in, while skills/ and .archcore/ both had one. Coverage now fails until a new persona is linked here, which is the intended workflow rather than an error.
    "personas/README.md": ("personas", "*.md"),
}

# Files a catalog may legitimately omit (the index itself, generated output, dotfiles).
CATALOG_EXEMPT: frozenset[str] = frozenset({"README.md", "__init__.py"})

# Countable noun -> (folder, glob). A prose claim like "26 documents" is checked against the real count. Choose the glob deliberately: "*.md" counts the
# folder's own index too, which is usually not what the prose means — prefer "[0-9]*.md" or a similar shape when the index is excluded from the claim.
# "personas" is countable as files; skill PACKAGES are directories, so members() cannot see them — that count is asserted against the manifest in
# check_library_counts() instead.
COUNT_CLAIMS: dict[str, tuple[str, str]] = {
    # "[a-z]*-*.md" excludes README.md: the index is not a persona, and counting it made every "15 personas" claim in the project read as wrong
    # the moment the index was created. The registry comment above says to choose this glob deliberately; this is that case.
    "personas": ("personas", "[a-z]*-*.md"),
}

# Lines carrying this marker state a historical fact, not a live claim, and are exempt from count checking.
ASAT_MARKER = "count:asat"

# Lines carrying this marker show an ILLUSTRATIVE filename — a naming-convention example — not a reference to a file that must exist. Same shape as ASAT_MARKER:
# explicit, per line, and visible in the document itself rather than hidden in an ignore-list here.
EXAMPLE_MARKER = "path:example"

# Paths a governance surface references CONDITIONALLY ("when present"). The generic skill-ai-it navigation block names several; each is a real artifact in SOME
# governed project, so its absence here is a fact about this project's toolchain rather than a broken reference. Registered with a per-entry reason rather than
# silently ignore-listed, so the exemption stays reviewable — remove an entry the day the artifact appears. Tune per project.
CONDITIONAL_PATHS: frozenset[str] = frozenset({
    "Taskfile.yml",                    # this project uses just, not Task
    "Makefile",                        # no make-based entrypoint
    "package.json",                    # no Node toolchain in the maintenance runtime
    "graphify-out/GRAPH_REPORT.md",    # generated; absent until the graph task has run
    "graphify-out/graph.json",
    ".ai-context/governance-pack.md",  # generated; absent until `just context-pack` has run
    ".ai-context/repo-pack.md",
    "memory-bank/activeContext.md",    # this project uses SCRATCHPAD.md, not a memory-bank
    "memory-bank/progress.md",
    "memory-bank/decisionLog.md",
    "translation-brief.md",            # emitted by a sync run into the working cache, not committed here
    # RETIRED 20260903 when upstream sync was removed. Registered rather than unbackticked because a changelog recording a removal must be able to NAME what it
    # removed, and the .archcore records superseded in place still describe how these worked. Same reasoning that put ARCHCORE_PROMOTION_CANDIDATES.md here.
    "scripts/sync_auto_company.py",
    "upstream-state.json",
    "translation-memory.json",
    "translation-policy.md",
    "tests/test_sync_auto_company.py",
    # Paths that are real, and deliberately NOT inside this repo. Registered with a reason rather than ignore-listed so the exemption stays reviewable.
    ".agents/skills",                              # consumer-side discovery path created by install_global.py
    "skills-working-cache/agent-stack/update-reports",  # sync reports land in the working-cache peer, never in source
    "MaxMiksa/Auto-Company",                       # upstream GitHub repo slug, not a path in this tree
    # Transient by design: it is a proposal queue that `/skill-ai-it promote` deletes once its candidates become .archcore/ documents. Registered so
    # CHANGELOG.md's historical mention of it does not fail path resolution after the file is gone — history is not a live claim. The durable index after
    # promotion is .archcore/README.md.
    "ARCHCORE_PROMOTION_CANDIDATES.md",
})

# Task runner file, or None if the project has none.
TASK_RUNNER: str | None = "justfile"

# Files whose prose names task-runner recipes.
RUNNER_REFERENCES: tuple[str, ...] = (
    "README.md",
    "AGENTS.md",
    "AI_NAVIGATION.md",
    "RUNTIME.md",
    "SKILL_STANDARD.md",
    "scripts/README.md",
)

# Generated artifact -> inputs it must not be older than.
DERIVED: dict[str, tuple[str, ...]] = {
    # "docs/CLASS-PROFILES.md": ("scripts/class_profiles.py", "process/vehicle-classes.yaml"),
}

# Facts deliberately restated across surfaces. Each entry: the regex that recognises a statement of the fact, and every file allowed to state it. Drift fails;
# so does an UNREGISTERED file stating it — that is what makes this self-extending. Pair each entry with a spec document explaining why the duplication is
# intentional.
CONSTANT_SURFACES: dict[str, dict[str, object]] = {
    # "profit-gate": { "pattern": r"\$2,500", "surfaces": ("AGENTS.md", "docs/07-DECISIONS.md"), "owner": ".archcore/rules/purchase-discipline.rule.md", },
}

# Append-only tables and the columns that give them their grain: (entity column, pass column). An append-only table records a re-measurement by ADDING a row,
# which is right and useless on its own — without a column that orders the passes there is no way to compute which row is current, and every aggregate over the
# table double-counts whatever was re-measured. Found in a governed project on 2026-08-28 with twelve rows standing for eight entities, the supersession
# recorded only in a prose note. Register the table here and the grain becomes an assertion instead of an intention.
APPEND_ONLY_TABLES: dict[str, tuple[str, str]] = {
    # "data/sku-scores.csv": ("sku_id", "scored_at"),
}

# YAML surfaces whose key stream is checked for duplicates. A duplicate key parses fine and silently discards a block, so well-formedness cannot catch it.
YAML_SURFACES: tuple[str, ...] = ("context-map.yaml", "manifest.yaml")

# Tracked JSONL evidence: append-only files written by one script and read by another. A malformed or under-populated line does not raise anywhere — the writer
# has already exited and the reader skips what it cannot parse — so evidence goes missing with no error. Maps each file to the keys every line must carry.
JSONL_EVIDENCE: dict[str, tuple[str, ...]] = {
    "evals/field-log.jsonl": ("ts", "task", "project", "owner", "followed"),
    "evals/capability-gaps.jsonl": ("at", "kind", "persona", "text"),
}

# Folder of dated evidence captures, or None if the project keeps none. A capture asserts what a source said on a date.
EVIDENCE_DIR: str | None = None  # e.g. "trackers/source-captures"

# The index file inside EVIDENCE_DIR, exempt from the provenance header because it is a catalog, not a capture.
EVIDENCE_INDEX = "README.md"

# Header fields that make a capture re-openable by someone who was not there: where it came from, when, and whether the fetch actually succeeded. A capture
# naming no URL and no HTTP status is a recollection in a capture's clothing — in the project this was promoted from, exactly that produced a VERIFIED cost row
# whose only recorded fetch returned 403.
EVIDENCE_PROVENANCE_FIELDS: tuple[str, ...] = ("Canonical URL", "Retrieved", "HTTP status")

# Captures taken before the provenance rule existed. Each MUST name the later capture supplying the missing provenance — this is a correction record, not an
# exemption. Where captures are immutable the only way to clear an entry is to take the correcting capture, which is the behaviour the rule wants. Removing an
# entry whose correction does not exist turns the check red rather than quiet, so the list cannot be emptied by deletion.
EVIDENCE_PROVENANCE_CORRECTED: dict[str, str] = {
    # "uae-wholesale-moq-discounts-20260828.md": "wholesale-house-price-provenance-20260828.md",
}

# Extensions scanned when hunting for unregistered restatements of a constant.
SCAN_SUFFIXES: frozenset[str] = frozenset({".md", ".py", ".yaml", ".yml"})

# Path-token discrimination. Prose is full of tokens that look like paths and are not; tune until the check is quiet.
PATHLIKE = re.compile(r"^[A-Za-z0-9._/-]+$")

REPO_SUFFIXES: frozenset[str] = frozenset({".md", ".py", ".json", ".yaml", ".yml", ".toml", ".sh", ".txt"})

IGNORE_PREFIXES: tuple[str, ...] = ("http://", "https://", "mailto:", "~/", "/")

# "SKILL.md" joins the generic filenames: SKILL_STANDARD.md discusses the shape every skill's SKILL.md must have, which is a convention, not a reference to one
# file at the repo root.
IGNORE_EXACT: frozenset[str] = frozenset(
    {"README.md", "AGENTS.md", "CLAUDE.md", "SCRATCHPAD.md", "CHANGELOG.md", "SKILL.md"}
)

# Manifest capability rows have a fixed inline-mapping shape, so they are read with a regex rather than PyYAML. This is deliberate: the governance gate is
# stdlib-only by doctrine ("a check that cannot run is indistinguishable from a check that passes"), and this project has already been bitten by exactly that —
# the skill-contract test failed on a missing PyYAML on 2026-09-01 because it had been supplied invisibly by the host interpreter. The richer YAML-aware
# validation lives in scripts/validate_agent_stack.py, which runs in the bootstrapped venv and may import yaml freely.
CAPABILITY_ROW = re.compile(
    r"^\s*-\s*\{id:\s*(?P<id>[^,]+),\s*kind:\s*(?P<kind>[^,]+),\s*path:\s*(?P<path>[^,]+),", re.MULTILINE
)

# The checker's own shape (skill-ai-it patterns/governance-checks.md, "Structure and growth"), policed by checks/structure.py.
CHECKER_PACKAGE = "scripts/govcheck"
MODULE_MAX_LINES = 400
CHECK_MAX_LINES = 60
#: Checks over CHECK_MAX_LINES when the standard was adopted, with their size then: a ratchet; they may shrink, never grow. None at adoption.
OVERSIZE: dict[str, int] = {}
CORE_TEMPLATE = "/Volumes/Data/_ai/_skills/skills_stuff/specialists/project/skill-ai-it/templates/govcheck/core.py"
