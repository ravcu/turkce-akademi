"""Idempotent editorial repairs for A2 units 1–7. No translation service is used."""
import json,re,unicodedata
from pathlib import Path
BASE=Path('kitaplar/lise-a2')
SLUGS=['tatil-donusu','hafta-sonu-planin-ne','bir-gunum','simdi-haberler','dedemin-meslegi','hayat-birlikte-guzel','akilli-teknoloji']
def norm(s):return re.sub(r'^[\s.,:;!?()\[\]{}\"“”’…\-−•]+|[\s.,:;!?()\[\]{}\"“”’…\-−•]+$','',unicodedata.normalize('NFC',s).strip().replace('I','ı').replace('İ','i').lower().replace('’',"'").replace('‘',"'"))
def save(p,d):
 text=p.read_text();out=json.dumps(d,ensure_ascii=False,indent=2) if '\n  ' in text else json.dumps(d,ensure_ascii=False,separators=(',',':'));p.write_text(out+('\n' if text.endswith('\n') else ''))
def arrays(x):
 if isinstance(x,list):
  if len(x)==5 and all(isinstance(t,str) for t in x):yield x
  else:
   for v in x:yield from arrays(v)
 elif isinstance(x,dict):
  for v in x.values():yield from arrays(v)
def shifted(a):return bool(re.search('[\u0600-\u06ff]',a[4]))
def proper(a):return len(a)==5 and not re.search('[\u0400-\u04ff\u0600-\u06ff]',a[0]+a[4]) and not re.search('[\u0400-\u04ff]',a[3])
def run():
 data={s:json.loads((BASE/s/'translations.json').read_text()) for s in SLUGS}
 pages={s:json.loads((BASE/s/'pages.json').read_text()) for s in SLUGS}
 pool={}
 for p in Path('kitaplar').glob('**/translations.json'):
  if p.parent.name=='dedemin-meslegi':continue
  for a in arrays(json.loads(p.read_text())):
   if proper(a):pool[tuple(a[:4])]=a
 french=dict(line.split('|',1) for line in Path('tools/a2-unit5-french-repairs.tsv').read_text().splitlines())
 repaired=0
 for a in arrays(data[SLUGS[4]]):
  if shifted(a):
   fixed=pool.get(tuple(a[1:]))
   if fixed is None:fixed=a[1:]+[french[a[1]]]
   a[:]=fixed;repaired+=1
 # Correct residual grammatical errors exposed by the legacy column shift.
 d=data[SLUGS[4]]
 replacements={
 'örneğin':['for example','например','мисалы','على سبيل المثال','par exemple'],
 'öğrencilere':['to students','ученикам','окуучуларга','للطلاب','aux élèves'],
 'türkiye’ye':['to Turkey','в Турцию','Түркияга','إلى تركيا','en Turquie'],
 "türkiye'ye":['to Turkey','в Турцию','Түркияга','إلى تركيا','en Turquie'],
 'başına':['on/to his/her head','на его/её голову','анын башына','على رأسه أو رأسها','sur sa tête'],
 'tasarılarını':['your/his/her plans (object)','твои/его/её замыслы','пландарыңды; пландарын','خططك أو خططه أو خططها','tes projets ; ses projets'],
 'hayallerini':['your/his/her dreams (object)','твои/его/её мечты','кыялдарыңды; кыялдарын','أحلامك أو أحلامه أو أحلامها','tes rêves ; ses rêves']}
 for k,v in replacements.items():
  d['words'][k]=v
  if k in d['forms']:d['forms'][k]['formTranslations']=v
 for k in ['salom','zdravo']:data[SLUGS[0]]['words'][k][3]='مرحبًا'
 data[SLUGS[0]]['words']['shavili'][3]='شافيلي'
 for p in pages[SLUGS[4]]:
  for w in p['words']:
   if w['t'].startswith('*'):w['entryKey']=norm(w['t'].lstrip('*'))
 # Replace an Arabic/Cyrillic mixed-script surname typo.
 for a in arrays(data[SLUGS[3]]):a[:]=[v.replace('Ayşа','Ayşa') for v in a]
 # Fill missing lexical forms in the project page; keep existing contextual forms.
 corrections={norm(a[0]):a[1:] for line in Path('tools/a2-print-vocabulary-repairs.tsv').read_text().splitlines() if (a:=line.split('|'))}
 d=data[SLUGS[1]]
 for k,v in corrections.items():
  d['words'][k]=v
  if "'" in k:d['words'][k.replace("'",'’')]=v
  if k in d.get('forms',{}):d['forms'][k]['formTranslations']=v
 for p in pages[SLUGS[1]]:
  for w in p['words']:
   k=norm(w['t'])
   if '@' in w['t']:d['words'][k]=[w['t']]*5
 # Distinguish homographs by occurrence, retaining valid summer/eat/thick senses.
 write=['write (command)','напиши','жаз','اكتب','écris']
 writeform={'text':'yaz','lemma':'yazmak','lemmaType':'verb','lemmaTranslations':['to write','писать','жазуу','يكتب','écrire'],'formTranslations':write,'exampleTr':'Bana kısa bir not yaz.','examples':['Write me a short note.','Напиши мне короткую записку.','Мага кыскача кат жаз.','اكتب لي ملاحظة قصيرة.','Écris-moi un petit mot.']}
 for s in [SLUGS[5],SLUGS[6]]:
  d=data[s];d['words']['yaz:emir']=write;d['forms']['yaz:emir']=writeform
  for p in pages[s]:
   if p['page']!=(14 if s==SLUGS[5] else 15):continue
   for section in ['words','exportWords']:
    for w in p.get(section,[]):
     if norm(w['t'])=='yaz':w['entryKey']='yaz:emir'
 d=data[SLUGS[2]];v=['place; ground','место; земля','жер; орун','مكان؛ أرض','lieu ; sol'];d['words']['yer:mekan']=v
 d['forms']['yer:mekan']={'text':'yer','lemma':'yer','lemmaType':'noun','lemmaTranslations':v,'formTranslations':v,'exampleTr':'Yaşadığım yer çok güzel.','examples':['The place where I live is very beautiful.','Место, где я живу, очень красивое.','Мен жашаган жер абдан кооз.','المكان الذي أعيش فيه جميل جدًا.','L’endroit où je vis est très beau.']}
 for p in pages[SLUGS[2]]:
  if p['page'] in [2,4,24]:
   for w in p['words']:
    if norm(w['t'])=='yer':w['entryKey']='yer:mekan'
 d=data[SLUGS[0]];v=['stay (polite/plural command)','оставайтесь','калыңыздар','ابقوا','restez'];d['words']['kalın:emir']=v
 d['forms']['kalın:emir']={'text':'kalın','lemma':'kalmak','lemmaType':'verb','lemmaTranslations':['to stay','оставаться','калуу','البقاء','rester'],'formTranslations':v,'exampleTr':'Hoşça kalın!','examples':['Goodbye!','До свидания!','Кош болуңуздар!','إلى اللقاء!','Au revoir !']}
 for w in pages[SLUGS[0]][4]['words']:
  if norm(w['t'])=='kalın':w['entryKey']='kalın:emir'
 d['words']['y)dı']=['-(y)DI: Turkish definite past-tense suffix','-(y)DI: турецкий суффикс определённого прошедшего времени','-(y)DI: түрк тилиндеги айкын өткөн чактын мүчөсү','-(y)DI: لاحقة الماضي المحدد في التركية','-(y)DI : suffixe du passé défini en turc']
 # Coin-toss labels are senses of their own, distinct from ordinary writing.
 d=data[SLUGS[4]]
 coin={
  'yazı':['tails (coin: writing side)','решка (сторона монеты с надписью)','тыйындын жазуусу бар жагы','ظهر العملة، الجانب ذو الكتابة','pile (côté de la monnaie portant les inscriptions)'],
  'tura':['heads (coin: portrait side)','орёл (сторона монеты с изображением)','тыйындын сүрөтү бар жагы','وجه العملة، الجانب ذو الصورة','face (côté de la monnaie portant le portrait)']}
 for k,v in coin.items():d['words'][k+':para']=v
 source=json.loads((BASE/SLUGS[4]/'source-text.json').read_text())
 for p in pages[SLUGS[4]]:
  if p['page'] not in [6,17]:continue
  if not p.get('exportWords'):
   tokens=re.split(r'[\s/]+',source[p['page']-1].replace('￾\n','').replace('￾',''))
   p['exportWords']=[{'t':t} for x in tokens if (t:=re.sub(r'^[*=]+|[*=]+$','',x)) and re.search(r'[^\W_]',t)]
  for section in ['words','exportWords']:
   for w in p.get(section,[]):
    if norm(w['t']) in coin:w['entryKey']=norm(w['t'])+':para'
 # In thanks/blessings, sağ means well/alive, rather than the right-hand direction.
 d=data[SLUGS[6]];v=['well; alive (in thanks and blessings)','здоровый; живой (в благодарности и пожеланиях)','соо; аман (ыраазычылык жана каалоо сөздөрүндө)','بصحة وعافية؛ حي، في الشكر والدعاء','en bonne santé ; en vie (dans les remerciements et les souhaits)']
 d['words']['sağ:esen']=v
 d['forms']['sağ:esen']={'text':'sağ','lemma':'sağ','lemmaType':'adjective','lemmaTranslations':v,'formTranslations':v,'exampleTr':'Sağ ol!','examples':['Thank you!','Спасибо!','Рахмат!','شكرًا لك!','Merci !']}
 for p in pages[SLUGS[6]]:
  if p['page'] not in [8,14]:continue
  for section in ['words','exportWords']:
   for w in p.get(section,[]):
    if norm(w['t'])=='sağ':w['entryKey']='sağ:esen'
 for s in SLUGS:
  htmlpath=BASE/s/'index.html';html=htmlpath.read_text()
  # Click and print must resolve exactly the same occurrence-specific dictionary key.
  html=html.replace('const key=phrase?phrase.key:normalize(word);','const key=phrase?phrase.key:(words[index]?.entryKey||normalize(word));')
  html=html.replace("key=normalize(word);","key=(joined?.single?joined.key:null)||w.entryKey||normalize(word);")
  html=html.replace("key=joined?.key||w.entryKey||normalize(word);","key=(joined?.single?joined.key:null)||w.entryKey||normalize(word);")
  if s==SLUGS[0]:html=html.replace("fetch('translations.json')","fetch('translations.json',{cache:'no-store'})")
  if s==SLUGS[1]:
   html=html.replace("20:[['etkin-','likler','etkinlikler'],['yapı-','lıyor?','yapılıyor']],\n        20:[['Sey-','yah','seyyah'],['is-','terdiniz?','isterdiniz']],","20:[['etkin-','likler','etkinlikler'],['yapı-','lıyor?','yapılıyor'],['Sey-','yah','seyyah'],['is-','terdiniz?','isterdiniz']],")
   # Numeric labels and contact identifiers are language-independent, not untranslated words.
   start=html.index('function exportCurrentPageWords(');end=html.index("$('#exportPageWords')",start)
   piece=html[start:end]
   if "if(!meaning&&/^[\\d\\s:.,–—\\-]+$/.test(word))meaning=word;" not in piece:piece=piece.replace("rows.push([word,typeof meaning", "if(!meaning&&/^[\\d\\s:.,–—\\-]+$/.test(word))meaning=word;\n        rows.push([word,typeof meaning")
   line="if(!meaning&&/^[\\d\\s:.,–—\\-]+$/.test(word))meaning=word;"
   piece=piece.replace(line+'\n        '+line,line)
   html=html[:start]+piece+html[end:]
  if s==SLUGS[4]:
   # Strip exercise markup and split slash-separated alternatives, preserving source order.
   html=html.replace("page.exportWords=(source[i]||'').replaceAll('￾\\n','').replaceAll('￾','').split(/\\s+/).filter(t=>/[\\p{L}\\p{N}]/u.test(t)).map(t=>({t}));", "page.exportWords=page.exportWords?.length?page.exportWords:(source[i]||'').replaceAll('￾\\n','').replaceAll('￾','').split(/[\\s/]+/).map(t=>t.replace(/^[*=]+|[*=]+$/g,'')).filter(t=>/[\\p{L}\\p{N}]/u.test(t)).map(t=>({t}));")
  if html!=htmlpath.read_text():htmlpath.write_text(html)
  save(BASE/s/'translations.json',data[s]);save(BASE/s/'pages.json',pages[s])
 print('Repaired shifted five-language arrays:',repaired)
if __name__=='__main__':run()
