import json,fitz,os
from pathlib import Path
from PIL import Image
from concurrent.futures import ProcessPoolExecutor
root=Path('repo/kitaplar/lise-a2/hafta-sonu-planin-ne/sunum');(root/'native-v2/slides').mkdir(parents=True,exist_ok=True);(root/'native-v2/answers').mkdir(parents=True,exist_ok=True)
records=json.loads(Path('rebuild/source-objects.json').read_text());jobs=[];counts={1:0,2:0}
for rec in records:
 part=rec['part'];page=counts[part];counts[part]+=1
 jobs.append((part,'clean',page,rec['sequence']))
 if rec['hasAnswers']:jobs.append((part,'full',page,rec['sequence']))
def run(job):
 part,variant,page,seq=job
 with fitz.open(f'rebuild/pdf-v2/part{part}-{variant}.pdf') as doc:
  p=doc[page];pix=p.get_pixmap(matrix=fitz.Matrix(2400/p.rect.width,2400/p.rect.width),alpha=False)
  im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
  path=root/f"native-v2/{'slides' if variant=='clean' else 'answers'}/{seq:03}.webp";im.save(path,format='WEBP',lossless=True,method=4)
  return path.stat().st_size
if __name__=='__main__':
 total=0
 with ProcessPoolExecutor(max_workers=4) as ex:
  for i,n in enumerate(ex.map(run,jobs)):
   total+=n
   if i%20==0:print('RENDER',i+1,'/',len(jobs),'MB',round(total/1e6,1),flush=True)
 print('RENDER COMPLETE',len(jobs),round(total/1e6,1),'MB',flush=True)
