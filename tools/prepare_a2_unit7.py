"""Prepare A2 unit 7 using source PDF coordinates and editorial vocabulary only."""
import json,re,unicodedata
from pathlib import Path
import fitz
ROOT=Path('kitaplar/lise-a2/akilli-teknoloji')
def norm(s):
 return re.sub(r'^[^\w]+|[^\w]+$','',s.replace('’',"'").replace('I','ı').replace('İ','i').lower())
def save(name,d): (ROOT/name).write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')))
def extract():
 doc=fitz.open('../upload/7.ünite(1).pdf');pages=[];texts=[]
 for n,p in enumerate(doc,1):
  raw=[]
  for x0,y0,x1,y1,t,b,l,wi in p.get_text('words'):
   # Separate punctuation-attached labels using proportional source rectangles.
   t=t.replace('başlıyor.Bir','başlıyor. Bir')
   parts=re.split(r'\s+|(?<=vardı)(?=ne)|(?<=\))(?=[A-Za-zÇĞİÖŞÜçğıöşü])|(?<=\d)-(?=[A-Za-zÇĞİÖŞÜçğıöşü])|(?<=[?:])(?=[A-Za-zÇĞİÖŞÜçğıöşü])|(?<=\d\.)(?=[A-Za-zÇĞİÖŞÜçğıöşü“])|(?<=[abcç]\.)\b(?=[A-Za-zÇĞİÖŞÜçğıöşü])',t)
   offset=0
   for part in parts:
    width=(x1-x0)*len(part)/len(t)
    if any(c.isalnum() for c in part):raw.append(dict(t=part,x=(x0+offset)/p.rect.width,y=y0/p.rect.height,w=width/p.rect.width,h=(y1-y0)/p.rect.height,block=b,line=l))
    offset+=width
  dedup=[]
  for w in raw:
   duplicate=False
   for other in dedup:
    if norm(w['t'])!=norm(other['t']):continue
    iw=max(0,min(w['x']+w['w'],other['x']+other['w'])-max(w['x'],other['x']))
    ih=max(0,min(w['y']+w['h'],other['y']+other['h'])-max(w['y'],other['y']))
    if iw*ih/max(1e-12,min(w['w']*w['h'],other['w']*other['h']))>.8:duplicate=True;break
   if not duplicate:dedup.append(w)
  raw=dedup
  words=[];groups=[];j=0
  while j<len(raw):
   w=raw[j];indices=[len(words)];full=w['t'];words.append(w);j+=1
   while full.endswith('-') and not full.endswith('?-') and j<len(raw) and 0<raw[j]['y']-w['y']<w['h']*1.8 and raw[j]['x']<w['x']:
    full=full[:-1]+raw[j]['t'];indices.append(len(words));w=raw[j];words.append(w);j+=1
   fixed={'bılım':'bilim','teknolojı':'teknoloji','dergısı':'dergisi','kösesinde':'köşesinde'}
   key=fixed.get(norm(full),norm(full))
   for i in indices:words[i]['entryKey']=key
   if len(indices)>1:groups.append(dict(key=key,text=full,indices=indices))
  for w in words:w.pop('block');w.pop('line')
  # A missing space in the source poem must not become a dictionary entry.
  for w in words:
   if w['entryKey']=='vardıne':w['entryKey']='vardı';w['t']='vardı'
  if n==3:
   # The outlined article title is vector artwork, absent from the PDF text layer.
   for t,(x0,y0,x1,y1) in [('Bu',(380,625,574,736)),('Sadece',(605,620,1117,737)),('Bir',(365,755,563,862)),('Telefon',(586,750,1116,872)),('Değil!',(1140,745,1580,887))]:
    words.append(dict(t=t,x=x0/3204,y=y0/4054,w=(x1-x0)/3204,h=(y1-y0)/4054,entryKey=norm(t)))
  if n==20:
   # Tighten tilted lettering rectangles to prevent adjacent lines capturing clicks.
   boxes={'Bir':(2040,783,2129,841),'hafta':(2150,775,2318,829),'zamanın':(2050,849,2328,906),'var!':(2347,824,2470,874)}
   for w in words:
    if w['t'] in boxes and w['x']>.6 and w['y']<.24:
     x0,y0,x1,y1=boxes[w['t']];w.update(x=x0/3204,y=y0/4054,w=(x1-x0)/3204,h=(y1-y0)/4054)
  pages.append(dict(page=n,bookPage=134+n,image=f'pages/page-{n:03}.webp',words=words,wordGroups=groups,phraseGroups=[],exportWords=[dict(t=g['text'],entryKey=g['key']) for g in groups]+[dict(t=w['t'],entryKey=w['entryKey']) for i,w in enumerate(words) if not any(i in g['indices'] for g in groups)]))
  texts.append(p.get_text())
 save('pages.json',pages);save('source-text.json',texts)
 return pages
def build():
 pages=json.loads((ROOT/'pages.json').read_text());base={k:{} for k in ['words','forms','examples','phrases','lemmas']}
 for path in Path('kitaplar').glob('**/translations.json'):
  if path.parent==ROOT:continue
  inherited=json.loads(path.read_text())
  # Older A1 exports start arrays with Turkish and lack French. Never import
  # those positional arrays into the five-target-language schema.
  if inherited.get('metadata',{}).get('languages')!=['en','ru','ky','ar','fr'] and 'lise-a2' not in str(path):continue
  def valid_values(a):
   return isinstance(a,list) and len(a)==5 and all(isinstance(v,str) and v.strip() for v in a) and not re.search('[\u0400-\u04ff\u0600-\u06ff]',a[0]+a[4]) and not re.search('[\u0400-\u04ff]',a[3])
  for section in base:
   for k,v in inherited.get(section,{}).items():
    if section=='words':valid=valid_values(v)
    elif section=='examples':valid=valid_values(v[1] if isinstance(v,list) else v.get('values'))
    else:
     attrs=['translations'] if section in ['phrases','lemmas'] else ['formTranslations','lemmaTranslations']
     valid=all(valid_values(v.get(a)) for a in attrs)
     if v.get('examples'):valid=valid and valid_values(v['examples'])
    if valid:base[section][norm(k)]=v
 g={k:dict(base.get(k,{})) for k in ['words','forms','examples','phrases','lemmas']}
 for file in ['unit7-lexicon.tsv','unit7-forms.tsv','unit7-verbs.tsv']:
  for line in Path('tools',file).read_text().splitlines():
   a=line.split('|');assert len(a) in [6,7],(file,a)
   key=norm(a[0]);g['words'][key]=a[-5:]
   if len(a)==7:
    lemma=a[1];values=g['words'].get(norm(lemma)) or g['lemmas'].get(norm(lemma),{}).get('translations')
    if values:g['forms'][key]={'text':a[0],'lemma':lemma,'lemmaType':'verb' if lemma.endswith(('mak','mek')) else 'noun','lemmaTranslations':values,'formTranslations':a[-5:]}
   else:g['forms'].pop(key,None)
 names={'adıgüzel':['Adıgüzel (surname)','Адыгюзель (фамилия)','Адыгюзел (фамилия)','أديغوزيل (اسم عائلة)','Adıgüzel (nom de famille)'],'aksakal':['Aksakal (surname)','Аксакал (фамилия)','Аксакал (фамилия)','أق سقال (اسم عائلة)','Aksakal (nom de famille)'],'ayşenur':['Ayşenur (name)','Айшенур','Айшенур','آيشَنور','Ayşenur'],'müfit':['Müfit (name)','Мюфит','Мүфит','مفيد','Müfit']}
 for k,v in names.items():g['words'][k]=v
 for k in ['altunizade','cevizlibağ','yenimahalle/ankara']:
  g['words'][k]=[k+' (place name)',k+' (топоним)',k+' (жердин аты)',k+' (اسم مكان)',k+' (nom de lieu)']
 for k in ['13a456v','r9','say-20','sor-17','sp','tekbil','tektel','türkbil','türktel','zius']:
  g['words'][k]=[k+' (model / brand / code)',k+' (модель / марка / код)',k+' (модель / бренд / код)',k+' (طراز / علامة / رمز)',k+' (modèle / marque / code)']
 keys={w['entryKey'] for p in pages for w in p['words']}
 for code in ['s.046','s.047','s.048','s.049','v.008']:
  label=code.upper();isvideo=code.startswith('v')
  g['words'][code]=[label+(' video reference' if isvideo else ' listening reference'),label+(' — код видео' if isvideo else ' — код аудиозаписи'),label+(' — видео коду' if isvideo else ' — угуу жазуусунун коду'),label+(' — رمز الفيديو' if isvideo else ' — رمز التسجيل الصوتي'),label+(' — référence vidéo' if isvideo else ' — référence audio')]
  tr=label+' kodu '+('videoyu' if isvideo else 'dinleme kaydını')+' gösterir.'
  g['examples'][code]={'tr':tr,'values':[label+' identifies the '+('video.' if isvideo else 'listening recording.'),label+' обозначает '+('видео.' if isvideo else 'аудиозапись.'),label+' '+('видеону' if isvideo else 'угуу жазуусун')+' көрсөтөт.',label+' يشير إلى '+('الفيديو.' if isvideo else 'التسجيل الصوتي.'),label+' désigne '+('la vidéo.' if isvideo else 'l’enregistrement audio.')]}
 for k in list(g['forms']):
  if k in g['words'] and k in keys and not g['forms'][k].get('formTranslations'):g['forms'].pop(k)
 # Restrict every teaching entry and quiz to this unit.
 for section in ['words','forms','examples']:
  g[section]={k:v for k,v in g[section].items() if k in keys}
 g['phrases']={k:v for k,v in g['phrases'].items() if all(norm(x) in keys for x in k.split())}
 g['lemmas']={v['lemma']:{'translations':v['lemmaTranslations']} for v in g['forms'].values() if v.get('lemmaTranslations')}
 g['quizVocabulary']=[k for k in g['words'] if k.isalpha() and len(k)>2]
 g['metadata']={'unit':7,'languages':['en','ru','ky','ar','fr'],'translationSource':'ChatGPT editorial translations; no machine translation service','status':'in progress'}
 for line in Path('tools/unit7-examples.tsv').read_text().splitlines():
  keysline,tr,*values=line.split('|');assert len(values)==5,line
  for k in keysline.split(','):
   k=norm(k)
   g['examples'][k]={'tr':tr,'values':values}
   if k in g['forms']:g['forms'][k]['exampleTr']=tr;g['forms'][k]['examples']=values
 for line in Path('tools/unit7-phrases.tsv').read_text().splitlines():
  phrase,*rest=line.split('|');values=rest[:5];examplekey=norm(rest[5]);example=g['examples'].get(examplekey) or base['examples'].get(examplekey)
  if isinstance(example,list):example={'tr':example[0],'values':example[1]}
  if not example:
   form=g['forms'].get(examplekey,{})
   if form.get('exampleTr'):example={'tr':form['exampleTr'],'values':form['examples']}
  assert example,(phrase,examplekey)
  g['phrases'][norm(phrase)]={'translations':values,'exampleTr':example['tr'],'examples':example['values']}
 usedphrases=set()
 for page in pages:
  joined={x['indices'][0]:x for x in page['wordGroups']};skip={i for x in page['wordGroups'] for i in x['indices'][1:]}
  seq=[]
  for i,w in enumerate(page['words']):
   if i in skip:continue
   group=joined.get(i);seq.append((norm(group['text'] if group else w['t']),group['indices'] if group else [i]))
  candidates=[]
  for phrase in sorted(g['phrases'],key=lambda k:-len(k.split())):
   parts=[norm(t) for t in phrase.split()]
   if len(parts)<2:continue
   for i in range(len(seq)-len(parts)+1):
    if [x[0] for x in seq[i:i+len(parts)]]!=parts:continue
    indices=[j for x in seq[i:i+len(parts)] for j in x[1]]
    if any(set(indices)&set(c['indices']) for c in candidates):continue
    original=' '.join(joined[seq[j][1][0]]['text'] if seq[j][1][0] in joined else page['words'][seq[j][1][0]]['t'] for j in range(i,i+len(parts)))
    candidates.append({'key':phrase,'text':original,'indices':indices});usedphrases.add(phrase)
  page['phraseGroups']=candidates
 g['phrases']={k:v for k,v in g['phrases'].items() if k in usedphrases}
 g['metadata']['status']='meanings and examples complete; technical verification pending'
 save('pages.json',pages)
 save('translations.json',g)
 missing=[];examples=[]
 for k in sorted(keys):
  if not re.search(r'[^\W\d_]',k) or re.match(r'^[smv]\.\d+$',k):continue
  if k not in g['words'] and k not in g['forms']:missing.append(k)
  if k not in g['examples'] and not g['forms'].get(k,{}).get('exampleTr'):examples.append(k)
 print('missing meanings',missing);print('missing examples',len(examples));Path('../missing-examples7.txt').write_text('\n'.join(examples))
if __name__=='__main__':
 import sys
 if '--build' in sys.argv:
  build()
  from repair_a2_print_vocabulary import run
  run()
 else:extract()
