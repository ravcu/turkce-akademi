"""Curate OCR hits, preserve source forms, and reuse verified lesson lexicons."""
from pathlib import Path
import json,re,collections,difflib,copy
R=Path(__file__).resolve().parents[2];W=R.parent/'rebuild';O=R/'kitaplar/lise-a2/bir-gunum/sunum';A=O/'assets'
master=W/'merged-dictionary.json'
D=json.loads((master if master.exists() else A/'translations.json').read_text());added={}
for key,value in list(D['examples'].items()):
 if isinstance(value,dict):D['examples'][key]=[value.get('tr',''),value.get('values',[])]
for line in (R/'tools/a2-unit3-sunu/extra.tsv').read_text().splitlines():
 parts=line.split('|')
 if len(parts)!=7:raise ValueError((len(parts),line))
 k,lemma,*tr=parts;added[k]=(lemma,tr)
 if k==lemma or k.lower()==lemma.lower():D['words'][k]=tr
 else:D['forms'][k]={'lemma':lemma,'formTranslations':tr}
D['words']['zeka']=D['words']['zekâ']
# Grammar markers have explanatory meanings rather than invented words.
for k in ['abil','ebil','abilir']:
 D['words'][k]=['ability suffix (-Abil-)','суффикс возможности (-Abil-)','мүмкүнчүлүк мүчөсү (-Abil-)','لاحقة الاستطاعة (-Abil-)','suffixe de capacité (-Abil-)']
for k in ['im','iz','sin','siniz','ler','ir','eme','me','du']:
 D['words'][k]=['grammatical suffix','грамматический суффикс','грамматикалык мүчө','لاحقة نحوية','suffixe grammatical']
# In these examples the infinitive is visually split to show morphemes.
for k,lemma in [('zıpla-mak','zıplamak'),('oku-mak','okumak'),('oyna-mak','oynamak'),('söyle-mek','söylemek'),('zıpla-mak','zıplamak')]:
 if lemma in D['words']:D['forms'][k]={'lemma':lemma,'formTranslations':D['words'][lemma]}
for k,lemma in [('altıya','altı'),('dokuzu','dokuz'),('dördü','dört'),('yediyi','yedi'),('sekize','sekiz')]:
 if lemma in D['words']:D['forms'][k]={'lemma':lemma,'formTranslations':D['words'][lemma]}
for k,number in [('ikide','two'),('üçte','three')]:
 D['forms'][k]={'lemma':{'ikide':'iki','üçte':'üç'}[k],'formTranslations':{'ikide':['at two','в два','саат экиде','في الساعة الثانية','à deux heures'],'üçte':['at three','в три','саат үчтө','في الساعة الثالثة','à trois heures']}[k]}
D['forms']['buçukta']={'lemma':'buçuk','formTranslations':['at half past','в половине следующего часа','жарымда','في النصف بعد الساعة','à la demie']}
D['words']['geçe']=['past (when stating a time)','после (при указании времени)','өтүп (саат жөнүндө)','بعد (عند تحديد الوقت)','passées (pour indiquer l’heure)']
if 'hiçbir zaman' in D['phrases']:D['phrases']['asla/hiçbir zaman']=copy.deepcopy(D['phrases']['hiçbir zaman'])
# Correct OCR readings; source typography remains unchanged.
alias={'afış':'afiş','afışinizi':'afişinizi','bulmaka':'bulmaca','çekrek':'çeyrek','âynı':'aynı','ınek':'inek','ınsanları':'insanları','kıtabı':'kitabı','oğle':'öğle','etni':'metni','rigami':'origami','saaton':'saat on','hersabah':'her sabah','hergün':'her gün','eliften':"elif'ten",'amaben':'ama ben','neile':'ne ile','benasla/hiçbir':'asla/hiçbir','ayarlıyorsunuz':'ayarlıyorsunuz','saat.altı':'saat altı','saat.on':'saat on','saat.ona':'saat ona','yirmi.beş':'yirmi beş','beşi.beş':'beşi beş','gitar.kursu':'gitar kursu','her.akşam':'her akşam','yapmak-zeka':'yapmak','1amina':'amina','3.origami':'origami','saba':'sabah','progran':'program','zama':'zaman','oynayabiliri':'oynayabilir','oynayama':'oynayamam','eyebilirim':'yüzebilirim','yüztetmez':'yüzemez','yüztetmeztsin':'yüzemezsin','oynam':'oynamak','söyl':'söylemek','yüztetmetm':'yüzemem','yıkanm':'yıkarım','neile':'ne ile','saatisiniz':'saatiniz','saaton':'saat on','sağlı':'sağlık','p eki':'peki','once':'önce','öğleyemeğiye':'öğle yemeği','13.00’ten':"13.00'ten"}
alias.update({"peki'ne":"peki","b:saat":"saat","2.saat":"saat","5.saat":"saat","2 saat":"saat","5 saat":"saat","tetmeztler":"etmezler","2130'da":"21:30'da","asla/hiçbir":"hiçbir zaman","her.sabah.saat.07:45'te":"her sabah"})
noise={'3.unıte' ,'eğini','tebil','erim','larınızı','lamam','orum','maya','edersin?/genellik','söyleyebilirim./hayır','ekleyebilirsi','onlar........her','maarıf','ürkç','ışılda','düşün','bitir','ç.dinlen'}
# Keep words that belong to the source text or have a trustworthy OCR reading.
native=set(json.loads((W/'native-tokens.json').read_text())) if (W/'native-tokens.json').exists() else set();rows=[];missing=collections.Counter();allkeys=lambda:set(D['words'])|set(D['forms'])|set(D['phrases'])
for f in sorted(W.glob('rendered-*.json')):
 s,spots=json.loads(f.read_text());oldseq=s['sequence']
 if (s['sourcePart'],s['sourcePartSlide']) in [(1,38),(1,59)]:continue
 clean=[]
 for w in spots:
  k=w['key']
  if k in noise:continue
  k=alias.get(k,k);k=alias.get(k,k)
  tm=re.fullmatch(r'(\d{1,2})[.:](\d{2})[\'’](de|da|te|ta|ten|tan|den|dan|d)',k)
  if tm:
   hh,mm,suf=tm.groups();clock=f'{int(hh):02}:{mm}';frm='from ' if suf in ['ten','tan','den','dan'] else 'at '
   D['forms'][k]={'lemma':clock,'formTranslations':[frm+clock,('с ' if frm=='from ' else 'в ')+clock,clock+('дөн' if frm=='from ' else 'дө'),('من الساعة ' if frm=='from ' else 'في الساعة ')+clock,('à partir de ' if frm=='from ' else 'à ')+clock]}
  if re.fullmatch(r'[0-9 .:\-]+',k):D['words'][k]=[w['text']]*5
  if k not in allkeys():
   # Joined OCR words can be recovered only if their component words exist.
   bits=k.split('.')
   if len(bits)>1 and all(v in allkeys() for v in bits):k=' '.join(bits)
  w['key']=k
  if k not in allkeys():missing[k]+=1
  clean.append(w)
 s['sequence']=len(rows)+1;rows.append((s,clean))
# Add natural examples and show both lemma and the exact source form.
for line in (R/'tools/a2-unit3-sunu/examples.tsv').read_text().splitlines():
 parts=line.split('|');assert len(parts)==7,(len(parts),line)
 key,tr,*translations=parts;D['examples'][key]=[tr,translations]
for form in D['forms'].values():
 lemma=form.get('lemma','');lower=lemma.replace('İ','i').replace('I','ı').lower()
 if lemma=='arkadaşı':lemma='arkadaş';form['lemma']=lemma;lower=lemma
 if lemma not in D['words']:
  if lower in D['words']:D['words'][lemma]=D['words'][lower]
  elif re.fullmatch(r'[0-9:]+',lemma) or lemma[:1].isupper():D['words'][lemma]=[lemma]*5
 ex=D['examples'].get(lemma) or D['examples'].get(lower)
 if ex and not form.get('exampleTr'):form['exampleTr']=ex[0];form['examples']=ex[1]
# Ship only entries needed by this unit, their lemmas, and nearby phrase matches.
used={w['key'] for slide,ss in rows for w in ss};roots={D['forms'][k]['lemma'] for k in used if k in D['forms']}
needed=used|roots
D['words']={k:v for k,v in D['words'].items() if k in needed}
D['forms']={k:v for k,v in D['forms'].items() if k in used}
D['examples']={k:v for k,v in D['examples'].items() if k in needed}
# Matching is constrained by geometry in the reader, so unrelated phrases cannot be selected.
D['phrases']={k:v for k,v in D['phrases'].items() if all(t in used for t in k.split()) or k in used}
(A/'slides.json').write_text(json.dumps({'slides':[s for s,w in rows]},ensure_ascii=False,indent=2));(A/'word-spots.json').write_text(json.dumps([w for s,w in rows],ensure_ascii=False));(A/'answer-overlays.json').write_text('{}')
(A/'translations.json').write_text(json.dumps(D,ensure_ascii=False));(W/'missing-final.json').write_text(json.dumps(missing,ensure_ascii=False,indent=2));print('slides',len(rows),'spots',sum(len(w) for s,w in rows),'missing',len(missing));print(' | '.join(missing))
