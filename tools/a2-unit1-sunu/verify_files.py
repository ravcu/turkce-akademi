from pathlib import Path
import os
from PIL import Image
import json,subprocess,hashlib,re,collections
R=Path(os.environ.get("A2_SUNU_WORK",Path(__file__).resolve().parents[3]/"a2-source"));repo=Path(os.environ.get("A2_SUNU_REPO",Path(__file__).resolve().parents[2]));root=repo/'kitaplar/lise-a2/tatil-donusu/sunum';slides=json.loads((root/'assets/slides.json').read_text())['slides'];rs=json.loads((R/'rendered.json').read_text());errors=[]
for r,s in zip(rs,slides):
 for f in ['image','answerImage']:
  if f in s:
   p=root/s[f]
   try:
    im=Image.open(p);im.load();assert im.size==(1921,1080)
    if f=='answerImage':assert im.mode=='RGBA' and im.getextrema()[3][0]==0
   except Exception as e:errors.append([str(p),str(e)])
 for a,p in zip(r['audio'],s.get('audio',[])):
  duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(root/p)]));expected=a['end']-a['start']
  if abs(duration-expected)>.12:errors.append([p,duration,expected])
base=(repo/'kitaplar/tanisalim/sunum/index.html').read_text();current=(root/'index.html').read_text();styles=lambda s:re.findall(r'<style[^>]*>(.*?)</style>',s,re.S);assert styles(base)==styles(current)[:-1]
assert 'A1 · TANIŞALIM' not in current;assert 'speech/player.js' in current;assert 'href="sunum/"' in (root.parent/'index.html').read_text()
spots=json.loads((root/'assets/word-spots.json').read_text());occluded=[]
for pi,hs in enumerate(spots,1):
 for i,h in enumerate(hs):
  if h.get('answer'):continue
  x=h['x']+h['w']/2;y=h['y']+h['h']/2
  for j,o in enumerate(hs[i+1:],i+1):
   if o.get('answer'):continue
   if o['x']<=x<=o['x']+max(o['w'],.003) and o['y']<=y<=o['y']+max(o['h'],.008):occluded.append([pi,i,j,h['key'],o['key']])
report={'slides':len(slides),'answerSlides':sum('answerImage' in s for s in slides),'audioClips':sum(len(s.get('audio',[])) for s in slides),'hotspots':sum(map(len,spots)),'cssMatchesA1':True,'occludedCentres':occluded,'errors':errors};(R/'file-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False));assert not errors
