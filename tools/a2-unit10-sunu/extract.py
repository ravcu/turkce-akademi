"""Separate added answer objects and retain original picture bytes from the source PPTX."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
import json,posixpath,hashlib,subprocess,copy
ROOT=Path(__file__).resolve().parents[2];W=ROOT.parent/'work10';W.mkdir(exist_ok=True)
OUT=ROOT/'kitaplar/lise-a2/geziyorum/sunum';OUT.mkdir(parents=True,exist_ok=True)
import sys
PART=int(sys.argv[1]);GLOBAL_OFFSET=[0,34,70][PART-1]
W=W/f'part{PART}';W.mkdir(exist_ok=True)
SOURCE=sorted((ROOT.parent/'upload').glob(f'*10*{PART}.part*.pptx'))[0]
N={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def red(sh):return any(len(c)==6 and int(c[:2],16)>170 and int(c[2:4],16)<100 and int(c[4:],16)<100 for c in sh.xpath('.//a:srgbClr/@val',namespaces=N))
z=ZipFile(SOURCE);pres=E.fromstring(z.read('ppt/presentation.xml'));dims=[int(pres.find('p:sldSz',N).get(k)) for k in ['cx','cy']]
rels={e.get('Id'):posixpath.normpath('ppt/'+e.get('Target')) for e in E.fromstring(z.read('ppt/_rels/presentation.xml.rels'))};ids=pres.find('p:sldIdLst',N)
records=[];excluded=[];changes={'clean':{},'full':{}};media_cache={}
for source_index,ref in enumerate(list(ids),1):
 path=rels[ref.get('{'+N['r']+'}id')];r=E.fromstring(z.read(path));text=' '.join(r.xpath('//a:t/text()',namespaces=N))
 if 'Kelime Listesi' in text or ('Türkçe kelime / ifade' in text and 'İngilizce anlamı' in text):
  ids.remove(ref);excluded.append({'slide':source_index,'reason':'vocabulary-list','text':text});continue
 rec={'sequence':len(records)+1,'sourceSlide':source_index+GLOBAL_OFFSET,'sourcePart':PART,'partSlide':source_index,'slidePath':path,'dimensions':dims,'audio':[],'answerShapes':[],'removedEnglish':[],'pictures':[],'text':text}
 rp=posixpath.dirname(path)+'/_rels/'+posixpath.basename(path)+'.rels';sr={e.get('Id'):e.get('Target') for e in E.fromstring(z.read(rp))}
 tree=r.find('p:cSld',N).find('p:spTree',N)
 for sh in list(tree):
  media=sh.xpath('.//*[local-name()="media"]')
  if media:
   for m in media:
    target=sr.get(m.get('{'+N['r']+'}embed'));target=posixpath.normpath(posixpath.dirname(path)+'/'+target)
    if target not in media_cache:
     data=z.read(target);sha=hashlib.sha256(data).hexdigest();f=W/'source-audio'/Path(target).name;f.parent.mkdir(exist_ok=True);f.write_bytes(data)
     dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(f)]));media_cache[target]={'file':str(f),'sha256':sha,'sourceDuration':dur}
    a=dict(media_cache[target]);trim=m.xpath('./*[local-name()="trim"]');attrs=dict(trim[0].attrib) if trim else {};start=float(attrs.get('st',0))/1000;end=a['sourceDuration']-float(attrs.get('end',0))/1000
    assert 0<=start<end<=a['sourceDuration']+.001,(source_index,start,end)
    a.update(sourceMedia=target,start=start,end=end,trim=attrs);rec['audio'].append(a)
   tree.remove(sh);continue
  txt=' '.join(sh.xpath('.//a:t/text()',namespaces=N))
  if sh.xpath('.//a:tbl',namespaces=N) and any(k in txt for k in ['English','İngilizce','İNGİLİZCE']):
   rec['removedEnglish'].append({'id':sh.xpath('.//p:cNvPr/@id',namespaces=N),'text':txt});tree.remove(sh);continue
  if txt.strip().casefold() in ['english','i̇ngilizce','ingilizce','çeviri','translation']:
   rec['removedEnglish'].append({'text':txt});tree.remove(sh);continue
  if PART==1 and source_index==1:
   for t in sh.xpath('.//a:t',namespaces=N):
    if '6. ÜNİTE' in (t.text or ''):t.text=t.text.replace('6. ÜNİTE','10. ÜNİTE')
  if sh.tag=='{'+N['p']+'}pic':
   for rid in sh.xpath('.//a:blip/@r:embed',namespaces=N):
    target=posixpath.normpath(posixpath.dirname(path)+'/'+sr[rid]);rec['pictures'].append({'part':target,'sha256':hashlib.sha256(z.read(target)).hexdigest()})
 for tag in ['timing','transition']:
  q=r.find('p:'+tag,N)
  if q is not None:r.remove(q)
 changes['full'][path]=E.tostring(r,xml_declaration=True,encoding='UTF-8',standalone=True)
 # Original book headings/shapes are inside the untouched raster pictures.
 # Only separate red vector/text objects authored over those pictures are answers.
 for sh in list(tree):
  if sh.tag in ['{'+N['p']+'}sp','{'+N['p']+'}cxnSp','{'+N['p']+'}grpSp'] and red(sh):
   rec['answerShapes'].append({'id':sh.xpath('.//p:cNvPr/@id',namespaces=N),'text':' '.join(sh.xpath('.//a:t/text()',namespaces=N)),'xml':E.tostring(sh).decode()});tree.remove(sh)
 changes['clean'][path]=E.tostring(r,xml_declaration=True,encoding='UTF-8',standalone=True);records.append(rec)
presxml=E.tostring(pres,xml_declaration=True,encoding='UTF-8',standalone=True)
for variant in ['clean','full']:
 with ZipFile(W/f'{variant}.pptx','w',ZIP_DEFLATED,compresslevel=1) as dest:
  for item in z.infolist():
   if item.filename.endswith(('.wav','.mp3','.wma','.m4a','.mp4')):continue
   dest.writestr(copy.copy(item),changes[variant].get(item.filename,presxml if item.filename=='ppt/presentation.xml' else z.read(item.filename)))
 print('Prepared',variant,flush=True)
dump(W/'source-objects.json',records);dump(W/'excluded.json',excluded)
checks=0
for variant in ['clean','full']:
 with ZipFile(W/f'{variant}.pptx') as check:
  for record in records:
   for pic in record['pictures']:
    assert hashlib.sha256(check.read(pic['part'])).hexdigest()==pic['sha256'];checks+=1
dump(W/'source-audit.json',{'sourceSha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'sourceSlides':len(ids)+len(excluded),'keptSlides':len(records),'excluded':excluded,'slides':records,'originalPicturesPreserved':True,'pictureHashChecks':checks,'removedEnglishTables':sum(len(r['removedEnglish']) for r in records),'addedAnswerObjects':sum(len(r['answerShapes']) for r in records)})
print({'slides':len(records),'answerObjects':sum(len(r['answerShapes']) for r in records),'englishTables':sum(len(r['removedEnglish']) for r in records),'audioUses':sum(len(r['audio']) for r in records),'uniqueAudio':len(media_cache)})
