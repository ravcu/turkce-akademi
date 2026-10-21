# Lise A2 · 6. Ünite · Hayat Birlikte Güzel

16 sayfalık PDF modu, 1–5. ünitelerle aynı okuyucu tasarımını kullanır. CSS değiştirilmedi.

- Sayfalar: 300 DPI, 2670 × 3378 piksel WebP; özgün sıra korunur.
- Kelime alanları: yüklenen PDF’nin gerçek metin koordinatlarından çıkarılır.
- Sözlük: İngilizce, Rusça, Kırgızca, Arapça, Fransızca; ChatGPT tarafından hazırlanan bağlama uygun anlamlar ve örnekler. Çeviri servisi kullanılmaz.
- Birleşik ifadeler ve satır sonunda bölünen kelimeler birlikte seçilir.
- Kök/mastar ve metindeki biçim birlikte gösterilir.
- Sayfa kelimeleri ve kalıp ifadeler seçilen dilde PDF olarak yazdırılabilir.
- Önceki ünite: Dedemin Mesleği Bana Göre mi? Sonraki ünite: Akıllı Teknoloji.
- Metne dayalı cevaplar ve açık uçlu bölümlerin örnekleri `answers.json` içinde bulunur. Açık uçlu cevaplar örnek olarak işaretlenir.

## Sesler

Kelime, anlam ve örnek cümle kayıtları aynı dilin yerel ses modeliyle hazırlanır. Tarayıcı başka bir dilin sesini yerine kullanmaz. Türkçe/İngilizce/Rusça/Arapça/Fransızca: Piper. Kırgızca: önceki doğrulanmış ortak kayıtlar ve eSpeak NG Kyrgyz. Bunlar özgün kitap dinleme kayıtları değildir.

Kaynak modeller: https://github.com/OHF-Voice/piper1-gpl ; https://huggingface.co/rhasspy/piper-voices ; https://github.com/espeak-ng/espeak-ng . Ortak kayıtların kaynakları: `assets/speech-20261013/README.md`. Model ağırlıkları depoda dağıtılmaz.

## Bekleyen özgün medya

S.038–S.045 ve V.007 dosyaları henüz yüklenmedi. Bu kodlar için başka ünitenin kaydı kullanılmaz. Yalnızca dinleme/video kaydıyla belirlenebilecek cevaplar doğrulanmış gibi gösterilmez.

## Kontrol

`tools/check_a2_unit6.py` tüm sayfaların kelime alanlarını, beş dilde anlam ve örneklerini, ifade seçimlerini, altı dilde ses dizinini, cevap alanlarını, PDF çıktısını ve mobil görünümü kontrol eder. Tamamlanan tarayıcı kontrolünün sonucu `verification.json` dosyasına yazılır.

Son doğrulama başarılı: 16 sayfa, 2784 alan (2602 sözcük alanı), 253 kalıp seçimi, 25 satır sonu birleşimi; beş dilde eksik anlam/örnek: 0. Türkçe ve beş hedef dilin kayıtları gerçek tarayıcıda oynatıldı. Her sayfanın beş dilde PDF çıktısı, cevap yerleşimleri ve mobil görünümü kontrol edildi. Rapor: `verification.json`.
