"""Verify every decoded page and exact composited answer against the native source render."""
from pathlib import Path
import json,fitz
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[2];W=ROOT.parent/'work10';O=ROOT/'kitaplar/lise-a2/geziyorum/sunum'
m=json.loads((O/'manifest.json').read_text())['slides'];checks=0
with fitz.open(W/'pdf/clean.pdf') as clean,fitz.open(W/'pdf/full.pdf') as full:
 for i,s in enumerate(m):
  native=[]
  for d in [clean,full]:
   p=d[i];px=p.get_pixmap(matrix=fitz.Matrix(2400/p.rect.width,2400/p.rect.width),alpha=False);native.append(Image.frombytes('RGB',(px.width,px.height),px.samples))
  base=Image.open(O/s['image']).convert('RGB');assert ImageChops.difference(base,native[0]).getbbox() is None,('base',i+1)
  shown=Image.alpha_composite(base.convert('RGBA'),Image.open(O/s['answers']).convert('RGBA')).convert('RGB') if s['answers'] else base
  assert ImageChops.difference(shown,native[1]).getbbox() is None,('answers',i+1);checks+=2
print(json.dumps({'decodedPages':len(m),'exactPixelComparisons':checks,'answerComposites':sum(bool(s['answers']) for s in m)}))
