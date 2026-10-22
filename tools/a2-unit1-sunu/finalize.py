from pathlib import Path
import os
import json,re
R=Path(os.environ.get("A2_SUNU_WORK",Path(__file__).resolve().parents[3]/"a2-source"));O=R.parent/'turkce-akademi/kitaplar/lise-a2/tatil-donusu/sunum/assets';d=json.loads((R/'curated.json').read_text());ss=json.loads((O/'word-spots.json').read_text())
d['words']["omar'ın"]=['Omar’s','Омара','Омардын','عمر','d’Omar'];d['forms'].pop('mıydın',None)
for hs in ss:hs[:]=[h for h in hs if h['key']!='u']
for line in (R/'examples.tsv').read_text().splitlines():
 ks,tr,*v=line.split('|');assert len(v)==5
 for k in ks.split(','):d['examples'][k]=[tr,v]
def put(k,tr,*v):assert len(v)==5;d['examples'][k]=[tr,list(v)]
# Person names identify the characters; examples describe fictional encounters.
people={'idris':('İdris','Идрис','Идрис','إدريس'),'kerem':('Kerem','Керем','Керем','كرم'),'furkan':('Furkan','Фуркан','Фуркан','فرقان'),'fatin':('Fatin','Фатин','Фатин','فاتن'),'imamova':('İmamova','Имамова','Имамова','إماموفا'),'ertaylan':('Ertaylan','Эртайлан','Эртайлан','إرتايلان'),'omar':('Omar','Омар','Омар','عمر'),'deniz':('Deniz','Дениз','Дениз','دنيز')}
keys={h['key'] for hs in ss for h in hs}
for k in keys:
 root=k.split("'")[0]
 if root in people and k not in d['examples']:
  n,ru,ky,ar=people[root];put(k,f'Arkadaşımın adı {n}.',f'My friend’s name is {n}.',f'Моего друга зовут {ru}.',f'Досумдун аты {ky}.',f'اسم صديقي {ar}.',f'Mon ami s’appelle {n}.')
put('aycan,elif','Aycan ve Elif aynı sınıfta.','Aycan and Elif are in the same class.','Айджан и Элиф учатся в одном классе.','Айжан менен Элиф бир класста окушат.','آيجان وإليف في الصف نفسه.','Aycan et Elif sont dans la même classe.')
places={'ark':('Ark Kalesi','Ark Citadel','крепость Арк','Арк чеби','قلعة أرك','la citadelle Ark'),'cumalıkızık':('Cumalıkızık','Cumalıkızık','Джумалыкызык','Жумалыкызык','جومالي كيزيك','Cumalıkızık'),'kalon':('Kalon Minaresi','Kalon Minaret','минарет Калон','Калон мунарасы','مئذنة كاليان','le minaret Kalon'),'ulugbek':('Uluğ Bey Medresesi','Ulugh Beg Madrasa','медресе Улугбека','Улукбек медресеси','مدرسة أولوغ بيك','la médersa d’Ouloug Beg'),'registon':('Registon Meydanı','Registan Square','площадь Регистан','Регистан аянты','ساحة ريجستان','la place du Régistan'),'ınkaya':('İnkaya','İnkaya','Инкая','Инкая','إنكايا','İnkaya'),'samsun':('Samsun','Samsun','Самсун','Самсун','سامسون','Samsun')}
for k,(tr,en,ru,ky,ar,fr) in places.items():put(k,f'Gezi programımızda {tr} de var.',f'{en} is also on our itinerary.',f'В программе нашей поездки есть и {ru}.',f'Саякатыбыздын программасында {ky} да бар.',f'يتضمن برنامج رحلتنا {ar} أيضاً.',f'{fr} figure aussi au programme de notre voyage.')
# Inflected place references use a simple travel memory; no current factual claims.
for k in ["kenya'da","kenya'ya","nevşehir'de","muğla'daki","muğla'daydık"]:
 root=k.split("'")[0];name={'kenya':('Kenya','Кения','Кения','كينيا'),'nevşehir':('Nevşehir','Невшехир','Невшехир','نوشهر'),'muğla':('Muğla','Мугла','Мугла','موغلا')}[root];tr,ru,ky,ar=name
 put(k,f'Geçen yaz {tr} gezisinde yeni arkadaşlar edindim.',f'I made new friends on my trip to {tr} last summer.',f'Прошлым летом во время поездки в {ru} я нашёл новых друзей.',f'Өткөн жайда {ky} саякатында жаңы досторду таптым.',f'تعرفت على أصدقاء جدد في رحلتي إلى {ar} الصيف الماضي.',f'Je me suis fait de nouveaux amis pendant mon voyage à {tr} l’été dernier.')
put("istanbul'dayım",'Bu hafta İstanbul’dayım.','I am in Istanbul this week.','На этой неделе я в Стамбуле.','Бул жумада Стамбулдамын.','أنا في إسطنبول هذا الأسبوع.','Je suis à Istanbul cette semaine.')
put("mardin'deydim",'Geçen hafta Mardin’deydim.','I was in Mardin last week.','На прошлой неделе я был в Мардине.','Өткөн жумада Мардинде болчумун.','كنت في ماردين الأسبوع الماضي.','J’étais à Mardin la semaine dernière.')
put("2021'de",'2021’de bu okulda okumaya başladım.','I started studying at this school in 2021.','Я начал учиться в этой школе в 2021 году.','2021-жылы бул мектепте окуй баштадым.','بدأت الدراسة في هذه المدرسة عام ٢٠٢١.','J’ai commencé à étudier dans cette école en 2021.')
put("bey'e",'Murat Bey’e bir e-posta gönderdim.','I sent Mr Murat an email.','Я отправил господину Мурату электронное письмо.','Мурат мырзага электрондук кат жөнөттүм.','أرسلت رسالة إلكترونية إلى السيد مراد.','J’ai envoyé un courriel à monsieur Murat.')
for k,tr,en,ru,ky,ar,fr in [
("sarayı'nı",'Topkapı Sarayı’nı gezdik.','We visited Topkapı Palace.','Мы посетили дворец Топкапы.','Топкапы сарайын кыдырдык.','زرنا قصر طوب قابي.','Nous avons visité le palais de Topkapi.'),
("meydanı'nı",'Şehrin merkezindeki meydanı gezdik.','We visited the square in the city centre.','Мы осмотрели площадь в центре города.','Шаардын борборундагы аянтты кыдырдык.','زرنا الساحة في مركز المدينة.','Nous avons visité la place du centre-ville.'),
("köyü'nü",'Dedemin köyünü ziyaret ettik.','We visited my grandfather’s village.','Мы посетили деревню моего дедушки.','Чоң атамдын айылына бардык.','زرنا قرية جدي.','Nous avons visité le village de mon grand-père.'),
("cami'nin",'Caminin kapısında arkadaşımı bekledim.','I waited for my friend at the mosque entrance.','Я ждал друга у входа в мечеть.','Мечиттин эшигинде досумду күттүм.','انتظرت صديقي عند باب المسجد.','J’ai attendu mon ami à l’entrée de la mosquée.'),
("çınar'ında",'Büyük çınarın altında biraz dinlendik.','We rested for a while under the large plane tree.','Мы немного отдохнули под большим платаном.','Чоң чынардын алдында бир аз эс алдык.','استرحنا قليلاً تحت شجرة الدلب الكبيرة.','Nous nous sommes reposés un moment sous le grand platane.')]:put(k,tr,en,ru,ky,ar,fr)
for k in ['-dan','-den']:d['examples'][k]=d['examples']['köyden']
for k in ['-madan','-meden']:d['examples'][k]=d['examples']['buluşmadan']
for k in ['-dıktan','-dikten','-tikten']:d['examples'][k]=d['examples']['yaptıktan']
for k in ['-dı','-(y)dı']:d['examples'][k]=d['examples']['evdeydim']
# Restrict to this unit and applicable compound expressions.
def token(t):return re.sub(r'^[^\wçğıöşü]+|[^\wçğıöşü]+$','',t.lower())
sets=[{token(h['key']) for h in hs} for hs in ss]
phr={k:v for k,v in d['phrases'].items() if k in keys or len(k.split())>1 and any(set(map(token,k.split()))<=s for s in sets)}
for k,ex in {'-dan önce':'buluşmadan','-dan sonra':'yaptıktan','-madan önce':'buluşmadan','-dıktan sonra':'yaptıktan','dan önce':'buluşmadan','dan sonra':'yaptıktan','spor yap':'yap-'}.items():
 if k in phr and ex in d['examples']:phr[k].update(exampleTr=d['examples'][ex][0],examples=d['examples'][ex][1])
for k,tr,ts,ex in [
('senin adın ne','Senin adın ne? Benim adım Elif.',['what is your name?','как тебя зовут?','атың ким?','ما اسمك؟','comment t’appelles-tu ?'],['What is your name? My name is Elif.','Как тебя зовут? Меня зовут Элиф.','Сенин атың ким? Менин атым Элиф.','ما اسمك؟ اسمي إليف.','Comment t’appelles-tu ? Je m’appelle Elif.']),
('burada ne var','Burada ne var? Burada bir kütüphane var.',['what is here?','что здесь?','бул жерде эмне бар?','ماذا يوجد هنا؟','qu’y a-t-il ici ?'],['What is here? There is a library here.','Что здесь? Здесь библиотека.','Бул жерде эмне бар? Бул жерде китепкана бар.','ماذا يوجد هنا؟ توجد هنا مكتبة.','Qu’y a-t-il ici ? Il y a une bibliothèque ici.']),
("allah'a ısmarladık",'Allah’a ısmarladık, yarın görüşürüz.',['goodbye (said by the person leaving)','до свидания (говорит уходящий)','аман болуңуз (кетип жаткан адам айтат)','في أمان الله (يقولها المغادر)','au revoir (dit par celui qui part)'],['Goodbye, see you tomorrow.','До свидания, до завтра.','Аман болуңуз, эртең көрүшөбүз.','في أمان الله، نلتقي غداً.','Au revoir, à demain.']),
('gün batımını','Sahilde gün batımını izledik.',['the sunset (object)','закат','күндүн батышын','غروب الشمس','le coucher du soleil'],['We watched the sunset on the beach.','Мы наблюдали закат на пляже.','Жээкте күндүн батышын көрдүк.','شاهدنا غروب الشمس على الشاطئ.','Nous avons regardé le coucher du soleil sur la plage.']),
('allah allah','Allah Allah! Anahtarımı nereye koydum?',['oh, really?; surprise','вот это да!','тобо!','يا للعجب!','tiens donc !'],['Oh dear! Where did I put my key?','Вот так! Куда я положил ключ?','Тобо! Ачкычымды кайда койдум?','يا للعجب! أين وضعت مفتاحي؟','Tiens donc ! Où ai-je mis ma clé ?'])]:phr[k]={'translations':ts,'exampleTr':tr,'examples':ex}
roots={d['forms'][k]['lemma'] for k in keys if k in d['forms']};keep=keys|roots
small={'words':{k:v for k,v in d['words'].items() if k in keep},'forms':{k:v for k,v in d['forms'].items() if k in keys},'examples':{k:v for k,v in d['examples'].items() if k in keep},'phrases':phr}
for k,f in small['forms'].items():
 if k in small['words']:f['formTranslations']=small['words'][k]
 if f['lemma'] in small['words']:f['lemmaTranslations']=small['words'][f['lemma']]
 if k in small['examples']:f.update(exampleTr=small['examples'][k][0],examples=small['examples'][k][1])
(O/'word-spots.json').write_text(json.dumps(ss,ensure_ascii=False,separators=(',',':')));(O/'translations.json').write_text(json.dumps(small,ensure_ascii=False,separators=(',',':')))
errors=[]
for k in keys:
 f=small['phrases'].get(k) or small['forms'].get(k);a=f.get('translations',f.get('formTranslations')) if f else small['words'].get(k);ex=[f.get('exampleTr'),f.get('examples')] if f and f.get('exampleTr') else small['examples'].get(k)
 if not isinstance(a,list) or len(a)!=5 or not all(a):errors.append([k,'meaning'])
 if not ex or not ex[0] or not isinstance(ex[1],list) or len(ex[1])!=5 or not all(ex[1]):errors.append([k,'example'])
for k,f in phr.items():
 if not f.get('exampleTr') or len(f.get('examples',[]))!=5:errors.append([k,'phrase example'])
print('keys',len(keys),'hits',sum(map(len,ss)),'phrases',len(phr),'errors',errors)
