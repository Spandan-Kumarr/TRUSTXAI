"""Feasibility only: consumes the20-source pool, never development/test messages.
Raw messages/prompts/generated text remain outside the checkout. No H1/H2/H3results.
"""
from pathlib import Path
import os,json,time,hashlib,argparse,re,resource,statistics,copy
os.environ['HF_HOME']='/workspace/thesis-runtime/cache/huggingface'
os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
import torch
from transformers import AutoModelForCausalLM,AutoTokenizer,AutoModelForSequenceClassification
from sklearn.metrics import balanced_accuracy_score,f1_score,confusion_matrix
parser=argparse.ArgumentParser();parser.add_argument('--phase',choices=['classification','rendering','nli'],required=True);parser.add_argument('--run-tag',default='qwen15_feasibility_v1');parser.add_argument('--suffix',default='');parser.add_argument('--prompt-file',default='CLASSIFICATION_PROMPT.json');parser.add_argument('--label-a',default='A');parser.add_argument('--label-b',default='B');parser.add_argument('--model',default='Qwen/Qwen2.5-1.5B-Instruct');parser.add_argument('--disable-thinking',action='store_true');parser.add_argument('--cache-prefix',action='store_true')
parser.add_argument('--renderer-profile',choices=['shared-fp32','dynamic-qint8','separate-bfloat16'],default='shared-fp32')
parser.add_argument('--classification-suffix',default=None)
parser.add_argument('--generation-threads',type=int,choices=[1,2,4],default=4)
args=parser.parse_args()
B=Path('/workspace/TRUSTXAI/research/step-04');PUBLIC=B/'feasibility';PRIVATE=Path('/workspace/thesis-runtime/pilot')/args.run_tag;PRIVATE.mkdir(parents=True,exist_ok=True)
META=json.loads((B/'evidence/MODEL_REVISIONS.json').read_text());ROWS=json.loads(Path('/workspace/thesis-runtime/data/feasibility20.json').read_text());PROMPT=json.loads((PUBLIC/args.prompt_file).read_text());MODEL=args.model
assert len(ROWS)==20 and {r['label'] for r in ROWS}=={'ham','spam'}
torch.set_num_threads(4);torch.set_num_interop_threads(1);torch.manual_seed(20261027)
def write(p,x):
 p.write_text(json.dumps(x,indent=2,ensure_ascii=False))
def rss():return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/(1024**2)
def model_path(name):
 m=META[name]
 if not m.get('weights_sha256_verified'):raise RuntimeError('Weights not verified: '+name)
 return m['local_path']
class Target:
 def __init__(self):
  t=time.perf_counter();p=model_path(MODEL)
  self.tok=AutoTokenizer.from_pretrained(p,local_files_only=True,trust_remote_code=False)
  self.m=AutoModelForCausalLM.from_pretrained(p,local_files_only=True,trust_remote_code=False,use_safetensors=True,dtype=torch.float32,attn_implementation='sdpa').eval()
  self.load_s=time.perf_counter()-t
  cache_start=time.perf_counter();self.prefix_ids=None;self.prefix_cache=None
  if args.cache_prefix:
   marker='__TRUSTXAI_SLOT_9F__';messages=[{'role':'system','content':PROMPT['system']},{'role':'user','content':PROMPT['user_template'].format(message=marker)}]
   full=self.tok.apply_chat_template(messages,tokenize=False,add_generation_prompt=True,enable_thinking=not args.disable_thinking)
   if full.count(marker)!=1:raise RuntimeError('Static prefix marker ambiguity')
   prefix_text=full.split(marker)[0];prefix_text=prefix_text.rsplit('\n',1)[0]+'\n'
   self.prefix_ids=self.tok.encode(prefix_text,add_special_tokens=False)
   ids=torch.tensor([self.prefix_ids])
   with torch.inference_mode():self.prefix_cache=self.m(input_ids=ids,attention_mask=torch.ones_like(ids),use_cache=True,logits_to_keep=1).past_key_values
  self.prefix_setup_s=time.perf_counter()-cache_start
  self.renderer=self.m;self.renderer_setup_s=0.0
  if args.phase=='rendering' and args.renderer_profile=='dynamic-qint8':
   quant_start=time.perf_counter()
   renderer=AutoModelForCausalLM.from_pretrained(p,local_files_only=True,trust_remote_code=False,use_safetensors=True,dtype=torch.float32,attn_implementation='sdpa').eval()
   self.renderer=torch.ao.quantization.quantize_dynamic(renderer,{torch.nn.Linear},dtype=torch.qint8,inplace=True).eval()
   self.renderer_setup_s=time.perf_counter()-quant_start
   self.quantized_linear_layers=sum(isinstance(layer,torch.ao.nn.quantized.dynamic.Linear) for layer in self.renderer.modules())
   if self.quantized_linear_layers==0:raise RuntimeError('No Linear layers quantized')
   if rss()>24:raise RuntimeError('Combined model load exceeded24GiB RSS gate')
   print('Renderer profile dynamic-qint8; Linear layers',self.quantized_linear_layers,'setup_seconds',round(self.renderer_setup_s,2),'peak_RSS_GiB',round(rss(),3),flush=True)
  elif args.phase=='rendering' and args.renderer_profile=='separate-bfloat16':
   start=time.perf_counter()
   self.renderer=AutoModelForCausalLM.from_pretrained(p,local_files_only=True,trust_remote_code=False,use_safetensors=True,dtype=torch.bfloat16,attn_implementation='sdpa').eval()
   self.renderer_setup_s=time.perf_counter()-start
   if rss()>24:raise RuntimeError('Combined model load exceeded24GiB RSS gate')
   print('Renderer profile separate-bfloat16; generation_threads',args.generation_threads,'peak_RSS_GiB',round(rss(),3),flush=True)
 def inputs(self,system,user):
  messages=[{'role':'system','content':system},{'role':'user','content':user}]
  return self.tok.apply_chat_template(messages,tokenize=True,add_generation_prompt=True,return_tensors='pt',return_dict=True,enable_thinking=not args.disable_thinking)
 @torch.inference_mode()
 def score(self,text):
  start=time.perf_counter()
  messages=[{'role':'system','content':PROMPT['system']},{'role':'user','content':PROMPT['user_template'].format(message=text)}]
  prefix_text=self.tok.apply_chat_template(messages,tokenize=False,add_generation_prompt=True,enable_thinking=not args.disable_thinking)
  inp=self.tok(prefix_text,add_special_tokens=False,return_tensors='pt');prefix=inp['input_ids'][0].tolist();suffixes={}
  for lab,candidate in [('A',args.label_a),('B',args.label_b)]:
   full=self.tok.encode(prefix_text+candidate,add_special_tokens=False)
   if full[:len(prefix)]!=prefix:raise RuntimeError('Candidate tokenization changes prefix boundary')
   suffixes[lab]=full[len(prefix):]
   if not suffixes[lab] or len(full)>512:raise RuntimeError('Label/context scoring bounds failed')
  if all(len(v)==1 for v in suffixes.values()):
   if args.cache_prefix:
    n=len(self.prefix_ids)
    if prefix[:n]!=self.prefix_ids:raise RuntimeError('Static prefix identity mismatch')
    kwargs={'input_ids':inp['input_ids'][:,n:],'attention_mask':inp['attention_mask'],'past_key_values':copy.deepcopy(self.prefix_cache),'cache_position':torch.arange(n,len(prefix)),'use_cache':True,'logits_to_keep':1}
   else:kwargs={**inp,'use_cache':False,'logits_to_keep':1}
   lp=self.m(**kwargs).logits[0,-1].float().log_softmax(-1)
   a,b=[float(lp[suffixes[lab][0]])for lab in ['A','B']]
  else:
   values=[]
   for lab in ['A','B']:
    full=prefix+suffixes[lab];ids=torch.tensor([full]);logits=self.m(input_ids=ids,attention_mask=torch.ones_like(ids),use_cache=False).logits[0]
    values.append(sum(float(logits[len(prefix)-1+j].float().log_softmax(-1)[token])for j,token in enumerate(suffixes[lab])))
   a,b=values
  return {'label':'A' if a>=b else 'B','logp_A':a,'logp_B':b,'spam_log_odds':b-a,'context_tokens':len(prefix),'candidate_token_ids':suffixes,'seconds':time.perf_counter()-start}
 def score_exact(self,text):
  previous=args.cache_prefix;args.cache_prefix=False
  try:return self.score(text)
  finally:args.cache_prefix=previous
 @torch.inference_mode()
 def generate(self,system,user,cap,seed=20261027,sample=False):
  torch.manual_seed(seed);inp=self.inputs(system,user);n=inp['input_ids'].shape[-1]
  if n+cap>4096:raise RuntimeError('Generation context limit; no truncation')
  kwargs={'max_new_tokens':cap,'do_sample':sample,'pad_token_id':self.tok.eos_token_id}
  if sample:kwargs.update(temperature=0.7,top_p=0.9,top_k=50)
  else:kwargs.update(temperature=None,top_p=None,top_k=None)
  previous_threads=torch.get_num_threads();torch.set_num_threads(args.generation_threads)
  start=time.perf_counter();cpu_start=time.process_time()
  try:out=self.renderer.generate(**inp,**kwargs)
  finally:torch.set_num_threads(previous_threads)
  elapsed=time.perf_counter()-start;cpu_elapsed=time.process_time()-cpu_start
  tail=out[0,n:];text=self.tok.decode(tail,skip_special_tokens=True)
  return {'text':text,'seconds':elapsed,'CPU_seconds':cpu_elapsed,'new_tokens':len(tail),'context_tokens':n,'seed':seed,'sampling':sample,'cap':cap,'hit_cap':len(tail)>=cap,'generation_profile':args.renderer_profile,'generation_threads':args.generation_threads}
def edit_distance(a,b):
 prev=list(range(len(b)+1))
 for i,x in enumerate(a,1):
  cur=[i]
  for j,y in enumerate(b,1):cur.append(min(cur[-1]+1,prev[j]+1,prev[j-1]+(x!=y)))
  prev=cur
 return prev[-1]
def schema_valid(raw):
 try:
  x=json.loads(raw)
  if set(x)!= {'novice','expert'}:return False
  for k in ['novice','expert']:
   if not isinstance(x[k],list) or len(x[k])!=4:return False
   if [q.get('claim_id') for q in x[k]]!=['C1','C2','C3','C4']:return False
   if not all(set(q)=={'claim_id','text'} and isinstance(q['text'],str) and q['text'].strip() for q in x[k]):return False
  return True
 except (ValueError,TypeError,KeyError,AttributeError):return False
if args.phase=='classification':
 out=PUBLIC/('CLASSIFICATION_PILOT'+args.suffix+'.json')
 if out.exists():raise SystemExit('Pilot already exists; preserve it and use a new declared run ID for changes.')
 target=Target();results=[];print('Target loaded; RSSGiB',round(rss(),3),flush=True)
 for row in ROWS:
  assert hashlib.sha256(row['text'].encode()).hexdigest()==row['text_sha256']
  r=target.score(row['text']);r.update(source_id=row['source_id'],true_label={'ham':'A','spam':'B'}[row['label']],input_sha256=row['text_sha256']);results.append(r)
  write(PRIVATE/'classification_progress.json',results)
  print('Scored',len(results),'of20; seconds',round(r['seconds'],3),flush=True)
 y=[r['true_label'] for r in results];pred=[r['label'] for r in results]
 summary={'run_id':args.run_tag,'model':MODEL,'revision':META[MODEL]['revision'],'prompt_sha256':hashlib.sha256((PUBLIC/args.prompt_file).read_bytes()).hexdigest(),'phase':'feasibility only','enable_thinking':not args.disable_thinking,'candidate_label_texts':{'A':args.label_a,'B':args.label_b},'sources':20,'balanced_accuracy':balanced_accuracy_score(y,pred),'macro_f1':f1_score(y,pred,labels=['A','B'],average='macro'),'correct':sum(a==b for a,b in zip(y,pred)),'confusion_matrix_rows_true_cols_pred_A_B':confusion_matrix(y,pred,labels=['A','B']).tolist(),'median_target_seconds':statistics.median(r['seconds'] for r in results),'load_seconds':target.load_s,'peak_rss_GiB':rss(),'dtype':'float32','torch_threads':4,'test_sources_scored':0,'classification_gate_pass':balanced_accuracy_score(y,pred)>=0.65,'latency_gate_pass':statistics.median(r['seconds'] for r in results)<=5,'memory_gate_pass':rss()<=24,'results':results}
 write(out,summary);print('SUMMARY',json.dumps({k:v for k,v in summary.items() if k!='results'}),flush=True)
elif args.phase=='rendering':
 out=PUBLIC/('RENDERING_PILOT'+args.suffix+'.json')
 if out.exists():raise SystemExit('Rendering pilot already exists; preserve before amendments.')
 prior_suffix=args.suffix if args.classification_suffix is None else args.classification_suffix
 prior=json.loads((PUBLIC/('CLASSIFICATION_PILOT'+prior_suffix+'.json')).read_text());assert prior['revision']==META[MODEL]['revision']
 assert prior['prompt_sha256']==hashlib.sha256((PUBLIC/args.prompt_file).read_bytes()).hexdigest()
 assert prior['candidate_label_texts']=={'A':args.label_a,'B':args.label_b}
 assert prior['enable_thinking']==(not args.disable_thinking)
 chosen=sorted([r for lab in ['ham','spam'] for r in [x for x in ROWS if x['label']==lab][:5]],key=lambda r:r['source_id'])
 assert len(chosen)==10
 write(PRIVATE/'render_source_selection.json',[r['source_id'] for r in chosen])
 target=Target();records=[]
 for index,row in enumerate(chosen):
  start=time.perf_counter();case_cpu_start=time.process_time();text=row['text'];original=target.score_exact(text);expected=next(r for r in prior['results']if r['source_id']==row['source_id']);assert original['label']==expected['label'];assert abs(original['logp_A']-expected['logp_A'])<0.0001 and abs(original['logp_B']-expected['logp_B'])<0.0001;letter=original['label'];name={'A':'ham','B':'spam'}[letter]
  base=(original['logp_B']-original['logp_A'])*(1 if letter=='B' else -1);deletions=[]
  for span in re.finditer(r'\S+',text):
   left,right=text[:span.start()],text[span.end():]
   edited=left.rstrip()+' '+right.lstrip() if left.strip() and right.strip() else left.rstrip() if left.strip() else right.lstrip()
   s=target.score(edited);value=(s['logp_B']-s['logp_A'])*(1 if letter=='B' else -1)
   deletions.append({'span':span.group(),'start':span.start(),'end':span.end(),'delta':base-value,'score':s})
  top=max(deletions,key=lambda r:(abs(r['delta']),-r['start']));delta=top['delta'];feature=top['span']
  print('Source',index+1,'deletion tests complete',len(deletions),flush=True)
  if abs(delta)<0.0001:c2=f'Removing the span {feature!r} showed no change above 0.0001 in the model decision-class log-odds under this deletion test.'
  else:c2=f'Removing the span {feature!r} '+('lowered' if delta>0 else 'raised')+f' the model {name}-versus-'+('ham' if name=='spam' else 'spam')+f' log-odds by {abs(delta):.4f} under this deletion test.'
  wanted='B' if letter=='A' else 'A';cap=min(6,max(1,int(0.25*len(text.split()))));attempts=[];seen=set();successes=[]
  for attempt in range(3):
   g=target.generate('Edit SMS text for a local model-behavior experiment. Return only one edited message, no explanation.',f'Original SMS:\n{text}\nDesired classification: '+{'A':'ham','B':'spam'}[wanted]+f'. Change at most {cap} whitespace words. Preserve as much of the original as possible. Candidate {attempt+1}: use a different minimal edit from earlier candidates. Return the edited SMS only.',96,20261027+index*10+attempt,True)
   candidate=g['text'].strip()
   if len(candidate)>1 and candidate[0]==candidate[-1] and candidate[0] in ['"',"'"]:candidate=candidate[1:-1]
   distance=edit_distance(text.split(),candidate.split());valid=bool(candidate) and '\n' not in candidate and candidate not in seen and 0<distance<=cap
   a={'generation':g,'candidate':candidate,'distance':distance,'within_constraints':valid};seen.add(candidate)
   if valid:
    s=target.score_exact(candidate);a['score']=s;a['target_success']=s['label']==wanted
    if a['target_success']:successes.append(a)
   attempts.append(a)
   print('Source',index+1,'CF attempt',attempt+1,'generation_seconds',round(g['seconds'],2),'valid_edit',valid,flush=True)
   if successes:break
  selected=min(successes,key=lambda a:a['distance']) if successes else next((a for a in attempts if 'score'in a),None)
  retest=target.score_exact(selected['candidate']) if selected else None
  if successes:c3=f'The exact selected edited SMS returned model label '+{'A':'ham','B':'spam'}[selected['score']['label']]+f' rather than the original {name}. This is an observed model result, not a guaranteed real-world outcome.'
  else:c3=f'No successful '+{'A':'ham','B':'spam'}[wanted]+f' edit was found in {len(attempts)} generation attempts; {sum("score"in a for a in attempts)} candidate messages were actually evaluated by the target model. This does not show that no successful edit exists.'
  facts={'C1':f'The recorded model decision is {name}. It is not independently verified real-world truth.','C2':c2,'C3':c3,'C4':'These deletion and edit observations do not prove real-world causation or expose the model complete internal reasoning.'}
  sys='Write two audience views from fixed evidence. Preserve all supplied facts, labels, numbers, units and limitations. Do not invent new claims. Output only valid JSON, with no Markdown fences.'
  schema_example={audience:[{'claim_id':cid,'text':'Replace with the audience-appropriate rendering of '+cid} for cid in facts] for audience in ['novice','expert']}
  usr='Essential claims:\n'+json.dumps(facts,ensure_ascii=False)+'\nUse this exact JSON structure, replacing each text value with the rendered claim:\n'+json.dumps(schema_example)+'\nEach view must contain four objects in C1,C2,C3,C4 order. Use plain wording for novice and technical wording for expert, with identical facts. Output no explanation outside JSON. First character { and last character }.'
  rendered=target.generate(sys,usr,512)
  raw={'source_id':row['source_id'],'original':original,'deletions':deletions,'counterfactual_attempts':attempts,'selected_retest':retest,'facts':facts,'rendering':rendered,'schema_valid':schema_valid(rendered['text'])};write(PRIVATE/(row['source_id']+'_render.json'),raw)
  rec={'source_id':row['source_id'],'deletion_tests':len(deletions),'deletion_total_seconds':sum(d['score']['seconds'] for d in deletions),'CF_attempts':len(attempts),'CF_generation_seconds':sum(a['generation']['seconds'] for a in attempts),'CF_generation_tokens':sum(a['generation']['new_tokens'] for a in attempts),'CF_evaluated':sum('score'in a for a in attempts),'CF_target_success':bool(successes),'CF_retest_label_agrees':retest['label']==selected['score']['label'] if selected else None,'informative_evidence_available':bool(selected),'pair_json_valid':schema_valid(rendered['text']),'pair_generation_seconds':rendered['seconds'],'pair_generation_tokens':rendered['new_tokens'],'pair_context_tokens':rendered['context_tokens'],'hit_token_cap':rendered['hit_cap'],'total_case_seconds':time.perf_counter()-start,'peak_rss_GiB':rss()};records.append(rec);write(PRIVATE/'render_progress_public.json',records)
  rec.update(pair_generation_CPU_seconds=rendered['CPU_seconds'],CF_generation_CPU_seconds=sum(a['generation']['CPU_seconds'] for a in attempts),total_case_CPU_seconds=time.process_time()-case_cpu_start)
  write(PRIVATE/'render_progress_public.json',records)
  print('Rendered',len(records),'of10; validJSON',rec['pair_json_valid'],'generation_seconds',round(rec['pair_generation_seconds'],2),flush=True)
 summary={'run_id':args.run_tag,'model':MODEL,'revision':META[MODEL]['revision'],'sources':10,'source_selection':'first5per original class in fixed feasibility order; not selected by predictions','valid_json_fraction':sum(r['pair_json_valid'] for r in records)/10,'median_pair_generation_seconds':statistics.median(r['pair_generation_seconds'] for r in records),'median_case_seconds_including_evidence':statistics.median(r['total_case_seconds'] for r in records),'median_tokens_per_second':statistics.median(r['pair_generation_tokens']/r['pair_generation_seconds'] for r in records),'peak_rss_GiB':rss(),'json_gate_pass':sum(r['pair_json_valid'] for r in records)>=8,'generation_latency_gate_pass':statistics.median(r['pair_generation_seconds'] for r in records)<=120,'memory_gate_pass':rss()<=24,'semantic_preservation_evaluated':False,'enable_thinking':not args.disable_thinking,'test_sources_used':0,'CF_sampling_temperature':0.7,'CF_top_p':0.9,'repair_experiment_run':False,'score_prefix_cache':args.cache_prefix,'cache_scope':'deletion attribution only; original/CF/retest calls uncached','prefix_cache_setup_seconds':target.prefix_setup_s,'results':records}
 summary.update(renderer_profile=args.renderer_profile,generation_threads=args.generation_threads,renderer_setup_seconds=target.renderer_setup_s,target_dtype='float32',classification_results_file='CLASSIFICATION_PILOT'+prior_suffix+'.json',process_CPU_seconds=time.process_time())
 write(out,summary);print('SUMMARY',json.dumps({k:v for k,v in summary.items() if k!='results'}),flush=True)
else:
 name='cross-encoder/nli-deberta-v3-base';p=model_path(name);start=time.perf_counter();tok=AutoTokenizer.from_pretrained(p,local_files_only=True,trust_remote_code=False);m=AutoModelForSequenceClassification.from_pretrained(p,local_files_only=True,trust_remote_code=False,use_safetensors=True,dtype=torch.float32).eval();load=time.perf_counter()-start
 cases=[('The recorded model decision is spam.','The recorded model decision is spam.','entailment'),('The recorded model decision is spam.','The recorded model decision is ham.','contradiction'),('The tested edit returned ham.','The tested edit returned spam.','contradiction'),('The tested edit returned ham.','The system has complete knowledge of every possible edit.','neutral')]
 inp=tok([x[0]for x in cases],[x[1]for x in cases],padding=True,truncation=False,return_tensors='pt');start=time.perf_counter()
 with torch.inference_mode():scores=m(**inp).logits.softmax(-1)
 duration=time.perf_counter()-start;ids={int(k):v for k,v in m.config.id2label.items()};assert set(ids.values())=={'contradiction','entailment','neutral'}
 results=[{'premise':a,'hypothesis':b,'expected_smoke_label':c,'predicted':ids[int(scores[i].argmax())],'scores':{ids[j]:float(scores[i,j])for j in ids}}for i,(a,b,c)in enumerate(cases)]
 out={'model':name,'revision':META[name]['revision'],'label_mapping':ids,'synthetic_smoke_cases':results,'load_seconds':load,'batch_inference_seconds':duration,'peak_rss_GiB':rss(),'not_a_checker_accuracy_benchmark':True,'heldout_sources_used':0}
 write(PUBLIC/'NLI_SMOKE.json',out);print(json.dumps(out),flush=True)
