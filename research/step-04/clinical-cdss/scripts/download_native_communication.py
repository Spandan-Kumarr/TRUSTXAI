"""Download official publisher Q8_0 GGUF; verify complete artifact against publisher SHA256."""
from pathlib import Path
import json,urllib.request,concurrent.futures,hashlib,os,time
B=Path(__file__).resolve().parents[1];R=Path(os.environ.get('TRUSTXAI_RUNTIME','/workspace/thesis-runtime'));name='Qwen/Qwen3-1.7B-GGUF';revision='90862c4b9d2787eaed51d12237eafdfe7c5f6077'
meta_path=R/'clinical-cdss/Qwen17_GGUF_metadata.json'
if not meta_path.exists():
 with urllib.request.urlopen(f'https://huggingface.co/api/models/{name}/revision/{revision}?blobs=true',timeout=20) as response:meta_path.write_bytes(response.read())
meta=json.loads(meta_path.read_text());assert meta['sha']==revision and meta.get('gated') is False
entry=next(x for x in meta['siblings']if x['rfilename']=='Qwen3-1.7B-Q8_0.gguf');expected='061b54daade076b5d3362dac252678d17da8c68f07560be70818cace6590cb1a';assert entry['lfs']['sha256']==expected
folder=R/'models/Qwen3-1.7B-GGUF'/revision;folder.mkdir(parents=True,exist_ok=True);parts=folder/'parts';parts.mkdir(exist_ok=True);jobs=[]
for start in range(0,entry['size'],64*1024*1024):
 end=min(start+64*1024*1024-1,entry['size']-1);jobs.append((start,end,parts/f'{start}-{end}'))
def transfer(job):
 start,end,path=job
 for trial in range(3):
  offset=start+(path.stat().st_size if path.exists() else 0)
  if offset==end+1:return
  if offset>end+1:raise RuntimeError('Oversized range')
  try:
   url=f'https://huggingface.co/{name}/resolve/{revision}/{entry["rfilename"]}?download=true'
   with urllib.request.urlopen(urllib.request.Request(url,headers={'Range':f'bytes={offset}-{end}'}),timeout=90) as response:
    if response.status!=206 or not response.headers.get('Content-Range','').startswith(f'bytes {offset}-'):raise RuntimeError('Range identity mismatch')
    remaining=end-offset+1
    with path.open('ab') as file:
     while remaining:
      chunk=response.read(min(4*1024*1024,remaining))
      if not chunk:raise OSError('Short range')
      file.write(chunk);remaining-=len(chunk)
   return
  except OSError:
   if trial==2:raise
   time.sleep(1)
output=folder/entry['rfilename']
if not output.exists():
 with concurrent.futures.ThreadPoolExecutor(4) as pool:
  for i,future in enumerate(concurrent.futures.as_completed([pool.submit(transfer,job) for job in jobs]),1):
   future.result()
   if i%4==0 or i==len(jobs):print('Completed range',i,'of',len(jobs),flush=True)
 partial=folder/(entry['rfilename']+'.part')
 with partial.open('wb') as file:
  for _,_,path in jobs:
   with path.open('rb') as source:
    for chunk in iter(lambda:source.read(4*1024*1024),b''):file.write(chunk)
 assert partial.stat().st_size==entry['size'];partial.rename(output)
h=hashlib.sha256()
with output.open('rb') as file:
 for chunk in iter(lambda:file.read(4*1024*1024),b''):h.update(chunk)
assert h.hexdigest()==expected
for _,_,path in jobs:
 if path.exists():path.unlink()
small=[]
for filename in ['README.md','LICENSE']:
 with urllib.request.urlopen(f'https://huggingface.co/{name}/resolve/{revision}/{filename}',timeout=20) as response:data=response.read(300000)
 (B/'evidence'/('Qwen17_GGUF_'+filename)).write_bytes(data);small.append({'file':filename,'sha256':hashlib.sha256(data).hexdigest()})
record={'model':name,'revision':revision,'format':'GGUF Q8_0','publisher':'Qwen','license_metadata':meta.get('cardData',{}).get('license'),'file':entry['rfilename'],'bytes':entry['size'],'sha256':h.hexdigest(),'matches_publisher_LFS':True,'local_path':str(output),'tokenizer_reference':'Qwen/Qwen3-1.7B revision70d244cc86ccca08cf5af4e1e306ecf908b1ad5e; native token equality still to be checked','source_conversion_commit':'Not established; pin actual published GGUF artifact','small_files':small}
(B/'evidence/NATIVE_COMMUNICATION_MODEL.json').write_text(json.dumps(record,indent=2));print('Publisher GGUF SHA256 verified',flush=True)
