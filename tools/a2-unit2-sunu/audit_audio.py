from zipfile import ZipFile
from pathlib import Path
from lxml import etree as E
import json,hashlib,posixpath,subprocess
N={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
recs=json.loads(Path('rebuild/source-objects.json').read_text());zips={i:ZipFile(f'upload/01-A2-2.-nite.{i}.part.pptx') for i in [1,2]};rows=[];media={};out=Path('rebuild/source-audio');out.mkdir(exist_ok=True)
for s in recs:
 z=zips[s['part']];i=s['localSlide'];r=E.fromstring(z.read(f'ppt/slides/slide{i}.xml'));rels=E.fromstring(z.read(f'ppt/slides/_rels/slide{i}.xml.rels'));byid={x.get('Id'):x for x in rels}
 for pic in r.xpath('//p:pic',namespaces=N):
  ids=pic.xpath('.//*[local-name()="media"]/@r:embed',namespaces=N)
  for rid in ids:
   target=posixpath.normpath('ppt/slides/'+byid[rid].get('Target'));data=z.read(target);sha=hashlib.sha256(data).hexdigest();ext=Path(target).suffix;f=out/(sha[:16]+ext)
   if not f.exists():f.write_bytes(data)
   if sha not in media:media[sha]=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(f)]))
   trim=pic.xpath('.//*[local-name()="trim"]')
   trim=trim[0].attrib if trim else {}
   trim_start=float(trim.get('st','0'))/1000;trim_end=float(trim.get('end','0'))/1000
   spid=pic.xpath('.//p:cNvPr/@id',namespaces=N)[0];dur=[]
   for cmd in r.xpath('//p:cmd',namespaces=N):
    if cmd.xpath('.//p:spTgt[@spid="'+spid+'"]',namespaces=N):dur+=cmd.xpath('.//p:cTn/@dur',namespaces=N)
   numeric=[float(x)/1000 for x in dur if x.isdigit()]
   rows.append({'sourceSlide':s['sourceSlide'],'sequence':s['sequence'],'part':s['part'],'sourceMedia':target,'sha':sha,'localSource':str(f),'sourceDuration':media[sha],'animationDuration':max(numeric,default=media[sha]-trim_start-trim_end),'ext':ext,'trimStart':trim_start,'trimEnd':trim_end})
for row in rows:
 row['start']=round(row['trimStart'],6);row['end']=round(row['sourceDuration']-row['trimEnd'],6)
 row['durationDifferenceFromAnimation']=round(row['end']-row['start']-row['animationDuration'],6)
 assert row['end']>row['start'],row
 assert abs(row['durationDifferenceFromAnimation'])<.25,row
old=json.loads(Path('repo/kitaplar/lise-a2/hafta-sonu-planin-ne/sunum/slides.json').read_text())['slides'];mismatches=[]
for row in rows:
 prev=old[row['sequence']-1].get('audioSegments',[])
 if not any(abs(x.get('sourceStart',x.get('start',0))-row['start'])<.06 and abs(x.get('sourceEnd',x.get('end',0))-row['end'])<.15 for x in prev):mismatches.append(row)
Path('rebuild/audio-source-audit.json').write_text(json.dumps({'rows':rows,'mismatchesWithPriorCuts':mismatches},ensure_ascii=False,indent=2))
print('Media occurrences',len(rows),'unique',len(media),'mismatches',len(mismatches));print([(r['sequence'],round(r['start'],3),round(r['end'],3)) for r in rows])
