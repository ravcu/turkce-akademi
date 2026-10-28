from pathlib import Path
import json,re,unicodedata,collections
ROOT=Path(__file__).resolve().parents[2];W=ROOT.parent/'work8';OUT=ROOT/'kitaplar/lise-a2/spor-ve-saglik/sunum';HERE=Path(__file__).parent
norm=lambda t:unicodedata.normalize('NFC',t).replace('I','ı').replace('İ','i').lower().replace('’',"'").strip(' \t\n.,;:!?()[]{}\"“”‘…−•-/')
def valid(a):return isinstance(a,list) and len(a)==5 and all(isinstance(x,str) and x.strip() for x in a) and bool(re.search('[а-яА-ЯёЁ]',a[1])) and bool(re.search('[а-яА-ЯөӨүҮңҢ]',a[2])) and bool(re.search('[\u0600-\u06ff]',a[3])) and not re.search('[\u0600-\u06ffа-яА-Я]',a[4])
def entry(g,k):
 p=g.get('phrases',{}).get(k) or {};f=g.get('forms',{}).get(k) or {};e=g.get('examples',{}).get(k) or {}
 m=p.get('translations') or f.get('formTranslations') or g.get('words',{}).get(k)
 tr=p.get('exampleTr') or f.get('exampleTr') or (e[0] if isinstance(e,list) else e.get('tr'))
 ex=p.get('examples') or f.get('examples') or ((e[1:] if len(e)==6 else e[1]) if isinstance(e,list) else e.get('values'))
 return m,tr,ex
base=json.loads((OUT.parent/'translations.json').read_text());D={s:{norm(k):v for k,v in base.get(s,{}).items()} for s in ['words','forms','examples','phrases','lemmas']};pool={};examplepool={}
for path in sorted((W/'pool').glob('*.json')):
 try:g=json.loads(path.read_text())
 except:continue
 for section in ['words','forms','phrases','examples']:
  for k in g.get(section,{}):
   m,tr,ex=entry(g,k)
   if valid(m) and tr and valid(ex):pool.setdefault(norm(k),(m,tr,ex))
   if tr and valid(ex):
    for token in set(re.findall(r"[\w]+(?:'[\w]+)?",norm(tr))):
     if token not in examplepool or len(tr)<len(examplepool[token][0]):examplepool[token]=(tr,ex)
if (HERE/'examples.tsv').exists():
 for line in (HERE/'examples.tsv').read_text().splitlines():
  keys,tr,*ex=line.split('\t');assert valid(ex),keys
  for k in keys.split('|'):
   if k in norm(tr) or k not in examplepool:examplepool[k]=(tr,ex)
if (HERE/'grammar.tsv').exists():
 for line in (HERE/'grammar.tsv').read_text().splitlines():
  k,*m=line.split('\t');assert valid(m),k
  subject='Ben' if k in ['okumuşum','okumamışım','okumuyorum','okumam','anlamıyorum','okudum','okumadım','okuyacağım','okumayacağım'] else 'Biz' if k.startswith('gör') else 'Onlar' if k in ['geliyorlar','gelmiyorlar','gelirler','gelmezler','gelecekler','gelmeyecekler'] else 'O'
  tr=(subject+' '+k).strip().capitalize()+'.';ex=[t[0].upper()+t[1:]+'.' for t in m];pool[k]=(m,tr,ex)
if (HERE/'extra.tsv').exists():
 for line in ((HERE/'extra.tsv').read_text()+(HERE/'nouns.tsv').read_text()+(HERE/'gerunds.tsv').read_text()).splitlines():
  k,*m=line.split('\t');assert valid(m),k;assert k in examplepool,('missing example',k);pool[k]=(m,*examplepool[k])
if (HERE/'finite.tsv').exists():
 for line in (HERE/'finite.tsv').read_text().splitlines():
  k,subject,*m=line.split('\t');assert valid(m),k
  # Complete short conjugation examples preserve tense, person and negation.
  tr=((subject+' '+k).strip().capitalize()+'.') if k not in ['kalmadı'] else 'Hiçbir şey kalmadı.'
  ex=[v[0].upper()+v[1:]+'.' for v in m];pool[k]=(m,tr,ex)
def resolve(k):
 m,tr,ex=entry(D,k)
 if m and tr and ex and len(m)==len(ex)==5:return True
 if k not in pool:return False
 m,tr,ex=pool[k];D['words'][k]=m;D['examples'][k]={'tr':tr,'values':ex};return True
corrections={'teknolojı':'teknoloji','elektriklı':'elektrikli','dijıtal':'dijital','bilgısayar':'bilgisayar','akılh':'akıllı','kullanımh':'kullanımlı','afış':'afiş','fılm':'film','tamır':'tamir','ıdris':'idris','hafıf':'hafif','çıta':'çita','maarıf':'maarif','yotoğraf':'fotoğraf','toğraf':'fotoğraf','pbot':'robot','ğünkü':'çünkü','ünkü':'çünkü','terçih':'tercih','müsteri':'müşteri','şize':'size','nceleyın':'inceleyin','gormuyoruz':'görmüyoruz','görduk':'gördük','gelmeler':'gelmezler','kösesinde':'köşesinde','ıstiyorum':'istiyorum','elekirikli':'elektrikli','manavv':'manav','ozaman':'o zaman','akılı':'akıllı','fıyata':'fiyata','metini':'metni','oyle':'öyle','hoşgeldiniz':'hoş geldiniz','sessizealmak':'sessize almak','tostmakinesi':'tost makinesi','önkamera':'ön kamera','akılısaat':'akıllı saat'}
corrections.update({'ıki':'iki','ızmir':'izmir','firçalayıp':'fırçalayıp','ıspanaktâki':'ıspanaktaki','zeylinyağı':'zeytinyağı','dereolu':'dereotu','karışlır':'karıştır','aleşte':'ateşte','yöğürt':'yoğurt','uzerine':'üzerine','ılk':'ilk','odemeyi':'ödemeyi','unlü':'ünlü','ışaretleyin':'işaretleyin','nasil':'nasıl','hâyâtın':'hayatın','süzüldüklen':'süzüldükten','garnilürleri':'garnitürleri','zeylinyağının':'zeytinyağının','yelişir':'yetişir','be’mbeyaz':'bembeyaz','yelerince':'yeterince'})
splits={'görseldeneler':['görselde','neler'],'hemfilm':['hem','film'],'buürünün':['bu','ürünün'],'ikigünönce':['iki','gün','önce'],'beşfarklı':['beş','farklı'],'bilgisayarınaneoldu':['bilgisayarına','ne','oldu']}
unknown=collections.defaultdict(set);slides=[];accepted=[];all_records=[]
for file in sorted(W.glob('rendered-*.json')):
 row=json.loads(file.read_text());i=row['sourceSlide'];s=row['slide'];words=sorted(row['words'],key=lambda w:0 if w.get('mode')=='vector' else 1);areas=[]
 for j,w in enumerate(words):
  k=norm(w['text']);conf=w['confidence'];x,y,ww,h=[w[t] for t in ['x','y','w','h']]
  if any(q is not w and norm(q['text'])==k and h>q['h']*1.4 and q['w']<=ww*1.15 and x<=q['x']+q['w']/2<=x+ww and y<=q['y']+q['h']/2<=y+h for q in words):continue
  if not re.search('[a-zçğıöşüâîû]',k) or not k or k in ['dk','dbtk','trt','a2','dbik'] or y<12 and x>85:continue
  if h<.75 or h>11 or ww<.25 or ww>35:continue
  k=corrections.get(k,k)
  if k in splits:
   tokens=splits[k];offset=0;total=sum(map(len,tokens))
   for token in tokens:
    if resolve(token):areas.append({'text':token,'x':x+ww*offset/total,'y':y,'w':ww*len(token)/total,'h':h,**({'answer':True} if w.get('answer') else {})})
    offset+=len(token)
   continue
  # Join only printed line-end fragments, retaining two clickable pieces.
  if w['text'].endswith('-') and j+1<len(words):
   n=words[j+1];joined=k+norm(n['text'])
   if resolve(joined):
    for q in [w,n]:
     z={a:q[a] for a in ['x','y','w','h']};z.update(text=joined,answer=bool(q.get('answer')));areas.append(z)
    n['text']='';continue
  if len(k)==1 and k!='o':continue
  if conf<55:continue
  if resolve(k):
   cx=x+ww/2;cy=y+h/2
   if not any(a['x']<=cx<=a['x']+a['w'] and a['y']-.1<=cy<=a['y']+a['h']+.1 for a in areas):areas.append({'text':k,'x':x,'y':y,'w':ww,'h':h,**({'answer':True} if w.get('answer') else {})})
  elif conf>=75 and re.fullmatch("[a-zçğıöşüâîû]+(?:'[a-zçğıöşüâîû]+)?",k):unknown[k].add(i)
 # Prefer whole words over duplicate OCR fragments at the same printed position.
 areas=[a for a in areas if not any(b is not a and len(a['text'])<len(b['text']) and a['text'] in b['text'] and b['x']<=a['x']+a['w']/2<=b['x']+b['w'] and b['y']-.1<=a['y']+a['h']/2<=b['y']+b['h']+.1 for b in areas)]
 # Remove oversized duplicates spanning an adjacent line.
 areas=[a for a in areas if not any(b is not a and b['text']==a['text'] and a['h']>b['h']*1.4 and max(a['x'],b['x'])<min(a['x']+a['w'],b['x']+b['w']) and max(a['y'],b['y'])<min(a['y']+a['h'],b['y']+b['h']) for b in areas)]
 s['words']=[{k:round(v,4) if isinstance(v,float) else v for k,v in a.items()} for a in sorted(areas,key=lambda a:(a['y'],a['x']))];slides.append(s);accepted.extend(a['text'] for a in areas);all_records.append(row)
for line in (HERE/'repetitions.tsv').read_text().splitlines():
 phrase,*m=line.split('\t');tr,ex=examplepool[phrase.split()[0]];assert valid(m) and valid(ex)
 D['phrases'][phrase]={'translations':m,'exampleTr':tr,'examples':ex}
# Existing idiomatic combinations are selected together, using the visible word fragments.
for key in list(D['words']):
 if 2<=len(key.split())<=7 and key not in D['phrases']:
  m,tr,ex=entry(D,key)
  if m and tr and ex:D['phrases'][key]={'translations':m,'exampleTr':tr,'examples':ex}
phrases=sorted(D['phrases'],key=lambda k:len(k.split()),reverse=True)
for s in slides:
 for phrase in phrases:
  tokens=phrase.split()
  if not 2<=len(tokens)<=7:continue
  for first in s['words']:
   if first['text']!=tokens[0] or 'phrase' in first:continue
   group=[first]
   for token in tokens[1:]:
    prev=group[-1];matches=[w for w in s['words'] if w['text']==token and not w.get('phrase') and bool(w.get('answer'))==bool(first.get('answer')) and abs(w['y']-prev['y'])<max(w['h'],prev['h'])*.6 and 0<=w['x']-(prev['x']+prev['w'])<3]
    if not matches:break
    group.append(min(matches,key=lambda w:w['x']))
   if len(group)==len(tokens):
    for w in group:w['phrase']=phrase
used=set(accepted)|{w['phrase'] for s in slides for w in s['words'] if 'phrase' in w}
for section in ['words','forms','examples','phrases']:D[section]={k:v for k,v in D[section].items() if k in used or section=='words' and any(f.get('lemma')==k or f.get('base')==k for f in D['forms'].values())}
(OUT/'manifest.json').write_text(json.dumps({'slides':slides},ensure_ascii=False,separators=(',',':'))+'\n');(OUT/'translations.json').write_text(json.dumps(D,ensure_ascii=False,separators=(',',':'))+'\n')
(W/'unknown.json').write_text(json.dumps({k:sorted(v) for k,v in unknown.items()},ensure_ascii=False,indent=1));(W/'example-pool.json').write_text(json.dumps(examplepool,ensure_ascii=False))
print({'slides':len(slides),'selections':len(accepted),'entries':len(used),'unknown':len(unknown)});print(json.dumps({k:sorted(v) for k,v in unknown.items()},ensure_ascii=False))
