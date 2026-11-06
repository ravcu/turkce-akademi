"""Encode numbered A2 grammar WAV files and merge the public audio manifest.
Dependencies: ffmpeg, ffprobe, numpy, scipy.
Usage: python3 tools/prepare_a2_grammar_audio.py INPUT_DIRECTORY [--workers 4]
"""
import argparse, hashlib, json, re, subprocess, warnings
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from scipy.io import wavfile

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('source',type=Path)
parser.add_argument('--output',type=Path,default=Path('sesler/Lise-A2-Dilbilgisi-ve-Telaffuz'))
parser.add_argument('--workers',type=int,default=4)
a=parser.parse_args();a.output.mkdir(parents=True,exist_ok=True)
manifest_path=a.output/'manifest.json'
old=json.loads(manifest_path.read_text()) if manifest_path.exists() else {'tracks':{}}
inputs=[];seen=set()
for p in sorted(a.source.glob('*.wav')):
 match=re.search(r'Dil[ -]+Bilgisi[ -]+(\d+)(?:[.-](\d+))?\.wav$',p.name,re.I)
 if not match:continue
 number=int(match[1]);extra=match[2];code=f'S.{number:03d}'+('.'+extra if extra else '')
 if code in seen:raise ValueError(f'Duplicate recording code: {code}')
 seen.add(code);inputs.append((p,number,extra,code))
if not inputs:raise ValueError('No numbered grammar WAV recordings found')

def encode(item):
 p,number,extra,code=item
 with warnings.catch_warnings():
  warnings.simplefilter('ignore',wavfile.WavFileWarning);rate,pcm=wavfile.read(p)
 mono=pcm.ndim==1 or (pcm.shape[1]==2 and np.array_equal(pcm[:,0],pcm[:,1]))
 duration=len(pcm)/rate
 suffix=str(number)+('-'+extra if extra else '')
 target=a.output/f'Lise - A2 - Dil Bilgisi - {suffix}.opus'
 bitrate='48k' if mono else '64k'
 cmd=['ffmpeg','-nostdin','-v','error','-y','-i',str(p),'-map','0:a:0','-map_metadata','-1']
 if pcm.ndim==2 and mono:cmd+=['-af','pan=mono|c0=c0']
 cmd+=['-ar','48000','-c:a','libopus','-b:a',bitrate,'-vbr','on','-compression_level','10','-application','audio','-frame_duration','20','-metadata',f'title=Lise A2 Dil Bilgisi ve Telaffuz - {code}',str(target)]
 subprocess.run(cmd,check=True)
 subprocess.run(['ffmpeg','-nostdin','-v','error','-i',str(target),'-f','null','-'],check=True)
 info=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','a:0','-show_entries','stream=codec_name,sample_rate,channels:format=duration','-of','json',str(target)]))
 stream=info['streams'][0];encoded=float(info['format']['duration'])
 if abs(encoded-duration)>.03:raise ValueError(f'Duration mismatch: {code}')
 if stream['codec_name']!='opus' or int(stream['sample_rate'])!=48000:raise ValueError(f'Invalid encoding: {code}')
 row={'number':number,'code':code,'file':target.name,'bytes':target.stat().st_size,'sourceBytes':p.stat().st_size,'duration':duration,'encodedDuration':encoded,'channels':stream['channels'],'targetBitrate':bitrate,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
 print(code,target.stat().st_size,flush=True);return code,row

with ThreadPoolExecutor(max_workers=a.workers) as executor:
 for code,row in executor.map(encode,inputs):old['tracks'][code]=row
tracks=dict(sorted(old['tracks'].items(),key=lambda item:[int(x) for x in item[0][2:].split('.')]))
result={'version':1,'codec':'opus','sampleRate':48000,'tracks':tracks,'sourceBytes':sum(t['sourceBytes'] for t in tracks.values()),'encodedBytes':sum(t['bytes'] for t in tracks.values()),'durationSeconds':sum(t['duration'] for t in tracks.values())}
temporary=manifest_path.with_suffix('.json.tmp');temporary.write_text(json.dumps(result,ensure_ascii=False,indent=2));temporary.replace(manifest_path)
print(f'Complete: {len(tracks)} recordings, {result["encodedBytes"]} bytes')
