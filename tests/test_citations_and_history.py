from copy import deepcopy

import pytest

from conftest import ScriptedModels, supported_score
from trustxai.pipeline import Pipeline
from trustxai.sources import check_cited_answer, source_record


@pytest.fixture
def sources():
    return [source_record('test-source', 'Recorded source', 'https://example.test/reference',
                          'The original answer was option A. A recheck returned option B.')]


@pytest.mark.parametrize('answer', [
    'The original answer was A.',
    'The original answer was A [0].',
    'The original answer was A [2].',
    'The original answer was A [999].',
    'The original answer was A [1]. Emergency surgery is required.',
])
def test_fabricated_or_missing_citations_are_rejected_before_nli(sources, answer):
    def must_not_score(_):
        raise AssertionError('Invalid citations must fail before any NLI call')
    assert not check_cited_answer(answer, sources, must_not_score, .9)['passed']


def test_citation_after_punctuation_is_normalized_and_checked(sources):
    result = check_cited_answer('The original answer was A. [1]', sources,
                                lambda pairs: [supported_score() for _ in pairs], .9)
    assert result['passed']
    assert result['normalized_answer'] == 'The original answer was A [1].'


def test_real_citation_does_not_bypass_support_check(sources):
    result = check_cited_answer('Emergency surgery is required [1].', sources,
                                lambda pairs: [{'status': 'scored', 'entailment': .01} for _ in pairs], .9)
    assert not result['passed']


@pytest.mark.parametrize('response', [[], [supported_score()], [supported_score()] * 3])
def test_every_cited_sentence_needs_its_own_score(sources, response):
    result = check_cited_answer('The original answer was A [1]. A recheck returned B [1].',
                                sources, lambda _: response, .9)
    assert not result['passed']


def test_unmeasured_comparison_cannot_be_released_with_a_real_citation(sources):
    def must_not_score(_):
        raise AssertionError('Known unmeasured comparisons must fail structurally')
    result = check_cited_answer('TRUSTXAI is more accurate than GPT [1].', sources, must_not_score, .9)
    assert not result['passed']


def test_rejected_chat_draft_releases_retrieved_passages(monkeypatch, sources):
    import trustxai.pipeline as pipeline
    monkeypatch.setattr(pipeline, 'retrieve', lambda *_: sources)
    models = ScriptedModels(drafts=['{"answer":"Emergency surgery is required [999].","insufficient":false}'])
    reply = Pipeline(models).chat('What was the original answer?', [], None, lambda _: None)
    assert reply['grounding_status'] == 'source_passages'
    assert sources[0]['content'] in reply['text']
    assert 'Emergency surgery' not in reply['text']
    assert reply['checks']['passed'] is False


def test_cited_plain_prose_from_local_model_is_checked_in_full(monkeypatch, sources):
    import trustxai.pipeline as pipeline
    monkeypatch.setattr(pipeline, 'retrieve', lambda *_: sources)
    scored = []
    models = ScriptedModels(drafts=['The original answer was option A [1].'])
    def score(pairs):
        scored.extend(pairs)
        return [supported_score() for _ in pairs]
    models.score_pairs = score
    reply = Pipeline(models).chat('What was the original answer?', [], None, lambda _: None)
    assert reply['grounding_status'] == 'source_checked'
    assert reply['draft_format'] == 'plain_text'
    assert scored == [(sources[0]['content'], 'The original answer was option A .')]


@pytest.mark.parametrize('draft', [
    'The original answer was option A.',
    '{"answer":"The original answer was option A [1]."',
    '```json\n{"answer":"The original answer was option A [1].","insufficient":false}\n```',
])
def test_plain_text_support_does_not_recover_uncited_or_malformed_payloads(monkeypatch, sources, draft):
    import trustxai.pipeline as pipeline
    monkeypatch.setattr(pipeline, 'retrieve', lambda *_: sources)
    models = ScriptedModels(drafts=[draft])
    def must_not_score(_):
        raise AssertionError('Uncited or malformed responses must fail before NLI')
    models.score_pairs = must_not_score
    reply = Pipeline(models).chat('What was the original answer?', [], None, lambda _: None)
    assert reply['grounding_status'] == 'source_passages'


def test_chat_does_not_generate_when_retrieval_has_no_passages(monkeypatch):
    import trustxai.pipeline as pipeline
    monkeypatch.setattr(pipeline, 'retrieve', lambda *_: [])
    models = ScriptedModels()
    reply = Pipeline(models).chat('Question without supporting evidence', [], None, lambda _: None)
    assert reply['grounding_status'] == 'insufficient_sources'
    assert reply['citations'] == []
    assert models.generations == []


def test_followup_uses_previous_question_without_duplicating_current_or_promoting_history_to_evidence(monkeypatch, sources):
    import trustxai.pipeline as pipeline
    queries = []
    def retrieve(query, case):
        queries.append(query)
        return sources
    monkeypatch.setattr(pipeline, 'retrieve', retrieve)
    previous = 'What happened in the omission audit?'
    current = 'Was that the original answer?'
    history = [
        {'role':'user','payload':{'text':'x' * 1801}},
        {'role':'user','payload':{'text':previous}},
        {'role':'assistant','payload':{'text':'Untrusted previous assistant claim'}},
        {'role':'user','payload':{'text':current}},
    ]
    models = ScriptedModels(drafts=['The original answer was option A [1].'])
    reply = Pipeline(models).chat(current, history, None, lambda _: None)
    assert queries == [previous+' '+current]
    prompt = models.generations[0]['user']
    assert 'Earlier user questions (context only, not evidence)' in prompt
    assert previous in prompt and prompt.count(current) == 1
    assert 'Untrusted previous assistant claim' not in prompt and 'x' * 1801 not in prompt
    assert reply['checks']['passed']


def test_frozen_case_option_conflict_is_rejected_even_with_mock_support(monkeypatch, sources, evidence):
    import trustxai.pipeline as pipeline
    monkeypatch.setattr(pipeline, 'retrieve', lambda *_: sources)
    models = ScriptedModels(drafts=['{"answer":"The selected option is B [1].","insufficient":false}'])
    case = {'result': {'evidence': evidence}}
    reply = Pipeline(models).chat('What is the selected option?', [], case, lambda _: None)
    assert reply['grounding_status'] == 'source_passages'
    assert not reply['checks']['passed']


def test_case_edits_create_new_record_and_leave_original_result_unchanged(isolated_store, case_payload):
    store = isolated_store
    original = store.create_case(case_payload)
    original_result = {'decision': 'A', 'input_sha256': 'original-input'}
    store.update_case(original['id'], status='completed', result=original_result)
    snapshot = deepcopy(store.get_case(original['id']))
    edited_payload = {**case_payload, 'parent_id': original['id'],
                      'case_text': case_payload['case_text'].replace('three days', 'four days')}
    edited = store.create_case(edited_payload)
    assert original['id'] != edited['id']
    assert store.get_case(original['id']) == snapshot
    assert edited['input']['parent_id'] == original['id']
    assert edited['result'] is None


def test_reading_records_or_history_cannot_mutate_persisted_snapshots(isolated_store, case_payload):
    store = isolated_store
    case = store.create_case(case_payload)
    store.update_case(case['id'], status='completed', result={'views': {'novice': {'C1': 'Original'}}})
    store.add_message(case['id'], 'user', 'chat', {'text': 'Original question'})
    store.add_message(case['id'], 'assistant', 'chat', {'text': 'Original answer', 'citations': [{'id': 'source'}]})
    read_case = store.get_case(case['id'])
    read_case['input']['options']['A'] = 'Changed in memory'
    read_case['result']['views']['novice']['C1'] = 'Changed in memory'
    history = store.messages(case['id'])
    history[1]['payload']['citations'][0]['id'] = 'Changed in memory'
    assert store.get_case(case['id'])['input']['options'] == case_payload['options']
    assert store.get_case(case['id'])['result']['views']['novice']['C1'] == 'Original'
    assert store.messages(case['id'])[1]['payload']['citations'][0]['id'] == 'source'
    store.add_message(case['id'], 'user', 'chat', {'text': 'Follow-up question'})
    assert [m['payload']['text'] for m in store.messages(case['id'])] == [
        'Original question', 'Original answer', 'Follow-up question',
    ]


def test_deleted_case_is_absent_without_altering_other_case_history(isolated_store, case_payload):
    store = isolated_store
    first = store.create_case(case_payload)
    second = store.create_case(case_payload)
    store.add_message(second['id'], 'user', 'chat', {'text': 'Keep this history'})
    store.delete_case(first['id'])
    assert store.get_case(first['id']) is None
    assert [case['id'] for case in store.list_cases()] == [second['id']]
    assert store.messages(second['id'])[0]['payload']['text'] == 'Keep this history'
