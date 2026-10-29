"""Four independent bounded HTTPS ranges; assemble in order and verify publisher SHA256."""
from pathlib import Path
import urllib.request,json,hashlib,concurrent.futures,time
B=Path('/workspace/TRUSTXAI/research/step-04');name='Qwen/Qwen3-1.7B';meta=json.loads((B/'evidence/Qwen__Qwen3-1.7B_metadata.json').read_text());rev=meta['sha'];dest=Path('/workspace/thesis-runtime/models/Qwen3-1.7B')/rev;segments=dest/'range_parts';segments.mkdir(exist_ok=True)
entries=[x for x in meta['siblings']if x['rfilename'].endswith('.safetensors')];jobs=[];plans={}
for ent in entries:
 out=dest/ent['rfilename'];part=dest/(ent['rfilename']+'.part')
 start=out.stat().st_size if out.exists() else part.stat().st_size if part.exists()else 0
 if start>ent['size']:raise RuntimeError('Partial oversized; refuse')
 plans[ent['rfilename']]=[]
 for a in range(start,ent['size'],64*1024*1024):
  z=min(a+64*1024*1024-1,ent['size']-1);f=segments/(ent['rfilename']+f'.{a}-{z}');job=(ent,a,z,f);jobs.append(job);plans[ent['rfilename']].append(job)
def transfer(job):
 ent,start,end,f=job;size=end-start+1
 for trial in range(3):
  offset=start+(f.stat().st_size if f.exists()else 0)
  if offset==end+1:return f
  if offset>end+1:raise RuntimeError('Segment oversized')
  url=f"https://huggingface.co/{name}/resolve/{rev}/{ent['rfilename']}?download=true"
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'Range':f'bytes={offset}-{end}'}),timeout=90) as r:
    if r.status!=206 or not r.headers.get('Content-Range','').startswith(f'bytes {offset}-'):raise RuntimeError('Range offset mismatch')
    remaining=end-offset+1
    with f.open('ab')as w:
     while remaining:
      d=r.read(min(4*1024*1024,remaining))
      if not d:raise OSError('Short segment; resume actual written offset')
      w.write(d);remaining-=len(d)
   if f.stat().st_size!=size:raise RuntimeError('Segment size mismatch')
   return f
  except OSError:
   if trial==2:raise
   time.sleep(1)
 raise RuntimeError('Transfer incomplete')
with concurrent.futures.ThreadPoolExecutor(4)as pool:
 futures=[pool.submit(transfer,j)for j in jobs]
 for i,f in enumerate(concurrent.futures.as_completed(futures),1):
  f.result();print('Verified range lengths',i,'of',len(jobs),flush=True)
records=[]
for ent in entries:
 out=dest/ent['rfilename'];part=dest/(ent['rfilename']+'.part')
 if not out.exists():
  with part.open('ab')as w:
   for job in plans[ent['rfilename']]:
    with job[3].open('rb')as r:
     for chunk in iter(lambda:r.read(4*1024*1024),b''):w.write(chunk)
  if part.stat().st_size!=ent['size']:raise RuntimeError('Assembled size mismatch')
  part.rename(out)
 h=hashlib.sha256()
 with out.open('rb')as r:
  for chunk in iter(lambda:r.read(4*1024*1024),b''):h.update(chunk)
 if h.hexdigest()!=ent['lfs']['sha256']:raise RuntimeError('Publisher checksum mismatch; artifact unusable')
 records.append({'name':ent['rfilename'],'bytes':ent['size'],'sha256':h.hexdigest(),'matches_hub_lfs_digest':True})
 for job in plans[ent['rfilename']]:job[3].unlink()
 print('Publisher SHA256 matched',ent['rfilename'],flush=True)
m=json.loads((B/'evidence/MODEL_REVISIONS.json').read_text());m[name].update(local_path=str(dest),weights_sha256_verified=True,files=records);(B/'evidence/MODEL_REVISIONS.json').write_text(json.dumps(m,indent=2));print('Alternative verified and usable',flush=True)
