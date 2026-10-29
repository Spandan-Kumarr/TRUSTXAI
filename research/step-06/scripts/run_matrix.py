#!/usr/bin/env python3
"""Run the private Step-6 development or frozen held-out matrix."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import socket
import sys


REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "backend"))
DEFAULT_RUNTIME = Path(os.environ.get("TRUSTXAI_RUNTIME", "/workspace/thesis-runtime")) / "clinical-cdss" / "step-06"
os.environ.setdefault("TRUSTXAI_APP_DATA", str(DEFAULT_RUNTIME / "checker-cache"))

from trustxai import store as checker_store  # noqa: E402
from trustxai.research_freeze import load_label_blind_test_inputs  # noqa: E402
from trustxai.research_runner import (  # noqa: E402
    MatrixConfig, PrivateRunStore, ResearchLocalModels, build_signatures,
    execute_partition, input_manifest_sha256, validate_test_freeze,
)


def app_server_running(host="127.0.0.1", port=8000):
    with socket.socket() as sock:
        sock.settimeout(0.2)
        return sock.connect_ex((host, port)) == 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--partition", choices=("development", "test"), required=True)
    parser.add_argument("--stage", choices=("evidence", "matrix", "all"), default="all")
    parser.add_argument("--runtime", type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument("--inputs", type=Path)
    parser.add_argument("--nli-threshold", type=float, required=True,
                        choices=(0.60, 0.70, 0.80, 0.90, 0.95))
    parser.add_argument("--critic-threshold", type=float, required=True)
    parser.add_argument("--cpu-budget-hours", type=float, default=24.0)
    parser.add_argument("--cpu-reserve-minutes", type=float, default=15.0)
    parser.add_argument("--freeze", type=Path)
    parser.add_argument("--freeze-sha256")
    parser.add_argument("--allow-app-server", action="store_true",
                        help="Explicitly accept model-memory competition with a running app server")
    args = parser.parse_args()

    if args.partition == "development" and args.stage == "all":
        raise ValueError(
            "Development must run --stage evidence, calibrate the checker, then run --stage matrix"
        )

    private = args.runtime / "private"
    input_path = args.inputs or private / f"{args.partition}_inputs.json"
    config = MatrixConfig(nli_threshold=args.nli_threshold,
                          critic_threshold=args.critic_threshold,
                          cpu_budget_seconds=args.cpu_budget_hours * 3600,
                          cpu_reserve_seconds=args.cpu_reserve_minutes * 60)
    models = ResearchLocalModels()
    signatures = build_signatures(models, config)

    # Avoid recording held-out access when execution cannot start because the
    # interactive application still owns the same memory-intensive models.
    if app_server_running() and not args.allow_app_server:
        raise RuntimeError("Stop the local app server before the memory-intensive research run")

    freeze = None
    if args.partition == "test":
        if args.freeze is None:
            raise ValueError("Held-out test requires --freeze and --freeze-sha256")
        # Refuse to open held-out inputs unless development already froze the
        # exact matrix configuration in this private runtime.
        run_signature_path = private / "RUN_SIGNATURE.json"
        if not run_signature_path.is_file():
            raise ValueError("Held-out test requires a completed development run signature")
        run_signature = json.loads(run_signature_path.read_text())
        if (run_signature.get("signatures", {}).get("evidence") != signatures["evidence"]
                or run_signature.get("signatures", {}).get("matrix") != signatures["matrix"]):
            raise ValueError("Held-out configuration differs from the frozen development runner")
        # Validate the immutable public freeze before opening even label-blind
        # held-out case text. The loader records the first access atomically.
        freeze = validate_test_freeze(args.freeze, args.freeze_sha256, signatures, "deferred", config)
        rows = load_label_blind_test_inputs(
            freeze_path=args.freeze,
            inputs_path=input_path,
            access_record_path=private / "test" / "TEST_ACCESS.json",
            expected_freeze_sha256=args.freeze_sha256,
        )
    elif args.freeze is not None or args.freeze_sha256 is not None:
        raise ValueError("Freeze arguments are reserved for the held-out test")
    else:
        rows = json.loads(input_path.read_text())
    if not isinstance(rows, list) or not rows:
        raise ValueError("Private input file must contain a non-empty JSON list")
    manifest = input_manifest_sha256(rows)

    checker_store.initialize()
    metadata = {"runner": "Step-6 private matrix", "raw_text_public": False,
                "gold_fields_accepted": False, "research_context_tokens": 2048}
    run_store = PrivateRunStore(private, signatures, metadata)

    def progress(value):
        print(json.dumps(value, sort_keys=True), flush=True)

    with run_store.exclusive():
        if freeze is not None:
            run_store.record_freeze("test", freeze, args.freeze_sha256)
        result = execute_partition(rows, args.partition, models, run_store, config,
                                   stage=args.stage, progress=progress)
    result.update({"input_manifest_sha256": manifest,
                   "input_file_sha256": hashlib.sha256(input_path.read_bytes()).hexdigest(),
                   "runner_signatures": signatures})
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
