(()=>{'use strict';
const $=id=>document.getElementById(id),params=new URLSearchParams(location.search),level=params.get('level')==='A2'?'A2':'A1',unit=Math.max(1,Math.min(10,parseInt(params.get('unit'),10)||1));
const titles={A1:['Tanışalım','Okuldayız','Ailem ve Evim','Bir Günüm','Şehir Gezisi','Çarşı Pazar','Bugün Hava Nasıl?','Geçmiş Olsun','Davetlisiniz','Tatil Planım'],A2:['Tatil Dönüşü','Hafta Sonu Planın Ne?','Bir Günüm','Şimdi Haberler','Dedemin Mesleği Bana Göre mi?','Hayat Birlikte Güzel','Akıllı Teknoloji','Spor-Sağlık','Bir Hikâyem Var','Geziyorum']};
const names=['reading','listening','speaking','writing','vocabulary'],scoreKey='ta-activities-'+level+'-'+unit,certKey='ta-certificate-'+level+'-'+unit;
const back='etkinlik.html?level='+level+'&unit='+unit;$('back').href=back;
function read(k){try{return JSON.parse(localStorage.getItem(k))}catch(e){return null}}
function dataScore(result){return result&&result.completed===true&&Number.isFinite(result.earned)&&Number.isFinite(result.possible)&&result.possible>0&&result.earned>=0&&result.earned<=result.possible?100*result.earned/result.possible:null}
const preview=params.get('preview')==='1',result=read(scoreKey)||{},values=preview?[90,85,78,88,80]:names.map(x=>dataScore(result[x]));
function tier(score){return score>=85?'gold':score>=70?'silver':'bronze'}
const colors={gold:['#fffbd6','#ffd542','#f4aa08'],silver:['#f8fdff','#cfe3f5','#8cadca'],bronze:['#ffe6d2','#ffbd84','#e67a37']};
const ns='http://www.w3.org/2000/svg',svg=$('achievementStar');
function makeSvg(scores){
 const c=340,R=285,r=146,angles=[-90,-18,54,126,198].map(a=>a*Math.PI/180);
 const polar=(radius,angle)=>[c+radius*Math.cos(angle),c+radius*Math.sin(angle)];
 const point=p=>p.map(v=>v.toFixed(2)).join(',');
 const poly=pts=>pts.map(point).join(' ');
 function smallStar(x,y){const pts=[];for(let i=0;i<10;i++){const a=-Math.PI/2+i*Math.PI/5;const radius=i%2===0?26:11;pts.push([x+radius*Math.cos(a),y+radius*Math.sin(a)])}return poly(pts)}
 let defs='<defs><filter id="wingShadow" x="-10%" y="-15%" width="125%" height="135%"><feDropShadow dx="0" dy="5" stdDeviation="5" flood-color="#82551d" flood-opacity=".24"/></filter>';
 let wings='',tips='';
 angles.forEach((a,i)=>{
  const pts=[[c,c],polar(r,a-Math.PI/5),polar(R,a),polar(r,a+Math.PI/5)];
  const colorset=colors[tier(scores[i])];
  defs+='<linearGradient id="wing'+i+'" x1="0" y1="0" x2=".65" y2="1"><stop offset="0" stop-color="'+colorset[0]+'"/><stop offset=".52" stop-color="'+colorset[1]+'"/><stop offset="1" stop-color="'+colorset[2]+'"/></linearGradient>';
  const shape=poly(pts);
  wings+='<polygon points="'+shape+'" fill="url(#wing'+i+')" stroke="#b7781d" stroke-width="10" stroke-linejoin="round" filter="url(#wingShadow)"/>';
  wings+='<polygon points="'+shape+'" fill="none" stroke="#ffe795" stroke-width="5" stroke-linejoin="round"/>';
  wings+='<polygon points="'+shape+'" fill="none" stroke="#d59425" stroke-width="2.2" stroke-linejoin="round"/>';
  const tip=polar(R,a);
  tips+='<polygon points="'+smallStar(tip[0],tip[1])+'" fill="#ffc23a" stroke="#b66b16" stroke-width="3"/>';
 });
 defs+='</defs>';svg.innerHTML=defs+wings+tips;
}
function resize(){const w=Math.max(260,Math.min(1500,document.documentElement.clientWidth-20)),ratio=w/1500;$('viewport').style.width=w+'px';$('viewport').style.height=(1000*ratio)+'px';$('certificate').style.transform='scale('+ratio+')'}
window.addEventListener('resize',resize);resize();
const name=preview?'Ahmet Yılmaz':(localStorage.getItem('ta-student-name')||'').trim(),validName=name.length>=3&&name.includes(' '),allScores=values.every(x=>x!==null);
$('levelBadge').textContent=level;$('unitTitle').textContent='Lise '+level+' – '+unit+'. Ünite: '+titles[level][unit-1];$('unitInText').textContent=unit+'. Ünite';$('studentName').textContent=validName?name:'Öğrenci Adı';
if(name.length>25)$('studentName').style.fontSize='63px';
let cert=read(certKey);if(!cert||typeof cert!=='object')cert={};
if(!preview&&!cert.date&&validName&&allScores){cert.date=new Date().toISOString();cert.name=name;try{localStorage.setItem(certKey,JSON.stringify(cert))}catch(e){}}
const when=cert.date?new Date(cert.date):new Date();$('dateText').textContent='Tarih: '+new Intl.DateTimeFormat('tr-TR',{day:'2-digit',month:'2-digit',year:'numeric'}).format(when);
if(!allScores||!validName){
 $('print').disabled=true;
 $('notice').textContent=!validName?'Sertifika için önce Etkinlik Modu üzerinden adınızı ve soyadınızı girin.':'Beş etkinliğin tamamında değerlendirilmiş puan bulunmadığından sertifika henüz oluşturulamaz. Eksik başarılar sıfır kabul edilmez.';
 ['readingScore','listeningScore','speakingScore','writingScore','vocabularyScore','overallScore'].forEach(id=>$(id).textContent='—');
 makeSvg([0,0,0,0,0]);
 return;
}
const ids=['readingScore','listeningScore','speakingScore','writingScore','vocabularyScore'];values.forEach((v,i)=>$(ids[i]).textContent='%'+Math.round(v));
const average=values.reduce((a,b)=>a+b,0)/5;$('overallScore').textContent='%'+(Math.round(average*10)/10).toLocaleString('tr-TR',{maximumFractionDigits:1});
makeSvg(values);
if(preview){$('print').disabled=true;$('notice').textContent='TASARIM ÖNİZLEMESİ · Ahmet Yılmaz ve örnek puanlar kullanılıyor. Gerçek başarı belgesi değildir.'}else{$('print').addEventListener('click',()=>window.print())}
})();