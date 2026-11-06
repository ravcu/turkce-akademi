"""Build the unit 9 PDF reader from the supplied PDF and WebP pages.
Run at repository root; vocabulary additions are kept alongside this script.
"""
from pathlib import Path
import json,re,unicodedata,fitz
ROOT=Path('kitaplar/lise-a2-dilbilgisi'); OUT=ROOT/'bir-hikayem-var'; PREV=ROOT/'spor-yapiyorum-saglikli-besleniyorum'
def norm(s):return re.sub(r'^[\s.,:;!?()\[\]{}\"“”’…−•]+|[\s.,:;!?()\[\]{}\"“”’…−•]+$','',unicodedata.normalize('NFC',s).strip().replace('I','ı').replace('İ','i').lower())
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')))
pool={};phrases={}
for p in ROOT.glob('*/translations.json'):
 if p.parent==OUT:continue
 d=json.loads(p.read_text());pool.update(d.get('words',{}));phrases.update(d.get('phrases',{}))
# The textbook dictionary is optional when running in a sparse checkout.
p=Path('kitaplar/lise-a2/bir-hikayem-var/translations.json')
if not p.exists():p=Path('/tmp/a2-u9-dictionary.json')
if p.exists():
 d=json.loads(p.read_text());pool.update(d.get('words',{}));phrases.update(d.get('phrases',{}))
for line in Path('tools/a2-grammar-unit9-lexicon.tsv').read_text().splitlines():
 if not line.strip():continue
 a=line.split('|');assert len(a)==6,a;pool[norm(a[0])]=a[1:]
pages=[];doc=fitz.open(next(OUT.glob('*.pdf')))
for n,p in enumerate(doc):
 raw=[w for w in p.get_text('words') if .05<w[1]/p.rect.height<.94 and re.search(r'[\w]',w[4])]
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
 pages.append({'image':f'sayfa-{n+1:02}.webp','bookPage':109+n,'words':words})
keys={norm(w['t']) for p in pages for w in p['words']}
for k in keys:
 if k.isdigit():pool[k]=[k]*5
 elif re.match(r'^s\.\d',k):
  num=k[2:];pool[k]=[f'Book audio reference {num}',f'Аудиозапись {num}',f'Аудиожазуу {num}',f'التسجيل الصوتي {num}',f'Référence audio {num}']
missing=sorted(keys-pool.keys());assert not missing,missing
# Context-specific corrections override ambiguous dictionary entries.
for line in Path('tools/a2-grammar-unit9-phrases.tsv').read_text().splitlines():
 if not line.strip():continue
 a=line.split('|');assert len(a)==6,a;phrases[norm(a[0])]={'translations':a[1:]}
used_phrases={}
for key,value in phrases.items():
 if not isinstance(value,dict) or len(value.get('translations',[]))!=5:continue
 parts=key.split()
 if len(parts)>1 and all(part in keys for part in parts):used_phrases[key]=value
save(OUT/'pages.json',pages)
save(OUT/'translations.json',{'words':{k:pool[k] for k in sorted(keys)},'phrases':used_phrases,'forms':{},'examples':{},'quizVocabulary':[k for k in ['hikâye','masal','kahraman','padişah','hükümdar','efsâne','sultan','fıkra','ayna','kral','kurbağa','fok','kurt','kuyruğu','tencere','kepçe','itfaiye','itfaiyeciler','yavru','bulmuş','kurtarmış','üşümüş','acıkmış','gülen','kızan','şaşıran','oynayan','yaşayan','koşan','somurtkan','cömert','kıskanç','dürüst','biyografi','rüya','uçmak','dilek','çözen','anlamışım','türkü'] if k in keys]})
h=(PREV/'index.html').read_text().replace('spor-yapiyorum-saglikli-besleniyorum','bir-hikayem-var').replace('Spor Yapıyorum Sağlıklı Besleniyorum','Bir Hikâyem Var').replace('8. Ünite','9. Ünite').replace('8. ünite, 18 sayfa','9. ünite, 12 sayfa').replace('8. ÜNİTE &nbsp;·&nbsp; 18 SAYFA','9. ÜNİTE &nbsp;·&nbsp; 12 SAYFA').replace('pages/sayfa-01.webp','sayfa-01.webp').replace('ders kitabı sayfa','dil bilgisi ve telaffuz kitabı sayfa')
h=h.replace('href="../akilli-teknoloji/">← Bir Önceki Ünite','href="../spor-yapiyorum-saglikli-besleniyorum/">← Bir Önceki Ünite')
h=h.replace('1 / 9</span><button id="next"','1 / 12</span><button id="next"').replace('8. ünite sayfası','9. ünite sayfası')
h=h.replace('p.image.replace(\'sayfa-\',\'onizleme-\')','p.image')
# Select a compound phrase only at the clicked occurrence.
h=h.replace("if(!phrase){for(let i=0;i<words.length;i++){if(normalize(words[i].t)===normalize(word)){const found=phraseAt(i,words);if(found){phrase=found;break}}}}",'')
(OUT/'index.html').write_text(h)
# Reuse existing recordings by reference; never copy unrelated audio into the new unit.
speech=OUT/'speech';speech.mkdir(exist_ok=True);entries={k:{} for k in ['tr','en','ru','ky','ar','fr']}
for p in ROOT.glob('*/speech/index.json'):
 if p.parent.parent==OUT:continue
 d=json.loads(p.read_text())
 for lang,items in d.get('entries',{}).items():
  if lang not in entries:continue
  for k,v in items.items():entries[lang][k]=[f'../../{p.parent.parent.name}/speech/{v[0]}',*v[1:]]
# Keep the index limited to text this unit can request.
wanted={lang:set() for lang in entries}
for k,v in {**{k:pool[k] for k in keys},**{k:v['translations'] for k,v in used_phrases.items()}}.items():
 wanted['tr'].add(norm(k))
 for lang,text in zip(['en','ru','ky','ar','fr'],v):wanted[lang].add(text.strip().lower().strip('.!?,:;… '))
for lang in entries:entries[lang]={k:v for k,v in entries[lang].items() if k in wanted[lang]}
save(speech/'index.json',{'entries':entries})
player=(PREV/'speech/player.js').read_text().replace("if (language === 'ar' || language === 'ky') return recorded(value,language,token);","if (language === 'ar' || language === 'ky') {\n      const index = await prepare();\n      if (index.entries[language]?.[key(value,language)]) return recorded(value,language,token);\n    }")
(speech/'player.js').write_text(player)
# Add the actual unit to every grammar picker, keeping each current marker intact.
card='<a href="../bir-hikayem-var/"><span class="unit-picker-number">9</span><span class="unit-picker-name">Bir Hikâyem Var</span><span class="unit-picker-pages">12 sayfa</span></a>'
for p in ROOT.glob('*/index.html'):
 h=p.read_text();start=h.index('<nav class="unit-picker-list"');end=h.index('</nav>',start)
 menu=h[start:end]
 if p.parent==OUT:
  # The template's eighth entry was renamed during title replacement.
  menu=menu.replace('href="../bir-hikayem-var/" aria-current="page"','href="../spor-yapiyorum-saglikli-besleniyorum/"').replace('<span class="unit-picker-number">8</span><span class="unit-picker-name">Bir Hikâyem Var</span>','<span class="unit-picker-number">8</span><span class="unit-picker-name">Spor Yapıyorum Sağlıklı Besleniyorum</span>')
 if p.parent==OUT:
  menu=menu.replace(' aria-current="page"','').replace('href="../bir-hikayem-var/"','href="../bir-hikayem-var/" aria-current="page"')
 if '<span class="unit-picker-number">9</span>' not in menu:menu+=card.replace('href="../bir-hikayem-var/"','href="../bir-hikayem-var/" aria-current="page"') if p.parent==OUT else card
 h=h[:start]+menu+h[end:]
 if p.parent==PREV:h=h.replace('<button class="unit-nav-button unit-nav-next" disabled aria-disabled="true">Bir Sonraki Ünite →</button>','<a class="unit-nav-button unit-nav-next" href="../bir-hikayem-var/">Bir Sonraki Ünite →</a>')
 p.write_text(h)
p=Path('index.html');h=p.read_text();start=h.index("if(selectedLevel==='A2'){grid.innerHTML=");end=h.index("';return;}",start)
if '9. Ünite Bir Hikâyem Var Dil Bilgisi' not in h[start:end]:
 card='<a class="unit-card unit-available" href="kitaplar/lise-a2-dilbilgisi/bir-hikayem-var/" aria-label="9. Ünite Bir Hikâyem Var Dil Bilgisi ve Telaffuz PDF kitabını aç"><span class="unit-number">09</span><span class="unit-name">9. Ünite</span><span class="unit-topic">Bir Hikâyem Var</span><span class="unit-open">PDF kitabını aç →</span></a>'
 h=h[:end]+card+h[end:];p.write_text(h)
print(f'{len(pages)} pages; {sum(len(p["words"]) for p in pages)} hotspots; {len(keys)} dictionary entries; {len(used_phrases)} phrase candidates')
