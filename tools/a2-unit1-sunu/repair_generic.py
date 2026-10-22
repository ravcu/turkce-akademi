from pathlib import Path
import os
import json,subprocess,wave,io,os,importlib.util
import numpy as np
repo=Path.cwd();R=repo.parent/'a2-source';OUT=repo/'kitaplar/lise-a2/tatil-donusu/sunum/speech';idx=json.loads((OUT/'index.json').read_text());errors=json.loads((R/'generic-audio-check.json').read_text())['errors']
sp=importlib.util.spec_from_file_location('builder',R/'speech_builder.py');b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b)
for file,maximum,duration in errors:
 lang=file.split('-')[0];rows=[(k,s,e) for k,(f,s,e) in idx['entries'][lang].items() if f==file];pcm=np.zeros(round((maximum+.2)*b.RATE),np.int16);env=os.environ.copy();env['LD_LIBRARY_PATH']=str(b.RUNTIME/'usr/lib/x86_64-linux-gnu')
 for k,start,end in sorted(rows,key=lambda row:row[1]):
  text=b.corpus[lang][k];spoken=b.re.sub(r'\([^)]*\)','',text).split(';')[0].strip() or text
  data=subprocess.check_output([str(b.RUNTIME/'usr/bin/espeak-ng'),'--path='+str(b.RUNTIME/'usr/lib/x86_64-linux-gnu'),'-v',lang,'-s','145','--stdout','--stdin'],input=(spoken+'.').encode(),stderr=subprocess.DEVNULL,env=env)
  with wave.open(io.BytesIO(data)) as f:a=np.frombuffer(f.readframes(f.getnframes()),np.int16)
  assert abs(len(a)/b.RATE-(end-start))<.002,(k,len(a)/b.RATE,end-start)
  i=round(start*b.RATE);pcm[i:i+len(a)]=a
 tmp=OUT/(file+'.repair.mp3');subprocess.run(['ffmpeg','-v','error','-y','-f','s16le','-ar',str(b.RATE),'-ac','1','-i','pipe:0','-c:a','libmp3lame','-b:a','48k',str(tmp)],input=pcm.tobytes(),check=True);actual=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(tmp)]));assert actual>=maximum;tmp.replace(OUT/file);print('repaired',file,'utterances',len(rows),'duration',actual)
