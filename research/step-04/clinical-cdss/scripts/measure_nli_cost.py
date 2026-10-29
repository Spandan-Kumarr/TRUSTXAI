"""Synthetic shape/timing probe only; NOT NLI correctness or biomedical validation."""
from pathlib import Path
import json,time,resource,os,statistics
os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
import torch
from transformers import AutoTokenizer,AutoModelForSequenceClassification
B=Path(__file__).resolve().parents[1];M=json.loads((B.parent/'evidence/MODEL_REVISIONS.json').read_text())['cross-encoder/nli-deberta-v3-base'];assert M['weights_sha256_verified']
torch.set_num_threads(4);torch.set_num_interop_threads(1);torch.manual_seed(20261027)
tok=AutoTokenizer.from_pretrained(M['local_path'],local_files_only=True);m=AutoModelForSequenceClassification.from_pretrained(M['local_path'],local_files_only=True,use_safetensors=True,trust_remote_code=False,dtype=torch.float32).eval()
record=[];base=tok.encode('The recorded option was A. Omitting the selected case span returned C. This is an observed input omission test.',add_special_tokens=False)
for length in [128,256,512]:
 for repeat in range(2):
  # Fixed valid token IDs produce declared shapes; predictions intentionally not interpreted.
  content=(base*((length//len(base))+1))[:length-2];seq=[tok.cls_token_id]+content+[tok.sep_token_id];assert len(seq)==length
  ids=torch.tensor([seq]*8);mask=torch.ones_like(ids);start=time.perf_counter();cpu=time.process_time()
  with torch.inference_mode():out=m(input_ids=ids,attention_mask=mask).logits
  assert out.shape==(8,3)and torch.isfinite(out).all()
  record.append({'batch':8,'tokens':length,'repeat':repeat,'wall_seconds':time.perf_counter()-start,'CPU_seconds':time.process_time()-cpu})
summary={'model':'cross-encoder/nli-deberta-v3-base','revision':M['revision'],'batch':8,'threads':4,'dtype':'float32','records':record,'median_CPU_seconds_per_pair_by_tokens':{str(n):statistics.median(x['CPU_seconds']/8 for x in record if x['tokens']==n)for n in [128,256,512]},'peak_RSS_GiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/(1024**2),'semantic_accuracy_evaluated':False,'healthcare_sources_used':0}
(B/'NLI_COST_PROBE.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
