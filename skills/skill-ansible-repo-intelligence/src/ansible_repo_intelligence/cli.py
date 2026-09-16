"""Command-line interface: scan / validate / clean (Phase 1).

query / impact / explain / benchmark are Phase 2–3 and report a clear
"not available in this phase" message rather than failing silently.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import sys
from pathlib import Path

from . import __version__
from .ansible_config import load_ansible_config
from .app_config import AppConfig, apply_config_overrides, load_config_file
from .diagnostics import Diagnostics
from .discovery import discover
from .graph import build_graph
from .renderer import (
    render_diagnostics_yaml, render_graph_yaml, render_manifest_yaml,
    render_repository_map, render_scan_state_yaml,
)
from .significance import load_significance_engine
from .variables import load_precedence_config
from .validator import validate_config_tables, validate_context

_PKG_ROOT = Path(__file__).resolve().parents[2]
_CONFIG_DIR = _PKG_ROOT / "config"
SIG_RULES = _CONFIG_DIR / "significance_rules.yaml"
PREC_RULES = _CONFIG_DIR / "variable_precedence_rules.yaml"


def _sha(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def cmd_scan(args) -> int:
    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        print(f"error: repo not found: {repo}", file=sys.stderr)
        return 2
    output = Path(args.output).resolve() if args.output else (repo / ".ai-context")

    # Gate: validate config rule tables BEFORE scanning.
    ctres = validate_config_tables(SIG_RULES, PREC_RULES)
    if not ctres.ok:
        for e in ctres.errors:
            print(f"config error: {e}", file=sys.stderr)
        return 3

    cfg = AppConfig(
        repo=repo, output=output,
        inventory=Path(args.inventory).resolve() if args.inventory else None,
        inventory_root=Path(args.inventory_root).resolve() if args.inventory_root else None,
        all_inventory_flavors=args.all_inventory_flavors,
        follow_symlinks=args.follow_symlinks,
        max_file_bytes=args.max_file_bytes,
        strict=args.strict, fail_on_warning=args.fail_on_warning,
        offline=not args.run_inventory, run_inventory=args.run_inventory,
        incremental=args.incremental, force=args.force,
        deep_index_vendored=args.deep_index_vendored,
        include_patterns=tuple(args.include or ()),
        exclude_patterns=tuple(args.exclude or ()),
    )
    if args.config:
        cfg = apply_config_overrides(cfg, load_config_file(Path(args.config)))

    acfg = load_ansible_config(repo)
    # Fall back to ansible.cfg inventory setting when none supplied.
    if cfg.inventory is None and cfg.inventory_root is None and acfg.inventory:
        inv = (repo / acfg.inventory)
        if inv.exists():
            cfg.inventory = inv.resolve()

    sig = load_significance_engine(SIG_RULES)
    pcfg = load_precedence_config(PREC_RULES)
    diags = Diagnostics()

    disc = discover(cfg, acfg)

    # Incremental short-circuit: if a prior scan-state matches parser + config
    # fingerprint AND no discovered file changed, the existing outputs are
    # already current. A change triggers a full (safe) rebuild, because
    # cross-file resolution must see the whole graph to stay correct.
    config_fp_early = _sha(str(sorted(cfg.fingerprint_dict().items())))
    if cfg.incremental and not cfg.force:
        state_p = output / "cache" / "scan-state.yaml"
        if state_p.is_file() and (output / "graph.yaml").is_file():
            from ruamel.yaml import YAML as _Y
            prior = _Y(typ="safe", pure=True).load(state_p.read_text(encoding="utf-8")) or {}
            changed = _changed_files(prior, disc, config_fp_early)
            if changed is not None and not changed:
                print(f"incremental: no changes; outputs current at {output}")
                return 0
            if changed:
                print(f"incremental: {len(changed)} file(s) changed; full safe rebuild")
    graph = build_graph(cfg, acfg, disc, sig, pcfg, diags)

    # Render artifacts.
    graph_yaml = render_graph_yaml(graph)
    diag_yaml = render_diagnostics_yaml(diags)
    map_md = render_repository_map(cfg, graph, diags)
    # diagnostics may have grown during map rendering; re-render for consistency.
    diag_yaml = render_diagnostics_yaml(diags)

    source_fp = _source_fingerprint(disc, repo, cfg.max_file_bytes)
    config_fp = _sha(str(sorted(cfg.fingerprint_dict().items())))
    output_hashes = {
        "graph.yaml": _sha(graph_yaml),
        "diagnostics.yaml": _sha(diag_yaml),
        "ANSIBLE_REPO_MAP.md": _sha(map_md),
    }
    # Optional ansible-playbook-grapher provenance (supplementary evidence only;
    # scan never depends on it). OPT-IN via --playbook-grapher: machine-specific
    # tool availability must not leak into the default deterministic manifest.
    external_tools: dict = {}
    if getattr(args, "playbook_grapher", False):
        from .grapher import detect as _grapher_detect
        from .grapher import run_grapher as _run_grapher
        gp = getattr(args, "grapher_playbook", None)
        if gp:
            prov = _run_grapher(repo, gp, output / "cache")
        else:
            prov = _grapher_detect()
        external_tools = {"ansible_playbook_grapher": prov.to_dict()}

    manifest_yaml = render_manifest_yaml(
        cfg, graph, diags, source_fp, config_fp, output_hashes,
        disc.vendored_yaml_count, external_tools=external_tools,
    )
    scan_state = render_scan_state_yaml(_file_hashes(disc), config_fp)

    # Write.
    output.mkdir(parents=True, exist_ok=True)
    (output / "cache").mkdir(exist_ok=True)
    (output / "graph.yaml").write_text(graph_yaml, encoding="utf-8")
    (output / "diagnostics.yaml").write_text(diag_yaml, encoding="utf-8")
    (output / "ANSIBLE_REPO_MAP.md").write_text(map_md, encoding="utf-8")
    (output / "manifest.yaml").write_text(manifest_yaml, encoding="utf-8")
    (output / "cache" / "scan-state.yaml").write_text(scan_state, encoding="utf-8")

    # Validate generated output.
    vres = validate_context(output, config_tables=(SIG_RULES, PREC_RULES))
    counts = diags.counts()
    print(f"scan complete: {graph.statistics()['node_count']} nodes, "
          f"{graph.statistics()['edge_count']} edges, diagnostics={counts}")
    print(f"output: {output}")
    if not vres.ok:
        for e in vres.errors:
            print(f"validation error: {e}", file=sys.stderr)
        return 4
    if cfg.strict and diags.has_blocking():
        print("strict mode: blocking diagnostics present", file=sys.stderr)
        return 5
    if cfg.fail_on_warning and diags.has_warnings():
        print("fail-on-warning: warnings present", file=sys.stderr)
        return 6
    return 0


def cmd_validate(args) -> int:
    output = Path(args.context).resolve()
    if not output.is_dir():
        print(f"error: context dir not found: {output}", file=sys.stderr)
        return 2
    vres = validate_context(output, config_tables=(SIG_RULES, PREC_RULES))
    if vres.ok:
        print(f"valid: {output}")
        for w in vres.warnings:
            print(f"warning: {w}")
        return 0
    for e in vres.errors:
        print(f"error: {e}", file=sys.stderr)
    return 1


def cmd_clean(args) -> int:
    output = Path(args.output).resolve()
    removed = []
    for name in ("graph.yaml", "diagnostics.yaml", "ANSIBLE_REPO_MAP.md", "manifest.yaml"):
        p = output / name
        if p.is_file():
            p.unlink()
            removed.append(name)
    cache = output / "cache" / "scan-state.yaml"
    if cache.is_file():
        cache.unlink()
        removed.append("cache/scan-state.yaml")
    print(f"removed: {removed}")
    return 0


def _resolve_context(args) -> Path:
    if getattr(args, "context", None):
        return Path(args.context).resolve()
    return (Path(args.repo).resolve() / ".ai-context") if getattr(args, "repo", None) \
        else Path(".ai-context").resolve()


def cmd_query(args) -> int:
    from .query import (
        QueryOptions, load_store, render_output, render_view, run_query, run_view,
    )
    ctx = _resolve_context(args)
    gp = ctx / "graph.yaml"
    if not gp.is_file():
        print(f"error: no graph.yaml at {ctx}; run scan first", file=sys.stderr)
        return 2
    store = load_store(ctx)
    opts = QueryOptions(
        limit=args.limit, max_depth=args.max_depth,
        max_output_bytes=args.max_output_bytes,
        fields=tuple(args.fields.split(",")) if args.fields else QueryOptions.fields,
        output=args.output,
        include_neighbours=not args.no_neighbours,
        include_attributes=args.include_attributes,
    )
    if getattr(args, "view", None):
        payload = run_view(store, args.selector, args.term, args.view, opts)
        print(render_view(payload, opts.output), end="")
        return 0
    payload = run_query(store, args.selector, args.term, opts)
    print(render_output(payload, opts.output), end="")
    return 0


def cmd_impact(args) -> int:
    from .query import QueryOptions, load_store, render_output, run_impact
    ctx = _resolve_context(args)
    gp = ctx / "graph.yaml"
    if not gp.is_file():
        print(f"error: no graph.yaml at {ctx}; run scan first", file=sys.stderr)
        return 2
    store = load_store(ctx)
    opts = QueryOptions(
        limit=args.limit, max_depth=args.max_depth,
        max_output_bytes=args.max_output_bytes,
        output=args.output, include_attributes=args.include_attributes,
    )
    payload = run_impact(store, args.path, opts)
    print(render_output(payload, opts.output), end="")
    return 0


def cmd_benchmark(args) -> int:
    from .benchmark import load_questions, render_benchmark, run_benchmark
    repo = Path(args.repo).resolve()
    ctx = _resolve_context(args)
    if not (ctx / "graph.yaml").is_file():
        print(f"error: no graph.yaml at {ctx}; run scan first", file=sys.stderr)
        return 2
    questions = load_questions(Path(args.questions))
    result = run_benchmark(repo, ctx, questions)
    out = render_benchmark(result, args.output)
    print(out, end="")
    if args.report:
        Path(args.report).write_text(render_benchmark(result, "yaml"), encoding="utf-8")
        print(f"benchmark report written: {args.report}")
    # PARTIAL by construction (external grading required); exit 0 = harness ran.
    return 0


def cmd_explain(args) -> int:
    from .query import QueryOptions, load_store, render_explain, run_explain
    ctx = _resolve_context(args)
    if not (ctx / "graph.yaml").is_file():
        print(f"error: no graph.yaml at {ctx}; run scan first", file=sys.stderr)
        return 2
    store = load_store(ctx)
    opts = QueryOptions(output=args.output, include_attributes=args.include_attributes)
    payload = run_explain(store, args.target, opts)
    print(render_explain(payload, opts.output), end="")
    return 0 if payload.get("found") else 1


def cmd_route(args) -> int:
    """Classify a question into a recommended command. NEVER executes it.

    Deterministic advisory router (q21 fix): keeps variable-origin/precedence/
    vars-plugin questions off the role action digest.
    """
    from .routing import classify_question
    r = classify_question(args.question)
    if args.output == "yaml":
        from ruamel.yaml import YAML
        y = YAML()
        y.default_flow_style = False
        buf = io.StringIO()
        y.dump(r.to_dict(), buf)
        print(buf.getvalue(), end="")
    else:
        print(f"category: {r.category}")
        print(f"subtype:  {r.subtype}")
        print(f"rule_id:  {r.rule_id}")
        print(f"reason:   {r.reason}")
        print("recommendations:")
        for c in r.recommendations:
            print(f"  - {c}")
        if r.alternatives:
            print("alternatives:")
            for c in r.alternatives:
                print(f"  - {c}")
        print("executes: false")
    return 0


def cmd_phase3(args) -> int:
    print(f"'{args.command}' is a Phase 3 command and is not available in this "
          "build. See docs/reports for phase status.", file=sys.stderr)
    return 10


def _source_fingerprint(disc, repo: Path, max_bytes: int) -> str:
    h = hashlib.sha256()
    for path, ch in sorted(_file_hashes(disc).items()):
        h.update(path.encode())
        h.update(ch.encode())
    return "sha256:" + h.hexdigest()


def _changed_files(prior: dict, disc, config_fp: str) -> list[str] | None:
    """Return changed file paths, [] if none, or None if prior state is unusable.

    None (unusable) forces a full rebuild — e.g. parser/config fingerprint drift.
    """
    from . import PARSER_VERSION
    if prior.get("parser_version") != PARSER_VERSION:
        return None
    if prior.get("configuration_fingerprint") != config_fp:
        return None
    prior_files = prior.get("files", {}) or {}
    current = _file_hashes(disc)
    changed = [p for p, h in current.items() if prior_files.get(p) != h]
    removed = [p for p in prior_files if p not in current]
    return sorted(set(changed) | set(removed))


def _file_hashes(disc) -> dict[str, str]:
    from .hashing import hash_bytes
    out: dict[str, str] = {}
    for f in disc.files:
        p = disc.repo / f.rel_path
        try:
            out[f.rel_path] = hash_bytes(p.read_bytes())
        except (OSError, ValueError):
            continue
    return out


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ansible-repo-intelligence",
                                description="Deterministic static Ansible repository intelligence.")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("scan", help="scan a repository and generate .ai-context")
    s.add_argument("--repo", required=True)
    s.add_argument("--output")
    s.add_argument("--config")
    s.add_argument("--inventory")
    s.add_argument("--inventory-root")
    s.add_argument("--inventory-flavor", action="append", default=[])
    s.add_argument("--all-inventory-flavors", action="store_true")
    s.add_argument("--playbook", action="append", default=[])
    s.add_argument("--include", action="append", default=[])
    s.add_argument("--exclude", action="append", default=[])
    s.add_argument("--follow-symlinks", action="store_true")
    s.add_argument("--max-file-bytes", type=int, default=2_000_000)
    s.add_argument("--strict", action="store_true")
    s.add_argument("--fail-on-warning", action="store_true")
    s.add_argument("--offline", action="store_true", default=True)
    s.add_argument("--run-inventory", action="store_true",
                   help="opt-in: execute ansible-inventory (may run plugin code)")
    s.add_argument("--incremental", action="store_true")
    s.add_argument("--force", action="store_true")
    s.add_argument("--deep-index-vendored", action="store_true")
    s.add_argument("--playbook-grapher", action="store_true",
                   help="opt-in: record ansible-playbook-grapher provenance (supplementary)")
    s.add_argument("--grapher-playbook", help="playbook (repo-relative) to graph when --playbook-grapher is set")
    s.add_argument("--format", default="yaml", choices=["yaml"])
    s.add_argument("--log-level", default="info")
    s.set_defaults(func=cmd_scan)

    v = sub.add_parser("validate", help="validate a generated .ai-context")
    v.add_argument("--context", required=True)
    v.set_defaults(func=cmd_validate)

    c = sub.add_parser("clean", help="remove generated artifacts")
    c.add_argument("--output", required=True)
    c.set_defaults(func=cmd_clean)

    # query
    q = sub.add_parser("query", help="bounded query over graph.yaml")
    q.add_argument("selector", help="role|variable|handler|tag|file|service|task|template|playbook|host|group|flavor|collection")
    q.add_argument("term", nargs="?", default=None)
    q.add_argument("--context")
    q.add_argument("--repo")
    q.add_argument("--limit", type=int, default=25)
    q.add_argument("--max-depth", type=int, default=1)
    q.add_argument("--max-output-bytes", type=int, default=65_536)
    q.add_argument("--fields", default=None)
    q.add_argument("--output", default="concise", choices=["concise", "yaml"])
    q.add_argument("--view", choices=["summary", "actions", "relationships", "sources"],
                   help="compact fact digest: actions = managed-resource digest")
    q.add_argument("--no-neighbours", action="store_true")
    q.add_argument("--include-attributes", action="store_true")
    q.set_defaults(func=cmd_query)

    # impact
    im = sub.add_parser("impact", help="static impact of a source path")
    im.add_argument("--path", required=True)
    im.add_argument("--context")
    im.add_argument("--repo")
    im.add_argument("--limit", type=int, default=50)
    im.add_argument("--max-depth", type=int, default=3)
    im.add_argument("--max-output-bytes", type=int, default=131_072)
    im.add_argument("--output", default="concise", choices=["concise", "yaml"])
    im.add_argument("--include-attributes", action="store_true")
    im.set_defaults(func=cmd_impact)

    # benchmark
    b = sub.add_parser("benchmark", help="token-efficiency benchmark (deterministic half)")
    b.add_argument("--repo", required=True)
    b.add_argument("--context")
    b.add_argument("--questions", required=True)
    b.add_argument("--report")
    b.add_argument("--output", default="concise", choices=["concise", "yaml"])
    b.set_defaults(func=cmd_benchmark)

    ex = sub.add_parser("explain", help="explain a single node (source, resolution, neighbours)")
    ex.add_argument("target", help="node id or name")
    ex.add_argument("--context")
    ex.add_argument("--repo")
    ex.add_argument("--output", default="concise", choices=["concise", "yaml"])
    ex.add_argument("--include-attributes", action="store_true")
    ex.set_defaults(func=cmd_explain)

    # route — deterministic advisory router (q21 fix); never executes a query
    rt = sub.add_parser("route",
                        help="classify a question into a recommended command (advisory only)")
    rt.add_argument("question", help="natural-language repo question")
    rt.add_argument("--output", default="concise", choices=["concise", "yaml"])
    rt.set_defaults(func=cmd_route)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
