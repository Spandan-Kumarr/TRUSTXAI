"""Mechanical input/label validation only; scores no source through the target model."""
from pathlib import Path
import json,csv,hashlib
from transformers import AutoTokenizer
B=Path('/workspace/TRUSTXAI/research/step-04');name='Qwen/Qwen3-1.7B';meta=json.loads((B/'evidence/MODEL_REVISIONS.json').read_text())[name];path=Path('/workspace/thesis-runtime/models/Qwen3-1.7B')/meta['revision'];tok=AutoTokenizer.from_pretrained(str(path),local_files_only=True,trust_remote_code=False)
prompt=json.loads((B/'feasibility/CLASSIFICATION_PROMPT_V3.json').read_text());manifest=list(csv.DictReader((B/'feasibility/SPLIT_MANIFEST.csv').open()));ids={r['source_id']:r for r in manifest};source={}
with Path('/workspace/thesis-runtime/data/SMSSpamCollection').open(encoding='utf-8',newline='')as f:
 for i,line in enumerate(f):
  sid=f'uci228-{i:05d}'
  if sid in ids:source[sid]=line.rstrip('\r\n').split('\t',1)[1]
checks=[]
for sid,record in ids.items():
 text=source[sid];assert hashlib.sha256(text.encode()).hexdigest()==record['text_sha256']
 messages=[{'role':'system','content':prompt['system']},{'role':'user','content':prompt['user_template'].format(message=text)}]
 full=tok.apply_chat_template(messages,tokenize=False,add_generation_prompt=True,enable_thinking=False);prefix=tok.encode(full,add_special_tokens=False);labels={}
 for k in ['ham','spam']:
  joined=tok.encode(full+k,add_special_tokens=False);assert joined[:len(prefix)]==prefix;labels[k]=joined[len(prefix):];assert labels[k]
 assert max(len(prefix)+len(v)for v in labels.values())<=512
 checks.append({'source_id':sid,'partition':record['partition'],'context_tokens':len(prefix),'label_tokens':labels})
result={'model':name,'revision':meta['revision'],'prompt_sha256':hashlib.sha256((B/'feasibility/CLASSIFICATION_PROMPT_V3.json').read_bytes()).hexdigest(),'enable_thinking':False,'sources_mechanically_checked':len(checks),'feasibility_sources':sum(c['partition']=='feasibility'for c in checks),'max_context_tokens':max(c['context_tokens']for c in checks),'label_token_ids':checks[0]['label_tokens'],'all_candidate_prefixes_stable':True,'target_inference_run':False,'test_target_inference_run':False,'details':checks}
(B/'feasibility/TOKENIZER_PREFLIGHT_Q3.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items()if k!='details'}))
