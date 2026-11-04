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
 const c=350,R=322,r=142;const angles=[-90,-18,54,126,198].map(x=>x*Math.PI/180);
 const polar=(rad,a)=>[c+rad*Math.cos(a),c+rad*Math.sin(a)];
 const pstr=pts=>pts.map(p=>p.map(x=>x.toFixed(2)).join(',')).join(' ');
 const starPoints=(x,y,R=27,r=12)=>{let pts=[];for(let i=0;i<10;i++){const a=-Math.PI/2+i*Math.PI/5;pts.push([x+(i%2?r:R)*Math.cos(a),y+(i%2?r:R)*Math.sin(a)])}return pstr(pts)};
 let def='<defs><filter id="softshadow" x="-15%" y="-15%" width="130%" height="130%"><feDropShadow dx="1" dy="6" stdDeviation="6" flood-color="#a16616" flood-opacity=".35"/></filter>';
 let parts='';
 angles.forEach((angle,i)=>{
  const pts=[[c,c],polar(r,angle-Math.PI/5),polar(R,angle),polar(r,angle+Math.PI/5)],poly=pstr(pts),color=colors[tier(scores[i])];
  def+='<linearGradient id="tone'+i+'" x1="0" y1="0" x2=".3" y2="1"><stop offset="0" stop-color="'+color[0]+'"/><stop offset=".48" stop-color="'+color[1]+'"/><stop offset="1" stop-color="'+color[2]+'"/></linearGradient><clipPath id="segment'+i+'"><polygon points="'+poly+'"/></clipPath>';
  const deg=angle*180/Math.PI,fillDistance=(R* scores[i]/100).toFixed(2);
  parts+='<polygon points="'+poly+'" fill="#f7f5ef" stroke="#b37620" stroke-width="11" filter="url(#softshadow)"/>';
  parts+='<g clip-path="url(#segment'+i+')"><rect x="0" y="-145" width="'+fillDistance+'" height="290" fill="url(#tone'+i+')" transform="translate(350 350) rotate('+deg+')"/></g>';
  parts+='<polygon points="'+poly+'" fill="none" stroke="#ffec95" stroke-width="6"/><polygon points="'+poly+'" fill="none" stroke="#ce8b22" stroke-width="2.5"/>';
  const tip=polar(R,angle);
  parts+='<polygon points="'+starPoints(tip[0],tip[1],29,12)+'" fill="#ffcb34" stroke="#be7811" stroke-width="3"/><polygon points="'+starPoints(tip[0]-2,tip[1]-3,19,7)+'" fill="#ffed94" stroke="#e5a923" stroke-width="1"/>';
 });
 def+='</defs>';
 svg.innerHTML=def+parts;
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