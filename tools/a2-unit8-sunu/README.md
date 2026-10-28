# A2 8. Ünite · Spor ve Sağlık · Sunu Modu

Üç özgün PowerPoint parçası, kaynak sırasıyla 25 + 25 + 45 olmak üzere 95 slayt içerir. Kaynak kitap resimlerinin baytları değiştirilmez. Clean ve full türevlerde 380 resim SHA-256 kontrolü yapılır. Kapaktaki ayrı metin nesnesinde kalmış 6. ünite etiketi 8 olarak düzeltilir.

56 slayttaki 303 ayrı kırmızı cevap nesnesi gösterilip gizlenir. Resim içindeki özgün kırmızı başlıklar ve basılı örnek işaretleri korunur. Cevap katmanı kayıpsız, saydam WebP olarak saklanır. Temiz sayfayla birleştirilen katmanın, cevaplı özgün dönüşümle piksel düzeyinde aynı olduğu doğrulanır.

Bu yüklemede ayrı İngilizce çeviri tablosu veya “Türkçe–İngilizce Kelime Listesi” slaytı yoktur. Çıkarma kuralları, bu öğelerle karşılaşılırsa uygulanır.

Beş özgün ses dosyasından dokuz kesit hazırlanır. İlk kayıt kaynakta dört slayta bölünmüştür: 17–66.5, 66.5–140.5, 140.5–223.5 ve 223.3–250.057 saniye. Mesut Özil kaydı iki slayta bölünmüştür: 15–113 ve 113.2–195.587 saniye. Kaynaktaki küçük boşluk ve örtüşmeler korunur. PowerPoint `p14:trim` başlangıç ve sondan kırpma değerleri doğrudan kullanılır; devam sayfasında kayıt başa dönmez.

Arayüz, onaylanmış 7. üniteyle aynıdır. Dinle, yerel ses oynatıcısı, cevap düğmesi, tam ekran, PDF dönüşü ve beş dilde sözlük/örnek alanları vardır. Boş bir açılış sayfası eklenmez. Önceki sözlükler ve bu ünitenin PDF sözlüğü öncelikli kullanılır; ek tarif, bakım, spor ve dil bilgisi ifadeleri TSV kaynaklarında tutulur. Dil sırası EN, RU, KY, AR, FR'dir. Çeviri servisi kullanılmaz.

## Yeniden hazırlama

Depo kökünden çalıştırın. Yüklenen kaynaklar deponun yanındaki `upload` klasöründe bulunur:

- `01-8.-nite-1.part.pptx`
- `01-8.-nite-2.part..pptx`
- `01-8.-nite-3.part.pptx`
- `01-8.-nite.pdf` (karşılaştırma kaynağı)

1. `python tools/a2-unit8-sunu/extract.py 1` (2 ve 3 için tekrarlayın).
2. Her `work8/partN` klasöründeki clean/full PPTX dosyasını LibreOffice ile aynı klasöre PDF olarak dönüştürün.
3. Üç parçanın clean ve full PDF'lerini sırayla `work8/pdf/clean.pdf` ve `full.pdf` olarak birleştirin; kaynak kayıtlarını sıra ve parça bilgisi korunarak `work8/source-objects.json` içine birleştirin.
4. `python tools/a2-unit8-sunu/audio.py`
5. Tesseract Türkçe modeli `work8/tessdata/tur.traineddata` konumundayken `python tools/a2-unit8-sunu/render.py`.
6. Önceki ünite sözlüklerini `work8/pool` içine hazırlayıp `python tools/a2-unit8-sunu/curate.py`.
7. `node tests/verify-lise-a2-unit8-sunum.cjs`
8. `python tools/a2-unit8-sunu/verify_artwork.py`

`source-audit.json` kaynak denetimini, `verification.json` gerçek Chromium kontrollerini içerir. Tarayıcı kontrolü her kelime alanının merkezine erişimi, seçili ifadelerin beş dilde anlam ve örneklerini, 56 cevap düğmesini, 9 sesin gerçekten oynatılmasını ve 1920/1440/1024/768/390 piksel ekran genişliklerini kapsar.
