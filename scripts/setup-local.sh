#!/usr/bin/env bash
set -euo pipefail

TASK_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
LOCAL_PYTHON="${TRUSTXAI_BOOTSTRAP_PYTHON:-python3}"

cd "$TASK_ROOT"
"$LOCAL_PYTHON" -m venv .venv
"$TASK_ROOT/.venv/bin/python" -m pip install --upgrade pip
"$TASK_ROOT/.venv/bin/python" -m pip install -r requirements-app.txt

cd "$TASK_ROOT/frontend"
npm ci
npm run build

cat <<'MESSAGE'
Local API/UI environment is ready.

Start it with:
  ./scripts/run.sh

Then open:
  http://127.0.0.1:8000

The interface and API can start without model weights. Diagnostic inference
remains unavailable until the pinned local model assets are provisioned.
MESSAGE
