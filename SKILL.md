---
name: golive-skill
description: Use when preparing, auditing, executing, or tracking a production go-live, deployment, or release across backend, frontend, and cloud/on-prem/edge environments. Trigger with "deploy", "canlıya alma", "go-live", "production'a çıkış", "release checklist", "deployment gate".
---

# Go-Live Orkestrasyon ve Canlıya Alma Becerisi (`golive-skill`)

Bu beceri; **Backend → Kalite & Eval → Frontend → Paketleme → CI/CD → Güvenlik → Gözlemlenebilirlik → Yayın & Rollback** akışını adım adım yönetir. Durum bilgisini repo içindeki `GOLIVE.md` durum dosyasında tutar ve çıkış kapıları (exit gates) onaylanmadan sonraki aşamaya geçişe izin vermez.

---

## 🔒 Dokunulmaz Güvenlik ve Kural Öncelikleri (Prime Rules)

Ajan bu beceriyi yürütürken aşağıdaki 3 kuralı **asla ihlal edemez**:

1. **Yıkıcı İşlemlerde Plan ve Onay Zorunluluğu**:
   - Veritabanı tablolarını/kolonlarını silme, veri dönüştürme, çalışan container/pod'ları durdurma, DNS değiştirme veya altyapıyı yeniden kurma (`terraform apply`, `helm upgrade`) gibi geri dönülemez adımlardan önce kullanıcıya açık bir etki analizi (impact analysis) sunulmalı ve **açık onay alınmadan** komut çalıştırılmamalıdır.
2. **Sıfır Secret Prensibi (Zero-Secrets-in-Code)**:
   - Parolalar, API anahtarları, özel sertifikalar asla kod içine, commit mesajlarına, PR açıklamalarına veya `GOLIVE.md` dosyasına yazılmaz.
3. **Hedef Ortam ve Bağlam Doğrulaması (Context Verification)**:
   - Herhangi bir dağıtım veya kontrol komutu çalıştırılmadan önce aktif ortam (`$env:NODE_ENV`, `kubectl config current-context`, `aws sts get-caller-identity`, veritabanı hostname'i) kontrol edilmeli; yanlış hesapta veya ortamda işlem yapılmadığı kesinleştirilmelidir.

---

## 🔄 Yaşam Döngüsü ve Çalışma Mantığı (Workflow)

```
[Başlat] 
   │
   ▼
1. GOLIVE.md Oku / Oluştur (assets/GOLIVE.template.md)
   │
   ▼
2. Hedef Sahaları Belirle (Cloud, On-Premises, Edge)
   │
   ▼
3. Ön Tarama Yap (scripts/audit.py çalıştır ve mevcutları işaretle)
   │
   ▼
4. Çekirdek Aşamaları Sırayla Yürüt (core/01 -> core/08)
   │   ├─ Her aşamanın çıkış kapısı (Gate) vardır
   │   └─ Gate geçilmeden sonraki aşamaya GEÇİLMEZ
   │
   ▼
5. Seçili Saha Dallarını Yürüt (fields/)
   │
   ▼
6. GOLIVE.md Durumunu Güncelle & Yayını İlan Et
```

---

## 📋 Adım Adım Yürütme Talimatları

### Adım 1: Durum Dosyasını Başlatma (`GOLIVE.md`)
1. Repo kök dizininde `GOLIVE.md` dosyasının varlığını kontrol edin.
2. Eğer dosya **yoksa**:
   - `assets/GOLIVE.template.md` şablonunu okuyun.
   - Proje adı ve tarih ile zenginleştirerek repo köküne `GOLIVE.md` olarak yazın.
3. Eğer dosya **varsa**:
   - Dosyayı okuyun; mevcut aşamayı, onaylanan kapıları ve bekleyen maddeleri hafızaya alın.

### Adım 2: Hedef Sahayı / Sahaları Belirleme
Kullanıcıya veya repo konfigürasyonuna göre projenin nereye çıkacağını belirleyin (birden fazlası seçilebilir):
- ☁️ **Cloud / SaaS**: AWS, GCP, Azure, DigitalOcean, Kubernetes, Sunucusuz (Serverless).
- 🏢 **Müşteri Ortamı (On-Premises)**: Banka/kamu/kurumsal veri merkezleri, air-gapped kapalı ağlar.
- 🤖 **Edge / Cihaz**: NVIDIA Jetson, Raspberry Pi, ARM64 endüstriyel üniteler, robotik sistemler.

### Adım 3: Otomatik Repo Ön Taraması (Pre-Audit)
Repo içindeki hazır bileşenleri elle tek tek aramak yerine denetim betiğini çalıştırın:
```powershell
python <path_to_skill>/scripts/audit.py --path . --sync
```
Bu betik Dockerfile, test dosyaları, CI pipeline'ları, secret sızıntılarını ve sağlık uçlarını tarayarak `GOLIVE.md` dosyasındaki ilgili maddeleri otomatik ön-işaretler.

---

## 🚪 Çekirdek Aşamalar ve Çıkış Kapıları (Core Stages)

Her aşamanın detaylı rehberini ilgili dosyadan okuyun ve kapı şartını sağlayın:

| No | Aşama Dosyası | Temel Odak | Çıkış Kapısı (Gate) Şartı |
|:---|:---|:---|:---|
| **01** | [`core/01-backend-hardening.md`](file:///core/01-backend-hardening.md) | Config şeması, fail-fast, global error handler, `/healthz` & `/readyz`, graceful shutdown, LLM token/cost limiti. | Eksik env değişkeninde uygulamanın anında çökmesi; DB kesildiğinde `/readyz`'nin 503 vermesi. |
| **02** | [`core/02-quality-and-eval.md`](file:///core/02-quality-and-eval.md) | Birim & entegrasyon testleri, E2E kritik akışlar, Golden eval veri seti, gecikme ve yük benchmark'ı. | Testlerin %100 yeşil olması; AI çıktılarının sıfır şema hatası vermesi; p95 SLA limitlerinde kalması. |
| **03** | [`core/03-frontend-readiness.md`](file:///core/03-frontend-readiness.md) | Sıfır hata ile build, bundle optimizasyonu, asset caching, 4-durumlu bileşenler, Error Boundary, API fallback. | `npm run build` hatasız tamamlanması; ağ kopukluğunda sayfanın beyaz ekrana düşmemesi; emoji yasağına uyum. |
| **04** | [`core/04-packaging.md`](file:///core/04-packaging.md) | Multi-stage Dockerfile, non-root kullanıcı, lockfile sabitleme, `.dockerignore`, Trivy CVE taraması. | Konteynerin `root` olmadan çalışması; imaj taramasında 0 CRITICAL açık olması. |
| **05** | [`core/05-ci-cd.md`](file:///core/05-ci-cd.md) | Otomatik test/build pipeline'ı, OIDC ile buluta bağlanma, ana dal koruması, manuel prodüksiyon onay kapısı. | CI adımlarının hatasız tamamlanması; ana dala doğrudan push yasağının aktif olması. |
| **06** | [`core/06-security-and-secrets.md`](file:///core/06-security-and-secrets.md) | Secret taraması (gitleaks), KMS/Vault entegrasyonu, kısıtlı CORS domainleri, CSP/HSTS başlıkları, rate limiting. | Git geçmişinde 0 sızıntı; bağımlılıklarda 0 CRITICAL CVE; CORS wildcard'ının bulunmaması. |
| **07** | [`core/07-observability.md`](file:///core/07-observability.md) | Yapılandırılmış JSON loglama, Correlation/Trace ID, 4 altın sinyal, LLM maliyet/token telemetrisi, alarm kuralları. | Test isteği loglarının JSON formatında aynı trace_id ile düşmesi; deneme alarmının kanala ulaşması. |
| **08** | [`core/08-release-and-rollback.md`](file:///core/08-release-and-rollback.md) | Sıfır kesinti dağıtım (Blue/Green, Rolling), geriye uyumlu DB migrasyonu, duman testleri, tek komutlu anında rollback. | Staging'de geri dönüşün başarıyla denenmiş olması; duman testlerinin 0 hata ile geçmesi. |

---

## 🌐 Saha Dalları Rehberleri (Field Branches)

Çekirdek aşamalar tamamlandıktan sonra, seçilen sahaya özel maddeleri işletin:

1. ☁️ **Cloud / SaaS**:
   - Dosya: [`fields/cloud-saas.md`](file:///fields/cloud-saas.md)
   - Odak: Terraform/IaC drift denetimi, DNS TTL indirimi, otomatik TLS, Kubernetes HPA ve pod kaynak sınırları, bulut bütçe alarmları, Canary routing.
2. 🏢 **Müşteri Ortamı (On-Premises / Air-Gapped)**:
   - Dosya: [`fields/customer-onprem.md`](file:///fields/customer-onprem.md)
   - Odak: Tek parça kurulum paketi, internetsiz kurulum testi, kurumsal proxy ve özel CA sertifikası desteği, çevrimdışı lisans anahtarı, log destek paketi script'i, sıfır dış veri sızıntısı (KVKK).
3. 🤖 **Edge / Cihaz (Embedded / IoT)**:
   - Dosya: [`fields/edge-device.md`](file:///fields/edge-device.md)
   - Odak: ARM64/Cross-compile derleme, offline-first yerel veritabanı (SQLite/RocksDB), A/B dual-partition güvenli OTA güncellemesi, donanım watchdog, flash bellek koruması ve termal dayanıklılık.

---

## 📝 Durum Güncelleme ve Sonuçlandırma Kuralı

- Her aşamanın son maddesi tamamlandığında operatör:
  1. `GOLIVE.md` dosyasındaki ilgili aşama kutularını `[x]` olarak işaretler.
  2. "Çıkış Kapısı" başlığı altına tarih, onaylayan ve kanıt çıktısını (örneğin test raporu, imaj hash'i veya link) işler.
  3. `Mevcut Aşama` alanını bir sonraki aşama adıyla günceller.
- 08-release-and-rollback ve seçili saha kapıları onaylandığında:
  - `Yayın Durumu` alanını `LIVE` olarak günceller.
  - Canlıya çıkış özetini ve metrik bağlantılarını raporlar.
