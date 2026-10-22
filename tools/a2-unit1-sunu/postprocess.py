from pathlib import Path
import os
import json
R=Path(os.environ.get("A2_SUNU_WORK",Path(__file__).resolve().parents[3]/"a2-source"));O=R.parent/'turkce-akademi/kitaplar/lise-a2/tatil-donusu/sunum/assets';p=O/'translations.json';d=json.loads(p.read_text());spots=json.loads((O/'word-spots.json').read_text())
fixes={"artvin'den":{1:'из Артвина'},"kenya'ya":{1:'в Кению',4:'au Kenya'},"kenya'da":{1:'в Кении',4:'au Kenya'},"trabzon'dan":{1:'из Трабзона',2:'Трабзондон'},"nevşehir'de":{1:'в Невшехире'},"özbekistan'dan":{1:'из Узбекистана',4:'d’Ouzbékistan'},"buhara'da":{1:'в Бухаре'},"buhara'dan":{1:'из Бухары'},"idris'i":{1:'Идриса',2:'Идристи'},"idris'in":{1:'Идриса',2:'Идристин',4:'d’İdris'},"deniz'den":{0:'from Deniz (person)',1:'от Дениза',4:'de Deniz'},"deniz'e":{0:'to Deniz (person)',1:'к Денизу',4:'à Deniz'},'öğretmenlerim':{3:'معلّميّ'}}
for k,changes in fixes.items():
 if k not in d['words']:continue
 for i,value in changes.items():d['words'][k][i]=value
 if k in d['forms']:d['forms'][k]['formTranslations']=d['words'][k]
# The common noun deniz is sea. Deniz in the assessment is a person's name.
d['words']['deniz']=['sea','море','деңиз','بحر','mer'];d['forms'].pop('deniz',None);d['words']['Deniz']=['Deniz (given name)','Дениз (имя)','Дениз (адамдын аты)','دنيز (اسم شخص)','Deniz (prénom)']
for hs in spots[98:]:
 for h in hs:
  if h['key']=='deniz':h['key']='Deniz'
for k in ["deniz'e","deniz'den","deniz'"]:
 if k in d['forms']:d['forms'][k]['lemma']='Deniz';d['forms'][k]['lemmaTranslations']=d['words']['Deniz']
# Refresh affected example grammar in the target languages.
for k in ["kenya'da","kenya'ya","nevşehir'de","muğla'daki","muğla'daydık"]:
 if k not in d['examples']:continue
 ex=d['examples'][k]
 if k.startswith('kenya'):
  ex[1][1]='Прошлым летом во время поездки в Кению я нашёл новых друзей.';ex[1][2]='Өткөн жайда Кенияга барганда жаңы досторду таптым.';ex[1][4]='Je me suis fait de nouveaux amis pendant mon voyage au Kenya l’été dernier.'
 elif k.startswith('muğla'):
  ex[1][1]='Прошлым летом во время поездки в Муглу я нашёл новых друзей.';ex[1][2]='Өткөн жайда Муглага барганда жаңы досторду таптым.'
 else:ex[1][2]='Өткөн жайда Невшехирге барганда жаңы досторду таптым.'
for k,e in d['examples'].items():
 if e[1][4]:e[1][4]=e[1][4][0].upper()+e[1][4][1:]
def ex(k,tr,*v):d['examples'][k]=[tr,list(v)]
ex('imamova','Öğretmenimin soyadı İmamova.','My teacher’s surname is İmamova.','Фамилия моей учительницы — Имамова.','Мугалимимдин фамилиясы Имамова.','اسم عائلة معلمتي إماموفا.','Le nom de famille de ma professeure est İmamova.')
ex('ertaylan','Arkadaşımın soyadı Ertaylan.','My friend’s surname is Ertaylan.','Фамилия моего друга — Эртайлан.','Досумдун фамилиясы Эртайлан.','اسم عائلة صديقي إرتايلان.','Le nom de famille de mon ami est Ertaylan.')
ex('onuncu','Bugün kursun onuncu günü.','Today is the tenth day of the course.','Сегодня десятый день курса.','Бүгүн курстун онунчу күнү.','اليوم هو اليوم العاشر من الدورة.','Aujourd’hui, c’est le dixième jour du cours.')
ex('yedinci','Asansör yedinci katta durdu.','The lift stopped on the seventh floor.','Лифт остановился на седьмом этаже.','Лифт жетинчи кабатта токтоду.','توقف المصعد في الطابق السابع.','L’ascenseur s’est arrêté au septième étage.')
ex('Deniz','Deniz bugün okula erken geldi.','Deniz came to school early today.','Дениз сегодня рано пришёл в школу.','Дениз бүгүн мектепке эрте келди.','جاء دنيز إلى المدرسة مبكراً اليوم.','Deniz est arrivé tôt à l’école aujourd’hui.')
# Cultural place names and lexical compounds are single selections.
rows=[('incik boncuk',['trinkets and beads','безделушки и бусины','майда жасалгалар жана шурулар','حلي وخرز','babioles et perles'],d['examples']['incik']),('koza han',['Koza Han (historic inn)','Коза-хан (исторический караван-сарай)','Коза Хан (тарыхый кербен сарай)','كوزا خان (خان تاريخي)','Koza Han (caravansérail historique)'],['Koza Han’da bir çay molası verdik.',['We took a tea break at Koza Han.','Мы сделали перерыв на чай в Коза-хане.','Коза Ханда чай ичип эс алдык.','توقفنا لشرب الشاي في كوزا خان.','Nous avons fait une pause thé à Koza Han.']]),('ulugbek medresesi',['Ulugh Beg Madrasa','медресе Улугбека','Улукбек медресеси','مدرسة أولوغ بيك','médersa d’Ouloug Beg'],d['examples']['ulugbek']),('kalon minaresi',['Kalon Minaret','минарет Калон','Калон мунарасы','مئذنة كاليان','minaret Kalon'],d['examples']['kalon']),('ark kalesi',['Ark Citadel','крепость Арк','Арк чеби','قلعة أرك','citadelle Ark'],d['examples']['ark']),('registon meydanı\'nı',['Registan Square (object)','площадь Регистан','Регистан аянтын','ساحة ريجستان','la place du Régistan'],d['examples']['registon'])]
for k,values,e in rows:d['phrases'][k]={'translations':values,'exampleTr':e[0],'examples':e[1]}
d['phrases']["koza han'da"]={'translations':['at Koza Han','в Коза-хане','Коза Ханда','في كوزا خان','à Koza Han'],'exampleTr':rows[1][2][0],'examples':rows[1][2][1]}
for k,f in d['forms'].items():
 if k in d['examples']:f.update(exampleTr=d['examples'][k][0],examples=d['examples'][k][1])
# Fill the five root records that were absent in older dictionary schemas.
root_records={'form':['form','бланк','бланк','استمارة','formulaire'],'tulum':['bag; overalls','мешок; комбинезон','кап; комбинезон','كيس؛ بدلة من قطعة واحدة','sac; combinaison'],'ilgili olmak':['to be related','быть связанным','байланыштуу болуу','تعلّق بـ','être lié à'],'çizelge':['chart; schedule','таблица; график','жадыбал','جدول','tableau; calendrier'],'Hüseyin':['Hüseyin (given name)','Хюсейн (имя)','Хүсейин (ысым)','حسين (اسم)','Hüseyin (prénom)']}
d['words'].update(root_records)
for f in d['forms'].values():
 if f['lemma'] in root_records:f['lemmaTranslations']=root_records[f['lemma']]
p.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')));(O/'word-spots.json').write_text(json.dumps(spots,ensure_ascii=False,separators=(',',':')))
