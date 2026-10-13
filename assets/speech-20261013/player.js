/* Türkçe Akademi: explicit language voices and same-site recorded speech. */
(() => {
  'use strict';
  const base = new URL('.', document.currentScript.src);
  const names = {tr:'Türkçe',en:'İngilizce',ru:'Rusça',ky:'Kırgızca',ar:'Arapça',fr:'Fransızca'};
  const locales = {tr:['tr-TR'],en:['en-US','en-GB'],ru:['ru-RU'],ky:['ky-KG'],ar:['ar-SA','ar-EG','ar-JO'],fr:['fr-FR','fr-CA']};
  let generation = 0, player = null, boundaryTimer = null, indexPromise = null;
  const clean = text => String(text ?? '').normalize('NFC').replace(/(^|\s)[\-−–—]+(?=\s*\S)/g,'$1').replace(/\s+/g,' ').trim();
  const key = (text, language) => clean(text).toLocaleLowerCase(language === 'tr' ? 'tr-TR' : 'und').replace(/^[.!?,:;…\s]+|[.!?,:;…\s]+$/g,'');
  function prepare() {
    if (!indexPromise) indexPromise = fetch(new URL('index.json',base)).then(r => {
      if (!r.ok) throw new Error('Ses sözlüğü yüklenemedi. Sayfayı yenileyin.');
      return r.json();
    }).catch(error => { indexPromise = null; throw error; });
    return indexPromise;
  }
  function stop() {
    generation++;
    clearInterval(boundaryTimer); boundaryTimer = null;
    if (player) { player.onloadedmetadata = null; player.onerror = null; player.onended = null; player.pause(); player = null; }
    window.speechSynthesis?.cancel();
  }
  function chooseVoice(voices, language) {
    for (const locale of locales[language] || []) {
      const voice = voices.find(v => v.lang.toLowerCase() === locale.toLowerCase());
      if (voice) return voice;
    }
    return voices.find(v => v.lang.toLowerCase().split('-')[0] === language) || null;
  }
  async function voicesReady() {
    if (!window.speechSynthesis) return [];
    const synth = window.speechSynthesis;
    if (synth.getVoices().length) return synth.getVoices();
    await new Promise(resolve => {
      const finish = () => { clearTimeout(timeout); synth.removeEventListener('voiceschanged',finish); resolve(); };
      const timeout = setTimeout(finish,750);
      synth.addEventListener('voiceschanged',finish);
    });
    return synth.getVoices();
  }
  async function recorded(text, language, token) {
    const index = await prepare();
    if (token !== generation) return;
    const entry = index.entries[language]?.[key(text,language)];
    if (!entry) throw new Error(`${names[language] || language} için bu ifadenin ses kaydı bulunamadı.`);
    const audio = new Audio(new URL(entry[0],base).href); player = audio; audio.preload = 'auto';
    await new Promise((resolve,reject) => {
      let finished = false;
      const finish = error => {
        if (finished) return; finished = true;
        if (player === audio) { clearInterval(boundaryTimer); boundaryTimer = null; audio.pause(); player = null; }
        audio.onloadedmetadata = null; audio.onerror = null; audio.onended = null;
        if (error && token === generation) reject(error); else resolve();
      };
      audio.onerror = () => finish(new Error(`${names[language] || language} ses kaydı açılamadı. Yeniden deneyin.`));
      audio.onended = () => finish();
      audio.onloadedmetadata = () => {
        if (token !== generation) { finish(); return; }
        audio.currentTime = entry[1];
        audio.play().then(() => {
          if (token !== generation) { finish(); return; }
          boundaryTimer = setInterval(() => {
            if (token !== generation || audio.currentTime >= entry[2]) finish();
          },25);
        }).catch(error => finish(error.name === 'AbortError' ? null : new Error('Sesi başlatmak için hoparlör düğmesine yeniden dokunun.')));
      };
      audio.load();
    });
  }
  async function speak(text, language = 'tr') {
    const value = clean(text); if (!value || value === '—') return;
    stop(); const token = generation;
    // These languages always use dedicated recordings, even without OS voices.
    if (language === 'ar' || language === 'ky') return recorded(value,language,token);
    const voices = await voicesReady(); if (token !== generation) return;
    const voice = chooseVoice(voices,language);
    if (!voice || !window.SpeechSynthesisUtterance) return recorded(value,language,token);
    return new Promise((resolve,reject) => {
      let done = false;
      const utterance = new SpeechSynthesisUtterance(value);
      utterance.voice = voice; utterance.lang = voice.lang; utterance.rate = .9;
      const finish = () => { if (done) return; done = true; clearTimeout(timeout); resolve(); };
      const fallback = () => {
        if (done) return; done = true; clearTimeout(timeout);
        if (token !== generation) { resolve(); return; }
        window.speechSynthesis.cancel(); recorded(value,language,token).then(resolve,reject);
      };
      const timeout = setTimeout(fallback,2200);
      utterance.onstart = () => clearTimeout(timeout);
      utterance.onend = finish;
      utterance.onerror = event => {
        if (event.error === 'canceled' || event.error === 'interrupted' || token !== generation) finish(); else fallback();
      };
      try { window.speechSynthesis.speak(utterance); } catch { fallback(); }
    });
  }
  window.TurkceSpeech = {prepare,speak,stop,chooseVoice,key};
  prepare().catch(() => {});
})();
