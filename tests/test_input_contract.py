from copy import deepcopy

import pytest
from pydantic import ValidationError

from trustxai.domain import CaseInput, digest, prepare_case, segment_case


def test_gold_labels_and_external_explanations_never_enter_inference(case_payload):
    payload = {
        **case_payload,
        'answer': 'Secret gold diagnosis',
        'answer_idx': 'D',
        'gold': 'D',
        'explanation': 'Secret reference explanation',
        'long_answer': 'Secret conclusion',
    }
    case = CaseInput(**payload)
    assert not (set(payload) - set(case_payload)) & set(case.model_dump())
    prepared = prepare_case(case)
    serialized = str(prepared)
    assert 'Secret' not in serialized
    assert not {'answer', 'answer_idx', 'gold', 'explanation', 'long_answer'} & set(prepared)
    assert prepared['options'] == case_payload['options']


@pytest.mark.parametrize('options', [
    {'A': 'One', 'B': 'Two', 'C': 'Three'},
    {'A': 'One', 'B': 'Two', 'C': 'Three', 'D': 'Four', 'E': 'Five'},
    {'A': 'One', 'B': ' one ', 'C': 'Three', 'D': 'Four'},
    {'A': '', 'B': 'Two', 'C': 'Three', 'D': 'Four'},
])
def test_options_require_four_distinct_nonempty_candidates(case_payload, options):
    with pytest.raises(ValidationError):
        CaseInput(**{**case_payload, 'options': options})


@pytest.mark.parametrize('question', [
    'What treatment should be given next?',
    'Which is the most likely diagnosis and next step in treatment?',
    'Which test confirms the most likely diagnosis?',
    'What is the mechanism of the most likely diagnosis?',
])
def test_only_diagnosis_selection_is_accepted(case_payload, question):
    with pytest.raises(ValidationError):
        CaseInput(**{**case_payload, 'question': question})


def test_spans_preserve_all_exact_source_characters(case_payload):
    text = case_payload['case_text']
    spans = segment_case(text)
    assert len(spans) == 3
    assert ''.join(span['text'] for span in spans) == text
    assert [span['id'] for span in spans] == ['S1', 'S2', 'S3']
    assert spans[0]['start'] == 0 and spans[-1]['end'] == len(text)
    for prior, current in zip(spans, spans[1:]):
        assert prior['end'] == current['start']
    assert all(text[span['start']:span['end']] == span['text'] for span in spans)


def test_long_cases_bound_omissions_without_dropping_findings():
    text = ' '.join(f'This is recorded clinical finding number {index}.' for index in range(20))
    spans = segment_case(text)
    assert 2 <= len(spans) <= 8
    assert ''.join(span['text'] for span in spans) == text


def test_single_unsegmentable_finding_cannot_claim_an_omission_audit(case_payload):
    case = CaseInput(**{**case_payload, 'case_text': 'The adult has cough and fever with focal crackles over the right lower lung'})
    with pytest.raises(ValueError, match='at least two'):
        prepare_case(case)


def test_input_identity_covers_text_question_and_candidates(case_payload, prepared):
    assert prepared['input_sha256'] == digest({
        'question': prepared['question'],
        'contexts': [span['text'] for span in prepared['spans']],
        'options': prepared['options'],
    })
    for field, value in (
        ('case_text', case_payload['case_text'].replace('three days', 'four days')),
        ('question', 'What diagnosis is most likely?'),
        ('options', {**case_payload['options'], 'D': 'Another candidate diagnosis'}),
    ):
        edited = deepcopy(case_payload)
        edited[field] = value
        assert prepare_case(CaseInput(**edited))['input_sha256'] != prepared['input_sha256']


def test_display_metadata_does_not_change_inference_identity(case_payload, prepared):
    renamed = CaseInput(**{**case_payload, 'title': 'Different display title', 'source_id': 'other-provenance'})
    assert prepare_case(renamed)['input_sha256'] == prepared['input_sha256']
