"""Extract source coordinates and assemble editorial A2 unit 10 vocabulary."""
import json,re,unicodedata
from pathlib import Path
import fitz
ROOT=Path('kitaplar/lise-a2/geziyorum');SOURCE=Path('../upload/10.ünite(2).pdf')
def norm(s):return re.sub(r'^[^\w]+|[^\w]+$','',unicodedata.normalize('NFC',s).replace('’',"'").replace('I','ı').replace('İ','i').lower())
def save(n,d):(ROOT/n).write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')))
def extract():
 doc=fitz.open(SOURCE);pages=[];texts=[]
 for n,p in enumerate(doc,1):
  raw=[]
  for x0,y0,x1,y1,t,*rest in p.get_text('words'):
   # Split printed alternatives, labels and accidental punctuation-adjacent words.
   parts=re.split(r'\s+|/|\+|(?<=nun)(?=önündeyim)|(?<=[.!?])(?=[A-ZÇĞİÖŞÜ])|(?<=\))(?=[A-Za-zÇĞİÖŞÜçğıöşü])|(?<=[?:])(?=[A-Za-zÇĞİÖŞÜçğıöşü])',t)
   offset=0
   for part in parts:
    position=t.find(part,offset);offset=position+len(part)
    if not part or not re.search(r'[\w]',part):continue
    raw.append(dict(t=part,x=(x0+(x1-x0)*position/max(1,len(t)))/p.rect.width,y=y0/p.rect.height,w=(x1-x0)*len(part)/max(1,len(t))/p.rect.width,h=(y1-y0)/p.rect.height))
  # The hotel wordmark is duplicated in the PDF text layer; keep its visible parts.
  raw=[w for w in raw if w['t']!='ÇalışOtel']
  if n in [3,5]:
   for w in raw:
    if w['t']=='İstanbul':w['y']+=w['h']*.12;w['h']*=.55
  extras=[]
  if n==3:extras=[('1',(670,783,680,800)),('Gece',(682,780,711,797)),('750',(713,776,739,795))]
  if n==5:extras=[('1',(829,704,837,717)),('Gece',(838,705,861,719)),('750',(863,709,884,723))]
  if n==28:
   for w in raw:
    if w['t']=='Bir' and w['x']>.7:w['y']+=w['h']*.12;w['h']*=.5
   extras=[('Mükemmel',(430,1476,550,1505)),('Çok',(666,1476,705,1505)),('iyi',(709,1476,736,1505)),('İyi',(846,1476,874,1505)),('Fena',(976,1476,1025,1505)),('değil',(1030,1476,1085,1505))]
  if n in [29,30]:extras=[('INTERNATIONAL',(598,756,877,779)),('MAARİF',(598,781,878,835)),('PROGRAM',(598,838,751,866)),('ULUSLARARASI',(751,837,876,850)),('MAARİF',(751,850,804,863)),('PROGRAMI',(807,850,877,863))]
  for text,(x0,y0,x1,y1) in extras:
   raw.append(dict(t=text,x=x0/1282,y=y0/1622,w=(x1-x0)/1282,h=(y1-y0)/1622,positionSource='editorial tracing of embedded artwork'))
  for page,text,x0,y0,x1,y1 in json.loads(Path('tools/unit10-image-lines.json').read_text()):
   if page!=n:continue
   pos=0
   for part in text.split():
    start=text.index(part,pos);pos=start+len(part)
    raw.append(dict(t=part,x=(x0+(x1-x0)*start/len(text))/1282,y=y0/1622,w=(x1-x0)*len(part)/len(text)/1282,h=(y1-y0)/1622,positionSource='editorial tracing of embedded form and ticket'))
  for w in raw:
   w['t']={'Gülekin':'Gültekin','Sulanahmet':'Sultanahmet'}.get(w['t'],w['t'])
  dedup=[]
  for w in raw:
   duplicate=False
   for z in dedup:
    if norm(w['t'])!=norm(z['t']):continue
    iw=max(0,min(w['x']+w['w'],z['x']+z['w'])-max(w['x'],z['x']));ih=max(0,min(w['y']+w['h'],z['y']+z['h'])-max(w['y'],z['y']))
    if iw*ih/max(1e-12,min(w['w']*w['h'],z['w']*z['h']))>.8:duplicate=True;break
   if not duplicate:dedup.append(w)
  words=[];groups=[];j=0
  while j<len(dedup):
   w=dedup[j];indices=[len(words)];full=w['t'];words.append(w);j+=1
   while full.endswith('-') and j<len(dedup) and ((0<dedup[j]['y']-w['y']<w['h']*1.9 and dedup[j]['x']<w['x']) or (n==10 and full=='ya-' and dedup[j]['t']=='pıyorum.')):
    full=full[:-1]+dedup[j]['t'];indices.append(len(words));w=dedup[j];words.append(w);j+=1
   key=norm(full)
   key={'kışısel':'kişisel','kosmanın':'koşmanın','ınceleyin':'inceleyin','inceleleyin':'inceleyin','filler':'fiiller','sulanahmet':'sultanahmet','gülekin':'gültekin','gezi-yorum':'geziyorum','ınternatıonal':'international'}.get(key,key)
   for i in indices:words[i]['entryKey']=key
   if len(indices)>1:groups.append(dict(text=full,key=key,indices=indices))
  pages.append(dict(page=n,bookPage=194+n,image=f'pages/sayfa-{n:02}.webp',words=words,wordGroups=groups,phraseGroups=[]))
  texts.append(p.get_text())
 ROOT.mkdir(parents=True,exist_ok=True);save('pages.json',pages);save('source-text.json',texts)
def valid(a):return isinstance(a,list) and len(a)==5 and all(isinstance(v,str) and v.strip() for v in a) and not re.search('[\u0400-\u04ff\u0600-\u06ff]',a[0]+a[4]) and not re.search('[\u0400-\u04ff]',a[3])
def build():
 pages=json.loads((ROOT/'pages.json').read_text());g={k:{} for k in ['words','forms','examples','phrases','lemmas']}
 for path in sorted(Path('kitaplar').glob('**/translations.json')):
  if path.parent==ROOT:continue
  d=json.loads(path.read_text())
  for sec in g:
   for k,v in d.get(sec,{}).items():
    if sec=='words':ok=valid(v)
    elif sec=='examples':ok=valid(v[1] if isinstance(v,list) else v.get('values'))
    else:
     attrs=['translations'] if sec in ['phrases','lemmas'] else ['formTranslations','lemmaTranslations']
     ok=all(valid(v.get(a)) for a in attrs) and (not v.get('examples') or valid(v['examples']))
    if ok:g[sec][norm(k)]=v
 for name in ['unit10-lexicon.tsv','unit10-forms.tsv']:
  path=Path('tools')/name
  if not path.exists():continue
  for line in path.read_text().splitlines():
   if not line.strip():continue
   a=line.split('|');assert len(a) in [6,7],(name,a);k=norm(a[0]);g['words'][k]=a[-5:]
   if len(a)==7:
    lemma=a[1];v=g['words'].get(norm(lemma)) or g['lemmas'].get(norm(lemma),{}).get('translations')
    assert v,(k,lemma)
    g['forms'][k]={'text':a[0],'lemma':lemma,'lemmaType':'verb' if lemma.endswith(('mak','mek')) else 'noun','lemmaTranslations':v,'formTranslations':a[-5:]}
   else:g['forms'].pop(k,None)
 for name in ['unit10-examples.tsv']:
  path=Path('tools')/name
  if not path.exists():continue
  for line in path.read_text().splitlines():
   keys,tr,*v=line.split('|');assert len(v)==5,line
   for k in keys.split(','):
    k=norm(k);g['examples'][k]={'tr':tr,'values':v}
    if k in g['forms']:g['forms'][k].update(exampleTr=tr,examples=v)
 # Canonical root corrections apply to imported as well as new inflections.
 for k,f in g['forms'].items():
  lk=norm(f['lemma'])
  if lk in g['words']:f['lemmaTranslations']=g['words'][lk]
  if lk=='yemek' and k not in ['yemeği','yemeğini','yemekleri','yemeklerin','yemeklerden','yemekten','yemeklerle']:
   f['lemmaType']='verb';f['lemmaTranslations']=['to eat','есть','жеш','يأكل','manger']
 if 'gelirinden' in g['forms']:g['forms']['gelirinden']['lemmaTranslations']=['income','доход','киреше','دخل','revenu']
 # Reuse a natural, five-language lemma example for its inflected forms.
 for k,f in g['forms'].items():
  if f.get('exampleTr') and f.get('examples'):continue
  ex=g['examples'].get(k) or g['examples'].get(norm(f.get('lemma','')))
  if isinstance(ex,list):ex={'tr':ex[0],'values':ex[1]}
  if ex and valid(ex.get('values')):
   f.update(exampleTr=ex['tr'],examples=ex['values']);g['examples'].setdefault(k,ex)
 path=Path('tools/unit10-phrases.tsv')
 if path.exists():
  for line in path.read_text().splitlines():
   phrase,*a=line.split('|');assert len(a)==6,line;ex=g['examples'].get(norm(a[5]));assert ex,(phrase,a[5])
   if isinstance(ex,list):ex={'tr':ex[0],'values':ex[1]}
   g['phrases'][norm(phrase)]={'translations':a[:5],'exampleTr':ex['tr'],'examples':ex['values']}
 # Preserve printed numeric identifiers, including parenthesised phone codes.
 for page in pages:
  for w in page['words']:
   if re.fullmatch(r'[\d+]+',w['entryKey']):g['words'].setdefault(w['entryKey'],[w['t']]*5)
 # Audio/video identifiers are references, not vocabulary words.
 for code in sorted({norm(w['t']) for p in pages for w in p['words'] if re.match(r'^[SMV]\.\d{3}$',w['t'])}):
  label=code.upper();kind='video' if code.startswith('v') else 'song' if code.startswith('m') else 'listening'
  g['words'][code]=[label+' '+kind+' reference',label+' — код записи',label+' — жазуунун коду',label+' — رمز التسجيل',label+' — référence de l’enregistrement']
  g['examples'][code]={'tr':label+' kodu ilgili kaydı gösterir.','values':[label+' identifies the corresponding recording.',label+' обозначает соответствующую запись.',label+' тиешелүү жазууну көрсөтөт.',label+' يشير إلى التسجيل المعني.',label+' désigne l’enregistrement correspondant.']}
 # Editorial contextual senses preserve words as printed.
 for page in pages:
  for i,w in enumerate(page['words']):
   k=w['entryKey']
   if k=='sorun' and i and norm(page['words'][i-1]['t'])=='soruları':w['entryKey']='sorun:emir'
   if k=='yarı' and page['page']==24:w['entryKey']='yarı:sevgili'
   if k=='yeme' and page['page'] in [21,22]:w['entryKey']='yeme:olumsuz-emir'
   if k=='çalış':w['entryKey']='çalış:otel'
   if k=='demet':w['entryKey']='demet:otel'
   if k=='temel' and page['page']==10:w['entryKey']='temel:sıfat'
 # Context overrides are occurrence-based. Do not overwrite valid unrelated senses.
 aliases=json.loads(Path('tools/unit10-context.json').read_text()) if Path('tools/unit10-context.json').exists() else []
 for a in aliases:
  p=pages[a['page']-1]
  for i in a['indices']:p['words'][i]['entryKey']=a['key']
 g['phrases'].pop('balık ekmek',None)
 used=set();keys=set()
 for p in pages:
  for w in p['words']:keys.add(w['entryKey'])
  first={x['indices'][0]:x for x in p['wordGroups']};skip={i for x in p['wordGroups'] for i in x['indices'][1:]}
  logical=[]
  for i,w in enumerate(p['words']):
   if i in skip:continue
   gr=first.get(i);logical.append({'text':gr['text'] if gr else w['t'],'key':gr['key'] if gr else w['entryKey'],'indices':gr['indices'] if gr else [i]})
  p['exportWords']=[{'t':x['text'],'entryKey':x['key']} for x in logical]
  seq=[norm(x['text']) for x in logical];matches=[];occupied=set()
  for phrase in sorted(g['phrases'],key=lambda k:-len(k.split())):
   parts=phrase.split()
   if len(parts)<2:continue
   for i in range(len(seq)-len(parts)+1):
    if seq[i:i+len(parts)]!=parts:continue
    indices=[j for x in logical[i:i+len(parts)] for j in x['indices']]
    if occupied.intersection(indices):continue
    # Neighbouring words may cross a normal line break, never a distant column.
    boxes=[p['words'][x['indices'][0]] for x in logical[i:i+len(parts)]]
    if not all(abs(a['y']-b['y'])<max(a['h'],b['h'])*2.5 and (abs(a['y']-b['y'])>min(a['h'],b['h'])*.5 or abs(b['x']-a['x']-a['w'])<.08) for a,b in zip(boxes,boxes[1:])):continue
    matches.append({'key':phrase,'text':' '.join(x['text'] for x in logical[i:i+len(parts)]),'indices':indices});occupied.update(indices);used.add(phrase)
  p['phraseGroups']=matches
 g['phrases']={k:v for k,v in g['phrases'].items() if k in used}
 for sec in ['words','forms','examples']:g[sec]={k:v for k,v in g[sec].items() if k in keys}
 g['lemmas']={v['lemma']:{'translations':v['lemmaTranslations']} for v in g['forms'].values() if v.get('lemmaTranslations')}
 g['quizVocabulary']=[k for k in keys if k.isalpha() and len(k)>2 and k in g['words']]
 g['metadata']={'unit':10,'languages':['en','ru','ky','ar','fr'],'translationSource':'ChatGPT editorial translations; no translation service','status':'meanings and examples complete; see verification.json for validation'}
 save('pages.json',pages);save('translations.json',g)
 missing=[];examples=[]
 for k in sorted(keys):
  if not re.search(r'[^\W\d_]',k):continue
  if k not in g['words'] and not g['forms'].get(k,{}).get('formTranslations'):missing.append(k)
  if k not in g['examples'] and not g['forms'].get(k,{}).get('examples'):examples.append(k)
 Path('../unit10-source/missing-meanings.txt').write_text('\n'.join(missing));Path('../unit10-source/missing-examples.txt').write_text('\n'.join(examples))
 print('pages',len(pages),'words',sum(len(p['words']) for p in pages),'unique',len(keys),'missing meanings',len(missing),'missing examples',len(examples))
if __name__=='__main__':
 import sys
 if '--extract' in sys.argv:extract()
 if '--build' in sys.argv:build()
