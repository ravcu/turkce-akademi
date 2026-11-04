# Türkçe Akademi — Yeni İçeriklerde Otomatik İlerleme Kaydı

## Amaç
Yeni eklenen kitap, ünite, PDF/Sunum ve Etkinlik sayfaları öğrenci hesabına bağlı ilerleme sistemini unutmasın.

## Nasıl çalışır?
1. Var olan kitapların çoğunda kullanılan `assets/js/media-loader.js`, yeni ortak `ta-progress-auto.js` modülünü de yükler.
2. GitHub'a yeni veya değişmiş öğretim HTML dosyaları gönderildiğinde `.github/workflows/auto-progress.yml` bunları tarar. Ortak yükleyicisi veya otomatik bağlantısı bulunmayan sayfalara script ekleyip GitHub'a commit gönderir.
3. `ta-progress-auto.js` kayıtlı kullanıcıda **ta- ile başlayan ve gizli/veri niteliğinde olmayan** localStorage ilerleme anahtarlarını bulur, Supabase'teki öğrenciye özgü kayıtlarla eşitler. Son açılan sayfa bilgisi de kaydedilir.
4. Önceden `student-position-sync.js` veya `student-progress-bridge.js` kullanan sayfalarda mevcut özel entegrasyon korunur; çifte eşitleme yapılmaz.

## Yeni etkinlik geliştiricilerine kural
- Yeni etkinlikte taslak cevaplarını, seçilen soruyu, puan ve tamamlanma durumunu `ta-...` önekiyle **localStorage**'a kaydet. Böylece bunlar otomatik senkronize edilir.
- Form taslakları için `<form data-ta-progress="benzersiz-etkinlik-kodu">...` kullan; alanların `name` değeri olmalı. Bu, şifre/e-posta gibi alanları kaydetmez.
- localStorage kullanmayan yeni/özel motorlar `window.TAProgressAuto.save('benzersiz-kod', veri)` ve `load('benzersiz-kod')` arabiriminden yararlanabilir. API girişten sonra `ready` olur; kullanan kod hazır olmasını kontrol etmelidir.
- Yeni testin soruları/sırası değişirse kaydedilen veriyi sürüm numarası veya soru kimliğiyle doğrula; eski cevapları başka sorulara yanlış eşleme.
- Öğrenci hesabı olmadan çalışma mevcut cihazda devam eder; bulut kaydı için giriş gereklidir.
- Bu altyapı mevcut sayfaya hiç kaydetme kodu yazılmadan **her olası etkileşimi veya sınav puanını sihirli şekilde keşfedemez**. Standart kayıt sözleşmesi, şablonlara dahil edilmelidir.

## Otomasyon sınırları
- Workflow'in GitHub depoya yazma izni olmalı. Branch koruması veya CI tarafından yazılan commit'in Pages yayını tetiklememesi durumunda, otomatik bağlantı commit'i bir sonraki normal yayımla canlıya geçebilir.
- 500 kayıt/sayfa sınırı koyuldu; büyük veri veya aynı anda çok cihazdan değişiklik için sürümlü çakışma çözümü eklenmesi önerilir.
- Supabase RLS, her kullanıcının kendi kayıtlarını korur; gerçek iki cihaz ve hesap değişimi testi ayrıca yapılmalıdır.
- Otomasyon yalnızca sitedeki öğretim amaçlı HTML dosyalarını hedefler; kitapların PDF dosyalarına veya resimlerine dokunmaz.

## Manuel kontrol
`python3 tools/ensure_auto_progress.py` komutu depodaki bütün öğretim HTML dosyalarını tarar ve eksik bağlantıları ekler.
