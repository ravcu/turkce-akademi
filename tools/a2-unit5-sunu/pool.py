import subprocess,json,pathlib,concurrent.futures
W=pathlib.Path('rebuild5');D=json.load(open(W/'pooled-dictionary.json'))
paths=subprocess.check_output(['git','-C','git-source','ls-tree','-r','--name-only','HEAD']).decode().splitlines();paths=[p for p in paths if p.endswith('/translations.json') and p.startswith('kitaplar/') and 'lise-a2/' not in p]
def read(p):
 try:return p,json.loads(subprocess.check_output(['git','-C','git-source','show','HEAD:'+p],timeout=60))
 except Exception:return p,{}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
 for p,d in ex.map(read,paths):
  for k in D:
   if isinstance(d.get(k),dict):
    for word,value in d[k].items():D[k].setdefault(word,value)
  print(p,flush=True)
# Current-unit meanings have priority over unrelated contexts.
d=json.loads(subprocess.check_output(['git','-C','git-source','show','HEAD:kitaplar/lise-a2/dedemin-meslegi/translations.json']))
for k in D:D[k].update(d.get(k,{}))
(W/'pooled-dictionary.json').write_text(json.dumps(D,ensure_ascii=False));print({k:len(v) for k,v in D.items()})
