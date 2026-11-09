(()=>{'use strict';
const source=window.TA_SPEAKING_A1_2;if(!source||source.tasks.length!==30)throw Error('Konuşma görevleri yüklenemedi.');
const {sections,tasks}=source,$=id=>document.getElementById(id),grader=window.TA_SPEAKING_GRADE;if(!grader||grader.ruleCount!==30)throw Error('Konuşma değerlendirme kuralları bulunamadı.');
const answers=tasks.map(()=>({url:null,blob:null,text:'',recognized:false,feedback:false}));
let pos=0,recorder=null,stream=null,chunks=[],recognition=null,recordingIndex=-1;
const SpeechRecognition=window.SpeechRecognition||window.webkitSpeechRecognition;
function haltVoice(){if('speechSynthesis'in window)speechSynthesis.cancel()}
function cleanupRecorder(){if(stream){stream.getTracks().forEach(t=>t.stop());stream=null}recorder=null;$('record').disabled=false;$('stop').disabled=true}
function stopForNavigation(){if(recorder&&recorder.state!=='inactive'){recorder.stop()}if(recognition){try{recognition.stop()}catch(e){}recognition=null}haltVoice()}
function answeredCount(){return answers.filter(a=>!!a.blob).length}
function updateText(){answers[pos].text=$('transcript').value;$('feedback').hidden=true;answers[pos].feedback=false}
function render(){
 const task=tasks[pos],answer=answers[pos];
 $('counter').textContent='Görev '+(pos+1)+' / 30';$('answered').textContent='Kaydedilen: '+answeredCount()+' · Boş: '+(30-answeredCount());
 $('bar').style.width=(answeredCount()/30*100)+'%';
 $('section').textContent=(task.section+1)+'. Bölüm – '+sections[task.section];
 $('prompt').textContent=task.prompt;
 $('numbers').replaceChildren();
 answers.forEach((item,i)=>{
  const b=document.createElement('button');b.type='button';b.textContent=i+1;
  b.className='num'+(item.blob?' done':'')+(i===pos?' active':'');
  b.setAttribute('aria-label',(i+1)+'. görev '+(item.blob?'kayıt var':'boş'));
  b.onclick=()=>navigate(i);$('numbers').append(b)
 });
 $('blankCount').textContent='Kaydedilen: '+answeredCount()+' / 30 · Boş: '+(30-answeredCount());
 $('transcript').value=answer.text;
 $('recordState').textContent=answer.blob?'Ses kaydı mevcut':'Kayda hazır';
 $('recorded').hidden=!answer.url;$('download').hidden=!answer.url;
 if(answer.url){$('recorded').src=answer.url;$('download').href=answer.url;$('download').download='A1-konusma-gorev-'+String(pos+1).padStart(2,'0')+'.webm'}
 else{$('recorded').removeAttribute('src');$('recorded').load();$('download').removeAttribute('href')}
 $('feedback').hidden=true;$('example').hidden=true;
 $('prev').disabled=pos===0;$('next').classList.toggle('hidden',pos===29);$('finish').hidden=pos!==29;
 $('recognitionNote').textContent=SpeechRecognition?'Konuşma tanıma destekleniyor; metni kontrol edebilirsin.':'Bu tarayıcıda Türkçe konuşma tanıma yok. Kaydını dinleyip metnini istersen yazabilirsin.';
}
function navigate(i){if(recorder&&recorder.state==='recording'){alert('Önce kaydı bitirin.');return}haltVoice();if($('recorded'))$('recorded').pause();pos=Math.max(0,Math.min(29,i));render()}
$('start').onclick=()=>{$('welcome').classList.add('hidden');$('test').classList.remove('hidden');render()};
$('hear').onclick=()=>{
 if(!('speechSynthesis'in window)){alert('Tarayıcınız Türkçe seslendirmeyi desteklemiyor.');return}
 haltVoice();const text=tasks[pos].prompt.replace(/^Soruya sesli cevap ver:\s*/i,'').replace(/^Şu cümleyi seslendir:\s*/i,'').replace(/^Şu kelimeleri oku:\s*/i,'');
 const u=new SpeechSynthesisUtterance(text);u.lang='tr-TR';u.rate=.96;u.pitch=1;
 const voices=speechSynthesis.getVoices(),v=voices.find(x=>x.lang.toLowerCase()==='tr-tr'&&/natural|online|neural/i.test(x.name))||voices.find(x=>x.lang.toLowerCase().startsWith('tr'));
 if(v)u.voice=v;speechSynthesis.speak(u);
};
function beginRecognition(i){
 if(!SpeechRecognition)return;
 try{const r=new SpeechRecognition();recognition=r;r.lang='tr-TR';r.continuous=true;r.interimResults=false;
 let recognized=[];
 r.onresult=e=>{if(recordingIndex!==i)return;for(let j=e.resultIndex;j<e.results.length;j++){if(e.results[j].isFinal)recognized.push(e.results[j][0].transcript)}const text=recognized.join(' ').trim();if(text){answers[i].text=text;answers[i].recognized=true;if(pos===i){$('transcript').value=text;$('feedback').hidden=true}}};
 r.onerror=()=>{if(pos===i)$('recognitionNote').textContent='Otomatik metin çözümlemesi başarısız. Ses kaydını dinleyip metni kendin girebilirsin.'};
 r.start()
 }catch(e){recognition=null}
}
$('record').onclick=async()=>{
 if(recorder&&recorder.state==='recording')return;
 if(!navigator.mediaDevices?.getUserMedia||!window.MediaRecorder){alert('Bu tarayıcı ses kaydını desteklemiyor. Güncel Chrome veya Edge deneyin.');return}
 haltVoice();
 try{
  stream=await navigator.mediaDevices.getUserMedia({audio:true});
  const type=['audio/webm;codecs=opus','audio/webm','audio/mp4'].find(t=>MediaRecorder.isTypeSupported(t))||'';
  recorder=new MediaRecorder(stream,type?{mimeType:type}:{});
  chunks=[];const i=pos;recordingIndex=i;
  recorder.ondataavailable=e=>{if(e.data.size)chunks.push(e.data)};
  recorder.onstop=()=>{const blob=new Blob(chunks,{type:recorder.mimeType||'audio/webm'});if(blob.size){if(answers[i].url)URL.revokeObjectURL(answers[i].url);answers[i].blob=blob;answers[i].url=URL.createObjectURL(blob)}cleanupRecorder();if(pos===i)render()};
  recorder.onerror=()=>{cleanupRecorder();$('recordState').textContent='Kayıt hatası'};
  recorder.start();$('record').disabled=true;$('stop').disabled=false;$('recordState').textContent='● Kayıt yapılıyor';
  beginRecognition(i);
 }catch(e){cleanupRecorder();alert('Mikrofona erişilemedi. Tarayıcının mikrofon iznini kontrol edin.')}
};
$('stop').onclick=()=>{if(recorder&&recorder.state!=='inactive')recorder.stop();if(recognition){try{recognition.stop()}catch(e){}recognition=null}};
$('transcript').addEventListener('input',updateText);
function normalize(s){return String(s||'').toLocaleLowerCase('tr-TR').normalize('NFC').replace(/[.,!?;:()\-]/g,' ').replace(/\s+/g,' ').trim()}
$('feedbackBtn').onclick=()=>{
 const a=answers[pos],result=grader.grade(pos,$('transcript').value,!!a.blob);
 $('feedback').replaceChildren();$('feedback').hidden=false;
 const heading=document.createElement('h3');heading.textContent='Transkripte göre ön kontrol';$('feedback').append(heading);
 const p=document.createElement('p');p.textContent=!a.blob?'Bu görevde ses kaydı yok.':result.untranscribed?'Ses kaydı var, ancak konuşma metni boş. Transkripti kontrol et.':'Beklenen dil işaretlerinden '+result.matched+'/'+result.total+' tanesi algılandı. Bu kontrol telaffuz veya akıcılığı ölçmez.';$('feedback').append(p);
 a.feedback=true;
};
$('exampleBtn').onclick=()=>{const e=$('example');e.hidden=!e.hidden;e.textContent='Örnek yanıt (tek doğru cevap değildir): '+tasks[pos].example};
$('clear').onclick=()=>{
 if(recorder&&recorder.state==='recording'){alert('Önce kaydı durdurun.');return}
 if(!confirm('Bu görevin ses kaydını ve metnini silmek istiyor musun?'))return;
 const a=answers[pos];if(a.url)URL.revokeObjectURL(a.url);answers[pos]={url:null,blob:null,text:'',recognized:false,feedback:false};render()
};
$('prev').onclick=()=>navigate(pos-1);$('next').onclick=()=>navigate(pos+1);
$('finish').onclick=()=>{
 if(recorder&&recorder.state==='recording'){alert('Önce ses kaydını bitir.');return}
 answers[pos].text=$('transcript').value;
 const grades=answers.map((a,i)=>grader.grade(i,a.text,!!a.blob));
 const missing=grades.filter(g=>!g.recorded).length,untranscribed=grades.filter(g=>g.untranscribed).length;
 if(!confirm((missing?missing+' soru kayıtsız. ':'')+(untranscribed?untranscribed+' kaydın transkripti boş; bu görevler puan alamaz. ':'')+'Sınavı bitirip otomatik puanı hesaplamak istiyor musun?'))return;
 haltVoice();$('recorded').pause();
 const completed=answeredCount(),earned=grades.reduce((s,g)=>s+g.earned,0);
 const correct=grades.filter(g=>g.earned===1).length,partial=grades.filter(g=>g.earned>0&&g.earned<1).length,wrong=grades.filter(g=>g.recorded&&!g.untranscribed&&g.earned===0).length,blank=missing+untranscribed;
 const now=new Date().toISOString();
 const stats={tasksCompleted:completed,totalTasks:30,updatedAt:now,assessmentStatus:'transcript_auto_scored',earned,possible:30,correct,partial,wrong,blank};
 try{
  localStorage.setItem('ta-speaking-a1-2-progress',JSON.stringify(stats));
  const key='ta-activities-A1-2',results=JSON.parse(localStorage.getItem(key))||{};
  results.speaking={earned,possible:30,completed:true,correct,partial,wrong,blank,tasksCompleted:completed,totalTasks:30,assessmentMethod:'transcript-keyword-rubric',updatedAt:now};
  localStorage.setItem(key,JSON.stringify(results))
 }catch(e){alert('Puan cihazda kaydedilemedi. Tarayıcının depolama ayarlarını kontrol et.')}
 $('test').classList.add('hidden');$('result').classList.remove('hidden');
 $('completion').textContent='%'+(earned/30*100).toFixed(1)+' · Transkript puanı';
 $('resultSummary').textContent='Tam doğru: '+correct+' · Kısmen doğru: '+partial+' · Yanlış: '+wrong+' · Boş / transkriptsiz: '+blank+' · Ses kaydı: '+completed+'/30';
 $('sectionResults').replaceChildren();sections.forEach((name,i)=>{const p=document.createElement('p');p.textContent=name+': '+grades.slice(i*5,i*5+5).reduce((s,g)=>s+g.earned,0).toFixed(2)+'/5 puan';$('sectionResults').append(p)});
 const review=$('taskReview');if(review){review.replaceChildren();grades.forEach((g,i)=>{const div=document.createElement('div');div.className='feedback';const heading=document.createElement('strong');heading.textContent=(i+1)+'. görev · '+(g.earned*100).toFixed(0)+' / 100';const p=document.createElement('p');p.textContent='Transkript: '+(answers[i].text.trim()||'(boş)')+' | Beklenen örnek: '+tasks[i].example;div.append(heading,p);review.append(div)})}
 window.scrollTo({top:0,behavior:'smooth'})
};
$('retry').onclick=()=>{$('result').classList.add('hidden');$('test').classList.remove('hidden');render()};
window.addEventListener('pagehide',()=>{haltVoice();if(stream)stream.getTracks().forEach(t=>t.stop());answers.forEach(a=>{if(a.url)URL.revokeObjectURL(a.url)})});
})();