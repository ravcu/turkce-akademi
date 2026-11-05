# Lise A1 Dil Bilgisi ve Telaffuz Kitabı – Ses Dosyaları

Bu klasör, Türkçe Akademi **Lise A1 Dil Bilgisi ve Telaffuz Kitabı** için yüksek oranda sıkıştırılmış Opus seslerini saklamak amacıyla oluşturuldu.

## Dosyalar
- Beklenen: 1–60, 64–67, 69–71 numaralı **67 adet** `.opus` ses dosyası.
- Eksik orijinal kayıtlar: **61, 62, 63 ve 68**.
- Orijinal isimleri aynen korunacak, örnek: `Lise - A1 - Dil Bilgisi - 1.opus`.
- Öğrencinin kitabındaki DİNLE kodlarını bu aşamada değiştirmiyoruz. Sesler yerleşince tek tek doğru kayıtlarla eşleştirilecek.

## Tek ZIP dosyasıyla yükleme
1. ChatGPT'nin oluşturduğu `Lise_A1_Dil_Bilgisi_67_Ses_Opus.zip` dosyasını indir.
2. GitHub'da **bu klasörü** aç → **Add file → Upload files**.
3. ZIP dosyasını **`Lise_A1_Dil_Bilgisi_67_Ses_Opus.zip`** adıyla doğrudan buraya yükle ve commit et.
4. `.github/workflows/lise-a1-dilbilgisi-ses-ac.yml` iş akışı ZIP'i doğrular, içindeki 67 Opus sesini burada tek tek açar ve kaydeder. Başarılı çalışırsa ZIP'i depodan kaldırır.

**Not:** GitHub Actions'ın ana dala yazma yetkisi ve dal koruması bu otomatik işlemi etkileyebilir. Actions çalışması başarısız olursa GitHub Actions → `Lise A1 Dil Bilgisi Seslerini Aç` kaydını incele.

**Ses formatı:** Opus, 48 kbps VBR. Orijinal WAV kayıtlar ayrıca güvenli bir yedekte saklanmalıdır.
