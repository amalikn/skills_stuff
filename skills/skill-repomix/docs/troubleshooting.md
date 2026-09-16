# Troubleshooting

## Repomix missing

Install or invoke Repomix separately. The skill never installs it automatically.

## Output too large

- narrow `--include`
- select a smaller subsystem
- enable compression for architecture-only work
- reduce token budget
- split the task

## Secrets detected

Stop. Add the source path to `.repomixignore`, remove the generated pack, and regenerate.

## Profile mismatch

Run:

```bash
scripts/detect-language-profile --explain
```

Then pass `--profile` explicitly.
