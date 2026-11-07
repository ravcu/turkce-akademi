/* Shared PDF workspace for all school levels. Keeps reader data and handlers intact. */
(()=>{'use strict';
if(/\/(sunum|deneme)\//.test(location.pathname))return;
function install(){
 const q=s=>document.querySelector(s),stage=q('#stage'),img=q('#pageImage'),book=q('.book'),reader=q('.reader'),sidebar=q('.side-stack'),shell=q('.shell');
 if(!stage||!img||!book||!reader||!sidebar||!shell||document.body.classList.contains('ta-unified-pdf'))return;
 const css=document.createElement('link');css.rel='stylesheet';css.href='/turkce-akademi/assets/css/pdf-workspace.css?v=20261108-2';document.head.append(css);
 const title=q('.heading h1')?.textContent||document.title.split('|')[0],eyebrow=q('.eyebrow')?.textContent||'Türkçe Kitabı';
 const oldHeader=q('header'),language=q('.ta-ui-language'),toolbar=q('.toolbar'),nav=q('.reader-actions')||q('.unit-navigation');
 const bar=document.createElement('header');bar.className='demo-bar';
 const name=document.createElement('div');name.className='demo-book-title';const level=document.createElement('small');level.textContent=eyebrow.replace(/Lise(?!-Yetişkin)/g,'Lise-Yetişkin');const heading=document.createElement('strong');heading.textContent=title;name.append(level,heading);bar.append(name);
 if(language)bar.append(language);if(nav){bar.append(nav);nav.querySelectorAll('.presentation-link').forEach(a=>a.hidden=true)}if(toolbar)bar.append(toolbar);
 const controls=document.createElement('div');controls.className='demo-controls';const full=document.createElement('button');full.id='demoFull';full.type='button';full.textContent='⛶ Tam ekran';controls.append(full);bar.append(controls);
 const brand=document.createElement('a');brand.className='academy-home';brand.href='/turkce-akademi/';brand.setAttribute('aria-label','Türkçe Akademi · Ana sayfaya dön');brand.innerHTML='<strong>TÜRKÇE AKADEMİ</strong><span class="academy-tagline">DÜNYANIN TÜRKÇE ÖĞRENME PLATFORMU</span><span class="academy-return">← Ana sayfaya dön</span>';bar.append(brand);
 if(oldHeader)oldHeader.replaceWith(bar);else document.body.prepend(bar);
 document.body.classList.add('ta-unified-pdf','demo-fit');
 let viewport=stage.parentElement.classList.contains('page-viewport')?stage.parentElement:null;
 if(!viewport){viewport=document.createElement('div');viewport.className='page-viewport';stage.before(viewport);viewport.append(stage)}
 const zone=document.createElement('div');zone.className='demo-page-zone';viewport.before(zone);zone.append(viewport);
 const arrows=[];for(const [id,label,target,cls,text] of [['demoPrev','Önceki sayfa','prev','demo-prev','‹'],['demoNext','Sonraki sayfa','next','demo-next','›']]){const b=document.createElement('button');b.id=id;b.type='button';b.className='demo-arrow '+cls;b.setAttribute('aria-label',label);b.textContent=text;b.onclick=()=>q('#'+target)?.click();zone.append(b);arrows.push([b,target])}
 const sideHeading=document.createElement('div');sideHeading.className='demo-panel-heading';sideHeading.textContent='KELİME VE ÜNİTE ÇALIŞMALARI';sidebar.prepend(sideHeading);sidebar.id='demoSidebar';
 const panel=sidebar.querySelector('.panel');if(panel){panel.style.flexShrink='0'}
 const exportActions=q('.page-export-actions');if(exportActions)sidebar.append(exportActions);
 let mode='fit',factor=1,frame=0;
 const scale=document.createElement('button');scale.id='demoScale';scale.type='button';scale.className='iconbtn pagecount';scale.title='Sayfanın tamamını ekrana sığdır';scale.setAttribute('aria-label','Sayfayı ekrana sığdır');q('#zoomOut')?.before(scale);scale.onclick=()=>{mode='fit';factor=1;layout()};
 function align(){const p=stage.getBoundingClientRect(),h=bar.getBoundingClientRect();if(p.width>0){const left=p.left+p.width/2-h.left;if(brand.style.left!==left+'px')brand.style.left=left+'px';zone.style.setProperty('--demo-page-half',p.width/2+'px')}}
 function layout(){cancelAnimationFrame(frame);frame=requestAnimationFrame(()=>{if(img.naturalWidth){const ratio=img.naturalHeight/img.naturalWidth;const width=Math.max(50,mode==='fit'?Math.min(viewport.clientWidth-2,(viewport.clientHeight-2)/ratio):680*factor);const px=Math.round(width)+'px';if(stage.style.width!==px)stage.style.width=px;stage.style.maxWidth='none';stage.style.margin='0 auto';scale.textContent=Math.round(width/680*100)+'%'}for(const [b,id]of arrows)b.disabled=!!q('#'+id)?.disabled;align()})}
 if(q('#zoomIn'))q('#zoomIn').onclick=()=>{factor=Math.min(2.4,factor+.1);mode='large';layout()};if(q('#zoomOut'))q('#zoomOut').onclick=()=>{factor=Math.max(.5,factor-.1);mode='large';layout()};
 full.onclick=async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen()}catch{const toast=q('#toast');if(toast){toast.textContent='Tam ekran için F11 tuşunu kullanabilirsiniz.';toast.classList.add('show');setTimeout(()=>toast.classList.remove('show'),2600)}}};
 document.addEventListener('fullscreenchange',()=>{full.textContent=document.fullscreenElement?'⛶ Tam ekrandan çık':'⛶ Tam ekran';layout()});
 const rail=q('#thumbrail');function syncPage(){viewport.scrollTop=0;viewport.scrollLeft=0;window.scrollTo(0,0);layout();const active=rail?.querySelector('.thumb.active');if(active&&rail){const top=active.offsetTop-rail.offsetTop;if(top<rail.scrollTop||top+active.offsetHeight>rail.scrollTop+rail.clientHeight)rail.scrollTo({top:Math.max(0,top-rail.clientHeight/2),behavior:'smooth'})}}
 if(q('#count'))new MutationObserver(syncPage).observe(q('#count'),{subtree:true,childList:true,characterData:true});
 if(rail)new MutationObserver(()=>{layout()}).observe(rail,{childList:true});
 new ResizeObserver(layout).observe(viewport);new ResizeObserver(align).observe(stage);new ResizeObserver(layout).observe(reader);
 img.addEventListener('load',layout);window.addEventListener('resize',layout);viewport.addEventListener('scroll',align,{passive:true});css.addEventListener('load',layout);
 if(nav){const summary=nav.querySelector('summary.unit-mark');if(summary){const number=(summary.textContent.match(/\d+/)||[])[0];if(number)summary.textContent=number+'. ÜNİTE';}}
 const mobileButton=document.createElement('button');mobileButton.className='ta-mobile-tools';mobileButton.textContent='Çalışma';mobileButton.type='button';mobileButton.setAttribute('aria-expanded','false');controls.prepend(mobileButton);
 const mobileClose=document.createElement('button');mobileClose.className='ta-mobile-close';mobileClose.type='button';mobileClose.textContent='×';mobileClose.setAttribute('aria-label','Çalışma panelini kapat');sideHeading.append(mobileClose);
 function mobilePanel(open){document.body.classList.toggle('ta-mobile-panel-open',open);mobileButton.setAttribute('aria-expanded',String(open));}
 mobileButton.onclick=()=>mobilePanel(!document.body.classList.contains('ta-mobile-panel-open'));mobileClose.onclick=()=>mobilePanel(false);
 q('#hotspots')?.addEventListener('click',e=>{if(innerWidth<=800&&e.target.closest('.word-hit'))mobilePanel(true)});
 layout();window.TAPdfWorkspace={version:1,layout,fit:()=>{mode='fit';layout()}};
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>setTimeout(install,0),{once:true});else setTimeout(install,0);
})();
