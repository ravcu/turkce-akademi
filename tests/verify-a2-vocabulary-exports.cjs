/* Exercise the reader's real boot, selection and print functions for all A2 units. */
const fs=require('fs'),path=require('path'),assert=require('assert');
const root=path.join(__dirname,'../kitaplar/lise-a2');
const slugs=['tatil-donusu','hafta-sonu-planin-ne','bir-gunum','simdi-haberler','dedemin-meslegi','hayat-birlikte-guzel','akilli-teknoloji'];
const langs=['en','ru','ky','ar','fr'];let totalExports=0,totalRows=0;const summary=[];
const decode=s=>s.replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"').replace(/&#39;/g,"'");
for(const [unitIndex,slug] of slugs.entries()){
 const unit=unitIndex+1;if(process.env.A2_UNITS&&!process.env.A2_UNITS.split(',').includes(String(unit)))continue;const r=path.join(root,slug),html=fs.readFileSync(path.join(r,'index.html'),'utf8');
 const pages=JSON.parse(fs.readFileSync(path.join(r,'pages.json'))),glossary=JSON.parse(fs.readFileSync(path.join(r,'translations.json')));
 const source=fs.existsSync(path.join(r,'source-text.json'))?JSON.parse(fs.readFileSync(path.join(r,'source-text.json'))):null;
 for(const m of html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g))assert.doesNotThrow(()=>new Function(m[1]),slug+' script syntax');
 function seg(name,end){const start=html.indexOf('function '+name+'('),finish=html.indexOf(end,start);assert(start>=0&&finish>=0);return html.slice(start,finish)}
 const funcs=seg('normalize','function cleanLeadingDashes')+seg('cleanLeadingDashes','function showToast')+seg('phraseAt','function setSelected')+seg('escapeHtml','function numberToEnglish')+seg('numberToEnglish','const speechLanguages')+seg('exportCurrentPageWords',"$('#exportPageWords')")+html.match(/function selectWord\([^\n]+/)[0];
 const bootStart=html.indexOf('pages=data;glossary=words;'),boot=html.slice(bootStart,html.indexOf('makeThumbs();',bootStart));
 const harness=new Function('pages','glossary','source',`
 const LANGS=[['en','🇬🇧','English'],['ru','🇷🇺','Русский'],['ky','🇰🇬','Кыргызча'],['ar','🇸🇦','العربية'],['fr','🇫🇷','Français']];
 let current=0,targetLang='en',printed='',activeWord='',activeSelection=null;
 const window={open:()=>({document:{open(){},write(s){printed=s},close(){}},focus(){},print(){}})},setTimeout=()=>{},showToast=()=>{},setSelected=()=>{},renderSelection=()=>{},$=()=>({});
 ${funcs}
 const data=pages,words=glossary,UNIT_ANSWERS={};${boot}
 const originalPhraseAt=phraseAt,cache=new Map();phraseAt=(i,w)=>{const k=current+':'+i;if(!cache.has(k))cache.set(k,originalPhraseAt(i,w));return cache.get(k)};
 return {print:(i,l)=>{current=i;targetLang=l;printed='';exportCurrentPageWords();return printed;},select:(pi,i)=>{current=pi;selectWord(pages[pi].words[i].t,i,pages[pi].words);return activeSelection;}};
 `)(pages,glossary,source);
 function columns(x,p){
  if(Array.isArray(x)){
   if(x.length===5&&x.every(v=>typeof v==='string')){
    assert(x.every(v=>v.trim()),p+' empty translation');
    assert(!/[\u0400-\u04ff\u0600-\u06ff]/.test(x[0]+x[4])&&!/[\u0400-\u04ff]/.test(x[3]),p+' shifted language columns');
   }else x.forEach((v,i)=>columns(v,p+':'+i));
  }else if(x&&typeof x==='object')Object.entries(x).forEach(([k,v])=>columns(v,p+':'+k));
 }
 columns(glossary,slug);
 let rowCount=0;const outputs=[];
 for(let pi=0;pi<pages.length;pi++){
  outputs[pi]={};
  for(const lang of langs){
   const out=harness.print(pi,lang);totalExports++;
   assert(out.includes('<tbody>'),`${slug}:${pi+1}:${lang} no print table`);
   assert(!out.includes('çeviri kontrol edilecek'),`${slug}:${pi+1}:${lang} missing translation`);
   const rows=[...out.matchAll(/<tr><td lang="tr">([\s\S]*?)<\/td><td lang="[^"]+"[^>]*>([\s\S]*?)<\/td><\/tr>/g)].map(m=>({text:decode(m[1]),meaning:decode(m[2])}));
   assert(rows.length,`${slug}:${pi+1}:${lang} empty list`);outputs[pi][lang]=rows;rowCount+=rows.length;
  }
 }
 // Homographs must select the occurrence's intended sense and print that same meaning.
 const cases=unit===1?[[4,47,'kalın:emir'],[7,119,'kalın']]:unit===3?[[1,107,'yer:mekan'],[3,145,'yer:mekan'],[23,98,'yer:mekan'],[0,34,'yer']]:unit===5?[[16,63,'yazı:para'],[16,64,'tura:para'],[17,127,'yazı']]:unit===6?[[13,153,'yaz:emir']]:unit===7?[[14,142,'yaz:emir'],[14,166,'yaz:emir'],[14,176,'yaz:emir'],[14,182,'yaz:emir'],[7,115,'sağ:esen'],[7,307,'sağ:esen'],[13,195,'sağ:esen'],[16,37,'sağ']]:[];
 for(const [pi,i,key] of cases){
  const s=harness.select(pi,i);assert(s.key===key||s.phrase,`${slug}:${pi+1} selection ${s.key} != ${key}`);
  langs.forEach((lang,li)=>{const meaning=glossary.forms?.[key]?.formTranslations?.[li]||glossary.words[key]?.[li];assert(outputs[pi][lang].some(r=>r.meaning===meaning),`${slug}:${pi+1}:${lang} wrong contextual export for ${key}`)});
 }
 if(unit===2){for(const lang of langs){assert(!outputs[20][lang].some(r=>['likler','yapı-','lıyor?'].includes(r.text)),'split wrapped word');assert(outputs[20][lang].some(r=>r.text.replace(/[?!.]+$/,'')==='yapılıyor'),'missing joined word')}}
 if(unit===5){for(const page of outputs)for(const lang of langs)assert(!page[lang].some(r=>/^[*/]|[=/]$/.test(r.text)||['yüzden/bu','sebeple/çünkü'].includes(r.text)),'exercise markup in vocabulary list');assert.deepStrictEqual(glossary.words.aile,['family','семья','үй-бүлө','عائلة','famille'])}
 summary.push({unit,pages:pages.length,exports:pages.length*5,rows:rowCount});totalRows+=rowCount;
 console.log(JSON.stringify(summary.at(-1)));
}
console.log(JSON.stringify({pages:summary.reduce((s,x)=>s+x.pages,0),exports:totalExports,rows:totalRows,errors:0}));
