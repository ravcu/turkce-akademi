"""Find source-confirmed OCR candidates in illustrated A2 unit 5 page regions."""
import csv, io, json, re, subprocess, tempfile, unicodedata
from pathlib import Path
from PIL import Image, ImageOps
ROOT=Path("kitaplar/lise-a2/dedemin-meslegi")
source=json.loads((ROOT/"source-text.json").read_text())
def norm(s):
    return re.sub(r"^[^\w]+|[^\w]+$", "", s.replace("I","ı").replace("İ","i").lower().replace("’","'").replace("‘","'"))
def overlap(a,b):
    area=max(0,min(a["x"]+a["w"],b["x"]+b["w"])-max(a["x"],b["x"]))*max(0,min(a["y"]+a["h"],b["y"]+b["h"])-max(a["y"],b["y"]))
    return area/max(1e-12,min(a["w"]*a["h"],b["w"]*b["h"]))
results=[]
(ROOT/"preview").mkdir(exist_ok=True)
for n in range(1,21):
    with Image.open(ROOT/"pages"/f"page-{n:03}.webp") as original:
        original=original.convert("RGB");width,height=original.size
        preview=original.copy();preview.thumbnail((1100,1500));preview.save(ROOT/"preview"/f"page-{n:03}.jpg",quality=83,optimize=True)
        text=source[n-1].replace("￾\n","").replace("￾","")
        allowed={norm(w):w for w in text.split()}
        for word in text.split():
            for part in word.split("/"):allowed.setdefault(norm(part),part)
        raw=[]
        if n in (1,2,3,4,5,6,8,9,11,12,13,14,15,17,18,19,20):
            regions=[(x,y,min(x+.42,1),min(y+.38,1)) for y in (0,.31,.62) for x in (0,.29,.58)]
            with tempfile.TemporaryDirectory() as td:
                for ci,(x0,y0,x1,y1) in enumerate(regions):
                    left,top,right,bottom=map(int,(x0*width,y0*height,x1*width,y1*height))
                    crop=ImageOps.autocontrast(ImageOps.grayscale(original.crop((left,top,right,bottom))))
                    path=Path(td)/f"crop-{ci}.png";crop.save(path)
                    tsv=subprocess.run(["tesseract",str(path),"stdout","-l","tur","--psm","6","tsv"],capture_output=True,text=True,check=True).stdout
                    for row in csv.DictReader(io.StringIO(tsv),delimiter="\t",quoting=csv.QUOTE_NONE):
                        word=(row.get("text") or "").strip()
                        if not word or float(row["conf"])<35 or not any(c.isalpha() for c in word):continue
                        if "\n" in word or "\t" in word:continue
                        box={"t":word,"x":round((left+int(row["left"]))/width,6),"y":round((top+int(row["top"]))/height,6),"w":round(int(row["width"])/width,6),"h":round(int(row["height"])/height,6),"confidence":round(float(row["conf"]),2)}
                        if any(overlap(box,b)>.6 and norm(box["t"])==norm(b["t"]) for b in raw):continue
                        raw.append(box)
        words=[];joined=[]
        for box in raw:
            key=norm(box["t"])
            if key in allowed and len(key)>1:
                words.append(box);continue
            if len(key)<2:continue
            key=key.rstrip("-")
            for other in raw:
                if other is box:continue
                dy=other["y"]-box["y"]
                if not(box["h"]*.5<dy<max(.045,box["h"]*2.5)):continue
                if other["x"]>box["x"] or box["x"]-other["x"]>.4:continue
                full=key+norm(other["t"])
                if full in allowed and len(full)>len(key):
                    joined.append({"key":full,"text":allowed[full],"segments":[box,other]});break
        results.append({"page":n,"words":words,"joined":joined})
        print(f"Page {n}: {len(words)} source-confirmed candidates, {len(joined)} joined candidates",flush=True)
(ROOT/"position-candidates.json").write_text(json.dumps(results,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
