"""Extract word rectangles for the uploaded A2 unit 5 images; no translation service."""
import csv, io, json, re, subprocess, tempfile, unicodedata
from pathlib import Path
from PIL import Image
ROOT=Path("kitaplar/lise-a2/dedemin-meslegi")
def norm(s):
    return re.sub(r"^[^\w]+|[^\w]+$", "", s.replace("I","ı").replace("İ","i").lower(), flags=re.UNICODE)
def overlap(a,b):
    ix=max(0,min(a["x"]+a["w"],b["x"]+b["w"])-max(a["x"],b["x"]))
    iy=max(0,min(a["y"]+a["h"],b["y"]+b["h"])-max(a["y"],b["y"]))
    return ix*iy/max(1e-12,min(a["w"]*a["h"],b["w"]*b["h"]))
pages=[]
report={"method":"tesseract tur, PSM 3 + supplementary PSM 11","reviewed":False,"pages":[]}
for n in range(1,21):
    image=ROOT/"pages"/f"page-{n:03}.webp"
    with Image.open(image) as im:
        width,height=im.size
        with tempfile.TemporaryDirectory() as td:
            png=Path(td)/"page.png"
            im.convert("RGB").save(png)
            words=[]
            for psm in (3,11):
                result=subprocess.run(["tesseract",str(png),"stdout","-l","tur","--psm",str(psm),"tsv"],capture_output=True,text=True,check=True)
                for row in csv.DictReader(io.StringIO(result.stdout),delimiter="\t"):
                    text=(row.get("text") or "").strip()
                    if not text or not any(c.isalnum() for c in text): continue
                    if float(row["conf"])<15: continue
                    box={"t":text,"x":round(int(row["left"])/width,6),"y":round(int(row["top"])/height,6),"w":round(int(row["width"])/width,6),"h":round(int(row["height"])/height,6)}
                    if psm==11 and any(overlap(box,b)>.55 for b in words):continue
                    words.append(box)
    words.sort(key=lambda b:(round(b["y"]/0.008),b["x"]))
    pages.append({"page":n,"bookPage":98+n,"image":f"pages/page-{n:03}.webp","words":words,"phrases":[]})
    report["pages"].append({"page":n,"words":len(words),"width":width,"height":height,"coordinateReview":"pending"})
ROOT.joinpath("pages.json").write_text(json.dumps(pages,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
ROOT.joinpath("coverage.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(report,ensure_ascii=False,indent=2))
