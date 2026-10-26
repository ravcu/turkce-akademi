from pathlib import Path
import json,re,collections,copy
R=Path(__file__).resolve().parents[2];W=R.parent/'rebuild5';O=R/'kitaplar/lise-a2/dedemin-meslegi-bana-gore-mi/sunum';A=O/'assets'
D=json.loads((W/'pooled-dictionary.json').read_text())
for form in D['forms'].values():
 if form.get('lemma')=='arkadaşı':form['lemma']='arkadaş'
 if form.get('lemma')=='yaşın':form['lemma']='yaş'
 if form.get('lemma')=='mi (question particle)':form['lemma']='mi'
for k,v in list(D['examples'].items()):
 if isinstance(v,dict):D['examples'][k]=[v.get('tr',''),v.get('values',[])]
for line in (R/'tools/a2-unit5-sunu/extra.tsv').read_text().splitlines():
 if not line.strip():continue
 parts=line.split('|');assert len(parts)==7,(len(parts),line)
 k,lemma,*values=parts
 if k==lemma:D['words'][k]=values;D['forms'].pop(k,None)
 else:D['forms'][k]={'lemma':lemma,'formTranslations':values};D['words'][k]=values
alias={'oyanmışlar':'oynamışlar','1.on':'on',"adel,rina'nın":"rina'nın",'a2.1':'a2','kıtabı':'kitabı','bahaf':'sahaf','ayârim':'yârim','aynızamanda':'aynı zamanda','on.parmağında':'on parmağında','on.marifet':'on marifet','yazarlı':'yazarlık','ıstanbul':'istanbul','ıslamabad':'islamabad','konusabilirim':'konuşabilirim','ekerleme':'tekerleme',"burak'dünyayı":'dünyayı','metini':'metni','ürkiye':'türkiye','pilot.olmak':'pilot olmak','ahmetve':'ahmet','vapabilir':'yapabilir','bulmaça':'bulmaca','biyotoğ':'biyolog','hayır,yüz':'yüz','yüzden/bu':'bu yüzden / bu sebeple','kendiiş':'kendi iş','taşve':'taş ve','vahşihayvanlardan':'vahşi hayvanlardan','dinleyinvetekrar':'dinleyin ve tekrar','kısaldı.kısa':'kısa'}
noise={'esna','ürkç','edeleri','nekteki','sorula','rını','onuşka','ylemeyi','nneni'}
slides=[];spots=[];missing=collections.Counter()
for file in sorted(W.glob('rendered-*.json')):
 s,row=json.loads(file.read_text());clean=[]
 for w in row:
  k=w['key']
  if k in noise:continue
  k=alias.get(k,k)
  negative=re.match(r'^[-−]\s*(\d+)(.*)$',w['text'])
  if negative:
   value=''.join(negative.groups());k='-'+value;D['words'][k]=['minus '+value,'минус '+value,'минус '+value,'سالب '+value,'moins '+value]
  if not re.search('[a-zçğıöşü]',k):D['words'].setdefault(k,[w['text']]*5)
  if k not in D['words'] and k not in D['forms'] and k not in D['phrases']:missing[k]+=1
  w['key']=k;clean.append(w)
 if s['sourcePart']==2 and s['sourcePartSlide']==26:s['videoUrl']='https://www.youtube.com/watch?v=PCL8y1WSmAk'
 slides.append(s);spots.append(clean)
for line in (R/'tools/a2-unit5-sunu/examples.tsv').read_text().splitlines():
 if not line.strip():continue
 parts=line.split('|');assert len(parts)==7,(len(parts),line)
 D['examples'][parts[0]]=[parts[1],parts[2:]]
def shifted(a):return isinstance(a,list) and len(a)==5 and re.search('[\u0400-\u04ff]',str(a[3])) and re.search('[\u0600-\u06ff]',str(a[4])) and not re.search('[\u0600-\u06ff]',str(a[3]))
for line in (R/'tools/a2-unit5-sunu/phrases.tsv').read_text().splitlines():
 if not line.strip():continue
 k,*values=line.split('|');assert len(values)==5
 D['phrases'].setdefault(k,{})['translations']=values
for entry in D['phrases'].values():
 if shifted(entry.get('examples')):entry.pop('exampleTr',None);entry.pop('examples',None)
for k,ex in list(D['examples'].items()):
 if shifted(ex[1]):
  lemma=D['forms'].get(k,{}).get('lemma');base=D['examples'].get(lemma)
  if base and not shifted(base[1]):D['examples'][k]=base
  else:D['examples'].pop(k)
for f in D['forms'].values():
 lemma=f.get('lemma','');lo=lemma.replace('İ','i').replace('I','ı').lower()
 if lemma not in D['words'] and lo in D['words']:D['words'][lemma]=D['words'][lo]
 if lemma not in D['words'] and lemma[:1].isupper():D['words'][lemma]=[lemma]*5
 ex=D['examples'].get(lemma) or D['examples'].get(lo)
 if ex and (not f.get('exampleTr') or shifted(f.get('examples'))):f['exampleTr']=ex[0];f['examples']=ex[1]
for f in D['forms'].values():
 if f.get('lemma') in D['words']:f['lemmaTranslations']=D['words'][f['lemma']]
used={w['key'] for row in spots for w in row};roots={D['forms'][k]['lemma'] for k in used if k in D['forms']};need=used|roots
D['words']={k:v for k,v in D['words'].items() if k in need};D['forms']={k:v for k,v in D['forms'].items() if k in used};D['examples']={k:v for k,v in D['examples'].items() if k in need};partsUsed={part for key in used for part in key.split()}
D['phrases']={k:v for k,v in D['phrases'].items() if k in used or all(w in partsUsed for w in k.split())}
(A/'slides.json').write_text(json.dumps({'slides':slides},ensure_ascii=False,indent=2));(A/'word-spots.json').write_text(json.dumps(spots,ensure_ascii=False));(A/'translations.json').write_text(json.dumps(D,ensure_ascii=False));(A/'answer-overlays.json').write_text('{}');(W/'missing-final.json').write_text(json.dumps(missing,ensure_ascii=False,indent=2));print('targets',len(used),'missing',len(missing));print(' | '.join(sorted(missing)))

