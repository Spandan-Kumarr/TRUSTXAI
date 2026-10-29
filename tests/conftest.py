"""Lightweight fixtures: these tests never instantiate or load model weights."""
from copy import deepcopy
import json

import pytest

from trustxai.domain import CaseInput, digest, prepare_case


@pytest.fixture
def case_payload():
    return {
        'case_text': (
            'The adult reports three days of cough and fever. '
            'Examination reveals focal crackles over the right lower lung. '
            'A chest image shows a new air space opacity.'
        ),
        'question': 'Which of the following is the most likely diagnosis?',
        'options': {
            'A': 'Community-acquired pneumonia',
            'B': 'Acute asthma exacerbation',
            'C': 'Pulmonary embolism',
            'D': 'Acute heart failure',
        },
        'source_id': None,
    }


@pytest.fixture
def prepared(case_payload):
    return prepare_case(CaseInput(**case_payload))


def query_hash(prepared, omitted=None):
    return digest({
        'question': prepared['question'],
        'contexts': [span['text'] for span in prepared['spans'] if span['id'] != omitted],
        'options': prepared['options'],
    })


class ScriptedModels:
    """Deterministic protocol fake for control flow, never a semantic evaluator."""
    target_identity = {'model': 'test-target', 'revision': 'unit-revision', 'decoding': 'greedy'}
    communicator_identity = {'model': 'test-communicator', 'revision': 'unit-revision'}

    def __init__(self, drafts=None, labels=None, scorer=None):
        self.drafts = list(drafts or ['valid'])
        self.labels = labels or {None: 'A', 'S1': 'B', 'S2': 'A', 'S3': 'A'}
        self.scorer = scorer
        self.classifications = []
        self.generations = []
        self.scored_pairs = []

    def classify(self, prepared, omitted=None):
        self.classifications.append((deepcopy(prepared), omitted))
        label = self.labels[omitted]
        if isinstance(label, list):
            label = label.pop(0)
        return {
            'label': label,
            'name': prepared['options'].get(label),
            'raw': label,
            'modified_input_sha256': query_hash(prepared, omitted),
            'seconds': 0.001,
            'CPU_seconds': 0.001,
        }

    def generate(self, system, user, cap=384):
        self.generations.append({'system': system, 'user': user, 'cap': cap})
        script = self.drafts.pop(0) if self.drafts else 'valid'
        if callable(script):
            text = script(system, user)
        elif script in ('valid', 'count_corruption', 'unsupported_clause'):
            start = user.index('Canonical facts:\n') + len('Canonical facts:\n')
            facts = json.JSONDecoder().raw_decode(user[start:])[0]
            pair = {'novice': dict(facts), 'expert': dict(facts)}
            if script == 'count_corruption':
                pair['novice']['C3'] = pair['novice']['C3'].replace('3 of 3', '8 of 3')
            elif script == 'unsupported_clause':
                pair['expert']['C2'] += ' Emergency surgery is required.'
            text = json.dumps(pair)
        else:
            text = script
        return {'text': text, 'seconds': 0.001, 'CPU_seconds': 0.001,
                'prompt_tokens': 1, 'new_tokens': 1, 'finish_reason': 'stop'}

    def score_pairs(self, pairs):
        self.scored_pairs.extend(deepcopy(pairs))
        if self.scorer:
            return self.scorer(pairs)
        return [supported_score() for _ in pairs]

    def memory(self):
        return {'peak_process_RSS_GiB': 0.01, 'residency': 'scripted test fake'}


def supported_score():
    return {'status': 'scored', 'entailment': 0.99, 'neutral': 0.005, 'contradiction': 0.005}


@pytest.fixture
def evidence(prepared):
    from trustxai.pipeline import Pipeline
    return Pipeline(ScriptedModels()).analyze(prepared, lambda _: None, condition='B4')['evidence']


@pytest.fixture
def isolated_store(tmp_path, monkeypatch):
    from trustxai import store
    monkeypatch.setattr(store, 'APP_DATA', tmp_path)
    monkeypatch.setattr(store, 'DB_PATH', tmp_path / 'test.sqlite3')
    store.initialize()
    return store
