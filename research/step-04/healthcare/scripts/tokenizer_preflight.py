"""Mechanical tokenization only; no model predictions or task outcomes."""
from pathlib import Path
import argparse,json,csv,hashlib,os
from transformers import AutoTokenizer
p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--prompt',required=True);p.add_argument('--suffix',required=True);a=p.parse_args()
B=Path(__file__).resolve().parents[1];R=Path(os.environ.get('TRUSTXAI_RUNTIME','/workspace/thesis-runtime'))/'healthcare';M=json.loads((B.parent/'evidence/MODEL_REVISIONS.json').read_text())[a.model];t=AutoTokenizer.from_pretrained(M['local_path'],local_files_only=True);prompt=json.loads((B/a.prompt).read_text());raw=json.loads((R/'source/data/ori_pqal.json').read_text());manifest=list(csv.DictReader((B/'SPLIT_MANIFEST.csv').open()));records=[]
for rec in manifest:
 x=raw[rec['source_id']];u=prompt['user_template'].format(question=x['QUESTION'],context='\n\n'.join(f'[S{i+1}] {v}'for i,v in enumerate(x['CONTEXTS'])))
 ids=t.apply_chat_template([{'role':'system','content':prompt['system']},{'role':'user','content':u}],tokenize=True,add_generation_prompt=True,enable_thinking=False)
 assert len(ids)<=1536
 records.append({'source_id':rec['source_id'],'partition':rec['partition'],'prompt_tokens':len(ids)})
out={'model':a.model,'revision':M['revision'],'prompt_sha256':hashlib.sha256((B/a.prompt).read_bytes()).hexdigest(),'sources':len(records),'max_prompt_tokens':max(r['prompt_tokens']for r in records),'cap':1536,'truncation':False,'target_inference_run':False,'test_model_inference_run':False,'records':records}
(B/('TOKENIZER_PREFLIGHT'+a.suffix+'.json')).write_text(json.dumps(out,indent=2));print({k:v for k,v in out.items()if k!='records'})
