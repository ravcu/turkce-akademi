"""Build the unit 10 PDF reader from the supplied PDF and WebP pages.
Run at repository root; vocabulary additions are kept alongside this script.
"""
from pathlib import Path
import json,re,unicodedata,fitz
ROOT=Path('kitaplar/lise-a2-dilbilgisi'); OUT=ROOT/'geziyorum'; PREV=ROOT/'bir-hikayem-var'
def norm(s):return re.sub(r'^[\s.,:;!?()\[\]{}\"“”’…−•]+|[\s.,:;!?()\[\]{}\"“”’…−•]+$','',unicodedata.normalize('NFC',s).strip().replace('I','ı').replace('İ','i').lower())
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')))
def valid(v):
 return isinstance(v,list) and len(v)==5 and all(isinstance(x,str) and x.strip() for x in v) and bool(re.search('[А-Яа-яЁё]',v[1])) and bool(re.search('[\u0600-\u06ff]',v[3]))
pool={};phrases={}
for p in ROOT.glob('*/translations.json'):
 if p.parent==OUT:continue
 d=json.loads(p.read_text());pool.update({k:v for k,v in d.get('words',{}).items() if valid(v)});phrases.update(d.get('phrases',{}))
for line in Path('tools/a2-grammar-unit10-lexicon.tsv').read_text().splitlines():
 if not line.strip():continue
 a=line.split('|');assert len(a)==6,a;pool[norm(a[0])]=a[1:]
pages=[];doc=fitz.open(next(OUT.glob('*.pdf')))
for n,p in enumerate(doc):
 raw=[]
 for x0,y0,x1,y1,t,*rest in p.get_text('words'):
  if not .05<y0/p.rect.height<.94:continue
  offset=0
  for part in t.split('/'):
   pos=t.find(part,offset);offset=pos+len(part)+1
   if not re.search(r'[\w]',part):continue
   raw.append((x0+(x1-x0)*pos/len(t),y0,x0+(x1-x0)*(pos+len(part))/len(t),y1,part,*rest))
 words=[];i=0
 while i<len(raw):
  w=raw[i];parts=[w];t=w[4];i+=1
  while t.endswith('-') and i<len(raw) and raw[i][1]>parts[-1][1] and raw[i][1]-parts[-1][1]<35:
   t=t[:-1]+raw[i][4];parts.append(raw[i]);i+=1
  for part in parts:
   x0,y0,x1,y1,*_=part
   item={'t':t,'x':x0/p.rect.width,'y':y0/p.rect.height,'w':(x1-x0)/p.rect.width,'h':(y1-y0)/p.rect.height}
   if len(parts)>1:item['group']=f'p{n+1}-w{len(words)-parts.index(part)}'
   words.append(item)
 pages.append({'image':f'sayfa-{n+1:02}.webp','bookPage':121+n if n<11 else 'Arka kapak','words':words})
keys={norm(w['t']) for p in pages for w in p['words']}
for k in keys:
 if k.isdigit():pool[k]=[k]*5
 elif re.match(r'^s\.\d',k):
  num=k[2:];pool[k]=[f'Book audio reference {num}',f'Аудиозапись {num}',f'Аудиожазуу {num}',f'التسجيل الصوتي {num}',f'Référence audio {num}']
# Reference codes, printed suffix labels and examples of number forms.
for k in keys:
 if k in ['14-17','17a','b12311223']:
  pool[k]=[k.upper() if k in ['17a','b12311223','ybt123’tür'] else k]*5
 if k in ['+da','+de','+ta','+te','-da','-iş','-mek','-yış','-ış','yiş']:
  pool[k]=[f'{k}: grammatical suffix',f'{k}: грамматический суффикс',f'{k}: грамматикалык мүчө',f'{k}: لاحقة نحوية',f'{k} : suffixe grammatical']
 if k=='-türkçe':pool[k]=['Turkish','турецкий язык','түрк тили','اللغة التركية','turc']
missing=sorted(keys-pool.keys());assert not missing,missing
# Context-specific corrections override ambiguous dictionary entries.
for line in Path('tools/a2-grammar-unit10-phrases.tsv').read_text().splitlines():
 if not line.strip():continue
 a=line.split('|');assert len(a)==6,a;phrases[norm(a[0])]={'translations':a[1:]}
used_phrases={}
def occurs(parts):
 for page in pages:
  logical=[]
  for w in page['words']:
   if logical and w.get('group') and logical[-1].get('group')==w['group']:continue
   logical.append(w)
  for i in range(len(logical)-len(parts)+1):
   seq=logical[i:i+len(parts)]
   if [norm(w['t']) for w in seq]!=parts:continue
   def adjacent(a,b):
    dy=(b['y']+b['h']/2)-(a['y']+a['h']/2)
    if abs(dy)<=max(.009,min(a['h'],b['h'])*.75):return b['x']>=a['x']-.015 and b['x']-a['x']-a['w']<=.08
    return 0<dy<=.026 and a['x']-.55<=b['x']<=a['x']+a['w']+.1
   if all(adjacent(a,b) for a,b in zip(seq,seq[1:])):return True
 return False
for key,value in phrases.items():
 if not isinstance(value,dict) or len(value.get('translations',[]))!=5:continue
 parts=key.split()
 if len(parts)>1 and occurs(parts):used_phrases[key]=value
save(OUT/'pages.json',pages)
quiz=['paraşüt','şemsiye','helikopterden','uçak','uçakta','yasak','iniş','kalkışına','gidiş','dönüş','bekleme','danışma','havalimanı','ziyaret','lokanta','cami','mesafe','iptal','memnuniyet','harita','güvenli','kalitesiz','indirimli','işlem','koltuk','piyano','faydalıdır','hoşgörü','cesaret','mimari','rasathane','fidanı','çam','sahilde','ormanda','yürüyüş','güneşleneceğiz','yüzeceğiz','bakışı','okuyuşu']
save(OUT/'translations.json',{'words':{k:pool[k] for k in sorted(keys)},'phrases':used_phrases,'forms':{},'examples':{},'quizVocabulary':[k for k in quiz if k in keys]})
# Retain the menu independently of title replacements, to keep units 1–9 intact.
h=(PREV/'index.html').read_text()
menu=re.search(r'<nav class="unit-picker-list".*?</nav>',h).group(0).replace(' aria-current="page"','')
h=h.replace('bir-hikayem-var','geziyorum').replace('Bir Hikâyem Var','Gezi-Yorum').replace('9. Ünite','10. Ünite').replace('9. ünite','10. ünite').replace('9. ÜNİTE','10. ÜNİTE')
h=re.sub(r'<nav class="unit-picker-list".*?</nav>',lambda m:menu,h,count=1)
h=re.sub(r'<a class="unit-nav-button" href="[^"]*">← Bir Önceki Ünite</a>','<a class="unit-nav-button" href="../bir-hikayem-var/">← Bir Önceki Ünite</a>',h,count=1)
h=re.sub(r'<(?:a|button) class="unit-nav-button unit-nav-next"[^>]*>Bir Sonraki Ünite →</(?:a|button)>','<button class="unit-nav-button unit-nav-next" disabled aria-disabled="true" title="Bu kitabın son ünitesi">Bir Sonraki Ünite →</button>',h,count=1)
h=h.replace('img.alt=`Gezi-Yorum ünitesi, dil bilgisi ve telaffuz kitabı sayfa ${p.bookPage}`','img.alt=p.bookPage===\'Arka kapak\'?\'Dil Bilgisi ve Telaffuz Kitabı arka kapağı\':`Gezi-Yorum ünitesi, dil bilgisi ve telaffuz kitabı sayfa ${p.bookPage}`')
(OUT/'index.html').write_text(h)
speech=OUT/'speech';speech.mkdir(exist_ok=True);entries={k:{} for k in ['tr','en','ru','ky','ar','fr']}
for p in ROOT.glob('*/speech/index.json'):
 if p.parent.parent==OUT:continue
 d=json.loads(p.read_text())
 for lang,items in d.get('entries',{}).items():
  if lang in entries:
   for k,v in items.items():entries[lang][k]=[f'../../{p.parent.parent.name}/speech/{v[0]}',*v[1:]]
wanted={lang:set() for lang in entries}
for k,v in {**{k:pool[k] for k in keys},**{k:v['translations'] for k,v in used_phrases.items()}}.items():
 wanted['tr'].add(norm(k))
 for lang,text in zip(['en','ru','ky','ar','fr'],v):wanted[lang].add(text.strip().lower().strip('.!?,:;… '))
for lang in entries:entries[lang]={k:v for k,v in entries[lang].items() if k in wanted[lang]}
save(speech/'index.json',{'entries':entries})
(speech/'player.js').write_text((PREV/'speech/player.js').read_text())
card='<a href="../geziyorum/"><span class="unit-picker-number">10</span><span class="unit-picker-name">Gezi-Yorum</span><span class="unit-picker-pages">12 sayfa</span></a>'
for p in ROOT.glob('*/index.html'):
 h=p.read_text();start=h.index('<nav class="unit-picker-list"');end=h.index('</nav>',start);menu=h[start:end]
 if p.parent==OUT:menu=menu.replace(' aria-current="page"','')
 if '<span class="unit-picker-number">10</span>' not in menu:menu+=card
 if p.parent==OUT:menu=menu.replace('href="../geziyorum/"','href="../geziyorum/" aria-current="page"')
 h=h[:start]+menu+h[end:]
 if p.parent==PREV:h=re.sub(r'<(?:a|button) class="unit-nav-button unit-nav-next"[^>]*>Bir Sonraki Ünite →</(?:a|button)>','<a class="unit-nav-button unit-nav-next" href="../geziyorum/">Bir Sonraki Ünite →</a>',h,count=1)
 p.write_text(h)
p=Path('index.html');h=p.read_text();start=h.index("if(selectedLevel==='A2'){grid.innerHTML=");end=h.index("';return;}",start)
if '10. Ünite Gezi-Yorum Dil Bilgisi' not in h[start:end]:
 card='<a class="unit-card unit-available" href="kitaplar/lise-a2-dilbilgisi/geziyorum/" aria-label="10. Ünite Gezi-Yorum Dil Bilgisi ve Telaffuz PDF kitabını aç"><span class="unit-number">10</span><span class="unit-name">10. Ünite</span><span class="unit-topic">Gezi-Yorum</span><span class="unit-open">PDF kitabını aç →</span></a>'
 h=h[:end]+card+h[end:];p.write_text(h)
print(f'{len(pages)} pages; {sum(len(p["words"]) for p in pages)} hotspots; {len(keys)} entries; {len(used_phrases)} phrases')
