# skill-smc Known Issues and Gaps

## Knowledge Gaps (by design — require execution layer)

| Gap | Why | Mitigation |
|---|---|---|
| Actual flattened topology output for a specific host | Requires executing `vars_plugins/topology_vars.py` against live inventory | Phase 3: ansible-wifi MCP |
| Live service status, log content, running metrics | Requires SSH access to the box | Phase 2: ssh-manager + mcp-grafana |
| Cross-flavor inventory impact at scale | Requires running `ansible-inventory --list` × 7 flavors | Phase 3: ansible-wifi MCP |

## Coverage Gaps (partial knowledge)

| Area | Status | Notes |
|---|---|---|
| x86 / apn flavor live validation | Not validated | RUNBOOK flavor differences are from code inspection only; malik-rct01 is the only live-validated box |
| cnmaestro-provisioning internals | Partial | Service config path known; provisioning logic not deeply documented |
| NBN Accelerate API behavior | Minimal | API call pattern noted; response handling and error states undocumented |
| Redis usage details | Minimal | Used by cnmaestro-provisioning; key schema undocumented |
| Kohana / Tstik web apps | Minimal | Running on RCT; role config paths known; app internals not documented |
| RISE monitoring suite (riseclient, risengine) | Partial | Unit names known; behavioral details from code inspection only |

## Skill Staleness Risks

- Service names and config paths may drift as ansible-wifi roles are updated.
- Flavor differences (RCT vs x86) are grounded in live RCT validation only; x86 assumptions are from role code inspection.
- Prometheus alert names and thresholds are taken from `roles/smc_prometheus/` at commit `0d0c91a`; these may change.

## Out of Scope (permanent)

- Bugs that only appear on live hardware (require CI/test environment)
- CNMaestro / NBN API behaviour (external systems; no test access)
- WiFi RF performance (hardware/environment)
- Multi-engineer workflow coordination (process problem, not knowledge problem)
