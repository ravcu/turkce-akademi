import pathlib,json,subprocess,re,collections
W=pathlib.Path('rebuild5');D=json.load(open(W/'pooled-dictionary.json'));S=json.load(open('repo/kitaplar/lise-a2/dedemin-meslegi-bana-gore-mi/sunum/assets/translations.json'))
def ar(s):return bool(re.search('[\u0600-\u06ff]',s))
def cy(s):return bool(re.search('[\u0400-\u04ff]',s))
def shifted(v):return isinstance(v,list) and len(v)==5 and cy(str(v[3])) and ar(str(v[4])) and not ar(str(v[3]))
paths=subprocess.check_output(['git','-C','git-source','ls-tree','-r','--name-only','HEAD']).decode().splitlines();paths=[p for p in paths if p.endswith('/translations.json') and p.startswith('kitaplar/')]
validWords={};validForms={};validExamples={}
for p in paths:
 d=json.loads(subprocess.check_output(['git','-C','git-source','show','HEAD:'+p]))
 for k,v in d.get('examples',{}).items():
  if isinstance(v,dict):v=[v.get('tr',''),v.get('values',[])]
  if not isinstance(v,list) or len(v)!=2:continue
  a=v[1]
  if len(a)==6:a=a[1:]
  if len(a)==5 and not shifted(a) and ar(str(a[3])):validExamples[k]=[v[0],a]
 for k,v in d.get('words',{}).items():
  if isinstance(v,list) and len(v)==6:v=v[1:]
  if isinstance(v,list) and len(v)==5 and not shifted(v) and ar(str(v[3])):validWords[k]=v
 for k,v in d.get('forms',{}).items():
  a=v.get('formTranslations')
  if isinstance(a,list) and len(a)==6:a=a[1:];v['formTranslations']=a
  if isinstance(a,list) and len(a)==5 and not shifted(a) and ar(str(a[3])):validForms[k]=v
for k,v in D['examples'].items():
 if isinstance(v,dict):v=[v.get('tr',''),v.get('values',[])]
 if shifted(v[1]) and k in validExamples:D['examples'][k]=validExamples[k]
for k,v in D['forms'].items():
 if shifted(v.get('examples')):
  ex=validExamples.get(k) or validExamples.get(v.get('lemma'))
  if ex:v['exampleTr']=ex[0];v['examples']=ex[1]
for k,v in D['words'].items():
 if shifted(v) and k in validWords:D['words'][k]=validWords[k]
for k,v in D['forms'].items():
 if shifted(v.get('formTranslations')):
  if k in validForms:D['forms'][k]=validForms[k]
  elif k in validWords:v['formTranslations']=validWords[k]
(W/'pooled-dictionary.json').write_text(json.dumps(D,ensure_ascii=False))
bad={}
for k,v in S['words'].items():
 if shifted(D['words'].get(k)):
  if k in validForms:D['words'][k]=validForms[k]['formTranslations']
  else:bad[k]=D['words'][k]
for k,v in S['forms'].items():
 if shifted(D['forms'].get(k,{}).get('formTranslations')):bad[k]=D['forms'][k]['formTranslations']
(W/'pooled-dictionary.json').write_text(json.dumps(D,ensure_ascii=False));(W/'shifted-remaining.json').write_text(json.dumps(bad,ensure_ascii=False,indent=2));print('REMAINING',len(bad));print(json.dumps(bad,ensure_ascii=False))
