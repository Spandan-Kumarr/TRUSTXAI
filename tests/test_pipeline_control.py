import json

import pytest

from conftest import ScriptedModels, query_hash
from trustxai.domain import digest, evidence_template
from trustxai.pipeline import Cancelled, Pipeline


def test_fresh_decision_every_omission_and_selected_recheck_are_bound(prepared):
    models = ScriptedModels()
    result = Pipeline(models).analyze(prepared, lambda _: None)
    omitted_ids = [omitted for _, omitted in models.classifications]
    assert omitted_ids == [None, 'S1', 'S2', 'S3', 'S1']
    evidence = result['evidence']
    assert evidence['selected']['span_id'] == 'S1'
    assert evidence['decision']['label'] == 'A'
    assert evidence['recheck']['label'] == 'B'
    for record, omitted in zip([evidence['decision'], *evidence['omissions'], evidence['recheck']], omitted_ids):
        assert record['modified_input_sha256'] == query_hash(prepared, omitted)
        assert record['model_signature_sha256'] == digest(models.target_identity)
    assert result['input_sha256'] == prepared['input_sha256']
    assert result['clinical_validation'] == 'not established'


def test_proposed_method_allows_one_repair_and_releases_corrected_pair(prepared):
    models = ScriptedModels(drafts=['count_corruption', 'valid'])
    result = Pipeline(models).analyze(prepared, lambda _: None)
    assert len(models.generations) == 2
    assert len(result['attempts']) == 2
    assert not result['attempts'][0]['checks']['passed']
    assert result['attempts'][1]['checks']['passed']
    assert result['release_status'] == 'generated'
    assert result['automated_release_passed'] is True
    assert 'count_binding' in models.generations[1]['user']


def test_two_failed_drafts_fall_back_without_third_generation(prepared):
    models = ScriptedModels(drafts=['count_corruption', 'count_corruption', 'valid'])
    result = Pipeline(models).analyze(prepared, lambda _: None)
    assert len(models.generations) == 2
    assert len(result['attempts']) == 2
    assert result['release_status'] == 'evidence_template'
    assert result['automated_release_passed'] is False
    assert result['views'] == evidence_template(result['evidence'])


def test_malformed_json_is_repaired_once_then_template(prepared):
    models = ScriptedModels(drafts=['not JSON', 'still not JSON'])
    result = Pipeline(models).analyze(prepared, lambda _: None)
    assert len(models.generations) == 2
    assert result['release_status'] == 'evidence_template'
    assert result['views'] == evidence_template(result['evidence'])


def test_invalid_original_answer_never_creates_omission_claims(prepared):
    models = ScriptedModels(labels={None: 'invalid'})
    result = Pipeline(models).analyze(prepared, lambda _: None)
    assert [omitted for _, omitted in models.classifications] == [None]
    assert result['evidence']['omissions'] == []
    assert result['evidence']['selected'] is None
    assert result['evidence']['recheck'] is None
    assert result['informative_evidence'] is False
    assert result['release_status'] == 'evidence_template'
    assert models.generations == []
    assert 'No diagnosis is recorded' in result['views']['novice']['C1']


def test_disagreeing_recheck_prevents_generated_release(prepared):
    models = ScriptedModels(labels={None: 'A', 'S1': ['B', 'C'], 'S2': 'A', 'S3': 'A'})
    result = Pipeline(models).analyze(prepared, lambda _: None)
    assert result['informative_evidence'] is False
    assert result['release_status'] == 'evidence_template'
    assert models.generations == []
    assert 'did not agree' in result['views']['expert']['C3']


def test_template_condition_never_invokes_communication_or_nli(prepared):
    models = ScriptedModels()
    result = Pipeline(models).analyze(prepared, lambda _: None, condition='B4')
    assert models.generations == [] and models.scored_pairs == []
    assert result['release_status'] == 'evidence_template'


@pytest.mark.parametrize('condition', ['B0', 'B1', 'B2', 'B3'])
def test_research_baselines_do_not_use_the_proposed_inline_nli_gate(prepared, condition):
    def draft(system, user):
        if 'Critique' in system or 'critic' in system.lower():
            return json.dumps({'score0to1': 0.1, 'feedback': 'Make the wording clearer.'})
        # Baseline outputs are retained as measured, even when schema-valid text is unsupported.
        return json.dumps({audience: {f'C{i}': f'Unverified claim {i}.' for i in range(1, 5)}
                           for audience in ('novice', 'expert')})
    models = ScriptedModels(drafts=[draft, draft, draft])
    result = Pipeline(models).analyze(prepared, lambda _: None, condition=condition)
    assert models.scored_pairs == []
    assert result['automated_release_passed'] is False
    assert result['release_status'] == 'baseline_unchecked'
    assert len(models.generations) == {'B0': 1, 'B1': 2, 'B2': 2, 'B3': 3}[condition]
    assert result['views']['novice']['C1'] == 'Unverified claim 1.'


def test_generic_critic_acceptance_retains_initial_pair_without_repair(prepared):
    models = ScriptedModels(drafts=['valid', '{"score0to1":0.99,"feedback":"The fixed evidence is retained."}'])
    result = Pipeline(models).analyze(prepared, lambda _: None, condition='B3')
    assert len(models.generations) == 2
    assert len(result['attempts']) == 1
    assert models.scored_pairs == []
    assert result['release_status'] == 'baseline_unchecked'
    assert result['automated_release_passed'] is False
    assert result['views'] == json.loads(result['attempts'][0]['generation']['text'])


def test_cancellation_stops_before_initial_model_call(prepared):
    models = ScriptedModels()
    with pytest.raises(Cancelled):
        Pipeline(models).analyze(prepared, lambda _: None, cancelled=lambda: True)
    assert models.classifications == []


def test_cancellation_between_omissions_stops_remaining_work(prepared):
    models = ScriptedModels()
    def cancelled():
        return len(models.classifications) >= 2
    with pytest.raises(Cancelled):
        Pipeline(models).analyze(prepared, lambda _: None, cancelled=cancelled)
    assert [omitted for _, omitted in models.classifications] == [None, 'S1']
    assert models.generations == []
