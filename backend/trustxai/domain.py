"""Input identity and evidence contract. No gold labels enter this module."""
import hashlib
import json
import re
from typing import Literal
from pydantic import BaseModel, Field, field_validator

LETTERS = ('A', 'B', 'C', 'D')
CLAIMS = ('C1', 'C2', 'C3', 'C4')


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(',', ':')).encode()).hexdigest()


class CaseInput(BaseModel):
    case_text: str = Field(min_length=30, max_length=18000)
    question: str = Field(default='Which of the following is the most likely diagnosis?', max_length=600)
    options: dict[str, str]
    title: str | None = Field(default=None, max_length=100)
    parent_id: str | None = None
    source_id: str | None = None

    @field_validator('case_text', 'question')
    @classmethod
    def strip_text(cls, value):
        value = value.strip()
        if not value:
            raise ValueError('Text cannot be empty')
        return value

    @field_validator('question')
    @classmethod
    def diagnosis_scope(cls, value):
        if not re.search(r'(?:\b(?:is|would be)\s+(?:the\s+)?most\s+(?:likely|probable)\s+(?:(?:clinical|underlying|final)\s+)?diagnosis\b|\b(?:which|what)\s+diagnosis\s+is\s+most\s+(?:likely|probable)\b)', value, re.I):
            raise ValueError('Use a most-likely-diagnosis question for this workspace')
        if re.search(r'\b(treatment|confirm|tests?|workup|next step|mechanism|except)\b', value, re.I):
            raise ValueError('This workspace evaluates diagnosis selection, rather than treatment or test selection')
        return value

    @field_validator('options')
    @classmethod
    def four_options(cls, value):
        if set(value) != set(LETTERS):
            raise ValueError('Provide exactly four candidate diagnoses, A through D')
        values = {key: str(value[key]).strip() for key in LETTERS}
        if any(not text or len(text) > 500 for text in values.values()):
            raise ValueError('Each candidate must contain between 1 and 500 characters')
        if len({text.casefold() for text in values.values()}) != 4:
            raise ValueError('The four candidates must be distinct')
        return values


def segment_case(text: str) -> list[dict]:
    """Preserve exact character ranges; merge fragments and bound to eight spans."""
    cuts = [0] + [m.end() for m in re.finditer(r'(?<=[.!?])\s+|\n\s*\n', text)] + [len(text)]
    spans, pending = [], 0
    for end in sorted(set(cuts[1:])):
        if len(text[pending:end].split()) >= 5:
            spans.append({'start': pending, 'end': end, 'text': text[pending:end]})
            pending = end
    if pending < len(text):
        if spans:
            spans[-1].update(end=len(text), text=text[spans[-1]['start']:])
        else:
            spans = [{'start': 0, 'end': len(text), 'text': text}]
    while len(spans) > 8:
        index = min(range(len(spans)-1), key=lambda i: (spans[i+1]['end']-spans[i]['start'], i))
        start, end = spans[index]['start'], spans[index+1]['end']
        spans[index:index+2] = [{'start': start, 'end': end, 'text': text[start:end]}]
    if len(spans) < 2:
        raise ValueError('Provide at least two short sentences or findings so that an omission audit is possible')
    assert ''.join(item['text'] for item in spans) == text
    return [dict(item, id=f'S{index+1}') for index, item in enumerate(spans)]


def prepare_case(case: CaseInput) -> dict:
    spans = segment_case(case.case_text)
    projected = {'question': case.question, 'contexts': [span['text'] for span in spans], 'options': case.options}
    return {'question': case.question, 'spans': spans, 'options': case.options,
            'input_sha256': digest(projected), 'source_id': case.source_id,
            'case_text': case.case_text}


def valid_pair(value) -> bool:
    return (isinstance(value, dict) and set(value) == {'novice', 'expert'}
            and all(isinstance(value[audience], dict) and set(value[audience]) == set(CLAIMS)
                    and all(isinstance(text, str) and 0 < len(text.strip()) <= 3000
                            for text in value[audience].values()) for audience in ('novice', 'expert')))


def canonical_facts(evidence: dict) -> dict[str, str]:
    decision = evidence['decision']
    tests = evidence['omissions']
    valid = [test for test in tests if test['label'] in LETTERS]
    flips = [test for test in valid if test['changed']]
    selected = evidence.get('selected')
    recheck = evidence.get('recheck')
    agrees = bool(selected and recheck and selected['label'] == recheck['label'])
    if decision['label'] not in LETTERS:
        c1 = 'The model did not return a valid diagnostic option. No diagnosis is recorded.'
    else:
        c1 = f"Recorded model suggestion: {decision['label']} ({decision['name']}). It is not a verified diagnosis."
    c2 = (f"Omitting {selected['span_id']} returned {selected['label']} "
          + (f"instead of {decision['label']}." if selected['changed'] else f", the same original answer {decision['label']}.")
          if selected else 'No valid selected omission result is available; no span effect is established.')
    c3 = (f"{len(tests)} of {len(evidence['spans'])} case spans tested by one-span omission; "
          f"{len(valid)} valid labels; {len(flips)} answer changes. "
          + ('The selected-result recheck agreed.' if agrees else 'The selected-result recheck did not agree.' if recheck else 'No selected result could be rechecked.'))
    return {'C1': c1, 'C2': c2, 'C3': c3,
            'C4': 'These tests do not prove clinical causation, all-edit outcomes or complete internal reasoning.'}


def evidence_template(evidence: dict) -> dict:
    facts = canonical_facts(evidence)
    decision, selected, recheck = evidence['decision'], evidence.get('selected'), evidence.get('recheck')
    valid = [test for test in evidence['omissions'] if test['label'] in LETTERS]
    flips = sum(test['changed'] for test in valid)
    simple = {}
    simple['C1'] = (f"The model chose {decision['label']}: {decision['name']}. This is a suggestion, not a confirmed diagnosis."
                    if decision['label'] in LETTERS else 'No valid diagnostic choice was returned. No diagnosis is recorded.')
    if selected:
        simple['C2'] = (f"Without case segment {selected['span_id']}, the model chose {selected['label']} instead of {decision['label']}."
                        if selected['changed'] else f"Without case segment {selected['span_id']}, the model still chose {decision['label']}.")
    else:
        simple['C2'] = 'There is no valid selected omission result to show.'
    repeat = ('Repeating the selected check gave the same answer.' if selected and recheck and selected['label']==recheck['label']
              else 'Repeating the selected check gave a different answer.' if recheck else 'No selected result could be repeated.')
    simple['C3'] = (f"We tested {len(evidence['omissions'])} of {len(evidence['spans'])} case segments, leaving out a single segment per test. "
                    f"There were {len(valid)} valid answers and {flips} answer changes. "+repeat)
    simple['C4'] = "These checks cannot establish clinical causes, what every other edit would do, or the model's full internal reasoning."
    return {'novice': simple, 'expert': dict(facts)}


def evidence_available(evidence: dict) -> bool:
    selected, recheck = evidence.get('selected'), evidence.get('recheck')
    return bool(evidence['decision']['label'] in LETTERS and selected and recheck
                and selected['label'] == recheck['label'] and recheck['label'] in LETTERS)
