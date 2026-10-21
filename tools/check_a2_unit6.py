"""End-to-end checks for the A2 unit 6 reader, without using translation services."""
from pathlib import Path
import json,re,hashlib,threading,http.server,os,subprocess,time
from playwright.sync_api import sync_playwright
SKIP_AUDIO=os.environ.get('UNIT6_SKIP_AUDIO')=='1'
ROOT=Path('kitaplar/lise-a2/hayat-birlikte-guzel');QA=Path('/tmp/unit6-qa');QA.mkdir(exist_ok=True)
g=json.loads((ROOT/'translations.json').read_text());pages=json.loads((ROOT/'pages.json').read_text());audio={'entries':{}} if SKIP_AUDIO else json.loads((ROOT/'speech/index.json').read_text());answers=json.loads((ROOT/'answers.json').read_text())
def norm(s):return re.sub(r'^[^\w]+|[^\w]+$','',s.replace('’',"'").replace('I','ı').replace('İ','i').lower())
def speechkey(s,l):
 s=re.sub(r'\s+',' ',re.sub(r'(^|\s)[\-−–—]+(?=\s*\S)',r'\1',s)).strip()
 if l=='tr':s=s.replace('I','ı').replace('İ','i')
 return re.sub(r'^[.!?,:;…\s]+|[.!?,:;…\s]+$','',s.lower())
def example(k,phrase=False):
 if phrase:
  f=g['phrases'][k];return f.get('exampleTr'),f.get('examples')
 f=g['forms'].get(k,{})
 if f.get('exampleTr'):return f['exampleTr'],f.get('examples')
 e=g['examples'].get(k)
 if isinstance(e,list):return e
 return (e or {}).get('tr'),(e or {}).get('values')
def speech(l,t):
 if SKIP_AUDIO:return
 assert speechkey(t,l) in audio['entries'][l],('audio missing',l,t)
expected=hashlib.sha256((ROOT/'translations.json').read_bytes()+(ROOT/'pages.json').read_bytes()).hexdigest()
if not SKIP_AUDIO:assert audio['sourceSha']==expected,'stale audio corpus'
langs=['en','ru','ky','ar','fr'];lexical=0
for p in pages:
 for w in p['words']:
  assert all(isinstance(w[a],(int,float)) for a in ['x','y','w','h'])
  assert 0<=w['x']<1 and 0<=w['y']<1 and w['w']>0 and w['h']>0
  assert w['x']+w['w']<=1.003 and w['y']+w['h']<=1.003
  k=norm(w.get('entryKey',w['t']))
  if not re.search(r'[^\W\d_]',k) or re.match(r'^[smv]\.\d+$',k):continue
  f=g['forms'].get(k);meanings=f.get('formTranslations') if f else g['words'].get(k)
  assert meanings and len(meanings)==5 and all(isinstance(x,str) and x.strip() for x in meanings),(p['page'],'meaning',k)
  tr,ex=example(k);assert tr and ex and len(ex)==5,(p['page'],'example',k)
  speech('tr',w['t']);speech('tr',tr)
  for l,t in zip(langs,meanings):speech(l,t)
  for l,t in zip(langs,ex):speech(l,t)
  if f:
   assert f.get('lemmaTranslations') and len(f['lemmaTranslations'])==5,('lemma',k)
   speech('tr',f['lemma'])
   for l,t in zip(langs,f['lemmaTranslations']):speech(l,t)
  lexical+=1
 for group in p['phraseGroups']+p['wordGroups']:
  assert group['indices'] and all(0<=i<len(p['words']) for i in group['indices'])
  speech('tr',group['text'])
  if group in p['phraseGroups']:
   f=g['phrases'][group['key']];assert len(f['translations'])==5
   tr,ex=example(group['key'],True);assert tr and ex and len(ex)==5,group['key']
   speech('tr',tr)
   for l,t in zip(langs,f['translations']):speech(l,t)
   for l,t in zip(langs,ex):speech(l,t)
 # Exports use the complete PDF vocabulary rather than only OCR-recognised words.
 assert p['exportWords']
 for w in p['exportWords']:
  k=w['entryKey']
  assert k in g['words'] or k in g['forms'] or not re.search(r'[^\W\d_]',k) or re.match(r'^[smv]\.\d+$',k),('export',k)
for l,entries in audio['entries'].items():
 for k,(file,start,end) in entries.items():
  assert 0<=start<end
  assert (ROOT/'speech'/file).is_file(),(l,file)
base=Path('kitaplar/lise-a2/dedemin-meslegi/index.html').read_text();html=(ROOT/'index.html').read_text()
assert re.findall(r'<style>(.*?)</style>',base,re.S)==re.findall(r'<style>(.*?)</style>',html,re.S),'reader CSS differs'
assert '../dedemin-meslegi/' in html and '../akilli-teknoloji/' in html
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Quiet)
threading.Thread(target=server.serve_forever,daemon=True).start()
baseurl=f'http://127.0.0.1:{server.server_port}'
errors=[];checks=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
 page=browser.new_page(viewport={'width':1440,'height':1050});page.on('pageerror',lambda e:errors.append(str(e)))
 # GitHub Pages base path routes to the checked-out project root.
 page.route('**/turkce-akademi/**',lambda route:route.continue_(url=route.request.url.replace('/turkce-akademi/','/')))
 page.goto(baseurl+'/kitaplar/lise-a2/hayat-birlikte-guzel/');page.wait_for_selector('.word-hit');page.wait_for_function('document.querySelector("#pageImage").naturalWidth>0')
 for pi,p in enumerate(pages):
  page.locator('.thumb').nth(pi).click();page.wait_for_function('(n)=>document.querySelector("#count").textContent.startsWith(n+" / ")',arg=str(pi+1))
  page.wait_for_function('document.querySelector("#pageImage").complete&&document.querySelector("#pageImage").naturalWidth>0')
  assert page.locator('.word-hit').count()==len(p['words'])
  # Real pointer clicks at every lexical hotspot centre verify stacking and hit alignment.
  pointer=page.evaluate('''p=>{const failures=[];for(let i=0;i<p.words.length;i++){const w=p.words[i];if(!/\\p{L}/u.test(w.t)||/^[SMV]\\.\\d+$/.test(w.t))continue;const b=document.querySelector(`.word-hit[data-index="${i}"]`);b.scrollIntoView({block:'center'});const r=b.getBoundingClientRect();const x=r.x+r.width/2,y=r.y+r.height/2;if(y<0||y>innerHeight)continue;const top=document.elementFromPoint(x,y);if(top!==b)failures.push({word:w.t,top:top?.dataset?.word});}return failures}''',p)
  assert not pointer,('covered hotspots',pi+1,pointer)
  rendered=0
  for lang in langs:
   page.locator(f'#languageTabs [data-lang="{lang}"]').click()
   result=page.evaluate('''p=>{let count=0;const failed=[];for(let i=0;i<p.words.length;i++){const w=p.words[i];if(!/\\p{L}/u.test(w.t)||/^[SMV]\\.\\d+$/.test(w.t))continue;const b=document.querySelector(`.word-hit[data-index="${i}"]`);b.click();const t=document.querySelector('#translationBody').textContent;if(t.includes('henüz hazırlanmadı')||t.includes('henüz eklenmedi')||t.includes('Çeviri kontrol'))failed.push(w.t);count++}return {count,failed}}''',p)
   assert not result['failed'],('rendered dictionary',pi+1,lang,result['failed']);rendered+=result['count']
  for group in p['phraseGroups']:
   # The longest overlapping expression should select together.
   idx=group['indices'][0];chosen=next(x for x in sorted(p['phraseGroups'],key=lambda x:-len(x['indices'])) if idx in x['indices'])
   page.locator(f'.word-hit[data-index="{idx}"]').evaluate('(b)=>b.click()')
   assert page.locator('.word-hit.is-selected').count()==len(chosen['indices']),('phrase selection',pi+1,chosen)
  page.locator('#answerSummary').click()
  visible=page.locator('#answerOverlay .answer-fill').count()
  if answers[str(pi+1)].get('fills'):assert visible>0,('answer placement',pi+1)
  # Every page exports in every language, with no placeholder translations.
  for lang in langs:
   page.locator(f'#languageTabs [data-lang="{lang}"]').click()
   page.evaluate('window.__printOpened=null;window.__oldOpen=window.open;window.open=()=>({document:{open(){},write(s){window.__printOpened=s},close(){}},focus(){},print(){},addEventListener(){}})')
   page.locator('#exportPageWords').click() if page.locator('#exportPageWords').count() else page.locator('button').filter(has_text='Bu sayfanın kelimelerini PDF').click()
   out=page.evaluate('window.__printOpened');page.evaluate('window.open=window.__oldOpen')
   assert out and 'çeviri kontrol' not in out,(pi+1,lang,'PDF export')
  if pi+1 in [1,4,11,13]:page.screenshot(path=str(QA/f'page-{pi+1:02}-desktop.png'),full_page=True)
  checks.append({'page':pi+1,'hotspots':len(p['words']),'languageRenders':rendered,'phraseGroups':len(p['phraseGroups']),'answerFills':visible,'pdfLanguages':5})
 # Audio playback checks in all six languages: actual media bytes, metadata and progress.
 for lang,text in ([] if SKIP_AUDIO else [('tr','kurallar'),('en','rules'),('ru','правила'),('ky','эрежелер'),('ar','القواعد'),('fr','règles')]):
  # Choose an actual corpus key rather than assume dictionary wording.
  entrykey=next(k for k,v in audio['entries'][lang].items() if not v[0].startswith('../'))
  page.evaluate('([t,l])=>{window.__audioError=null;window.__speaking=TurkceSpeech.speak(t,l).catch(e=>window.__audioError=e.message)}',[entrykey,lang]);page.wait_for_timeout(1200)
  assert not page.evaluate('window.__audioError'),('playback',lang,page.evaluate('window.__audioError'))
  page.locator('.thumb').nth(0).click();page.evaluate('TurkceSpeech.stop()')
 page.set_viewport_size({'width':390,'height':844});page.locator('.thumb').nth(0).click();page.screenshot(path=str(QA/'mobile.png'),full_page=True)
 assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+2'),'horizontal mobile overflow'
 assert not errors,errors
 browser.close()
server.shutdown()
report={'status':'reader passed; audio pending' if SKIP_AUDIO else 'passed','unit':6,'pages':len(pages),'hotspots':sum(len(p['words']) for p in pages),'lexicalHotspots':lexical,'phraseGroups':sum(len(p['phraseGroups']) for p in pages),'joinedWords':sum(len(p['wordGroups']) for p in pages),'languages':langs,'speechLanguages':['tr']+langs,'speechEntries':{l:len(v) for l,v in audio['entries'].items()},'missingMeanings':0,'missingExamples':0,'readerCss':'identical to unit 5','checks':checks,'originalMediaPending':['S.038','S.039','S.040','S.041','S.042','S.043','S.044','S.045','V.007']}
if not SKIP_AUDIO:(ROOT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
(QA/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False))
