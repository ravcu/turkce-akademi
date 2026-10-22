from pathlib import Path
import os
import json,re,collections
R=Path(os.environ.get("A2_SUNU_WORK",Path(__file__).resolve().parents[3]/"a2-source"));O=R.parent/'turkce-akademi/kitaplar/lise-a2/tatil-donusu/sunum/assets';d=json.loads((R/'dictionary.json').read_text());ss=json.loads((O/'word-spots.json').read_text());roots={}
for file in ['editorial.tsv','answer-editorial.tsv']:
 for line in (R/file).read_text().splitlines():
  k,root,*v=line.split('|');assert len(v)==5;d['words'][k]=v;roots[k]=root
names={'artvin':['Artvin','Артвин','Артвин','أرتفين','Artvin'],'kenya':['Kenya','Кения','Кения','كينيا','Kenya'],'istanbul':['Istanbul','Стамбул','Стамбул','إسطنبول','Istanbul'],'mardin':['Mardin','Мардин','Мардин','ماردين','Mardin'],'bolu':['Bolu','Болу','Болу','بولو','Bolu'],'trabzon':['Trabzon','Трабзон','Трабзон','طرابزون','Trabzon'],'muğla':['Muğla','Мугла','Мугла','موغلا','Muğla'],'nevşehir':['Nevşehir','Невшехир','Невшехир','نوشهر','Nevşehir'],'özbekistan':['Uzbekistan','Узбекистан','Өзбекстан','أوزبكستان','Ouzbékistan'],'buhara':['Bukhara','Бухара','Бухара','بخارى','Boukhara'],'idris':['İdris','Идрис','Идрис','إدريس','İdris'],'omar':['Omar','Омар','Омар','عمر','Omar'],'ali':['Ali','Али','Али','علي','Ali'],'deniz':['Deniz','Дениз','Дениз','دنيز','Deniz'],'samsun':['Samsun','Самсун','Самсун','سامسون','Samsun'],'kalon':['Kalon','Калон','Калон','كاليان','Kalon'],'ark':['Ark Citadel','крепость Арк','Арк чеби','قلعة أرك','citadelle Ark'],'ulugbek':['Ulugh Beg','Улугбек','Улукбек','أولوغ بيك','Ouloug Beg'],'registon':['Registan','Регистан','Регистан','ريجستان','Régistan'],'ınkaya':['İnkaya','Инкая','Инкая','إنكايا','İnkaya'],'cumalıkızık':['Cumalıkızık','Джумалыкызык','Жумалыкызык','جومالي كيزيك','Cumalıkızık'],'ertaylan':['Ertaylan','Эртайлан','Эртайлан','إرتايلان','Ertaylan'],'fatin':['Fatin','Фатин','Фатин','فاتن','Fatin'],'furkan':['Furkan','Фуркан','Фуркан','فرقان','Furkan'],'kerem':['Kerem','Керем','Керем','كرم','Kerem'],'aycan,elif':['Aycan and Elif','Айджан и Элиф','Айжан жана Элиф','آيجان وإليف','Aycan et Elif']}
d['words'].update(names)
extras={"istanbul'dayım":['I am in Istanbul','я в Стамбуле','мен Стамбулдамын','أنا في إسطنبول','je suis à Istanbul'],"mardin'deydim":['I was in Mardin','я был(а) в Мардине','мен Мардинде болчумун','كنت في ماردين','j’étais à Mardin'],"muğla'daydık":['we were in Muğla','мы были в Мугле','биз Муглада болгонбуз','كنا في موغلا','nous étions à Muğla'],"muğla'daki":['in Muğla','находящийся в Мугле','Мугладагы','الموجود في موغلا','situé à Muğla'],"limanı'ndan":['from the harbour','из порта','портунан','من الميناء','du port'],"2021'de":['in 2021','в 2021 году','2021-жылы','في عام ٢٠٢١','en 2021'],"sarayı'nı":['the palace (object)','дворец','сарайын','القصر','le palais'],"meydanı'nı":['the square (object)','площадь','аянтын','الساحة','la place'],"çınar'ında":['at the plane tree','у платана','чынарынын жанында','عند شجرة الدلب','au pied du platane'],"cami'nin":['of the mosque','мечети','мечиттин','المسجد','de la mosquée'],"han'da":['at the historic inn','в караван-сарае','кербен сарайда','في الخان','au caravansérail'],"köyü'nü":['the village (object)','деревню','айылын','القرية','le village'],"deniz'":names['deniz'],'taşındık':['we moved house','мы переехали','биз көчтүк','انتقلنا إلى بيت جديد','nous avons déménagé'],'komşuyuz':['we are neighbours','мы соседи','биз кошунабыз','نحن جيران','nous sommes voisins'],'trabzonluyum':['I am from Trabzon','я из Трабзона','мен Трабзондонмун','أنا من طرابزون','je suis de Trabzon'],'akşehirliyim':['I am from Akşehir','я из Акшехира','мен Акшехирденмин','أنا من آق شهير','je suis d’Akşehir'],'tanıştığıma':['to have met (in a greeting)','что познакомился(-ась)','таанышканыма','لتعارفي','d’avoir fait connaissance']}
d['words'].update(extras)
for hs in ss:
 for h in hs:
  k=h['key'];k='tarih' if k=='k.tarih' else k;h['key']=k
  if "'" in k and k not in d['words']:
   root,suf=k.split("'",1);v=names.get(root) or d['words'].get(root)
   if not v:continue
   pre={'a':['to ','в ','','إلى ','à '],'e':['to ','в ','','إلى ','à '],'ya':['to ','в ','','إلى ','à '],'ye':['to ','в ','','إلى ','à '],'da':['in ','в ','','في ','à '],'de':['in ','в ','','في ','à '],'dan':['from ','из ','','من ','de '],'den':['from ','из ','','من ','de '],'in':['of ','','', 'لـ','de '],'nin':['of ','','', 'لـ','de '],'ı':['','','','',''],'i':['','','','',''],'yi':['','','','','']}.get(suf)
   if pre:
    a=[pre[i]+v[i] for i in range(5)];a[2]=v[2]+{'a':'га','e':'ге','ya':'га','ye':'ге','da':'да','de':'де','dan':'дан','den':'ден','in':'дин','nin':'нин','ı':'ды','i':'ди','yi':'ди'}.get(suf,'');d['words'][k]=a;roots[k]=root
for k,root in {'yap-':'yapmak','et-':'etmek','yüz-':'yüzmek','tanış-':'tanışmak','güneş-':'güneşlenmek','ye-':'yemek','dön-':'dönmek','kal-':'kalmak','çık-':'çıkmak'}.items():
 if root in d['words']:d['words'][k]=d['words'][root];roots[k]=root
for k in ['-dan','-den','-dı','-(y)dı','-madan','-meden','-dıktan','-dikten','-tikten']:
 d['words'][k]=(['from; ablative suffix','из; исходный падеж','-дан/-ден; чыгыш жөндөмө','من؛ لاحقة الابتعاد','de; suffixe de provenance'] if k in ['-dan','-den'] else ['before doing; without doing','до действия; не делая','кылганга чейин; кылбастан','قبل الفعل؛ دون فعله','avant de faire; sans faire'] if k in ['-madan','-meden'] else ['after doing (with sonra)','после действия (с sonra)','кылгандан кийин (sonra менен)','بعد الفعل (مع sonra)','après avoir fait (avec sonra)'] if 'ktan' in k or 'kten' in k else ['past tense suffix','суффикс прошедшего времени','өткөн чак мүчөсү','لاحقة الماضي','suffixe du passé'])
for k,f in d['forms'].items():roots.setdefault(k,f['lemma'])
for k,root in roots.items():
 if k not in d['examples'] and root in d['examples']:d['examples'][k]=d['examples'][root]
 if k!=root and k in d['words'] and root in d['words']:d['forms'][k]={'lemma':root,'lemmaTranslations':d['words'][root],'formTranslations':d['words'][k]}
ks={h['key'] for hs in ss for h in hs}
for k,f in d['forms'].items():
 if k in d['words']:f['formTranslations']=d['words'][k]
 if f['lemma'] in d['words']:f['lemmaTranslations']=d['words'][f['lemma']]
 if k in d['examples']:f.update(exampleTr=d['examples'][k][0],examples=d['examples'][k][1])
missing=sorted(k for k in ks if k not in d['words'] and k not in d['forms'] and k not in d['phrases']);ex=sorted(k for k in ks if k not in d['examples'] and not d['forms'].get(k,{}).get('exampleTr') and not d['phrases'].get(k,{}).get('exampleTr'));print('missing',missing);print('examples',len(ex),ex)
(R/'curated.json').write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')));(O/'word-spots.json').write_text(json.dumps(ss,ensure_ascii=False,separators=(',',':')));(R/'missing-examples.json').write_text(json.dumps(ex,ensure_ascii=False))
