"""Build same-language educational pronunciation from local speech models, without translation APIs."""
from pathlib import Path
import json,re,unicodedata,io,wave,os,subprocess,hashlib,math
from concurrent.futures import ProcessPoolExecutor
import numpy as np
ROOT=Path('kitaplar/lise-a2/hayat-birlikte-guzel');OUT=ROOT/'speech';MODELS=Path(os.environ.get('UNIT6_MODELS','/tmp/unit6-models'))
LANGS=['en','ru','ky','ar','fr'];RATE=22050
def clean(t):return re.sub(r'\s+',' ',re.sub(r'(^|\s)[\-−–—]+(?=\s*\S)',r'\1',str(t))).strip()
def key(t,lang):
 t=unicodedata.normalize('NFC',clean(t))
 if lang=='tr':t=t.replace('I','ı').replace('İ','i')
 return re.sub(r'^[.!?,:;…\s]+|[.!?,:;…\s]+$','',t.lower())
def corpus():
 g=json.loads((ROOT/'translations.json').read_text());pg=json.loads((ROOT/'pages.json').read_text());c={l:{} for l in ['tr']+LANGS}
 def add(l,t):
  if isinstance(t,str) and t.strip() and t.strip()!='—':c[l][key(t,l)]=clean(t)
 def meanings(a):
  if a:
   assert len(a)==5,a
   for l,t in zip(LANGS,a):add(l,t)
 def ex(tr,a):
  if tr and a and len(a)==5:add('tr',tr);meanings(a)
 for p in pg:
  for w in p['words']:add('tr',w['t'])
  for gr in p['wordGroups']+p['phraseGroups']:add('tr',gr['text'])
 for k,a in g['words'].items():add('tr',k);meanings(a)
 for k,f in g['forms'].items():add('tr',k);add('tr',f.get('lemma',''));meanings(f.get('lemmaTranslations'));meanings(f.get('formTranslations'));ex(f.get('exampleTr'),f.get('examples'))
 for k,f in g['phrases'].items():add('tr',k);meanings(f['translations']);ex(f.get('exampleTr'),f.get('examples'))
 for e in g['examples'].values():
  if isinstance(e,list):ex(*e)
  else:ex(e.get('tr'),e.get('values'))
 small='zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split();tens=['','','twenty','thirty','forty','fifty','sixty','seventy','eighty','ninety']
 def en(n):
  if n<20:return small[n]
  if n<100:return tens[n//10]+('-'+small[n%10] if n%10 else '')
  if n<1000:return small[n//100]+' hundred'+(' '+en(n%100) if n%100 else '')
  return str(n)
 for p in pg:
  for w in p['words']:
   n=re.sub(r'\D','',w['t'])
   if n and re.fullmatch(r'[\d.]+',w['t']):
    add('en',en(int(n)))
    for l in ['ru','ky','ar','fr']:add(l,n)
 return c

def build(item):
 lang,data=item
 import onnxruntime as ort
 from piper import PiperVoice
 original_options=ort.SessionOptions
 def options():
  o=original_options();o.intra_op_num_threads=1;o.inter_op_num_threads=1;return o
 ort.SessionOptions=options
 model=MODELS/('tr_TR-dfki-medium.onnx' if lang=='tr' else lang+'.onnx')
 voice=None if lang=='ky' else PiperVoice.load(model)
 shared=json.loads(Path('assets/speech-20261013/index.json').read_text()).get('entries',{}).get(lang,{})
 entries={};todo=[];reuse=0
 for k,t in sorted(data.items()):
  if k in shared:
   old=shared[k];entries[k]=['../../../../assets/speech-20261013/'+old[0],old[1],old[2]];reuse+=1
  else:todo.append((k,t))
 part=0;frames=0;buffer=[];silence=np.zeros(int(RATE*.18),dtype=np.int16);pending=[]
 def flush():
  nonlocal part,frames,buffer,pending
  if not pending:return
  filename=f'{lang}-{part:03}.mp3';pcm=np.concatenate(buffer)
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','s16le','-ar',str(RATE),'-ac','1','-i','pipe:0','-codec:a','libmp3lame','-b:a','48k',str(OUT/filename)],input=pcm.tobytes(),check=True)
  for k,s,e in pending:entries[k]=[filename,round(s,4),round(e,4)]
  part+=1;frames=0;buffer=[];pending=[]
 for i,(k,text) in enumerate(todo):
  # Read a concise dictionary equivalent, omitting grammatical parentheticals.
  spoken=re.sub(r'\([^)]*\)','',text).split(';')[0].strip() or text
  if lang=='tr':spoken=spoken.replace('havalanına','havaalanına').replace('Birtane','Bir tane').replace('birtane','bir tane')
  stream=io.BytesIO()
  if lang=='ky':
   env=os.environ.copy()
   result=subprocess.run(['espeak-ng','-v','ky','-s','145','--stdout','--stdin'],input=spoken.encode(),stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,env=env,check=True)
   stream=io.BytesIO(result.stdout)
  else:
   with wave.open(stream,'wb') as wav:voice.synthesize_wav(spoken,wav)
   stream.seek(0)
  with wave.open(stream,'rb') as wav:
   rate=wav.getframerate();a=np.frombuffer(wav.readframes(wav.getnframes()),dtype=np.int16)
  if rate!=RATE:
   from scipy.signal import resample_poly
   common=math.gcd(rate,RATE);a=resample_poly(a.astype(float),RATE//common,rate//common).clip(-32768,32767).astype(np.int16)
  if len(a)<RATE*.06 or np.sqrt(np.mean(a.astype(float)**2))<8:raise ValueError((lang,k,'silent audio'))
  buffer.extend([silence,a,silence]);start=(frames+len(silence))/RATE;end=(frames+len(silence)+len(a))/RATE;pending.append((k,start,end));frames+=len(a)+2*len(silence)
  if frames>RATE*180:flush()
  if i%100==0:print(lang,i,'/',len(todo),flush=True)
 flush()
 result={'sourceSha':hashlib.sha256((ROOT/'translations.json').read_bytes()+(ROOT/'pages.json').read_bytes()).hexdigest(),'lang':lang,'entries':entries,'generated':len(todo),'reused':reuse,'model':'eSpeak NG Kyrgyz' if lang=='ky' else model.name}
 (OUT/(lang+'.json')).write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')))
 print(lang,'DONE',len(entries),flush=True)
 return result
if __name__=='__main__':
 import argparse,urllib.request
 parser=argparse.ArgumentParser();parser.add_argument('--language',choices=['tr']+LANGS,required=True);args=parser.parse_args()
 OUT.mkdir(exist_ok=True);MODELS.mkdir(exist_ok=True)
 paths={'tr':'tr/tr_TR/dfki/medium/tr_TR-dfki-medium','en':'en/en_US/amy/medium/en_US-amy-medium','ru':'ru/ru_RU/ruslan/medium/ru_RU-ruslan-medium','ar':'ar/ar_JO/kareem/medium/ar_JO-kareem-medium','fr':'fr/fr_FR/siwis/medium/fr_FR-siwis-medium'}
 if args.language!='ky':
  stem='tr_TR-dfki-medium' if args.language=='tr' else args.language
  for ext in ['.onnx.json','.onnx']:
   dest=MODELS/(stem+ext)
   if not dest.exists():urllib.request.urlretrieve('https://huggingface.co/rhasspy/piper-voices/resolve/main/'+paths[args.language]+ext,dest)
 c=corpus();print({l:len(v) for l,v in c.items()},flush=True);build((args.language,c[args.language]))
