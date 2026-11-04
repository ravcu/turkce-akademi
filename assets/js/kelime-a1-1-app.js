(()=>{'use strict';
const vocab=window.TA_VOCAB_A1_1;if(!Array.isArray(vocab)||vocab.length!==50)throw Error('Kelime verisi yüklenemedi');
const $=id=>document.getElementById(id),scoreKey='ta-activities-A1-1';
let lang='ru',pos=0,chosen=Array(50).fill(null),questions=[],submitted=false;
const draftKey=()=> 'ta-a1-u1-vocabulary-v2-'+lang;
function hash(x){let h=2166136261;for(const c of x)h=Math.imul(h^c.charCodeAt(0),16777619);return h>>>0}
function randomOrder(items,seed){const a=items.slice();let s=(seed||1)>>>0;for(let i=a.length-1;i>0;i--){s=(Math.imul(s,1664525)+1013904223)>>>0;const j=s%(i+1);[a[i],a[j]]=[a[j],a[i]]}return a}
function build(){
 questions=vocab.map((v,i)=>{
 const forward=i%2===0,answer=forward?v[lang]:v.tr,key=forward?lang:'tr';
 const candidates=vocab.filter((x,j)=>j!==i&&x[key]!==answer);
 const same=candidates.filter(x=>x.topic===v.topic),other=candidates.filter(x=>x.topic!==v.topic);
 const distractors=randomOrder(same,hash(v.tr+'-topic-'+lang)).concat(randomOrder(other,hash(v.tr+'-other-'+lang))).map(x=>x[key]);
 const distinct=[...new Set(distractors)].filter(x=>x!==answer).slice(0,3);
 const options=randomOrder([answer,...distinct],hash(v.tr+'-options-'+lang));
 if(options.length!==4||new Set(options).size!==4||!options.includes(answer))throw Error('Seçenek hatası '+i);
 return {word:forward?v.tr:v[lang],options,correct:options.indexOf(answer),forward,topic:v.topic,answer}
 });
}
function count(){return chosen.filter(x=>x!==null).length}
function save(){try{localStorage.setItem(draftKey(),JSON.stringify(chosen))}catch(e){}}
function render(){
 const q=questions[pos];$('counter').textContent='Soru '+(pos+1)+' / 50';$('answered').textContent='Cevaplanan: '+count()+' · Boş: '+(50-count());
 $('bar').style.width=(count()/50*100)+'%';$('topic').textContent=q.topic;
 $('direction').textContent=q.forward?'Türkçe ifadenin '+(lang==='ru'?'Rusça':'İngilizce')+' karşılığı nedir?':(lang==='ru'?'Rusça':'İngilizce')+' ifadenin Türkçesi nedir?';
 $('word').textContent=q.word;$('options').replaceChildren();
 q.options.forEach((o,i)=>{const b=document.createElement('button');b.className='option-btn';b.type='button';b.setAttribute('aria-pressed',String(chosen[pos]===i));const letter=document.createElement('strong'),span=document.createElement('span');letter.textContent='ABCD'[i]+')';span.textContent=o;b.append(letter,span);b.onclick=()=>{chosen[pos]=i;save();render()};$('options').append(b)});
 $('numbers').replaceChildren();chosen.forEach((a,i)=>{const b=document.createElement('button');b.className='num'+(a!==null?' done':'')+(pos===i?' active':'');b.textContent=i+1;b.type='button';b.setAttribute('aria-label',(i+1)+'. soru '+(a!==null?'cevaplandı':'boş'));b.onclick=()=>{pos=i;render()};$('numbers').append(b)});
 $('blankCount').textContent='Boş: '+(50-count())+' / 50';$('prev').disabled=pos===0;$('next').classList.toggle('hidden',pos===49);$('finish').classList.toggle('hidden',pos!==49)
}
$('start').onclick=()=>{
 lang=document.querySelector('input[name=lang]:checked')?.value==='en'?'en':'ru';build();
 try{const data=JSON.parse(localStorage.getItem(draftKey()));if(Array.isArray(data)&&data.length===50)chosen=data.map(x=>Number.isInteger(x)&&x>=0&&x<4?x:null)}catch(e){}
 $('welcome').classList.add('hidden');$('test').classList.remove('hidden');render()
};
$('prev').onclick=()=>{pos--;render()};$('next').onclick=()=>{pos++;render()};$('clear').onclick=()=>{chosen[pos]=null;save();render()};
$('finish').onclick=()=>{
 const blank=50-count();if(blank&&!confirm(blank+' soru boş. Yine de testi bitirmek istiyor musun?'))return;
 if(!confirm('Sınavı teslim etmek ve sonuçları görmek istiyor musun?'))return;
 if(submitted)return;submitted=true;
 const correct=questions.filter((q,i)=>q.correct===chosen[i]).length,wrong=count()-correct;
 let record={};try{record=JSON.parse(localStorage.getItem(scoreKey))||{}}catch(e){}
 record.vocabulary={earned:correct,possible:50,completed:true,correct,wrong,blank,languagePair:lang==='ru'?'tr-ru':'tr-en',submittedAt:new Date().toISOString()};
 try{localStorage.setItem(scoreKey,JSON.stringify(record));localStorage.removeItem(draftKey())}catch(e){}
 $('test').classList.add('hidden');$('result').classList.remove('hidden');
 $('score').textContent=(correct*2)+' / 100 puan';$('stats').textContent='Doğru: '+correct+' · Yanlış: '+wrong+' · Boş: '+blank+' · Dil çifti: Türkçe – '+(lang==='ru'?'Rusça':'İngilizce');
 $('review').replaceChildren();questions.forEach((q,i)=>{const span=document.createElement('span');span.className=chosen[i]===q.correct?'correct':chosen[i]===null?'':'wrong';span.textContent=(i+1)+': '+(chosen[i]===null?'Boş':chosen[i]===q.correct?'Doğru':'Yanlış');span.title='Doğru karşılık: '+q.answer;$('review').append(span)});window.scrollTo({top:0,behavior:'smooth'})
};
$('retry').onclick=()=>{if(!confirm('Testi tekrar başlatmak istiyor musun? Yeni sonuç öncekinin yerine geçecektir.'))return;submitted=false;chosen=Array(50).fill(null);pos=0;$('result').classList.add('hidden');$('welcome').classList.remove('hidden')};
})();