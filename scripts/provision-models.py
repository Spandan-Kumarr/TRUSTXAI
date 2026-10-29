"""Provision pinned public model artifacts into the portable runtime directory."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
from pathlib import Path

from huggingface_hub import hf_hub_download, snapshot_download


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = Path(os.environ.get('TRUSTXAI_RUNTIME', ROOT / '.trustxai-runtime')).expanduser()
EVIDENCE = ROOT / 'research/step-04'
MANIFESTS = json.loads((EVIDENCE / 'evidence/MODEL_REVISIONS.json').read_text())
SELECTED = json.loads((EVIDENCE / 'clinical-cdss/evidence/SELECTED_MODEL_ARTIFACTS.json').read_text())
NATIVE = SELECTED['communication']


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(4 * 1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def verify(folder: Path, records: list[dict], key: str = 'name') -> None:
    for record in records:
        path = folder / record[key]
        if not path.is_file():
            raise RuntimeError(f'Missing downloaded artifact: {path}')
        expected = record.get('sha256')
        if expected and sha256(path) != expected:
            raise RuntimeError(f'Publisher digest mismatch: {path.name}')


def main() -> None:
    if platform.system() != 'Darwin' or platform.machine() != 'arm64':
        raise SystemExit('This installer profile is for Apple Silicon macOS.')
    free = shutil.disk_usage(ROOT).free
    if free < 15 * 1024**3:
        raise SystemExit('At least 15 GiB free disk space is required for model provisioning.')

    target = MANIFESTS['Qwen/Qwen3-4B-Instruct-2507']
    target_dir = RUNTIME / 'models/Qwen3-4B-Instruct-2507' / target['revision']
    target_files = [record['name'] for record in target['files']]
    target_files += ['model.safetensors.index.json', 'config.json', 'generation_config.json',
                     'tokenizer_config.json', 'tokenizer.json', 'merges.txt', 'vocab.json']
    print('Downloading the pinned diagnostic target (about 8 GB)...', flush=True)
    snapshot_download('Qwen/Qwen3-4B-Instruct-2507', revision=target['revision'],
                      local_dir=target_dir, allow_patterns=target_files)
    verify(target_dir, target['files'])

    tokenizer = SELECTED['communication_tokenizer']
    tokenizer_dir = RUNTIME / 'models/Qwen3-1.7B' / tokenizer['revision']
    tokenizer_files = [record['file'] for record in tokenizer['files']]
    print('Downloading the pinned communication tokenizer...', flush=True)
    snapshot_download(tokenizer['model'], revision=tokenizer['revision'],
                      local_dir=tokenizer_dir, allow_patterns=tokenizer_files)
    verify(tokenizer_dir, tokenizer['files'], key='file')

    communicator_dir = RUNTIME / 'models/Qwen3-1.7B-GGUF' / NATIVE['revision']
    print('Downloading the pinned explanation model (about 1.8 GB)...', flush=True)
    communicator = Path(hf_hub_download(NATIVE['model'], revision=NATIVE['revision'],
                        filename=NATIVE['file'], local_dir=communicator_dir))
    if sha256(communicator) != NATIVE['sha256']:
        raise RuntimeError('Publisher digest mismatch for the explanation model')

    checker = MANIFESTS['cross-encoder/nli-deberta-v3-base']
    checker_dir = RUNTIME / 'models/nli-deberta-v3-base' / checker['revision']
    checker_files = [record['name'] for record in checker['files']]
    print('Downloading the pinned explanation checker (about 0.75 GB)...', flush=True)
    snapshot_download('cross-encoder/nli-deberta-v3-base', revision=checker['revision'],
                      local_dir=checker_dir, allow_patterns=checker_files)
    verify(checker_dir, checker['files'])

    RUNTIME.mkdir(parents=True, exist_ok=True)
    (RUNTIME / 'profile').write_text('mac16_mps_fp16\n')
    record = {'profile': 'mac16_mps_fp16', 'platform': platform.platform(),
              'target_revision': target['revision'], 'communicator_revision': NATIVE['revision'],
              'checker_revision': checker['revision'],
              'research_result_compatible': False,
              'note': 'Local Apple FP16/MPS demo; frozen thesis measurements use CPU FP32.'}
    (RUNTIME / 'provisioning.json').write_text(json.dumps(record, indent=2) + '\n')
    print('Pinned model assets verified. The Mac 16 GB local-demo profile is ready.', flush=True)


if __name__ == '__main__':
    main()
