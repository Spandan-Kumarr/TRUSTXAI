"""Pinned, local-only inference. One worker owns all model objects."""
import ctypes
import gc
import hashlib
import json
import resource
import time
from pathlib import Path
from .config import RESEARCH, TARGET_CONTEXT, NATIVE_CONTEXT, MODEL_MEMORY_GIB
from .domain import LETTERS, digest


class LocalModels:
    def __init__(self):
        self.manifests = json.loads((RESEARCH.parent / 'evidence/MODEL_REVISIONS.json').read_text())
        self.native_info = json.loads((RESEARCH / 'evidence/NATIVE_COMMUNICATION_MODEL.json').read_text())
        self.prompt = json.loads((RESEARCH / 'CLASSIFICATION_PROMPT.json').read_text())
        self.target = self.target_tok = self.generator = self.generator_tok = self.nli = self.nli_tok = None
        self.torch_initialized = False
        self.phase = 'idle'

    @property
    def target_identity(self):
        meta = self.manifests['Qwen/Qwen3-4B-Instruct-2507']
        return {'model': 'Qwen/Qwen3-4B-Instruct-2507', 'revision': meta['revision'],
                'dtype': 'float32', 'threads': 4, 'enable_thinking': False, 'max_new_tokens': 8,
                'prompt_sha256': hashlib.sha256((RESEARCH / 'CLASSIFICATION_PROMPT.json').read_bytes()).hexdigest(),
                'decoding': 'greedy; strict A-D; fresh full query; no decision retry'}

    @property
    def communicator_identity(self):
        return {'model': self.native_info['model'], 'revision': self.native_info['revision'],
                'sha256': self.native_info['sha256'], 'backend': 'llama-cpp-python 0.3.16',
                'quantization': 'Q8_0', 'threads_decode': 2, 'threads_prefill': 4,
                'context_tokens': NATIVE_CONTEXT, 'enable_thinking': False, 'temperature': 0,
                'repeat_penalty': 1}

    def available(self):
        target = self.manifests['Qwen/Qwen3-4B-Instruct-2507']
        checker = self.manifests['cross-encoder/nli-deberta-v3-base']
        checks = {'target': all((Path(target['local_path']) / f['name']).exists() for f in target['files']),
                  'communicator': Path(self.native_info['local_path']).exists(),
                  'checker': (Path(checker['local_path']) / 'model.safetensors').exists()}
        return {'ready': all(checks.values()), 'assets': checks, 'phase': self.phase,
                'target': self.target_identity, 'communicator': self.communicator_identity,
                'device': 'CPU', 'integrity_basis': 'Previously verified pinned setup manifests'}

    def _torch(self):
        import torch
        if not self.torch_initialized:
            torch.set_num_threads(4)
            torch.set_num_interop_threads(1)
            self.torch_initialized = True
        return torch

    @staticmethod
    def _trim():
        gc.collect()
        try:
            ctypes.CDLL('libc.so.6').malloc_trim(0)
        except OSError:
            pass

    def release_communication(self):
        if self.generator is not None:
            self.generator.close()
        self.generator = self.nli = None
        self._trim()

    def release_target(self):
        self.target = None
        self._trim()

    def _memory_check(self):
        import psutil
        if psutil.Process().memory_info().rss / 2**30 > MODEL_MEMORY_GIB:
            raise RuntimeError('The configured 24 GiB inference memory budget was exceeded')

    def load_target(self):
        if self.target is not None:
            return
        self.phase = 'loading target'
        self.release_communication()
        torch = self._torch()
        from transformers import AutoModelForCausalLM, AutoTokenizer
        path = self.manifests['Qwen/Qwen3-4B-Instruct-2507']['local_path']
        self.target_tok = AutoTokenizer.from_pretrained(path, local_files_only=True, trust_remote_code=False)
        self.target = AutoModelForCausalLM.from_pretrained(path, local_files_only=True,
                        trust_remote_code=False, use_safetensors=True, dtype=torch.float32,
                        attn_implementation='sdpa').eval()
        self._memory_check()

    def classify(self, prepared, omitted=None):
        self.load_target()
        self.phase = 'diagnostic target'
        torch = self._torch()
        context = '\n\n'.join(f"[{span['id']}] {span['text']}" for span in prepared['spans'] if span['id'] != omitted)
        user = self.prompt['user_template'].format(question=prepared['question'], context=context,
                    options='\n'.join(f'{key}: {value}' for key, value in prepared['options'].items()))
        messages = [{'role': 'system', 'content': self.prompt['system']}, {'role': 'user', 'content': user}]
        inputs = self.target_tok.apply_chat_template(messages, tokenize=True, add_generation_prompt=True,
                        return_tensors='pt', return_dict=True, enable_thinking=False)
        n = inputs['input_ids'].shape[-1]
        if n > TARGET_CONTEXT:
            raise ValueError(f'The case uses {n} target tokens; the local limit is {TARGET_CONTEXT}. Shorten the case or options; no text was truncated.')
        start, cpu = time.perf_counter(), time.process_time()
        with torch.inference_mode():
            out = self.target.generate(**inputs, max_new_tokens=8, do_sample=False, temperature=None,
                    top_p=None, top_k=None, pad_token_id=self.target_tok.eos_token_id)
        text = self.target_tok.decode(out[0, n:], skip_special_tokens=True)
        label = text.strip().upper()
        label = label if label in LETTERS else 'invalid'
        return {'label': label, 'name': prepared['options'].get(label), 'raw': text,
                'seconds': time.perf_counter()-start, 'CPU_seconds': time.process_time()-cpu,
                'prompt_tokens': n, 'new_tokens': len(out[0, n:]),
                'modified_input_sha256': digest({'question': prepared['question'],
                    'contexts': [span['text'] for span in prepared['spans'] if span['id'] != omitted],
                    'options': prepared['options']})}

    def load_generator(self):
        self.release_target()
        if self.generator is not None:
            return
        self.phase = 'loading communicator'
        from llama_cpp import Llama
        from transformers import AutoTokenizer
        tokenizer = self.manifests['Qwen/Qwen3-1.7B']
        path = tokenizer.get('tokenizer_local_path', tokenizer['local_path'])
        self.generator_tok = AutoTokenizer.from_pretrained(path, local_files_only=True, trust_remote_code=False)
        self.generator = Llama(model_path=self.native_info['local_path'], n_ctx=NATIVE_CONTEXT,
                    n_threads=2, n_threads_batch=4, n_gpu_layers=0, seed=20261027, verbose=False)
        self._memory_check()

    def generate(self, system, user, cap=384):
        self.load_generator()
        self.phase = 'grounded generation'
        text = self.generator_tok.apply_chat_template([{'role': 'system', 'content': system},
                    {'role': 'user', 'content': user}], tokenize=False, add_generation_prompt=True, enable_thinking=False)
        ids = self.generator_tok.encode(text, add_special_tokens=False)
        if ids != self.generator.tokenize(text.encode(), add_bos=False, special=True):
            raise RuntimeError('Native and reference tokenizers disagree')
        if len(ids)+cap > NATIVE_CONTEXT:
            raise ValueError('Grounded response exceeds the configured context budget; no truncation was applied')
        self.generator.reset()
        start, cpu = time.perf_counter(), time.process_time()
        result = self.generator.create_completion(prompt=ids, max_tokens=cap, temperature=0,
                    top_p=1, top_k=0, repeat_penalty=1, seed=20261027)
        return {'text': result['choices'][0]['text'], 'seconds': time.perf_counter()-start,
                'CPU_seconds': time.process_time()-cpu, 'prompt_tokens': len(ids),
                'new_tokens': result['usage']['completion_tokens'],
                'finish_reason': result['choices'][0]['finish_reason']}

    def load_nli(self):
        if self.nli is not None:
            return
        self.release_target()
        self.phase = 'loading checker'
        torch = self._torch()
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        path = self.manifests['cross-encoder/nli-deberta-v3-base']['local_path']
        self.nli_tok = AutoTokenizer.from_pretrained(path, local_files_only=True)
        self.nli = AutoModelForSequenceClassification.from_pretrained(path, local_files_only=True,
                    trust_remote_code=False, use_safetensors=True, dtype=torch.float32).eval()
        labels = {int(key): value.lower() for key, value in self.nli.config.id2label.items()}
        if set(labels.values()) != {'contradiction', 'entailment', 'neutral'}:
            raise RuntimeError('Unrecognized checker label mapping')
        self.nli_labels = labels
        self._memory_check()

    def score_pairs(self, pairs):
        """Exact-token cache; case binding is always checked outside this function."""
        from . import store
        self.load_nli()
        self.phase = 'checking evidence support'
        torch = self._torch()
        signature = {'revision': self.manifests['cross-encoder/nli-deberta-v3-base']['revision'],
                     'dtype': 'float32', 'torch': torch.__version__,
                     'CPU': torch.backends.cpu.get_cpu_capability()}
        outputs, pending = [None]*len(pairs), []
        for index, (premise, hypothesis) in enumerate(pairs):
            encoded = dict(self.nli_tok(premise, hypothesis, truncation=False))
            if len(encoded['input_ids']) > 512:
                outputs[index] = {'status': 'unresolved', 'reason': 'Checker context exceeds 512 tokens'}
                continue
            key = digest([signature, encoded])
            cached = store.cached_score(key)
            if cached:
                outputs[index] = dict(cached, cached=True)
            else:
                pending.append((index, key, encoded))
        for offset in range(0, len(pending), 8):
            batch = pending[offset:offset+8]
            inputs = self.nli_tok.pad([item[2] for item in batch], padding=True, return_tensors='pt')
            with torch.inference_mode():
                probs = self.nli(**inputs).logits.float().softmax(-1).tolist()
            values = []
            for (index, key, _), row in zip(batch, probs):
                scores = {'status': 'scored', **{self.nli_labels[j]: float(row[j]) for j in range(3)}}
                outputs[index] = dict(scores, cached=False)
                values.append((key, scores))
            store.save_scores(values)
        return outputs

    def memory(self):
        return {'peak_process_RSS_GiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/(1024**2),
                'residency': 'Target released before communicator/checker phase'}
