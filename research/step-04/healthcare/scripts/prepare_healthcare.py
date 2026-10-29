"""Prepare PubMedQA source splits without model inference; raw text stays outside Git."""
from pathlib import Path
import json,hashlib,unicodedata,re,csv,random,collections,os
from transformers import AutoTokenizer
B=Path(__file__).resolve().parents[1];R=Path(os.environ.get('TRUSTXAI_RUNTIME','/workspace/thesis-runtime'))/'healthcare';D=R/'source/data'
META=json.loads((B.parent/'evidence/MODEL_REVISIONS.json').read_text());M=META['Qwen/Qwen3-1.7B'];tok=AutoTokenizer.from_pretrained(M['local_path'],local_files_only=True)
data=json.loads((D/'ori_pqal.json').read_text());official_test=set(json.loads((D/'test_set.json').read_text()));official_cv=set(data)-official_test
assert len(data)==1000 and len(official_cv)==len(official_test)==500
prompt=json.loads((B/'CLASSIFICATION_PROMPT.json').read_text())
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False))
def norm(s):return ' '.join(unicodedata.normalize('NFC',s).casefold().split())
def project(x):return {'question':x['QUESTION'],'contexts':x['CONTEXTS']}
def sha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def user(x):return prompt['user_template'].format(question=x['question'],context='\n\n'.join(f'[S{i+1}] {v}'for i,v in enumerate(x['contexts'])))
# Explicit allowlist; excluded answer/model-output fields cannot enter serialized inputs.
sentinel={'QUESTION':'Allowed question','CONTEXTS':['Allowed context'],**{k:'LEAK_SENTINEL_'+k for k in ['LONG_ANSWER','final_decision','reasoning_free_pred','reasoning_required_pred','MESHES','YEAR','LABELS']}}
assert set(project(sentinel))=={'question','contexts'} and 'LEAK_SENTINEL' not in user(project(sentinel))
ids=list(data);parent={i:i for i in ids}
def root(i):
 while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
 return i
def join(i,j):
 a,b=root(i),root(j)
 if a!=b:parent[max(a,b)]=min(a,b)
exact={};qs={};wordsets={};exact_repeats=0;q_repeats=0
for i,x in data.items():
 text=norm(x['QUESTION']+' '+' '.join(x['CONTEXTS']));key=hashlib.sha256(text.encode()).hexdigest();q=norm(x['QUESTION'])
 if key in exact:join(i,exact[key]);exact_repeats+=1
 else:exact[key]=i
 if q in qs:join(i,qs[q]);q_repeats+=1
 else:qs[q]=i
 wordsets[i]=set(re.findall(r'\w+',text))
near_edges=0
for n,i in enumerate(ids):
 a=wordsets[i]
 for j in ids[n+1:]:
  z=wordsets[j]
  if min(len(a),len(z))<.90*max(len(a),len(z)):continue
  inter=len(a&z)
  if inter/(len(a)+len(z)-inter)>=.90:join(i,j);near_edges+=1
groups=collections.defaultdict(list)
for i in ids:groups[root(i)].append(i)
quarantine={};representatives=[]
for g,members in groups.items():
 partitions={i in official_test for i in members};labs={data[i]['final_decision'] for i in members}
 reason='cross-official-partition' if len(partitions)>1 else 'conflicting-labels' if len(labs)>1 else None
 if reason:
  for i in members:quarantine[i]=reason
 else:representatives.append(min(members,key=int))
features={};exclusions=collections.Counter();eligible={'official_cv':[],'official_test':[]}
for i in representatives:
 x=data[i];inp=project(x);sections=len(inp['contexts'])
 if not isinstance(inp['question'],str) or not inp['question'].strip() or any(not isinstance(c,str) or not c.strip() for c in inp['contexts']):exclusions['empty_or_malformed']+=1;continue
 if not 2<=sections<=8:exclusions['section_budget']+=1;continue
 nt=len(tok.encode(inp['question']+'\n'+'\n'.join(inp['contexts']),add_special_tokens=False))
 full=tok.apply_chat_template([{'role':'system','content':prompt['system']},{'role':'user','content':user(inp)}],tokenize=True,add_generation_prompt=True,enable_thinking=False)
 if nt>1024 or len(full)>1536:exclusions['token_budget']+=1;continue
 features[i]={'sections':sections,'qcontext_tokens':nt,'full_prompt_tokens':len(full),'input_sha256':sha(inp)}
 eligible['official_test' if i in official_test else 'official_cv'].append(i)
rng=random.Random(20261027);chosen={};used=set()
for split,n,pool in [('feasibility',8,'official_cv'),('development',15,'official_cv'),('test',20,'official_test')]:
 picked=[]
 for label in ['yes','no','maybe']:
  candidates=sorted([i for i in eligible[pool] if data[i]['final_decision']==label and i not in used],key=int);rng.shuffle(candidates)
  if len(candidates)<n:raise RuntimeError('Insufficient eligible sources; revise declaration before inference')
  picked.extend(candidates[:n]);used.update(candidates[:n])
 chosen[split]=sorted(picked,key=int)
assert len(used)==129 and len({root(i)for i in used})==129
records=[]
for split,members in chosen.items():
 for i in members:records.append({'source_id':i,'partition':split,'official_partition':'test'if i in official_test else 'cv','gold_label':data[i]['final_decision'],'group_id':root(i),**features[i]})
with (B/'SPLIT_MANIFEST.csv').open('w',newline='')as f:
 w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
# Inputs/gold are separate; only feasibility raw inputs are exposed to inference harness now.
dump(R/'feasibility_inputs.json',[{'source_id':i,**project(data[i]),'input_sha256':features[i]['input_sha256']}for i in chosen['feasibility']]);dump(R/'feasibility_gold.json',{i:data[i]['final_decision']for i in chosen['feasibility']})
dump(R/'partition_ids.json',chosen)
counts={pool:dict(collections.Counter(data[i]['final_decision']for i in members))for pool,members in eligible.items()}
out={'raw_records':len(data),'raw_labels':dict(collections.Counter(x['final_decision']for x in data.values())),'official_CV':500,'official_test':500,'official_test_labels':dict(collections.Counter(data[i]['final_decision']for i in official_test)),'official_test_membership_sha256':sha(sorted(official_test,key=int)),'normalized_exact_repeats':exact_repeats,'normalized_question_repeats':q_repeats,'near_duplicate_edges':near_edges,'source_components':len(groups),'quarantined_sources':dict(collections.Counter(quarantine.values())),'eligibility_exclusions':dict(exclusions),'eligible_counts':counts,'selected_sources':{s:len(v)for s,v in chosen.items()},'cross_split_component_overlap':False,'max_selected_prompt_tokens':max(features[i]['full_prompt_tokens']for i in used),'manifest_sha256':hashlib.sha256((B/'SPLIT_MANIFEST.csv').read_bytes()).hexdigest(),'leakage_projection_sentinel_passed':True,'dataset_model_predictions_excluded':True,'model_inference_run':False,'test_model_inference_run':False,'tokenizer_revision':M['revision'],'source_text_in_public_pack':False}
dump(B/'DATA_PREPARATION.json',out);print(json.dumps(out,indent=2))
