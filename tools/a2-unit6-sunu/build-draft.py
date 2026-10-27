"""Build A2 unit 3 from original PPTX files, preserving source artwork."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
import json,re,posixpath,hashlib,subprocess,copy
ROOT=Path(__file__).resolve().parents[2];WORK=ROOT.parent/'rebuild';WORK.mkdir(exist_ok=True)
OUT=ROOT/'kitaplar/lise-a2/hayat-birlikte-guzel/sunum';OUT.mkdir(parents=True,exist_ok=True)
N={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2))
def red(el):
 for c in el.xpath('.//a:srgbClr/@val',namespaces=N):
  if len(c)==6 and int(c[:2],16)>170 and int(c[2:4],16)<110 and int(c[4:],16)<110:return True
 return False
records=[];excluded=[];vocabulary=[];offset=0
for part in [1,2,3]:
 source=sorted((ROOT.parent/'upload').glob('*.pptx'))[part-1];z=ZipFile(source)
 pres=E.fromstring(z.read('ppt/presentation.xml'));sz=pres.find('p:sldSz',N);dims=[int(sz.get(k)) for k in ['cx','cy']]
 rels={e.get('Id'):posixpath.normpath('ppt/'+e.get('Target')) for e in E.fromstring(z.read('ppt/_rels/presentation.xml.rels'))};ids=pres.find('p:sldIdLst',N);count=len(ids);changes={'clean':{},'full':{}}
 for local,ref in enumerate(list(ids),1):
  path=rels[ref.get('{'+N['r']+'}id')];r=E.fromstring(z.read(path));text=' '.join(r.xpath('//a:t/text()',namespaces=N))
  if 'Kelime Listesi' in text or ('Türkçe kelime / ifade' in text and 'İngilizce anlamı' in text):
   excluded.append({'part':part,'slide':local,'reason':'vocabulary-list'});vocabulary.append({'part':part,'slide':local,'text':text});ids.remove(ref);continue
  # Extra English-only teaching tables are omitted; Turkish grammar tables remain.
  if False:
   excluded.append({'part':part,'slide':local,'reason':'English-translation-table'});ids.remove(ref);continue
  rec={'sequence':len(records)+1,'part':part,'localSlide':local,'sourceSlide':offset+local,'slidePath':path,'dimensions':dims,'text':text,'audio':[],'answerShapes':[],'removedEnglish':[],'pictures':[]}
  rp=posixpath.dirname(path)+'/_rels/'+posixpath.basename(path)+'.rels';sr={e.get('Id'):e.get('Target') for e in E.fromstring(z.read(rp))} if rp in z.namelist() else {}
  for sh in list(r.xpath('//p:spTree/*',namespaces=N)):
   media=sh.xpath('.//*[local-name()="media"]')
   if media:
    for m in media:
     rid=m.get('{'+N['r']+'}embed');target=sr.get(rid)
     if not target:continue
     target=posixpath.normpath(posixpath.dirname(path)+'/'+target);data=z.read(target);sha=hashlib.sha256(data).hexdigest();f=WORK/'source-audio'/(sha[:16]+Path(target).suffix);f.parent.mkdir(exist_ok=True);f.write_bytes(data)
     dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(f)]));trim=m.xpath('./*[local-name()="trim"]');attrs=trim[0].attrib if trim else {};start=float(attrs.get('st',0))/1000;end=dur-float(attrs.get('end',0))/1000
     assert end>start,(part,local,start,end)
     rec['audio'].append({'file':str(f),'sha256':sha,'sourceMedia':target,'sourceDuration':dur,'start':start,'end':end,'trim':dict(attrs)})
    sh.getparent().remove(sh);continue
   st=' '.join(sh.xpath('.//a:t/text()',namespaces=N))
   if ('İNGİLİZCE' in st or 'İngilizce' in st) and sh.xpath('.//a:tbl',namespaces=N):
    rec['removedEnglish'].append(st);sh.getparent().remove(sh);continue
   if st.strip().lower() in ['english','i̇ngilizce','ingilizce','çeviri','translation']:
    rec['removedEnglish'].append(st);sh.getparent().remove(sh);continue
   if False:
    rec['removedEnglish'].append('English raster translation table');sh.getparent().remove(sh);continue
   if sh.tag=='{'+N['p']+'}pic':
    for rid in sh.xpath('.//a:blip/@r:embed',namespaces=N):
     target=posixpath.normpath(posixpath.dirname(path)+'/'+sr[rid]);rec['pictures'].append({'part':target,'sha256':hashlib.sha256(z.read(target)).hexdigest()})
  for tag in ['timing','transition']:
   q=r.find('p:'+tag,N)
   if q is not None:r.remove(q)
  changes['full'][path]=E.tostring(r,xml_declaration=True,encoding='UTF-8',standalone=True)
  for sh in list(r.xpath('//p:sp | //p:cxnSp | //p:pic',namespaces=N)):
   if red(sh) :
    rec['answerShapes'].append({'text':' '.join(sh.xpath('.//a:t/text()',namespaces=N)),'xml':E.tostring(sh).decode()});sh.getparent().remove(sh)
  changes['clean'][path]=E.tostring(r,xml_declaration=True,encoding='UTF-8',standalone=True);records.append(rec)
 presxml=E.tostring(pres,xml_declaration=True,encoding='UTF-8',standalone=True)
 for variant in ['clean','full']:
  with ZipFile(WORK/f'part{part}-{variant}.pptx','w',ZIP_DEFLATED,compresslevel=1) as zz:
   for item in z.infolist():zz.writestr(copy.copy(item),changes[variant].get(item.filename,presxml if item.filename=='ppt/presentation.xml' else z.read(item.filename)))
 offset+=count
 print('PART',part,'kept',sum(x['part']==part for x in records),flush=True)
dump(WORK/'source-objects.json',records);dump(WORK/'vocabulary-source.json',vocabulary)
dump(OUT/'source-audit.json',{'sourceSlides':offset,'keptSlides':len(records),'excluded':excluded,'slides':records})
print('TOTAL',len(records),'excluded',len(excluded),'audio occurrences',sum(len(x['audio']) for x in records),flush=True)

