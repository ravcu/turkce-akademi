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

# Reuse existing local editorial entries; retain only entries occurring in this unit.
base={k:{} for k in ("words","forms","examples","phrases","lemmas")}
for slug in ("ailem-ve-evim","bir-gunum","sehir-gezisi","bugun-hava-nasil","carsi-pazar","lise-a2/tatil-donusu","lise-a2/hafta-sonu-planin-ne","lise-a2/bir-gunum","lise-a2/simdi-haberler"):
    path=Path("kitaplar")/slug/"translations.json"
    if not path.exists():continue
    old=json.loads(path.read_text())
    for k in base:base[k].update(old.get(k,{}))
source=json.loads(ROOT.joinpath("source-text.json").read_text())
keys={norm(w) for text in source for w in text.replace("￾\\n","").split() if any(c.isalpha() for c in w)}
keys.update(norm(w["t"]) for p in pages for w in p["words"])
glossary={k:{key:value for key,value in base[k].items() if key in keys} for k in ("words","forms","examples","lemmas")}
glossary["phrases"]={key:value for key,value in base["phrases"].items() if all(norm(w) in keys for w in key.split())}
glossary["quizVocabulary"]=[k for k in glossary["words"] if len(k)>2 and k in keys]
glossary["metadata"]={"unit":5,"source":"uploaded WebP + source PDF","editorialStatus":"in progress","languages":["en","ru","ky","ar","fr"]}
ROOT.joinpath("translations.json").write_text(json.dumps(glossary,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
missing=sorted(k for k in keys if k and k not in glossary["words"] and k not in glossary["forms"])
report["missingMeanings"]=missing
report["uniqueEntries"]=len(keys)
ROOT.joinpath("coverage.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
