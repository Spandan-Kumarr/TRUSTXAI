"""Fetch the pinned, explicitly identified mirror files; no inference or raw-text export."""
from pathlib import Path
import os,json,urllib.request,hashlib
B=Path(__file__).resolve().parents[1]
R=Path(os.environ.get('TRUSTXAI_RUNTIME','/workspace/thesis-runtime'))/'clinical-cdss'
R.mkdir(parents=True,exist_ok=True)
provenance=json.loads((B/'evidence/SOURCE_PROVENANCE.json').read_text())
for record in provenance['files']:
 path=R/record['file']
 if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()==record['sha256']:
  print('Existing verified file:',path.name);continue
 with urllib.request.urlopen(record['url'],timeout=30) as response:data=response.read(40000000)
 if hashlib.sha256(data).hexdigest()!=record['sha256']:raise RuntimeError('Dataset digest mismatch; do not use')
 path.write_bytes(data);print('Publisher snapshot bytes verified:',path.name)
