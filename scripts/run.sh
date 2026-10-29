#!/usr/bin/env bash
set -euo pipefail
TASK_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
TASK_PYTHON="${TRUSTXAI_PYTHON:-/workspace/thesis-runtime/venv/bin/python}"
export PYTHONPATH="$TASK_ROOT/backend${PYTHONPATH:+:$PYTHONPATH}"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
cd "$TASK_ROOT"
exec "$TASK_PYTHON" -m uvicorn trustxai.main:app --host "${TRUSTXAI_HOST:-127.0.0.1}" --port "${TRUSTXAI_PORT:-8000}"
