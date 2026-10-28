# A2 6. Ünite · Sunum sözlüğü ve kelime alanları

Boş beyaz açılış slaytı çıkarıldıktan sonra gösterilen 76 slaytın görünen metinlerinden kelime alanları çıkarılır. Resim, cevap katmanı ve dinleme kayıtları değiştirilmez. PDF sözlüğü değiştirilmeden sunuya özel `translations.json` üretilir.

`ocr-inputs.json.gz`, özgün seçim alanlarını ve üç metin tanıma geçişinin TSV sonuçlarını içerir. `extra.tsv` bağlama göre hazırlanmış beş dilli anlamları, `examples.tsv` Türkçe örnekleri ve beş dilde karşılıklarını içerir. Dillerin sırası EN, RU, KY, AR, FR'dir. Diğer ünitelerden alınan kayıtlarda dil sırası ve eksiksiz örnek bulunması denetlenir. Çeviri servisi kullanılmaz.

Yeniden üretim:

```sh
python tools/a2-unit6-sunu/rebuild.py
node tests/verify-lise-a2-unit6-sunum.cjs
```

`rebuild.py`, satır sonu bölünmelerini ve elle doğrulanmış metin tanıma hatalarını düzeltir. Boş cevap alanlarına bağlı eski seçimleri kaldırır. Mevcut kalıpların görünen parçaları aynı sözlük kaydına bağlanır. Büyük resimleri kelime sanan hatalı alanlar ve taşan yinelenen alanlar elenir.

Gerçek Chromium kontrolünde bütün slaytlardaki seçim alanlarının merkezinden tıklanabilmesi, bütün seçilen kayıtların beş dilde anlam ve çevrilmiş örnek göstermesi, mobil taşma ve JavaScript hataları denetlenmiştir. Sonuç `sunum/selection-verification.json` içindedir.

