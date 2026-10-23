from pathlib import Path
from PIL import Image
root=Path('repo/kitaplar/lise-a2/hafta-sonu-planin-ne/sunum');sprite=Image.new('RGB',(384*8,216*13),'white')
for i in range(104):
 im=Image.open(root/f'native-v2/slides/{i+1:03}.webp').resize((384,216),Image.Resampling.LANCZOS);sprite.paste(im,((i%8)*384,(i//8)*216))
sprite.save(root/'native-v2/thumbnails.webp','WEBP',quality=90,method=6)
p=root/'index.html';s=p.read_text()
if 'class="thumb-preview"' not in s:
 s=s.replace('<img loading="lazy" src="${s.image}" alt="">','<span class="thumb-preview" style="background-position:${(i%8)/7*100}% ${Math.floor(i/8)/12*100}%"></span>')
 s=s.replace('</head>','<style>.thumb-preview{display:block;width:100%;aspect-ratio:16/9;height:auto;background-image:url(native-v2/thumbnails.webp);background-size:800% 1300%;background-repeat:no-repeat;margin:0!important;line-height:0}.answer-toggle:disabled{cursor:default}</style></head>')
 s=s.replace('renderShell();renderSlide();',"renderShell();document.getElementById('slideImg').onload=()=>{[current-1,current+1].forEach(i=>{if(slides[i]){const preload=new Image();preload.decoding='async';preload.fetchPriority='low';preload.src=slides[i].image}})};renderSlide();")
 p.write_text(s)
