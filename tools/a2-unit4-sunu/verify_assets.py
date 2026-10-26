from pathlib import Path
import json,os,io,subprocess,hashlib
import fitz
from PIL import Image
R=Path(__file__).resolve().parents[2];W=R.parent/'rebuild4';O=R/'kitaplar/lise-a2/simdi-haberler/sunum'
def atomic(path,data):
 temp=path.with_name(path.name+'.tmp');fd=os.open(temp,os.O_CREAT|os.O_TRUNC|os.O_WRONLY,0o644)
 try:
  view=memoryview(data)
  while view:view=view[os.write(fd,view[:65536]):]
  os.fsync(fd)
 finally:os.close(fd)
 assert temp.stat().st_size==len(data);temp.replace(path);assert hashlib.sha256(path.read_bytes()).digest()==hashlib.sha256(data).digest()
S=json.loads((O/'assets/slides.json').read_text())['slides'];records=json.loads((W/'source-objects.json').read_text());repaired=[]
for s in S:
 for key,mode in [('image','clean'),('answerImage','full')]:
  if key not in s:continue
  path=O/s[key]
  try:
   with Image.open(path) as im:im.load();assert im.size==(2400,1350)
  except Exception:
   rs=[r for r in records if r['part']==s['sourcePart']];pg=next(i for i,r in enumerate(rs) if r['localSlide']==s['sourcePartSlide'])
   with fitz.open(W/f'pdf/part{s["sourcePart"]}-{mode}.pdf') as d:
    p=d[pg];pix=p.get_pixmap(matrix=fitz.Matrix(2400/p.rect.width,2400/p.rect.width),alpha=False);im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);buf=io.BytesIO();im.save(buf,format='WEBP',lossless=True,method=4);atomic(path,buf.getvalue())
   repaired.append(str(path));print('Repaired image',s['sequence'],mode,flush=True)
 r=next(r for r in records if r['part']==s['sourcePart'] and r['localSlide']==s['sourcePartSlide'])
 for a,native in zip(s.get('audioSegments',[]),r['audio']):
  target=O/a['src'];duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(target)]));length=a['sourceEnd']-a['sourceStart']
  if abs(duration-length)>.12:
   temp=W/'recut.mp3';subprocess.run(['ffmpeg','-v','error','-y','-ss',str(native['start']),'-i',native['file'],'-t',str(length),'-c:a','libmp3lame','-b:a','128k',str(temp)],check=True);atomic(target,temp.read_bytes());repaired.append(str(target));print('Repaired audio',s['sequence'],flush=True)
  final=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(target)]));assert abs(final-length)<.12,(s['sequence'],final,length)
print('ALL REFERENCES VERIFIED; repaired',len(repaired),flush=True)
