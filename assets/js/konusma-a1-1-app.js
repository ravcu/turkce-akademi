(()=>{'use strict';
const source=window.TA_SPEAKING_A1_1;if(!source||source.tasks.length!==30)throw Error('Konuşma görevleri yüklenemedi.');
const {sections,tasks}=source,$=id=>document.getElementById(id);
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
 const task=tasks[pos],a=answers[pos],text=normalize($('transcript').value);
 $('feedback').replaceChildren();$('feedback').hidden=false;const heading=document.createElement('h3');heading.textContent='Metne dayalı öğrenme geri bildirimi';$('feedback').append(heading);
 function line(t){const p=document.createElement('p');p.textContent=t;$('feedback').append(p)}
 if(!a.blob){line('Henüz bu görev için ses kaydı oluşturulmadı. Önce konuşmanı kaydet.');return}
 if(!text){line('Konuşma metni bulunamadı. Ses kaydını dinleyip metni kontrol ederek yazabilirsin.');return}
 const matches=task.terms.filter(t=>text.includes(normalize(t)));
 if(matches.length){line('İlgili anahtar ifadeler metinde bulundu: '+matches.slice(0,5).join(', ')+'.');line('Bu, görevin tam doğru yapıldığını kanıtlamaz. Söylediğin sözlerin anlamını öğretmeninle de kontrol et.')}
 else{line('Görevle ilgili beklenen anahtar ifadeler metinde bulunamadı. Soruyu tekrar dinleyip yanıtını gözden geçir.');line('Farklı ama doğru cevaplar da mümkündür; bu otomatik kontrol bunları her zaman tanıyamayabilir.')}
 line('Telaffuz ve akıcılık: Bu metinden güvenilir biçimde puanlanamaz. Ses kaydı üzerinden öğretmen kontrolü gerekir.');
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
 const missing=30-answeredCount();if(!confirm((missing?missing+' görevde kayıt yok. ':'')+'Etkinlik özetine geçilsin mi?'))return;
 haltVoice();if($('recorded'))$('recorded').pause();
 const completed=answeredCount();const stats={tasksCompleted:completed,totalTasks:30,updatedAt:new Date().toISOString(),assessmentStatus:'teacher_review_required'};
 try{localStorage.setItem('ta-speaking-a1-1-progress',JSON.stringify(stats));const key='ta-activities-A1-1';const results=JSON.parse(localStorage.getItem(key))||{};results.speaking={tasksCompleted:completed,totalTasks:30,assessmentStatus:'teacher_review_required',updatedAt:stats.updatedAt,completed:false};localStorage.setItem(key,JSON.stringify(results))}catch(e){}
 $('test').classList.add('hidden');$('result').classList.remove('hidden');
 $('completion').textContent=completed+' / 30 görevde ses kaydı';
 $('resultSummary').textContent='Tamamlanan görev: '+completed+' · Eksik görev: '+missing+' · Konuşma puanı: öğretmen değerlendirmesi bekleniyor.';
 $('sectionResults').replaceChildren();sections.forEach((s,i)=>{const p=document.createElement('p');p.textContent=s+': '+answers.slice(i*5,i*5+5).filter(a=>a.blob).length+' / 5 kayıt';$('sectionResults').append(p)});
 window.scrollTo({top:0,behavior:'smooth'})
};
$('retry').onclick=()=>{$('result').classList.add('hidden');$('test').classList.remove('hidden');render()};
window.addEventListener('pagehide',()=>{haltVoice();if(stream)stream.getTracks().forEach(t=>t.stop());answers.forEach(a=>{if(a.url)URL.revokeObjectURL(a.url)})});
})();