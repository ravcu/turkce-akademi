from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
import re,json,hashlib,posixpath,copy
N={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
SLIDENS=N['p'];RNS=N['r'];relsns='http://schemas.openxmlformats.org/package/2006/relationships'
all_slides=[];offset=0
for part in [1,2]:
 source=Path(f'upload/01-A2-2.-nite.{part}.part.pptx');z=ZipFile(source);pres=E.fromstring(z.read('ppt/presentation.xml'));rels=E.fromstring(z.read('ppt/_rels/presentation.xml.rels'));by_id={x.get('Id'):posixpath.normpath('ppt/'+x.get('Target')) for x in rels};ids=pres.find('p:sldIdLst',N);kept=[];changes={'clean':{},'full':{}}
 for local,ref in enumerate(list(ids),1):
  path=by_id[ref.get('{'+RNS+'}id')];r=E.fromstring(z.read(path));text=' '.join(r.xpath('//a:t/text()',namespaces=N))
  if 'Kelime Listesi' in text:
   ids.remove(ref);continue
  sequence=len(all_slides)+1;rec={'sequence':sequence,'sourceSlide':offset+local,'part':part,'localSlide':local,'removedAnswerShapes':[],'removedMediaIcons':0,'removedEnglishTables':0,'pictures':[]}
  # These picture bytes are never decoded, retouched, or replaced in the deck.
  relpath=posixpath.dirname(path)+'/_rels/'+posixpath.basename(path)+'.rels';sr=E.fromstring(z.read(relpath));srels={x.get('Id'):x for x in sr}
  for pic in r.xpath('//p:pic',namespaces=N):
   if pic.xpath('.//*[local-name()="media" or local-name()="audioFile" or local-name()="videoFile"]'):
    pic.getparent().remove(pic);rec['removedMediaIcons']+=1;continue
   for rid in pic.xpath('.//a:blip/@r:embed',namespaces=N):
    target=posixpath.normpath(posixpath.dirname(path)+'/'+srels[rid].get('Target'));rec['pictures'].append({'part':target,'sha256':hashlib.sha256(z.read(target)).hexdigest()})
  for frame in r.xpath('//p:graphicFrame',namespaces=N):
   ft=' '.join(frame.xpath('.//a:t/text()',namespaces=N))
   if frame.xpath('.//a:tbl',namespaces=N) and any(t in ft for t in ['İngilizce','May your holiday','May hearts','May  hearts']):frame.getparent().remove(frame);rec['removedEnglishTables']+=1
  # Animations are presentation controls, not part of the static background.
  for tag in ['timing','transition']:
   node=r.find('p:'+tag,N)
   if node is not None:r.remove(node)
  full=E.tostring(r,xml_declaration=True,encoding='UTF-8',standalone=True);changes['full'][path]=full
  for sp in r.xpath('//p:sp | //p:cxnSp',namespaces=N):
   if sp.xpath('.//a:srgbClr[translate(@val,"abcdef","ABCDEF")="FF0000"]',namespaces=N):
    rec['removedAnswerShapes'].append({'id':sp.xpath('.//p:cNvPr/@id',namespaces=N),'text':' '.join(sp.xpath('.//a:t/text()',namespaces=N)),'xml':E.tostring(sp).decode()});sp.getparent().remove(sp)
  changes['clean'][path]=E.tostring(r,xml_declaration=True,encoding='UTF-8',standalone=True)
  rec['hasAnswers']=bool(rec['removedAnswerShapes']);all_slides.append(rec);kept.append(path)
 # Keep precisely the same source slide sequence in clean and answer decks.
 presxml=E.tostring(pres,xml_declaration=True,encoding='UTF-8',standalone=True)
 for variant in ['full','clean']:
  out=Path(f'rebuild/part{part}-{variant}.pptx')
  with ZipFile(out,'w',ZIP_DEFLATED,compresslevel=1) as zz:
   for item in z.infolist():zz.writestr(copy.copy(item),changes[variant].get(item.filename,presxml if item.filename=='ppt/presentation.xml' else z.read(item.filename)))
  with ZipFile(out) as zz:
   for name in z.namelist():
    if name.startswith('ppt/media/'):assert zz.read(name)==z.read(name),name
 print(part,'kept',len(kept),'answers',sum(x['hasAnswers'] for x in all_slides if x['part']==part),flush=True)
 offset+=len(E.fromstring(z.read('ppt/presentation.xml')).find('p:sldIdLst',N))
Path('rebuild/source-objects.json').write_text(json.dumps(all_slides,ensure_ascii=False,indent=2))
old=json.loads(Path('staging/slides.json').read_text())['slides'];assert [s['sourceSlide'] for s in all_slides]==[s['sourceSlide'] for s in old]
print('SOURCE MAPPING MATCHES',len(all_slides),flush=True)
