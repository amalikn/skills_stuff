**Title:** Contributing

**Source:** [https://www.getpad.dev/contribute](https://www.getpad.dev/contribute)

---

# Page Structure Map
```text
Contributing
├── Prerequisites
├── Development loop
├── Branch naming
├── Pull requests
├── Filing issues
└── Contributor License Agreement
```

---

Pad is open source under Apache 2.0. Contributions are welcome — bug fixes, features, docs improvements, anything.

The canonical contributor guide is CONTRIBUTING.md on GitHub. The summary below is the quick path.

## Prerequisites

- Go 1.26+
- Node.js 22+
- Make

## Development loop

```bash
git clone https://github.com/PerpetualSoftware/pad
cd pad
make build      # Build web UI + Go binary
make test       # Run Go tests
make dev-web    # SvelteKit dev server with hot reload (localhost:5173)
make install    # Build, install to ~/.local/bin/pad, restart server
```

After backend changes, `make install` rebuilds the binary, kills the running server, installs the new binary to `~/.local/bin/pad`, and restarts. The web UI at `localhost:7777` reflects your changes immediately.

Frontend-only iteration is faster with `make dev-web` (SvelteKit's hot reload against the running pad backend).

## Branch naming

- `feat/relation-field-picker` — new features
- `fix/dashboard-progress-bar` — bug fixes
- `docs/update-api-reference` — documentation
- `refactor/store-interface` — refactoring

## Pull requests

- Keep PRs focused — one feature or fix per PR.
- Include a description of what changed and *why* — the why is what matters in the long term.
- Add tests for new backend functionality.
- Verify `make build` and `make test` pass before opening.

## Filing issues

- **Bugs** — use the bug-report template, include reproduction steps and the version (`pad --version`).
- **Features** — describe the problem first, then your proposed solution. The "why" matters more than the "what".
- **Questions / discussion** — open a GitHub Discussion rather than an issue.
- **Security vulnerabilities** — see Security; report privately, not via public issue.

## Contributor License Agreement

By submitting a pull request, you agree to the terms of our Contributor License Agreement. It's a lightweight CLA that preserves your rights while letting the project make coherent licensing decisions over time.
