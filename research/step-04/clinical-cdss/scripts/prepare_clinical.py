"""Label-blind diagnostic-vignette cohort; no model inference; no raw text in checkout."""
from pathlib import Path
import os,json,re,hashlib,csv,random,unicodedata,collections
from transformers import AutoTokenizer
B=Path(__file__).resolve().parents[1]
R=Path(os.environ.get('TRUSTXAI_RUNTIME','/workspace/thesis-runtime'))/'clinical-cdss'
M=json.loads((B.parent/'evidence/MODEL_REVISIONS.json').read_text())['Qwen/Qwen3-4B-Instruct-2507']
tok=AutoTokenizer.from_pretrained(M['local_path'],local_files_only=True)
PROMPT=json.loads((B/'CLASSIFICATION_PROMPT.json').read_text())
def write(path,data):path.write_text(json.dumps(data,indent=2,ensure_ascii=False))
def normalize(text):return ' '.join(unicodedata.normalize('NFC',text).casefold().split())
def sha(data):return hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def query_parts(question):
 full=question.strip()
 starts=list(re.finditer(r'\b(?:Which of the following|What is|What would be|Which diagnosis)\b',full,re.I))
 start=starts[-1].start() if starts else full.rfind(re.split(r'(?<=[.!?])\s+',full)[-1])
 stop=full.find('?',start)
 stop=stop+1 if stop>=0 else len(full)
 return full,full[start:stop],start

def is_diagnosis_query(terminal):
 formulation=re.search(r'(?:\b(?:is|would be)\s+(?:the\s+)?most\s+(?:likely|probable)\s+(?:(?:underlying|clinical|final)\s+)?diagnosis\b|\b(?:which|what)\s+diagnosis\s+is\s+most\s+(?:likely|probable)\b)',terminal,re.I)
 procedural=re.search(r'\b(?:tests?|confirm|confirmation|work[- ]?up|next step|mechanism|hypersensitivity|underlies|treatment|pathological|pathologically|supports|except|not)\b',terminal,re.I)
 return bool(formulation) and not procedural
def project(row):
 full,terminal,qstart=query_parts(row['question']);qend=qstart+len(terminal)
 spans=[]
 for begin,finish in [(0,qstart),(qend,len(full))]:
  block=full[begin:finish]
  if not block.strip(' \t\r\n"\''):continue
  cuts=[0]+[m.end() for m in re.finditer(r'(?<=[.!?])\s+(?=[A-Z0-9])',block)]+[len(block)]
  pending=0
  for end in cuts[1:]:
   if len(block[pending:end].split())>=5:
    spans.append({'start':begin+pending,'end':begin+end,'text':block[pending:end]});pending=end
  if pending<len(block):
   if spans and spans[-1]['end']>=begin:
    spans[-1].update(end=finish,text=full[spans[-1]['start']:finish])
   else:spans.append({'start':begin+pending,'end':finish,'text':block[pending:]})
 while len(spans)>8:
  adjacent=[j for j in range(len(spans)-1) if spans[j]['end']==spans[j+1]['start']]
  if not adjacent:raise RuntimeError('Cannot merge contiguous evidence spans')
  i=min(adjacent,key=lambda j:(spans[j+1]['end']-spans[j]['start'],j))
  spans[i:i+2]=[{'start':spans[i]['start'],'end':spans[i+1]['end'],'text':full[spans[i]['start']:spans[i+1]['end']]}]
 for span in spans:assert span['text']==full[span['start']:span['end']]
 expected=full[:qstart]+full[qend:]
 assert ''.join(span['text'] for span in spans).strip(' \t\r\n"\'')==expected.strip(' \t\r\n"\'')
 return {'question':terminal,'contexts':[span['text'] for span in spans],'options':{k:row['options'][k] for k in ['A','B','C','D']}},spans

def user(inp):
 return PROMPT['user_template'].format(question=inp['question'],context='\n\n'.join(f'[S{i+1}] {t}' for i,t in enumerate(inp['contexts'])),options='\n'.join(f'{k}: {v}' for k,v in inp['options'].items()))
sentinel={'question':'A patient has fever. Which diagnosis is most likely?','options':dict.fromkeys(['A','B','C','D'],'Allowed option'),'answer':'LEAK_SENTINEL','answer_idx':'LEAK_SENTINEL','meta_info':'LEAK_SENTINEL','metamap_phrases':'LEAK_SENTINEL'}
assert 'LEAK_SENTINEL' not in user(project(sentinel)[0])
raw_counts={};candidates={};excluded=collections.Counter();projected={};features={};raw={}
exploratory_exclusions=set(json.loads((B/'EXPLORATORY_SOURCE_EXCLUSIONS.json').read_text()))
for partition in ['train','test']:
 path=R/f'phrases_no_exclude_{partition}.jsonl';rows=[json.loads(line) for line in path.read_text().splitlines() if line.strip()];raw_counts[partition]=len(rows)
 for index,row in enumerate(rows):
  sid=f'medqa-{partition}-{index:05d}';question,terminal,_=query_parts(row['question'])
  if not re.search(r'\b(patient|man|woman|boy|girl|infant|newborn)\b|\b\d+-year-old\b',question,re.I):excluded[partition+':nonclinical_heuristic']+=1;continue
  if not is_diagnosis_query(terminal):excluded[partition+':not_terminal_diagnosis_question']+=1;continue
  if set(row['options'])!={'A','B','C','D'} or any(not isinstance(v,str) or not v.strip() for v in row['options'].values()):excluded[partition+':invalid_options']+=1;continue
  if row['answer_idx'] not in row['options'] or normalize(row['answer'])!=normalize(row['options'][row['answer_idx']]):excluded[partition+':inconsistent_gold_fields']+=1;continue
  candidates[sid]=row;raw[sid]=row
# Group candidate questions, including altered option orders, before eligibility sampling.
ids=list(candidates);parent={s:s for s in ids}
def root(s):
 while parent[s]!=s:parent[s]=parent[parent[s]];s=parent[s]
 return s
def join(a,b):
 a,b=root(a),root(b)
 if a!=b:parent[max(a,b)]=min(a,b)
seen={};wordsets={};exact=0
for sid,row in candidates.items():
 text=normalize(row['question'])
 if text in seen:join(sid,seen[text]);exact+=1
 else:seen[text]=sid
 wordsets[sid]=set(re.findall(r'\w+',text))
near=0
for index,sid in enumerate(ids):
 a=wordsets[sid]
 for other in ids[index+1:]:
  z=wordsets[other]
  if min(len(a),len(z))<.9*max(len(a),len(z)):continue
  overlap=len(a&z)
  if overlap/(len(a)+len(z)-overlap)>=.9:join(sid,other);near+=1
groups=collections.defaultdict(list)
for sid in ids:groups[root(sid)].append(sid)
quarantined=[];representatives=[]
for members in groups.values():
 if len({s.split('-')[1] for s in members})>1:quarantined.extend(members)
 else:representatives.append(min(members))
eligible={'train':[],'test':[]}
for sid in representatives:
 row=candidates[sid];inp,spans=project(row);part=sid.split('-')[1]
 if sid in exploratory_exclusions:excluded[part+':archived_exploratory_source']+=1;continue
 if not 2<=len(spans)<=8:excluded[part+':span_budget']+=1;continue
 messages=[{'role':'system','content':PROMPT['system']},{'role':'user','content':user(inp)}]
 tokens=tok.apply_chat_template(messages,tokenize=True,add_generation_prompt=True,enable_thinking=False)
 if len(tokens)>1536:excluded[part+':prompt_token_budget']+=1;continue
 projected[sid]=inp;features[sid]={'input_sha256':sha(inp),'original_question_sha256':hashlib.sha256(row['question'].encode()).hexdigest(),'options_sha256':sha(inp['options']),'span_count':len(spans),'prompt_tokens':len(tokens),'source_offsets':spans};eligible[part].append(sid)
rng=random.Random(20261027);chosen={};used=set()
for split,n,origin in [('feasibility',6,'train'),('development',10,'train'),('test',15,'test')]:
 selected=[]
 for label in ['A','B','C','D']:
  pool=sorted(s for s in eligible[origin] if s not in used and raw[s]['answer_idx']==label);rng.shuffle(pool)
  if len(pool)<n:raise RuntimeError(f'Not enough eligible {origin} option {label}: {len(pool)}; change protocol before inference')
  selected.extend(pool[:n]);used.update(pool[:n])
 chosen[split]=sorted(selected)
assert len(used)==124 and len({root(s) for s in used})==124
records=[]
for split,members in chosen.items():
 for sid in members:
  feature=features[sid]
  records.append({'source_id':sid,'partition':split,'source_partition':sid.split('-')[1],'correct_option':raw[sid]['answer_idx'],'group_id':root(sid),**{k:v for k,v in feature.items() if k!='source_offsets'}})
with (B/'SPLIT_MANIFEST.csv').open('w',newline='') as file:
 writer=csv.DictWriter(file,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)
write(R/'feasibility_inputs.json',[{'source_id':sid,**projected[sid],'input_sha256':features[sid]['input_sha256'],'original_question_sha256':features[sid]['original_question_sha256']} for sid in chosen['feasibility']]);write(R/'feasibility_gold.json',{sid:raw[sid]['answer_idx'] for sid in chosen['feasibility']});write(R/'partition_ids.json',chosen);write(R/'source_offsets.json',{sid:features[sid]['source_offsets'] for sid in used})
record={'source':'Explicitly identified GBaker public mirror; no silent attribution as original author release','raw_counts':raw_counts,'diagnostic_candidates_before_text_grouping':dict(collections.Counter(s.split('-')[1] for s in ids)),'candidate_exact_question_repeats':exact,'near_duplicate_edges':near,'text_components':len(groups),'cross_source_partition_quarantined_cases':len(quarantined),'exclusions':dict(excluded),'eligible_cases':{p:len(v) for p,v in eligible.items()},'eligible_correct_option_counts':{p:dict(collections.Counter(raw[s]['answer_idx'] for s in v)) for p,v in eligible.items()},'selected_sources':{p:len(v) for p,v in chosen.items()},'cross_partition_group_overlap':False,'sampling_seed':20261027,'max_selected_prompt_tokens':max(features[s]['prompt_tokens'] for s in used),'split_manifest_sha256':hashlib.sha256((B/'SPLIT_MANIFEST.csv').read_bytes()).hexdigest(),'answer_field_projection_sentinel_passed':True,'raw_exam_text_packaged':False,'clinical_model_inference_run':False,'test_model_inference_run':False,'option_position_balance_not_disease_balance':True}
write(B/'DATA_PREPARATION.json',record);print(json.dumps(record,indent=2))
