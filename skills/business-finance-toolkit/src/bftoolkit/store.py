"""Small SQLite persistence layer for local claims, approvals, and run manifests."""

import sqlite3
from pathlib import Path

from .models import Claim, HumanApproval, RunManifest


class LocalStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS claims (id TEXT PRIMARY KEY, payload TEXT NOT NULL, saved_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
                CREATE TABLE IF NOT EXISTS approvals (id INTEGER PRIMARY KEY AUTOINCREMENT, scope TEXT NOT NULL, payload TEXT NOT NULL, saved_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
                CREATE TABLE IF NOT EXISTS runs (run_id TEXT PRIMARY KEY, payload TEXT NOT NULL, saved_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
                """
            )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def save_claim(self, claim: Claim) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO claims(id, payload, saved_at) VALUES (?, ?, CURRENT_TIMESTAMP) ON CONFLICT(id) DO UPDATE SET payload = excluded.payload, saved_at = CURRENT_TIMESTAMP",
                (claim.id, claim.model_dump_json()),
            )

    def get_claim(self, claim_id: str) -> Claim:
        with self._connect() as connection:
            row = connection.execute("SELECT payload FROM claims WHERE id = ?", (claim_id,)).fetchone()
        if row is None:
            raise KeyError(claim_id)
        return Claim.model_validate_json(row[0])

    def save_approval(self, approval: HumanApproval) -> None:
        with self._connect() as connection:
            connection.execute("INSERT INTO approvals(scope, payload) VALUES (?, ?)", (approval.scope, approval.model_dump_json()))

    def latest_approval(self, scope: str) -> HumanApproval:
        with self._connect() as connection:
            row = connection.execute("SELECT payload FROM approvals WHERE scope = ? ORDER BY id DESC LIMIT 1", (scope,)).fetchone()
        if row is None:
            raise KeyError(scope)
        return HumanApproval.model_validate_json(row[0])

    def save_run(self, manifest: RunManifest) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO runs(run_id, payload, saved_at) VALUES (?, ?, CURRENT_TIMESTAMP) ON CONFLICT(run_id) DO UPDATE SET payload = excluded.payload, saved_at = CURRENT_TIMESTAMP",
                (manifest.run_id, manifest.model_dump_json()),
            )
