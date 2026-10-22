from pathlib import Path
import os
import json,re,shutil
R=Path(os.environ.get("A2_SUNU_WORK",Path(__file__).resolve().parents[3]/"a2-source"));repo=Path(os.environ.get("A2_SUNU_REPO",Path(__file__).resolve().parents[2]));O=repo/'kitaplar/lise-a2/tatil-donusu/sunum'
s=(repo/'kitaplar/tanisalim/sunum/index.html').read_text().replace('A1 · TANIŞALIM','A2 · TATİL DÖNÜŞÜ').replace('A1 Tanışalım','A2 Tatil Dönüşü').replace('A1 · Tanışalım','A2 · Tatil Dönüşü')
s=re.sub(r'  const speakerClean=.*?;\n','  const speakerClean={};\n',s)
s=s.replace('assets/slides-20261011b.json','assets/slides.json').replace('assets/word-spots-20261011c.json','assets/word-spots.json').replace('../translations-20261011b.json','assets/translations.json').replace('assets/answer-overlays-20261011i.json','assets/answer-overlays.json').replace('../../../assets/speech-20261013/player.js','speech/player.js').replace('sunum-current','a2-unit1-sunum-current')
s=s.replace('<a class="unit-nav-button" href="../../okuldayiz/sunum/">Bir Sonraki Ünite →</a>','<button class="unit-nav-button" disabled title="2. ünitenin sunu modu henüz hazırlanmadı.">Bir Sonraki Ünite →</button>')
a=s.index('  function renderAnswers()');b=s.index('\n',a)
s=s[:a]+'''  function renderAnswers(){
 const available=Boolean(slides[current]?.answerImage),panel=document.getElementById('answerPanel'),overlay=document.getElementById('answerOverlay'),toggle=document.getElementById('answerToggle');panel.hidden=!available;overlay.innerHTML=available?`<img src="${slides[current].answerImage}" style="width:100%;height:100%" alt="PowerPoint cevapları">`:'';
 const update=()=>{overlay.hidden=!available||!answersVisible;toggle.setAttribute('aria-pressed',String(answersVisible));toggle.textContent=answersVisible?'Cevapları gizle':'Cevapları göster';document.getElementById('answerStatus').textContent=answersVisible?'Cevaplar gösteriliyor':'Cevaplar gizli';document.querySelectorAll('.hotspot[data-answer="true"]').forEach(b=>b.style.display=answersVisible?'block':'none')};toggle.onclick=()=>{answersVisible=!answersVisible;update()};update();
  }'''+s[b:]
s=s.replace("new Audio('assets/audio/page-turn.mp3')","new Audio('../../../tanisalim/sunum/assets/audio/page-turn.mp3')")
s=s.replace("&&!x.h.answer","&&(answersVisible||!x.h.answer)&&Boolean(x.h.answer)===Boolean(hit.answer)")
s=s.replace('gap<=.14','gap<=.045').replace('b.x>=a.x-.025','b.x>=a.x-.005')
s=s.replace("return cleanText(text);","return cleanText(text);")
s=s.replace(".toLocaleLowerCase('tr-TR').replace(/^[", ".toLocaleLowerCase('tr-TR').replace(/[’‘]/g,\"'\").replace(/^[")
s=s.replace('Math.max(h.w*100,0.8)','Math.max(h.w*100,0.3)').replace('Math.max(h.h*100,2.2)','Math.max(h.h*100,0.8)')
s=s.replace('</head>','<style>.hotspot{min-width:0;min-height:0}</style></head>')
s=s.replace("const ending=String(last.text||'').match","best.indices.forEach((n,i)=>{if(/^[A-ZÇĞİÖŞÜ]/.test(list[n].text||''))display[i]=display[i].replace(/^./u,c=>c.toLocaleUpperCase('tr-TR'))});const ending=String(last.text||'').match");(O/'index.html').write_text(s);(O/'speech').mkdir(exist_ok=True);shutil.copyfile(repo/'kitaplar/lise-a2/geziyorum/speech/player.js',O/'speech/player.js')
rs=json.loads((R/'rendered.json').read_text());slides=[]
for r in rs:
 i=r['sequence'];p={'sequence':i,'sourcePart':r['part'],'sourceSlide':r['slide'],'image':f'assets/slides/{i:03}.webp'}
 if r['answers']:p['answerImage']=f'assets/answers/{i:03}.webp'
 if r['audio']:p['audio']=['assets/audio/'+a['output'] for a in r['audio']]
 slides.append(p)
(O/'assets/slides.json').write_text(json.dumps({'slides':slides},ensure_ascii=False,indent=2));(O/'assets/answer-overlays.json').write_text('{}')
p=repo/'kitaplar/lise-a2/tatil-donusu/index.html';s=p.read_text().replace('class="toplink presentation-link" href="#"','class="toplink presentation-link" href="sunum/"').replace('.mode-links a[href="#"]','.mode-links a.presentation-link');p.write_text(s)
d=json.loads((O/'assets/translations.json').read_text());d['phrases']['bu sebeple'].update(exampleTr='Yağmur başladı, bu sebeple eve döndük.',examples=['It started raining, so we went home.','Начался дождь, поэтому мы вернулись домой.','Жамгыр жаай баштады, ошондуктан үйгө кайттык.','بدأ المطر، ولهذا عدنا إلى البيت.','Il a commencé à pleuvoir, c’est pourquoi nous sommes rentrés.']);(O/'assets/translations.json').write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')))
print('slides',len(slides),'answers',sum(bool(r.get('answerImage')) for r in slides))
