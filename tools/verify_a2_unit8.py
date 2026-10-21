"""Validate A2 unit 8 editorial coverage, reader exports and speech resources."""
import hashlib,json,os,re,subprocess,sys
from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
import prepare_a2_unit8_speech as speech
ROOT=speech.ROOT
report=json.loads(subprocess.check_output(['node','tests/verify-lise-a2-unit8.cjs']))
assert not report['errors'],report['errors']
pages=json.loads((ROOT/'pages.json').read_text());g=json.loads((ROOT/'translations.json').read_text())
index=json.loads((ROOT/'speech/index.json').read_text())
source=hashlib.sha256((ROOT/'translations.json').read_bytes()+(ROOT/'pages.json').read_bytes()).hexdigest()
assert index['sourceSha']==source,'stale speech index'
for lang,items in speech.corpus.items():
 assert not set(items)-set(index['entries'][lang]),(lang,'missing speech text')
base=Path('kitaplar/lise-a2/akilli-teknoloji/index.html').read_text();html=(ROOT/'index.html').read_text()
assert re.findall('<style>(.*?)</style>',base,re.S)==re.findall('<style>(.*?)</style>',html,re.S)
for p in pages:
 image=Image.open(ROOT/p['image']);assert image.size==(3204,4054),(p['page'],image.size)
covered=[]
for p in pages:
 for i,w in enumerate(p['words']):
  if not re.search('[a-zA-ZÇĞİÖŞÜçğıöşü]',w['t']):continue
  x=w['x']+w['w']/2;y=w['y']+w['h']/2
  if any(z['x']<x<z['x']+z['w'] and z['y']<y<z['y']+z['h'] for z in p['words'][i+1:]):covered.append((p['page'],w['t']))
assert not covered,covered
expected={(3,339):'için:emir',(13,5):'iç:emir',(13,8):'yüz:organ',(14,1):'yazı:para',(14,5):'tura:para',(16,75):'basma:kumaş',(16,98):'yazması:başörtüsü',(16,103):'yazı:kader',(16,104):'yazması:eylem',(18,37):'yaz:emir',(18,48):'yaz:emir',(20,107):'yüz:sayı'}
for (pi,wi),key in expected.items():
 assert pages[pi-1]['words'][wi]['entryKey']==key,(pi,wi,key)
 assert any(w['entryKey']==key for w in pages[pi-1]['exportWords'])
assert g['words']['adım'][0]=='step'
assert g['words']['ana'][0]=='main; principal'
assert g['words']['cilt'][0]=='skin'
assert g['words']['tarif'][0]=='recipe'
assert g['forms']['sürer']['formTranslations'][0]=='lasts; takes (time)'
assert g['forms']['yemeden']['lemmaTranslations'][0]=='to eat'
assert 'href="../akilli-teknoloji/"' in html
assert 'title="9. ünite henüz hazırlanmadı"' in html
assert 'href="../spor-ve-saglik/"' in base
tracked=set(subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD']).decode().splitlines())
files={};external=set()
for lang,entries in index['entries'].items():
 for k,(file,start,end) in entries.items():
  assert 0<=start<end,(lang,k)
  if file.startswith('../'):external.add(os.path.normpath(str(ROOT/'speech'/file)))
  else:files.setdefault(file,[]).append((start,end))
assert external<=tracked,('missing shared audio',external-tracked)
def duration(name):
 path=ROOT/'speech'/name
 try:
  assert path.is_file() and path.stat().st_size>500
  d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(path)],stderr=subprocess.DEVNULL))
  assert all(end<=d+.1 for start,end in files[name])
  return None
 except Exception:return name
with ThreadPoolExecutor(max_workers=8) as pool:bad=[x for x in pool.map(duration,files) if x]
assert not bad,('invalid local media',bad)
# Discard only obsolete generated clips from this unit.
for path in (ROOT/'speech').glob('*.mp3'):
 if path.name not in files:path.unlink()
report.update(unit=8,languages=['en','ru','ky','ar','fr'],readerCss='identical to unit 7',coveredHotspotCentres=covered,
 validation='static reader harness, source word rectangles, language columns, phrase grouping, print export, speech corpus and MP3 duration checks',
 browserValidation='not run: local browser sockets unavailable',
 originalMediaPending=['S.050','S.051','S.052','S.053','M.006','V.009'],
 answerKeyStatus='reading and open-ended sample answers added; unavailable original media answers not guessed; ambiguous reading question flagged',
 speechSourceSha=source,speechEntries={l:len(x) for l,x in index['entries'].items()},localSpeechFiles=len(files),sharedSpeechFiles=len(external))
(ROOT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
coverage={k:report[k] for k in ['unit','pages','hotspots','forms','phraseEntries','phraseOccurrences','originalMediaPending']}
coverage.update(wordEntries=len(g['words']),missingMeanings=[],missingExamples=[],verification='verification.json')
(ROOT/'coverage.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2))
(ROOT/'speech/README.md').write_text('Synthetic vocabulary pronunciation in Turkish, English, Russian, Kyrgyz, Arabic and French. New clips use local eSpeak NG synthesis; matching earlier recordings are reused from units 6 and 7 and the shared audio corpus. These are separate from the original textbook listening recordings, which have not been supplied. The index maps normalized text and language to MP3 files with start and end offsets. Local MP3 durations and every required text key were checked.\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
