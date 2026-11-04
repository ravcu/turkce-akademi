/* Türkçe Akademi — future content progress integration.
   New HTML pages: automatically identifies ta-* student progress keys.
   Pages with the existing dedicated sync use that sync instead.
   Do not persist credentials, profile names or unmarked free-form fields. */
(function(){
'use strict';
if(window.TAProgressAuto)return;
const site='/turkce-akademi/';
if(!location.pathname.startsWith(site)||/\/ogrenci-girisi\.html$/.test(location.pathname))return;
const pageId=Array.from(location.pathname).reduce((h,c)=>Math.imul(h^c.charCodeAt(0),16777619)>>>0,2166136261).toString(36);
const prefix='ta-auto-'+pageId+'-';
const sensitive=/(?:auth|token|secret|password|passwd|email|session|credential|supabase|student-name|sync-account|api-key)/i;
const keyAllowed=k=>typeof k==='string'&&k.startsWith('ta-')&&k.length<=130&&!sensitive.test(k)&&!k.startsWith('ta-auto-')&&!k.startsWith('ta-sync-')&&k!=='ta-last-location';
const originalSet=Storage.prototype.setItem,originalRemove=Storage.prototype.removeItem;
const api={ready:false,save:async()=>false,load:async()=>null};
window.TAProgressAuto=api;
const keys=new Set(),timers=new Map();
let cloud=null,userId=null,active=false,restoring=false;
const remoteKey=k=>prefix+k;
function readInitial(){
 for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(keyAllowed(k))keys.add(k)}
}
readInitial();
function write(k,v,removed=false){
 if(!keyAllowed(k))return;
 keys.add(k);
 if(!active||restoring)return;
 clearTimeout(timers.get(k));
 timers.set(k,setTimeout(async()=>{
  try{
   const user=await cloud.user();if(!user||user.id!==userId)return;
   const value=localStorage.getItem(k);
   await cloud.save(remoteKey(k),removed||value===null?{deleted:true}:{value});
  }catch(e){console.warn('Otomatik ilerleme kaydedilemedi:',e)}
 },700));
}
Storage.prototype.setItem=function(k,v){
 const result=originalSet.call(this,k,v);
 if(this===localStorage)write(k,v,false);
 return result
};
Storage.prototype.removeItem=function(k){
 const result=originalRemove.call(this,k);
 if(this===localStorage)write(k,null,true);
 return result
};
function script(src){
 return new Promise((resolve,reject)=>{
  const el=document.createElement('script');el.src=src;el.onload=resolve;el.onerror=reject;document.head.append(el)
 })
}
async function init(){
 // Existing readers/tests are already linked to a specific audited progress schema.
 if(document.querySelector('script[src*="student-position-sync.js"],script[src*="student-progress-bridge.js"]'))return;
 try{
  if(!window.TA_SUPABASE_URL||!window.TA_SUPABASE_ANON_KEY)await script(site+'assets/js/supabase-config.js');
  if(!window.supabase)await script('https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.min.js');
  if(!window.TAStudentCloud?.ready)await script(site+'assets/js/student-cloud.js');
  cloud=window.TAStudentCloud;
  if(!cloud?.ready)return;
  const user=await cloud.user();if(!user)return;
  userId=user.id;
  const marker='ta-sync-account',prior=localStorage.getItem(marker);
  const changedUser=Boolean(prior&&prior!==userId);
  restoring=true;
  if(changedUser)for(const k of keys)originalRemove.call(localStorage,k);
  originalSet.call(localStorage,marker,userId);
  readInitial();
  const {data,error}=await cloud.client.from('student_progress')
    .select('progress_key,payload').eq('user_id',userId)
    .like('progress_key',prefix+'%').limit(500);
  if(error)throw error;
  let changed=changedUser;
  const returned=new Set();
  for(const record of data||[]){
   const key=record.progress_key.slice(prefix.length);
   if(!keyAllowed(key))continue;
   returned.add(key);keys.add(key);
   if(record.payload?.deleted===true){
    if(localStorage.getItem(key)!==null){originalRemove.call(localStorage,key);changed=true}
   }else if(typeof record.payload?.value==='string'&&localStorage.getItem(key)!==record.payload.value){
    originalSet.call(localStorage,key,record.payload.value);changed=true
   }
  }
  for(const k of keys){
   if(!returned.has(k)&&localStorage.getItem(k)!==null&&!changedUser){
    await cloud.save(remoteKey(k),{value:localStorage.getItem(k)})
   }
  }
  restoring=false;active=true;api.ready=true;
  api.save=async(id,payload)=>{
   if(!/^[\w-]{1,80}$/.test(id))throw Error('Geçersiz ilerleme kimliği');
   const current=await cloud.user();if(current?.id!==userId)return false;
   return cloud.save(prefix+'event-'+id,payload)
  };
  api.load=async id=>{
   if(!/^[\w-]{1,80}$/.test(id))throw Error('Geçersiz ilerleme kimliği');
   const current=await cloud.user();if(current?.id!==userId)return null;
   return cloud.load(prefix+'event-'+id)
  };
  await cloud.save('ta-last-location',{path:location.pathname+location.search,updatedAt:new Date().toISOString()});
  // Fresh pages can use the generic data-ta-progress attribute for input drafts.
  document.querySelectorAll('form[data-ta-progress]').forEach(form=>{
   const id=form.dataset.taProgress;
   if(!/^[\w-]{1,70}$/.test(id))return;
   const formKey='ta-form-'+pageId+'-'+id;
   const allowed=el=>['INPUT','TEXTAREA','SELECT'].includes(el.tagName)&&!!el.name&&!/password|email|hidden|file/i.test(el.type||'')&&!sensitive.test(el.name);
   const fields=()=>[...form.elements].filter(allowed);
   const saved=localStorage.getItem(formKey);
   if(saved){try{
    const values=JSON.parse(saved);
    for(const el of fields())if(Object.hasOwn(values,el.name)){
     if(el.type==='checkbox'||el.type==='radio')el.checked=values[el.name]===el.value;
     else el.value=String(values[el.name]);
    }
   }catch(e){}}
   const store=()=>{
    const data={};
    for(const el of fields()){
     if(el.type==='radio'||el.type==='checkbox'){if(el.checked)data[el.name]=el.value}
     else data[el.name]=el.value;
    }
    originalSet.call(localStorage,formKey,JSON.stringify(data));
    write(formKey,null,false)
   };
   form.addEventListener('input',store);
   form.addEventListener('change',store);
  });
  if(changed)location.reload();
 }catch(e){restoring=false;console.warn('Otomatik öğrenci ilerleme bağlantısı kurulamadı:',e)}
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();