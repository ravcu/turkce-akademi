# Lise A2 4. Ünite — Şimdi Haberler: devam notu

Kayıt tarihi: 26 Ekim 2026. Kullanıcı: Ramazan Avcu. Depo: ravcu/turkce-akademi.

## Gerçek durum

- A2 3. ünite sunu modu tamamlandı, kullanıcı tasarımı ve sonucu onayladı.
- Onaylı sürüm: a0a4728ed6cee1c4a3b9ced7d94f50ad93d83048.
- Canlı örnek: https://ravcu.github.io/turkce-akademi/kitaplar/lise-a2/bir-gunum/sunum/
- 4. ünite için henüz dönüştürme, görsel/ses üretimi veya yayımlama yapılmadı. Hazır olduğu iddia edilmemeli.
- Kullanıcı kalan kullanım hakkı azaldığı için çalışmayı durdurup yeni konuşmada devam etmek üzere kayıt istedi.

## 4. ünite kaynakları

1. A2 4.ünite.1.part.pptx: YÜKLEME BAŞARISIZ. Dosya erişilebilir olmadı; okunmadı. Yeniden yüklenmeli.
2. A2 4.ünite.2.part.pptx: Bu konuşmada erişildi; ZIP/PPTX temel envanteri kontrol edildi.
   - Boyut: 90.150.367 bayt.
   - Slayt sayısı: 52.
   - Medya: 62 PNG, 1 JPG, 7 WAV, 1 MP3, 1 SVG. Bunlar paket dosya sayılarıdır; sayfalardaki kullanım/kesit sayısı henüz çıkarılmadı.
   - SHA-256: fd4c197108f1a58d7a0e72d18c13640de50aca68737bc2354e3eec3cf32272b6.
   - Konuşmaya özgü geçici yol: /workspace/scratch/e00e62f8dcc2/upload/01-A2-4.-nite.2.part.pptx.
   - Bu geçici yolun yeni konuşmada bulunacağı varsayılmamalı.
   - Kalıcı dosya kaydı iki denemede hazırlama aşamasında başarısız oldu; başarılı bir Library kimliği oluşmadı. Yüklenmiş kalıcı kopya varmış gibi davranılmamalı.
   - Devam ederken kullanıcı iki parçayı da yeniden yüklemeli; 2. parça yeniden geldiğinde bu boyut/hash ile eşleştirilebilir.

## Kullanıcının onaylı kuralları

- A1 ve A2 1–3. ünitelerdeki sunu tasarımı korunacak. Yeniden tasarım yapılmayacak.
- Slaytlar özgün PowerPoint görüntüsü korunarak 2400 × 1350 piksel hazırlanacak.
- Gömülü dinleme kayıtları çıkarılıp DİNLE butonuyla bağlanacak.
- Aynı ses birkaç sayfaya bölündüyse sonraki sayfa kaydın başına dönmeyecek. Kaynak PowerPoint p14:trim süreleri okunacak; end değeri sondan kırpılan süredir.
- Sayfa değişince dinleme duracak.
- Kırmızı cevap yazıları, daireler ve ayrı SVG tikleri Cevapları Göster/Gizle düğmesine bağlanacak.
- Türkçe–İngilizce Kelime Listesi sayfaları sunuya alınmayacak; çevirilerinden yararlanılabilecek.
- Ek İngilizce çeviri sekmeleri/tam çeviri tabloları kaldırılacak. Bunlar bazen Türkçe görselin üstüne yerleştirilmiş ayrı resimlerdir. Alttaki Türkçe içerik korunmalı.
- Kelimeler ve birleşik ifadeler tıklanabilir olacak; EN/RU/KY/AR/FR anlamlar, yalın hâl ve metindeki biçim, doğal örnekler ve ses seçenekleri korunacak.
- Kod ve üretilen dosyalar aşamalı biçimde GitHub'a kaydedilecek. Sonu beklenmeyecek.
- Masaüstü/mobil görünüm, yatay taşma, cevap katmanı ve ses durdurma davranışı kontrol edilecek.

## Yeniden kullanılacak kaynaklar

- Okuyucu şablonu: kitaplar/lise-a2/bir-gunum/sunum/index.html
- Sözlük biçimi: aynı klasörde assets/translations.json
- Slayt/veri biçimi: assets/slides.json ve assets/word-spots.json
- Ses yöntemi: speech.js; önce A2 1. ünite kayıt arşivi, kayıt yoksa cihazda aynı dile ait tarayıcı sesi. Cihazda dil sesi yoksa başka dilde okutulmaz, açıklama gösterilir.
- Tam üretim araçları: tools/a2-unit3-sunu/
- Kontrol raporu: kitaplar/lise-a2/bir-gunum/sunum/verification.json
- Kaynak nesne denetimi: aynı klasörde source-audit.json

## Sonraki uygulama adımları

1. Kullanıcıdan 4. ünitenin her iki PowerPoint parçasını al.
2. Depodaki güncel şablonu/araçları oku; varsa AGENTS.md talimatlarını uygula.
3. Hedef: kitaplar/lise-a2/simdi-haberler/sunum/ ; üretim araçları için tools/a2-unit4-sunu/.
4. 3. ünite araçlarının üniteye özel dosya adları, kaynak slayt numaraları, İngilizce resim adları ve tik SVG adları yeni kaynağa göre incelenerek değiştirilmeli; körlemesine kopyalanmamalı.
5. Kelime listesi ve İngilizce eklentileri çıkar; Türkçe tabloları ve özgün görselleri koru. Cevaplı/cevapsız yerel PPTX kopyalarını PDF'ye aktar; 2400 piksel WebP üret.
6. Sesleri geçici dosyada kesip sürelerini doğrula, sonra atomik olarak hedefe taşı. 3. ünitede iki sesin sonradan eksik yazıldığı görüldü; bu nedenle tüm çıktıların sürelerini aktarım öncesi tekrar doğrula.
7. OCR/sözlük alanlarını çıkar; çeviri boşluklarını ve yalın hâlleri kontrol et. Aynı şablonun kelime/çekim/örnek veri biçimleri korunmalı.
8. 4. ünite PDF sayfasındaki sunu bağlantısını ve 3. ünite sunusundaki sonraki ünite bağlantısını yayıma hazır olduğunda güncelle.
9. Aşamaları GitHub'a kaydet; resimlerin açıldığını, boyutlarını ve ses sürelerini doğrula. Aktarılan dosyaları Git blob SHA ile karşılaştır.
10. GitHub Pages dağıtımını ve canlı adresi kontrol et. Dağıtım tamamlanmadan yayında denmemeli.

## Teknik notlar

- Önceki çalışma ortamında Python/lxml/Pillow/PyMuPDF, ffmpeg/ffprobe, LibreOffice ve Tesseract kullanıldı.
- Türkçe OCR modeli /tmp/tur.traineddata idi; bu geçici dosyanın yeni ortamda bulunacağı varsayılmamalı.
- GitHub bağlantı araçlarıyla dosyalar blob/tree/commit/ref akışıyla yazılabiliyor. Aynı main dalındaki başka çalışmaları korumak için yeni ağaç güncel dal başından kurulmalı; ref güncellemesinde expected_sha kullanılmalı.
- Büyük ikili dosyalar okunurken base64 parçaları 393216 bayt üzerinden birleştirildi; her blobun SHA'sı yerel git hash-object ile doğrulandı.
- Ortamda bazı büyük tek seferlik yazımlar eksik kalabildi. Büyük dosyaları atomik yazım ve boyut/hash doğrulaması olmadan tamamlanmış sayma.
- 3. ünite için kullanılan geçici rebuild/ klasörü ve araç belleği yeni konuşmaya aktarılmış kabul edilmemeli. Esas kaynak GitHub'daki kayıtlı dosyalardır.
