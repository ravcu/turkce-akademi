/* Türkçe Akademi — PDF Bakınız köprüleri */
(function(){
'use strict';
const root='/turkce-akademi/';
const destinations={
 'tanisalim':[2,6,5,8,8,11],
 'okuldayiz':[2,6,12,14,17,20],
 'ailem-ve-evim':[2,4,7,9,11],
 'bir-gunum':[2,5,7,11,13,16],
 'sehir-gezisi':[2,3,4,5,8],
 'carsi-pazar':[2,7,11,12,15,16],
 'bugun-hava-nasil':[2,5,8,15,17,20],
 'gecmis-olsun':[2,4,5,8],
 'davetlisiniz':[2,5,8,9,12,15],
 'tatil-planim':[2,3,6]
};
const pageMap=new Map();
function makeMap(slug,allPages){
 let count=0;
 const targets=destinations[slug]||[];
 for(let p=0;p<allPages.length;p++){
  for(const w of (allPages[p].words||[]).filter(x=>/^Bakınız\s*:/i.test(x.t))){
   const target=targets[count++];
   if(Number.isInteger(target))pageMap.set((p+1)+'@'+w.x.toFixed(4)+'@'+w.y.toFixed(4),target);
  }
 }
 if(count!==targets.length)console.warn('Köprü sayısı kontrol edilmeli:',slug,count,targets.length);
}
function style(){
 if(document.getElementById('ta-pdf-bridge-style'))return;
 const el=document.createElement('style');el.id='ta-pdf-bridge-style';
 el.textContent='.ta-pdf-bridges{position:absolute;inset:0;z-index:8;pointer-events:none}.ta-pdf-bridge{position:absolute;pointer-events:auto;display:flex;align-items:center;gap:3px;padding:3px 8px;border:1px solid #008f96;border-radius:20px;background:#008f96;color:white;box-shadow:0 2px 6px #004c5255;font:800 clamp(7px,.95cqw,12px)/1.2 system-ui,sans-serif;text-decoration:none;white-space:nowrap;transform:translateY(-8%);cursor:pointer}.ta-pdf-bridge:hover,.ta-pdf-bridge:focus-visible{background:#006d72;outline:2px solid #ffcb78;outline-offset:1px}.ta-pdf-return{position:fixed;right:18px;bottom:18px;z-index:99999;background:#008f96;color:#fff!important;border:2px solid #fff;border-radius:22px;box-shadow:0 3px 12px #15343f55;padding:10px 16px;text-decoration:none;font:700 13px system-ui,sans-serif}.ta-pdf-return:hover,.ta-pdf-return:focus-visible{background:#00666b}@media print{.ta-pdf-bridges,.ta-pdf-return{display:none!important}}';
 document.head.append(el);
}
function hrefFor(slug,pdfPage,originPage){
 const url=new URL(root+'kitaplar/lise-a1-dilbilgisi/'+slug+'/',location.origin);
 url.searchParams.set('page',String(pdfPage));
 const back=new URL(location.href);
 back.searchParams.set('page',String(originPage));
 url.searchParams.set('from',back.pathname+back.search);
 return url.pathname+url.search;
}
function renderSource(slug,pages,current,container){
 if(!container||!destinations[slug])return;
 style();
 if(!pageMap.size)makeMap(slug,pages);
 let layer=container.querySelector('.ta-pdf-bridges');
 if(!layer){layer=document.createElement('div');layer.className='ta-pdf-bridges';container.append(layer)}
 layer.replaceChildren();
 for(const marker of (pages[current]?.words||[]).filter(x=>/^Bakınız\s*:/i.test(x.t))){
   const key=(current+1)+'@'+marker.x.toFixed(4)+'@'+marker.y.toFixed(4);
   const target=pageMap.get(key);
   if(!target)continue;
   const left=marker.x>.5?Math.min(marker.x+.15,.83):Math.min(marker.x+.28,.76);
   const top=marker.y>.84?Math.max(.01,marker.y-.045):Math.min(.95,marker.y+.025);
   const a=document.createElement('a');a.className='ta-pdf-bridge';
   a.style.left=(left*100)+'%';a.style.top=(top*100)+'%';
   a.href=hrefFor(slug,target,current+1);
   a.textContent='↗ TIKLA';
   a.title='Dil Bilgisi ve Telaffuz Kitabı – ilgili konunun olduğu sayfaya git';
   a.setAttribute('aria-label','Dil Bilgisi ve Telaffuz Kitabının ilgili konusunu aç');
   layer.append(a);
 }
}
function resolveInitialPage(pages,fallback){
 const params=new URLSearchParams(location.search);
 const value=params.get('page');
 if(value&&/^\d{1,4}$/.test(value)){
  const num=Number(value);
  if(num>=1&&num<=pages.length)return num-1;
 }
 return fallback;
}
function returnLink(){
 const value=new URLSearchParams(location.search).get('from');
 if(!value||!value.startsWith(root+'kitaplar/')||value.includes('//')||/[<>"']/.test(value))return;
 let link;
 try{link=new URL(value,location.origin);if(link.origin!==location.origin||!link.pathname.startsWith(root+'kitaplar/'))return}catch{return}
 style();
 const a=document.createElement('a');a.className='ta-pdf-return';a.href=link.pathname+link.search;
 a.textContent='← Ders Kitabına Dön';a.title='Ders kitabındaki önceki sayfayı aç';
 document.body.append(a);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',returnLink,{once:true});else returnLink();
window.TAPdfBridge={renderSource,resolveInitialPage};
})();