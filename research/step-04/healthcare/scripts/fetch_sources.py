from pathlib import Path
import urllib.request,json,hashlib,concurrent.futures
REV='1cbae8e92f72f20c8d3747cbb3bf5bc53554d997'
B=Path('/workspace/thesis-runtime/healthcare');PUB=Path('/workspace/TRUSTXAI/research/step-04/healthcare');PUB.mkdir(exist_ok=True);(PUB/'evidence').mkdir(exist_ok=True)
files=['data/ori_pqal.json','preprocess/split_dataset.py','LICENSE','README.md','evaluation.py']
def get(name):
 url=f'https://raw.githubusercontent.com/pubmedqa/pubmedqa/{REV}/{name}'
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'TRUSTXAI-academic-research'}),timeout=20) as r:data=r.read(6000000)
 p=B/'source'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 if name!='data/ori_pqal.json':
  p2=PUB/'evidence'/name.replace('/','__');p2.write_bytes(data)
 return {'file':name,'url':url,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:records=list(ex.map(get,files))
record={'repository':'https://github.com/pubmedqa/pubmedqa','revision':REV,'revision_method':'git ls-remote refs/heads/master; subsequent downloads use immutable commit','files':records,'raw_data_location':str(B/'source/data/ori_pqal.json'),'repository_license':'MIT','underlying_abstracts':'Preserve attribution; no raw corpus/abstract redistribution in public pack; NLM policy route not accessible in this environment'}
(PUB/'evidence/SOURCE_PROVENANCE.json').write_text(json.dumps(record,indent=2))
print(json.dumps(record,indent=2))
