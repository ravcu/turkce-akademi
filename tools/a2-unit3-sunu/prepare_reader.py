from pathlib import Path
import re
R=Path(__file__).resolve().parents[2];O=R/'kitaplar/lise-a2/bir-gunum/sunum'
h=(R/'kitaplar/lise-a2/tatil-donusu/sunum/index.html').read_text()
h=h.replace('<title>Tanışalım · Sunum Modu</title>','<title>Bir Günüm · A2 3. Ünite · Sunum Modu</title>')
h=h.replace('TATİL DÖNÜŞÜ','BİR GÜNÜM').replace('Tatil Dönüşü','Bir Günüm').replace('a2-unit1-sunum-current','a2-unit3-sunum-current')
h=re.sub(r'<nav class="unit-navigation".*?</nav>','<nav class="unit-navigation" aria-label="Üniteler arasında geçiş"><a class="unit-nav-button" href="../../hafta-sonu-planin-ne/sunum/">← Bir Önceki Ünite</a><span class="unit-current" aria-current="step">3. ÜNİTE</span><a class="unit-nav-button" href="../../simdi-haberler/">Bir Sonraki Ünite →</a></nav>',h,flags=re.S)
h=h.replace('<script src="speech/player.js"></script>','<script src="../../tatil-donusu/sunum/speech/player.js"></script><script src="speech.js"></script>')
h=h.replace('text=canonical;','text=raw||canonical;')
h=h.replace("img.src=s.image+'?v='+Date.now()","img.src=s.image")
h=h.replace('</head>','<style>.toolbar{flex-wrap:wrap;min-height:40px}.viewer{grid-template-rows:auto minmax(0,1fr) 61px}@media(max-width:860px){.viewer{grid-template-rows:auto auto 65px}}@media(max-width:520px){.brand{flex:1;min-width:0}.brand>span:last-child{min-width:0}.brand small{white-space:normal;letter-spacing:.025em;line-height:1.2}.header-right{flex-shrink:0}.header-right .back{max-width:96px}}</style></head>')
(O/'index.html').write_text(h)
print('Reader ready')
