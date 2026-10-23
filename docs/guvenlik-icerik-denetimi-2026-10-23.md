# Türkçe Akademi — Güvenlik ve içerik denetimi (23.10.2026)

> Durum: İlk aşama, salt-okunur kaynak incelemesi. Bu belge güvenlik açığı bulunmadığını veya bütün dosyaların incelendiğini iddia etmez.

## Doğrulanan bulgular

1. Depo herkese açıktır. GitHub Pages'te sunulan HTML, WebP, ses ve JSON içerikleri ziyaretçiler tarafından indirilebilir. Sağ tıklamayı kapatmak veya kodu gizlemek bunu önlemez.
2. `kitaplar/lise-a2/hafta-sonu-planin-ne/sunum/README.md` içinde `native-v2/slides/` için 2400×1350 WebP, `translations.json` için beş dilde sözlük, 323 örneksiz anahtar ve video kaydının korunduğu yazıyor. Bu bilgiler yayımlanan dosyalar ve kullanıcı talebiyle ayrıca karşılaştırılmalıdır.
3. `.github/workflows/prepare-a2-unit5.yml`, `repair-a2-unit5-positions.yml` ve `prepare-a2-unit6.yml` dosyalarında `permissions: contents: write` bulunuyor. Bu yetkiler dosya üretip depoya yazan işler için tanımlanmış. Yetki daraltılmadan önce işlevleri test edilmelidir.
4. `.github/workflows/check-a2-unit6-reader.yml` salt-okunur `contents: read` kullanıyor.
5. `assets/speech-20261013/README.md` üçüncü taraf konuşma modelleri/veri kümeleri ve lisans atıfları içeriyor. Seslerin yeniden dağıtım ve ticari kullanım hakları ayrı değerlendirilmelidir.
6. Depo kökünde `LICENSE` dosyası bulunamadı. Bu durum materyallerin serbest lisanslı olduğu anlamına gelmez.

## Önerilen eylemler

- **Öncelik 1:** Actions iş akışlarını, tetikleyicileri ve yazma yetkilerini tek tek denetle. Özellikle otomatik `git push` yapan işleri gereksiz yere çalıştırma.
- **Öncelik 2:** Yayında gerekli olmayan kaynak PPTX/PDF/ZIP ve geçici üretim dosyalarını envanterle. Dosyaları yedek ve bağımlılık kontrolü olmadan silme; Git geçmişindeki eski sürümler de erişilebilir olabilir.
- **Öncelik 3:** Türkiye Maarif Vakfı materyalleri için kurumsal olarak onaylanan telif/izin metnini belirle. Üçüncü taraf lisans atıflarını koru.
- **Öncelik 4:** Filigranı tek bir örnek sayfada dene; görüntü kalitesi, sözlük tıklama bölgeleri ve cevap katmanları bozulmamalı.
- **Öncelik 5:** A2 2. ünite README ile canlı sürümün video ve sözlük durumunu karşılaştır.

## Değişiklik politikası

Bu rapor dışında canlı kitap, sunu, sözlük, ses, görsel, GitHub Actions veya GitHub Pages ayarları değiştirilmemiştir. Güvenlik düzenlemeleri önce ayrı dalda hazırlanıp test edilmelidir.
