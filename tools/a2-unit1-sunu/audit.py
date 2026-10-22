from pathlib import Path
import os
from concurrent.futures import ThreadPoolExecutor
import json,hashlib,subprocess,collections
R=Path(os.environ.get("A2_SUNU_WORK",Path(__file__).resolve().parents[3]/"a2-source"));repo=Path(os.environ.get("A2_SUNU_REPO",Path(__file__).resolve().parents[2]));root=repo/'kitaplar/lise-a2/tatil-donusu/sunum';idx=json.loads((root/'speech/index.json').read_text());errors=[];local=collections.defaultdict(float);shared=set();tracked=set(subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD'],cwd=repo).decode().splitlines())
sha=hashlib.sha256((root/'assets/translations.json').read_bytes()+(root/'assets/word-spots.json').read_bytes()).hexdigest();assert idx['sourceSha']==sha
for lang,entries in idx['entries'].items():
 for key,(file,start,end) in entries.items():
  if not 0<=start<end:errors.append([lang,key,'invalid times'])
  p=(root/'speech'/file).resolve()
  if '/' not in file:local[p]=max(local[p],end)
  else:
   rel=str(p.relative_to(repo.resolve()));shared.add(rel)
   if rel not in tracked:errors.append([rel,'not tracked'])
def check(item):
 p,end=item
 try:
  duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(p)]))
  return [str(p),end,duration] if end>duration+.03 else None
 except Exception as e:return [str(p),str(e)]
with ThreadPoolExecutor(max_workers=8) as pool:
 for result in pool.map(check,local.items()):
  if result:errors.append(result)
report={'dictionarySha256':hashlib.sha256((root/'assets/translations.json').read_bytes()).hexdigest(),'speechSourceSha256':sha,'speechTexts':{k:len(v) for k,v in idx['entries'].items()},'localSpeechPacks':len(local),'sharedSpeechPacks':len(shared),'errors':errors};(R/'speech-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False));assert not errors
