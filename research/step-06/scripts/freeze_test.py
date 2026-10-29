#!/usr/bin/env python3
"""Create/verify the immutable Step 6 held-out-test freeze."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "backend"))

from trustxai.research_freeze import (  # noqa: E402
    FreezeError, create_freeze, load_label_blind_test_inputs, verify_freeze,
)


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    create = commands.add_parser("create", help="Create a new write-protected freeze")
    create.add_argument("--repo-root", type=Path, default=REPO)
    create.add_argument("--development-evidence", type=Path, required=True)
    create.add_argument("--development-matrix", type=Path, required=True)
    create.add_argument("--calibration", type=Path, required=True)
    create.add_argument("--projection", type=Path, required=True)
    create.add_argument("--test-inputs", type=Path, required=True)
    create.add_argument("--output", type=Path, required=True)
    create.add_argument("--fallback-threshold", type=float)
    create.add_argument("--deviation", type=Path)
    create.add_argument("--recorded-at")

    verify = commands.add_parser("verify", help="Verify immutability and digest")
    verify.add_argument("--freeze", type=Path, required=True)
    verify.add_argument("--expected-sha256")

    access = commands.add_parser("open-test", help="Open only frozen label-blind test inputs")
    access.add_argument("--freeze", type=Path, required=True)
    access.add_argument("--inputs", type=Path, required=True)
    access.add_argument("--access-record", type=Path, required=True)
    access.add_argument("--expected-freeze-sha256")
    return parser.parse_args()


def main() -> int:
    args = arguments()
    try:
        if args.command == "create":
            record = create_freeze(
                repo_root=args.repo_root,
                output=args.output,
                development_evidence=args.development_evidence,
                development_matrix=args.development_matrix,
                calibration_path=args.calibration,
                projection_path=args.projection,
                test_inputs=args.test_inputs,
                fallback_threshold=args.fallback_threshold,
                deviation_path=args.deviation,
                recorded_at=args.recorded_at,
            )
            print(json.dumps({
                "status": record["status"],
                "threshold": record["checker"]["selected_operating_threshold"],
                "independent_semantic_validation": record["checker"]["independent_semantic_validation"],
                "output": str(args.output),
                "checksum": str(args.output.with_suffix(args.output.suffix + ".sha256")),
            }, indent=2))
        elif args.command == "verify":
            record, digest = verify_freeze(args.freeze, expected_sha256=args.expected_sha256)
            print(json.dumps({"status": record["status"], "sha256": digest}, indent=2))
        else:
            rows = load_label_blind_test_inputs(
                freeze_path=args.freeze,
                inputs_path=args.inputs,
                access_record_path=args.access_record,
                expected_freeze_sha256=args.expected_freeze_sha256,
            )
            print(json.dumps({
                "status": "authorized_label_blind_test_access",
                "source_count": len(rows),
                "access_record": str(args.access_record),
                "gold_loaded": False,
                "outcomes_exposed": False,
            }, indent=2))
    except FreezeError as error:
        print(f"FREEZE REFUSED: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
