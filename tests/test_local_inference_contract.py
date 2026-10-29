"""Exercise inference adapters with tiny protocol objects, never model weights."""
from contextlib import nullcontext
from types import SimpleNamespace

from conftest import query_hash
from trustxai.models import LocalModels


def test_research_identity_is_unchanged_and_mac_profile_is_explicit():
    model = LocalModels()
    assert model.profile == 'research_cpu_fp32'
    assert model.target_identity['dtype'] == 'float32'
    assert 'runtime_profile' not in model.target_identity
    assert 'runtime_profile' not in model.communicator_identity

    model.profile = 'mac16_mps_fp16'
    assert model.target_identity['dtype'] == 'float16'
    assert model.target_identity['device'] == 'Apple MPS'
    assert model.target_identity['runtime_profile'] == 'mac16_mps_fp16'
    assert model.communicator_identity['device'] == 'Metal'


def test_portable_runtime_layout_overrides_recorded_cloud_paths(tmp_path, monkeypatch):
    import trustxai.models as models_module

    monkeypatch.setattr(models_module, 'RUNTIME', tmp_path)
    model = LocalModels()
    target = model.manifests['Qwen/Qwen3-4B-Instruct-2507']
    target_dir = tmp_path / 'models/Qwen3-4B-Instruct-2507' / target['revision']
    target_dir.mkdir(parents=True)
    for record in target['files']:
        (target_dir / record['name']).touch()

    communicator = tmp_path / 'models/Qwen3-1.7B-GGUF' / model.native_info['revision'] / model.native_info['file']
    communicator.parent.mkdir(parents=True)
    communicator.touch()

    tokenizer = model.manifests['Qwen/Qwen3-1.7B']
    tokenizer_dir = tmp_path / 'models/Qwen3-1.7B' / tokenizer['revision']
    tokenizer_dir.mkdir(parents=True)
    (tokenizer_dir / 'tokenizer.json').touch()

    checker = model.manifests['cross-encoder/nli-deberta-v3-base']
    checker_dir = tmp_path / 'models/nli-deberta-v3-base' / checker['revision']
    checker_dir.mkdir(parents=True)
    (checker_dir / 'model.safetensors').touch()

    status = model.available()
    assert status['ready'] is True
    assert all(status['assets'].values())
    assert model._target_path() == target_dir
    assert model._communicator_path() == communicator
    assert model._communicator_tokenizer_path() == tokenizer_dir
    assert model._checker_path() == checker_dir


class OutputTokens:
    def __getitem__(self, key):
        assert key[0] == 0 and isinstance(key[1], slice)
        return [42]


class FakeTargetTokenizer:
    eos_token_id = 0

    def __init__(self, outputs):
        self.outputs = iter(outputs)
        self.messages = []

    def apply_chat_template(self, messages, **kwargs):
        self.messages.append((messages, kwargs))
        return {'input_ids': SimpleNamespace(shape=(1, 32))}

    def decode(self, tokens, **kwargs):
        return next(self.outputs)


class FakeTarget:
    def __init__(self):
        self.calls = []

    def generate(self, **kwargs):
        self.calls.append(kwargs)
        return OutputTokens()


def tiny_target(outputs):
    model = LocalModels.__new__(LocalModels)
    model.prompt = {'system': 'Choose exactly one diagnosis letter.',
                    'user_template': '{question}\n{context}\n{options}'}
    model.load_target = lambda: None
    model._torch = lambda: SimpleNamespace(inference_mode=nullcontext)
    model.target_tok = FakeTargetTokenizer(outputs)
    model.target = FakeTarget()
    return model


def test_target_queries_are_fresh_and_modified_hashes_match_exact_contexts(prepared):
    model = tiny_target([' A\n', 'B', 'A'])
    original = model.classify(prepared)
    omitted = model.classify(prepared, omitted='S1')
    repeated_original = model.classify(prepared)
    calls = model.target_tok.messages
    assert calls[0][0] == calls[2][0]
    assert all(span['text'] in calls[0][0][1]['content'] for span in prepared['spans'])
    assert prepared['spans'][0]['text'] not in calls[1][0][1]['content']
    assert all(span['text'] in calls[1][0][1]['content'] for span in prepared['spans'][1:])
    assert original['modified_input_sha256'] == repeated_original['modified_input_sha256'] == prepared['input_sha256']
    assert omitted['modified_input_sha256'] == query_hash(prepared, 'S1')
    assert original['label'] == 'A' and omitted['label'] == 'B'
    assert len(model.target.calls) == 3
    assert all(call['do_sample'] is False and call['max_new_tokens'] == 8 for call in model.target.calls)
    assert all(kwargs['enable_thinking'] is False for _, kwargs in calls)


def test_unparseable_target_output_is_invalid_and_never_retried(prepared):
    model = tiny_target(['Answer: A'])
    result = model.classify(prepared)
    assert result['label'] == 'invalid'
    assert result['name'] is None
    assert result['raw'] == 'Answer: A'
    assert len(model.target.calls) == 1


def test_target_context_overflow_is_rejected_without_truncation(prepared):
    import pytest
    model = tiny_target(['A'])
    original_template = model.target_tok.apply_chat_template
    def over_budget(*args, **kwargs):
        original_template(*args, **kwargs)
        return {'input_ids': SimpleNamespace(shape=(1, 99999))}
    model.target_tok.apply_chat_template = over_budget
    with pytest.raises(ValueError, match='no text was truncated'):
        model.classify(prepared)
    assert model.target.calls == []


class FakeNliTokenizer:
    def __call__(self, premise, hypothesis, **kwargs):
        assert kwargs['truncation'] is False
        return {'input_ids': list(range(513 if premise == 'oversized' else 5)),
                'attention_mask': [1] * (513 if premise == 'oversized' else 5)}

    def pad(self, encoded, **kwargs):
        return {'encoded': encoded}


class FakeLogits:
    def __init__(self, size): self.size = size
    def float(self): return self
    def softmax(self, _): return self
    def tolist(self): return [[.01, .98, .01] for _ in range(self.size)]


class FakeNli:
    def __init__(self): self.calls = []
    def __call__(self, **inputs):
        self.calls.append(inputs)
        return SimpleNamespace(logits=FakeLogits(len(inputs['encoded'])))


def tiny_checker(monkeypatch):
    import trustxai.store as store
    cache = {}
    monkeypatch.setattr(store, 'cached_score', lambda key: cache.get(key))
    monkeypatch.setattr(store, 'save_scores', lambda values: cache.update(values))
    model = LocalModels.__new__(LocalModels)
    model.manifests = {'cross-encoder/nli-deberta-v3-base': {'revision': 'unit-checker'}}
    model.nli_labels = {0: 'contradiction', 1: 'entailment', 2: 'neutral'}
    model.nli_tok = FakeNliTokenizer()
    model.nli = FakeNli()
    model.load_nli = lambda: None
    model._torch = lambda: SimpleNamespace(
        __version__='unit-torch',
        backends=SimpleNamespace(cpu=SimpleNamespace(get_cpu_capability=lambda: 'unit-cpu')),
        inference_mode=nullcontext,
    )
    return model


def test_nli_context_overflow_is_unresolved_and_not_truncated(monkeypatch):
    model = tiny_checker(monkeypatch)
    scores = model.score_pairs([('oversized', 'claim')])
    assert scores[0]['status'] == 'unresolved'
    assert model.nli.calls == []


def test_exact_token_score_cache_is_bound_to_checker_revision(monkeypatch):
    model = tiny_checker(monkeypatch)
    first = model.score_pairs([('source', 'claim')])
    second = model.score_pairs([('source', 'claim')])
    assert first[0]['cached'] is False and second[0]['cached'] is True
    assert first[0]['entailment'] == second[0]['entailment'] == .98
    assert len(model.nli.calls) == 1
    model.manifests['cross-encoder/nli-deberta-v3-base']['revision'] = 'changed-checker-revision'
    third = model.score_pairs([('source', 'claim')])
    assert third[0]['cached'] is False
    assert len(model.nli.calls) == 2
