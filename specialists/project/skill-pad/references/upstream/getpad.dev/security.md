**Title:** Security

**Source:** [https://www.getpad.dev/security](https://www.getpad.dev/security)

---

# Page Structure Map
```text
Security
├── Reporting a vulnerability
├── What to expect
├── Scope
│   └── Out of scope
└── Supported versions
```

---

We take security seriously. If you discover a vulnerability in Pad — the OSS binary, the hosted Pad Cloud service, or the marketing site — please report it privately so we can fix it before it becomes a problem.

## Reporting a vulnerability

Two private channels:

- **Email:** security@perpetualsoftware.org
- **GitHub:** Private vulnerability advisory

Please do **not** open a public issue for security reports.

Include in your report:

- A description of the vulnerability
- Reproduction steps
- The potential impact
- Any suggested fixes (if you have them)

## What to expect

| Phase | Timeline |
| --- | --- |
| Acknowledgement | Within 48 hours |
| Initial assessment | Within 1 week |
| Critical severity fix | Target: 72 hours |
| High severity fix | Target: 1 week |
| Medium / Low severity fix | Next release |

## Scope

Both the OSS Pad binary and the hosted Pad Cloud service are in scope. Specifically:

- **Data integrity** — unauthorized modification or deletion
- **Authentication / authorization** — bypassing role checks, session hijacking, privilege escalation
- **Network exposure** — outside Docker, Pad binds to localhost by default; any vulnerability that widens access beyond the intended deployment is in scope
- **Code injection** — paths where user input (item content, wiki-links, field values) could lead to code execution
- **Path traversal** — reading or writing files outside the workspace directory
- **Embedded web UI** — XSS or other web vulnerabilities in the SvelteKit frontend

### Out of scope

- Vulnerabilities in third-party dependencies (please report those upstream — we're happy to know so we can update)
- Issues that require physical access to the machine
- Social engineering
- Self-hosted instances misconfigured to bypass our security defaults

## Supported versions

Security fixes ship for the latest release. Older versions are not patched.

See SECURITY.md on GitHub for the canonical version of this policy.
