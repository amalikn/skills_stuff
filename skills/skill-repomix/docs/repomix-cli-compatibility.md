# Repomix CLI Compatibility

Always check:

```bash
repomix --version
repomix --help
```

or:

```bash
npx --yes repomix --version
npx --yes repomix --help
```

Validate required options before use:

- `--config`
- `--style`
- `--include`
- `--ignore`
- `--compress`
- `--include-diffs`
- `--token-budget`
- `--token-count-tree`
- `--mcp`
- `--remote`
- `--remote-branch`

Never silently weaken security or reproducibility when a flag is unavailable.
