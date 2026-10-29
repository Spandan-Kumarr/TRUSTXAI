"""Fallible automated release checks, not independent semantic ground truth."""
import re
from .config import NLI_THRESHOLD
from .domain import CLAIMS, LETTERS, canonical_facts, digest, evidence_available, valid_pair

WORDS = dict(zip(('zero','one','two','three','four','five','six','seven','eight'), range(9)))


def normalized(text):
    return ' '.join(re.findall(r'\w+', text.casefold()))


def numbers(text):
    text = re.sub(r'\bone[- ](?:span|segment)\b', 'individual-span', text, flags=re.I)
    return [int(token) if token.isdigit() else WORDS[token] for token in re.findall(r'\b\d+\b|\b(?:zero|one|two|three|four|five|six|seven|eight)\b', text.casefold())]


def sentence_parts(text):
    return [part.strip() for part in re.split(r'(?<=[.!?])\s+|;\s*', text) if part.strip()]


def structural_issues(pair, evidence, expected_input_sha, expected_target_signature=None):
    issues = []
    computed = digest({'question': evidence['question'], 'contexts': [span['text'] for span in evidence['spans']], 'options': evidence['options']})
    if evidence['input_sha256'] != expected_input_sha or computed != expected_input_sha:
        return [{'claim': 'record', 'code': 'case_binding', 'detail': 'Evidence does not match this immutable case'}]
    signature = evidence.get('target_signature_sha256')
    if not signature or digest(evidence.get('target')) != signature or (expected_target_signature and signature != expected_target_signature):
        issues.append({'claim': 'record', 'code': 'record_binding', 'detail': 'Target model signature is inconsistent'})
    spans = evidence['spans']
    source_text = evidence.get('case_text', '')
    if [span['id'] for span in spans] != [f'S{i+1}' for i in range(len(spans))]:
        issues.append({'claim': 'record', 'code': 'record_binding', 'detail': 'Source span identities are inconsistent'})
    contiguous = bool(spans) and spans[0]['start']==0 and spans[-1]['end']==len(source_text) and all(spans[i]['end']==spans[i+1]['start'] for i in range(len(spans)-1))
    if not contiguous or ''.join(span['text'] for span in spans) != source_text or any(source_text[span['start']:span['end']] != span['text'] for span in spans):
        issues.append({'claim': 'record', 'code': 'record_binding', 'detail': 'Source offsets/text are inconsistent'})
    expected_full = digest({'question': evidence['question'], 'contexts': [span['text'] for span in spans], 'options': evidence['options']})
    decision = evidence['decision']
    if decision.get('model_signature_sha256') != signature or decision.get('modified_input_sha256') != expected_full or (decision['label'] in LETTERS and decision.get('name') != evidence['options'][decision['label']]):
        issues.append({'claim': 'record', 'code': 'record_binding', 'detail': 'Original decision is not bound to this input/model'})
    span_ids = {span['id'] for span in spans}
    tests = evidence['omissions']
    if len({test['span_id'] for test in tests}) != len(tests):
        issues.append({'claim': 'record', 'code': 'record_binding', 'detail': 'Duplicate omission test identities'})
    for test in tests:
        expected_hash = digest({'question': evidence['question'], 'contexts': [span['text'] for span in spans if span['id'] != test['span_id']], 'options': evidence['options']})
        actual_changed = test['label'] in LETTERS and test['label'] != decision['label']
        if test['span_id'] not in span_ids or test.get('modified_input_sha256') != expected_hash or test.get('model_signature_sha256') != signature or test['changed'] != actual_changed or test.get('removed_characters') != next((len(span['text']) for span in spans if span['id'] == test['span_id']), None):
            issues.append({'claim': 'record', 'code': 'record_binding', 'detail': 'An omission observation has a wrong source/model binding'})
    selected, recheck = evidence.get('selected'), evidence.get('recheck')
    if selected and selected not in tests:
        issues.append({'claim': 'record', 'code': 'record_binding', 'detail': 'Selected observation is not a recorded test'})
    if selected and recheck and (recheck.get('modified_input_sha256') != selected.get('modified_input_sha256') or recheck.get('model_signature_sha256') != signature):
        issues.append({'claim': 'record', 'code': 'record_binding', 'detail': 'Selected-result recheck uses another input/model'})
    if not evidence_available(evidence):
        issues.append({'claim': 'record', 'code': 'insufficient_evidence', 'detail': 'A valid decision, tested omission and agreeing recheck are required'})
    if not valid_pair(pair):
        return issues+[{'claim': 'schema', 'code': 'invalid_schema', 'detail': 'Both views must contain exactly C1-C4 nonempty strings'}]
    decision, selected = evidence['decision'], evidence.get('selected')
    valid = [test for test in evidence['omissions'] if test['label'] in LETTERS]
    expected_counts = [len(evidence['omissions']), len(evidence['spans']), len(valid), sum(test['changed'] for test in valid)]
    for audience, view in pair.items():
        def fail(claim, code, detail):
            issues.append({'audience': audience, 'claim': claim, 'code': code, 'detail': detail})
        c1, c2, c3, c4 = (view[cid] for cid in CLAIMS)
        if decision['label'] not in re.findall(r'\b[A-D]\b', c1) or normalized(decision.get('name') or '') not in normalized(c1):
            fail('C1', 'decision_binding', 'Retain the recorded option and exact supplied diagnosis name')
        claimed = re.findall(r'\b(?:option|choice|suggestion|selected|answer|label)\s*:?\s*([A-D])\b', c1, re.I)
        if any(letter.upper() != decision['label'] for letter in claimed):
            fail('C1', 'wrong_option', 'A conflicting recorded option was asserted')
        if selected:
            if set(re.findall(r'\bS\d+\b', c2)) != {selected['span_id']}:
                fail('C2', 'span_binding', 'Use only the selected tested span identifier')
            needed = {decision['label'], selected['label']}
            if not needed.issubset(set(re.findall(r'\b[A-D]\b', c2))):
                fail('C2', 'transition_binding', 'Retain both original and omitted-input option labels')
        # Role order is fixed in the claim plan; numbers alone are not proof of meaning.
        if numbers(c3) != expected_counts:
            fail('C3', 'count_binding', f'Retain counts in tested/available/valid/changed order: {expected_counts}')
        if re.search(r'\d\s*%|percent|confidence|certainly|guaranteed', ' '.join(view.values()), re.I):
            fail('all', 'unsupported_certainty', 'No calibrated diagnostic confidence or guarantees were measured')
        if not re.search(r'caus|causation', c4, re.I) or not re.search(r'internal|reason', c4, re.I) or not re.search(r'all|every|possible', c4, re.I):
            fail('C4', 'missing_scope', 'Retain causation, untested-edit and internal-reasoning limitations')
    return issues


def check_pair(pair, evidence, expected_input_sha, scorer, threshold=NLI_THRESHOLD, expected_target_signature=None):
    issues = structural_issues(pair, evidence, expected_input_sha, expected_target_signature)
    report = {'passed': False, 'threshold': threshold, 'operating_point': 'provisional_development',
              'independent_semantic_validation': False, 'issues': issues, 'nli': []}
    if any(item['code'] in ('case_binding','record_binding','invalid_schema','insufficient_evidence') for item in issues):
        return report
    facts = canonical_facts(evidence)
    pairs, refs = [], []
    for audience, view in pair.items():
        clauses = sum((sentence_parts(view[cid]) for cid in CLAIMS), [])
        if len(clauses) > 16:
            issues.append({'audience': audience, 'claim': 'all', 'code': 'clause_budget', 'detail': 'More than sixteen rendered clauses; unresolved'})
            continue
        for cid in CLAIMS:
            for clause in sentence_parts(view[cid]):
                pairs.append((facts[cid], clause)); refs.append({'audience': audience, 'claim': cid, 'direction': 'support'})
            pairs.append((' '.join(view.values()), facts[cid])); refs.append({'audience': audience, 'claim': cid, 'direction': 'coverage'})
    scores = scorer(pairs)
    if len(scores) != len(refs):
        issues.append({'claim':'checker','code':'incomplete_checker_result','detail':'Not every support/coverage query returned a result'})
        return report
    for ref, score in zip(refs, scores):
        passed = score.get('status') == 'scored' and score.get('entailment', 0) >= threshold
        report['nli'].append({**ref, **score, 'passed': passed})
        if not passed:
            issues.append({**ref, 'code': 'nli_unresolved' if score.get('status') != 'scored' else 'nli_not_entailed', 'detail': 'Support/coverage did not meet the provisional operating point'})
    report['passed'] = not issues
    return report
