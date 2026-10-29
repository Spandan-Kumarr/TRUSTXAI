"""Official pinned public artifacts; bounded resumable HTTPS ranges and publisher SHA256."""
from pathlib import Path
import urllib.request,json,hashlib,concurrent.futures,time,os
B=Path(__file__).resolve().parents[1];R=Path(os.environ.get('TRUSTXAI_RUNTIME','/workspace/thesis-runtime'));name='Qwen/Qwen3-4B-Instruct-2507'
metadata_path=R/'healthcare/Qwen3-4B_metadata.json'
if not metadata_path.exists():
 metadata_url='https://huggingface.co/api/models/Qwen/Qwen3-4B-Instruct-2507/revision/cdbee75f17c01a7cc42f958dc650907174af0554?blobs=true'
 with urllib.request.urlopen(metadata_url,timeout=30) as response:metadata_path.write_bytes(response.read())
meta=json.loads(metadata_path.read_text());rev=meta['sha'];assert rev=='cdbee75f17c01a7cc42f958dc650907174af0554';dest=R/'models/Qwen3-4B-Instruct-2507'/rev;dest.mkdir(parents=True,exist_ok=True);segments=dest/'range_parts';segments.mkdir(exist_ok=True)
assert meta.get('gated') is False and meta.get('cardData',{}).get('license')=='apache-2.0'
small=['model.safetensors.index.json','config.json','generation_config.json','tokenizer_config.json','tokenizer.json','merges.txt','vocab.json','README.md','LICENSE']
for file in small:
 url=f'https://huggingface.co/{name}/resolve/{rev}/{file}'
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'TRUSTXAI-research'}),timeout=30)as r:data=r.read(30000000)
 (dest/file).write_bytes(data)
 if file in ['README.md','LICENSE']:(B/'evidence'/('Qwen3-4B_'+file)).write_bytes(data)
(B/'evidence/Qwen3-4B_metadata.json').write_text(json.dumps(meta,indent=2))
entries=[x for x in meta['siblings']if x['rfilename'].endswith('.safetensors')];jobs=[];plans={}
for ent in entries:
 out=dest/ent['rfilename'];part=dest/(ent['rfilename']+'.part');start=out.stat().st_size if out.exists()else part.stat().st_size if part.exists()else 0
 if start>ent['size']:raise RuntimeError('Oversized partial')
 plans[ent['rfilename']]=[]
 for a in range(start,ent['size'],64*1024*1024):
  z=min(a+64*1024*1024-1,ent['size']-1);f=segments/(ent['rfilename']+f'.{a}-{z}');job=(ent,a,z,f);jobs.append(job);plans[ent['rfilename']].append(job)
def transfer(job):
 ent,start,end,f=job;size=end-start+1
 for trial in range(3):
  offset=start+(f.stat().st_size if f.exists()else 0)
  if offset==end+1:return
  if offset>end+1:raise RuntimeError('Oversized range')
  try:
   url=f"https://huggingface.co/{name}/resolve/{rev}/{ent['rfilename']}?download=true"
   with urllib.request.urlopen(urllib.request.Request(url,headers={'Range':f'bytes={offset}-{end}'}),timeout=90)as r:
    if r.status!=206 or not r.headers.get('Content-Range','').startswith(f'bytes {offset}-'):raise RuntimeError('Range mismatch')
    remaining=end-offset+1
    with f.open('ab')as w:
     while remaining:
      data=r.read(min(4*1024*1024,remaining))
      if not data:raise OSError('Short range')
      w.write(data);remaining-=len(data)
   if f.stat().st_size!=size:raise RuntimeError('Range length mismatch')
   return
  except OSError:
   if trial==2:raise
   time.sleep(1)
with concurrent.futures.ThreadPoolExecutor(8)as pool:
 for i,f in enumerate(concurrent.futures.as_completed([pool.submit(transfer,j)for j in jobs]),1):
  f.result()
  if i%8==0 or i==len(jobs):print('Completed ranges',i,'of',len(jobs),flush=True)
records=[]
for ent in entries:
 out=dest/ent['rfilename'];part=dest/(ent['rfilename']+'.part')
 if not out.exists():
  with part.open('ab')as w:
   for job in plans[ent['rfilename']]:
    with job[3].open('rb')as f:
     for chunk in iter(lambda:f.read(4*1024*1024),b''):w.write(chunk)
  if part.stat().st_size!=ent['size']:raise RuntimeError('Assembled length mismatch')
  part.rename(out)
 h=hashlib.sha256()
 with out.open('rb')as f:
  for chunk in iter(lambda:f.read(4*1024*1024),b''):h.update(chunk)
 if h.hexdigest()!=ent['lfs']['sha256']:raise RuntimeError('Publisher checksum mismatch')
 records.append({'name':ent['rfilename'],'bytes':ent['size'],'sha256':h.hexdigest(),'matches_hub_lfs_digest':True})
 for job in plans[ent['rfilename']]:job[3].unlink()
 print('Publisher SHA256 matched',ent['rfilename'],flush=True)
p=B.parent/'evidence/MODEL_REVISIONS.json';m=json.loads(p.read_text());m[name]={'revision':rev,'license_metadata':'apache-2.0','gated':False,'local_path':str(dest),'weights_sha256_verified':True,'files':records};p.write_text(json.dumps(m,indent=2));print('Stronger candidate artifacts verified',flush=True)
