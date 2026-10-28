"""Render untouched native artwork and only separately added answer objects."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import json,subprocess,os,io,hashlib,csv
import fitz
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[2];W=ROOT.parent/'work9';O=ROOT/'kitaplar/lise-a2/bir-hikayem-var/sunum'
RECORDS=json.loads((W/'source-objects.json').read_text())
for d in ['slides','answers']:(O/d).mkdir(exist_ok=True)
(W/'ocr').mkdir(exist_ok=True)
def process(r):
 seq=r['sequence'];cache=W/f'rendered-{seq:03}.json'
 if cache.exists():return json.loads(cache.read_text())
 images=[];vector=[]
 for mode in ['clean','full']:
  with fitz.open(W/'pdf'/f'{mode}.pdf') as d:
   p=d[seq-1];pix=p.get_pixmap(matrix=fitz.Matrix(2400/p.rect.width,2400/p.rect.width),alpha=False);images.append(Image.frombytes('RGB',(pix.width,pix.height),pix.samples))
   if mode=='full':
    for x0,y0,x1,y1,text,*_ in p.get_text('words'):vector.append({'text':text,'x':100*x0/p.rect.width,'y':100*y0/p.rect.height,'w':100*(x1-x0)/p.rect.width,'h':100*(y1-y0)/p.rect.height})
 clean,full=images;diff=ImageChops.difference(clean,full).convert('L').point(lambda v:255 if v>12 else 0);bbox=diff.getbbox()
 assert bool(bbox)==bool(r['answerShapes']),(seq,'unexplained visual difference',bbox,len(r['answerShapes']))
 image=f'slides/{seq:03}.webp';buffer=io.BytesIO();clean.save(buffer,format='WEBP',lossless=True,method=3);assert len(buffer.getvalue())>100;(O/image).write_bytes(buffer.getvalue())
 answers=None
 if bbox:
  answers=f'answers/{seq:03}.webp'
  rr,gg,bb=ImageChops.difference(clean,full).split();mask=ImageChops.lighter(ImageChops.lighter(rr,gg),bb).point(lambda v:255 if v else 0)
  overlay=full.convert('RGBA');overlay.putalpha(mask)
  assert ImageChops.difference(Image.alpha_composite(clean.convert('RGBA'),overlay).convert('RGB'),full).getbbox() is None
  buffer=io.BytesIO();overlay.save(buffer,format='WEBP',lossless=True,method=4);assert len(buffer.getvalue())>100;(O/answers).write_bytes(buffer.getvalue())
 allwords=[]
 for mode,im,psm in [('native',full,3),('threshold',full.convert('L').point(lambda v:255 if v>150 else 0),11)]:
  png=W/'ocr'/f'{seq:03}-{mode}.png';im.save(png)
  raw=subprocess.check_output(['tesseract',str(png),'stdout','--tessdata-dir',str(W/'tessdata'),'-l','tur','--psm',str(psm),'-c','tessedit_create_tsv=1'],env={**os.environ,'OMP_THREAD_LIMIT':'1'},stderr=subprocess.DEVNULL).decode()
  (W/'ocr'/f'{seq:03}-{mode}.tsv').write_text(raw);png.unlink()
  for row in csv.DictReader(io.StringIO(raw),delimiter='\t',quoting=csv.QUOTE_NONE):
   if row.get('level')!='5' or not row.get('text','').strip():continue
   x,y,w,h=[int(row[k]) for k in ['left','top','width','height']]
   crop=diff.crop((x,y,x+w,y+h));is_answer=bool(bbox) and sum(crop.get_flattened_data())/(255*max(w*h,1))>.08
   allwords.append({'text':row['text'],'x':100*x/full.width,'y':100*y/full.height,'w':100*w/full.width,'h':100*h/full.height,'confidence':float(row['conf']),'mode':mode,**({'answer':True} if is_answer else {})})
 for v in vector:
  x,y,w,h=[int(v[k]* (full.width if k in ['x','w'] else full.height)/100) for k in ['x','y','w','h']];crop=diff.crop((x,y,x+w,y+h));v.update(confidence=100,mode='vector')
  if bbox and sum(crop.get_flattened_data())/(255*max(w*h,1))>.08:v['answer']=True
  allwords.append(v)
 s={'image':image,'answers':answers,'audio':[a['published']['src'] for a in r['audio']],'audioSegments':[a['published'] for a in r['audio']],'source_slide':r['sourceSlide'],'part':r['sourcePart'],'words':[],'label':next((t for t in r['text'].splitlines() if False),'')}
 data={'slide':s,'words':allwords,'answerDifference':{'bbox':bbox,'pixels':sum(1 for v in diff.get_flattened_data() if v)},'sourceSlide':r['sourceSlide']};cache.write_text(json.dumps(data,ensure_ascii=False));return data
if __name__=='__main__':
 with ProcessPoolExecutor(max_workers=3) as pool:
  result=[]
  for i,row in enumerate(pool.map(process,RECORDS),1):
   result.append(row)
   if i%10==0:print('Rendered and scanned',i,'/',len(RECORDS),flush=True)
 (W/'rendered.json').write_text(json.dumps(result,ensure_ascii=False));print('Ready',len(result),flush=True)
