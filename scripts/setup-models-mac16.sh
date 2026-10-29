#!/usr/bin/env bash
set -euo pipefail

TASK_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
TASK_PYTHON="$TASK_ROOT/.venv/bin/python"

if [[ "$(uname -s)" != Darwin || "$(uname -m)" != arm64 ]]; then
  echo "This installer is only for Apple Silicon macOS." >&2
  exit 1
fi
if [[ ! -x "$TASK_PYTHON" ]]; then
  echo "Run scripts/setup-local.sh before installing the model profile." >&2
  exit 1
fi
if ! command -v cmake >/dev/null 2>&1; then
  echo "CMake is required. Run: brew install cmake" >&2
  exit 1
fi

"$TASK_PYTHON" -m pip install \
  'torch==2.8.0' \
  'transformers==4.57.1' \
  'huggingface-hub==0.36.0' \
  'accelerate>=1.4,<2' \
  'psutil==7.1.0' \
  'sentencepiece==0.2.1' \
  'protobuf==6.33.0' \
  'safetensors==0.6.2'

CMAKE_ARGS='-DGGML_METAL=on' FORCE_CMAKE=1 \
  "$TASK_PYTHON" -m pip install 'llama-cpp-python==0.3.16'

cd "$TASK_ROOT"
"$TASK_PYTHON" scripts/provision-models.py

cat <<'MESSAGE'
Mac 16 GB model setup is complete.

Start the application with:
  ./scripts/run.sh

This local FP16/MPS profile is for the interactive demo. The frozen thesis
measurements remain the recorded CPU FP32 research profile.
MESSAGE
