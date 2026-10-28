"""Rebuild unit 6 vocabulary hit areas from the visible slide pixels.

Input: Tesseract TSV passes in --audit-dir (native psm 3/11 and threshold psm 11).
The original slide images, answers and audio remain unchanged.
"""
import argparse, collections, csv, gzip, json, re, tempfile, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'kitaplar/lise-a2/hayat-birlikte-guzel/sunum'
HERE = Path(__file__).parent
def norm(s):
    return unicodedata.normalize('NFC', str(s)).replace('I','ı').replace('İ','i').lower().replace('’',"'").strip(' \t\n.,:;!?()[]{}\"“”‘…−•-/')
def valid5(a):
    return (isinstance(a,list) and len(a)==5 and all(isinstance(x,str) and x.strip() for x in a)
        and bool(re.search('[а-яА-ЯёЁ]',a[1])) and bool(re.search('[а-яА-ЯөӨүҮңҢ]',a[2]))
        and bool(re.search('[\u0600-\u06ff]',a[3])) and not re.search('[\u0600-\u06ffа-яА-Я]',a[4]))
def entry(g,k):
    ph=g.get('phrases',{}).get(k) or {}; f=g.get('forms',{}).get(k) or {}; e=g.get('examples',{}).get(k) or {}
    meanings=ph.get('translations') or f.get('formTranslations') or g.get('words',{}).get(k)
    tr=ph.get('exampleTr') or f.get('exampleTr') or (e[0] if isinstance(e,list) else e.get('tr'))
    vals=ph.get('examples') or f.get('examples') or ((e[1:] if len(e)==6 else e[1]) if isinstance(e,list) else e.get('values'))
    return meanings,tr,vals
def load(p): return json.loads(p.read_text())
def dump(p,x): p.write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')

def main():
    args=argparse.ArgumentParser();args.add_argument('--audit-dir',type=Path);a=args.parse_args();audit=a.audit_dir
    if audit is None:
        temporary=tempfile.TemporaryDirectory();audit=Path(temporary.name)
        snapshot=json.loads(gzip.decompress((HERE/'ocr-inputs.json.gz').read_bytes()))
        for name,content in snapshot.items():
            target=audit/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(content)
    original=load(audit/'manifest.json'); g=load(OUT.parent/'translations.json')
    for section in ['words','forms','examples','phrases','lemmas']:
        g[section]={norm(k):v for k,v in g.get(section,{}).items()}
    pool={}; examples={}; source={}
    for p in sorted((ROOT/'kitaplar').rglob('translations.json')):
        if p==OUT/'translations.json':continue
        d=load(p)
        for section in ['words','forms','phrases','examples']:
            for raw in d.get(section,{}):
                k=norm(raw);m,tr,vals=entry(d,raw)
                if valid5(m) and tr and valid5(vals):pool.setdefault(k,(m,tr,vals));source.setdefault(k,str(p.relative_to(ROOT)))
                if tr and valid5(vals):
                    for token in set(re.findall(r"[\w]+(?:['’][\w]+)?",norm(tr))):
                        if token not in examples or len(tr)<len(examples[token][0]):examples[token]=(tr,vals)
    for line in (HERE/'examples.tsv').read_text().splitlines():
        keys,tr,*vals=line.split('\t');assert valid5(vals),(keys,vals)
        for k in keys.split('|'):examples[k]=(tr,vals)
    extra={}
    for line in (HERE/'extra.tsv').read_text().splitlines():
        k,*m=line.split('\t');m=[x.strip() for x in m];assert len(m)==5,(k,m)
        # Person names may use Latin characters in every language.
        assert valid5(m) or k in ['aykız'],k
        assert k in examples,('missing example',k)
        tr,vals=examples[k];extra[k]=(m,tr,vals)
    pool.update(extra)
    def resolve(k):
        m,tr,v=entry(g,k)
        if m and tr and v and len(m)==len(v)==5:return True
        if k not in pool:return False
        m,tr,v=pool[k];g['words'][k]=m;g['examples'][k]={'tr':tr,'values':v};return True

    # These corrections were checked against the visible slide images.
    corrections={'çarplım':'çarptım','nasil':'nasıl','oncelikle':'öncelikle','dıkkatlı':'dikkatli',
        'tenefüs':'teneffüs','tenefüste':'teneffüste','esya':'eşya','afışteki':'afişteki',
        'kuwetli':'kuvvetli','kuwvetli':'kuvvetli','kuwvetli':'kuvvetli','taşima':'taşıma',
        'oğrenciler':'öğrenciler','trafık':'trafik','sari':'sarı','ruralları':'kuralları','âile':'aile','6.ünite':'ünite'}
    splits={'biliyormuydunuz':['biliyor','muydunuz'],'buifadelerin':['bu','ifadelerin'],
        'içinkonsolosluğa':['için','konsolosluğa'],'bahçelerdeyerlereçöp':['bahçelerde','yerlere','çöp'],
        'buyüzden':['bu','yüzden'],'gecegündüz':['gece','gündüz'],'adımadım':['adım','adım'],
        'inceleyin.siz':['inceleyin','siz'],'sağdanbazıülkel':['sağdan','bazı','ülkelerinde'],
        'erindeise':['ülkelerinde','ise']}
    fragment_corrections={5:{'gelmek':'gelmektedir','tedir':'gelmektedir','ülkel':'ülkelerinde','erinde':'ülkelerinde'},
        13:{'söy':'söyleyin','leyin':'söyleyin'},69:{'kapatı':'kapatınız','niz':'kapatınız','nız':'kapatınız'},70:{'minde':'çekiminde','çeki':'çekiminde'}}
    ignored={'dk','dbtk','dbik','trt','a2','trt1','s.072','prof','dr','vb'}
    slides=original['slides']; before_counts=[len(s['words']) for s in slides]; records=[];unresolved=collections.defaultdict(set)
    for i,s in enumerate(slides,1):
        candidates=[]
        for sub in ['ocr5','ocr3','ocr4']:
            file=audit/sub/f'{i}.tsv'
            if not file.exists():continue
            with file.open() as f:rows=list(csv.DictReader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
            if not rows:continue
            width=int(rows[0]['width']);height=int(rows[0]['height']);words=[r for r in rows if r['level']=='5' and r['text'].strip()]
            for j,r in enumerate(words):
                raw=r['text'];k=norm(raw);conf=float(r['conf']);x,y,w,h=[int(r[c]) for c in ['left','top','width','height']]
                if not k or k in ignored or not re.search('[a-zçğıöşüâîû]',k):continue
                # Labels and page numbers are navigation, not lexical content.
                if y/height<.12 and x/width>.85:continue
                if i==2 and y/height>.72:continue
                if i==3 and y/height>.35:continue
                k=corrections.get(k,k)
                k=fragment_corrections.get(i,{}).get(k,k)
                rect={'x':100*x/width,'y':100*y/height,'w':100*w/width,'h':100*h/height}
                # OCR occasionally treats an illustration as one enormous word.
                if rect['w']>32 or rect['h']>10 or rect['w']<.25 or rect['h']<.75:continue
                if k in splits:
                    offset=0;tokens=splits[k];total=sum(map(len,tokens))
                    for t in tokens:
                        if resolve(t):candidates.append(dict(rect,x=rect['x']+rect['w']*offset/total,w=rect['w']*len(t)/total,text=t,confidence=conf,origin=sub))
                        offset+=len(t)
                    continue
                # Join a word split by a printed line-end hyphen; keep both visible fragments clickable.
                if raw.rstrip().endswith('-') and j+1<len(words):
                    nr=words[j+1];joined=k+norm(nr['text'])
                    if resolve(joined):
                        candidates.append(dict(rect,text=joined,confidence=conf,origin=sub));nx,ny,nw,nh=[int(nr[c]) for c in ['left','top','width','height']]
                        candidates.append({'text':joined,'x':100*nx/width,'y':100*ny/height,'w':100*nw/width,'h':100*nh/height,'confidence':float(nr['conf']),'origin':sub})
                        nr['text']='';continue
                if conf>=55 and len(k)>1 and resolve(k):candidates.append(dict(rect,text=k,confidence=conf,origin=sub))
                elif conf>=65 and len(k)>2 and re.fullmatch("[a-zçğıöşüâîû]+(?:'[a-zçğıöşüâîû]+)?",k):unresolved[k].add(i)
        # Prefer native OCR, then supplement only genuinely uncovered words.
        areas=[]
        for r in candidates:
            cx=r['x']+r['w']/2;cy=r['y']+r['h']/2
            if any(q['x']<=cx<=q['x']+q['w'] and q['y']-.2<=cy<=q['y']+q['h']+.2 for q in areas):continue
            areas.append(r)
        # A second OCR pass can put an oversized duplicate across the previous line.
        areas=[r for r in areas if not any(q is not r and q['text']==r['text'] and r['h']>q['h']*1.4
            and max(r['x'],q['x'])<min(r['x']+r['w'],q['x']+q['w'])
            and max(r['y'],q['y'])<min(r['y']+r['h'],q['y']+q['h']) for q in areas)]
        if i==39:
            for r in areas:
                if r['text']=='görebiliriz' and r['y']<40:r['y']=36.2;r['h']=2.9
        # Retain earlier hand-positioned choices when their text is present in this part of the image.
        for r in s['words']:
            k=norm(r['text'])
            if len(k)>55 or '\n' in k or '\x0b' in k or not resolve(k):continue
            tokens=k.split();over=[q for q in areas if max(r['x'],q['x'])<min(r['x']+r['w'],q['x']+q['w']) and max(r['y'],q['y'])<min(r['y']+r['h'],q['y']+q['h'])]
            if len(tokens)==1:
                if any(norm(q['text'])==k for q in over):continue
                # Text already manually transcribed on prior edits; do not retain answer-only fields.
                if len(over)==0 and len(k)>1 and r['w']<18 and r['h']<8:areas.append(dict(r,text=k,confidence=100,origin='previous-manual'))
            elif i==3 and k=='hayat birlikte güzel':
                areas.append(dict(r,text=k,confidence=100,origin='verified-title'))
            elif all(any(t in norm(q['text']).split() for q in over) for t in tokens):
                # Separate fragments follow wrapped phrases without blocking empty space.
                for q in over:
                    if norm(q['text']) in tokens:q['phrase']=k
        areas.sort(key=lambda r:(r['y'],r['x']))
        s['words']=[{k:(round(v,4) if isinstance(v,float) else v) for k,v in r.items() if k not in ['confidence','origin']} for r in areas]
        records.append({'slide':i,'before':before_counts[i-1], 'after':len(areas),'tokens':sorted(set(q['text'] for q in areas))})
    used={w['text'] for s in slides for w in s['words']}|{w['phrase'] for s in slides for w in s['words'] if 'phrase' in w}
    # The presentation has its own supplement; the PDF dictionary remains authoritative for PDF mode.
    for sec in ['words','forms','examples','phrases']:
        g[sec]={k:v for k,v in g[sec].items() if k in used or sec=='words' and any((f.get('lemma') or f.get('base'))==k for f in g['forms'].values())}
    missing=[k for k in used if not all(entry(g,k))]
    assert not missing,missing
    # The original first slide is a blank white sheet, not presentation content.
    keep=[j for j,s in enumerate(slides) if not (s.get('part')==1 and s.get('source_slide')==1)]
    slides=[slides[j] for j in keep];records=[records[j] for j in keep]
    for j,record in enumerate(records,1):record['slide']=j
    dump(OUT/'manifest.json',{'slides':slides});dump(OUT/'translations.json',g)
    dump(audit/'unresolved.json',{k:sorted(v) for k,v in unresolved.items()})
    dump(OUT/'vocabulary-audit.json',{'method':'Visible slide pixels; native psm3/11 and threshold psm11; editorial corrections; five-language dictionary and examples','slides':records,'totalSelections':sum(len(s['words']) for s in slides),'uniqueEntries':len(used),'newEditorialEntries':len(extra),'missingMeaningsOrExamples':len(missing)})
    print(json.dumps({'selections':sum(len(s['words']) for s in slides),'entries':len(used),'editorial':len(extra),'unresolvedCandidates':len(unresolved)}))

if __name__=='__main__':main()

