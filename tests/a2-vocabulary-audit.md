# Lise A2 · 1–7. üniteler · Kelime yazdırma düzeltme raporu

Tarih: 21 Ekim 2026

Önceki denetimde bulunan hatalar giderildi. Okuyucuların CSS tasarımı değiştirilmedi. Yeni çeviriler editoryal olarak hazırlandı; Google Translate veya başka bir çeviri API'si kullanılmadı.

| Ünite | Düzeltme |
|---|---|
| 1 — Tatil Dönüşü | Geçmiş zaman eki açıklaması eklendi. “Hoşça kalın” içindeki emir anlamı, “kalın ünlü” sıfatından ayrıldı. Üç Arapça kayıttaki yabancı alfabe hatası düzeltildi. |
| 2 — Hafta Sonu Planın Ne? | Eksik proje/afiş/duyuru kelimeleri ve özel adlar tamamlandı. İletişim bilgileri ve sayılar yazdırılabiliyor. Yinelenen sayfa anahtarı nedeniyle bozulan satır sonu birleştirmesi düzeltildi: etkin-likler ve yapı-lıyor artık tek kelime. Kesme işaretinin iki biçimi destekleniyor. |
| 3 — Bir Günüm | “Yer çekimi” ve “yaşadığı yer” kullanımlarındaki yer, yemek fiilinin “yer” çekiminden ayrıldı. |
| 4 — Şimdi Haberler | Ayşa adının son harfindeki Kiril/Latin karışıklığı kelime, çekim, ifade ve örnek kayıtlarında düzeltildi. |
| 5 — Dedemin Mesleği | Dil sırası kaymış 645 anlam/çekim/kök/örnek/ifade dizisi beş hedef dile düzeltildi; eksik Fransızca karşılıklar tamamlandı. Eğik çizgili seçenekler ve *= işaretleri temizlenerek önceki 12 bozuk yazdırma kaydı giderildi. Röportaj işareti sözlük anahtarından ayrıldı. Yazı–tura oyunu, normal “yazı” anlamından ayrıldı. |
| 6 — Hayat Birlikte Güzel | Küçük harfle yazılan emir “yaz” da yazmak fiiline bağlandı; “Yaz Okulu” mevsim anlamını koruyor. Ses dizininin kaynak sürümü güncellendi. |
| 7 — Akıllı Teknoloji | Dört emir “yaz” kaydı yazmak fiiline bağlandı. “Sağ ol/sağ olsun” içindeki sağ, yön anlamından ayrıldı. Yeni anlamların ses kayıtları ve doğrulama raporu güncellendi. |

## Doğrulama

- Gerçek okuyucu başlatma, kelime seçme ve yazdırma JavaScript işlevleri Node ortamında çalıştırıldı.
- 146 sayfa × 5 hedef dil = **730 çıktı**, toplam **88.210 kelime/ifade satırı** kontrol edildi.
- Çıktılarda boş/eksik çeviri işareti bulunmadı. Sözlükteki beş dilli dizilerde boş alan veya dil sütunu kayması bulunmadı.
- Bağlama göre değişen kalın, yer, yaz, sağ ve yazı/tura için özel regresyon kontrolleri eklendi. Doğru olan diğer anlamlar korunuyor.
- 7. ünite: 4.291 kelime alanı, 21.455 dil/seçim kontrolü; 100 yazdırma kontrolü; ifade grupları; ses metni kapsamı; yerel MP3 süreleri kontrol edildi.
- 6. ünitenin ses metni kapsamı ve güncel kaynak özeti kontrol edildi.
- Düzeltme aracı ikinci çalıştırmada dosyaları yeniden değiştirmiyor.

Komutlar:

```sh
python tools/repair_a2_print_vocabulary.py
node tests/verify-a2-vocabulary-exports.cjs
python tools/verify_a2_unit7.py
```

Bu sonuç, belirlenen bağlam hatalarının düzeltildiğini ve teknik kapsam kontrollerinin geçtiğini gösterir. Bütün eski örnek cümleler için bağımsız dil uzmanı incelemesi yapıldığı anlamına gelmez. Tarayıcının gerçek yazdırma penceresi görsel olarak sınanmadı; testler okuyucunun ürettiği yazdırma HTML'sini kontrol eder. Daha önce temin edilmeyen 7. ünite dinleme/video dosyalarının durumu bu düzeltmeden ayrıdır.
