"""Extract word rectangles for the uploaded A2 unit 5 images; no translation service."""
import csv, io, json, re, subprocess, tempfile, unicodedata
from pathlib import Path
from PIL import Image
import difflib
ROOT=Path("kitaplar/lise-a2/dedemin-meslegi")
def norm(s):
    return re.sub(r"^[^\w]+|[^\w]+$", "", s.replace("I","ı").replace("İ","i").lower(), flags=re.UNICODE)
def overlap(a,b):
    ix=max(0,min(a["x"]+a["w"],b["x"]+b["w"])-max(a["x"],b["x"]))
    iy=max(0,min(a["y"]+a["h"],b["y"]+b["h"])-max(a["y"],b["y"]))
    return ix*iy/max(1e-12,min(a["w"]*a["h"],b["w"]*b["h"]))
source=json.loads(ROOT.joinpath("source-text.json").read_text())
source=[text.replace("￾\n","").replace("￾","").replace("￾","") for text in source]
pages=[]
cache=ROOT/"pages.json"
cache_report=ROOT/"coverage.json"
if cache.exists() and cache_report.exists():
    old_report=json.loads(cache_report.read_text())
    if "PSM 6" in old_report.get("method",""):
        cached=json.loads(cache.read_text())
        if len(cached)==20 and all(p.get("words") for p in cached):pages=cached
report={"method":"tesseract tur, PSM 3 + PSM 11 + PSM 6; PDF text filter","reviewed":False,"pages":[]}
for n in ([] if pages else range(1,21)):
    allowed={norm(w).replace("’","'") for w in source[n-1].split()}
    allowed.update(norm(part).replace("’","'") for w in source[n-1].split() for part in w.split("/"))
    image=ROOT/"pages"/f"page-{n:03}.webp"
    with Image.open(image) as im:
        width,height=im.size
        with tempfile.TemporaryDirectory() as td:
            png=Path(td)/"page.png"
            im.convert("RGB").save(png)
            words=[]
            for psm in (3,11,6):
                result=subprocess.run(["tesseract",str(png),"stdout","-l","tur","--psm",str(psm),"tsv"],capture_output=True,text=True,check=True)
                for row in csv.DictReader(io.StringIO(result.stdout),delimiter="\t",quoting=csv.QUOTE_NONE):
                    text=(row.get("text") or "").strip()
                    if not text or not any(c.isalnum() for c in text): continue
                    if float(row["conf"])<(35 if psm==3 else 65): continue
                    candidate=norm(text).replace("’","'")
                    if candidate not in allowed and not candidate.isdigit() and not re.fullmatch(r"[SMV]\.\d{3}",text):
                        continue
                    box={"t":text,"x":round(int(row["left"])/width,6),"y":round(int(row["top"])/height,6),"w":round(int(row["width"])/width,6),"h":round(int(row["height"])/height,6)}
                    if psm!=3 and any(overlap(box,b)>.55 for b in words):continue
                    words.append(box)
    words.sort(key=lambda b:(round(b["y"]/0.008),b["x"]))
    pages.append({"page":n,"bookPage":98+n,"image":f"pages/page-{n:03}.webp","words":words,"phrases":[]})
    report["pages"].append({"page":n,"words":len(words),"width":width,"height":height,"coordinateReview":"pending"})
if not report["pages"]:
    report["pages"]=[{"page":p["page"],"words":len(p["words"]),"coordinateReview":"pending"} for p in pages]
ROOT.joinpath("pages.json").write_text(json.dumps(pages,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
ROOT.joinpath("coverage.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(report,ensure_ascii=False,indent=2))

# Reuse existing local editorial entries; retain only entries occurring in this unit.
base={k:{} for k in ("words","forms","examples","phrases","lemmas")}
for slug in ("tanisalim","okuldayiz","ailem-ve-evim","bir-gunum","sehir-gezisi","bugun-hava-nasil","carsi-pazar","gecmis-olsun","davetlisiniz","tatil-planim","lise-a2/tatil-donusu","lise-a2/hafta-sonu-planin-ne","lise-a2/bir-gunum","lise-a2/simdi-haberler"):
    path=Path("kitaplar")/slug/"translations.json"
    if not path.exists():continue
    old=json.loads(path.read_text())
    for k in base:base[k].update(old.get(k,{}))
keys={norm(w) for text in source for w in text.replace("￾\n","").split() if any(c.isalpha() for c in w)}
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

# Apply unit-specific editorial translations after inherited entries.
editorial=ROOT/"editorial.json"
if editorial.exists():
    edits=json.loads(editorial.read_text())
    for section in ("words","forms","examples","phrases"):
        glossary.setdefault(section,{}).update(edits.get(section,{}))
# Names retain their identity across languages. Inflected names need separate editorial review.
names={"Rina","Habiba","Armin","Karima","Hiba","Adel","Amira","Nisa","Melik","Muhammad","Hayfa","Adim","Lili","Ayşa","Burak","Sema","Mustafa","Betül","Selin","Selçuk","Bayraktar","Mesut","Barış","Manço","Güngör","Robert","Sarıyer"}
for name in names:
    key=norm(name)
    if key in keys and key not in glossary["words"]:glossary["words"][key]=[name]*5
def token(s):
    return norm(s).replace("’","'").replace("â","a").replace("î","i")
phrase_keys=sorted(glossary["phrases"],key=lambda s:len(s.split()),reverse=True)
for page in pages:
    words=page["words"];groups=[];used=set()
    for phrase in phrase_keys:
        parts=[token(w) for w in phrase.split()]
        if len(parts)<2:continue
        for i,word in enumerate(words):
            if i in used or token(word["t"])!=parts[0]:continue
            indices=[i]
            for part in parts[1:]:
                last=words[indices[-1]]
                candidates=[]
                for j,other in enumerate(words):
                    if j in indices or j in used or token(other["t"])!=part:continue
                    same=abs(other["y"]-last["y"])<max(last["h"],other["h"])*.6 and 0<=other["x"]-(last["x"]+last["w"])<.075
                    wrap=0<other["y"]-last["y"]<max(.045,last["h"]*2.2) and other["x"]<last["x"] and abs(other["y"]-last["y"])>last["h"]*.5
                    if same or wrap:candidates.append((0 if same else 1,abs(other["y"]-last["y"])+abs(other["x"]-last["x"])*.1,j))
                if not candidates:break
                indices.append(min(candidates)[2])
            if len(indices)==len(parts):
                groups.append({"key":phrase,"text":" ".join(words[j]["t"] for j in indices),"indices":indices})
                used.update(indices)
    page["phraseGroups"]=groups
    page.pop("phrases",None)
# Preserve only vocabulary actually present; the quiz must not include another unit's words.
glossary["quizVocabulary"]=sorted(k for k in keys if k in glossary["words"] and len(k)>2 and not k.isdigit() and k not in {norm(n) for n in names})
ROOT.joinpath("pages.json").write_text(json.dumps(pages,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
ROOT.joinpath("translations.json").write_text(json.dumps(glossary,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
report["missingMeanings"]=sorted(k for k in keys if k and k not in glossary["words"] and k not in glossary["forms"])
report["missingExamples"]=sorted(k for k in keys if k not in glossary["examples"] and not glossary["forms"].get(k,{}).get("exampleTr"))
report["phraseGroups"]=sum(len(p.get("phraseGroups",[])) for p in pages)
ROOT.joinpath("coverage.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
