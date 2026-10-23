import json,subprocess,shutil
from pathlib import Path
root=Path('repo/kitaplar/lise-a2/hafta-sonu-planin-ne/sunum');audio=root/'native-v2/audio';audio.mkdir(parents=True,exist_ok=True);video=root/'native-v2/video';video.mkdir(parents=True,exist_ok=True)
rows=json.loads(Path('rebuild/audio-source-audit.json').read_text())['rows'];tracks={}
for r in rows:
 seq=r['sequence'];n=tracks.get(seq,0)+1;tracks[seq]=n
 if r['ext']=='.mp4':
  r['publishedFile']=f'native-v2/video/{seq:03}.mp4';shutil.copyfile(r['localSource'],root/r['publishedFile']);r['kind']='video';continue
 name=f'native-v2/audio/{seq:03}-{n}.mp3';r['publishedFile']=name;r['kind']='audio'
 subprocess.run(['ffmpeg','-loglevel','error','-y','-ss',str(r['start']),'-i',r['localSource'],'-t',str(r['end']-r['start']),'-c:a','libmp3lame','-q:a','3',str(root/name)],check=True)
 duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(root/name)]));assert abs(duration-(r['end']-r['start']))<.10
 r['publishedDuration']=duration
Path('rebuild/native-tracks.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));print('Native cuts saved',len(rows))
