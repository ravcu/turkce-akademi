from pathlib import Path
import os
import json,io,subprocess,concurrent.futures,os
import fitz
from PIL import Image,ImageChops
R=Path(os.environ.get("A2_SUNU_WORK",Path(__file__).resolve().parents[3]/"a2-source"));O=R.parent/'turkce-akademi/kitaplar/lise-a2/tatil-donusu/sunum/assets'
for f in ['slides','answers','audio']:(O/f).mkdir(parents=True,exist_ok=True)
rs=[r for r in json.loads((R/'inventory.json').read_text()) if not r['excluded']]
def writeim(im,p,**kw):
 b=io.BytesIO();im.save(b,format='WEBP',**kw);tmp=p.with_suffix('.tmp');tmp.write_bytes(b.getvalue());tmp.replace(p)
def work(r):
 i=r['sequence'];ims=[]
 for mode in ['clean','full']:
  d=fitz.open(R/f'part{r["part"]}-{mode}.pdf');pix=d[r['slide']-1].get_pixmap(matrix=fitz.Matrix(2,2));ims.append(Image.open(io.BytesIO(pix.tobytes('png'))).convert('RGB'))
 clean,full=ims;writeim(clean,O/'slides'/f'{i:03}.webp',quality=94,method=4);diff=ImageChops.difference(clean,full).convert('L').point(lambda a:255 if a>10 else 0);r['answers']=bool(diff.getbbox())
 if r['answers']:im=full.convert('RGBA');im.putalpha(diff);writeim(im,O/'answers'/f'{i:03}.webp',lossless=True)
 b=io.BytesIO();clean.save(b,format='PNG');p=R/f'{i:03}.png';p.write_bytes(b.getvalue());env=os.environ.copy();env['OMP_THREAD_LIMIT']='1'
 raw=subprocess.check_output(['tesseract',str(p),'stdout','--tessdata-dir','/tmp','-l','tur','--psm','11','-c','tessedit_create_tsv=1'],env=env,stderr=subprocess.DEVNULL);(R/f'{i:03}.tsv').write_bytes(raw);p.unlink()
 for j,a in enumerate(r['audio'],1):
  dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',a['file']]));a['end']=dur-a['trimEnd'];length=a['end']-a['start'];assert length>0;name=f'p{r["part"]}-{r["slide"]:03}-{j}.mp3'
  subprocess.run(['ffmpeg','-v','error','-y','-ss',str(a['start']),'-i',a['file'],'-t',str(length),'-vn','-c:a','libmp3lame','-b:a','128k',str(O/'audio'/name)],check=True);a['output']=name
 return i
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
 for i in pool.map(work,rs):print(i,flush=True)
(R/'rendered.json').write_text(json.dumps(rs,ensure_ascii=False,indent=2))
