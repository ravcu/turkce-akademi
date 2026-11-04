(()=>{'use strict';
const data=window.TA_WRITING_A1_1;if(!data||data.tasks.length!==30)throw Error('Yazma soru bankası yüklenemedi');
const {tasks,sections}=data,$=id=>document.getElementById(id),storageKey='ta-a1-u1-writing-draft-v2',scoreKey='ta-activities-A1-1';
let pos=0,answers=Array(30).fill(''),submitted=false;
try{const d=JSON.parse(localStorage.getItem(storageKey));if(d&&Array.isArray(d.answers)&&d.answers.length===30)answers=d.answers.map(x=>String(x||''))}catch(e){}
const kindName={blank:'Boşluk doldurma',order:'Kelimeleri sıralama',correct:'Cümleyi düzeltme',short:'Kısa cümle yazma'};
function clean(s){return String(s||'').toLocaleLowerCase('tr-TR').normalize('NFC').replace(/[.,!?;:()”“"‘’']/g,' ').replace(/\s+/g,' ').trim()}
function correct(t,answer){const a=clean(answer);return a.length>0&&[t.answer,...(t.alternatives||[])].some(x=>clean(x)===a)}
function persist(){try{localStorage.setItem(storageKey,JSON.stringify({answers,updatedAt:new Date().toISOString()}))}catch(e){}}
function count(){return answers.filter(x=>x.trim()).length}
function save(){const text=$('shortAnswer').value;if(text!==answers[pos]){answers[pos]=text;persist()}}
function showFeedback(msg){$('feedback').textContent=msg;$('feedback').classList.remove('hidden')}
function render(){
 const t=tasks[pos];$('counter').textContent='Soru '+(pos+1)+' / 30';$('answered').textContent='Cevaplanan: '+count()+' · Boş: '+(30-count());
 $('bar').style.width=(count()/30*100)+'%';$('section').textContent=(t.section+1)+'. Bölüm – '+sections[t.section]+' · '+kindName[t.kind];
 $('prompt').textContent=t.prompt;$('hint').textContent=t.hint;$('shortAnswer').value=answers[pos];
 $('feedback').classList.add('hidden');
 $('numbers').replaceChildren();
 answers.forEach((v,i)=>{const b=document.createElement('button');b.type='button';b.textContent=i+1;b.className='num'+(v.trim()?' done':'')+(pos===i?' active':'');b.setAttribute('aria-label',(i+1)+'. soru '+(v.trim()?'cevaplandı':'boş'));b.onclick=()=>go(i);$('numbers').append(b)});
 $('blankCount').textContent='Boş: '+(30-count())+' / 30';
 $('prev').disabled=pos===0;$('next').classList.toggle('hidden',pos===29);$('finish').classList.toggle('hidden',pos!==29)
}
function go(i){save();pos=Math.max(0,Math.min(29,i));render()}
$('start').onclick=()=>{$('welcome').classList.add('hidden');$('test').classList.remove('hidden');render()};
$('shortAnswer').addEventListener('input',()=>{save();$('feedback').classList.add('hidden');$('answered').textContent='Cevaplanan: '+count()+' · Boş: '+(30-count());$('bar').style.width=(count()/30*100)+'%';});
$('check').onclick=()=>{save();showFeedback(answers[pos].trim()?'Yanıtın kaydedildi. Doğruluk kontrolü sınavın sonunda tüm sorular için otomatik yapılacak.':'Bu soruya henüz cevap yazmadın.')};
$('prev').onclick=()=>go(pos-1);$('next').onclick=()=>go(pos+1);
$('clear').onclick=()=>{answers[pos]='';persist();render()};
function exportText(){
 const lines=['TÜRKÇE AKADEMİ – LİSE A1 1. ÜNİTE YAZMA ETKİNLİĞİ','Tarih: '+new Date().toLocaleDateString('tr-TR'),''];
 tasks.forEach((t,i)=>lines.push((i+1)+'. '+t.prompt,'Öğrenci yanıtı: '+(answers[i].trim()||'(Boş)'),''));const blob=new Blob([lines.join('\n')],{type:'text/plain;charset=utf-8'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='lise-a1-1-unite-yazma-cevaplari.txt';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),3000)
}
$('export').onclick=exportText;
$('finish').onclick=()=>{
 save();if(submitted)return;const blank=30-count();
 if(blank&&!confirm(blank+' soru boş. Yine de testi bitirmek istiyor musun?'))return;
 if(!confirm('Sınavı bitirip otomatik sonucu görmek istiyor musun?'))return;submitted=true;
 const hits=tasks.map((t,i)=>correct(t,answers[i])),earned=hits.filter(Boolean).length,wrong=count()-earned;
 let record={};try{record=JSON.parse(localStorage.getItem(scoreKey))||{}}catch(e){}
 record.writing={earned,possible:30,completed:true,correct:earned,wrong,blank,submittedAt:new Date().toISOString(),assessmentMethod:'guided-exact-and-alternative'};
 try{localStorage.setItem(scoreKey,JSON.stringify(record));localStorage.removeItem(storageKey)}catch(e){}
 $('test').classList.add('hidden');$('result').classList.remove('hidden');
 $('completed').textContent='%'+(100*earned/30).toFixed(1)+' ('+earned+'/30 doğru)';
 $('summaryText').textContent='Doğru: '+earned+' · Yanlış: '+wrong+' · Boş: '+blank;
 $('automatic').textContent='30 sorunun tamamı otomatik kontrol edildi. Büyük/küçük harf, noktalama ve tanımlı alternatif cevaplar kabul edilir.';
 $('sectionResult').replaceChildren();
 sections.forEach((s,i)=>{const p=document.createElement('p');p.textContent=s+': '+hits.slice(i*5,i*5+5).filter(Boolean).length+'/5 doğru';$('sectionResult').append(p)});
 const review=$('review');if(review){review.replaceChildren();tasks.forEach((t,i)=>{const box=document.createElement('div');box.className='review-item '+(hits[i]?'correct':answers[i].trim()?'wrong':'blank');
 const title=document.createElement('strong');title.textContent=(i+1)+'. '+(hits[i]?'Doğru':answers[i].trim()?'Yanlış':'Boş');
 const msg=document.createElement('p');msg.textContent='Cevabın: '+(answers[i].trim()||'—')+' | Beklenen: '+t.answer;box.append(title,msg);review.append(box)})}
 window.scrollTo({top:0,behavior:'smooth'})
};
$('edit').onclick=()=>{$('result').classList.add('hidden');$('test').classList.remove('hidden');submitted=false;render()};
})();