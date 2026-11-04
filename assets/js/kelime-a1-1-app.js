(()=>{'use strict';
const vocab=window.TA_VOCAB_A1_1;if(!Array.isArray(vocab)||vocab.length<90)throw Error('Kelime havuzu yüklenemedi');
const $=id=>document.getElementById(id),scoreKey='ta-activities-A1-1';
const langs={en:'İngilizce',ru:'Rusça',kg:'Kırgızca',ar:'Arapça',fr:'Fransızca'},bank=new Map(vocab.map(v=>[v.tr,v]));
let lang='ru',mode='standard',pos=0,questions=[],chosen=[],submitted=false,round=0;
const attemptKey=()=> 'ta-a1-u1-vocab-round-'+lang+'-'+mode;
const mistakeKey=()=> 'ta-a1-u1-vocab-mistakes-'+lang;
const draftKey=()=> 'ta-a1-u1-vocab-draft-v4-'+lang+'-'+mode;
function readJSON(key,backup){try{return JSON.parse(localStorage.getItem(key))??backup}catch(e){return backup}}
function hash(s){let h=2166136261;for(const c of String(s)){h=Math.imul(h^c.charCodeAt(0),16777619)}return h>>>0}
function shuffled(list,seed){const a=list.slice();let s=seed||1;for(let i=a.length-1;i>0;i--){s=(Math.imul(s,1664525)+1013904223)>>>0;let j=s%(i+1);[a[i],a[j]]=[a[j],a[i]]}return a}
function currentList(){if(mode==='all')return shuffled(vocab,hash(lang+'all'));if(mode==='mistakes'){const missed=readJSON(mistakeKey(),[]);return vocab.filter(v=>Array.isArray(missed)&&missed.includes(v.tr))}return shuffled(vocab,hash(lang+'standard-'+round)).slice(0,50)}
function makeQuestion(v){
 const answer=v[lang],same=vocab.filter(x=>x.tr!==v.tr&&x.topic===v.topic&&x[lang]!==answer),other=vocab.filter(x=>x.tr!==v.tr&&x.topic!==v.topic&&x[lang]!==answer);
 const candidates=shuffled(same,hash(v.tr+lang+'topic')).concat(shuffled(other,hash(v.tr+lang+'other')));
 const distractors=[...new Set(candidates.map(x=>x[lang]).filter(x=>x!==answer))].slice(0,3);
 const options=shuffled([answer,...distractors],hash(v.tr+lang+'opts'));
 if(options.length!==4||new Set(options).size!==4)throw Error('Seçenek hatası: '+v.tr);
 return {id:v.tr,word:v.tr,options,correct:options.indexOf(answer),answer,topic:v.topic}
}
function begin(){
 const desired=document.querySelector('input[name=lang]:checked')?.value;
 lang=Object.prototype.hasOwnProperty.call(langs,desired)?desired:'ru';
 mode=document.querySelector('input[name=mode]:checked')?.value||'standard';
 round=Number(readJSON(attemptKey(),0))||0;
 const list=currentList();
 if(!list.length){$('noMistakes').textContent='Bu dilde henüz yanlış cevap kaydı yok. Önce standart veya kapsamlı testi çöz.';return}
 $('noMistakes').textContent='';
 questions=list.map(makeQuestion);chosen=Array(questions.length).fill(null);pos=0;submitted=false;
 const draft=readJSON(draftKey(),null);
 if(draft&&Array.isArray(draft.ids)&&Array.isArray(draft.answers)&&draft.ids.join('\u0000')===questions.map(x=>x.id).join('\u0000')&&draft.answers.length===questions.length)chosen=draft.answers.map(x=>Number.isInteger(x)&&x>=0&&x<=3?x:null);
 $('welcome').classList.add('hidden');$('test').classList.remove('hidden');render()
}
function count(){return chosen.filter(x=>x!==null).length}
function save(){try{localStorage.setItem(draftKey(),JSON.stringify({ids:questions.map(x=>x.id),answers:chosen}))}catch(e){}}
function render(){
 const n=questions.length,q=questions[pos];$('counter').textContent='Soru '+(pos+1)+' / '+n;$('answered').textContent='Cevaplanan: '+count()+' · Boş: '+(n-count());
 $('bar').style.width=(count()/n*100)+'%';$('topic').textContent=q.topic;
 $('direction').textContent='Türkçe kelimenin '+langs[lang]+' karşılığını seç.';
 $('word').textContent=q.word;$('options').replaceChildren();
 q.options.forEach((o,i)=>{const b=document.createElement('button');b.type='button';b.className='option-btn';b.setAttribute('aria-pressed',String(chosen[pos]===i));const letter=document.createElement('strong'),span=document.createElement('span');letter.textContent='ABCD'[i]+')';span.textContent=o;b.append(letter,span);b.onclick=()=>{chosen[pos]=i;save();render()};$('options').append(b)});
 $('numbers').replaceChildren();chosen.forEach((a,i)=>{const b=document.createElement('button');b.className='num'+(a!==null?' done':'')+(i===pos?' active':'');b.type='button';b.textContent=i+1;b.onclick=()=>{pos=i;render()};$('numbers').append(b)});
 $('blankCount').textContent='Boş: '+(n-count())+' / '+n;$('prev').disabled=pos===0;
 $('next').classList.toggle('hidden',pos===n-1);$('finish').classList.toggle('hidden',pos!==n-1);
}
$('start').onclick=begin;
$('prev').onclick=()=>{if(pos>0){pos--;render()}};
$('next').onclick=()=>{if(pos<questions.length-1){pos++;render()}};
$('clear').onclick=()=>{chosen[pos]=null;save();render()};
$('finish').onclick=()=>{
 if(submitted)return;
 const blank=chosen.length-count();if(blank&&!confirm(blank+' soru boş. Yine de testi bitirmek istiyor musun?'))return;
 if(!confirm('Sınavı tamamlayıp sonucunu görmek istiyor musun?'))return;
 submitted=true;
 const correct=questions.filter((q,i)=>chosen[i]===q.correct).length,wrong=count()-correct;
 const missed=new Set(readJSON(mistakeKey(),[]));questions.forEach((q,i)=>{if(chosen[i]===q.correct)missed.delete(q.id);else missed.add(q.id)});
 try{localStorage.setItem(mistakeKey(),JSON.stringify([...missed]));localStorage.removeItem(draftKey());localStorage.setItem(attemptKey(),JSON.stringify(round+1))}catch(e){}
 if(mode!=='mistakes'){
  let record=readJSON(scoreKey,{});if(!record||typeof record!=='object')record={};
  record.vocabulary={earned:correct,possible:questions.length,completed:true,correct,wrong,blank,languagePair:'tr-'+lang,testMode:mode,submittedAt:new Date().toISOString()};
  try{localStorage.setItem(scoreKey,JSON.stringify(record))}catch(e){}
 }
 $('test').classList.add('hidden');$('result').classList.remove('hidden');
 const percent=Math.round(correct/questions.length*100);
 $('score').textContent='%'+percent+' ('+correct+' / '+questions.length+')';
 $('stats').textContent='Doğru: '+correct+' · Yanlış: '+wrong+' · Boş: '+blank+' · Türkçe – '+langs[lang]+' · '+(mode==='standard'?'Standart test':mode==='all'?'Kapsamlı test':'Yanlışlarımı tekrar et');
 $('resultNote').textContent=mode==='mistakes'?'Bu tekrar alıştırması önceki başarı grafiği puanını değiştirmedi. Yanlışlar listesi güncellendi.':'Bu testin sonucu başarı grafiğine kaydedildi; yanlış ve boş cevaplar tekrar listesine alındı.';
 $('review').replaceChildren();questions.forEach((q,i)=>{const el=document.createElement('span');el.className=chosen[i]===q.correct?'correct':chosen[i]===null?'':'wrong';el.textContent=(i+1)+': '+(chosen[i]===null?'Boş':chosen[i]===q.correct?'Doğru':'Yanlış');el.title=q.word+' → '+q.answer;$('review').append(el)});
 window.scrollTo({top:0,behavior:'smooth'})
};
$('retry').onclick=()=>{$('result').classList.add('hidden');$('welcome').classList.remove('hidden');submitted=false};
})();