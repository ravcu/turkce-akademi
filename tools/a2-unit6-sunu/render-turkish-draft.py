"""Render native slides at 2400px and extract clickable text and trimmed audio."""
from pathlib import Path
import json,io,subprocess,csv,re,unicodedata,concurrent.futures
import fitz
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[2];W=ROOT.parent/'fresh-turkish';O=ROOT/'kitaplar/lise-a2/hayat-birlikte-guzel/sunum-draft2';A=O/'assets'
for n in ['slides','answers','audio']:(A/n).mkdir(parents=True,exist_ok=True)
records=json.loads((W/'source-objects.json').read_text());counts={1:0,2:0,3:0}
for r in records:r['pdfPage']=counts[r['part']];counts[r['part']]+=1
D=json.loads((O.parent/'translations.json').read_text());keys=set(D['words'])|set(D['forms'])|set(D['phrases'])
def norm(t):return re.sub(r'^[^\wÇĞİÖŞÜçğıöşü]+|[^\wÇĞİÖŞÜçğıöşü]+$','',unicodedata.normalize('NFC',t).replace('İ','i').replace('I','ı').lower().replace('’',"'"))
def work(r):
 seq=r['sequence'];cache=W/f'rendered-{seq:03}.json'
 if cache.exists():
  saved=json.loads(cache.read_text())
  if saved[0]['sourcePart']==r['part'] and saved[0]['sourcePartSlide']==r['localSlide']:return saved
 images=[]
 for mode in ['clean','full']:
  with fitz.open(W/f'pdf2/part{r["part"]}-{mode}.pdf') as d:
   p=d[r['pdfPage']];pix=p.get_pixmap(matrix=fitz.Matrix(2400/p.rect.width,2400/p.rect.width),alpha=False);images.append(Image.frombytes('RGB',(pix.width,pix.height),pix.samples))
 clean,full=images;
 destination=A/'slides'/f'{seq:03}.webp'
 if not destination.exists() or not destination.stat().st_size:clean.save(destination,lossless=True,method=4)
 diff=ImageChops.difference(clean,full).convert('L').point(lambda v:255 if v>12 else 0);has=bool(diff.getbbox())
 if has and not (A/'answers'/f'{seq:03}.webp').exists():full.save(A/'answers'/f'{seq:03}.webp',lossless=True,method=4)
 png=W/f'ocr-{seq:03}.png';full.save(png)
 raw=subprocess.check_output(['tesseract',str(png),'stdout','--tessdata-dir','/tmp','-l','tur','--psm','11','-c','tessedit_create_tsv=1'],stderr=subprocess.DEVNULL,env={**__import__('os').environ,'OMP_THREAD_LIMIT':'1'}).decode();png.unlink()
 spots=[]
 for w in csv.DictReader(io.StringIO(raw),delimiter='\t',quoting=csv.QUOTE_NONE):
  t=(w.get('text') or '').strip()
  if not t or not re.search('[A-Za-zÇĞİÖŞÜçğıöşü0-9]',t):continue
  x,y,ww,hh=[int(w[k]) for k in ['left','top','width','height']];k=norm(t)
  if not k:continue
  crop=diff.crop((x,y,x+ww,y+hh));answer=has and sum(crop.getdata())/(255*max(ww*hh,1))>.08
  spots.append({'text':t,'key':k,'confidence':float(w['conf']),'x':x/2400,'y':y/1350,'w':ww/2400,'h':hh/1350,**({'answer':True} if answer else {})})
 s={'sequence':seq,'sourceSlide':r['sourceSlide'],'sourcePart':r['part'],'sourcePartSlide':r['localSlide'],'image':f'assets/slides/{seq:03}.webp','imageWidth':2400,'imageHeight':1350}
 if has:s['answerImage']=f'assets/answers/{seq:03}.webp'
 for i,a in enumerate(r['audio'],1):
  path=f'assets/audio/{seq:03}-{i}.mp3';subprocess.run(['ffmpeg','-v','error','-y','-ss',str(a['start']),'-i',a['file'],'-t',str(a['end']-a['start']),'-vn','-c:a','libmp3lame','-b:a','128k',str(O/path)],check=True)
  duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(O/path)]));assert abs(duration-(a['end']-a['start']))<.12
  s.setdefault('audio',[]).append(path);s.setdefault('audioSegments',[]).append({'src':path,'sourceStart':a['start'],'sourceEnd':a['end'],'sourceMediaSha256':a['sha256'],'publishedDuration':duration})
 cache.write_text(json.dumps([s,spots],ensure_ascii=False));return s,spots
if __name__=='__main__':
 rows=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
  for i,row in enumerate(ex.map(work,records),1):
   rows.append(row)
   if i%10==0:print('Rendered',i,'/',len(records),flush=True)
 (A/'slides.json').write_text(json.dumps({'slides':[r[0] for r in rows]},ensure_ascii=False,indent=2));(A/'word-spots.json').write_text(json.dumps([r[1] for r in rows],ensure_ascii=False));(A/'answer-overlays.json').write_text('{}');(A/'translations.json').write_text(json.dumps(D,ensure_ascii=False))
 missing={w['key'] for _,ss in rows for w in ss if w['key'] not in keys and re.search('[a-zçğıöşü]',w['key'])};(W/'missing-words.json').write_text(json.dumps(sorted(missing),ensure_ascii=False,indent=2));print('DONE missing',len(missing),flush=True)

