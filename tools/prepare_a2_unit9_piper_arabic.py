"""Produce A2 unit 9 Arabic Piper speech, reusing unit 8 Piper recordings."""
import argparse, hashlib, json, os, re, subprocess, unicodedata, wave
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np

RATE = 22050
VOICE = None
CONFIG = None
CACHE = None

def clean(text):
    return re.sub(r'\s+', ' ', re.sub(r'(^|\s)[\-−–—]+(?=\s*\S)', r'\1', str(text))).strip()

def key(text):
    return re.sub(r'^[.!?,:;…\s]+|[.!?,:;…\s]+$', '', unicodedata.normalize('NFC', clean(text)).lower())

def init_worker(model, cache):
    global VOICE, CONFIG, CACHE
    import onnxruntime as ort
    from piper import PiperVoice, SynthesisConfig
    from piper.config import PiperConfig
    from piper.tashkeel import TashkeelDiacritizer, TASHKEEL_DIR
    options = ort.SessionOptions(); options.intra_op_num_threads = 1; options.inter_op_num_threads = 1
    VOICE = PiperVoice(session=ort.InferenceSession(str(model), sess_options=options, providers=['CPUExecutionProvider']), config=PiperConfig.from_dict(json.loads(Path(str(model)+'.json').read_text())))
    diacritizer = TashkeelDiacritizer()
    diacritizer.session = ort.InferenceSession(str(TASHKEEL_DIR/'model.onnx'), sess_options=options, providers=['CPUExecutionProvider'])
    VOICE.tashkeel_diacritizier = diacritizer
    CONFIG = SynthesisConfig(length_scale=1.08, noise_scale=.55, noise_w_scale=.7)
    CACHE = Path(cache)

def render(job):
    target = CACHE/job['wav']
    if not target.exists():
        temporary = target.with_suffix(f'.{os.getpid()}.tmp.wav')
        with wave.open(str(temporary), 'wb') as f: VOICE.synthesize_wav(job['spoken'], f, CONFIG)
        with wave.open(str(temporary)) as f:
            pcm = np.frombuffer(f.readframes(f.getnframes()), np.int16)
            assert f.getframerate()==RATE and f.getnchannels()==1 and len(pcm)>RATE*.05, (job['key'], 'empty')
            assert np.sqrt(np.mean(pcm.astype(float)**2))>8, (job['key'], 'silent')
        temporary.replace(target)
    return job

def run(args):
    root=args.repo_root/'kitaplar/lise-a2/bir-hikayem-var'; shared_root=args.repo_root/'kitaplar/lise-a2/spor-ve-saglik/speech'
    out=args.work_dir/'output';out.mkdir(parents=True, exist_ok=True)
    cache=args.cache_dir or args.work_dir/'cache';cache.mkdir(parents=True, exist_ok=True)
    old=json.loads((root/'speech/index.json').read_text()); glossary=json.loads((root/'translations.json').read_text())
    shared=json.loads((shared_root/'index.json').read_text())
    assert shared.get('languageEngines',{}).get('ar',{}).get('engine')=='Piper', 'Unit 8 must already use Piper'
    texts={}
    def add(t):
        if isinstance(t,str) and t.strip():texts[key(t)]=clean(t)
    def values(a):
        if isinstance(a,list) and len(a)>3:add(a[3])
    for a in glossary['words'].values():values(a)
    for f in glossary['forms'].values():
        for field in ['lemmaTranslations','formTranslations','examples']:values(f.get(field))
    for e in glossary['examples'].values():values(e[1] if isinstance(e,list) else e['values'])
    for f in glossary['phrases'].values():values(f['translations']);values(f['examples'])
    for k in old['entries']['ar']:texts.setdefault(k,k)
    model_sha=hashlib.sha256(args.model.read_bytes()).hexdigest()
    assert model_sha==shared['languageEngines']['ar']['modelSha256'], 'Use the same reviewed Piper model as unit 8'
    entries={}; jobs=[];manifest=[]
    for k,original in sorted(texts.items()):
        if k in shared['entries']['ar']:
            file,start,end=shared['entries']['ar'][k]
            entry=[os.path.relpath((shared_root/file).resolve(),(root/'speech').resolve()),start,end]
            entries[k]=entry;manifest.append(dict(key=k,original=original,reusedFrom='unit8',entry=entry))
        else:
            spoken=original.replace('/', '، ').replace(';','؛')
            digest=hashlib.sha256((model_sha+'|piper-ar-v1|'+spoken).encode()).hexdigest()[:20]
            job=dict(key=k,original=original,spoken=spoken,wav=digest+'.wav')
            jobs.append(job);manifest.append(job)
    print('CORPUS',len(texts),'REUSED',len(entries),'NEW',len(jobs),flush=True)
    with ProcessPoolExecutor(max_workers=args.workers, initializer=init_worker, initargs=(args.model,cache)) as pool:
        for i,_ in enumerate(pool.map(render,jobs),1):
            if i%100==0 or i==len(jobs):print('RENDER',i,'/',len(jobs),flush=True)
    (out/'arabic-piper-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    revision=hashlib.sha256(json.dumps(jobs,ensure_ascii=False,sort_keys=True).encode()).hexdigest()[:12]
    buffer=[];pending=[];frames=0;part=0;silence=np.zeros(round(RATE*.20),np.int16)
    def flush():
        nonlocal buffer,pending,frames,part
        if not pending:return
        name=f'ar-piper-{revision}-{part:04}.mp3';temporary=out/(name+'.tmp.mp3')
        subprocess.run(['ffmpeg','-v','error','-y','-f','s16le','-ar',str(RATE),'-ac','1','-i','pipe:0','-af','loudnorm=I=-18:TP=-1.5:LRA=9','-ar',str(RATE),'-c:a','libmp3lame','-b:a','64k',str(temporary)],input=np.concatenate(buffer).tobytes(),check=True)
        duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(temporary)]))
        for k,start,end in pending:
            assert 0<=start<end<=duration
            entries[k]=[name,round(start,4),round(end,4)]
        temporary.replace(out/name)
        buffer=[];pending=[];frames=0;part+=1
    for job in jobs:
        with wave.open(str(cache/job['wav'])) as f:
            assert f.getframerate()==RATE and f.getnchannels()==1
            pcm=np.frombuffer(f.readframes(f.getnframes()),np.int16)
        assert len(pcm)>RATE*.05 and np.sqrt(np.mean(pcm.astype(float)**2))>8
        if frames and frames+len(pcm)+2*len(silence)>RATE*120:flush()
        start=(frames+len(silence))/RATE;end=start+len(pcm)/RATE
        buffer.extend([silence,pcm,silence]);pending.append((job['key'],start,end));frames+=len(pcm)+2*len(silence)
    flush()
    assert set(old['entries']['ar'])<=set(entries)
    old['entries']['ar']=entries
    old['languageEngines']={**old.get('languageEngines',{}),'ar':dict(engine='Piper',voice='ar_JO-kareem-medium',modelSha256=model_sha,lengthScale=1.08,diacritization='Piper Tashkeel; shared unit 8 Piper clips retain reviewed overrides',fullText=True,reusedUnit8=len(entries)-len(jobs),newTexts=len(jobs))}
    (out/'index.json').write_text(json.dumps(old,ensure_ascii=False,separators=(',',':')))
    (out/'ar.json').write_text(json.dumps(dict(engine='Piper ar_JO-kareem-medium',entries=entries),ensure_ascii=False,separators=(',',':')))
    print('DONE',len(entries),'texts;',part,'new MP3 packs',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--work-dir',type=Path,required=True)
    p.add_argument('--model',type=Path,required=True);p.add_argument('--cache-dir',type=Path);p.add_argument('--workers',type=int,default=4)
    run(p.parse_args())
