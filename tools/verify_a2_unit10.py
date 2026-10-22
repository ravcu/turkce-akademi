"""Verify all unit 10 selections/exports, unchanged design, source areas and speech."""
from pathlib import Path
import json,re,hashlib,subprocess,os
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import prepare_a2_unit10_speech as speech
R=speech.ROOT
report=json.loads(subprocess.check_output(['node','tests/verify-lise-a2-unit10.cjs']))
assert not report['errors'],report['errors']
pages=json.loads((R/'pages.json').read_text());g=json.loads((R/'translations.json').read_text());idx=json.loads((R/'speech/index.json').read_text())
assert len(pages)==30
assert idx['sourceSha']==hashlib.sha256((R/'translations.json').read_bytes()+(R/'pages.json').read_bytes()).hexdigest()
for lang,corpus in speech.corpus.items():assert not set(corpus)-set(idx['entries'][lang]),(lang,'missing speech',set(corpus)-set(idx['entries'][lang]))
base=Path('kitaplar/lise-a2/bir-hikayem-var/index.html').read_text();html=(R/'index.html').read_text()
assert re.findall('<style>(.*?)</style>',html,re.S)==re.findall('<style>(.*?)</style>',base,re.S),'reader design changed'
assert 'href="../geziyorum/"' in base
assert 'href="../bir-hikayem-var/"' in html
assert 'Lise A2 kitabının son ünitesindesiniz' in html
covered=[]
for page in pages:
 im=Image.open(R/page['image']);assert im.size==(3204,4054),(page['page'],im.size)
 for i,w in enumerate(page['words']):
  x=w['x']+w['w']/2;y=w['y']+w['h']/2
  if any(z['x']<x<z['x']+z['w'] and z['y']<y<z['y']+z['h'] for z in page['words'][i+1:]):covered.append((page['page'],w['t']))
assert not covered,covered
for key in ['kız kulesi','yer ayırtma','alışveriş çeki','yeme de yanında yat','emniyet kemerinizi']:
 assert any(x['key']==key for page in pages for x in page['phraseGroups']),key
assert any(w['t']=='Biniş' and w.get('positionSource') for w in pages[10]['words'])
for key,meaning in {'karar':'decision','o':'he; she; it; that','oda':'room','kitap':'book','yarı:sevgili':'the beloved (object; from yar)'}.items():assert g['words'][key][0]==meaning
assert g['forms']['dersin']['lemma']=='demek'
assert idx['languageEngines']['ar']['engine']=='Piper'
assert idx['languageEngines']['ar']['voice']=='ar_JO-kareem-medium'
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
report.update(unit=10,languages=['en','ru','ky','ar','fr'],coveredHotspotCentres=covered,readerCss='identical to unit 9',imageResolution='360 DPI; 3204 x 4054 pixels',translationSource='ChatGPT editorial translations; no translation service',speechEngine='eSpeak NG with existing matching clips reused; Arabic Piper ar_JO-kareem-medium with Tashkeel',speechEntries={l:len(e) for l,e in idx['entries'].items()},localSpeechFiles=len(files),sharedSpeechFiles=len(external),originalMediaPending=['S.058','S.059','S.060','S.061','S.062','M.007','V.012','V.013'],validation='all word selections in five languages; all 150 print exports include every distinct printed word and matching phrase; all phrase selection members; source word coordinates; six speech corpora and MP3 duration limits',browserValidation='not performed: Chromium download unavailable in this environment',sourceNotes=['Page 10 fifth announcement describes a hospital; the printed options omit hospital.','Page 11 form and ticket labels are embedded images; all visible labels have editorial word areas.','Hotel prices and travel claims are treated as textbook content rather than current commercial or transport information.','Page 24 yarı means the beloved, not half; daşları is a dialect form; refrain syllables are explained as nonlexical.','Printed Gülekin and Sulanahmet text-layer errors map to the visually printed Gültekin and Sultanahmet.'])
(R/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
coverage={k:report[k] for k in ['unit','pages','hotspots','logicalSelections','forms','phraseEntries','phraseOccurrences','originalMediaPending']};coverage.update(missingMeanings=[],missingExamples=[],verification='verification.json')
(R/'coverage.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2))
(R/'speech/README.md').write_text('# Kelime ve örnek sesleri\n\nTürkçe, İngilizce, Rusça, Kırgızca ve Fransızca: mevcut eşleşen kayıtlar ve yerel eSpeak NG üretimi. Arapça: ar_JO-kareem-medium Piper modeli ve Tashkeel; 9. ünitenin aynı modelle üretilen eşleşen kayıtları yeniden kullanılır.\n\nBunlar sözcük ve örnek telaffuz kayıtlarıdır. Kitabın özgün S/M/V medya kayıtları değildir. index.json metinleri dosya ve zaman aralıklarına eşler. Sayfa değişiminde ses durdurulur.\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
