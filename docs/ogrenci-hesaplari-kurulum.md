# Türkçe Akademi Öğrenci Hesapları

Bu dal ön hazırlıktır. Supabase projesi ve gerçek bağlantı değerleri olmadan kayıt/giriş çalışmaz.

1. Supabase hesabında proje açın. Authentication > Providers > Email etkin ve e-posta doğrulaması açık olsun.
2. SQL Editor üzerinden `supabase/ogrenci-hesaplari.sql` dosyasını çalıştırın. RLS sayesinde her öğrenci yalnızca kendi verisine erişebilir.
3. `assets/js/supabase-config.example.js` dosyasını `assets/js/supabase-config.js` adıyla kopyalayıp proje URL ve **publishable/anon** anahtarını ekleyin. **Secret / service_role** anahtarını asla siteye yazmayın.
4. Authentication > URL Configuration bölümünde sitenin URL'sini ve `https://ravcu.github.io/turkce-akademi/ogrenci-girisi.html` adresini izinli yönlendirmelere ekleyin. Özel alan adı varsa gerçek URL'yi kullanın.
5. `ogrenci-girisi.html` kayıt/giriş prototipidir. Ana menü bağlantısı, PDF/Sunum sayfa konumu, etkinlik soru cevapları ve sertifika bulut senkronizasyonu henüz entegre edilmedi.
6. `TAStudentCloud.save(key,payload)`, `.load(key)`, `.profile()` fonksiyonları bu sonraki entegrasyon için hazırlanmıştır. Mevcut etkinlik ilerleme anahtarlarına bağlanmalı, çakışmalar ve çevrimdışı durumlar ele alınmalıdır.
7. Mevcut sertifika `ta-student-name` değerini okuyor. Hesaba girişte isim buraya aktarılır; doğrudan kullanıcı hesabından okuma ve cihazlar arası sonuç senkronizasyonu ayrıca tamamlanmalıdır.
8. Üretime çıkmadan önce hesap silme ve gizlilik akışları, e-posta doğrulama ve cihazlar arası testler tamamlanmalıdır.
