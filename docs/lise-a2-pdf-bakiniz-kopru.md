# Lise A2 PDF Bakınız Köprüleri

A1 ile aynı tasarım: ders kitabındaki “Bakınız: Dil Bilgisi ve Telaffuz Kitabı – A/B bölümü” işaretinin hemen üstünde turkuaz **↗ TIKLA** butonu. Dil Bilgisi PDF Modunda ilgili konu sayfası `?page=N` ile açılır; “← Ders Kitabına Dön” bağlantısı önceki sayfayı geri açar.

## Bağlı üniteler

| Ünite | “Bakınız” sayısı | Hedef DBTK |
| --- | ---: | --- |
| 1 – Tatil Dönüşü | 6 | `tatil-donusu` |
| 2 – Hafta Sonu Planın Ne? | 5 | `hafta-sonu-planin-ne` |
| 3 – Bir Günüm | 5 | `bir-gunum` |
| 4 – Şimdi Haberler | 6 | `simdi-haberler` |
| 5 – Dedemin Mesleği Bana Göre mi? | 6 | `dedemin-meslegi` |
| 6 – Hayat Birlikte Güzel | 5 | `hayat-birlikte-guzel` |
| 7 – Akıllı Teknoloji | 5 | `akilli-teknoloji` |
| 8 – Spor ve Sağlık | 6 | `spor-yapiyorum-saglikli-besleniyorum` |
| **Toplam** | **44** | **8 ünite** |

Kaynak `pages.json` dosyalarında her bir yönlendirme sayıldı; her hedef sayfa numarasının mevcut Dil Bilgisi PDF sayfa aralığı içinde olduğu kontrol edildi. Sekiz Ders Kitabı ve sekiz Dil Bilgisi okuyucusunda JavaScript sözdizimi kontrolünden geçti.

## Tamamlanması gerekenler

9. ünitenin Dil Bilgisi PDF okuyucusunda `pages.json` henüz bulunamadı. 10. ünitenin Ders Kitabı `pages.json` verisi bu kontrolde geçerli JSON olarak okunamadı ve Dil Bilgisi PDF okuyucusunun `pages.json` dosyası da bulunamadı. **Bu üniteler için doğrulanmamış yönlendirme eklenmedi.** İlgili kitapların PDF Modları tamamlanınca köprü tablosu genişletilmelidir.

Canlı tarayıcıda buton hizalama ve her referansın konu başlığıyla birebir örtüşmesi için ayrıca görsel kullanıcı kabul testi gerekir.
