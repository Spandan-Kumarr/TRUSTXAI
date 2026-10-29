"""Resume pinned public model downloads after network update; verify weight digests.
No token extraction, TLS bypass, alternate proxy or expected-checksum changes.
"""
import os
os.environ['HF_HOME']='/workspace/thesis-runtime/cache/huggingface'
os.environ['HF_HUB_DISABLE_XET']='1'  # Supported ordinary HTTPS transfer; TLS/hash verification retained.
os.environ['HF_HUB_DISABLE_PROGRESS_BARS']='1'
from pathlib import Path
import json,hashlib,urllib.request,urllib.parse
from huggingface_hub import snapshot_download
B=Path('/workspace/TRUSTXAI/research/step-04');manifest=json.loads((B/'evidence/MODEL_REVISIONS.json').read_text())
class Redirects(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  print('Weight host:',urllib.parse.urlparse(newurl).hostname,flush=True)
  return super().redirect_request(req,fp,code,msg,headers,newurl)
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(4*1024*1024),b''):h.update(chunk)
 return h.hexdigest()
for model in ['Qwen/Qwen2.5-1.5B-Instruct','cross-encoder/nli-deberta-v3-base']:
 m=manifest[model];rev=m['revision'];meta=json.loads((B/'evidence'/(model.replace('/','__')+'_metadata.json')).read_text())
 expected={s['rfilename']:s.get('lfs',{}).get('sha256') for s in meta['siblings'] if s.get('lfs')}
 url=f'https://huggingface.co/{model}/resolve/{rev}/model.safetensors'
 try:
  with urllib.request.build_opener(Redirects()).open(urllib.request.Request(url,headers={'Range':'bytes=0-15'}),timeout=25) as r:r.read(16)
 except Exception as ex:
  raise SystemExit('Public weight delivery preflight failed: '+type(ex).__name__+'. Check recorded redirect host and network settings; no signed URL printed.')
 path=Path(snapshot_download(model,revision=rev,allow_patterns=['*.json','*.safetensors','*.model','merges.txt','vocab.json','README.md','LICENSE'],max_workers=2))
 records=[];weights=0
 for p in sorted(path.glob('*')):
  if not p.is_file():continue
  h=digest(p);known=expected.get(p.name)
  if p.name.endswith('.safetensors'):
   if not known:raise RuntimeError('No publisher LFS digest for weight file')
   if h!=known:raise RuntimeError('Weight checksum mismatch; do not use artifact')
   weights+=1
  elif known and h!=known:raise RuntimeError('Artifact checksum mismatch')
  records.append({'name':p.name,'bytes':p.stat().st_size,'sha256':h,'matches_hub_lfs_digest':h==known if known else None})
 if not weights:raise RuntimeError('No verified safetensors weights downloaded')
 m.update(local_path=str(path),files=records,download_error=None,weights_sha256_verified=True)
 (B/'evidence/MODEL_REVISIONS.json').write_text(json.dumps(manifest,indent=2))
 print('Pinned weights verified:',model,weights,flush=True)
