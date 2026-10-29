#!/usr/bin/env bash
set -euo pipefail
TASK_RUNTIME=/workspace/thesis-runtime
TASK_SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export UV_CACHE_DIR="$TASK_RUNTIME/cache/uv"
export UV_SYSTEM_CERTS=true
export HF_HOME="$TASK_RUNTIME/cache/huggingface"
mkdir -p "$TASK_RUNTIME" "$UV_CACHE_DIR" "$HF_HOME"
if [ ! -x "$TASK_RUNTIME/venv/bin/python" ]; then
  uv venv --python python3 "$TASK_RUNTIME/venv"
fi
uv pip install --python "$TASK_RUNTIME/venv/bin/python" --index-url https://download.pytorch.org/whl/cpu 'torch==2.8.0+cpu'
rg -v '^torch==' "$TASK_SCRIPT_DIR/evidence/CPU_DEPENDENCIES.freeze.txt" > "$TASK_RUNTIME/non_torch_requirements.txt"
uv pip install --python "$TASK_RUNTIME/venv/bin/python" -r "$TASK_RUNTIME/non_torch_requirements.txt"
uv pip check --python "$TASK_RUNTIME/venv/bin/python"
"$TASK_RUNTIME/venv/bin/python" -c 'import torch, transformers; from transformers import Qwen2ForCausalLM, AutoModelForSequenceClassification; print("CPU architecture imports passed; model weights and inference remain separate checks.")'
