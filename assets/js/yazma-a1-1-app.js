(()=>{'use strict';
const data=window.TA_WRITING_A1_1;if(!data||data.tasks.length!==30)throw Error('Yazma görevleri yüklenemedi');
const {tasks,sections}=data,$=id=>document.getElementById(id),storageKey='ta-a1-u1-writing-draft-v1';
let pos=0,answers=Array(30).fill(''),checked=Array(30).fill(false);
try{const d=JSON.parse(localStorage.getItem(storageKey));if(d&&Array.isArray(d.answers)&&d.answers.length===30)answers=d.answers.map(x=>String(x||''));if(d&&Array.isArray(d.checked)&&d.checked.length===30)checked=d.checked.map(Boolean)}catch(e){}
const kindName={blank:'Boşluk doldurma',order:'Kelimeleri sıralama',correct:'Yanlışı düzeltme',short:'Kısa cevap',free:'Bağımsız yazma'};
function clean(s){return String(s||'').toLocaleLowerCase('tr-TR').normalize('NFC').replace(/[.,!?;:()”“"']/g,' ').replace(/\s+/g,' ').trim()}
function equals(a,b){return clean(a)===clean(b)}
function persist(){try{localStorage.setItem(storageKey,JSON.stringify({answers,checked,updatedAt:new Date().toISOString()}))}catch(e){}}
function count(){return answers.filter(x=>x.trim()).length}
function readInput(){return tasks[pos].kind==='free'?$('longAnswer').value:$('shortAnswer').value}
function save(){const text=readInput();if(answers[pos]!==text){answers[pos]=text;checked[pos]=false;persist()}}
function showFeedback(message){$('feedback').textContent=message;$('feedback').classList.remove('hidden')}
function render(){
 const t=tasks[pos];$('counter').textContent='Soru '+(pos+1)+' / 30';$('answered').textContent='Cevaplanan: '+count()+' · Boş: '+(30-count());
 $('bar').style.width=(count()/30*100)+'%';$('section').textContent=(t.section+1)+'. Bölüm – '+sections[t.section]+' · '+kindName[t.kind];
 $('prompt').textContent=t.prompt;$('hint').textContent=t.hint;
 $('shortAnswer').classList.toggle('hidden',t.kind==='free');$('longAnswer').classList.toggle('hidden',t.kind!=='free');
 $('shortAnswer').value=answers[pos];$('longAnswer').value=answers[pos];
 $('feedback').classList.add('hidden');$('check').textContent=t.kind==='short'||t.kind==='free'?'Yanıtımı Kaydet / Kontrol Et':'Cevabımı Kontrol Et';
 $('numbers').replaceChildren();answers.forEach((v,i)=>{const b=document.createElement('button');b.type='button';b.textContent=i+1;b.className='num'+(v.trim()?' done':'')+(pos===i?' active':'');b.setAttribute('aria-label',(i+1)+'. soru '+(v.trim()?'cevaplandı':'boş'));b.onclick=()=>go(i);$('numbers').append(b)});
 $('blankCount').textContent='Boş: '+(30-count())+' / 30';
 $('prev').disabled=pos===0;$('next').classList.toggle('hidden',pos===29);$('finish').classList.toggle('hidden',pos!==29)
}
function go(i){save();pos=Math.max(0,Math.min(29,i));render()}
$('start').onclick=()=>{$('welcome').classList.add('hidden');$('test').classList.remove('hidden');render()};
$('shortAnswer').addEventListener('input',()=>{save();$('answered').textContent='Cevaplanan: '+count()+' · Boş: '+(30-count());$('feedback').classList.add('hidden')});
$('longAnswer').addEventListener('input',()=>{save();$('answered').textContent='Cevaplanan: '+count()+' · Boş: '+(30-count());$('feedback').classList.add('hidden')});
$('check').onclick=()=>{
 save();const t=tasks[pos],v=answers[pos];if(!v.trim()){showFeedback('Henüz yanıt yazmadın.');return}
 if(t.kind==='short'||t.kind==='free'){showFeedback('Yanıtın kaydedildi. Bu tür görevlerde anlam, dil bilgisi, anlatım ve yazım öğretmen tarafından değerlendirilecek. Otomatik puan verilmedi.');return}
 const right=equals(v,t.answer);checked[pos]=true;persist();
 showFeedback(right?'Doğru! Yazdığın cevap beklenen ifadeyle eşleşiyor.':'Cevabın beklenen ifadeyle eşleşmedi. Yazımını ve kelime sırasını gözden geçir. Farklı ama doğru yazımlar için öğretmen kontrolü gerekebilir.')
};
$('example').onclick=()=>{showFeedback('Örnek cevap: '+tasks[pos].answer+'\nBu yanıt, serbest yazma görevlerinde tek doğru cevap değildir.')};
$('prev').onclick=()=>go(pos-1);$('next').onclick=()=>go(pos+1);
$('clear').onclick=()=>{answers[pos]='';checked[pos]=false;persist();render()};
function exportText(){const lines=['TÜRKÇE AKADEMİ - LİSE A1 1. ÜNİTE YAZMA ETKİNLİĞİ','Tarih: '+new Date().toLocaleDateString('tr-TR'),''];tasks.forEach((t,i)=>{lines.push((i+1)+'. '+t.prompt,'Cevap: '+(answers[i].trim()||'(Boş)'),'')});const blob=new Blob([lines.join('\n')],{type:'text/plain;charset=utf-8'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='lise-a1-1-unite-yazma-cevaplari.txt';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),3000)}
$('export').onclick=exportText;
$('finish').onclick=()=>{
 save();const missing=30-count();if(!confirm((missing?missing+' görev boş. ':'')+'Yazma etkinliğini bitirmek istiyor musun?'))return;
 const closed=tasks.map((t,i)=>({t,i})).filter(x=>!['short','free'].includes(x.t.kind));const correct=closed.filter(({t,i})=>equals(answers[i],t.answer)).length;
 const status={completed:count(),total:30,autoCorrect:correct,autoPossible:20,teacherReviewPending:10,assessmentStatus:'teacher_review_required',updatedAt:new Date().toISOString()};
 try{localStorage.setItem('ta-writing-a1-1-progress',JSON.stringify(status))}catch(e){}
 $('test').classList.add('hidden');$('result').classList.remove('hidden');
 $('completed').textContent=count()+' / 30 görev tamamlandı';$('summaryText').textContent='Boş görev: '+missing+' · Öğretmen değerlendirmesi bekleniyor.';
 $('automatic').textContent='Kapalı uçlu etkinlikler: '+correct+' / 20 eşleşme. Bu sonuç nihai yazma becerisi puanı değildir.';
 $('sectionResult').replaceChildren();sections.forEach((s,i)=>{const p=document.createElement('p');p.textContent=s+': '+answers.slice(i*5,i*5+5).filter(x=>x.trim()).length+'/5 cevap';$('sectionResult').append(p)});
 window.scrollTo({top:0,behavior:'smooth'})
};
$('edit').onclick=()=>{$('result').classList.add('hidden');$('test').classList.remove('hidden');render()};
})();