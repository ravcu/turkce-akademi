"""Verify every page/selection/export, shared/local audio and unchanged reader styles."""
from pathlib import Path
import json,re,hashlib,subprocess,os
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import prepare_a2_unit9_speech as speech
R=speech.ROOT
report=json.loads(subprocess.check_output(['node','tests/verify-lise-a2-unit9.cjs']))
assert not report['errors'],report['errors']
pages=json.loads((R/'pages.json').read_text());g=json.loads((R/'translations.json').read_text());idx=json.loads((R/'speech/index.json').read_text())
assert len(pages)==20
assert idx['sourceSha']==hashlib.sha256((R/'translations.json').read_bytes()+(R/'pages.json').read_bytes()).hexdigest()
for lang,corpus in speech.corpus.items():assert not set(corpus)-set(idx['entries'][lang]),(lang,'missing speech')
base=Path('kitaplar/lise-a2/spor-ve-saglik/index.html').read_text();html=(R/'index.html').read_text()
assert re.findall('<style>(.*?)</style>',html,re.S)==re.findall('<style>(.*?)</style>',base,re.S),'reader design changed'
covered=[]
for page in pages:
 im=Image.open(R/page['image']);assert im.size==(3204,4054),(page['page'],im.size)
 for i,w in enumerate(page['words']):
  x=w['x']+w['w']/2;y=w['y']+w['h']/2
  if any(z['x']<x<z['x']+z['w'] and z['y']<y<z['y']+z['h'] for z in page['words'][i+1:]):covered.append((page['page'],w['t']))
assert not covered,covered
for key in ['dünya evine girmek','hayata gözlerini yummak']:
 assert any(p['key']==key for p in pages[17]['phraseGroups']),key
assert any(w['t']=='Mükemmel' for w in pages[19]['words'])
for key,meaning in {'o':'he; she; it; that','karadaki':'on land','havaya':'into the air; up','adım':'step; stage','muradına':"to their heart's desire; to their wish",'evlendim':'I got married','konuşamamak':'to be unable to speak'}.items():assert g['words'][key][0]==meaning,(key,g['words'][key])
assert 'href="../bir-hikayem-var/"' in base
assert 'href="../spor-ve-saglik/"' in html
assert '10. ünite henüz hazırlanmadı' in html
tracked=set(subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD']).decode().splitlines())
files={};external=set()
for lang,entries in idx['entries'].items():
 for k,(f,start,end) in entries.items():
  assert 0<=start<end,(lang,k)
  if f.startswith('../'):external.add(os.path.normpath(str(R/'speech'/f)))
  else:files.setdefault(f,[]).append((start,end))
assert external<=tracked,('missing shared files',external-tracked)
def duration(name):
 p=R/'speech'/name
 try:
  assert p.is_file() and p.stat().st_size>500
  secs=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(p)],stderr=subprocess.DEVNULL))
  assert all(end<=secs+.1 for _,end in files[name])
 except Exception:return name
with ThreadPoolExecutor(max_workers=8) as pool:bad=[x for x in pool.map(duration,files) if x]
assert not bad,bad
for p in (R/'speech').glob('*.mp3'):
 if p.name not in files:p.unlink()
report.update(unit=9,languages=['en','ru','ky','ar','fr'],coveredHotspotCentres=covered,readerCss='identical to unit 8',imageResolution='360 DPI; 3204 x 4054 pixels',translationSource='ChatGPT editorial translations; no translation service',speechEngine='eSpeak NG local synthesis; existing matching recordings reused',speechEntries={l:len(e) for l,e in idx['entries'].items()},localSpeechFiles=len(files),sharedSpeechFiles=len(external),originalMediaPending=['S.054','S.055','S.056','S.057','V.010','V.011'],validation='all word selections in five languages; 100 print exports; all phrase selection members; source word coordinates; six speech corpora and MP3 duration limits',browserValidation='not performed: container disallows browser sockets',sourceNotes=['Printed date 12 Ocak 1273 is flagged for review; answer key uses the printed year only.','Biography task asks for five sections but displays four sections.','The source typo gözlerine inanamak is grouped and translated as gözlerine inanamamak.'])
(R/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
coverage={k:report[k] for k in ['unit','pages','hotspots','logicalSelections','forms','phraseEntries','phraseOccurrences','originalMediaPending']};coverage.update(missingMeanings=[],missingExamples=[],verification='verification.json')
(R/'coverage.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
