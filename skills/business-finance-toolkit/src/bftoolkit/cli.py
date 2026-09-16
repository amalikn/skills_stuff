import argparse
import json
from collections.abc import Sequence

from . import __version__
from .advisor import build_assessment_plan
from .gates import evaluate_pilot_gate
from .models import Claim, HumanApproval
from .provenance import create_run_manifest
from .store import LocalStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bftoolkit", description="Evidence-governed business assessment toolkit")
    subparsers = parser.add_subparsers(dest="command", required=True)
    assess = subparsers.add_parser("assess", help="Build a read-only assessment plan")
    assess.add_argument("--idea", required=True)
    assess.add_argument("--domain-pack", default="generic-import", choices=["generic-import", "australia-jdm"])
    gate = subparsers.add_parser("gate", help="Evaluate evidence and the pilot approval gate")
    gate.add_argument("--claims", required=True, help="Path to a JSON array of Claim objects")
    gate.add_argument("--required-claim", action="append", required=True)
    gate.add_argument("--approver", help="Named human pilot approver; omitted means review is still required")
    gate.add_argument("--store", help="Optional local SQLite path for claim, approval, and run persistence")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "assess":
        plan = build_assessment_plan(args.idea, domain_pack=args.domain_pack)
        payload = {"idea": args.idea, "domain_pack": args.domain_pack}
        manifest = create_run_manifest(payload, [], calculator_version=__version__, artifacts=["assessment-plan"])
        print(json.dumps({"plan": plan.model_dump(mode="json"), "run_manifest": manifest.model_dump(mode="json")}, indent=2, default=str))
        return 0
    if args.command == "gate":
        claims = [Claim.model_validate(item) for item in json.loads(open(args.claims, encoding="utf-8").read())]
        approval = HumanApproval(approver=args.approver, scope="pilot") if args.approver else None
        gate = evaluate_pilot_gate(claims, required_claim_ids=args.required_claim, approval=approval)
        manifest = create_run_manifest(
            {"claims": [claim.model_dump(mode="json") for claim in claims], "required_claim_ids": args.required_claim, "approval": approval.model_dump(mode="json") if approval else None},
            claims,
            calculator_version=__version__,
            artifacts=["pilot-gate"],
        )
        if args.store:
            store = LocalStore(args.store)
            for claim in claims:
                store.save_claim(claim)
            if approval:
                store.save_approval(approval)
            store.save_run(manifest)
        print(json.dumps({"gate": gate.model_dump(mode="json"), "run_manifest": manifest.model_dump(mode="json")}, indent=2, default=str))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
