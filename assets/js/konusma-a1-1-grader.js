(()=>{'use strict';
const rules=[
 [['günaydın']],
 [['merhaba','selam','selamünaleyküm']],
 [['nasılsın']],
 [['rica ederim','bir şey değil']],
 [['hoşça kal','görüşürüz','güle güle']],
 [/(?:benim\s+)?adım\s+[a-zçğıöşü]{2,}/u],
 [/(?:[0-9]+|[a-zçğıöşü]+(?:\s+[a-zçğıöşü]+)?)\s+yaşındayım|yaşım\s+(?:[0-9]+|[a-zçğıöşü]+)/u],
 [/(?:kırgız|türki|türk|özbek|kazak|pakistan|japon|kanada|tunus|tanzan|bosna|suriye|afgan|iran|rus|ırak|almanya|fransa|ingiltere|kenya|kamerun|gürcistan|azerbaycan)/u],
 [['türkçe','kırgızca','ingilizce','rusça','özbekçe','kazakça','arapça','japonca','urduca','fransızca','konuşuyorum','biliyorum']],
 [['adım','ismim'],['yaşındayım','yaşım'],['kırgız','türk','özbek','kazak','pakistan','japon','tanzan','kanada','rus','bosna'],['konuşuyorum','dilim','biliyorum']],
 [/(?:benim\s+)?adım\s+[a-zçğıöşü]{2,}/u],
 [['iyiyim','çok iyiyim','fena değil','teşekkür ederim']],
 [/(?:kırgız|türki|türk|özbek|kazak|pakistan|japon|kanada|tunus|tanzan|bosna|suriye|afgan|iran|rus|ırak|almanya|fransa|ingiltere|kenya|kamerun|gürcistan|azerbaycan)/u],
 [/(?:[0-9]+|[a-zçğıöşü]+(?:\s+[a-zçğıöşü]+)?)\s+yaşındayım|yaşım\s+(?:[0-9]+|[a-zçğıöşü]+)/u],
 [['türkçe','kırgızca','ingilizce','rusça','özbekçe','kazakça','arapça','japonca','urduca','fransızca','konuşuyorum','biliyorum']],
 [['üzüm'],['elma']],
 [['çay'],['şeker'],['cam'],['saat']],
 [['merhaba'],['adım'],['ali']],
 [['ben'],['on beş','15'],['yaşındayım']],
 [['tanıştığımıza'],['memnun oldum']],
 [['günaydın','merhaba'],['nasılsın','nasılsınız','iyi']],
 [['günaydın','merhaba'],['öğretmenim','nasılsınız']],
 [['akira'],['japon']],
 [['murat'],['yaşında','15','on beş'],['istanbul']],
 [['zarina'],['özbek'],['osman'],['tanzan']],
 [['merhaba','selam'],[/\badım\s+[a-zçğıöşü]{2,}/u,'benim adım']],
 [['memnun'],['iyiyim','fena değil']],
 [/(?:kırgız|türki|türk|özbek|kazak|pakistan|japon|kanada|tunus|tanzan|bosna|suriye|afgan|iran|rus|ırak|almanya|fransa|ingiltere|kenya|kamerun|gürcistan|azerbaycan)/u],
 [['yaşındayım','yaşım'],['konuşuyorum','biliyorum','dilim']],
 [['rica ederim','bir şey değil'],['görüşürüz','hoşça kal','güle güle']]
];
function normalize(s){return String(s||'').toLocaleLowerCase('tr-TR').normalize('NFC').replace(/[.,!?;:()\-”“"']/g,' ').replace(/\s+/g,' ').trim()}
function hits(text,group){const items=Array.isArray(group)?group:[group];return items.some(x=>x instanceof RegExp?x.test(text):(' '+text+' ').includes(' '+normalize(x)+' '))}
function grade(i,text,hasRecording){const normalized=normalize(text),groups=rules[i];if(!groups)throw Error('Kural yok: '+i);const matched=normalized&&hasRecording?groups.map(g=>hits(normalized,g)):groups.map(()=>false);return {earned:matched.filter(Boolean).length/groups.length,possible:1,matched:matched.filter(Boolean).length,total:groups.length,untranscribed:hasRecording&&!normalized,recorded:!!hasRecording}}
window.TA_SPEAKING_GRADE={grade,normalize,ruleCount:rules.length}
})();