import json

from pathlib import Path

from bftoolkit.cli import main


def test_assess_command_emits_a_traceable_plan(capsys) -> None:
    exit_code = main(
        [
            "assess",
            "--idea",
            "Import used equipment from Japan to Australia",
            "--domain-pack",
            "australia-jdm",
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["plan"]["domain_pack"] == "australia-jdm"
    assert payload["run_manifest"]["calculator_version"] == "0.1.0"


def test_gate_command_reads_claim_file_and_persists_auditable_approval(tmp_path, capsys) -> None:
    claims_file = Path(tmp_path) / "claims.json"
    claims_file.write_text(
        json.dumps(
            [
                {
                    "id": "market-demand",
                    "statement": "Demand checked",
                    "state": "VERIFIED",
                    "evidence_quality": "VERIFIED_PRIMARY",
                    "sources": [{"title": "Authority", "url": "https://example.test", "retrieved_on": "2026-08-29", "primary": True}],
                }
            ]
        )
    )
    store_file = Path(tmp_path) / "records.sqlite"

    exit_code = main(
        [
            "gate",
            "--claims",
            str(claims_file),
            "--required-claim",
            "market-demand",
            "--approver",
            "Owner",
            "--store",
            str(store_file),
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["gate"]["status"] == "APPROVED"
    assert store_file.exists()
