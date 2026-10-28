# Go-Live State Tracker (`GOLIVE.md`)

> **Durum Dosyası Protokolü**: Bu dosya, canlıya alma (go-live) sürecinin resmi durum kaydıdır. Aşamalar tamamlandıkça işaretlenir, çıkış kapıları (exit gates) geçilmeden sonraki aşamaya başlanmaz.

---

## 📌 Proje ve Yayın Üst Verileri

- **Proje Adı**: [PROJE_ADI]
- **Hedef Sürüm / Tag**: `v1.0.0`
- **Hedef Sahalar (Fields)**:
  - [ ] Cloud / SaaS
  - [ ] Müşteri Ortamı (On-Premises / Enterprise)
  - [ ] Edge / Cihaz (Embedded / IoT)
- **Başlangıç Tarihi**: YYYY-MM-DD
- **Son Güncelleme**: YYYY-MM-DD HH:MM
- **Sorumlu / Yayın Yöneticisi**: @operator
- **Mevcut Aşama**: `01-backend-hardening`
- **Yayın Durumu**: `IN_PROGRESS` <!-- PENDING | IN_PROGRESS | GATE_BLOCKED | READY_FOR_DEPLOY | LIVE | ROLLED_BACK -->

---

## 🚦 Çıkış Kapıları Özeti (Gates Summary)

| No | Aşama Adı | Saha Dalları | Durum | Onaylayan / Tarih |
|:---|:---|:---|:---:|:---|
| 01 | Backend Sertleştirme | Tümü | 🟡 BEKLİYOR | - |
| 02 | Kalite & Eval | Tümü | ⚪ KUYRUKTA | - |
| 03 | Frontend Hazırlığı | Tümü / İlgili | ⚪ KUYRUKTA | - |
| 04 | Paketleme | Tümü | ⚪ KUYRUKTA | - |
| 05 | CI/CD | Tümü | ⚪ KUYRUKTA | - |
| 06 | Güvenlik & Secret Yönetimi | Tümü | ⚪ KUYRUKTA | - |
| 07 | Gözlemlenebilirlik (Observability) | Tümü | ⚪ KUYRUKTA | - |
| 08 | Yayın & Rollback Hazırlığı | Tümü | ⚪ KUYRUKTA | - |
| F1 | Saha Eklentisi: Cloud / SaaS | Cloud | ⚪ KUYRUKTA | - |
| F2 | Saha Eklentisi: Müşteri Ortamı | On-Prem | ⚪ KUYRUKTA | - |
| F3 | Saha Eklentisi: Edge / Cihaz | Edge | ⚪ KUYRUKTA | - |

*(Durum simgeleri: 🟢 GEÇTİ, 🟡 DEVAM EDİYOR, 🔴 BLOKE, ⚪ KUYRUKTA, 🔘 KAPSAM DIŞI)*

---

## 🛠️ Çekirdek Aşamalar (Core Checklist)

### Aşama 01: Backend Sertleştirme
> Rehber: `core/01-backend-hardening.md`
- [ ] Ortam değişkenleri schema doğrulaması (Zod / Pydantic / Envalid) ile başlatılıyor; eksik değişkende fail-fast çalışıyor.
- [ ] Merkezi hata yakalama (Global exception handler), hassas stack trace sızıntısını engelliyor.
- [ ] Kimlik doğrulama & yetkilendirme (AuthN/AuthZ) middleware ve token doğrulaması tam.
- [ ] `/healthz` (liveness) ve `/readyz` (readiness; DB/Redis/upstream kontrolleri) endpoint'leri aktif.
- [ ] Graceful shutdown sinyalleri (SIGTERM/SIGINT) dinleniyor; aktif istekler ve havuzlar temiz kapatılıyor.
- **AI/LLM Özel Maddeleri**:
  - [ ] Prompt ve model versiyonları kodda sabit değil, konfigürasyondan dinamik okunuyor.
  - [ ] LLM API zaman aşımı (timeout), yeniden deneme (exponential backoff) ve fallback modeli hazır.
  - [ ] Kullanıcı/oturum bazlı token ve bütçe maliyet limitleri (cost rate limiter) devrede.
- **Çıkış Kapısı (Gate 01)**:
  - Durum: `[ ] ONAYLANDI`
  - Kanıt / Log Çıktısı: 

---

### Aşama 02: Kalite ve Eval
> Rehber: `core/02-quality-and-eval.md`
- [ ] Birim ve entegrasyon testleri (Unit & Integration tests) yeşil (0 failure).
- [ ] Kritik iş akışları (E2E) başarıyla simüle edildi.
- [ ] AI / RAG regresyon eval veri seti (Golden dataset) doğrulandı; minimum doğruluk eşiği aşıldı.
- [ ] Servis gecikme ve verim benchmark'ı (p95 / p99 latency) hedeflenen SLA limitlerinde.
- **Çıkış Kapısı (Gate 02)**:
  - Durum: `[ ] ONAYLANDI`
  - Test Raporu Bağlantısı / Özeti: 

---

### Aşama 03: Frontend Hazırlığı
> Rehber: `core/03-frontend-readiness.md`
- [ ] Production build (`npm run build` / `vite build`) hatasız ve 0 lint uyarısıyla tamamlanıyor.
- [ ] Bundle boyutu ve code-splitting optimize edildi; gereksiz ağır kütüphaneler ayıklandı.
- [ ] Statik varlıklar (assets) için cache-busting ve doğru `Cache-Control` başlıkları belirlendi.
- [ ] 4-Durumlu bileşen kontrolü: Loading skeleton, Empty, Error (retry butonlu), Interactive states.
- [ ] Hata yakalama sınırları (React/Vue Error Boundaries) çökmeleri izole ediyor.
- [ ] Backend API erişilemediğinde kullanıcıya graceful fallback / offline mesajı gösteriliyor.
- **Çıkış Kapısı (Gate 03)**:
  - Durum: `[ ] ONAYLANDI`
  - Build Çıktısı Boyutu: 

---

### Aşama 04: Paketleme (Packaging & Containerization)
> Rehber: `core/04-packaging.md`
- [ ] Multi-stage `Dockerfile` kullanılıyor; build araçları ve SDK'lar son imaja sızmıyor.
- [ ] Container non-root kullanıcı (UID != 0) ile çalıştırılıyor.
- [ ] Bağımlılıklar kilitli dosyalardan kuruluyor (`package-lock.json`, `poetry.lock`, `uv.lock`, `go.sum`).
- [ ] Container imajı güvenlik taramasından geçirildi (Trivy / Grype / Snyk - 0 Critical).
- [ ] `.dockerignore` dosyası `.git`, `.env`, test dosyaları ve yerel artıkları dışlıyor.
- **Çıkış Kapısı (Gate 04)**:
  - Durum: `[ ] ONAYLANDI`
  - Container İmaj Hash / Boyutu: 

---

### Aşama 05: CI/CD Pipeline
> Rehber: `core/05-ci-cd.md`
- [ ] Pipeline her PR ve ana dalda otomatik tetikleniyor (Lint -> Test -> Build -> Scan).
- [ ] Ortam izolasyonu (Dev / Staging / Prod) sağlandı; secret'lar doğrudan pipeline içine enjekte edilmiyor.
- [ ] Ana dal (main/master) için branch protection aktif (en az 1 onay + yeşil CI şartı).
- [ ] Production yayını manuel onay kapısına (environment approval gate) bağlı.
- **Çıkış Kapısı (Gate 05)**:
  - Durum: `[ ] ONAYLANDI`
  - Pipeline Çalışma ID / Linki: 

---

### Aşama 06: Güvenlik ve Secret Yönetimi
> Rehber: `core/06-security-and-secrets.md`
- [ ] Kod deposunda hardcoded secret, token veya private key tespiti yapılmadı (gitleaks / trufflehog temiz).
- [ ] Production secret'ları güvenli bir vault (AWS Secrets Manager, GCP Secret Manager, Vault) üzerinden temin ediliyor.
- [ ] CORS politikaları sadece izinli domainlere kısıtlandı (asla wildcard `*` yok).
- [ ] Güvenlik başlıkları (CSP, HSTS, X-Content-Type-Options, X-Frame-Options) devrede.
- [ ] API endpoint'lerinde Rate Limiting ve brute-force koruması aktif.
- **Çıkış Kapısı (Gate 06)**:
  - Durum: `[ ] ONAYLANDI`
  - Güvenlik Tarama Özeti: 

---

### Aşama 07: Gözlemlenebilirlik (Observability)
> Rehber: `core/07-observability.md`
- [ ] Yapılandırılmış JSON loglama standardı devrede (Correlation ID / Trace ID her istekte taşınıyor).
- [ ] Kritik metrikler toplanıyor: İstek sayısı (RPS), hata oranı (5xx), p95/p99 latency, CPU/RAM doygunluğu.
- [ ] LLM kullanım metrikleri devrede: Token sayısı, maliyet ($/gün), sağlayıcı hata oranları, model yanıt süresi.
- [ ] Pager/Slack/E-posta alarm kuralları tanımlı (Örn: 5xx > %1 ise 5 dk boyunca, disk doluluğu > %85).
- **Çıkış Kapısı (Gate 07)**:
  - Durum: `[ ] ONAYLANDI`
  - Dashboard & Alarm Bağlantıları: 

---

### Aşama 08: Yayın ve Rollback Hazırlığı
> Rehber: `core/08-release-and-rollback.md`
- [ ] Sıfır kesinti (Zero-downtime) stratejisi belirlendi (Blue/Green veya Rolling Update).
- [ ] Geri dönüş (Rollback) senaryosu önceden test edildi ve 5 dakika içinde uygulanabilir durumda.
- [ ] Veritabanı migrasyonları geriye uyumlu (Backward-compatible; expand-and-contract modeli).
- [ ] Yayın esnasında ve sonrasında izlenecek duman testleri (Smoke tests) listesi hazır.
- **Çıkış Kapısı (Gate 08)**:
  - Durum: `[ ] ONAYLANDI`
  - Rollback Komutu Doğrulandı: 

---

## 🌐 Saha Dalları (Field Branches)

### Saha F1: Cloud / SaaS
> Rehber: `fields/cloud-saas.md` (Sadece Cloud sahası seçildiyse)
- [ ] Altyapı kod olarak tanımlı (IaC: Terraform / Pulumi / OpenTofu); elle (clickops) değişiklik yok.
- [ ] DNS, TLS/SSL sertifikaları otomatik yenilemeli (Let's Encrypt / ACM) ve HSTS yapılandırılmış.
- [ ] Otomatik yatay ölçekleme (HPA / Auto Scaling Group) metrikleri ayarlandı.
- [ ] Cloud maliyet bütçe alarmları (AWS/GCP/Azure Budget Alert) kuruldu.
- [ ] Kademeli yayın (Canary / Weighted routing) konfigüre edildi.
- **Kapı Durumu**: `[ ] ONAYLANDI`

---

### Saha F2: Müşteri Ortamı (On-Premises / Air-Gapped)
> Rehber: `fields/customer-onprem.md` (Sadece On-Premises seçildiyse)
- [ ] Tek komutlu/offline kurulum paketi (Helm chart / Docker Compose / tarball bundle) hazır.
- [ ] İnternetsiz (Air-gapped) kurulum ve bağımlılık önbellekleri doğrulandı.
- [ ] Kurumsal proxy, özel CA sertifikası ve kısıtlı port kuralları dokümante edildi.
- [ ] Lisanslama kontrolü ve süreli anahtar mekanizması test edildi.
- [ ] KVKK / GDPR uyumu: Müşteri verisi izinsiz dışarı çıkmıyor; lokal loglama ayarlandı.
- **Kapı Durumu**: `[ ] ONAYLANDI`

---

### Saha F3: Edge / Cihaz (Embedded / IoT)
> Rehber: `fields/edge-device.md` (Sadece Edge/IoT seçildiyse)
- [ ] Donanım mimarisi uyumluluğu (ARM64/x86, NPU/GPU CUDA uyumu) test edildi.
- [ ] Tamamen çevrimdışı (offline-first) çalışma ve yerel veri önbellekleme doğrulandı.
- [ ] A/B sistem bölümü veya OTA (Over-The-Air) geri dönüş mekanizması çalışıyor (brick-proof).
- [ ] Bellek sızıntısı (memory leak) ve termal kısılma (thermal throttling) dayanıklılık testi yapıldı.
- [ ] Watchdog timer ve beklenmedik kapanma sonrası otomatik toparlanma devrede.
- **Kapı Durumu**: `[ ] ONAYLANDI`

---

## 🚨 Acil Durum & Rollback Protokolü

Acil bir durumda yayını derhal geri almak için:
1. **Rollback Tetikleyici Şartlar**:
   - 5xx Hata oranı son 3 dakikada > %2 ise
   - Veritabanı bağlantı havuzu kilitlendiyse
   - Kritik kullanıcı akışı (login, ödeme, ana sayfa) çöktüyse
2. **Uygulanacak Tek Komut**:
   - Kubernetes: `kubectl rollout undo deployment/<DEPLOYMENT_NAME> -n <NAMESPACE>`
   - Docker Compose: `docker compose -f docker-compose.prod.yml down && docker compose -f docker-compose.prod.yml up -d --build <PREVIOUS_IMAGE>`
   - Terraform: `terraform apply -var="image_tag=vPREVIOUS"`
3. **İletişim Kanalı**: İlgili kriz kanalı veya yayın odası.
