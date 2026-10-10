"""The checks, by family, and the order they run in (unchanged from the single-file checker, so output is identical)."""

from __future__ import annotations

from . import paths
from . import catalog
from . import library
from . import runtime
from . import records
from . import evidence
from . import structure

CHECKS = (
    paths.check_referenced_paths,
    paths.check_index_links,
    catalog.check_count_claims,
    catalog.check_catalog_coverage,
    catalog.check_task_recipes,
    library.check_manifest_paths_exist,
    library.check_manifest_covers_library,
    library.check_package_skills_have_skill_md,
    library.check_library_counts,
    records.check_archcore_document_contract,
    records.check_status_markers_resolved,
    runtime.check_venv_outside_repo,
    runtime.check_interpreter_pinning,
    records.check_derived_freshness,
    records.check_constant_sync,
    records.check_append_only_grain,
    evidence.check_evidence_provenance,
    evidence.check_jsonl_evidence_contract,
    paths.check_skill_package_references,
    paths.check_superseded_marked_in_index,
    evidence.check_no_duplicate_yaml_keys,
    structure.check_govcheck_structure,
)
