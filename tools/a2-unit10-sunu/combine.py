"""Join the three native PDF exports and audited records in presentation order."""
from pathlib import Path
import json,fitz
ROOT=Path(__file__).resolve().parents[2];W=ROOT.parent/'work10';O=ROOT/'kitaplar/lise-a2/geziyorum/sunum';(W/'pdf').mkdir(exist_ok=True)
rows=[];audits=[]
for part in range(1,4):
 p=W/f'part{part}';audit=json.loads((p/'source-audit.json').read_text());audits.append(audit)
 for r in json.loads((p/'source-objects.json').read_text()):r['sequence']=len(rows)+1;rows.append(r)
(W/'source-objects.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
a={'sourceParts':[{'part':i+1,'sourceSha256':a['sourceSha256'],'sourceSlides':a['sourceSlides']} for i,a in enumerate(audits)],'sourceSlides':sum(a['sourceSlides'] for a in audits),'keptSlides':len(rows),'excluded':sum([a['excluded'] for a in audits],[]),'slides':rows,'originalPicturesPreserved':True,'pictureHashChecks':sum(a['pictureHashChecks'] for a in audits),'removedEnglishTables':sum(a['removedEnglishTables'] for a in audits),'addedAnswerObjects':sum(a['addedAnswerObjects'] for a in audits)}
(O/'source-audit.json').write_text(json.dumps(a,ensure_ascii=False,indent=2))
for mode in ['clean','full']:
 out=fitz.open()
 for part in range(1,4):
  with fitz.open(W/f'part{part}/{mode}.pdf') as d:out.insert_pdf(d)
 assert len(out)==len(rows);out.save(W/f'pdf/{mode}.pdf')
print('Combined',len(rows),'slides')
