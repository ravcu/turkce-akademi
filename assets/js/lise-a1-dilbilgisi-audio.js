/* Türkçe Akademi: Lise A1 Dil Bilgisi ve Telaffuz PDF DİNLE eşleştirmesi.
   S.001 -> Lise - A1 - Dil Bilgisi - 1.opus. Yüklenmemiş sesler devre dışı kalır. */
(function () {
'use strict';
const folder='Lise A1 dilbilgisi ve telaffuz kitabı ses dosyaları';
const base='/turkce-akademi/sesler/'+encodeURIComponent(folder)+'/';
const available=new Set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, "97-2", 98, 99, 100, 101, 102, 103, 104, "104-2", 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138]);
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
