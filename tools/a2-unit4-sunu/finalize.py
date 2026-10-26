from pathlib import Path
import json,re,collections,copy
R=Path(__file__).resolve().parents[2];W=R.parent/'rebuild4';O=R/'kitaplar/lise-a2/simdi-haberler/sunum';A=O/'assets'
D=json.loads((W/'pooled-dictionary.json').read_text())
for k,v in list(D['examples'].items()):
 if isinstance(v,dict):D['examples'][k]=[v.get('tr',''),v.get('values',[])]
for line in (R/'tools/a2-unit4-sunu/extra.tsv').read_text().splitlines():
 if not line.strip():continue
 parts=line.split('|');assert len(parts)==7,(len(parts),line)
 k,lemma,*values=parts
 if k==lemma:D['words'][k]=values
 else:D['forms'][k]={'lemma':lemma,'formTranslations':values}
alias={'berlerini':'haberlerini','eş/yakın':'eş','a2.1':'a2','1.bilgisayar':'bilgisayar','2.tablet':'tablet','ıstanbul':'istanbul',"ıstanbul'da":"istanbul'da","ıstanbul'un":"istanbul'un",'kıtabı':'kitabı','ruzgar':'rüzgâr','rüzgar':'rüzgâr','bulmaka':'bulmaca','dakka':'dakika','komsu':'komşu','dunya':'dünya','arasıra':'ara sıra','hergün':'her gün','herzaman':'her zaman','ağlık':'sağlık','eduydun':'duydun','eknoloji':'teknoloji','ergiyi':'dergiyi','evizyonda':'televizyonda','kon om i':'ekonomi','konomi':'ekonomi','gmurlu':'yağmurlu','garlı':'karlı','ifajde':'ifade','kaşınızdayız':'karşınızdayız','koso':'kosova','osova':'kosova','kulbu':'kulübü','odeyeceksin':'ödeyeceksin','renciler':'öğrenciler','rencileri':'öğrencileri','simlere':'resimlere','vlenmiş':'evlenmiş','vvetli':'kuvvetli','üzgârlı':'rüzgârlı','ğitim':'eğitim','baku':'bakü','b.bence':'bence','b.dil':'dil','amamlayın':'tamamlayın','eşleş':'eşleştirin','denle':'dinle','elektirikler':'elektrikler','düşü':'düşün','mumyarın':'mumyanın','radio':'radyo','zereler':'gazeteler','zeteler':'gazeteler','hayırduymadım':'duymadım','mi?güle':'güle','yarın.hava':'hava','insan.hasta':'insan','alacağım.her':'alacağım','macaristan.ve':'macaristan',"röportajlar'canlı":'röportajlar',"istanbul\"dur":"istanbul'dur",'ıhtimal/olasılık/tahmin':'ihtimal/olasılık/tahmin'}
noise={'4.unıte','5nık','a2.1','alşalım','b.üçyüzyıl','detaylarıy','edir','erler','esanat','geçin.a','gürül','güvenil','inizi','istan','kadara','karıyorlar','landı','likte','lında','ncil','olduğ','pakis','reniriz','rincisi','rinden','sizokulunuzdane','sına','telerin','televizyonda.en.çok','türetkinlikler','ullanım','unuzu','yarışması(w','çoküzül','önleriyle','ürkç','şilerle','şulda','gaze','ağmış'}
slides=[];spots=[];missing=collections.Counter()
for file in sorted(W.glob('rendered-*.json')):
 s,row=json.loads(file.read_text());clean=[]
 for w in row:
  k=w['key']
  if k in noise:continue
  k=alias.get(k,k)
  if not re.search('[a-zçğıöşü]',k):D['words'].setdefault(k,[w['text']]*5)
  if k not in D['words'] and k not in D['forms'] and k not in D['phrases']:missing[k]+=1
  w['key']=k;clean.append(w)
 if s['sourcePart']==2 and s['sourcePartSlide'] in [29,38]:s['videoUrl']='https://www.youtube.com/watch?v='+('t5A7YYzzveI' if s['sourcePartSlide']==29 else '9uewQP8TmXA')
 slides.append(s);spots.append(clean)
for line in (R/'tools/a2-unit4-sunu/examples.tsv').read_text().splitlines():
 parts=line.split('|');assert len(parts)==7,(len(parts),line)
 D['examples'][parts[0]]=[parts[1],parts[2:]]
for f in D['forms'].values():
 lemma=f.get('lemma','');lo=lemma.replace('İ','i').replace('I','ı').lower()
 if lemma not in D['words'] and lo in D['words']:D['words'][lemma]=D['words'][lo]
 if lemma not in D['words'] and lemma[:1].isupper():D['words'][lemma]=[lemma]*5
 ex=D['examples'].get(lemma) or D['examples'].get(lo)
 if ex and not f.get('exampleTr'):f['exampleTr']=ex[0];f['examples']=ex[1]
used={w['key'] for row in spots for w in row};roots={D['forms'][k]['lemma'] for k in used if k in D['forms']};need=used|roots
D['words']={k:v for k,v in D['words'].items() if k in need};D['forms']={k:v for k,v in D['forms'].items() if k in used};D['examples']={k:v for k,v in D['examples'].items() if k in need};D['phrases']={k:v for k,v in D['phrases'].items() if k in used or all(w in used for w in k.split())}
(A/'slides.json').write_text(json.dumps({'slides':slides},ensure_ascii=False,indent=2));(A/'word-spots.json').write_text(json.dumps(spots,ensure_ascii=False));(A/'translations.json').write_text(json.dumps(D,ensure_ascii=False));(A/'answer-overlays.json').write_text('{}');(W/'missing-final.json').write_text(json.dumps(missing,ensure_ascii=False,indent=2));print('targets',len(used),'missing',len(missing));print(' | '.join(sorted(missing)))
