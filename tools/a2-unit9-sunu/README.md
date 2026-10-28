# A2 9. Ünite · Bir Hikâyem Var · Sunu Modu

Üç özgün PowerPoint parçası, kaynak sırasıyla 20 + 19 + 40 olmak üzere 79 slayt içerir. Kitap resimlerinin kaynak baytları değiştirilmez; clean/full türevlerinde 262 SHA-256 resim kontrolü yapılır. Kapakta ayrı metin nesnesinde kalan 6. ünite etiketi 9 olarak düzeltilir.

43 slayttaki 263 ayrı kırmızı cevap nesnesi açılıp kapanır. Resimlerin içindeki özgün kırmızı başlıklar ve basılı örnekler korunur. Cevap katmanları kayıpsız ve saydam WebP'dir. Temiz resimle birleştirilen cevap katmanı, cevaplı kaynak dönüşümüyle piksel düzeyinde aynıdır.

Kaynakta ayrı İngilizce açıklama tablosu veya “Türkçe–İngilizce Kelime Listesi” slaytı yoktur. Çıkarma kuralları bu tür nesnelerle karşılaşıldığında uygulanır.

Dört özgün kayıt için beş ses kesiti vardır. İlk kayıt 4. sayfada 17–109.207, 5. sayfada 109.561–214.567 saniyelerinden oynatılır. Diğer kayıtlar 18, 40 ve 53. sayfalardadır. PowerPoint `p14:trim` başlangıç ve sondan kırpma değerleri korunur; devam sayfasında kayıt başa dönmez. FFmpeg ile fiziksel MP3 kesitleri hazırlanır; süre farkı 0.12 saniyeden küçüktür.

Arayüz onaylanmış 7/8. ünite tasarımıdır. Dinle, yerel ses oynatıcısı, cevap düğmesi, PDF dönüşü, tam ekran ve beş dilde sözlük/örnek kartları vardır. PDF sayfasındaki turkuaz, beyaz ▶ simgeli “Sunum Modu” düğmesi 6. üniteyle aynıdır. 8. ünitenin sonraki ünite bağlantısı bu sunuya yönelir. Boş giriş sayfası eklenmez.

Sözlük, 9. ünitenin mevcut beş dilli sözlüğünü ve önceki ünitelerdeki doğrulanmış kayıtları kullanır. Ek sözlük/örnek ve çekim kayıtları TSV dosyalarındadır; dil sırası EN, RU, KY, AR, FR'dir. Çeviri servisi kullanılmaz.

## Yeniden hazırlama

Kaynaklar depo yanındaki `upload` klasöründedir:

- `01-9.-nite-1.pptx`
- `01-9.-nite-2.part.pptx`
- `01-9.-nite-3.part.pptx`
- `01-9.-nite.pdf` (karşılaştırma kaynağı)

Depo kökünden:

1. `python tools/a2-unit9-sunu/extract.py 1` (2 ve 3 için de çalıştırın).
2. Her `work9/partN` içindeki clean/full PPTX'i LibreOffice ile aynı klasöre PDF olarak dönüştürün.
3. `python tools/a2-unit9-sunu/combine.py`
4. `python tools/a2-unit9-sunu/audio.py`
5. Türkçe Tesseract modeli `work9/tessdata/tur.traineddata` konumundayken `python tools/a2-unit9-sunu/render.py`.
6. Önceki sözlükleri `work9/pool` içine hazırlayıp `python tools/a2-unit9-sunu/curate.py`.
7. `node tests/verify-lise-a2-unit9-sunum.cjs`
8. `python tools/a2-unit9-sunu/verify_artwork.py`

`source-audit.json` kaynak kontrollerini, `verification.json` tarayıcı ve piksel doğrulama sonuçlarını içerir. Chromium kontrolü bütün kelime alanlarının merkezlerini, seçilen ifadelerin beş dilde anlam/örneklerini, bütün cevap katmanlarını, beş ses kesitinin Dinle ile gerçekten oynatılmasını ve telefon/tablet/masaüstü genişliklerini doğrular.
