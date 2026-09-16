---
id: variable-origin-routing
type: rule
title: Variable-origin questions must never be answered from the role action digest alone
status: proposed
created: 20260703_1745
provenance: q21 external-benchmark regression (topology-vars misrouted to role digest); fixed via routing.py + `route` CLI, confirmed by isolated Experiment 1 retest (docs/reports/ari-experiment1-routing-retest-20260703_1736.md)
tags: [correctness, routing, regression-prevention]
---

# Variable-origin questions must never be answered from the role action digest alone

A role action digest (`query role <role> --view actions`) shows what a role
**does** — packages, templates, services, commands. It does not, and must
never be treated as, evidence for where an inventory or vars-plugin variable
**originates**.

The external benchmark's q21 miss ("Where do per-host topology variables come
from?") was caused by an agent answering a variable-origin question from the
role digest instead of `query variable` / `query vars_plugin`. This is a
routing failure class, not a parser or graph defect, and it can recur any time
a question superficially resembles a role-configuration question.

**Enforcement:** `src/ansible_repo_intelligence/routing.py::classify_question`
checks variable-origin / variable-precedence / vars-plugin-origin keyword
classes **before** role-config keywords, so this question class cannot fall
through to the digest. `ansible-repo-intelligence route "<question>"` exposes
this classification directly (advisory only — it never executes a query).

Any future digest view, CLI command, or agent-workflow rewrite that touches
variable-origin questions must preserve this ordering and must not let the
role digest become the default source of truth for variable origin.
