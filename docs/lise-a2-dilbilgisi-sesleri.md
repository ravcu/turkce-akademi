# Lise A2 Dil Bilgisi ve Telaffuz — özgün dinleme kayıtları

İlk paket S.001–S.078 olmak üzere 78 kayıt içerir. Kaynak WAV toplamı 1.233.662.856 bayt, Opus toplamı 28.463.997 bayttır (%97,69 küçülme). Toplam süre 4.283,365 saniyedir.

Dosyalar `sesler/Lise-A2-Dilbilgisi-ve-Telaffuz/` altında, kaynak numaraları korunarak saklanır. `manifest.json` dosyasında kod, dosya adı, süre, boyut, kanal sayısı ve SHA-256 yer alır.

Kodlama 48 kHz Opus, değişken bit hızı ve en yüksek kodlayıcı karmaşıklığı ile yapıldı. İki kanalı örnek düzeyinde tamamen aynı olan 43 dosyada tek kanal ve 48 kbit/s; diğer 35 dosyada stereo ve 64 kbit/s hedefi kullanıldı. Seviyeye, hıza, başlangıç ve bitişlere bir düzenleme uygulanmadı. Opus kayıplı bir dağıtım biçimidir; kaynak WAV arşivinin yerine geçmez.

Her çıktı baştan sona çözümlendi. Süreler kaynaklarla karşılaştırıldı; farklar 30 ms sınırının altında. Beş farklı kaydın örnek kesitlerinde kanal başına RMS farkı 0,081 dB altında, dalga biçimi korelasyonu 0,991 üzerinde bulundu. Bu sayısal ölçümler bir algısal kalite sertifikası değildir.

## PDF bağlantıları

`assets/js/lise-a2-dilbilgisi-audio.js`, dosya listesini manifestten alır. On PDF okuyucusu bu ortak dosyayı kullanır. Yeni kayıtlar doğru kodla manifeste eklendiğinde okuyucuda otomatik tanınır.

- 1–6. üniteler: tüm özgün kayıtlar mevcut (S.001–S.073).
- 7. ünite: S.074–S.078 mevcut; S.079–S.084 bekleniyor.
- 8–10. üniteler: sonraki paket bekleniyor.
- S.107.1 gibi alt kayıtlar ayrı kimliktir; S.107 dosyasına yönlendirilmez.
- Eksik kaydın DİNLE düğmesi pasiftir. Sayfa değişince oynatma durur ve kaynak temizlenir.
- Düğmeler resim boyutu değişince yeniden konumlandırılır; basılı metinlerle çakışma kontrol edilir.

## Sonraki paket

`python3 tools/prepare_a2_grammar_audio.py GIRDILER` komutu, numaralı WAV dosyalarını dönüştürür ve mevcut manifeste ekler. `numpy`, `scipy`, `ffmpeg` ve `ffprobe` gerekir. Dosyalar ve güncel manifest birlikte yayımlanmalıdır.
