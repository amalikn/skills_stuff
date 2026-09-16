# Ansible Repository Map

> Derived, non-authoritative navigation metadata. **Source files are
> authoritative.** This map orients an agent; it never replaces reading
> the original source. High-coverage *static* understanding only —
> dynamic/unresolved behaviour is labelled, not guessed.

## Scan metadata

- Nodes: 27 | Edges: 12
- Roles: 2
- Playbooks: 1
- Diagnostics: {'info': 3, 'warning': 1, 'error': 0, 'fatal': 0}

## Entry playbooks

- `site.yml`

## Inventory scopes (flavors / environments)

- **prod_env** — environments: prod; var dirs: group_vars

## Role catalogue

- `dns`
- `web`

## Role dependencies

- `web` → `dns`

## Key handlers

- `restart resolved` (roles/dns/handlers/main.yml)

## High-impact templates

- `roles/dns/templates/resolved.conf.j2`

## Critical operations (review carefully)

- `Deploy resolved config` — roles/dns/tasks/main.yml:2 [ansible.builtin.template]
- `Destroy old data` — roles/dns/tasks/main.yml:9 [ansible.builtin.shell]
- `Notify restart` — site.yml:8 [ansible.builtin.command]

## Custom vars plugins (dynamic variable sources)

- `vars_plugins/custom_vars.py` — supplies variables at inventory load (**dynamic**, not statically resolvable)

## Dynamic & unresolved references

- `ARI002_DYNAMIC_INCLUDE` dynamic include/notify target: {{ os_family }}.yml (roles/dns/tasks/main.yml)

## Retrieval guidance

1. Start here, not in `graph.yaml`.
2. Run a bounded query: `ansible-repo-intelligence query <kind> <name>`.
3. Open only the 3–10 source files the query points to.
4. Verify every important claim against source. Never treat this map as source.
5. Do not load `graph.yaml` in full unless doing a repository-wide audit.
