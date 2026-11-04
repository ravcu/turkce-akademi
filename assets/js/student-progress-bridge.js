/* Türkçe Akademi: Etkinlik sonuçlarını hesapla eşleştirme (yalnızca bağlı ünite). */
(async function(){
'use strict';
const api=window.TAStudentCloud;
if(!api?.ready)return;
let current;
try{current=await api.user()}catch(e){return}
if(!current)return;
const params=new URLSearchParams(location.search),level=(params.get('level')||'A1').toUpperCase(),unit=Math.max(1,Math.min(10,Number(params.get('unit'))||1));
const keys=['ta-activities-'+level+'-'+unit,'ta-certificate-'+level+'-'+unit];
let restoring=true;
try{
 const p=await api.profile();
 if(p?.first_name&&p?.last_name)localStorage.setItem('ta-student-name',p.first_name+' '+p.last_name);
 let changed=false;
 for(const key of keys){
   const remote=await api.load(key);
   if(remote!==null){
     const encoded=JSON.stringify(remote);
     if(localStorage.getItem(key)!==encoded){localStorage.setItem(key,encoded);changed=true}
   }
 }
 restoring=false;
 if(changed){location.reload();return;}
}catch(e){restoring=false;console.warn('Öğrenci ilerlemesi yüklenemedi:',e)}
const original=Storage.prototype.setItem;
const pending=new Map();
Storage.prototype.setItem=function(key,value){
 original.call(this,key,value);
 if(this!==localStorage||restoring||!keys.includes(key))return;
 clearTimeout(pending.get(key));
 pending.set(key,setTimeout(async()=>{
   try{const now=await api.user();if(now?.id!==current.id)return;await api.save(key,JSON.parse(localStorage.getItem(key)))}catch(e){console.warn('Öğrenci ilerlemesi kaydedilemedi:',e)}
 },650));
};
})();