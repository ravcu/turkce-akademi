"""Separate red SVG checkmarks from the source slides for answer toggling."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
import json,posixpath
R=Path(__file__).resolve().parents[2];W=R.parent/'rebuild';N={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'};audit=[]
for part in [1,2]:
 with ZipFile(W/f'part{part}-clean.pptx') as z,ZipFile(W/f'checks{part}.pptx','w',ZIP_DEFLATED,compresslevel=1) as out:
  pres=E.fromstring(z.read('ppt/presentation.xml'));ids=pres.find('p:sldIdLst',N);rr={e.get('Id'):posixpath.normpath('ppt/'+e.get('Target')) for e in E.fromstring(z.read('ppt/_rels/presentation.xml.rels'))};patch={};index=0
  for ref in list(ids):
   name=rr[ref.get('{'+N['r']+'}id')];r=E.fromstring(z.read(name));rp=posixpath.dirname(name)+'/_rels/'+posixpath.basename(name)+'.rels';rels={e.get('Id'):e.get('Target') for e in E.fromstring(z.read(rp))};removed=[]
   for pic in r.xpath('//p:pic',namespaces=N):
    if any(rels.get(x,'').endswith('image55.svg') for x in pic.xpath('.//@r:embed',namespaces=N)):removed.append(E.tostring(pic).decode());pic.getparent().remove(pic)
   if not removed:ids.remove(ref);continue
   local=int(name.rsplit('slide',1)[1].split('.')[0]);audit.append({'part':part,'localSlide':local,'repairPage':index,'count':len(removed)});index+=1;patch[name]=E.tostring(r)
  for name in z.namelist():out.writestr(name,E.tostring(pres) if name=='ppt/presentation.xml' else patch.get(name,z.read(name)))
(W/'checkmark-audit.json').write_text(json.dumps(audit));print(audit,flush=True)
