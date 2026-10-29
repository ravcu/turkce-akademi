/* Binary assets are served independently of the GitHub Pages HTML/data build. */
(()=>{'use strict';
  if(window.TurkceMedia)return;
  const script=document.currentScript;
  const scriptURL=new URL(script.src,document.baseURI);
  const siteRoot=scriptURL.pathname.slice(0,scriptURL.pathname.lastIndexOf('/assets/js/')+1);
  const base='https://raw.githubusercontent.com/ravcu/turkce-akademi/main/';
  const media=/\.(?:mp3|wav|opus|ogg|m4a|aac|flac|webp|png|jpe?g|gif|svg|ico|mp4|webm|woff2?|ttf|otf|pdf)$/i;
  function resolve(value){
    if(typeof value!=='string'||!value||value.startsWith('#'))return value;
    let url;try{url=new URL(value,document.baseURI)}catch{return value}
    if(url.origin!==scriptURL.origin||!url.pathname.startsWith(siteRoot)||!media.test(url.pathname))return value;
    // Keep URL path separators; encode spaces and Unicode consistently across browsers.
    const path=url.pathname.slice(siteRoot.length).split('/').map(part=>{try{return encodeURIComponent(decodeURIComponent(part))}catch{return part}}).join('/');
    return base+path+url.search+url.hash;
  }
  function srcset(value){
    if(typeof value!=='string'||value.includes('data:'))return value;
    return value.split(',').map(item=>{const match=item.trim().match(/^(\S+)(\s+.*)?$/);return match?resolve(match[1])+(match[2]||''):item}).join(', ');
  }
  const sourceTags=new Set(['IMG','AUDIO','VIDEO','SOURCE','TRACK','INPUT']);
  function mapped(element,name,value){
    name=String(name).toLowerCase();
    if(name==='src'&&sourceTags.has(element.tagName))return resolve(value);
    if(name==='poster'&&element.tagName==='VIDEO')return resolve(value);
    if(name==='href'&&['A','LINK'].includes(element.tagName))return resolve(value);
    if(name==='srcset'&&['IMG','SOURCE'].includes(element.tagName))return srcset(value);
    return value;
  }
  const nativeSet=Element.prototype.setAttribute;
  Element.prototype.setAttribute=function(name,value){return nativeSet.call(this,name,mapped(this,name,value))};
  function patch(ctor,name,convert=resolve){
    if(!ctor)return;const descriptor=Object.getOwnPropertyDescriptor(ctor.prototype,name);
    if(!descriptor?.set||!descriptor.configurable)return;
    Object.defineProperty(ctor.prototype,name,{...descriptor,set(value){descriptor.set.call(this,convert(value))}});
  }
  patch(window.HTMLImageElement,'src');patch(window.HTMLImageElement,'srcset',srcset);
  patch(window.HTMLMediaElement,'src');patch(window.HTMLSourceElement,'src');patch(window.HTMLSourceElement,'srcset',srcset);
  patch(window.HTMLVideoElement,'poster');patch(window.HTMLTrackElement,'src');patch(window.HTMLAnchorElement,'href');
  const NativeAudio=window.Audio;
  if(NativeAudio){const Audio=function(...args){if(args.length)args[0]=resolve(args[0]);return Reflect.construct(NativeAudio,args,new.target||NativeAudio)};Audio.prototype=NativeAudio.prototype;Object.setPrototypeOf(Audio,NativeAudio);window.Audio=Audio}
  const nativeFetch=window.fetch;
  if(nativeFetch)window.fetch=function(input,init){
    if(typeof input==='string')input=resolve(input);
    else if(input instanceof URL)input=new URL(resolve(input.href));
    else if(window.Request&&input instanceof Request){const url=resolve(input.url);if(url!==input.url)input=new Request(url,input)}
    return nativeFetch.call(this,input,init);
  };
  if(window.XMLHttpRequest){const open=XMLHttpRequest.prototype.open;XMLHttpRequest.prototype.open=function(method,url,...rest){return open.call(this,method,resolve(url),...rest)}}
  function refresh(element){
    if(element.nodeType!==1)return;
    for(const name of ['src','srcset','poster','href']){const old=element.getAttribute(name);if(old===null)continue;const next=mapped(element,name,old);if(next!==old)nativeSet.call(element,name,next)}
  }
  function scan(root){refresh(root);root.querySelectorAll?.('img,source,audio,video,track,input[type="image"],a[href],link[href]').forEach(refresh)}
  const observer=new MutationObserver(records=>{for(const record of records){if(record.type==='attributes')refresh(record.target);else record.addedNodes.forEach(scan)}});
  observer.observe(document.documentElement,{subtree:true,childList:true,attributes:true,attributeFilter:['src','srcset','poster','href']});
  scan(document.documentElement);
  window.TurkceMedia=Object.freeze({resolve,base,siteRoot});
})();
