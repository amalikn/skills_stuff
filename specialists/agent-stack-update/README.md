# Agent Stack Delta Update

Base: `agent-stack.zip`
Update: routing-evals revision

- Added files: 20
- Modified files: 30
- Removed files: 0

Run:

```bash
./apply-agent-stack-update.sh /path/to/agent-stack
```

Optional:

```bash
./apply-agent-stack-update.sh --dry-run /path/to/agent-stack
./apply-agent-stack-update.sh --force /path/to/agent-stack
```

The script backs up replaced files under `.agent-stack-update-backups/<timestamp>/` in the target repository.
