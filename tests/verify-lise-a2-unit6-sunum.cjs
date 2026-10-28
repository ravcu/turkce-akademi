const fs=require('fs'),path=require('path'),assert=require('assert');
const root=path.resolve(__dirname,'../kitaplar/lise-a2/hayat-birlikte-guzel/sunum');
const slides=JSON.parse(fs.readFileSync(root+'/manifest.json')).slides;
const g=JSON.parse(fs.readFileSync(root+'/translations.json'));
const html=fs.readFileSync(root+'/index.html','utf8');
assert.equal(slides.length,77);
assert(html.includes("fetch('translations.json?v="),'presentation supplement must load');
assert(html.includes('showWord(w.phrase||w.text)'),'phrase selection must be retained');
const used=new Set();let selections=0;
function values(key){const p=g.phrases?.[key],f=g.forms?.[key],e=g.examples?.[key];return [p?.translations||f?.formTranslations||g.words?.[key],p?.exampleTr||f?.exampleTr||(Array.isArray(e)?e[0]:e?.tr),p?.examples||f?.examples||(Array.isArray(e)?e[1]:e?.values)];}
for(const [i,s] of slides.entries()){
 assert(fs.statSync(path.join(root,s.image)).size>100,'missing slide '+(i+1));
 if(s.answers)assert(fs.statSync(path.join(root,s.answers)).size>100);
 for(const a of s.audio)assert(fs.statSync(path.join(root,a)).size>100);
 for(const w of s.words){
  for(const k of ['x','y','w','h'])assert(Number.isFinite(w[k]),k+' '+i);
  assert(w.x>=0&&w.y>=0&&w.w>0&&w.h>0&&w.x+w.w<=100.1&&w.y+w.h<=100.1,'invalid area '+i+' '+w.text);
  assert((w.w<=32||(i===2&&w.text==='hayat birlikte güzel'&&w.w<=60))&&w.h<=11,'oversized OCR area '+i+' '+w.text);
  used.add(w.phrase||w.text);selections++;
 }
}
for(const key of used){const [m,tr,ex]=values(key);assert(Array.isArray(m)&&m.length===5&&m.every(t=>typeof t==='string'&&t.trim()),'meaning '+key);assert(tr?.trim(),'example '+key);assert(Array.isArray(ex)&&ex.length===5&&ex.every(t=>typeof t==='string'&&t.trim()),'translated example '+key);assert(/[а-яА-ЯёЁ]/.test(m[1])&&/[а-яА-ЯөӨүҮңҢ]/.test(m[2])&&/[\u0600-\u06ff]/.test(m[3])&&!/[\u0600-\u06ffа-яА-Я]/.test(m[4]),'language order '+key);}
for(const [page,keys] of [[16,['dönerken','sinyal','vermeli','öğrenmeli']],[28,['fadime','galoş','giymemiz']],[39,['puan','sürüyorsun','görebiliriz']],[77,['kahveyi','yudum','yerleştirilir','şahitlikleri']]])for(const key of keys)assert(slides[page-1].words.some(w=>w.text===key),'missing restored selection '+page+' '+key);
assert(selections>=4000);
console.log(JSON.stringify({slides:slides.length,selections,selectedEntries:used.size,languages:5,missingMeaningsOrExamples:0}));
