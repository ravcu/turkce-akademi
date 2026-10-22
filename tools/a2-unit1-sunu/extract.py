from pathlib import Path
import os
from lxml import etree as E
import zipfile,json,re,posixpath,hashlib,io,subprocess
R=Path(os.environ.get("A2_SUNU_WORK",Path(__file__).resolve().parents[3]/"a2-source"));ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships','p14':'http://schemas.microsoft.com/office/powerpoint/2010/main'};rs=[]
for part in [1,2]:
 z=zipfile.ZipFile(R.parent/'upload'/f'A2 1.ünite.{part}.part.pptx');changes={'clean':{},'full':{}}
 for n in z.namelist():
  if not re.fullmatch(r'ppt/slides/slide\d+.xml',n):continue
  num=int(re.search(r'slide(\d+)',n)[1]);t=E.fromstring(z.read(n));text=' '.join(t.xpath('//a:t/text()',namespaces=ns));norm=re.sub(r'\s+','',text).lower().replace('i\u0307','i');exclude=any(x in norm for x in ['türkçe–ingilizce','türkçe-ingilizce','önemligrameryapıları','tatilhakkındaörneksorular']) or text.startswith(('A  Day','Three  Cultural','40 Our third'))
  rels={x.get('Id'):x.get('Target') for x in E.fromstring(z.read(f'ppt/slides/_rels/slide{num}.xml.rels'))};audio=[]
  for sh in list(t.xpath('//p:spTree/*',namespaces=ns)):
   ms=sh.xpath('.//p14:media',namespaces=ns)
   if ms:
    m=ms[0];tar=rels.get(m.get('{'+ns['r']+'}embed'))
    if tar and tar!='NULL':
     tar=posixpath.normpath(posixpath.join('ppt/slides',tar));raw=z.read(tar);dest=R/'media'/(hashlib.sha256(raw).hexdigest()[:16]+Path(tar).suffix);dest.parent.mkdir(exist_ok=True)
     if not dest.exists():dest.write_bytes(raw)
     trim=m.find('p14:trim',ns);audio.append({'file':str(dest),'start':float(trim.get('st','0'))/1000 if trim is not None else 0,'trimEnd':float(trim.get('end','0'))/1000 if trim is not None else 0})
    sh.getparent().remove(sh)
   elif part==2 and num==79 and sh.xpath('string(.//p:cNvPr/@id)',namespaces=ns)=='2':sh.getparent().remove(sh)
  changes['full'][n]=E.tostring(t,xml_declaration=True,encoding='UTF-8',standalone=True);answer=[]
  for sh in list(t.xpath('//p:spTree/*',namespaces=ns)):
   cols=sh.xpath('.//a:srgbClr/@val',namespaces=ns);red=any(len(c)==6 and int(c[:2],16)>170 and int(c[2:4],16)<110 and int(c[4:],16)<110 for c in cols)
   svg=any(rels.get(v,'').endswith('image21.svg') for v in sh.xpath('.//@r:embed',namespaces=ns))
   accent='accent2' in sh.xpath('.//a:schemeClr/@val',namespaces=ns)
   if red or svg or accent or (part==2 and num==16 and E.QName(sh).localname=='cxnSp'):answer.append(sh.xpath('string(.//p:cNvPr/@id)',namespaces=ns));sh.getparent().remove(sh)
  changes['clean'][n]=E.tostring(t,xml_declaration=True,encoding='UTF-8',standalone=True);rs.append({'part':part,'slide':num,'excluded':exclude,'text':text,'audio':audio,'answerShapes':answer})
 for mode,patches in changes.items():
  with zipfile.ZipFile(R/f'part{part}-{mode}.pptx','w',zipfile.ZIP_DEFLATED,compresslevel=1) as out:
   for n in z.namelist():out.writestr(n,patches.get(n,z.read(n)))
rs.sort(key=lambda r:(r['part'],r['slide']));seq=0
for r in rs:
 if not r['excluded']:seq+=1;r['sequence']=seq
(R/'inventory.json').write_text(json.dumps(rs,ensure_ascii=False,indent=2));print('kept',seq,flush=True)
