"""Atomically export each exact native trim and validate decoded MP3 duration."""
from pathlib import Path
import json,subprocess,os
R=Path(__file__).resolve().parents[2];W=R.parent/'rebuild';O=R/'kitaplar/lise-a2/bir-gunum/sunum';S=json.loads((O/'assets/slides.json').read_text());source=json.loads((W/'source-objects.json').read_text())
for s in S['slides']:
 r=next(r for r in source if r['part']==s['sourcePart'] and r['localSlide']==s['sourcePartSlide'])
 for a,native in zip(s.get('audioSegments',[]),r['audio']):
  target=O/a['src'];temp=W/(target.stem+'.validated.mp3');length=native['end']-native['start']
  subprocess.run(['ffmpeg','-v','error','-y','-ss',str(native['start']),'-i',native['file'],'-t',str(length),'-vn','-c:a','libmp3lame','-b:a','128k',str(temp)],check=True)
  actual=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(temp)]));assert abs(actual-length)<.12,(s['sequence'],actual,length)
  os.replace(temp,target);a['publishedDuration']=actual
(O/'assets/slides.json').write_text(json.dumps(S,ensure_ascii=False,indent=2));print('Validated',sum(len(s.get('audio',[])) for s in S['slides']),'native segments',flush=True)
