const fs=require('fs'),path=require('path');const r=path.join(__dirname,'../kitaplar/lise-a2/simdi-haberler');
const html=fs.readFileSync(path.join(r,'index.html'),'utf8'),pages=JSON.parse(fs.readFileSync(path.join(r,'pages.json'))),glossary=JSON.parse(fs.readFileSync(path.join(r,'translations.json')));
let errors=[];
for(const m of html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)){try{new Function(m[1])}catch(e){errors.push('Syntax: '+e.message)}}
function segment(name,end){return html.slice(html.indexOf('function '+name+'('),html.indexOf(end,html.indexOf('function '+name+'(')));}
const funcs=segment('normalize','function cleanLeadingDashes')+segment('cleanLeadingDashes','function showToast')+segment('phraseAt','function setSelected')+segment('renderSelection','function selectWord')+segment('escapeHtml','function numberToEnglish')+segment('numberToEnglish','const speechLanguages')+segment('exportCurrentPageWords',"$('#exportPageWords')");
const harness=new Function('pages','glossary',`
const LANGS=[['en','🇬🇧','English'],['ru','🇷🇺','Русский'],['ky','🇰🇬','Кыргызча'],['ar','🇸🇦','العربية'],['fr','🇫🇷','Français']];
let current=0,targetLang='en',activeSelection=null,printed='';const body={innerHTML:'',querySelectorAll:()=>[]};
const node={disabled:false,textContent:''};const $=()=>node;const isSaved=()=>false,updateLanguageTabs=()=>{},alignStudyArea=()=>{},requestAnimationFrame=()=>{},setTimeout=()=>{},showToast=()=>{};
const window={open:()=>({document:{open:()=>{},write:x=>{printed=x},close:()=>{}},focus:()=>{},print:()=>{}})};
${funcs}
const originalPhraseAt=phraseAt,cache=new Map();phraseAt=(i,words)=>{const key=current+':'+i;if(!cache.has(key))cache.set(key,originalPhraseAt(i,words));return cache.get(key)};
return {test:(pi,i,lang)=>{current=pi;targetLang=lang;const w=pages[pi].words[i],p=phraseAt(i,pages[pi].words);const key=p?p.key:(w.entryKey||normalize(w.t));activeSelection={key,text:cleanLeadingDashes(p?p.text:w.t),phrase:!!p&&(!p.single||!!glossary.phrases?.[key])};renderSelection();return {key,html:body.innerHTML,selection:activeSelection,phrase:p};},export:(pi,lang)=>{current=pi;targetLang=lang;printed='';exportCurrentPageWords();return printed;}};
`)(pages,glossary);
const langs=['en','ru','ky','ar','fr'];let selections=new Set(),checked=0,exportCount=0;
for(let pi=0;pi<pages.length;pi++){
 const page=pages[pi];if(page.page!==pi+1||page.bookPage!==77+pi)errors.push('page order '+pi);
 for(const group of [...page.wordGroups,...page.phraseGroups])for(const i of group.indices)if(!page.words[i])errors.push('bad index '+pi+':'+i);
 for(let i=0;i<page.words.length;i++){
  const w=page.words[i];if(!/[\p{L}\p{N}]/u.test(w.t))continue;
  if([w.x,w.y,w.w,w.h].some(v=>!Number.isFinite(v))||w.x<0||w.y<0||w.x+w.w>1.002||w.y+w.h>1.002)errors.push('geometry '+pi+':'+w.t);
  for(const lang of langs){const result=harness.test(pi,i,lang);checked++;if(!/[\p{L}]/u.test(w.t)||/^[\d\s:.,°\-]+$/.test(w.t))continue;
   selections.add(result.key);if(result.html.includes('henüz hazırlanmadı')||result.html.includes('Çeviri kontrol ediliyor'))errors.push('missing '+(pi+1)+':'+w.t+':'+lang+':'+result.key);
  }
 }
 for(const lang of langs){const content=harness.export(pi,lang);exportCount++;if(!content.includes('<tbody>')||content.includes('çeviri kontrol edilecek'))errors.push('export '+(pi+1)+':'+lang);}
}
for(const [key,f] of Object.entries(glossary.forms)){if(!Array.isArray(f.lemmaTranslations)||f.lemmaTranslations.length!==5)errors.push('root '+key);}
// Regression cases where the same Turkish spelling has another sense in earlier units.
if(glossary.words['mısır']?.[0]!=='Egypt (country)')errors.push('Egypt sense');
if(glossary.forms['yer']||glossary.words['yer']?.[0]!=='place; space')errors.push('place sense');
if(glossary.forms['kullanım']?.lemmaTranslations?.[0]!=='to use')errors.push('infinitive root');
for(let pi=0;pi<pages.length;pi++)for(const group of pages[pi].phraseGroups)for(const i of group.indices){
 if(harness.test(pi,i,'en').key!==group.key)errors.push('phrase consistency '+pi+':'+group.key);
}
const result={pages:pages.length,hotspots:pages.reduce((a,p)=>a+p.words.length,0),logicalSelections:selections.size,checked,exportChecks:exportCount,forms:Object.keys(glossary.forms).length,phraseEntries:Object.keys(glossary.phrases).length,phraseOccurrences:pages.reduce((a,p)=>a+p.phraseGroups.length,0),errors:[...new Set(errors)]};
console.log(JSON.stringify(result,null,2));if(errors.length)process.exitCode=1;
