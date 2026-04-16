# Healthcheck Checklist

- `git -C <repo-path> rev-parse --show-toplevel` succeeds.
- `~/_ansible/local-knowledge/<repo-name>/snapshots/` exists after snapshot.
- `history/.git/` exists after `history-init`.
- `git -C <history-path> status --short` is clean immediately after `history-commit`.
