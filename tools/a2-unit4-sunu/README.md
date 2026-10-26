# A2 4. Ünite — Şimdi Haberler

Özgün iki PowerPoint parçasından, 3. ünitedeki sunu tasarımı korunarak üretilmiştir.

- 102 slayt; her görsel 2400 × 1350 piksel, kayıpsız WebP.
- 63 slaytta ayrı cevap görüntüsü; kırmızı metinler, daireler ve SVG tikleri başlangıçta gizlidir.
- 26 dinleme kesiti; kaynak p14:trim başlangıç ve sondan kırpma süreleri korunur.
- 5.564 tıklama alanı, 1.895 farklı sözlük anahtarı; beş dilde kayıt ve çekimli biçimlerin yalın hâlleri bulunur.
- Kaynakta İngilizce kelime listesi sayfası yoktur; 102 slaytın tamamı tutulmuştur.
- Kaynaktaki iki YouTube bağlantısı ayrı VİDEO düğmesiyle açılır.

## Üretim

Kaynakları çalışma kökünün upload klasörüne `A2 4.ünite.1.part.pptx` ve `A2 4.ünite.2.part.pptx` olarak koyun. `build.py` yerel PowerPoint nesnelerini ayırır. Üretilen dört PPTX'i LibreOffice ile rebuild4/pdf klasörüne aktarın. Türkçe Tesseract modeli `/tmp/tur.traineddata` konumunda olmalıdır. `render.py` görselleri, sesleri ve kelime alanlarını üretir. `finalize.py`, havuz sözlük ile extra.tsv ve examples.tsv dosyalarını kullanır. Üretilmiş assets/translations.json, kaydedilmiş nihai sözlüktür. `verify_assets.py` tüm görüntüleri açıp boyutlarını, ses sürelerini doğrular; eksik yazılmış dosyaları atomik olarak onarır.

Sözlük havuzu oluşturulurken mevcut A2 sözlükleri kullanılmış; bu ünitenin PDF sözlüğüne öncelik verilmiştir. Örnek nesneleri okuyucunun dizi biçimine dönüştürülür. Yayımlanmış sözlükte yalnız bu sunuda kullanılan kayıtlar, yalın hâller ve ilgili kalıplar tutulur.

Kelime sesleri önce mevcut A2 1. ünite kayıt arşivinde aranır. Kayıt bulunamazsa cihazdaki aynı dile ait ses kullanılır. İlgili dil sesi yoksa başka dilde okunmaz; açıklama gösterilir. Dinleme kayıtları cihaz seslerinden bağımsızdır.

Doğrulama: sunum/verification.json.
