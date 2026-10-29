from copy import deepcopy

import pytest

from conftest import ScriptedModels, supported_score
from trustxai.checks import check_pair, structural_issues
from trustxai.domain import digest, evidence_template


def test_recorded_template_passes_structural_checks(evidence):
    assert structural_issues(evidence_template(evidence), evidence, evidence['input_sha256']) == []


def test_changed_case_cannot_reuse_another_cases_audit(evidence):
    altered = deepcopy(evidence)
    altered['options']['A'] = 'Different supplied diagnosis'
    issues = structural_issues(evidence_template(evidence), altered, evidence['input_sha256'])
    assert issues and any(item['code'] == 'case_binding' for item in issues)


@pytest.mark.parametrize('tamper', [
    lambda e: e['spans'][0].update(start=1),
    lambda e: e['spans'][0].update(end=e['spans'][0]['end'] - 1),
    lambda e: e['spans'][0].update(id='S99'),
    lambda e: e.update(case_text='Altered source text that does not match the span records.'),
    lambda e: e['decision'].update(modified_input_sha256='bad-original-input'),
    lambda e: e['decision'].update(name=e['options']['B']),
    lambda e: e['omissions'][0].update(modified_input_sha256=e['input_sha256']),
    lambda e: e['omissions'][0].update(removed_characters=1),
    lambda e: e['omissions'][1].update(removed_characters=1),
    lambda e: e['omissions'][0].update(changed=False),
    lambda e: e['recheck'].update(modified_input_sha256=e['input_sha256']),
    lambda e: e['decision'].update(model_signature_sha256='other-model'),
    lambda e: e['omissions'][0].update(model_signature_sha256='other-model'),
    lambda e: e['recheck'].update(model_signature_sha256='other-model'),
    lambda e: e.update(target_signature_sha256='other-model'),
    lambda e: e['target'].update(revision='other-revision'),
    lambda e: e['selected'].update(span_id='S99'),
    lambda e: e['selected'].update(label='D', name=e['options']['D']),
], ids=[
    'span-start', 'span-end', 'span-id', 'source-text', 'original-input-hash',
    'diagnosis-name', 'omitted-input-hash', 'removed-character-count', 'unselected-removed-count', 'changed-flag',
    'recheck-input-hash', 'original-model', 'omission-model', 'recheck-model',
    'target-signature', 'target-revision', 'selected-span', 'selected-result',
])
def test_tampered_behavior_records_are_unreleasable(evidence, tamper):
    original_pair = evidence_template(evidence)
    altered = deepcopy(evidence)
    # JSON round-trip reflects database records: selected is a snapshot, not an alias.
    import json
    altered = json.loads(json.dumps(altered))
    tamper(altered)
    issues = structural_issues(original_pair, altered, evidence['input_sha256'])
    assert issues, 'The evidence identity must be checked before rendered claims are considered'


def test_expected_model_signature_is_independent_of_untrusted_record(evidence):
    altered = deepcopy(evidence)
    altered['target']['revision'] = 'substituted-model'
    signature = digest(altered['target'])
    altered['target_signature_sha256'] = signature
    for item in [altered['decision'], *altered['omissions'], altered['selected'], altered['recheck']]:
        item['model_signature_sha256'] = signature
    issues = structural_issues(
        evidence_template(evidence), altered, evidence['input_sha256'],
        expected_target_signature=digest(ScriptedModels.target_identity),
    )
    assert issues


def test_repeated_source_findings_still_require_contiguous_exact_offsets(case_payload):
    from trustxai.domain import CaseInput, prepare_case
    from trustxai.pipeline import Pipeline
    prepared = prepare_case(CaseInput(**{
        **case_payload,
        'case_text': 'The adult reports cough and fever for three days. ' * 3,
    }))
    evidence = Pipeline(ScriptedModels()).analyze(prepared, lambda _: None, condition='B4')['evidence']
    pair = evidence_template(evidence)
    # The two findings contain identical characters, but identify different occurrences.
    assert evidence['spans'][0]['text'] == evidence['spans'][1]['text']
    evidence['spans'][1].update(start=evidence['spans'][0]['start'], end=evidence['spans'][0]['end'])
    assert structural_issues(pair, evidence, prepared['input_sha256'])


def test_count_corruption_is_rejected_even_if_mock_nli_says_entails(evidence):
    pair = evidence_template(evidence)
    pair['novice']['C3'] = pair['novice']['C3'].replace('3 of 3', '8 of 3')
    report = check_pair(pair, evidence, evidence['input_sha256'], lambda pairs: [supported_score() for _ in pairs])
    assert not report['passed']
    assert any(item['code'] == 'count_binding' for item in report['issues'])


def test_unsupported_extra_clause_is_sent_for_its_own_support_check(evidence):
    pair = evidence_template(evidence)
    pair['expert']['C2'] += ' Emergency surgery is required.'
    inspected = []

    def scripted_nli(pairs):
        inspected.extend(pairs)
        return [
            {'status': 'scored', 'entailment': 0.01} if 'Emergency surgery' in hypothesis else supported_score()
            for _, hypothesis in pairs
        ]

    report = check_pair(pair, evidence, evidence['input_sha256'], scripted_nli)
    assert any(hypothesis == 'Emergency surgery is required.' for _, hypothesis in inspected)
    assert not report['passed']
    assert any(item['claim'] == 'C2' and item['code'] == 'nli_not_entailed' for item in report['issues'])


@pytest.mark.parametrize('response', [[], [supported_score()], [supported_score()] * 100])
def test_checker_requires_one_score_for_every_requested_pair(evidence, response):
    report = check_pair(evidence_template(evidence), evidence, evidence['input_sha256'], lambda _: response)
    assert not report['passed']
    assert report['issues']


def test_context_overflow_or_missing_semantic_score_is_unresolved(evidence):
    report = check_pair(evidence_template(evidence), evidence, evidence['input_sha256'],
                        lambda pairs: [{'status': 'unresolved', 'reason': 'over context'} for _ in pairs])
    assert not report['passed']
    assert all(item['code'] == 'nli_unresolved' for item in report['issues'])
    assert report['independent_semantic_validation'] is False


def test_invalid_schema_does_not_call_nli(evidence):
    def must_not_score(_):
        raise AssertionError('Malformed views must fail before any model call')
    report = check_pair({'novice': {'C1': 'Partial view'}}, evidence, evidence['input_sha256'], must_not_score)
    assert not report['passed']
    assert any(item['code'] == 'invalid_schema' for item in report['issues'])


def test_unsupported_confidence_has_a_deterministic_failure(evidence):
    pair = evidence_template(evidence)
    pair['novice']['C1'] += ' The diagnosis has 98% confidence.'
    report = check_pair(pair, evidence, evidence['input_sha256'], lambda pairs: [supported_score() for _ in pairs])
    assert not report['passed']
    assert any(item['code'] == 'unsupported_certainty' for item in report['issues'])
