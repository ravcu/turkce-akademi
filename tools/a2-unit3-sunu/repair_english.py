"""Remove added English raster tables and render the exposed Turkish originals."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from lxml import etree as E
import posixpath
ROOT=Path(__file__).resolve().parents[2];W=ROOT.parent/'rebuild'
N={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
for variant in ['clean','full']:
 with ZipFile(W/f'part1-{variant}.pptx') as z,ZipFile(W/f'repair-{variant}.pptx','w',ZIP_DEFLATED,compresslevel=1) as out:
  pres=E.fromstring(z.read('ppt/presentation.xml'));ids=pres.find('p:sldIdLst',N);rels={e.get('Id'):posixpath.normpath('ppt/'+e.get('Target')) for e in E.fromstring(z.read('ppt/_rels/presentation.xml.rels'))};kept=[];changes={}
  for ref in list(ids):
   name=rels[ref.get('{'+N['r']+'}id')]
   if name not in ['ppt/slides/slide1.xml','ppt/slides/slide37.xml','ppt/slides/slide68.xml','ppt/slides/slide69.xml']:ids.remove(ref);continue
   kept.append(name);r=E.fromstring(z.read(name));rp=posixpath.dirname(name)+'/_rels/'+posixpath.basename(name)+'.rels';rr={e.get('Id'):e.get('Target') for e in E.fromstring(z.read(rp))}
   for pic in r.xpath('//p:pic',namespaces=N):
    targets=[rr.get(x,'') for x in pic.xpath('.//a:blip/@r:embed',namespaces=N)]
    if any(x.endswith(('image36.png','image60.png')) for x in targets):pic.getparent().remove(pic)
   if name.endswith('slide1.xml'):
    for t in r.xpath('//a:t',namespaces=N):t.text=(t.text or '').replace('2.ÜNİTE','3.ÜNİTE')
   changes[name]=E.tostring(r)
  for f in z.namelist():out.writestr(f, E.tostring(pres) if f=='ppt/presentation.xml' else changes.get(f,z.read(f)))
  print(variant,kept)
