# Aşama 06: Güvenlik ve Secret Yönetimi (Security & Secrets)

> **Amaç**: Sistemin kimlik bilgilerini, şifreleme anahtarlarını ve müşteri verilerini korumak; yetkisiz erişimleri, kaba kuvvet saldırılarını (brute-force) ve web güvenlik açıklarını prodüksiyona çıkmadan önce bertaraf etmek.

---

## 1. Yapılacak Maddeler (Action Items)

### A. Secret Hijyeni ve Yönetimi (Zero-Secret-in-Code)
- [ ] **Depo Taraması**: Kod tabanında, commit geçmişinde veya pull request'lerde hiçbir API anahtarı, özel anahtar (`.pem`), veritabanı parolası bulunmamalıdır (`gitleaks detect` veya `trufflehog` ile %100 temiz).
- [ ] **Merkezi Secret Yönetimi**: Prodüksiyon parolaları asla düz metin dosyalarda (`.env`) saklanmamalıdır; kurumsal bir secret kasasından (AWS Secrets Manager, HashiCorp Vault, GCP Secret Manager) çalışma zamanında güvenli şekilde enjekte edilmelidir.
- [ ] **Anahtar Rotasyonu (Key Rotation)**: Veritabanı ve harici API anahtarlarının gerektiğinde sıfır kesintiyle yenilenebilmesi (rotation plan) hazır olmalıdır.

### B. Bağımlılık ve Paket Güvenlik Taraması (Supply Chain Security)
- [ ] **Bağımlılık Açık Taraması**: Kod bağımlılıkları taranmalı (`npm audit`, `pip-audit`, `cargo audit`, `trivy fs .`); bilinen `HIGH` veya `CRITICAL` güvenlik açıkları içeren paketler derhal güncellenmeli veya izole edilmelidir.
- [ ] **Pinlenmiş Sürümler**: Tüm üçüncü taraf kütüphaneler tam sürüm numaralarıyla sabitlenmelidir.

### C. Ağ, CORS ve HTTP Güvenlik Başlıkları
- [ ] **Katı CORS Politikası**: `Access-Control-Allow-Origin: *` kesinlikle yasaktır; yalnızca uygulamanın resmi frontend domainleri açıkça listelenmelidir.
- [ ] **Güvenlik Başlıkları (Security Headers)**:
  - `Content-Security-Policy (CSP)`: XSS saldırılarını önlemek için script ve kaynak kısıtlaması.
  - `Strict-Transport-Security (HSTS)`: `max-age=31536000; includeSubDomains; preload` ile HTTPS zorunluluğu.
  - `X-Content-Type-Options: nosniff`: MIME type sniffing engelleme.
  - `X-Frame-Options: DENY`: Clickjacking engelleme.

### D. Hız Sınırlaması ve Kötüye Kullanım Koruması (Rate Limiting & Anti-Abuse)
- [ ] **IP ve Kullanıcı Bazlı Rate Limiting**: Kimlik doğrulama endpoint'lerine (login, register, forgot-password) dakikada en fazla 5-10 deneme sınırı konulmalıdır.
- [ ] **DDoS ve Bot Koruması**: Cloudflare, AWS WAF veya Nginx seviyesinde temel bot filtreleme ve anomali tespiti devreye alınmalıdır.
- [ ] **Girdi Sanitizasyonu ve Doğrulama**: SQL Injection, NoSQL Injection ve SSRF açıklarına karşı tüm kullanıcı girdileri katı şemalar ve ORM parametrik sorguları ile işlenmelidir.

---

## 2. Çıkış Kriteri (Exit Gate)

Aşağıdaki koşulların **tamamı** sağlanmadan Aşama 07'ye geçilemez:
1. `GOLIVE.md` dosyasında Aşama 06 maddelerinin tamamı işaretlenmiş olmalı.
2. Git deposunda çalıştırılan `gitleaks` veya `trufflehog` taraması 0 sızıntı ile sonuçlanmış olmalı.
3. Bağımlılık güvenlik tarayıcısında 0 CRITICAL ve 0 HIGH güvenlik açığı kalmış olmalı.
4. `curl -I <api_url>` ile çekilen başlıklarda HSTS, X-Frame-Options ve kısıtlı CORS domaini doğrulanmış olmalı.

---

## 3. Her Maddenin Nedeni (Rationale)

| Madde | Neden Zorunlu? |
|:---|:---|
| Git Sızıntı Kontrolü | GitHub'a yanlışlıkla push edilen bir AWS veya veritabanı parolası, 60 saniye içinde botlar tarafından taranıp ele geçirilir ve tüm veri tabanı şifrelenebilir / silinebilir. |
| Wildcard CORS Yasağı | `*` tanımlı bir CORS, kötü niyetli sitelerin kullanıcının açık oturumunu kullanarak tarayıcı üzerinden hassas verileri çalabilmesine (Cross-Origin Data Leak) izin verir. |
| Login Rate Limiting | Rate limiting yoksa saldırganlar sözlük saldırısıyla (credential stuffing) kullanıcı hesaplarını kolayca ele geçirebilir. |
| Güvenlik Başlıkları (CSP / HSTS) | Tarayıcı düzeyinde çalışarak XSS ve Ortadaki Adam (MitM) saldırılarını henüz istek gerçekleşirken bloke eder. |

---

## 4. Sık Yapılan Hatalar (Common Pitfalls)

- ❌ **`git rm` ile Secret Sildiğini Sanmak**: Dosyayı silip commit atmak; parolanın git geçmişinde (commit history) sonsuza dek kalması.
- ❌ **CORS'u Geliştirme Kolaylığı İçin Açık Bırakmak**: `Access-Control-Allow-Origin: *` ve `Allow-Credentials: true` kombinasyonuyla devasa güvenlik açığı yaratmak.
- ❌ **Şifreleri Loglamak**: Kullanıcı giriş isteğini loglarken `password` alanını gizlemeden (sanitization) doğrudan log dosyasına yazdırmak.
- ❌ **Kendi Kriptografisini Yazmaya Çalışmak**: Standart bcrypt/argon2 yerine basit hash'ler veya ev yapımı şifreleme yöntemleri kullanmak.
