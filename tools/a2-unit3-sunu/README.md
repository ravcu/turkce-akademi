# Lise A2, 3. Ünite: Bir Günüm — Sunu Modu

- İki özgün PowerPoint parçasından 113 slayt.
- 2400 × 1350 piksel; özgün görseller korunur.
- 25 yerel PowerPoint ses kesiti; başlangıç ve bitişler kaynak trim verileridir.
- Kırmızı yazılar, daireler ve SVG tikleri ayrı cevap görüntüsündedir.
- Kelime listeleri ve ek İngilizce çeviri tabloları öğrenci sunusuna alınmaz.
- Beş dilde sözlük; metindeki biçim ile yalın hâl birlikte gösterilir.

Girdiler çalışma klasörünün `upload/01-A2-3.-nite.1.part.pptx` ve `upload/01-A2-3.-nite.2.part.pptx` dosyalarıdır. `build.py` kaynak nesneleri ayırır. Üretilen dört PowerPoint'i LibreOffice ile `rebuild/pdf/` içine PDF olarak aktarın. `render.py` görüntüleri, tıklama alanlarını ve kesilmiş sesleri üretir. Tesseract Türkçe modeli `/tmp/tur.traineddata` konumunda olmalıdır. `finalize.py`, ek sözlüğü ve örnekleri uygular. Yayımlanmış sözlük, önceki birleştirilmiş sözlük bulunmadığında başlangıç verisidir.

`repair_english.py` ve `repair_checks.py`, ilk aşamada kaydedilmiş görselleri aşamalı olarak onarmak için kullanılmıştır. Bu kurallar güncel `build.py` içine de işlenmiştir. `recut_audio.py` sesleri geçici dosyada doğruladıktan sonra atomik olarak değiştirir.

Kelime seslendirmesi önce mevcut A2 1. ünite kayıt arşivinde aynı metni arar; kayıt yoksa cihazda aynı dile ait tarayıcı sesini kullanır. Dilin sesi cihazda yoksa farklı bir dilde okunmaz; kullanıcıya açıklama gösterilir. Dinleme kayıtları bundan bağımsızdır.
