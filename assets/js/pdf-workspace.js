/* Shared PDF workspace for all school levels. Keeps reader data and handlers intact. */
(()=>{'use strict';
if(/\/(sunum|deneme)\//.test(location.pathname))return;
function install(){
 const q=s=>document.querySelector(s),stage=q('#stage'),img=q('#pageImage'),book=q('.book'),reader=q('.reader'),sidebar=q('.side-stack'),shell=q('.shell');
 if(!stage||!img||!book||!reader||!sidebar||!shell||document.body.classList.contains('ta-unified-pdf'))return;
 const css=document.createElement('link');css.rel='stylesheet';css.href='/turkce-akademi/assets/css/pdf-workspace.css?v=20261108-mobile3';document.head.append(css);
 const title=q('.heading h1')?.textContent||document.title.split('|')[0],eyebrow=q('.eyebrow')?.textContent||'Türkçe Kitabı';
 const oldHeader=q('header'),language=q('.ta-ui-language'),toolbar=q('.toolbar'),nav=q('.reader-actions')||q('.unit-navigation');
 const bar=document.createElement('header');bar.className='demo-bar';
 const name=document.createElement('div');name.className='demo-book-title';const level=document.createElement('small');level.textContent=eyebrow.replace(/Lise(?!-Yetişkin)/g,'Lise-Yetişkin');const heading=document.createElement('strong');heading.textContent=title;name.append(level,heading);bar.append(name);
 if(nav)nav.querySelectorAll('a.unit-nav-button').forEach(a=>{if(a.textContent.includes('→'))a.classList.add('unit-nav-next')});if(language)bar.append(language);if(nav){bar.append(nav);nav.querySelectorAll('.presentation-link').forEach(a=>a.hidden=true)}if(toolbar)bar.append(toolbar);
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
 function layout(){cancelAnimationFrame(frame);frame=requestAnimationFrame(()=>{if(img.naturalWidth){const ratio=img.naturalHeight/img.naturalWidth;const fitWidth=innerWidth<=800&&viewport.clientHeight<260?viewport.clientWidth-2:Math.min(viewport.clientWidth-2,(viewport.clientHeight-2)/ratio);const width=Math.max(50,mode==='fit'?fitWidth:(innerWidth<=800?fitWidth:680)*factor);const px=Math.round(width)+'px';if(stage.style.width!==px)stage.style.width=px;stage.style.maxWidth='none';stage.style.margin='0 auto';scale.textContent=Math.round(width/680*100)+'%'}for(const [b,id]of arrows)b.disabled=!!q('#'+id)?.disabled;align()})}
 if(q('#zoomIn'))q('#zoomIn').onclick=()=>{factor=Math.min(2.4,factor+.1);mode='large';layout()};if(q('#zoomOut'))q('#zoomOut').onclick=()=>{factor=Math.max(.5,factor-.1);mode='large';layout()};
 full.onclick=async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen()}catch{const toast=q('#toast');if(toast){toast.textContent='Tam ekran için F11 tuşunu kullanabilirsiniz.';toast.classList.add('show');setTimeout(()=>toast.classList.remove('show'),2600)}}};
 document.addEventListener('fullscreenchange',()=>{full.textContent=document.fullscreenElement?'⛶ Tam ekrandan çık':'⛶ Tam ekran';layout()});
 const rail=q('#thumbrail'),phone=()=>innerWidth<=800;
 const phoneNav=document.createElement('nav');phoneNav.className='ta-mobile-page-nav';phoneNav.setAttribute('aria-label','Kitap sayfası geçişleri');
 const phonePrev=document.createElement('button'),phoneNext=document.createElement('button'),phoneStatus=document.createElement('span');
 phonePrev.type=phoneNext.type='button';phonePrev.textContent='← Önceki';phoneNext.textContent='Sonraki →';phonePrev.setAttribute('aria-label','Önceki kitap sayfası');phoneNext.setAttribute('aria-label','Sonraki kitap sayfası');phoneStatus.className='ta-mobile-page-status';phoneStatus.setAttribute('aria-live','polite');phoneNav.append(phonePrev,phoneStatus,phoneNext);book.append(phoneNav);
 phonePrev.onclick=()=>q('#prev')?.click();phoneNext.onclick=()=>q('#next')?.click();
 function syncPhone(){phonePrev.disabled=!!q('#prev')?.disabled;phoneNext.disabled=!!q('#next')?.disabled;phoneStatus.textContent=(q('#count')?.textContent||'').trim();}
 function keepThumbVisible(){const active=rail?.querySelector('.thumb.active');if(!active||!rail)return;const r=rail.getBoundingClientRect(),a=active.getBoundingClientRect();if(phone()){if(a.left<r.left||a.right>r.right)rail.scrollTo({left:rail.scrollLeft+a.left-r.left-(rail.clientWidth-a.width)/2,behavior:'smooth'})}else{if(a.top<r.top||a.bottom>r.bottom)rail.scrollTo({top:rail.scrollTop+a.top-r.top-(rail.clientHeight-a.height)/2,behavior:'smooth'})}}
 function syncPage(){viewport.scrollTop=0;viewport.scrollLeft=0;window.scrollTo(0,0);layout();syncPhone();requestAnimationFrame(keepThumbVisible);if(phone())mobilePanel(false,false);}
 if(q('#count'))new MutationObserver(syncPage).observe(q('#count'),{subtree:true,childList:true,characterData:true});
 if(rail)new MutationObserver(()=>{layout();syncPhone();requestAnimationFrame(keepThumbVisible)}).observe(rail,{childList:true,subtree:true,attributes:true,attributeFilter:['class']});
 new ResizeObserver(layout).observe(viewport);new ResizeObserver(align).observe(stage);new ResizeObserver(layout).observe(reader);
 img.addEventListener('load',layout);window.addEventListener('resize',layout);viewport.addEventListener('scroll',align,{passive:true});css.addEventListener('load',layout);
 if(nav){const summary=nav.querySelector('summary.unit-mark');if(summary){const number=(summary.textContent.match(/\d+/)||[])[0];if(number)summary.textContent=number+'. ÜNİTE';}}
 const mobileButton=document.createElement('button');mobileButton.className='ta-mobile-tools';mobileButton.textContent='Çalışma';mobileButton.type='button';mobileButton.setAttribute('aria-expanded','false');controls.prepend(mobileButton);
 const mobileClose=document.createElement('button');mobileClose.className='ta-mobile-close';mobileClose.type='button';mobileClose.textContent='×';mobileClose.setAttribute('aria-label','Çalışma panelini kapat');sideHeading.append(mobileClose);
 const backdrop=document.createElement('button');backdrop.className='ta-mobile-backdrop';backdrop.type='button';backdrop.setAttribute('aria-label','Çalışma panelini kapat');backdrop.tabIndex=-1;document.body.append(backdrop);
 let panelOpener=null;
 function mobilePanel(open,restore=true){if(open&&!document.body.classList.contains('ta-mobile-panel-open'))panelOpener=document.activeElement;document.body.classList.toggle('ta-mobile-panel-open',open);mobileButton.setAttribute('aria-expanded',String(open));if(phone()){sidebar.setAttribute('role','dialog');sidebar.setAttribute('aria-modal',String(open));sidebar.setAttribute('aria-label','Sözlük ve ünite çalışmaları');if(open)mobileClose.focus({preventScroll:true});else if(restore&&panelOpener?.isConnected)panelOpener.focus({preventScroll:true});}}
 backdrop.onclick=()=>mobilePanel(false);
 document.addEventListener('keydown',e=>{if(!phone()||!document.body.classList.contains('ta-mobile-panel-open'))return;if(e.key==='Escape'){e.preventDefault();mobilePanel(false)}if(e.key==='Tab'){const els=[...sidebar.querySelectorAll('button:not(:disabled),a[href],input,select,summary,[tabindex="0"]')].filter(e=>e.getClientRects().length);const first=els[0],last=els[els.length-1];if(e.shiftKey&&document.activeElement===first){e.preventDefault();last?.focus()}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first?.focus()}}});
 const returnLink=q('.ta-pdf-return');const returnParent=returnLink?.parentElement;
 function mobileResize(){if(returnLink){if(phone())sidebar.append(returnLink);else if(returnParent&&returnLink.parentElement!==returnParent)returnParent.append(returnLink)}if(!phone()){document.body.classList.remove('ta-mobile-panel-open');sidebar.removeAttribute('role');sidebar.removeAttribute('aria-modal')}requestAnimationFrame(()=>{syncPhone();keepThumbVisible();layout()})}
 window.addEventListener('resize',mobileResize);window.visualViewport?.addEventListener('resize',layout);mobileResize();syncPhone();
 mobileButton.onclick=()=>mobilePanel(!document.body.classList.contains('ta-mobile-panel-open'));mobileClose.onclick=()=>mobilePanel(false);
 q('#hotspots')?.addEventListener('click',e=>{if(phone()&&e.target.closest('.word-hit')){sidebar.scrollTop=0;mobilePanel(true)}});
 layout();window.TAPdfWorkspace={version:2,layout,fit:()=>{mode='fit';layout()}};
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>setTimeout(install,0),{once:true});else setTimeout(install,0);
})();

