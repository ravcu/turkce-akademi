const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
class Element{constructor(tag='IMG'){this.tagName=tag;this.nodeType=1;this.attrs={}}setAttribute(k,v){this.attrs[k]=String(v)}getAttribute(k){return this.attrs[k]??null}querySelectorAll(){return []}}
function type(tag,attrs){class Type extends Element{constructor(){super(tag)}}for(const a of attrs)Object.defineProperty(Type.prototype,a,{configurable:true,get(){return this.getAttribute(a)||''},set(v){this.attrs[a]=String(v)}});return Type}
const Img=type('IMG',['src','srcset']),Media=type('AUDIO',['src']),Source=type('SOURCE',['src','srcset']),Video=type('VIDEO',['poster']),Anchor=type('A',['href']),Track=type('TRACK',['src']);
class Audio extends Media{constructor(src){super();if(src!==undefined)this.src=src}}
class XHR{open(...args){this.args=args}}
let observer,fetchInput;
const context={URL,Request,Reflect,Set,Object,Element,HTMLImageElement:Img,HTMLMediaElement:Media,HTMLSourceElement:Source,HTMLVideoElement:Video,HTMLAnchorElement:Anchor,HTMLTrackElement:Track,Audio,XMLHttpRequest:XHR,
 document:{currentScript:{src:'https://ravcu.github.io/turkce-akademi/assets/js/media-loader.js'},baseURI:'https://ravcu.github.io/turkce-akademi/kitaplar/lise-a2/tatil-donusu/',documentElement:new Element('HTML')},
 MutationObserver:class{constructor(fn){observer=fn}observe(){}},fetch(input){fetchInput=input;return Promise.resolve(input)}};
context.window=context;vm.createContext(context);
vm.runInContext(fs.readFileSync(require('path').join(__dirname,'../assets/js/media-loader.js'),'utf8'),context);
const base='https://raw.githubusercontent.com/ravcu/turkce-akademi/main/';
const local='/turkce-akademi/kitaplar/lise-a2/audio/Lise - A2 - Ders Kitabı - 1.mp3';
assert.equal(context.TurkceMedia.resolve(local),base+'kitaplar/lise-a2/audio/Lise%20-%20A2%20-%20Ders%20Kitab%C4%B1%20-%201.mp3');
assert.equal(context.TurkceMedia.resolve('pages/sayfa_01.webp?v=1'),base+'kitaplar/lise-a2/tatil-donusu/pages/sayfa_01.webp?v=1');
for(const v of ['pages.json','../index.html','#answerArrow','data:image/png;base64,AA','https://example.com/picture.png','/other-site/image.png'])assert.equal(context.TurkceMedia.resolve(v),v);
assert.equal(context.TurkceMedia.resolve(base+'already.mp3'),base+'already.mp3');
const image=new Img();image.src='pages/sayfa_01.webp';assert(image.src.startsWith(base));image.setAttribute('src',local);assert(image.src.endsWith('1.mp3'));
const audio=new context.Audio(local);assert(audio instanceof Audio);assert(audio.src.startsWith(base));
context.fetch('pages.json');assert.equal(fetchInput,'pages.json');context.fetch(local);assert(fetchInput.startsWith(base));
context.fetch(new Request('https://ravcu.github.io'+local,{headers:{Range:'bytes=0-10'}}));assert(fetchInput.url.startsWith(base));assert.equal(fetchInput.headers.get('Range'),'bytes=0-10');
const xhr=new XHR();xhr.open('GET',local);assert(xhr.args[1].startsWith(base));
const parsed=new Img();parsed.attrs.src='pages/sayfa_01.webp';observer([{type:'childList',addedNodes:[parsed]}]);assert(parsed.src.startsWith(base));
const anchor=new Anchor();anchor.href='../index.html';assert.equal(anchor.href,'../index.html');
const source=new Source();source.srcset='pages/a.webp 1x, pages/b.webp 2x';assert(source.srcset.includes(base));assert(source.srcset.includes('2x'));
console.log('Media URL resolution, native setters, Audio, fetch, Range, XHR, parsed DOM and navigation passed');
