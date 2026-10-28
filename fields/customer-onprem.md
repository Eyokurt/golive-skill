# Saha Eklentisi: Müşteri Ortamı (Customer On-Premises & Enterprise)

> **Amaç**: Müşterinin kendi veri merkezinde, özel sanal bulutunda (VPC) veya tamamen internete kapalı (air-gapped) ortamlarında çalışacak yazılımların kurulum, ağ, lisanslama, uyumluluk (KVKK) ve destek gereksinimlerini eksiksiz karşılamak.

---

## 1. Yapılacak Maddeler (Action Items)

### A. Kurulum Paketi ve Taşınabilirlik (Distribution Bundle)
- [ ] **Kendi Kendine Yeterli Paket**: Docker Compose, Helm Chart veya tek dosyalık binary dağıtım paketi oluşturulmalıdır.
- [ ] **İnternetsiz (Air-Gapped) Kurulum**: Dış internet erişimi olmayan ortamlarda tüm konteyner imajları ve bağımlılıklar tek bir tarball arşivinde (`docker save` / helm offline package) sunulabilmeli ve yerel registry'ye aktarılabilmelidir.
- [ ] **Sistem Gereksinimleri Script'i (Pre-flight Check)**: Müşteri sunucusunda CPU, RAM, disk alanı, Docker/K8s sürümü ve OS çekirdek parametrelerini denetleyen tek komutluk bir `precheck.sh` betiği bulunmalıdır.

### B. Kurumsal Ağ ve Güvenlik Kısıtları (Enterprise Networking)
- [ ] **Özel Proxy ve CA Desteği**: Müşterinin kurumsal HTTP/HTTPS proxy'si (`HTTP_PROXY`, `NO_PROXY`) ve kurum içi özel sertifika yetkilisi (Custom Internal CA / Root Certificate) uygulama tarafından tanınmalı ve konfigüre edilebilmelidir.
- [ ] **Kısıtlı Port Kullanımı**: Sistem sadece belgelenmiş minimum portları (örn. yalnızca 443 ve 80) dinlemeli; dışa rastgele yüksek portlar açmamalıdır.

### C. Lisanslama ve Donanım Bağlama (Licensing & Node Locking)
- [ ] **Çevrimdışı Lisans Doğrulaması**: Müşterinin internete çıkmadan doğrulayabileceği, kriptografik olarak imzalanmış (asymmetric RSA/ECDSA) lisans anahtarı veya süreli dosya mekanizması çalışmalıdır.
- [ ] **Kapasite ve Süre Kısıtları**: Lisansın kullanıcı sayısı, CPU çekirdeği veya son kullanma tarihi kısıtları sisteme entegre edilmeli ve süresi dolmadan önce arayüzde uyarı verilmelidir.

### D. Uzaktan Destek ve Tanılama (Diagnostics & Support)
- [ ] **Destek Paketi Üretici (Support Bundle)**: Müşterinin tek bir komutla (`./support-dump.sh`) sistem loglarını, konfigürasyon özetini (şifreler otomatik maskelenmiş olarak) ve metrikleri tek bir zip arşivi halinde toplamasını sağlayan araç sağlanmalıdır.
- [ ] **Audit Trail (Denetim İzi)**: Sistemdeki tüm yönetici aksiyonları (kullanıcı ekleme, yetki değişimi, veri dışa aktarma) silinemez yerel denetim günlüğüne (audit log) yazılmalıdır.

### E. KVKK, GDPR ve Veri İzolasyonu
- [ ] **Sıfır Dış Veri Sızıntısı**: Telemetri, analitik, harici font veya harici CDN çağrıları müşteri ortamında kesinlikle engellenmeli veya yerelleştirilmelidir (No external calls).
- [ ] **Veri İzolasyonu ve Şifreleme**: Müşteri veritabanı dosyaları ve yedekleri at-rest (disk üzerinde) şifrelenebilmeli; veri silme talepleri için script hazır olmalıdır.

---

## 2. Çıkış Kriteri (Field Gate: Customer On-Premises)

Aşağıdaki koşulların **tamamı** sağlanmadan Müşteri Ortamına paket teslim edilemez:
1. `GOLIVE.md` dosyasındaki Müşteri Ortamı maddeleri eksiksiz işaretlenmiş olmalı.
2. Tamamen internet bağlantısı kesilmiş sanal bir makinede (Air-gapped VM) kurulum paketi başarıyla kurulup ayağa kalkmış olmalı.
3. Pre-flight kontrol script'i yetersiz kaynaklı bir ortamda doğru uyarıları vererek kurulumu güvenle durdurmalı.
4. Ağ dinlemesinde (Wireshark/tcpdump) dış dünyaya herhangi bir izinsiz telemetri veya DNS isteği atılmadığı kanıtlanmalıdır.

---

## 3. Her Maddenin Nedeni (Rationale)

| Madde | Neden Zorunlu? |
|:---|:---|
| Air-Gapped Kurulum | Banka, savunma ve sağlık müşterilerinin sunucuları internete tamamen kapalıdır. Kurulum sırasında `npm install` veya Docker Hub'a gitmeye çalışan yazılım o ortamda asla çalışmaz. |
| Kurumsal Proxy & CA | Kurum içi ağlarda SSL termination yapan kurumsal proxy'ler bulunur. Özel Root CA tanıtılamazsa tüm TLS istekleri `CERTIFICATE_VERIFY_FAILED` hatası verir. |
| Destek Paketi (Diagnostics) | Müşteri ortamına SSH erişimi olamayacağı için, kriz anında müşteriden hızlıca temizlenmiş log paketi alabilmek sorunu çözmenin tek yoludur. |
| Sıfır Dış Arama (KVKK) | Müşterinin hassas ortamından Google Analytics'e veya yabancı bir CDN'e giden tek bir istek bile KVKK/GDPR ihlali ve ağır yasal cezalar doğurur. |

---

## 4. Sık Yapılan Hatalar (Common Pitfalls)

- ❌ **Gizli İnternet Bağımlılığı**: Arayüzde CDN'den font (`fonts.googleapis.com`) veya ikon kütüphanesi çekip air-gapped ortamda ekranın kırılması.
- ❌ **Destek Paketine Secret Yazdırmak**: Müşterinin ürettiği log dump dosyasına veritabanı şifrelerini maskelemeden koyup firmanıza göndertmek.
- ❌ **Sabit Hostname / IP Varsayımı**: Kod içinde `localhost` veya sabit IP adresleri hardcode edip müşterinin özel domain/ağ yapısında çalışmamak.
- ❌ **Pre-flight Kontrolü Yapmamak**: Yetersiz RAM'e sahip sunucuda kuruluma başlayıp kurulumun ortasında sessizce disk bozulmasına yol açmak.
