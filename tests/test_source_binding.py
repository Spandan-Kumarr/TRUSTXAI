from copy import deepcopy
import json

import pytest

from conftest import ScriptedModels
from trustxai.domain import CaseInput, digest, evidence_template
from trustxai.checks import structural_issues
from trustxai.pipeline import Pipeline
from trustxai import sources


@pytest.fixture
def public_row(case_payload, prepared, monkeypatch):
    # The frozen benchmark has a different span plan from automatic sentence splitting.
    contexts = [prepared['spans'][0]['text'] + prepared['spans'][1]['text'], prepared['spans'][2]['text']]
    row = {
        'source_id': 'medqa-feasibility-unit-001',
        'question': case_payload['question'],
        'contexts': contexts,
        'options': deepcopy(case_payload['options']),
        'original_question_sha256': digest('original benchmark question'),
        'input_sha256': digest({'question': case_payload['question'], 'contexts': contexts,
                                'options': case_payload['options']}),
        'answer_idx': 'D',
        'answer': 'A deliberately hidden evaluation label',
    }
    monkeypatch.setattr(sources, 'public_case_rows', lambda: [deepcopy(row)])
    return row


def source_payload(row):
    return CaseInput(case_text=''.join(row['contexts']).strip(), question=row['question'],
                     options=row['options'], source_id=row['source_id'])


def test_exact_public_case_retains_original_span_plan_and_input_identity(public_row):
    prepared = sources.prepare_bound_case(source_payload(public_row))
    assert [span['text'] for span in prepared['spans']] == public_row['contexts']
    assert [span['id'] for span in prepared['spans']] == ['S1', 'S2']
    assert prepared['case_text'] == ''.join(public_row['contexts'])
    assert prepared['input_sha256'] == public_row['input_sha256']
    assert prepared['source']['category'] == 'public_benchmark'
    assert prepared['source']['id'] == public_row['source_id']
    assert prepared['source']['original_question_sha256'] == public_row['original_question_sha256']
    assert not {'answer', 'answer_idx'} & set(prepared)
    assert 'deliberately hidden' not in str(prepared)
    models = ScriptedModels(labels={None: 'A', 'S1': 'B', 'S2': 'A'})
    result = Pipeline(models).analyze(prepared, lambda _: None, condition='B4')
    assert structural_issues(evidence_template(result['evidence']), result['evidence'], prepared['input_sha256']) == []


@pytest.mark.parametrize('field,value', [
    ('case_text', 'The adult now has four days of cough and fever. A new distinct clinical finding is also reported.'),
    ('question', 'What diagnosis is most likely?'),
    ('options', {'A': 'Altered candidate diagnosis', 'B': 'Acute asthma exacerbation',
                 'C': 'Pulmonary embolism', 'D': 'Acute heart failure'}),
])
def test_edited_public_content_cannot_retain_its_original_source_id(public_row, field, value):
    payload = source_payload(public_row).model_dump()
    payload[field] = value
    with pytest.raises(ValueError, match='source case was edited'):
        sources.prepare_bound_case(CaseInput(**payload))


def test_edited_case_becomes_valid_after_clearing_public_attribution(public_row):
    payload = source_payload(public_row).model_dump()
    payload.update(source_id=None, case_text=payload['case_text'].replace('three days', 'four days'))
    prepared = sources.prepare_bound_case(CaseInput(**payload))
    assert prepared['source']['category'] == 'user_provided'
    assert prepared['input_sha256'] != public_row['input_sha256']


def test_unknown_source_cannot_claim_public_or_synthetic_provenance(case_payload, monkeypatch):
    monkeypatch.setattr(sources, 'public_case_rows', lambda: [])
    for identifier in ('medqa-invented', 'synthetic-invented'):
        with pytest.raises(ValueError, match='Unrecognized source'):
            sources.prepare_bound_case(CaseInput(**{**case_payload, 'source_id': identifier}))


def test_corrupted_public_snapshot_cannot_reuse_its_recorded_input_hash(public_row):
    public_row['input_sha256'] = 'digest-from-a-different-source'
    with pytest.raises(ValueError, match='no longer matches'):
        sources.prepare_bound_case(source_payload(public_row))


def test_public_example_projection_does_not_expose_gold_fields(public_row):
    example = next(item for item in sources.examples() if item['id'] == public_row['source_id'])
    assert not {'answer', 'answer_idx', 'gold'} & set(example)
    assert 'deliberately hidden' not in json.dumps(example)
    assert example['source_id'] == public_row['source_id']


def test_whitespace_equivalent_public_input_uses_canonical_query_identity(public_row):
    payload = source_payload(public_row).model_dump()
    payload['question'] = payload['question'].replace('is the', 'is   the')
    payload['case_text'] = payload['case_text'].replace('cough and', 'cough   and')
    prepared = sources.prepare_bound_case(CaseInput(**payload))
    # If equivalent display whitespace is accepted, inference must use the frozen query.
    assert prepared['question'] == public_row['question']
    assert prepared['input_sha256'] == digest({
        'question': prepared['question'],
        'contexts': [span['text'] for span in prepared['spans']],
        'options': prepared['options'],
    })
