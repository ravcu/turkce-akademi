# A2 10. Ünite · Gezi-yorum · Sunu Modu

Üç özgün PowerPoint parçası kaynak sırasıyla 34 + 36 + 33 olmak üzere 103 slayttır. Kitap resimlerinin kaynak baytları değiştirilmez; clean/full türevlerinde 240 SHA-256 resim kontrolü yapılır. Kapaktaki ayrı metin nesnesinde kalan 6. ünite etiketi 10 olarak düzeltilir. Kaynakta boş açılış sayfası yoktur: 2. slayt ünite kapağı, 3. slayt hazırlık sorularıdır ve korunur.

41 slayttaki 223 ayrı cevap nesnesi (184 kırmızı metin/şekil ve 39 ayrı kırmızı onay resmi) açılıp kapanır. Görsellerin içindeki özgün kırmızı başlıklar, şekiller ve basılı örnekler korunur. Kayıpsız, saydam WebP cevap katmanlarının temiz sayfayla birleşimi, cevaplı kaynak dönüşümüyle piksel düzeyinde aynıdır.

Ayrı resim olarak eklenen 39 kırmızı onay işareti de cevap katmanındadır. Doğrulanmış simge SHA-256 değeriyle belirlenir; kitap görsellerinin içindeki kırmızı renkler maskeleme yoluyla silinmez. Etkilenen 7/10/12/28/32/61/83. sayfaların görsel adresleri `answers-v2` sürümüyle yenilenir. Cevabı bulunmayan sayfalarda düğme devre dışıdır ve “Bu Sayfada Cevap Yok” yazar.

Kaynakta ayrı İngilizce çeviri tablosu veya “Türkçe–İngilizce Kelime Listesi” slaytı yoktur. Bu tür öğeler için çıkarma kuralları mevcuttur.

16 özgün ses dosyasında 26 kullanım vardır; 25 ayrı MP3 kesiti hazırlanır. 27 ve 28. slaytlar kaynakta aynı kesiti kullandığından tek dosyayı paylaşır. İlk kayıt 7/8/9. sayfalarda 16.2–74.5, 75.5–146.5 ve 148–242.291 saniyelerinden oynatılır. Dört sayfaya dağılmış diğer kayıt 79–82. sayfalarda 32.682, 91.799, 123.113 ve 239.201 saniyelerinden başlar. PowerPoint p14:trim başlangıç ve sondan kırpma değerleri, küçük boşluk ve örtüşmeler dahil korunur. Kaynakta 71. ve 72. slaytlardaki örtüşen aralık da aynen saklanır; ardışık oldukları varsayılarak değiştirilmez. 42. sayfanın iki kaydı açılır seçim alanından dinlenebilir.

Arayüz onaylanmış 7/8/9. ünite tasarımıdır: Dinle, ses oynatıcısı, cevap düğmesi, tam ekran, PDF dönüşü ve beş dilde sözlük/örnek kartları. PDF sayfasındaki turkuaz, beyaz ▶ simgeli “Sunum Modu” düğmesi 6. üniteyle aynıdır. 9. ünitenin sonraki ünite bağlantısı bu sunuya yönelir.

Sözlük, ünitenin mevcut beş dilli sözlüğünü ve önceki ünitelerin doğrulanmış kayıtlarını kullanır. Ek otel, seyahat, ulaşım ve çekim kayıtları TSV dosyalarındadır. Dil sırası EN, RU, KY, AR, FR'dir. Çeviri servisi kullanılmaz.

## Yeniden hazırlama

Kaynaklar depo yanındaki upload klasöründedir: 01-10.-nite-1.part.pptx, 01-10.-nite-2.part.pptx, 01-10.-nite-3.part.pptx ve karşılaştırma kaynağı 01-10.-nite.pdf.

Depo kökünden:

1. `python tools/a2-unit10-sunu/extract.py 1` (2 ve 3 için de çalıştırın).
2. Her work10/partN içindeki clean/full PPTX'i LibreOffice ile aynı klasöre PDF olarak dönüştürün.
3. `python tools/a2-unit10-sunu/combine.py`
4. `python tools/a2-unit10-sunu/audio.py`
5. Türkçe Tesseract modeli work10/tessdata/tur.traineddata konumundayken `python tools/a2-unit10-sunu/render.py`.
6. Önceki sözlükleri work10/pool içine hazırlayıp `python tools/a2-unit10-sunu/curate.py`.
7. `node tests/verify-lise-a2-unit10-sunum.cjs`
8. `python tools/a2-unit10-sunu/verify_artwork.py`

source-audit.json kaynak denetimini, verification.json Chromium ve piksel kontrol sonuçlarını içerir. Kontroller her seçim alanının merkezini, kullanılan ifadelerin beş dilde anlam ve örneklerini, bütün cevap katmanlarını, 26 sesin Dinle ile gerçekten oynatılmasını ve telefon/tablet/masaüstü genişliklerini kapsar.

Regresyon kontrolü, yalnızca hidden niteliğini değil 41 sayfanın gerçek Chromium ekran görüntülerini karşılaştırır: gösterince sayfa değişmeli, gizleyince önceki görüntü piksel düzeyinde aynen geri gelmelidir.
