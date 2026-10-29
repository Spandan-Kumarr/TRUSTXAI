#!/usr/bin/env bash
set -euo pipefail
TASK_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -n "${TRUSTXAI_PYTHON:-}" ]]; then
  TASK_PYTHON="$TRUSTXAI_PYTHON"
elif [[ -x "$TASK_ROOT/.venv/bin/python" ]]; then
  TASK_PYTHON="$TASK_ROOT/.venv/bin/python"
elif [[ -x /workspace/thesis-runtime/venv/bin/python ]]; then
  TASK_PYTHON=/workspace/thesis-runtime/venv/bin/python
else
  TASK_PYTHON=python3
fi
export PYTHONPATH="$TASK_ROOT/backend${PYTHONPATH:+:$PYTHONPATH}"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
cd "$TASK_ROOT"
exec "$TASK_PYTHON" -m uvicorn trustxai.main:app --host "${TRUSTXAI_HOST:-127.0.0.1}" --port "${TRUSTXAI_PORT:-8000}"
