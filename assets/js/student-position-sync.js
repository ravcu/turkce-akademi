/* Student position sync: scoped by page URL and account.
   Only configured local keys are mirrored. Never sends passwords or other local storage. */
(function () {
'use strict';
const keys = (document.currentScript?.dataset?.keys || '').split(',').map(x=>x.trim()).filter(Boolean);
if(!keys.length)return;
const path = location.pathname.replace(/[^a-zA-Z0-9_-]/g,'_').slice(-110);
const originalSet = Storage.prototype.setItem;
const initial = new Map(keys.map(k=>[k,localStorage.getItem(k)]));
let ready=false, current=null;
const pending=new Map();
function remoteKey(key){return key.startsWith('ta-activities-') ? key : 'ta-sync-'+path+'-'+key.replace(/[^a-zA-Z0-9_-]/g,'_').slice(0,35)}
function start() {
 const api=window.TAStudentCloud;
 if(!api?.ready)return;
 api.user().then(async user=>{
   if(!user)return;
   current=user;
   let changed=false;
   const marker='ta-sync-account';
   const prior=localStorage.getItem(marker);
   if(prior && prior!==user.id){
     for(const key of keys){Storage.prototype.removeItem.call(localStorage,key);initial.set(key,null)}
     changed=true;
   }
   originalSet.call(localStorage,marker,user.id);
   try {
     for(const key of keys){
       const saved=await api.load(remoteKey(key));
       if(saved!==null && (key.startsWith('ta-activities-') || Object.prototype.hasOwnProperty.call(saved,'value'))){
         const val=key.startsWith('ta-activities-')?JSON.stringify(saved):String(saved.value);
         if(localStorage.getItem(key)!==val){originalSet.call(localStorage,key,val);changed=true}
       } else if(initial.get(key)!==null) {
         await api.save(remoteKey(key),key.startsWith('ta-activities-')?JSON.parse(initial.get(key)):{value:initial.get(key)});
       }
     }
   }catch(err){console.warn('Türkçe Akademi ilerleme yükleme hatası:',err)}
   ready=true;
   if(changed){location.reload();return;}
   try{await api.save('ta-last-location',{path:location.pathname+location.search,updatedAt:new Date().toISOString()})}catch(err){console.warn('Son konum kaydedilemedi:',err)}
 }).catch(err=>console.warn('Oturum kontrolü başarısız:',err));
}
Storage.prototype.setItem=function(key,value){
 originalSet.call(this,key,value);
 if(this!==localStorage||!keys.includes(key)||!ready||!current)return;
 clearTimeout(pending.get(key));
 pending.set(key,setTimeout(async()=>{
  try{const api=window.TAStudentCloud;const u=await api.user();if(u?.id===current.id)await api.save(remoteKey(key),key.startsWith('ta-activities-')?JSON.parse(localStorage.getItem(key)||'{}'):{value:String(localStorage.getItem(key))})}
  catch(err){console.warn('İlerleme kaydedilemedi:',err)}
 },850));
};
document.addEventListener('DOMContentLoaded',start,{once:true});
})();
