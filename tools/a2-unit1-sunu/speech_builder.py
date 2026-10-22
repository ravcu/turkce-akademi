"""Render same-language local speech, without translation or remote TTS APIs."""
from pathlib import Path
import os
import json,re,unicodedata,os,subprocess,io,wave,hashlib
from concurrent.futures import ThreadPoolExecutor
import numpy as np
ROOT=Path('kitaplar/lise-a2/tatil-donusu/sunum');OUT=ROOT/'speech';OUT.mkdir(exist_ok=True)
LANGS=['en','ru','ky','ar','fr'];RATE=22050
RUNTIME=Path('../speech-runtime/local').resolve()
def clean(t):return re.sub(r'\s+',' ',re.sub(r'(^|\s)[\-−–—]+(?=\s*\S)',r'\1',str(t))).strip()
def key(t,l):
 t=unicodedata.normalize('NFC',clean(t))
 if l=='tr':t=t.replace('I','ı').replace('İ','i')
 return re.sub(r'^[.!?,:;…\s]+|[.!?,:;…\s]+$','',t.lower())
g=json.loads((ROOT/'assets/translations.json').read_text());spots=json.loads((ROOT/'assets/word-spots.json').read_text());corpus={l:{} for l in ['tr']+LANGS}
def add(l,t):
 if isinstance(t,str) and t.strip():corpus[l][key(t,l)]=clean(t)
def values(a):
 if isinstance(a,list):
  for l,t in zip(LANGS,a):add(l,t)
for hs in spots:
 for h in hs:add('tr',h['key']);add('tr',h['text'])
for k,a in g['words'].items():add('tr',k);values(a)
for k,f in g['forms'].items():
 add('tr',f['lemma']);values(f.get('lemmaTranslations'));values(f.get('formTranslations'));add('tr',f.get('exampleTr'));values(f.get('examples'))
for k,e in g['examples'].items():add('tr',e[0]);values(e[1])
for k,f in g['phrases'].items():add('tr',k);values(f['translations']);add('tr',f.get('exampleTr'));values(f.get('examples'))
sourcehash=hashlib.sha256((ROOT/'assets/translations.json').read_bytes()+(ROOT/'assets/word-spots.json').read_bytes()).hexdigest()
shared={l:{} for l in ['tr']+LANGS}
for indexpath in sorted(Path('kitaplar/lise-a2').glob('*/speech/index.json')):
 if indexpath.parent.parent==ROOT:continue
 for l,items in json.loads(indexpath.read_text()).get('entries',{}).items():
  for k,(file,start,end) in items.items():
   shared.setdefault(l,{})[k]=[os.path.relpath((indexpath.parent/file).resolve(),OUT.resolve()),start,end]
def render(item):
 l,data=item;entries={};frames=0;part=0;buffer=[];pending=[];silence=np.zeros(int(RATE*.18),np.int16)
 cachedfile=OUT/(l+'.json')
 if cachedfile.exists():
  previous=json.loads(cachedfile.read_text());entries={k:v for k,v in previous.get('entries',{}).items() if k in data}
 todo=[]
 for k,t in data.items():
  if k in entries:continue
  if k in shared.get(l,{}):
   file,start,end=shared[l][k];entries[k]=[file,start,end]
  else:todo.append((k,t))
 revision=hashlib.sha256(json.dumps(sorted(todo),ensure_ascii=False).encode()).hexdigest()[:8]
 env=os.environ.copy();env['LD_LIBRARY_PATH']=str(RUNTIME/'usr/lib/x86_64-linux-gnu')
 if l=='ar':return l,entries  # Arabic additions are rendered by the Piper builder below.
 def flush():
  nonlocal frames,part,buffer,pending
  if not pending:return
  name=f'{l}-{sourcehash[:8]}-{revision}-{part:03}.mp3';pcm=np.concatenate(buffer)
  temporary=OUT/(name+'.tmp.mp3')
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','s16le','-ar',str(RATE),'-ac','1','-i','pipe:0','-codec:a','libmp3lame','-b:a','48k',str(temporary)],input=pcm.tobytes(),check=True)
  temporary.replace(OUT/name)
  for k,s,e in pending:entries[k]=[name,round(s,4),round(e,4)]
  frames=0;part+=1;buffer=[];pending=[]
 for i,(k,t) in enumerate(sorted(todo)):
  spoken=re.sub(r'\([^)]*\)','',t).split(';')[0].strip() or t
  r=subprocess.run([str(RUNTIME/'usr/bin/espeak-ng'),'--path='+str(RUNTIME/'usr/lib/x86_64-linux-gnu'),'-v',l,'-s','145','--stdout','--stdin'],input=(spoken+'.').encode(),stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,env=env,check=True)
  with wave.open(io.BytesIO(r.stdout),'rb') as wav:
   assert wav.getframerate()==RATE
   a=np.frombuffer(wav.readframes(wav.getnframes()),np.int16)
  if len(a)<=RATE*.04 or np.sqrt(np.mean(a.astype(float)**2))<=8:
   # Pure abbreviations enclosed in parentheses have no spoken remainder.
   spoken=' '.join(re.findall(r'\w+',t))
   prefixes={'tr':'kod','en':'code','ru':'код','ky':'код','ar':'الرمز','fr':'code'}
   r=subprocess.run([str(RUNTIME/'usr/bin/espeak-ng'),'--path='+str(RUNTIME/'usr/lib/x86_64-linux-gnu'),'-v',l,'-s','145','--stdout','--stdin'],input=(prefixes[l]+' '+spoken+'.').encode(),stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,env=env,check=True)
   with wave.open(io.BytesIO(r.stdout),'rb') as wav:a=np.frombuffer(wav.readframes(wav.getnframes()),np.int16)
  assert len(a)>RATE*.04 and np.sqrt(np.mean(a.astype(float)**2))>8,(l,k,'silent')
  buffer.extend([silence,a,silence]);start=(frames+len(silence))/RATE;end=start+len(a)/RATE
  pending.append((k,start,end));frames+=len(a)+2*len(silence)
  if frames>RATE*180:flush()
  if i%300==0:print(l,i,'/',len(todo),flush=True)
 flush();cachedfile.write_text(json.dumps({'sourceSha':sourcehash,'entries':entries},ensure_ascii=False,separators=(',',':')));return l,entries
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=6) as pool:entries=dict(pool.map(render,corpus.items()))
 metadata=json.loads((OUT/'index.json').read_text()).get('languageEngines',{}) if (OUT/'index.json').exists() else {}
 (OUT/'index.json').write_text(json.dumps({'sourceSha':sourcehash,'engine':'eSpeak NG 1.51, local synthesis; Arabic Piper','languageEngines':metadata,'entries':entries},ensure_ascii=False,separators=(',',':')))
 print('DONE',{l:len(x) for l,x in entries.items()},flush=True)
