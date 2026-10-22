/* A1-style device voices with same-language recorded fallbacks; no paid API. */
(() => {
  'use strict';
  const base=new URL('.',document.currentScript.src);
  const names={tr:'Türkçe',en:'İngilizce',ru:'Rusça',ky:'Kırgızca',ar:'Arapça',fr:'Fransızca'};
  const clean=t=>String(t??'').normalize('NFC').replace(/(^|\s)[\-−–—]+(?=\s*\S)/g,'$1').replace(/\s+/g,' ').trim();
  const key=(t,l)=>clean(t).toLocaleLowerCase(l==='tr'?'tr-TR':'und').replace(/^[.!?,:;…\s]+|[.!?,:;…\s]+$/g,'');
  let indexPromise=null,player=null,generation=0,timer=null,settle=null;
  function prepare(){if(!indexPromise)indexPromise=fetch(new URL('index.json',base),{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('Sesler henüz yüklenemedi. Sayfayı yenileyin.');return r.json()}).catch(e=>{indexPromise=null;throw e});return indexPromise}
  function stop(){generation++;clearInterval(timer);timer=null;if(player){player.pause();player.removeAttribute('src');player.load();player=null}if(settle){settle();settle=null}window.speechSynthesis?.cancel()}
  async function recorded(text,language='tr'){
    const value=clean(text);if(!value)return;stop();const token=generation;
    const index=await prepare();if(token!==generation)return;
    const entry=index.entries[language]?.[key(value,language)];
    if(!entry)throw Error(`${names[language]||language} ses kaydı bulunamadı.`);
    await new Promise((resolve,reject)=>{
      const audio=new Audio(new URL(entry[0],base).href);player=audio;audio.preload='auto';let done=false;
      const finish=error=>{if(done)return;done=true;clearInterval(timer);timer=null;if(player===audio){audio.pause();player=null}audio.onloadedmetadata=null;audio.onerror=null;audio.onended=null;if(settle===cancel)settle=null;if(error&&token===generation)reject(error);else resolve()};
      const cancel=()=>finish();settle=cancel;
      audio.onerror=()=>finish(Error('Ses kaydı açılamadı. Yeniden deneyin.'));audio.onended=()=>finish();
      audio.onloadedmetadata=()=>{if(token!==generation){finish();return}audio.currentTime=entry[1];audio.play().then(()=>{if(token!==generation){finish();return}timer=setInterval(()=>{if(token!==generation||audio.currentTime>=entry[2])finish()},20)}).catch(e=>finish(e.name==='AbortError'?null:Error('Sesi başlatmak için düğmeye yeniden dokunun.')))};
      audio.load();
    });
  }
  const locales={tr:['tr-TR'],en:['en-US','en-GB'],ru:['ru-RU'],ky:['ky-KG'],ar:['ar-SA','ar-EG','ar-JO'],fr:['fr-FR','fr-CA']};
  function chooseVoice(voices,language){
    for(const locale of locales[language]||[]){const voice=voices.find(v=>v.lang.toLowerCase()===locale.toLowerCase());if(voice)return voice}
    return voices.find(v=>v.lang.toLowerCase().split('-')[0]===language)||null;
  }
  async function speak(text,language='tr'){
    const value=clean(text);if(!value||value==='—')return;stop();const token=generation;
    // Arabic and Kyrgyz use recordings, as in the A1 shared player.
    if(language==='ar'||language==='ky')return recorded(value,language);
    const synth=window.speechSynthesis;
    if(!synth||!window.SpeechSynthesisUtterance)return recorded(value,language);
    if(!synth.getVoices().length)await new Promise(resolve=>{
      const finish=()=>{clearTimeout(timeout);synth.removeEventListener('voiceschanged',finish);resolve()};
      const timeout=setTimeout(finish,750);synth.addEventListener('voiceschanged',finish);
    });
    if(token!==generation)return;
    const voice=chooseVoice(synth.getVoices(),language);
    if(!voice)return recorded(value,language);
    return new Promise((resolve,reject)=>{
      let done=false;
      const finish=()=>{if(done)return;done=true;clearTimeout(timeout);if(settle===finish)settle=null;resolve()};
      const fallback=()=>{if(done)return;done=true;clearTimeout(timeout);if(settle===finish)settle=null;if(token!==generation){resolve();return}synth.cancel();recorded(value,language).then(resolve,reject)};
      const utterance=new SpeechSynthesisUtterance(value);utterance.voice=voice;utterance.lang=voice.lang;utterance.rate=.9;
      const timeout=setTimeout(fallback,2200);settle=finish;
      utterance.onstart=()=>clearTimeout(timeout);utterance.onend=finish;
      utterance.onerror=e=>{if(e.error==='canceled'||e.error==='interrupted'||token!==generation)finish();else fallback()};
      try{synth.speak(utterance)}catch{fallback()}
    });
  }
  window.TurkceSpeech={prepare,speak,stop,key};prepare().catch(()=>{});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stop()});
})();
