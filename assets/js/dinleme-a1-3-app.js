(()=>{'use strict';
const {sections,questions:qs}=window.LISTENING_A1_3;
const $=id=>document.getElementById(id);
let answers=Array(30).fill(null),plays=Array(30).fill(0),pos=0,lastAudioPos=-1;
const draft='ta-listening-a1-3-draft-v1',key='ta-activities-A1-3';
function stop(){if('speechSynthesis'in window)speechSynthesis.cancel();const player=$('audioPlayer');if(player){player.pause();player.currentTime=0}}
function save(){sessionStorage.setItem(draft,JSON.stringify({answers,plays,pos}))}
function render(){
 const q=qs[pos];
 $('topic').textContent=(q.section+1)+'. Bölüm: '+sections[q.section];
 $('counter').textContent=(pos+1)+' / 30';
 $('fill').style.width=(answers.filter(x=>x!==null).length/30*100)+'%';
 $('nums').replaceChildren();
 qs.forEach((_,i)=>{
  const b=document.createElement('button');
  b.className='num'+(i===pos?' active':'')+(answers[i]!==null?' done':'');
  b.textContent=i+1;
  b.onclick=()=>{stop();pos=i;save();render()};
  $('nums').append(b)
 });
 $('ask').textContent=q.question;$('opts').replaceChildren();
 q.options.forEach((o,i)=>{
  const b=document.createElement('button');
  b.className='option-btn';const circle=document.createElement('span');circle.className='circle';const label=document.createElement('span');label.textContent='ABCD'[i]+') '+o;b.append(circle,label);
  b.setAttribute('aria-pressed',String(answers[pos]===i));
  b.onclick=()=>{answers[pos]=i;save();render()};
  $('opts').append(b)
 });
 $('listenCount').textContent='Tekrar dinleme serbest';
 $('listen').disabled=!('speechSynthesis'in window);
 const audio=$('audioPlayer');const src=qs[pos].audioFile||'';
 if(lastAudioPos!==pos){if(src){audio.hidden=false;audio.src=src;audio.load();$('listen').hidden=true;$('voiceFallback').hidden=true}else{audio.pause();audio.removeAttribute('src');audio.load();audio.hidden=true;$('listen').hidden=false;$('voiceFallback').hidden=false}lastAudioPos=pos}
 $('prev').disabled=pos===0;$('next').classList.toggle('hidden',pos===29);$('finish').classList.toggle('hidden',pos!==29);
 $('stats').textContent='Cevaplanan: '+answers.filter(x=>x!==null).length+' · Boş: '+answers.filter(x=>x===null).length;
 $('rightStats').textContent='Boş sorular: '+answers.filter(x=>x===null).length+' / 30'
}
$('start').onclick=()=>{
 try{
 const s=JSON.parse(sessionStorage.getItem(draft));
 if(s&&s.answers?.length===30&&s.plays?.length===30){
  answers=s.answers;plays=s.plays;pos=Math.min(29,Math.max(0,s.pos||0))
 }
 }catch(e){}
 $('intro').classList.add('hidden');$('exam').classList.remove('hidden');render()
};
$('listen').onclick=()=>{
 if(!('speechSynthesis'in window))return;
 stop();
 const u=new SpeechSynthesisUtterance(qs[pos].text);
 u.lang='tr-TR';u.rate=.85;
 const v=speechSynthesis.getVoices().find(v=>v.lang.toLowerCase().startsWith('tr'));
 if(v)u.voice=v;
 plays[pos]++;save();speechSynthesis.speak(u)
};
$('clear').onclick=()=>{answers[pos]=null;save();render()};
$('prev').onclick=()=>{stop();pos--;save();render()};
$('next').onclick=()=>{stop();pos++;save();render()};
$('finish').onclick=()=>{
 const blank=answers.filter(a=>a===null).length;
 if(!confirm((blank?blank+' soru boş. ':'')+'Sınavı bitirmek istiyor musun?'))return;
 stop();
 let correct=0,wrong=0;const counts=Array(6).fill(0);
 answers.forEach((a,i)=>{if(a===qs[i].correct){correct++;counts[qs[i].section]++}else if(a!==null)wrong++});
 const score=correct/30*100;
 let stored={};try{stored=JSON.parse(localStorage.getItem(key))||{}}catch(e){}
 stored.listening={earned:correct,possible:30,completed:true,updatedAt:new Date().toISOString()};
 localStorage.setItem(key,JSON.stringify(stored));
 sessionStorage.removeItem(draft);
 $('exam').classList.add('hidden');$('result').classList.remove('hidden');
 $('percent').textContent='%'+score.toFixed(1);
 $('counts').textContent='Doğru: '+correct+' · Yanlış: '+wrong+' · Boş: '+blank;
 $('resultLines').replaceChildren();
 sections.forEach((s,i)=>{const p=document.createElement('p');p.textContent=s+': '+counts[i]+'/5';$('resultLines').append(p)})
};
$('retry').onclick=()=>{answers=Array(30).fill(null);plays=Array(30).fill(0);pos=0;lastAudioPos=-1;$('result').classList.add('hidden');$('exam').classList.remove('hidden');save();render()};
if(!('speechSynthesis'in window)){$('voiceWarning').textContent='Tarayıcınız geçici seslendirmeyi desteklemiyor. Ses dosyaları eklenince çubuktan oynatılabilecek.'}
window.addEventListener('pagehide',stop);
})();