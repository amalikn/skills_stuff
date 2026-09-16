"""Deterministic question-router tests (Experiment-1 q21 fix).

Covers Part 8 "Routing" requirements: variable-origin / vars-plugin / precedence
questions must NOT route to the role action digest; role-config still does; the
router never executes a tool and always emits a rule_id + reason.
"""

from __future__ import annotations

from ansible_repo_intelligence.cli import main
from ansible_repo_intelligence.routing import (
    CAT_DIRECT, CAT_LIVE, CAT_RELATIONSHIP, SUB_HANDLER_CHAIN, SUB_IMPACT,
    SUB_INVENTORY_SCOPE, SUB_VARIABLE_ORIGIN, SUB_VARIABLE_PRECEDENCE,
    SUB_VARS_PLUGIN_ORIGIN, classify_question,
)

ROLE_ACTIONS = "query role <role> --view actions"


def _recs(r) -> str:
    return " | ".join(r.recommendations)


# --- the q21 regression class: variable origin must never hit the digest ----

def test_variable_origin_routes_to_variable_query():
    r = classify_question("Where does topology_dns_servers come from?")
    assert r.category == CAT_RELATIONSHIP
    assert r.subtype == SUB_VARIABLE_ORIGIN
    assert "query variable topology_dns_servers" in r.recommendations
    assert ROLE_ACTIONS not in r.recommendations


def test_topology_vars_without_explicit_name_still_routes_to_variable():
    # exact q21 shape: no snake_case var token, word 'variable' absent
    r = classify_question("Where do topology vars come from?")
    assert r.subtype == SUB_VARIABLE_ORIGIN
    assert any("query variable" in c for c in r.recommendations)
    assert ROLE_ACTIONS not in r.recommendations


def test_vars_plugin_question_routes_to_vars_plugin_query():
    r = classify_question(
        "Is this variable set by inventory, role defaults, set_fact, or a vars plugin?")
    assert r.subtype == SUB_VARS_PLUGIN_ORIGIN
    assert any("query vars_plugin" in c for c in r.recommendations)
    assert ROLE_ACTIONS not in r.recommendations


def test_precedence_question_does_not_route_to_role_actions():
    r = classify_question("Which value wins for topology_dns_servers?")
    assert r.subtype == SUB_VARIABLE_PRECEDENCE
    assert ROLE_ACTIONS not in r.recommendations
    assert any("query variable" in c for c in r.recommendations)


def test_ambiguous_variable_question_returns_both_query_recommendations():
    r = classify_question("What are the possible origins of dns_servers?")
    assert r.subtype == SUB_VARIABLE_ORIGIN
    joined = _recs(r)
    assert "query variable dns_servers" in joined
    assert "query vars_plugin dns_servers" in joined


# --- role config still routes to the digest (no over-correction) ------------

def test_role_config_question_still_routes_to_action_digest():
    r = classify_question("How is Unbound configured in the smc_dns role?")
    assert r.category == CAT_DIRECT
    assert ROLE_ACTIONS in r.recommendations


def test_package_question_routes_to_action_digest():
    r = classify_question("What packages does smc_base install?")
    assert r.category == CAT_DIRECT
    assert ROLE_ACTIONS in r.recommendations


# --- other relationship classes ---------------------------------------------

def test_handler_chain_routes_to_relationship_query():
    r = classify_question("Which tasks notify the Restart unbound handler?")
    assert r.category == CAT_RELATIONSHIP
    assert r.subtype == SUB_HANDLER_CHAIN
    assert any("query handler" in c for c in r.recommendations)


def test_impact_routes_to_impact_command():
    r = classify_question("What is the blast radius if the DNS role changes?")
    assert r.subtype == SUB_IMPACT
    assert any(c.startswith("impact --path") for c in r.recommendations)


def test_inventory_scope_routes_to_group_query():
    r = classify_question("In which inventory flavors does the smc group appear?")
    assert r.subtype == SUB_INVENTORY_SCOPE
    assert any("query group" in c for c in r.recommendations)


def test_live_host_scope_routes_to_mcp_smc():
    r = classify_question("Which hosts currently have unbound running right now?")
    assert r.category == CAT_LIVE
    assert any("mcp-smc" in c for c in r.recommendations)


# --- invariants: rule id + reason present, never executes -------------------

def test_every_route_has_rule_id_and_reason_and_does_not_execute():
    for q in [
        "Where does topology_dns_servers come from?",
        "How is Unbound configured?",
        "Which tasks notify Restart unbound?",
        "blast radius of smc_dns",
        "something totally unclassifiable zzz",
    ]:
        r = classify_question(q)
        assert r.rule_id and isinstance(r.rule_id, str)
        assert r.reason and isinstance(r.reason, str)
        assert r.executes is False


def test_ambiguous_question_returns_alternatives():
    r = classify_question("something totally unclassifiable zzz")
    assert r.category == "ambiguous"
    assert r.alternatives  # non-empty guidance list


# --- determinism -------------------------------------------------------------

def test_classification_is_deterministic():
    q = "Where does topology_dns_servers come from?"
    a = classify_question(q).to_dict()
    b = classify_question(q).to_dict()
    assert a == b


# --- CLI smoke: route command runs, is advisory, never executes -------------

def test_cli_route_command_is_advisory(capsys):
    rc = main(["route", "Where does topology_dns_servers come from?"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "ROUTE-VAR-ORIGIN" in out
    assert "query variable topology_dns_servers" in out
    assert "executes: false" in out


def test_cli_route_yaml_output(capsys):
    rc = main(["route", "How is Unbound configured?", "--output", "yaml"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "rule_id:" in out and "recommendations:" in out
