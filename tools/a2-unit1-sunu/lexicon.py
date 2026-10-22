from pathlib import Path
import os
import json,csv,re,collections,fitz
R=Path(os.environ.get("A2_SUNU_WORK",Path(__file__).resolve().parents[3]/"a2-source"));repo=Path(os.environ.get("A2_SUNU_REPO",Path(__file__).resolve().parents[2]));O=repo/'kitaplar/lise-a2/tatil-donusu/sunum/assets'
def norm(s):return s.translate(str.maketrans('Iİ','ıi')).lower().replace('’',"'").replace('‘',"'").strip(" .,:;!?\"“”‘’()[]{}–—/\\")
d={x:{} for x in ['words','forms','examples','phrases']}
for p in sorted(repo.glob('kitaplar/**/translations*.json'),key=lambda p:(p.parent.name!='tatil-donusu','2026' in p.name)):
 try:g=json.loads(p.read_text())
 except:continue
 for k,v in g.get('words',{}).items():
  if isinstance(v,list) and len(v)==5 and all(isinstance(a,str) and a.strip() for a in v):d['words'].setdefault(norm(k),v)
 for k,v in g.get('examples',{}).items():
  if isinstance(v,dict):v=[v.get('tr',v.get('exampleTr','')),v.get('values',v.get('translations',v.get('examples',[])))]
  if isinstance(v,list) and len(v)==2 and isinstance(v[1],list) and len(v[1])==5 and v[0] and all(v[1]):d['examples'].setdefault(norm(k),v)
 for k,v in g.get('forms',{}).items():
  if isinstance(v,dict) and v.get('lemma'):d['forms'].setdefault(norm(k),v)
 for k,v in g.get('phrases',{}).items():
  if isinstance(v,dict) and len(v.get('translations',[]))==5:d['phrases'].setdefault(norm(k),v)
known=set(d['words'])|set(d['forms'])|set(d['phrases'])
fix={'milli':'millî','mükafatla':'mükâfatla','komsu':'komşu','ıslam':'islâm','hazi:ne':'hazine','ıstanbul':'istanbul',"ıstanbul'da":"istanbul'da",'ürkçe':'türkçe','onümüzdeki':'önümüzdeki','nşallah':'inşallah','corafya':'coğrafya','dinlevin':'dinleyin','ekerleme':'tekerleme','efterinize':'defterinize','idri':'idris','sidri':'idris','10/€c':'10/c','tatiltürünü':'tatil türünü','tatileneile':'tatile ne ile','neile':'ne ile','yılönce':'yıl önce','buyıl':'bu yıl','cevabınıiçeren':'cevabını içeren','birmetin':'bir metin','teşekkürederim':'teşekkür ederim','z.iki':'iki','a.dinleyin':'dinleyin','ahvaltı':'kahvaltı','eydoğu':'güneydoğu','ulmaça':'bulmaca','lmaça':'bulmaca','yamam':'tamam','kat$ı':'karşı','oyle':'öyle','etim':'ettim','antalta':'antalya','dördünü':'dördüncü','labaratuvarı':'laboratuvarı','meden':'-meden','tikten':'-tikten'}
noise=set('dbtk lan dee geçt güze bil turi ati «iy ald pir sia mas til pon anr soya oluşturu kon teh itleri şehirl çiz mem atra keni irüme ard tli nlik tiy otobü ahati hiz min mmm metini ilgilide ote day cin bü ge he j p s t ti v w z'.split());noise.update(['1.ünite','a,b,c,ç,d.ef.g','-b,c.d.gdeğilmi','myılmazaturkiyemaarif.com','->ü'])
rs=json.loads((R/'rendered.json').read_text());spots=[]
for r in rs:
 hs=[]
 for row in csv.DictReader((R/f'{r["sequence"]:03}.tsv').open(),delimiter='\t',quoting=csv.QUOTE_NONE):
  t=row.get('text','').strip();k=fix.get(norm(t),norm(t))
  if not t or float(row.get('conf') or -1)<45 or k in noise or not re.search('[a-zçğıöşü]',k) or (len(k)<3 and k not in known) or re.match(r'^(dk|dbtk|a2)[.:0-9]',k) or re.fullmatch(r'[a-d]\.\d|[12]/[ac]',k):continue
  hs.append({'text':t,'key':k,'x':int(row['left'])/1921,'y':int(row['top'])/1080,'w':int(row['width'])/1921,'h':int(row['height'])/1080})
 doc=fitz.open(R/f'part{r["part"]}-full.pdf');page=doc[r['slide']-1];W,H=page.rect.width,page.rect.height;red=[]
 for block in page.get_text('dict')['blocks']:
  for line in block.get('lines',[]):
   for sp in line['spans']:
    c=sp['color']
    if (c>>16)&255>170 and (c>>8)&255<110 and c&255<110:red.append(fitz.Rect(sp['bbox']))
 for x0,y0,x1,y1,t,*_ in page.get_text('words'):
  if not any(fitz.Rect(x0,y0,x1,y1).intersects(b) for b in red):continue
  k=fix.get(norm(t),norm(t))
  if len(k)<2 or not re.search('[a-zçğıöşü]',k):continue
  hs.append({'text':t,'key':k,'x':x0/W,'y':y0/H,'w':(x1-x0)/W,'h':(y1-y0)/H,'answer':True})
 spots.append(hs)
(O/'word-spots.json').write_text(json.dumps(spots,ensure_ascii=False,separators=(',',':')));(R/'dictionary.json').write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')))
ks=collections.Counter(h['key'] for hs in spots for h in hs);missing=[k for k in ks if k not in d['words'] and k not in d['forms'] and k not in d['phrases']];(R/'missing.txt').write_text('\n'.join(missing));print('hits',sum(map(len,spots)),'missing',len(missing));print(' '.join(missing))
