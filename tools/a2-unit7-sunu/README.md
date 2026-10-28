# A2 7. Ünite · Akıllı Teknoloji · Sunu Modu

Yüklenen özgün PowerPoint'ten 100 slayt hazırlanır. Kitap resimlerinin kaynak baytları değiştirilmez. Kapaktaki ayrı metin nesnesinde kalan yanlış 6. ünite etiketi 7 olarak düzeltilir. Ayrı eklenmiş 103 kırmızı cevap nesnesi 12 sayfada açılıp kapanır. Resimlerin içindeki özgün kırmızı başlıklar, şekiller ve basılı örnekler korunur.

Kaynakta “Türkçe–İngilizce Kelime Listesi” başlıklı slayt yoktur. Bu başlıkla karşılaşılırsa çıkarma kuralı uygulanır. 21 ve 22. slaytlardaki sonradan eklenmiş iki İngilizce açıklama tablosu kaldırılır; arkalarındaki kitap görselleri korunur.

10 özgün ses dosyasının PowerPoint kırpma bilgileri okunur. 20 kullanım için 19 farklı kesit hazırlanır. Aynı kesiti tekrar kullanan 29 ve 30. slaytlar tek dosyayı paylaşır. Yedi sayfaya dağıtılmış ilk ses kaydı ve üç sayfaya dağıtılmış diğer kayıt kendi başlangıç/bitiş noktalarından kesilir. Okuyucu bu hazırlanmış kesitleri oynatır.

Tasarım, 6. ünitenin kullanıcı tarafından onaylanan son sürümünden alınır: dil ve sözlük kartları, üstte Dinle ve yerel ses oynatıcısı, cevap düğmesi, tam ekran ve PDF dönüşü. Boş açılış slaytı eklenmez. Kelimeler ve kalıplar beş dilli yerel sözlükten anlam ve örnek gösterir. Çeviri servisi kullanılmaz.

## Hazırlama

Kaynak PowerPoint `upload/01-L-SE-A2-7.-N-TE-D-J-TAL-K-TAP.pptx`, PDF karşılaştırma kaynağı `upload/02-7.-nite.pdf` yolundadır. `work7` ara çalışma klasörüdür.

1. `python tools/a2-unit7-sunu/extract.py`
2. `work7/clean.pptx` ve `work7/full.pptx` dosyalarını LibreOffice ile `work7/pdf` içine PDF olarak dönüştürün.
3. `python tools/a2-unit7-sunu/audio.py`
4. `python tools/a2-unit7-sunu/render.py` (Tesseract Türkçe modeli `work7/tessdata/tur.traineddata`)
5. `python tools/a2-unit7-sunu/pool.py`
6. `python tools/a2-unit7-sunu/curate.py`
7. `node tests/verify-lise-a2-unit7-sunum.cjs`

`extra.tsv`, `grammar.tsv` ve `examples.tsv` ek sözlük kayıtlarını içerir. Dil sırası EN, RU, KY, AR, FR'dir. Özgün kaynak denetimi `sunum/source-audit.json`, tarayıcı sonucu `sunum/verification.json` içindedir.
