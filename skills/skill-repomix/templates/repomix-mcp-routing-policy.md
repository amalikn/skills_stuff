# Repomix MCP Routing Policy

## Tool Boundaries

- Repomix MCP MUST be used for broad repository packaging, searchable snapshots, and remote repository context.
- Static Repomix packs SHOULD be used for reproducible audits, handoffs, fixed evidence, and local LLM input.
- Semantic-code tools SHOULD be used for symbol-aware navigation and editing.
- Context7 or official documentation MUST be used for current third-party documentation.
- Git and GitHub tools MUST be used for repository history, branches, commits, PRs, and mutation.
- Semgrep or another static analyser MUST be used for security and code-pattern analysis.
- Project-context or memory tools SHOULD be used for durable decisions, tasks, and state.
- Runtime and test tools MUST be used for behavioural validation.

## Routing Workflow

1. Identify the task.
2. Read governance and navigation files.
3. Select the smallest relevant subsystem.
4. Select a language profile.
5. Apply security exclusions.
6. Check token usage.
7. Choose MCP or static output.
8. Decide whether compression is appropriate.
9. Generate and validate output.
10. Report scope, format, compression, security status, and limitations.

## Security

- Security scanning MUST remain enabled.
- Secrets MUST be excluded before scanning.
- Remote Repomix configuration MUST NOT be trusted.
- Mutable local state MUST NOT be packed.
- Output MUST be reviewed before external upload.
