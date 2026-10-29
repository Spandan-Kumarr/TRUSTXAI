"""Small, inspectable source registry. Retrieval never uploads a clinical case."""
from pathlib import Path
import hashlib
import json
import re
from .config import ROOT, RESEARCH, RUNTIME
from .domain import digest


def source_record(identifier, title, url, content, path=None, category='public_research'):
    path = Path(path) if path else None
    return {'id': identifier, 'title': title, 'url': url, 'content': content,
            'category': category, 'content_type': 'curated_source_summary' if category == 'public_research' else 'recorded_context',
            'verification': 'Primary-source provenance recorded' if path and path.exists() else 'Recorded reference',
            'snapshot_sha256': hashlib.sha256(path.read_bytes()).hexdigest() if path and path.exists() else None,
            'captured_date': '2026-10-27'}


def public_sources():
    return [
      source_record('medqa', 'MedQA · clinical exam questions', 'https://arxiv.org/abs/2009.13081',
        'MedQA supplies a question and multiple answer candidates, of which only one should be chosen as most appropriate. '
        'The original USMLE dataset has 10,178 training, 1,272 development and 1,273 test questions. '
        'It contains medical knowledge questions and patient-condition descriptions. The four-option variant retains one correct and three wrong options. '
        'This is an exam-question benchmark; it does not by itself validate a real-patient diagnostic service.',
        RESEARCH/'evidence/MEDQA_PAPER_PROVENANCE.json'),
      source_record('medqa-mirror', 'MedQA · pinned public data mirror',
        'https://huggingface.co/datasets/GBaker/MedQA-USMLE-4-options',
        'The GBaker public mirror identifies the original MedQA dataset introduced by Di Jin and colleagues. Its card declares CC BY 4.0. '
        'The retrieved four-option files contain 10,178 training and 1,273 test cases. The answer and answer_idx fields are evaluation labels; '
        'they must not be included in a model input. Case questions and all candidate options are legitimate multiple-choice inputs.',
        RESEARCH/'evidence/MedQA_mirror_card.md'),
      source_record('pubmedqa', 'PubMedQA · biomedical research QA', 'https://aclanthology.org/D19-1259/',
        'PubMedQA answers biomedical research questions with yes, no or maybe using the corresponding abstract without its conclusion. '
        'The original dataset has 1,000 expert-annotated examples. Its long answer is the conclusion and is an evaluation target, not inference evidence. '
        'PubMedQA is a different task from choosing a diagnosis for a clinical vignette.',
        ROOT/'research/step-04/healthcare/evidence/PUBMEDQA_PAPER_PROVENANCE.json'),
      source_record('medexqa', 'MedExQA · multiple medical explanations', 'https://aclanthology.org/2024.bionlp-1.14/',
        'MedExQA contains 965 multiple-choice questions across five medical specialties and two reference explanations per question. '
        'It evaluates explanation generation in addition to classification accuracy. Its reported human evaluation used three health-related MSc annotators '
        'on 25 development examples. Multiple medical explanations are existing research, not automatically a new contribution of TRUSTXAI.',
        ROOT/'research/step-04/healthcare/evidence/HEALTHCARE_FULLTEXT_PROVENANCE.json'),
      source_record('medhallu', 'MedHallu · medical hallucination detection', 'https://arxiv.org/abs/2502.14302',
        'MedHallu studies medical hallucination detection using 10,000 samples derived from PubMedQA: 1,000 labelled-source and 9,000 artificial-source examples. '
        'Its generation/filtering pipeline uses model discriminators, bidirectional natural-language inference and iterative feedback. '
        'Medical hallucination detection and post-generation verification therefore predate TRUSTXAI.',
        ROOT/'research/step-04/healthcare/evidence/HEALTHCARE_FULLTEXT_PROVENANCE.json'),
      source_record('qwen', 'Qwen3 · local instruction model', 'https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507',
        'Qwen3-4B-Instruct-2507 is the pinned local model used for diagnostic option selection. '
        'TRUSTXAI uses the model in CPU FP32 with greedy A-D output. A separate official Qwen3-1.7B GGUF Q8_0 model renders explanations. '
        'These existing local models are components of the framework; TRUSTXAI is not a newly pretrained foundation model.',
        RESEARCH/'evidence/Qwen3-4B_card.md'),
      source_record('project-protocol', 'TRUSTXAI · research protocol', None,
        'TRUSTXAI is a diagnostic decision-support research prototype. Its primary research benchmark is a diagnosis-only subset of public MedQA four-option questions; PubMedQA is an auxiliary biomedical research-QA task. It chooses among four supplied diagnoses, freezes the model answer, '
        'tests omission of case spans, repeats the selected modified input, and renders simple and technical explanations. '
        'Automated structural and entailment checks are fallible. One repair is allowed before a labelled evidence-template fallback. '
        'The primary 24-case feasibility pilot got 16 answers correct; this is not final-test or clinical validation. '
        'No GPT or Gemini comparison has been run. No improvement over those systems or patient benefit has been established. '
        'User input, case audit facts and public research references are distinct source types. '
        'Source-grounded chat retrieves this finite local collection; it does not search the entire web.',
        RESEARCH/'STEP_04_CLINICAL_PROTOCOL.md', category='project_protocol'),
    ]


def retrieve(question, case=None, limit=5):
    sources = public_sources()
    if case and case.get('result'):
        evidence = case['result']['evidence']
        for cid, text in case['result']['facts'].items():
            sources.append(source_record('case-'+cid, 'Recorded audit · '+cid, None, text, category='recorded_model_behavior'))
        for test in evidence['omissions']:
            sources.append(source_record('case-test-'+test['span_id'], 'Recorded omission · '+test['span_id'], None,
                f"In this case the original recorded option was {evidence['decision']['label']}. A fresh query omitting {test['span_id']} returned option {test['label']}. This is an input-omission observation, not clinical causation.",
                category='recorded_model_behavior'))
        for span in evidence['spans']:
            sources.append(source_record('case-'+span['id'], 'Supplied case · '+span['id'], None,
                       span['text'], category='supplied_case_finding'))
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    corpus = [item['title']+' '+item['content'] for item in sources]
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1,2))
    matrix = vectorizer.fit_transform(corpus+[question])
    scores = cosine_similarity(matrix[-1], matrix[:-1])[0]
    ranked = sorted(range(len(sources)), key=lambda index: float(scores[index]), reverse=True)
    selected = [dict(sources[index], retrieval_score=float(scores[index])) for index in ranked if scores[index] > .025][:limit]
    if not selected:
        selected = [next(item for item in sources if item['id'] == 'project-protocol')]
    if case and case.get('result'):
        # Always retain the frozen answer and its interpretation boundary.
        for identifier in ('case-C1','case-C4'):
            item = next(item for item in sources if item['id'] == identifier)
            if not any(value['id'] == identifier for value in selected):
                selected.insert(0, dict(item, retrieval_score=None))
        selected = selected[:7]
    return selected


def check_cited_answer(answer, sources, scorer, threshold):
    """Validate cited passages and sentence support; no fabricated references released."""
    if not isinstance(answer, str):
        return {'passed':False,'reason':'Response is not text','scores':[]}
    answer = re.sub(r'([.!?])\s*((?:\[\d+\]\s*)+)', r' \2\1', answer).strip()
    all_ids = [int(value) for value in re.findall(r'\[(\d+)\]', answer)]
    if not answer or not all_ids or any(value < 1 or value > len(sources) for value in all_ids):
        return {'passed': False, 'reason': 'Missing or unrecognized citation', 'scores': []}
    if re.search(r'TRUSTXAI.{0,80}(?:outperform|better than|more accurate than).{0,30}(?:GPT|Gemini)', answer, re.I):
        return {'passed': False, 'reason': 'Unmeasured comparative performance claim', 'scores': []}
    pairs = []
    for sentence in re.split(r'(?<=[.!?])\s+', answer):
        ids = sorted({int(value) for value in re.findall(r'\[(\d+)\]', sentence)})
        hypothesis = re.sub(r'\[\d+\]', '', sentence).strip()
        if not hypothesis: continue
        if not ids:
            return {'passed': False, 'reason': 'A sentence has no supporting citation', 'scores': []}
        premise = '\n'.join(sources[index-1]['content'] for index in ids)
        pairs.append((premise, hypothesis))
    if len(pairs) > 12:
        return {'passed': False, 'reason': 'Response exceeds the checked sentence budget', 'scores': []}
    scores = scorer(pairs)
    passed = bool(scores) and len(scores) == len(pairs) and all(row.get('status') == 'scored' and row.get('entailment',0) >= threshold for row in scores)
    return {'passed': passed, 'reason': None if passed else 'Citation support did not pass the provisional entailment check',
            'scores': scores, 'normalized_answer': answer}


SYNTHETIC_CASES = [
 {'id':'synthetic-respiratory','title':'Fever & productive cough','synthetic':True,
  'case_text':'A 54-year-old man has three days of fever and a productive cough. His respiratory rate is 26 per minute and oxygen saturation is 91% on room air. Examination finds focal crackles over the right lower lung. A chest radiograph shows a new right lower-lobe air-space opacity.',
  'question':'Which of the following is the most likely diagnosis?',
  'options':{'A':'Community-acquired pneumonia','B':'Acute asthma exacerbation','C':'Pulmonary embolism','D':'Acute heart failure'}},
 {'id':'synthetic-endocrine','title':'Thirst & frequent urination','synthetic':True,
  'case_text':'A 42-year-old adult reports several weeks of thirst, frequent urination and unintentional weight loss. Random plasma glucose is 318 mg/dL. Urine testing detects glucose. There is no reported medication use that would explain the elevated glucose.',
  'question':'Which of the following is the most likely diagnosis?',
  'options':{'A':'Diabetes insipidus','B':'Diabetes mellitus','C':'Primary polydipsia','D':'Urinary tract infection'}},
 {'id':'synthetic-airways','title':'Episodic wheezing','synthetic':True,
  'case_text':'A 23-year-old adult has recurrent episodes of cough, wheeze and chest tightness that are worse at night. Symptoms increase after exercise and exposure to cats. Spirometry shows an obstructive pattern that improves after an inhaled bronchodilator. The patient feels well between episodes.',
  'question':'Which of the following is the most likely diagnosis?',
  'options':{'A':'Bronchiectasis','B':'Pulmonary fibrosis','C':'Asthma','D':'Pneumothorax'}},
]


def public_case_rows():
    path = RUNTIME / 'clinical-cdss/feasibility_inputs.json'
    if not path.exists():
        return []
    # This fixed file is the feasibility pool; no test/development/gold files are read.
    rows = json.loads(path.read_text())
    return rows if isinstance(rows, list) else []


def examples():
    public = []
    for row in public_case_rows()[:4]:
        public.append({'id': row['source_id'], 'source_id': row['source_id'],
                       'title': 'MedQA case '+row['source_id'].rsplit('-',1)[-1],
                       'synthetic': False, 'case_text': ''.join(row['contexts']).strip(),
                       'question': row['question'], 'options': row['options'],
                       'source_title': 'Public MedQA feasibility case',
                       'source_url': 'https://huggingface.co/datasets/GBaker/MedQA-USMLE-4-options'})
    return SYNTHETIC_CASES + public


def prepare_bound_case(payload):
    from .domain import prepare_case
    prepared = prepare_case(payload)
    if not payload.source_id:
        prepared['source'] = {'category':'user_provided','title':'User-provided research case'}
        return prepared
    synthetic = next((item for item in SYNTHETIC_CASES if item['id']==payload.source_id),None)
    row = next((item for item in public_case_rows() if item['source_id']==payload.source_id),None)
    if not synthetic and not row:
        raise ValueError('Unrecognized source attribution')
    reference = synthetic or {'case_text':''.join(row['contexts']).strip(),'question':row['question'],'options':row['options']}
    compact = lambda text: ' '.join(text.split())
    if compact(payload.case_text)!=compact(reference['case_text']) or compact(payload.question)!=compact(reference['question']) or payload.options!={key:value.strip() for key,value in reference['options'].items()}:
        raise ValueError('The source case was edited. Clear its source reference and analyze it as a new user-provided case.')
    if row:
        cursor, spans = 0, []
        for index,text in enumerate(row['contexts']):
            spans.append({'id':f'S{index+1}','start':cursor,'end':cursor+len(text),'text':text});cursor+=len(text)
        prepared.update(case_text=''.join(row['contexts']),question=row['question'],options=dict(row['options']),spans=spans,
                        input_sha256=digest({'question':row['question'],'contexts':row['contexts'],'options':row['options']}),
                        source={'category':'public_benchmark','title':'MedQA feasibility case','id':row['source_id'],
                                'url':'https://huggingface.co/datasets/GBaker/MedQA-USMLE-4-options',
                                'dataset_revision':'0fb93dd23a7339b6dcd27e241cb9b5eca62d4d18',
                                'original_question_sha256':row['original_question_sha256']})
        if prepared['input_sha256']!=row['input_sha256']:
            raise ValueError('The public source snapshot no longer matches its recorded input hash')
    else:
        prepared['source']={'category':'synthetic','title':reference['title'],'id':payload.source_id}
    return prepared
