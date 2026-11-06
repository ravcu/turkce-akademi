/* Türkçe Akademi — PDF Bakınız köprüleri */
(function(){
'use strict';
const root='/turkce-akademi/';
const destinations={
 'tanisalim':[2,8,5,8,8,11],
 'okuldayiz':[2,6,12,14,17,20],
 'ailem-ve-evim':[2,4,7,9,11],
 'bir-gunum':[2,5,7,14,14,16],
 'sehir-gezisi':[2,3,4,8,8],
 'carsi-pazar':[2,7,11,12,15,16],
 'bugun-hava-nasil':[2,5,8,15,17,20],
 'gecmis-olsun':[2,4,5,8],
 'davetlisiniz':[2,5,8,9,12,15],
 'tatil-planim':[2,3,6]
};
const destinationsA2={
 'tatil-donusu':[2,5,5,9,12,14],
 'hafta-sonu-planin-ne':[2,5,7,8,10],
 'bir-gunum':[2,5,7,8,11],
 'simdi-haberler':[2,5,6,8,11,14],
 'dedemin-meslegi':[2,4,7,8,10,12],
 'hayat-birlikte-guzel':[2,5,8,9,11],
 'akilli-teknoloji':[2,6,8,9,12],
 'spor-ve-saglik':[2,4,7,11,15,18],
 'bir-hikayem-var':[2,7,5,8,12]
};
const a2TargetSlugs={'spor-ve-saglik':'spor-yapiyorum-saglikli-besleniyorum'};
const pageMap=new Map();
let activeMapId=null;
function makeMap(slug,allPages,level){
 let count=0;
 const targets=(level==='a2'?destinationsA2:destinations)[slug]||[];
 pageMap.clear();
 activeMapId=level+'/'+slug;
 for(let p=0;p<allPages.length;p++){
  for(const w of (allPages[p].words||[]).filter(x=>/^Bakınız\s*:/i.test(x.t))){
   const target=targets[count++];
   if(Number.isInteger(target))pageMap.set(level+'/'+slug+'/'+(p+1)+'@'+w.x.toFixed(4)+'@'+w.y.toFixed(4),target);
  }
 }
 if(count!==targets.length)console.warn('Köprü sayısı kontrol edilmeli:',slug,count,targets.length);
}
function style(){
 if(document.getElementById('ta-pdf-bridge-style'))return;
 const el=document.createElement('style');el.id='ta-pdf-bridge-style';
 el.textContent='.ta-pdf-bridges{position:absolute;inset:0;z-index:8;pointer-events:none}.ta-pdf-bridge{position:absolute;pointer-events:auto;display:flex;align-items:center;gap:3px;padding:3px 8px;border:1px solid #008f96;border-radius:20px;background:#008f96;color:white;box-shadow:0 2px 6px #004c5255;font:800 11px/1.15 system-ui,sans-serif;height:24px;min-width:74px;box-sizing:border-box;justify-content:center;text-decoration:none;white-space:nowrap;cursor:pointer}.ta-pdf-bridge:hover,.ta-pdf-bridge:focus-visible{background:#006d72;outline:2px solid #ffcb78;outline-offset:1px}.ta-pdf-return{position:fixed;right:18px;bottom:18px;z-index:99999;background:#008f96;color:#fff!important;border:2px solid #fff;border-radius:22px;box-shadow:0 3px 12px #15343f55;padding:10px 16px;text-decoration:none;font:700 13px system-ui,sans-serif}.ta-pdf-return:hover,.ta-pdf-return:focus-visible{background:#00666b}@media print{.ta-pdf-bridges,.ta-pdf-return{display:none!important}}';
 document.head.append(el);
}
function hrefFor(slug,pdfPage,originPage,level){
 const pathSlug=level==='a2'?(a2TargetSlugs[slug]||slug):slug;
 const url=new URL(root+'kitaplar/lise-'+level+'-dilbilgisi/'+pathSlug+'/',location.origin);
 url.searchParams.set('page',String(pdfPage));
 const back=new URL(location.href);
 back.searchParams.set('page',String(originPage));
 url.searchParams.set('from',back.pathname+back.search);
 return url.pathname+url.search;
}
function renderSource(slug,pages,current,container,level='a1'){
 if(!container||!(level==='a2'?destinationsA2:destinations)[slug])return;
 style();
 if(activeMapId!==level+'/'+slug)makeMap(slug,pages,level);
 let layer=container.querySelector('.ta-pdf-bridges');
 if(!layer){layer=document.createElement('div');layer.className='ta-pdf-bridges';container.append(layer)}
 layer.replaceChildren();
 for(const marker of (pages[current]?.words||[]).filter(x=>/^Bakınız\s*:/i.test(x.t))){
   const key=level+'/'+slug+'/'+(current+1)+'@'+marker.x.toFixed(4)+'@'+marker.y.toFixed(4);
   const target=pageMap.get(key);
   if(!target)continue;
   // One standard placement for every unit: directly ABOVE the printed Bakınız line.
   // Pixel-based vertical clearance avoids touching the reference text at any zoom.
   const width=container.clientWidth||1000, height=container.clientHeight||1250;
   const buttonWidth=74,buttonHeight=24,gap=7;
   const top=Math.max(2,marker.y*height-buttonHeight-gap);
   const left=Math.min(width-buttonWidth-4,Math.max(4,marker.x*width+12));
   const a=document.createElement('a');a.className='ta-pdf-bridge';
   a.style.left=left+'px';a.style.top=top+'px';
   a.href=hrefFor(slug,target,current+1,level);
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