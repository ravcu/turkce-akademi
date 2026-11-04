/* Türkçe Akademi — etkinlik puanı, sertifika ve ad-soyad eşitleme */
(async function(){
'use strict';
const api=window.TAStudentCloud;if(!api?.ready)return;
const qs=new URLSearchParams(location.search);
const level=['A1','A2','B1','B2','C1'].includes((qs.get('level')||'').toUpperCase())?qs.get('level').toUpperCase():'A1';
const unit=Math.max(1,Math.min(10,parseInt(qs.get('unit'),10)||1));
const keys=['ta-activities-'+level+'-'+unit,'ta-certificate-'+level+'-'+unit];
const set=Storage.prototype.setItem,remove=Storage.prototype.removeItem;
let uid=null,ready=false;const pending=new Map();
async function persist(key,deleted){
 const u=await api.user();if(!u||u.id!==uid)return;
 const val=localStorage.getItem(key);
 await api.save(key,deleted||val===null?{deleted:true}:JSON.parse(val));
}
function enqueue(key,deleted){
 if(!ready||!keys.includes(key))return;
 clearTimeout(pending.get(key));
 pending.set(key,setTimeout(()=>persist(key,deleted).catch(e=>console.warn('Etkinlik bulut kaydı:',e)),650));
}
Storage.prototype.setItem=function(k,v){const r=set.call(this,k,v);if(this===localStorage)enqueue(k,false);return r};
Storage.prototype.removeItem=function(k){const r=remove.call(this,k);if(this===localStorage)enqueue(k,true);return r};
try{
 const u=await api.user();if(!u)return;uid=u.id;
 const marker='ta-sync-account',prior=localStorage.getItem(marker);
 let changed=false;
 if(prior&&prior!==uid){
  for(const k of Object.keys(localStorage)){
   if(k==='ta-student-name'||k.startsWith('ta-activities-')||k.startsWith('ta-certificate-')||k.startsWith('ta-sync-'))remove.call(localStorage,k);
  }
  changed=true;
 }
 set.call(localStorage,marker,uid);
 const profile=await api.profile();
 if(profile?.first_name&&profile?.last_name){
  const name=profile.first_name.trim()+' '+profile.last_name.trim();
  if(localStorage.getItem('ta-student-name')!==name){set.call(localStorage,'ta-student-name',name);changed=true}
 }
 const remote=await api.loadMany(keys);
 for(const k of keys){
  if(remote.has(k)){
   const v=remote.get(k);
   if(v?.deleted===true){if(localStorage.getItem(k)!==null){remove.call(localStorage,k);changed=true}}
   else if(localStorage.getItem(k)!==JSON.stringify(v)){set.call(localStorage,k,JSON.stringify(v));changed=true}
  }else{
   const local=localStorage.getItem(k);
   if(local!==null)await api.save(k,JSON.parse(local));
  }
 }
 ready=true;
 if(changed){location.reload();return}
 try{await api.save('ta-last-location',{path:location.pathname+location.search,updatedAt:new Date().toISOString()})}catch(e){}
}catch(e){console.warn('Etkinlik senkronizasyonu yapılamadı:',e)}
})();