# Expected output shape

Running `just example` against `examples/inventory/hosts.yml` and
`examples/playbooks/site.yml` should produce, under the chosen `--output-dir`:

```
<output-dir>/
├── .ansible-grapher-owned
├── inventory/
│   ├── inventory.dot
│   └── inventory.svg
├── playbooks/
│   └── site.svg
└── logs/
    └── commands.log
```

Checks worth doing manually:

- `inventory/inventory.svg` starts with `<?xml` / contains `<svg` and does NOT contain
  the literal strings `http_port` or `db_port` (variables are suppressed by default).
- `playbooks/site.svg` contains `<svg` and references both plays (`Configure web tier`,
  `Configure database tier`).
- `logs/commands.log` is valid JSON-lines and contains no raw extra-vars values.

No file under `examples/inventory/` or `examples/playbooks/` should ever be modified by
a run — this skill only reads sources and writes to the output directory.
