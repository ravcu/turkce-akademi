"""Regenerate all A2 unit 8 Arabic speech using local Piper, with checkpoints."""
import hashlib, json, re, subprocess, unicodedata, wave
from pathlib import Path
import numpy as np
import onnxruntime as ort
from piper import PiperVoice, SynthesisConfig
from piper.config import PiperConfig
from piper.tashkeel import TashkeelDiacritizer, TASHKEEL_DIR

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[1])
parser.add_argument('--model', type=Path, required=True, help='ar_JO-kareem-medium.onnx, with adjacent .onnx.json')
parser.add_argument('--work-dir', type=Path, required=True, help='Checkpoint directory outside published files')
args = parser.parse_args()
ROOT = args.repo_root / 'kitaplar/lise-a2/spor-ve-saglik'
MODEL = args.model
CACHE = args.work_dir / 'arabic-cache'
OUT = args.work_dir / 'arabic-production'
RATE = 22050

def clean(t):
    return re.sub(r'\s+', ' ', re.sub(r'(^|\s)[\-−–—]+(?=\s*\S)', r'\1', str(t))).strip()

def key(t):
    return re.sub(r'^[.!?,:;…\s]+|[.!?,:;…\s]+$', '', unicodedata.normalize('NFC', clean(t)).lower())

def run():
    CACHE.mkdir(parents=True, exist_ok=True); OUT.mkdir(parents=True, exist_ok=True)
    old = json.loads((ROOT / 'speech/index.json').read_text())
    glossary = json.loads((ROOT / 'translations.json').read_text())
    texts = {}
    def add(t):
        if isinstance(t, str) and t.strip(): texts[key(t)] = clean(t)
    def values(a):
        if isinstance(a, list) and len(a) > 3: add(a[3])
    for a in glossary['words'].values(): values(a)
    for f in glossary['forms'].values():
        for field in ['lemmaTranslations', 'formTranslations', 'examples']: values(f.get(field))
    for e in glossary['examples'].values(): values(e[1] if isinstance(e, list) else e['values'])
    for f in glossary['phrases'].values():
        values(f['translations']); values(f['examples'])
    required = old['entries']['ar']
    for k in required: texts.setdefault(k, k)
    overrides = {key(s['originalText']): s['spokenText'] for s in json.loads((ROOT / 'arabic-review/samples.json').read_text())}
    options = ort.SessionOptions(); options.intra_op_num_threads = 2; options.inter_op_num_threads = 1
    voice = PiperVoice(session=ort.InferenceSession(str(MODEL), sess_options=options, providers=['CPUExecutionProvider']), config=PiperConfig.from_dict(json.loads(Path(str(MODEL) + '.json').read_text())))
    diacritizer = TashkeelDiacritizer()
    diacritizer.session = ort.InferenceSession(str(TASHKEEL_DIR / 'model.onnx'), sess_options=options, providers=['CPUExecutionProvider'])
    voice.tashkeel_diacritizier = diacritizer
    config = SynthesisConfig(length_scale=1.08, noise_scale=.55, noise_w_scale=.7)
    manifest = []
    model_sha = hashlib.sha256(MODEL.read_bytes()).hexdigest()
    for i, (k, original) in enumerate(sorted(texts.items())):
        spoken = overrides.get(k, original).replace('/', '، ').replace(';', '؛')
        # Manual overrides retain their reviewed marks; other text gets Piper's tashkeel.
        voice.use_tashkeel = k not in overrides
        digest = hashlib.sha256((model_sha + '|piper-ar-v1|' + spoken).encode()).hexdigest()[:20]
        target = CACHE / (digest + '.wav')
        if not target.exists():
            tmp = target.with_suffix('.tmp.wav')
            with wave.open(str(tmp), 'wb') as f: voice.synthesize_wav(spoken, f, config)
            with wave.open(str(tmp)) as f:
                pcm = np.frombuffer(f.readframes(f.getnframes()), np.int16)
                assert f.getframerate() == RATE and len(pcm) > RATE * .05, (k, 'empty')
                assert np.sqrt(np.mean(pcm.astype(float) ** 2)) > 8, (k, 'silent')
            tmp.replace(target)
        manifest.append(dict(key=k, original=original, spoken=spoken, wav=target.name))
        if i % 100 == 0: print(f'RENDER {i}/{len(texts)}', flush=True)
    (OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    entries = {}; buffer = []; pending = []; frames = 0; part = 0
    silence = np.zeros(round(RATE * .20), dtype=np.int16)
    revision = hashlib.sha256(json.dumps(manifest, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:12]
    def flush():
        nonlocal buffer, pending, frames, part
        if not pending: return
        name = f'ar-piper-{revision}-{part:04}.mp3'
        subprocess.run(['ffmpeg','-v','error','-y','-f','s16le','-ar',str(RATE),'-ac','1','-i','pipe:0','-af','loudnorm=I=-18:TP=-1.5:LRA=9','-ar',str(RATE),'-c:a','libmp3lame','-b:a','64k',str(OUT/name)], input=np.concatenate(buffer).tobytes(), check=True)
        duration = float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(OUT/name)]))
        for k, start, end in pending:
            assert 0 <= start < end <= duration
            entries[k] = [name, round(start, 4), round(end, 4)]
        buffer = []; pending = []; frames = 0; part += 1
    for item in manifest:
        with wave.open(str(CACHE/item['wav'])) as f: pcm = np.frombuffer(f.readframes(f.getnframes()), np.int16)
        if frames and frames + len(pcm) + 2 * len(silence) > RATE * 120: flush()
        start = (frames + len(silence))/RATE; end = start + len(pcm)/RATE
        buffer.extend([silence, pcm, silence]); pending.append((item['key'], start, end)); frames += len(pcm) + 2 * len(silence)
    flush()
    assert set(required) <= set(entries)
    old['entries']['ar'] = entries
    old['languageEngines'] = {**old.get('languageEngines', {}), 'ar': dict(engine='Piper', voice='ar_JO-kareem-medium', modelSha256=model_sha, lengthScale=1.08, diacritization='Piper tashkeel with reviewed sample overrides', fullText=True)}
    (OUT/'index.json').write_text(json.dumps(old, ensure_ascii=False, separators=(',', ':')))
    (OUT/'ar.json').write_text(json.dumps(dict(engine='Piper ar_JO-kareem-medium', entries=entries), ensure_ascii=False, separators=(',', ':')))
    print('DONE', len(entries), 'Arabic texts;', part, 'MP3 packs', flush=True)

if __name__ == '__main__': run()
