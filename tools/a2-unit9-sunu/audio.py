"""Publish exactly the embedded PPTX trim ranges, never a restarted full recording."""
from pathlib import Path
import json,subprocess
ROOT=Path(__file__).resolve().parents[2];W=ROOT.parent/'work9';O=ROOT/'kitaplar/lise-a2/bir-hikayem-var/sunum/audio';O.mkdir(parents=True,exist_ok=True)
rows=json.loads((W/'source-objects.json').read_text());segments={}
for row in rows:
 for a in row['audio']:
  key=(a['sha256'],a['start'],a['end'])
  if key not in segments:
   name=f'segment-{len(segments)+1:03}.mp3';out=O/name
   if not out.exists():subprocess.run(['ffmpeg','-v','error','-y','-ss',str(a['start']),'-i',a['file'],'-t',str(a['end']-a['start']),'-vn','-c:a','libmp3lame','-b:a','96k',str(out)],check=True)
   duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(out)]));assert abs(duration-(a['end']-a['start']))<.12
   segments[key]={'src':'audio/'+name,'sourceStart':a['start'],'sourceEnd':a['end'],'sourceMediaSha256':a['sha256'],'publishedDuration':duration}
  a['published']=segments[key]
(W/'source-objects.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');print({'audioUses':sum(len(r['audio']) for r in rows),'uniqueSegments':len(segments)})
