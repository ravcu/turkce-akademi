/* Lise A2 Dil Bilgisi ve Telaffuz: manifest-driven original book recordings.
   Only exact S.xxx identities are used; e.g. S.107.1 never falls back to S.107. */
(function () {
'use strict';
const base='/turkce-akademi/sesler/Lise-A2-Dilbilgisi-ve-Telaffuz/';
const available=new Set();
let tracks={},lastRender=null,observer=null,activeButton=null,toastTimer=null;
function parsed(value){
 const m=/^S\.(\d{1,3})(?:[.-](\d+))?$/.exec(String(value||'').trim());
 return m?'S.'+m[1].padStart(3,'0')+(m[2]?'.'+m[2]:''):null;
}
function audioUrl(code){const key=parsed(code),track=key&&tracks[key];return track?base+encodeURIComponent(track.file):null}
function tell(message){const toast=document.getElementById('toast');if(!toast)return;clearTimeout(toastTimer);toast.textContent=message;toast.classList.add('show');toastTimer=setTimeout(()=>toast.classList.remove('show'),2600)}
function ensureStyle(){
 if(document.getElementById('ta-a2-grammar-audio-style'))return;
 const style=document.createElement('style');style.id='ta-a2-grammar-audio-style';
 style.textContent='.audio-cue{min-height:18px;padding:2px 5px;font-size:clamp(8px,1.4cqw,10px)}.audio-cue:disabled{opacity:.55;cursor:not-allowed;background:#e8eef0;color:#63737a;border-color:#c9d0d3}.audio-cue[data-playing="true"]{background:#087f83;color:white;border-color:#087f83}';document.head.append(style);
}
function positionButtons(page,layer){
 const width=layer.clientWidth,height=layer.clientHeight;if(!width||!height)return;
 const text=page.words.filter(w=>/[\p{L}\p{N}]/u.test(w.t)).map(w=>({x:w.x*width,y:w.y*height,w:w.w*width,h:w.h*height}));
 const placed=[],overlaps=(a,b,pad=2)=>a.x<b.x+b.w+pad&&a.x+a.w>b.x-pad&&a.y<b.y+b.h+pad&&a.y+a.h>b.y-pad;
 for(const button of layer.querySelectorAll('.audio-cue')){
  const w=button.offsetWidth||42,h=button.offsetHeight||18,word=page.words[Number(button.dataset.wordIndex)];
  const rawX=(word.x+word.w+.007)*width,rawY=(word.y-.004)*height;
  const x=Math.max(3,Math.min(rawX,width-w-3)),y=Math.max(2,Math.min(rawY,height-h-2));
  let position=null;
  const ys=[y,Math.max(2,word.y*height-h-4),Math.min(height-h-2,(word.y+word.h)*height+4)];
  for(let dy=8;dy<=64;dy+=8){ys.push(Math.max(2,y-dy),Math.min(height-h-2,y+dy))}
  for(const reach of [Math.min(128,width*.3),width]){
   const shifts=[0];for(let dx=8;dx<=reach;dx+=8)shifts.push(-dx,dx);
   for(const py of ys){
    for(const dx of shifts){
    const box={x:x+dx,y:py,w,h};if(box.x<3||box.x+w>width-3)continue;
    if(text.some(t=>overlaps(box,t))||placed.some(t=>overlaps(box,t)))continue;
    position=box;break;
    }
    if(position)break;
   }
   if(position)break;
  }
  if(!position)position={x,y,w,h};
  button.style.left=position.x+'px';button.style.top=position.y+'px';placed.push(position);
 }
}
function render(page,layer,playCallback=play){
 if(!layer)return;ensureStyle();lastRender={page,layer,playCallback};layer.replaceChildren();
 if(!observer&&window.ResizeObserver){observer=new ResizeObserver(()=>{if(lastRender)positionButtons(lastRender.page,lastRender.layer)});observer.observe(layer.parentElement)}
 const seen=new Set();
 (page?.words||[]).forEach((word,index)=>{
  const code=parsed(word.t);if(!code)return;
  const identity=code+'@'+word.x.toFixed(5)+'@'+word.y.toFixed(5);if(seen.has(identity))return;seen.add(identity);
  const ready=available.has(code),button=document.createElement('button');button.type='button';button.className='audio-cue';button.textContent='DİNLE';button.dataset.wordIndex=index;button.dataset.code=code;
  button.title=ready?code+' ses kaydını dinle':code+' ses dosyası henüz yüklenmedi';button.setAttribute('aria-label',ready?code+' dinleme kaydını oynat':code+' ses kaydı henüz mevcut değil');button.disabled=!ready;
  button.style.left=Math.min(word.x+word.w+.007,.92)*100+'%';button.style.top=Math.max(word.y-.004,.02)*100+'%';
  if(ready)button.addEventListener('click',()=>playCallback(code,button));layer.append(button);
 });
 positionButtons(page,layer);
}
function clearActive(){if(activeButton)delete activeButton.dataset.playing;activeButton=null}
function stop(){
 const player=document.getElementById('audioPlayer');if(!player)return;
 player.onplay=null;player.onpause=null;player.onended=null;player.onerror=null;player.pause();player.removeAttribute('src');player.load();clearActive();const box=document.getElementById('listeningPlayer');if(box)box.hidden=true;
}
function play(value,button){
 const code=parsed(value),url=audioUrl(code);if(!url)return;
 const player=document.getElementById('audioPlayer'),box=document.getElementById('listeningPlayer');if(!player||!box)return;
 stop();window.TurkceSpeech?.stop();window.speechSynthesis?.cancel();box.hidden=false;
 const label=box.querySelector('.listening-label');if(label)label.textContent='🎧 '+code+' — Dil Bilgisi ve Telaffuz';
 activeButton=button||null;player.src=url;player.preload='metadata';
 player.onplay=()=>{if(activeButton)activeButton.dataset.playing='true'};
 player.onpause=()=>{if(activeButton)delete activeButton.dataset.playing};player.onended=clearActive;
 player.onerror=()=>{clearActive();tell(code+' kaydı açılamadı. Bağlantıyı kontrol edin.')};
 player.play().catch(error=>{if(error.name!=='AbortError'){clearActive();tell('Sesi başlatmak için oynat düğmesine basın.')}});
}
const whenReady=fetch(base+'manifest.json',{cache:'no-store'}).then(response=>{if(!response.ok)throw new Error('Ses listesi yüklenemedi');return response.json()}).then(data=>{
 tracks=data.tracks||{};available.clear();for(const [code,track] of Object.entries(tracks))if(parsed(code)===code&&typeof track.file==='string')available.add(code);
 if(lastRender)render(lastRender.page,lastRender.layer,lastRender.playCallback);return data;
}).catch(error=>{console.warn('Lise A2 grammar recordings:',error.message);return null});
window.TAA2DilbilgisiAudio={render,play,stop,available,audioUrl,parsed,whenReady};
})();
