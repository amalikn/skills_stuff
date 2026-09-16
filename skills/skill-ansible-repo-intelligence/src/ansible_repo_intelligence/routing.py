"""Deterministic question router (Experiment-1 q21 fix).

Pure, offline classification of a natural-language repository question into a
*recommended* ARI command. This module NEVER executes a query — it only advises.
It is the enforceable form of the SKILL.md routing rule so the variable-origin
miss (external benchmark q21: a variable-origin question was answered from the
role action digest) cannot silently regress.

Design invariants:
- No I/O, no graph load, no tool execution. Classification is a pure function of
  the question text (and the config keyword tables passed in, if any).
- Deterministic: same text -> same result, first-match-wins priority order.
- Variable-origin / precedence / vars-plugin questions outrank role-config
  keywords, because that is precisely the class the role digest must not answer.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# Categories (coarse) and subtypes (fine) — mirror the prompt's routing spec.
CAT_RELATIONSHIP = "relationship_query"
CAT_DIRECT = "direct_config"
CAT_LIVE = "live_operational"
CAT_REPO_WIDE = "repo_wide"
CAT_AMBIGUOUS = "ambiguous"

SUB_VARIABLE_ORIGIN = "variable_origin"
SUB_VARIABLE_PRECEDENCE = "variable_precedence"
SUB_VARS_PLUGIN_ORIGIN = "vars_plugin_origin"
SUB_HANDLER_CHAIN = "handler_chain"
SUB_IMPACT = "impact"
SUB_REACHABILITY = "reachability"
SUB_INVENTORY_SCOPE = "inventory_scope"
SUB_DYNAMIC_REFERENCE = "dynamic_reference"
SUB_DIRECT_CONTROL = "direct_control"


@dataclass(frozen=True)
class RouteResult:
    category: str
    subtype: str
    rule_id: str
    reason: str
    recommendations: tuple[str, ...]
    variable: str | None = None
    executes: bool = False  # always False — the router never runs tools
    alternatives: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "subtype": self.subtype,
            "rule_id": self.rule_id,
            "reason": self.reason,
            "recommendations": list(self.recommendations),
            "variable": self.variable,
            "executes": self.executes,
            "alternatives": list(self.alternatives),
        }


# Extract a candidate variable name: snake_case token, or a `backticked` token.
_BACKTICK = re.compile(r"`([A-Za-z_][A-Za-z0-9_]*)`")
_SNAKE = re.compile(r"\b([a-z][a-z0-9]*(?:_[a-z0-9]+)+)\b")


def _candidate_variable(text: str) -> str | None:
    m = _BACKTICK.search(text)
    if m:
        return m.group(1)
    # Prefer topology_* / *_vars-looking tokens, else first snake_case token that
    # is not an obvious module/command word.
    stop = {"tasks_main", "handlers_main", "group_vars", "host_vars",
            "vars_plugins", "main_yml", "ansible_os", "ansible_os_family"}
    for cand in _SNAKE.findall(text):
        if cand not in stop:
            return cand
    return None


# Keyword tables. Ordered checks below decide priority; keep tables small/literal.
_KW_VAR_PRECEDENCE = (
    "precedence", "which value wins", "value wins", "wins for", "overrides",
    "override", "takes precedence", "effective value", "which definition wins",
)
_KW_VARS_PLUGIN = (
    "vars plugin", "vars_plugin", "topology_vars", "vars plugins", "plugin inject",
    "inject", "injects", "injected",
)
# STRONG cues are almost always variable-origin questions on their own.
_KW_VAR_ORIGIN_STRONG = (
    "come from", "comes from", "originate", "origin of", "possible origins",
    "which source", "source supplies", "supplies", "set by inventory",
    "defined in inventory",
)
# WEAK cues need a variable signal (the word 'variable' or a snake_case token).
_KW_VAR_ORIGIN_WEAK = (
    "where does", "where is it defined", "which file defines", "who defines",
    "where can", "where.*defined",
)
_KW_HANDLER = (
    "notify", "notifies", "handler", "listen", "flush_handlers", "flush handlers",
    "restart", "reload", "trigger", "triggers",
)
_KW_IMPACT = (
    "impact", "affected", "blast radius", "blast-radius", "downstream",
    "what happens if", "if this changes", "if.*change",
)
_KW_REACH = (
    "reach", "reachable", "reaches", "which playbooks", "can reach",
    "reachability",
)
_KW_INVENTORY = (
    "flavor", "flavour", "which environment", "inventory scope", "group appear",
    "same-named group", "cross-flavor", "cross flavor", "which groups",
)
_KW_DYNAMIC = (
    "dynamic include", "jinja expression", "cannot be resolved", "unresolved",
    "templated name", "dynamic reference", "custom plugin",
)
_KW_LIVE = (
    "currently", "right now", "live host", "running host", "on the box",
    "actual host", "host state", "which hosts currently",
)
_KW_REPO_WIDE = (
    "all playbooks", "list playbooks", "every role", "repository-wide",
    "repo-wide", "audit the repo", "whole repo", "entire repository",
)


def _has(text: str, needles: tuple[str, ...]) -> str | None:
    for n in needles:
        if ".*" in n:
            if re.search(n, text):
                return n
        elif n in text:
            return n
    return None


def _var_recs(var: str | None) -> tuple[str, ...]:
    name = var if var else "<name>"
    return (
        f"query variable {name}",
        f"query vars_plugin {name}",
    )


def classify_question(text: str) -> RouteResult:
    """Classify a repo question into a recommended (never executed) command.

    First-match-wins priority. Variable-origin/precedence/vars-plugin classes are
    checked BEFORE role-config so q21-style questions never route to the digest.
    """
    t = (text or "").strip().lower()
    var = _candidate_variable(text or "")

    # --- 1. Variable precedence (most specific variable class) --------------
    if _has(t, _KW_VAR_PRECEDENCE):
        return RouteResult(
            category=CAT_RELATIONSHIP, subtype=SUB_VARIABLE_PRECEDENCE,
            rule_id="ROUTE-VAR-PRECEDENCE",
            reason="Precedence/'which value wins' cannot be answered from a role "
                   "action digest; needs variable + vars_plugin origin analysis.",
            recommendations=_var_recs(var), variable=var,
            alternatives=("source verification when origins conflict or are dynamic",),
        )

    # --- 2. Vars-plugin supply ----------------------------------------------
    if _has(t, _KW_VARS_PLUGIN):
        return RouteResult(
            category=CAT_RELATIONSHIP, subtype=SUB_VARS_PLUGIN_ORIGIN,
            rule_id="ROUTE-VARS-PLUGIN",
            reason="Vars-plugin supply is a dynamic origin; route to vars_plugin "
                   "query, not the role digest.",
            recommendations=_var_recs(var), variable=var,
            alternatives=("source verification: vars_plugins/*.py is dynamic",),
        )

    # --- 3. Variable origin (general) ---------------------------------------
    # STRONG cue alone triggers; WEAK cue needs a variable signal.
    strong = _has(t, _KW_VAR_ORIGIN_STRONG)
    weak = _has(t, _KW_VAR_ORIGIN_WEAK)
    mentions_variable = ("variable" in t) or (var is not None)
    if strong or (weak and mentions_variable):
        return RouteResult(
            category=CAT_RELATIONSHIP, subtype=SUB_VARIABLE_ORIGIN,
            rule_id="ROUTE-VAR-ORIGIN",
            reason="Variable-origin question: a role digest shows what a role "
                   "DOES, not where inventory/plugin variables ORIGINATE.",
            recommendations=_var_recs(var), variable=var,
            alternatives=("source verification when results are dynamic/conflicting",),
        )

    # --- 4. Handler chains ---------------------------------------------------
    if _has(t, _KW_HANDLER) and ("handler" in t or "notify" in t
                                 or "listen" in t or "restart" in t or "reload" in t):
        return RouteResult(
            category=CAT_RELATIONSHIP, subtype=SUB_HANDLER_CHAIN,
            rule_id="ROUTE-HANDLER-CHAIN",
            reason="Handler notify/listen chains are graph relationships; use "
                   "bounded query/explain, not a flat file read.",
            recommendations=(
                'query handler "<handler name>"',
                'explain "<handler node>"',
            ),
        )

    # --- 5. Impact / reachability -------------------------------------------
    if _has(t, _KW_IMPACT):
        return RouteResult(
            category=CAT_RELATIONSHIP, subtype=SUB_IMPACT,
            rule_id="ROUTE-IMPACT",
            reason="Static blast-radius question; use bounded impact traversal.",
            recommendations=("impact --path <file-or-role>",),
            alternatives=("mcp-smc for LIVE host-level blast radius",),
        )
    if _has(t, _KW_REACH):
        return RouteResult(
            category=CAT_RELATIONSHIP, subtype=SUB_REACHABILITY,
            rule_id="ROUTE-REACHABILITY",
            reason="Reachability (which playbooks/roles reach X) is a graph query.",
            recommendations=("query file <path>", "impact --path <path>"),
        )

    # --- 6. Inventory scope --------------------------------------------------
    if _has(t, _KW_INVENTORY):
        return RouteResult(
            category=CAT_RELATIONSHIP, subtype=SUB_INVENTORY_SCOPE,
            rule_id="ROUTE-INVENTORY-SCOPE",
            reason="Flavor/group scope is inventory-relationship data; keep "
                   "flavor+environment namespacing.",
            recommendations=("query group <group>", "query flavor <flavor>"),
            alternatives=("mcp-smc for live inventory resolution",),
        )

    # --- 7. Dynamic / unresolved references ---------------------------------
    if _has(t, _KW_DYNAMIC):
        return RouteResult(
            category=CAT_RELATIONSHIP, subtype=SUB_DYNAMIC_REFERENCE,
            rule_id="ROUTE-DYNAMIC-REF",
            reason="Dynamic/unresolved references are labelled, not resolved; "
                   "query then verify source.",
            recommendations=('query playbook <name>', 'explain "<node>"'),
            alternatives=("source verification: target is dynamic/unresolved",),
        )

    # --- 8. Live operational -------------------------------------------------
    if _has(t, _KW_LIVE):
        return RouteResult(
            category=CAT_LIVE, subtype=SUB_DIRECT_CONTROL,
            rule_id="ROUTE-LIVE",
            reason="Live/current host state is out of static scope; use live tooling.",
            recommendations=("mcp-smc (live inventory / host blast-radius)",),
        )

    # --- 9. Repo-wide --------------------------------------------------------
    if _has(t, _KW_REPO_WIDE):
        return RouteResult(
            category=CAT_REPO_WIDE, subtype=SUB_DIRECT_CONTROL,
            rule_id="ROUTE-REPO-WIDE",
            reason="Repository-wide audit is the only case that justifies the map.",
            recommendations=("read ANSIBLE_REPO_MAP.md (repo-wide only)",),
        )

    # --- 10. Direct role config (default for 'how is X configured') ---------
    if _has(t, ("install", "configure", "package", "template", "service",
                "how is", "which template", "what packages", "does the role")):
        return RouteResult(
            category=CAT_DIRECT, subtype=SUB_DIRECT_CONTROL,
            rule_id="ROUTE-DIRECT-CONFIG",
            reason="Role-local configuration question; the action digest answers "
                   "it from facts without opening every task file.",
            recommendations=("query role <role> --view actions",),
        )

    # --- 11. Ambiguous -------------------------------------------------------
    return RouteResult(
        category=CAT_AMBIGUOUS, subtype="unknown",
        rule_id="ROUTE-AMBIGUOUS",
        reason="No confident classification; agent should pick from alternatives.",
        recommendations=("query role <role> --view actions",),
        alternatives=(
            "query variable <name>  (if about a variable's origin)",
            'query handler "<name>"  (if about a handler)',
            "impact --path <path>  (if about blast radius)",
        ),
    )
