# Lise A1 Dil Bilgisi ve Telaffuz Kitabı – PDF Dinleme Eşleştirmesi

Bu çalışma, 10 ünitenin **PDF Modundaki** sayfa verilerinde bulunan `S.001`–`S.138` dinleme işaretlerini tespit ederek yanlarına **DİNLE** düğmesi koyar.

- Her düğme kendi `S.xxx` koduna bağlıdır.
- `S.001` → `Lise - A1 - Dil Bilgisi - 1.opus` biçiminde eşleşir.
- Opus dosyaları `sesler/Lise A1 dilbilgisi ve telaffuz kitabı ses dosyaları/` klasöründedir.
- Kitap sayfasının görselleri, sözlükleri, cevap anahtarları ve mevcut tasarımı korunur.
- Kayıtlar **yalnızca DİNLE düğmesine basılınca** oynatılmaya çalışılır; sayfa açılırken hepsi indirilmez.
- Sayfa değiştirildiğinde mevcut ses durur.
- Ses oynatıcı önceki/sonraki sayfalar arasında tek instance olarak kullanılır.

## Şu anki seslerin kapsadığı üniteler

| Ünite | Kayıt kodları | Durum |
| --- | --- | --- |
| 1 – Tanışalım | S.001–S.017 | Tam |
| 2 – Sınıftayız / Okuldayız | S.018–S.036 | Tam |
| 3 – Ailem ve Evim | S.037–S.050 | Tam |
| 4 – Bir Günüm | S.051–S.065 | S.061, S.062, S.063 eksik |
| 5 – Şehir Gezisi | S.066–S.079 | S.068 ve S.072–S.079 eksik |
| 6 – Çarşı Pazar | S.080–S.093 | Henüz ses yok |
| 7 – Bugün Hava Nasıl | S.094–S.106 | Henüz ses yok |
| 8 – Geçmiş Olsun | S.107–S.116 | Henüz ses yok |
| 9 – Davetlisiniz | S.117–S.128 | Henüz ses yok |
| 10 – Tatil Planım | S.129–S.138 | Henüz ses yok |

Eksik bir sesin DİNLE düğmesi **pasif** gösterilir ve ses yüklenmediğini belirtir; yanlış bir kayıt oynatılmaz. `S.097.2` ve `S.104.2` gibi ek numaralar için de ayrı özgün ses dosyası sağlanana kadar düğmeler pasif kalır.

## Yeni seslerin eklenmesi

Yeni sesler `Lise - A1 - Dil Bilgisi - N.opus` adıyla mevcut klasöre eklendikten sonra `assets/js/lise-a1-dilbilgisi-audio.js` dosyasındaki `available` kümesine numaraları eklenmelidir. Gelecek aşamada bu listeyi dosya manifestosundan otomatik üretebiliriz.

**Kontrol:** 10 PDF okuyucusunun kodları sözdizimi kontrolünden geçirilmiştir. Gerçek tarayıcıdan oynatma ve sayfadaki düğme yerleşimi canlı yayında ayrıca test edilmelidir.
