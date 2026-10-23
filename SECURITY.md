# Security policy / Güvenlik politikası

## Güvenlik açığı bildirimi

Türkçe Akademi'de bir güvenlik açığı bulursanız lütfen GitHub deposunun **Security → Advisories → Report a vulnerability** bölümündeki özel bildirim özelliğini kullanın (özellik etkinse). Açığın ayrıntılarını herkese açık issue veya pull request açıklamalarında paylaşmayın.

**Hassas bilgi paylaşmayın:** API anahtarları, GitHub token'ları, kişisel veriler ve erişim kodlarını raporlara eklemeyin.

## Kapsam

Bu politika `ravcu/turkce-akademi` kaynak deposunun güvenliğiyle ilgilidir. GitHub Pages'te herkese açık sunulan HTML, JSON, WebP ve ses dosyalarının ziyaretçilerce görüntülenmesi ve indirilmesi teknik olarak engellenemez.

## Bakım ilkeleri

- İş akışlarında yalnızca gereken GitHub token izinleri kullanılmalıdır.
- Sırlar kodda veya statik web dosyalarında saklanmamalıdır; gerektiğinde GitHub Actions secrets kullanılmalıdır.
- Üçüncü taraf GitHub Actions ve bağımlılıkları düzenli gözden geçirilmelidir.
- Yayınlanan içeriklerdeki güvenlik değişiklikleri önce ayrı dalda test edilmelidir.
