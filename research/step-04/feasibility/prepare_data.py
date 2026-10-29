"""Prepare source-level splits; runs no target inference and exports no raw SMS to Git."""
from pathlib import Path
import json,csv,hashlib,re,unicodedata,random,collections,math
from transformers import AutoTokenizer
BASE=Path('/workspace/TRUSTXAI/research/step-04');DATA=Path('/workspace/thesis-runtime/data')
REV=json.loads((BASE/'evidence/MODEL_REVISIONS.json').read_text())['Qwen/Qwen2.5-1.5B-Instruct']['revision']
TOK=Path('/workspace/thesis-runtime/cache/huggingface/hub/models--Qwen--Qwen2.5-1.5B-Instruct/snapshots')/REV
tok=AutoTokenizer.from_pretrained(str(TOK),local_files_only=True,trust_remote_code=False)
norm=lambda s:' '.join(unicodedata.normalize('NFC',s).casefold().split())
sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
rows=[];malformed=[]
with (DATA/'SMSSpamCollection').open(encoding='utf-8',newline='') as f:
 for idx,line in enumerate(f):
  line=line.rstrip('\r\n')
  if not line:continue
  if '\t' not in line:malformed.append(idx);continue
  label,text=line.split('\t',1)
  if label not in ['ham','spam']:malformed.append(idx);continue
  rows.append({'source_id':f'uci228-{idx:05d}','label':label,'text':text,'text_sha256':sha(text),'normalized':norm(text)})
exact=collections.defaultdict(list)
for r in rows:exact[r['normalized']].append(r)
conflict_exact=[v for v in exact.values() if len({r['label'] for r in v})>1]
unique=[v for v in exact.values() if len({r['label'] for r in v})==1]
unique.sort(key=lambda v:v[0]['source_id'])
parent=list(range(len(unique)))
def find(i):
 while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
 return i
def union(i,j):
 a,b=find(i),find(j)
 if a!=b:parent[max(a,b)]=min(a,b)
post=collections.defaultdict(list);sets=[];edges=0
for i,group in enumerate(unique):
 s=set(group[0]['normalized'].split());sets.append(s);counts=collections.Counter()
 for token in s:counts.update(post[token])
 for j,ncommon in counts.items():
  la,lb=len(s),len(sets[j])
  if min(la,lb)<0.90*max(la,lb):continue
  if ncommon/(la+lb-ncommon)>=0.90:union(i,j);edges+=1
 for token in s:post[token].append(i)
components=collections.defaultdict(list)
for i,group in enumerate(unique):components[find(i)].extend(group)
conflict_near=0;elig=[];excluded=collections.Counter()
for comp in components.values():
 if len({r['label'] for r in comp})>1:conflict_near+=1;continue
 representative=min(comp,key=lambda r:r['source_id'])
 text=representative['text'];nw=len(re.findall(r'\S+',text));nt=len(tok.encode(text,add_special_tokens=False))
 if not 8<=nw<=60:excluded['word_budget']+=1;continue
 if nt>256:excluded['token_budget']+=1;continue
 group_id=sha('|'.join(sorted(r['source_id']+':'+r['text_sha256'] for r in comp)))
 elig.append({**representative,'group_id':group_id,'group_original_rows':len(comp),'words':nw,'payload_tokens':nt})
rng=random.Random(20261027);byclass={lab:sorted([r for r in elig if r['label']==lab],key=lambda x:x['source_id']) for lab in ['ham','spam']}
for seq in byclass.values():rng.shuffle(seq)
parts={};cursor=0
for name,perclass in [('feasibility',10),('development',20),('test',30)]:
 selected=[]
 for lab in ['ham','spam']:
  if len(byclass[lab])<cursor+perclass:raise RuntimeError('Insufficient independent eligible groups')
  selected.extend(byclass[lab][cursor:cursor+perclass])
 selected.sort(key=lambda r:r['source_id']);parts[name]=selected;cursor+=perclass
out=BASE/'feasibility';manifest=[]
for name,selected in parts.items():
 for r in selected:manifest.append({'partition':name,**{k:r[k] for k in ['source_id','label','text_sha256','group_id','group_original_rows','words','payload_tokens']}})
with (out/'SPLIT_MANIFEST.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(manifest[0]),lineterminator='\n');w.writeheader();w.writerows(manifest)
for a in parts:
 for b in parts:
  if a!=b:assert not ({r['group_id'] for r in parts[a]}&{r['group_id'] for r in parts[b]})
private=[{k:v for k,v in r.items() if k!='normalized'} for r in parts['feasibility']]
(DATA/'feasibility20.json').write_text(json.dumps(private,indent=2))
summary={'dataset_rows':len(rows),'labels':dict(collections.Counter(r['label'] for r in rows)),'malformed_records':len(malformed),'unique_normalized_exact_groups':len(exact),'removed_exact_repeated_rows':len(rows)-len(exact),'conflicting_exact_groups':len(conflict_exact),'near_duplicate_edges':edges,'near_components':len(components),'conflicting_near_components_quarantined':conflict_near,'excluded_components':dict(excluded),'eligible_independent_groups':len(elig),'eligible_labels':{k:len(v) for k,v in byclass.items()},'partitions':{k:{'sources':len(v),'labels':dict(collections.Counter(r['label'] for r in v))} for k,v in parts.items()},'cross_partition_group_overlap':False,'split_manifest_sha256':hashlib.sha256((out/'SPLIT_MANIFEST.csv').read_bytes()).hexdigest(),'tokenizer_model':'Qwen/Qwen2.5-1.5B-Instruct','tokenizer_revision':REV,'test_inputs_scored_by_model':False,'amendment':'Also quarantine mixed-label near-connected components, before model outcome inspection.'}
(out/'DATA_PREPARATION.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))
