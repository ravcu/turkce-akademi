import json,numpy as np
from pathlib import Path
from PIL import Image
r=Path('repo/kitaplar/lise-a2/hafta-sonu-planin-ne/sunum');records=json.loads(Path('rebuild/source-objects.json').read_text());boxes=json.loads(Path('rebuild/answer-boxes.json').read_text());results=[]
for rec in records:
 seq=rec['sequence'];a=np.array(Image.open(r/f'native-v2/slides/{seq:03}.webp').convert('RGB'));assert a.shape==(1350,2400,3)
 if not rec['hasAnswers']:continue
 b=np.array(Image.open(r/f'native-v2/answers/{seq:03}.webp').convert('RGB'));delta=np.any(a!=b,axis=2);allowed=np.zeros(delta.shape,dtype=bool)
 for x,y,w,h in boxes[str(seq)]:
  x1=max(0,int(x*2400)-24);y1=max(0,int(y*1350)-24);x2=min(2400,int((x+w)*2400)+24);y2=min(1350,int((y+h)*1350)+24);allowed[y1:y2,x1:x2]=True
 outside=int(np.count_nonzero(delta&~allowed));results.append({'sequence':seq,'changedPixels':int(np.count_nonzero(delta)),'changedOutsideAnswerBounds':outside})
Path('rebuild/pixel-verification.json').write_text(json.dumps(results,indent=2));bad=[x for x in results if x['changedOutsideAnswerBounds']];print('Verified',len(results),'answer variants. Changes outside answer objects:',bad)
