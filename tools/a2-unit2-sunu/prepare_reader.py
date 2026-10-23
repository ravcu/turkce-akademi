from pathlib import Path
from lxml import etree as E
import json,re,copy
root=Path('repo/kitaplar/lise-a2/hafta-sonu-planin-ne/sunum');slides=json.loads((root/'slides.json').read_text());recs=json.loads(Path('rebuild/source-objects.json').read_text());tracks=json.loads(Path('rebuild/native-tracks.json').read_text());N={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
spots=json.loads((root/'word-spots.json').read_text());answerboxes={}
for s,rec,row in zip(slides['slides'],recs,spots):
 seq=rec['sequence'];assert s['sequence']==seq and s['sourceSlide']==rec['sourceSlide']
 s['image']=f'native-v2/slides/{seq:03}.webp';s.pop('answersEmbedded',None);s.pop('answerImage',None);s.pop('audio',None);s.pop('audioSegments',None)
 if rec['hasAnswers']:s['answerImage']=f'native-v2/answers/{seq:03}.webp'
 s['sourcePart']=rec['part'];s['sourcePartSlide']=rec['localSlide'];s['imageWidth']=2400;s['imageHeight']=1350
 media=[t for t in tracks if t['sequence']==seq]
 for t in media:
  if t['kind']=='video':s['video']=t['publishedFile'];continue
  s.setdefault('audio',[]).append(t['publishedFile']);s.setdefault('audioSegments',[]).append({'src':t['publishedFile'],'sourceStart':t['start'],'sourceEnd':t['end'],'sourceMediaSha256':t['sha'],'timingBasis':'Native PowerPoint p14:trim start and end values; file duration minus end trim'})
 boxes=[]
 for obj in rec['removedAnswerShapes']:
  x=E.fromstring(obj['xml'].encode()).find('.//a:xfrm',N)
  if x is None:continue
  off=x.find('a:off',N);ext=x.find('a:ext',N)
  if off is not None and ext is not None:boxes.append([int(off.get('x'))/12192000,int(off.get('y'))/6858000,int(ext.get('cx'))/12192000,int(ext.get('cy'))/6858000])
 answerboxes[seq]=boxes
 for w in row:
  cx=w['x']+w['w']/2;cy=w['y']+w['h']/2
  w['answer']=any(x-.001<=cx<=x+ww+.001 and y-.002<=cy<=y+hh+.002 for x,y,ww,hh in boxes)
 # Remove obsolete hotspots in deleted English table areas.
 if seq==81:row[:]=[w for w in row if w['y']<.60]
(root/'slides.json').write_text(json.dumps(slides,ensure_ascii=False,indent=2));(root/'word-spots.json').write_text(json.dumps(spots,ensure_ascii=False,indent=2));Path('rebuild/answer-boxes.json').write_text(json.dumps(answerboxes))
html=Path('rebuild/reader-before-native.html').read_text();template=Path('repo/kitaplar/lise-a2/tatil-donusu/sunum/index.html').read_text();start=template.index('  function renderAnswers(){');end=template.index('  function showEntry(hit){',start);fun=template[start:end];start=html.index('  function renderAnswers(){');end=html.index('  function showEntry(hit){',start);html=html[:start]+fun+html[end:]
html=html.replace('original-restore-1','ppt-native-v2').replace("fetch('translations.json')","fetch('translations.json?v=ppt-native-v2')")
# The English labels on slide 78 are baked into the original single picture.
# Retain native CSS masks for these labels; slide 81's tables are removed natively.
html=html.replace(",81:[[0,.608,1,.392,'white'],[.772,0,.065,.127,'white']]",'')
# Embedded video gets a separate player; it does not restart the lesson audio.
html=html.replace('<button class="listen toolbar-listen" id="toolbarListen" hidden>▶ DİNLE</button>','<button class="listen toolbar-listen" id="toolbarListen" hidden>▶ DİNLE</button><button class="listen toolbar-listen" id="toolbarVideo" hidden>▶ VİDEO</button>')
html=html.replace('<div class="toast" id="toast" role="status"></div>','<dialog id="videoDialog" style="width:min(960px,94vw);border:0;border-radius:14px;padding:12px;background:#fffefa"><button id="closeVideo" type="button" class="plain-btn" style="float:right;margin-bottom:8px">Kapat ×</button><video id="videoPlayer" controls playsinline preload="metadata" style="display:block;width:100%;max-height:80vh"></video></dialog><div class="toast" id="toast" role="status"></div>')
html=html.replace('renderAudio(s.audio);renderAnswers();','renderAudio(s.audio);renderVideo(s.video);renderAnswers();')
html=html.replace("function stopAudio(){const lessonPanel", "function stopAudio(){const video=document.getElementById('videoPlayer');if(video)video.pause();const dialog=document.getElementById('videoDialog');if(dialog?.open)dialog.close();const lessonPanel")
needle='  const speechLanguages='
func='''  function renderVideo(src){const b=document.getElementById('toolbarVideo');b.hidden=!src;b.onclick=()=>{stopAudio();const d=document.getElementById('videoDialog'),v=document.getElementById('videoPlayer');v.src=src;d.showModal();v.play().catch(()=>{})};document.getElementById('closeVideo').onclick=()=>{document.getElementById('videoPlayer').pause();document.getElementById('videoDialog').close()};document.getElementById('videoDialog').oncancel=()=>document.getElementById('videoPlayer').pause()}
'''
html=html.replace(needle,func+needle)
(root/'index.html').write_text(html)
# Add previously available non-generic examples without changing meanings.
dictpath=root/'translations.json';d=json.loads(dictpath.read_text());extras=json.loads(Path('extra-examples.json').read_text());d['examples'].update(extras);dictpath.write_text(json.dumps(d,ensure_ascii=False,indent=2))
keys={w['key'] for row in spots for w in row};noex=[k for k in keys if not d.get('examples',{}).get(k) and not d.get('forms',{}).get(k,{}).get('exampleTr') and not d.get('phrases',{}).get(k,{}).get('exampleTr')]
print('Reader prepared',len(slides['slides']),'answer hotspots',sum(bool(w.get('answer')) for row in spots for w in row),'examples missing',len(noex))
