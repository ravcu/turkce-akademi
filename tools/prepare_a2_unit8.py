"""Extract source coordinates and assemble editorial A2 unit 8 vocabulary."""
import json,re,unicodedata
from pathlib import Path
import fitz
ROOT=Path('kitaplar/lise-a2/spor-ve-saglik');SOURCE=Path('../unit8-source/8.ünite(1).pdf')
def norm(s):return re.sub(r'^[^\w]+|[^\w]+$','',unicodedata.normalize('NFC',s).replace('’',"'").replace('I','ı').replace('İ','i').lower())
def save(n,d):(ROOT/n).write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')))
def extract():
 doc=fitz.open(SOURCE);pages=[];texts=[]
 for n,p in enumerate(doc,1):
  raw=[]
  for x0,y0,x1,y1,t,*rest in p.get_text('words'):
   # Split printed alternatives, labels and accidental punctuation-adjacent words.
   parts=re.split(r'\s+|/|\+|(?<=me)(?=programı)|(?<=[.!?])(?=[A-ZÇĞİÖŞÜ])|(?<=\))(?=[A-Za-zÇĞİÖŞÜçğıöşü])|(?<=[?:])(?=[A-Za-zÇĞİÖŞÜçğıöşü])',t)
   offset=0
   for part in parts:
    position=t.find(part,offset);offset=position+len(part)
    if not part or not re.search(r'[\w]',part):continue
    raw.append(dict(t=part,x=(x0+(x1-x0)*position/max(1,len(t)))/p.rect.width,y=y0/p.rect.height,w=(x1-x0)*len(part)/max(1,len(t))/p.rect.width,h=(y1-y0)/p.rect.height))
  if n==5:
   for text,(x0,y0,x1,y1) in [(a[0],a[1:]) for a in json.loads(Path('tools/unit8-menu-hotspots.json').read_text())]:
    pos=0
    for t in text.split():
     start=text.index(t,pos);pos=start+len(t)
     raw.append({'t':t,'x':(x0+(x1-x0)*start/len(text))/1282,'y':y0/1622,'w':(x1-x0)*len(t)/len(text)/1282,'h':(y1-y0)/1622,'positionSource':'editorial tracing of embedded menu image'})
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
   key={'kışısel':'kişisel','kosmanın':'koşmanın','ınceleyin':'inceleyin','inceleleyin':'inceleyin','filler':'fiiller'}.get(key,key)
   for i in indices:words[i]['entryKey']=key
   if len(indices)>1:groups.append(dict(text=full,key=key,indices=indices))
  if n==20:
   boxes={16:(696,344,727,360),17:(734,336,794,354),18:(697,362,797,381),19:(802,354,843,369),26:(393,600,458,619),31:(416,623,478,642),32:(326,670,391,688),35:(352,687,414,706)}
   for i,(x0,y0,x1,y1) in boxes.items():words[i].update(x=x0/1282,y=y0/1622,w=(x1-x0)/1282,h=(y1-y0)/1622)
  pages.append(dict(page=n,bookPage=154+n,image=f'pages/sayfa-{n:02}.webp',words=words,wordGroups=groups,phraseGroups=[]))
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
 for name in ['unit8-lexicon.tsv','unit8-forms.tsv']:
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
 for name in ['unit8-examples.tsv']:
  path=Path('tools')/name
  if not path.exists():continue
  for line in path.read_text().splitlines():
   keys,tr,*v=line.split('|');assert len(v)==5,line
   for k in keys.split(','):
    k=norm(k);g['examples'][k]={'tr':tr,'values':v}
    if k in g['forms']:g['forms'][k].update(exampleTr=tr,examples=v)
 # Keep noun/verb homographs and contextual root meanings distinct.
 eat=['to eat','есть','жеш','يأكل','manger']
 for k in ['yediklerime','yemeden','yemedi','yemelisin','yemeye','yemeyelim','yemeyin','yemiyor','yiyemem','yiyorsunuz']:
  if k in g['forms']:g['forms'][k].update(lemmaTranslations=eat,lemmaType='verb')
 for k in ['yemeklerinde','yemeğinizi','yemeğinizin']:
  if k in g['forms']:g['forms'][k]['lemmaType']='noun'
 ring=['to ring','звенеть','шыңгыроо','يرن','sonner']
 if 'çalıyor' in g['forms']:g['forms']['çalıyor']['lemmaTranslations']=ring
 for k,lemma,base in [
  ('iç:emir','içmek',['to drink','пить','ичүү','يشرب','boire']),
  ('için:emir','içmek',['to drink','пить','ичүү','يشرب','boire']),
  ('yaz:emir','yazmak',['to write','писать','жазуу','يكتب','écrire']),
  ('yazması:eylem','yazmak',['to write','писать','жазуу','يكتب','écrire'])]:
  if k in g['words']:
   g['forms'][k]={'text':k.split(':')[0],'lemma':lemma,'lemmaType':'verb','lemmaTranslations':base,'formTranslations':g['words'][k]}
 # Reuse a natural, five-language lemma example for its inflected forms.
 for k,f in g['forms'].items():
  if f.get('exampleTr') and f.get('examples'):continue
  ex=g['examples'].get(k) or g['examples'].get(norm(f.get('lemma','')))
  if isinstance(ex,list):ex={'tr':ex[0],'values':ex[1]}
  if ex and valid(ex.get('values')):
   f.update(exampleTr=ex['tr'],examples=ex['values']);g['examples'].setdefault(k,ex)
 path=Path('tools/unit8-phrases.tsv')
 if path.exists():
  for line in path.read_text().splitlines():
   phrase,*a=line.split('|');assert len(a)==6,line;ex=g['examples'].get(norm(a[5]));assert ex,(phrase,a[5])
   if isinstance(ex,list):ex={'tr':ex[0],'values':ex[1]}
   g['phrases'][norm(phrase)]={'translations':a[:5],'exampleTr':ex['tr'],'examples':ex['values']}
 # Audio/video identifiers are references, not vocabulary words.
 for code in ['s.050','s.051','s.052','s.053','m.006','v.009']:
  label=code.upper();kind='video' if code.startswith('v') else 'song' if code.startswith('m') else 'listening'
  g['words'][code]=[label+' '+kind+' reference',label+' — код записи',label+' — жазуунун коду',label+' — رمز التسجيل',label+' — référence de l’enregistrement']
  g['examples'][code]={'tr':label+' kodu ilgili kaydı gösterir.','values':[label+' identifies the corresponding recording.',label+' обозначает соответствующую запись.',label+' тиешелүү жазууну көрсөтөт.',label+' يشير إلى التسجيل المعني.',label+' désigne l’enregistrement correspondant.']}
 # Context overrides are occurrence-based. Do not overwrite valid unrelated senses.
 aliases=json.loads(Path('tools/unit8-context.json').read_text()) if Path('tools/unit8-context.json').exists() else []
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
 g['metadata']={'unit':8,'languages':['en','ru','ky','ar','fr'],'translationSource':'ChatGPT editorial translations; no translation service','status':'meanings and examples complete; see verification.json for validation'}
 save('pages.json',pages);save('translations.json',g)
 missing=[];examples=[]
 for k in sorted(keys):
  if not re.search(r'[^\W\d_]',k):continue
  if k not in g['words'] and not g['forms'].get(k,{}).get('formTranslations'):missing.append(k)
  if k not in g['examples'] and not g['forms'].get(k,{}).get('examples'):examples.append(k)
 Path('../unit8-source/missing-meanings.txt').write_text('\n'.join(missing));Path('../unit8-source/missing-examples.txt').write_text('\n'.join(examples))
 print('pages',len(pages),'words',sum(len(p['words']) for p in pages),'unique',len(keys),'missing meanings',len(missing),'missing examples',len(examples))
if __name__=='__main__':
 import sys
 if '--extract' in sys.argv:extract()
 if '--build' in sys.argv:build()
