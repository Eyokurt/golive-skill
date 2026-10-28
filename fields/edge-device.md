# Saha Eklentisi: Edge ve Cihaz (Edge, Embedded & IoT Field Branch)

> **Amaç**: Uç cihazlarda (Raspberry Pi, NVIDIA Jetson, endüstriyel IPC'ler, robotik üniteler, drone ve mikrobilgisayarlar) çalışan gömülü yazılımların donanım uyumluluğunu, çevrimdışı dayanıklılığını, kaynak sınırlarını ve hatasız OTA (Over-The-Air) güncelleme güvenliğini temin etmek.

---

## 1. Yapılacak Maddeler (Action Items)

### A. Donanım ve Mimari Uyumluluğu (Hardware & Architecture)
- [ ] **Çoklu Mimari Derleme (Cross-Compilation / Multi-Arch)**: Hedef işlemci mimarisine (`linux/arm64`, `linux/arm/v7`, `linux/amd64`) göre çapraz derlenmiş ve test edilmiş binary veya konteyner imajı üretilmelidir.
- [ ] **Donanım Hızlandırıcı ve Sürücü Doğrulaması**: Model çıkarımı (inference) veya ağır işlem için GPU (CUDA/TensorRT), NPU (Hailo, Rockchip NPU, Coral TPU) veya VPU sürücülerinin doğru sürümleri ve izinleri doğrulanmalıdır.

### B. Çevrimdışı Çalışma ve Yerel Veri Senkronizasyonu (Offline-First)
- [ ] **Kesintisiz Çevrimdışı Mod**: İnternet veya yerel ağ koptuğunda cihazın temel tüm fonksiyonlarını yerel önbellek ve yerel gömülü veritabanı (SQLite, RocksDB, DuckDB) üzerinden sürdürebilmesi sağlanmalıdır.
- [ ] **Kuyruklu Senkronizasyon (Store-and-Forward)**: Ağ bağlantısı geri geldiğinde cihazda biriken telemetri ve olay verileri ağ tıkanıklığı yaratmadan, logaritmik aralıklarla (backoff) sunucuya iletilmelidir.

### C. A/B Güncelleme ve Tuğla Koruması (OTA & Anti-Brick Recovery)
- [ ] **A/B Sistem Bölümleme (Dual Partition OTA)**: Güncelleme aktif olmayan pasif bölüme (Slot B) yazılmalı; cihaz yeniden başladığında yeni sürüm test edilmeli ve sağlık kontrolünden geçmezse otomatik olarak çalışan eski bölüme (Slot A) geri dönmelidir (Fail-Safe Bootloader / RAUC / Mender).
- [ ] **Donanım ve Yazılım Watchdog Timer**: Sistem donduğunda veya ana proses kilitlendiğinde cihazı otomatik olarak yeniden başlatan fiziksel veya yazılımsal watchdog devrede olmalıdır.

### D. Kaynak Sınırları ve Termal Yönetim (Resource Limits & Thermal)
- [ ] **RAM ve Disk Koruma**:
  - RAM kullanım tavanı (örn. toplam belleğin %60'ı) belirlenmeli, OOM killer'ın kritik cihaz süreçlerini öldürmesi engellenmelidir.
  - Flash bellek ömrünü korumak için loglar RAM disk üzerinde (`tmpfs`) tutulmalı veya diske yazım sıklığı sınırlandırılmalıdır.
- [ ] **Termal Kısılma (Thermal Throttling) Dayanıklılığı**: Cihaz yüksek ortam sıcaklığında tam yük altında test edilmeli; CPU frekansı kısıldığında bile kritik algoritmaların zaman aşımına uğramadığı teyit edilmelidir.
- [ ] **Güç Kesintisi Dayanıklılığı**: Cihaz tam veri yazarken elektriğin aniden kesilmesi durumunda dosya sisteminin bozulmadığı (power-loss resilience, journaling/overlayfs) test edilmelidir.

---

## 2. Çıkış Kriteri (Field Gate: Edge/Device)

Aşağıdaki koşulların **tamamı** sağlanmadan Edge sahaya sürüm dağıtılamaz:
1. `GOLIVE.md` dosyasındaki Edge/Cihaz maddeleri eksiksiz işaretlenmiş olmalı.
2. Hedef donanım platformunda (gerçek cihaz üzerinde) en az 24 saatlik stres testi tamamlanmış ve 0 çökme/bellek sızıntısı kaydedilmiş olmalı.
3. Simüle edilmiş hatalı bir OTA güncellemesinde cihazın tuğlaya (brick) dönüşmeden otomatik olarak eski kararlı sürüme döndüğü kanıtlanmalı.
4. Yazma esnasında 5 kez elektrik kesilip yeniden başlatıldığında veritabanı veya işletim sistemi bozulması (corruption) yaşanmadığı test edilmiş olmalıdır.

---

## 3. Her Maddenin Nedeni (Rationale)

| Madde | Neden Zorunlu? |
|:---|:---|
| A/B Güvenli OTA | Sahadaki yüzlerce cihaza uzaktan fiziksel müdahale imkansızdır. Başarısız bir güncelleme cihazı kilitlerse (bricked) sahaya teknik servis göndermek devasa maliyet yaratır. |
| Store-and-Forward | Fabrika veya tarım arazisi gibi noktalarda ağ günlerce kesilebilir. Çevrimdışı önbellekleme yoksa kritik sensör ve üretim verisi kalıcı olarak kaybolur. |
| Flash Bellek Koruması | Cihaz üzerindeki eMMC veya SD kartlar sürekli log yazıldığında aylar içinde aşınarak (wear-out) kalıcı donanım arızasına yol açar. |
| Güç Kesintisi Dayanıklılığı | Endüstriyel ortamlarda ve sahadaki jeneratör geçişlerinde elektrik aniden kesilir. Dosya sistemi bozulursa cihaz bir daha asla boot edemez. |

---

## 4. Sık Yapılan Hatalar (Common Pitfalls)

- ❌ **Geliştirici Bilgisayarında Derleyip ARM'da Çalışacağını Sanmak**: x86-64'e göre derlenen binary'yi Raspberry Pi'ye atıp `Exec format error` almak.
- ❌ **SD Karta Sürekli Debug Logu Yazmak**: Birkaç ay içinde SD kartın yazma ömrünü tüketip cihazı kullanılamaz hale getirmek.
- ❌ **Ağ Kesintisinde Sonsuz Beklemek**: Ağ çağrılarına timeout vermeyip, ağ koptuğunda ana arayüzün veya kontrol döngüsünün donmasına yol açmak.
- ❌ **Tek Partition Üzerine Güncelleme Yazmak**: Güncelleme inerken internet kesildiğinde cihazın yarım kalmış bozuk dosyalarla yeniden başlayamaması.
