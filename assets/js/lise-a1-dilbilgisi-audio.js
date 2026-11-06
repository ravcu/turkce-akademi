/* Türkçe Akademi: Lise A1 Dil Bilgisi ve Telaffuz PDF DİNLE eşleştirmesi.
   S.001 -> Lise - A1 - Dil Bilgisi - 1.opus. Yüklenmemiş sesler devre dışı kalır. */
(function () {
'use strict';
const folder='Lise A1 dilbilgisi ve telaffuz kitabı ses dosyaları';
const base='/turkce-akademi/sesler/'+encodeURIComponent(folder)+'/';
const available=new Set([...Array(60)].map((_,i)=>i+1).concat([64,65,66,67,69,70,71]));
const labelFor=(code)=>{const m=String(code).match(/^(\d+)(?:-(\d+))?$/);return m?'S.'+m[1].padStart(3,'0')+(m[2]?'.'+m[2]:''):'S.'+code};
function parsed(text){
  const m=/^S\.(\d{3})(?:\.(\d+))?$/.exec(String(text||'').trim());
  return m?{number:Number(m[1]),extra:m[2]||'',label:text}:null;
}
function audioUrl(number){
  const file='Lise - A1 - Dil Bilgisi - '+number+'.opus';
  return base+encodeURIComponent(file);
}
function ensureStyle(){
 if(document.getElementById('ta-dilbilgisi-audio-styles'))return;
 const s=document.createElement('style');s.id='ta-dilbilgisi-audio-styles';
 s.textContent='.audio-cue:disabled{opacity:.58;cursor:not-allowed;background:#e8eef0;color:#63737a;border-color:#c9d0d3}.audio-cue[data-playing="true"]{background:#0a827f;color:#fff;border-color:#0a827f}';
 document.head.append(s)
}
function render(page,layer,play){
 if(!layer)return;
 ensureStyle();layer.replaceChildren();
 const seen=new Set();
 for(const word of page?.words||[]){
   const data=parsed(word.t);
   if(!data)continue;
   const identity=data.label+'-'+Math.round(word.x*1000)+'-'+Math.round(word.y*1000);
   if(seen.has(identity))continue;seen.add(identity);
   const track=data.extra?data.number+'-'+data.extra:data.number;
   const ready=available.has(track);
   const b=document.createElement('button');b.type='button';b.className='audio-cue';
   b.textContent='DİNLE';
   b.title=ready?data.label+' ses kaydını dinle':data.label+' ses dosyası henüz yüklenmedi';
   b.setAttribute('aria-label',ready?data.label+' dinleme kaydını oynat':data.label+' ses kaydı henüz mevcut değil');
   b.style.left=(Math.max(.06,Math.min(Number(word.x)+Number(word.w)+.007,.91))*100)+'%';
   b.style.top=(Math.max(.02,Math.min(Number(word.y)-.004,.95))*100)+'%';
   b.disabled=!ready;
   if(ready)b.addEventListener('click',()=>play(track,b));
   layer.append(b);
 }
}
function play(number,button){
 if(!available.has(number))return;
 const player=document.getElementById('audioPlayer');
 const wrapper=document.getElementById('listeningPlayer');
 if(!player||!wrapper)return;
 player.pause();
 player.removeAttribute('src');
 player.load();
 wrapper.hidden=false;
 wrapper.querySelector('.listening-label').textContent='🎧 '+labelFor(number)+' – Dil Bilgisi ve Telaffuz';
 document.querySelectorAll('.audio-cue[data-playing="true"]').forEach(x=>delete x.dataset.playing);
 if(button)button.dataset.playing='true';
 player.src=audioUrl(number);
 player.preload='metadata';
 const clear=()=>{if(button)delete button.dataset.playing};
 player.onended=clear;player.onpause=clear;
 player.onerror=()=>{clear();window.alert(labelFor(number)+' kaydı şu anda oynatılamıyor. Bağlantıyı kontrol edin.')};
 player.play().catch(()=>{clear();const toast=document.querySelector('#toast');if(toast){toast.textContent='Sesi başlatmak için oynat düğmesine basın.';toast.classList.add('show');setTimeout(()=>toast.classList.remove('show'),2100)}});
}
window.TAA1DilbilgisiAudio={render,play,available,audioUrl};
})();
