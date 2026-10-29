"""Pinned publisher artifacts via bounded HTTPS ranges; final LFS SHA256 mandatory."""
from pathlib import Path
import os,json,urllib.request,time,hashlib,shutil
os.environ['HF_HOME']='/workspace/thesis-runtime/cache/huggingface';os.environ['HF_HUB_DISABLE_XET']='1';os.environ['HF_HUB_DISABLE_PROGRESS_BARS']='1'
from huggingface_hub import snapshot_download
B=Path('/workspace/TRUSTXAI/research/step-04');name='Qwen/Qwen3-1.7B';meta=json.loads((B/'evidence/Qwen__Qwen3-1.7B_metadata.json').read_text());rev=meta['sha'];dest=Path('/workspace/thesis-runtime/models/Qwen3-1.7B')/rev;dest.mkdir(parents=True,exist_ok=True)
p=Path(snapshot_download(name,revision=rev,allow_patterns=['*.json','*.model','merges.txt','vocab.json','README.md','LICENSE'],max_workers=2))
for f in p.iterdir():
 if f.is_file():shutil.copy2(f,dest/f.name)
records=[]
for entry in meta['siblings']:
 if not entry['rfilename'].endswith('.safetensors'):continue
 filename=entry['rfilename'];expected=entry['lfs']['sha256'];size=entry['size'];out=dest/filename;partial=dest/(filename+'.part')
 if not out.exists():
  url=f'https://huggingface.co/{name}/resolve/{rev}/{filename}?download=true'
  while (partial.stat().st_size if partial.exists()else 0)<size:
   offset=partial.stat().st_size if partial.exists()else 0;end=min(size-1,offset+64*1024*1024-1)
   try:
    with urllib.request.urlopen(urllib.request.Request(url,headers={'Range':f'bytes={offset}-{end}'}),timeout=90) as r:
     cr=r.headers.get('Content-Range','')
     if r.status!=206 or not cr.startswith(f'bytes {offset}-'):raise RuntimeError('Range response inconsistent; artifact not accepted')
     remaining=end-offset+1
     with partial.open('ab')as f:
      while remaining:
       d=r.read(min(4*1024*1024,remaining))
       if not d:raise RuntimeError('Short range response; resume from actual written offset')
       f.write(d);remaining-=len(d)
    if partial.stat().st_size%(256*1024*1024)<64*1024*1024:print(filename,'bytes',partial.stat().st_size,'of',size,flush=True)
   except (OSError,RuntimeError)as ex:
    print('Transfer interruption',type(ex).__name__,'; partial retained; no checksum override',flush=True);raise
  if partial.stat().st_size!=size:raise RuntimeError('Unexpected weight size')
  partial.rename(out)
 h=hashlib.sha256()
 with out.open('rb')as f:
  for chunk in iter(lambda:f.read(4*1024*1024),b''):h.update(chunk)
 if h.hexdigest()!=expected:raise RuntimeError('Weight digest mismatch; do not use')
 records.append({'name':filename,'bytes':size,'sha256':h.hexdigest(),'matches_hub_lfs_digest':True});print('SHA256verified',filename,flush=True)
manifest=json.loads((B/'evidence/MODEL_REVISIONS.json').read_text());manifest[name].update(local_path=str(dest),weights_sha256_verified=True,files=records);(B/'evidence/MODEL_REVISIONS.json').write_text(json.dumps(manifest,indent=2))
print('Alternative model pinned files verified',flush=True)
