"""Retrieve previously curated local dictionaries; this is not a translation service."""
from pathlib import Path
import subprocess,concurrent.futures,urllib.request
ROOT=Path(__file__).resolve().parents[2];W=ROOT.parent/'work7/pool';W.mkdir(parents=True,exist_ok=True)
paths=subprocess.check_output(['git','-C',str(ROOT),'ls-tree','-r','--name-only','origin/main']).decode().splitlines()
paths=[p for p in paths if p.startswith('kitaplar/') and p.endswith('/translations.json') and '/akilli-teknoloji/sunum/' not in p]
def get(p):
 target=W/p.replace('/','__')
 if not target.exists():urllib.request.urlretrieve('https://raw.githubusercontent.com/ravcu/turkce-akademi/main/'+p,target)
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:list(ex.map(get,paths))
print('Dictionary sources:',len(paths))
