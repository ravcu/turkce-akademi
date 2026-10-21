"""Render supplied PDF pages at 360 DPI, preserving the uploaded filenames."""
import argparse,fitz
from PIL import Image
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
p=argparse.ArgumentParser();p.add_argument('pdf');a=p.parse_args();source=Path(a.pdf);out=Path('kitaplar/lise-a2/spor-ve-saglik/pages');out.mkdir(exist_ok=True)
with fitz.open(source) as d:count=len(d)
def render(i):
 with fitz.open(source) as d:
  pix=d[i].get_pixmap(matrix=fitz.Matrix(5,5),alpha=False)
  image=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
  target=out/f'sayfa-{i+1:02}.webp';image.save(target,'WEBP',quality=95,method=6)
  return (i+1,pix.width,pix.height,target.stat().st_size)
with ThreadPoolExecutor(max_workers=4) as pool:
 for row in pool.map(render,range(count)):print(*row,flush=True)
