/* Türkçe Akademi — account-scoped automatic progress synchronization. */
(function(){
'use strict';
const element=document.currentScript;
const keys=(element?.dataset.keys||'').split(',').map(x=>x.trim()).filter(Boolean);
if(!keys.length)return;
const api=()=>window.TAStudentCloud;
const path=location.pathname;
const hash=Array.from(path).reduce((h,c)=>Math.imul(h^c.charCodeAt(0),16777619)>>>0,2166136261).toString(36);
const remoteKey=k=>k.startsWith('ta-activities-')?k:'ta-sync-'+hash+'-'+k;
const localKey='ta-sync-account';
const originalSet=Storage.prototype.setItem,originalRemove=Storage.prototype.removeItem;
const initial=new Map(keys.map(k=>[k,localStorage.getItem(k)]));
let ready=false,accountId=null;
const pending=new Map();
const isResult=k=>k.startsWith('ta-activities-');
function serialize(k,value){return isResult(k)?JSON.parse(value):{value:String(value)}}
function restore(k,value) {
 if(value===null)return false;
 if(value&&value.deleted===true){
   if(localStorage.getItem(k)!==null){originalRemove.call(localStorage,k);return true}
   return false;
 }
 const next=isResult(k)?JSON.stringify(value):(value&&typeof value.value==='string'?value.value:null);
 if(next===null)return false;
 if(localStorage.getItem(k)===next)return false;
 originalSet.call(localStorage,k,next);return true;
}
async function commit(k,removed=false){
 const cloud=api();
 const u=await cloud.user();
 if(!u||u.id!==accountId)return;
 const val=localStorage.getItem(k);
 const payload=removed||val===null?{deleted:true}:serialize(k,val);
 await cloud.save(remoteKey(k),payload);
}
function queue(k,removed){
 if(!ready||!accountId||!keys.includes(k))return;
 clearTimeout(pending.get(k));
 pending.set(k,setTimeout(()=>commit(k,removed).catch(err=>console.warn('İlerleme kaydı başarısız:',err)),650));
}
Storage.prototype.setItem=function(k,v){const r=originalSet.call(this,k,v);if(this===localStorage)queue(k,false);return r};
Storage.prototype.removeItem=function(k){const r=originalRemove.call(this,k);if(this===localStorage)queue(k,true);return r};
async function initialize(){
 const cloud=api();if(!cloud?.ready)return;
 let user;
 try{user=await cloud.user()}catch(e){return}
 if(!user)return;
 accountId=user.id;
 const previous=localStorage.getItem(localKey);
 const otherAccount=Boolean(previous&&previous!==user.id);
 if(otherAccount)for(const k of keys){originalRemove.call(localStorage,k);initial.set(k,null)}
 originalSet.call(localStorage,localKey,user.id);
 let changed=otherAccount;
 try{
  for(const k of keys){
   const saved=await cloud.load(remoteKey(k));
   if(saved!==null){changed=restore(k,saved)||changed}
   else if(initial.get(k)!==null){await cloud.save(remoteKey(k),serialize(k,initial.get(k)))}
  }
 }catch(e){console.warn('Bulut ilerlemesi alınamadı:',e);return}
 ready=true;
 if(changed){location.reload();return}
 try{await cloud.save('ta-last-location',{path:location.pathname+location.search,updatedAt:new Date().toISOString()})}
 catch(e){console.warn('Son konum kaydı başarısız:',e)}
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',initialize,{once:true});
else initialize();
})();
