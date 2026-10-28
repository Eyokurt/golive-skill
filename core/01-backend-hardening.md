# Aşama 01: Backend Sertleştirme (Backend Hardening)

> **Amaç**: Backend servisinin prodüksiyon yükü, kesintiler ve beklenmedik veri girişleri karşısında çökmesini önlemek; sistemin kendi durumunu bildirebilmesini ve AI/LLM bileşenlerinin maliyet/hata kontrolü altında çalışmasını sağlamak.

---

## 1. Yapılacak Maddeler (Action Items)

### A. Konfigürasyon ve Ortam Doğrulaması
- [ ] **Fail-Fast Başlatma**: Uygulama açılışında tüm ortam değişkenleri (`process.env` / `os.environ`) katı bir şema (Pydantic, Zod, Envalid) ile taranmalı; tek bir zorunlu değişken eksik veya tip uyuşmazlığı varsa uygulama anında durmalı (`exit 1`).
- [ ] **Ortam Ayrımı**: Debug flag'leri (`DEBUG=False`), geliştirme profilleri, yerel mock servisler ve test veritabanı bağlantıları prodüksiyon bayrağıyla kesin olarak kapatılmalı.

### B. Hata Yönetimi ve Dayanıklılık (Error Handling & Resilience)
- [ ] **Merkezi Hata Yakalayıcı (Global Exception Handler)**: Beklenmeyen istisnalar (unhandled exceptions) tek bir merkezden yakalanmalı; kullanıcıya asla ham stack trace veya SQL hata metni dönülmemeli, jenerik bir hata kodu ve Correlation ID iletilmeli.
- [ ] **Bağlantı Havuzları ve Zaman Aşımları (Timeouts & Pool Limits)**: Veritabanı, Redis ve tüm dış HTTP isteklerine katı zaman aşımı süreleri (connect timeout: maks 2s, read timeout: maks 5s) ve connection pool sınırları konulmalı.
- [ ] **Graceful Shutdown**: İşletim sisteminden gelen `SIGTERM` ve `SIGINT` sinyalleri dinlenmeli; yeni istek kabulü durdurulup mevcut isteklerin tamamlanması için makul bir süre (örn. 10-15s) tanınmalı ve bağlantı havuzları temiz şekilde kapatılmalıdır.

### C. Sağlık ve Hazırlık Kontrolleri (Health Endpoints)
- [ ] **Liveness Probe (`/healthz`)**: Sistemin 프로세s olarak canlı olup olmadığını döner (hafif kontrol, DB sorgusu yapmaz).
- [ ] **Readiness Probe (`/readyz`)**: Sistemin istek kabul etmeye hazır olup olmadığını doğrular (veritabanı ping'i, redis bağlantısı, kuyruk bağlantısı). Biri bile hazır değilse HTTP 503 dönmelidir.

### D. Kimlik Doğrulama ve Yetkilendirme (AuthN / AuthZ)
- [ ] Her korumalı endpoint'te JWT/Session doğrulaması yapılmalı; süresi dolmuş veya geçersiz token'lar 401 dönmelidir.
- [ ] Rol ve izin kontrolleri (RBAC / ABAC) servis veya controller katmanında katı şekilde enforced edilmelidir.

### E. AI ve LLM Entegrasyon Sertleştirmesi (AI-Specific Hardening)
- [ ] **Prompt ve Model Sürümleme**: Prompt şablonları ve model isimleri (örn. `gemini-1.5-pro-002`, `gpt-4o-2024-08-06`) kod içine hardcode edilmemeli, versiyonlu konfigürasyon veya CMS/Registry üzerinden yönetilmelidir.
- [ ] **Fallback Modeli & Circuit Breaker**: Birincil model sağlayıcısı 5xx döndüğünde veya rate limit aşıldığında yedek modele (fallback model) geçiş sağlayan bir devre kesici (circuit breaker) bulunmalıdır.
- [ ] **Zaman Aşımı ve Exponential Backoff**: LLM istekleri için kesin üst süre (örn. streaming için 30s) ve logaritmik bekleme süreleriyle en fazla 2-3 yeniden deneme mekanizması olmalıdır.
- [ ] **Kullanıcı ve Oturum Başına Maliyet/Token Limiti**: Kötüye kullanımı ve devasa faturaları engellemek amacıyla kullanıcı başına dakikalık token kotası ve bütçe tavanı tanımlanmalıdır.

---

## 2. Çıkış Kriteri (Exit Gate)

Aşağıdaki koşulların **tamamı** sağlanmadan Aşama 02'ye geçilemez:
1. `GOLIVE.md` dosyasında Aşama 01 maddelerinin tamamı işaretlenmiş olmalı.
2. Zorunlu bir çevre değişkeni silinerek uygulama başlatıldığında uygulamanın anlamlı bir hata mesajıyla hemen çöktüğü (`exit code != 0`) test edilmiş olmalı.
3. `/healthz` HTTP 200 dönerken, veritabanı simüle olarak kesildiğinde `/readyz` anında HTTP 503 dönmeli.
4. LLM endpoint'lerinde birim başına maliyet/token limiti aşıldığında sistemin 429 Too Many Requests döndüğü doğrulanmış olmalı.

---

## 3. Her Maddenin Nedeni (Rationale)

| Madde | Neden Zorunlu? |
|:---|:---|
| Fail-Fast Konfigürasyon | Eksik veya hatalı bir secret çalışma zamanında (runtime) ilk kullanıcı bir fonksiyona tıkladığında `KeyError` verirse veri kaybına ve kötü kullanıcı deneyimine yol açar. |
| Global Exception Handler | Kullanıcıya stack trace göstermek saldırganlara iç kod yapısını, SQL şemasını veya gizli kütüphane sürümlerini ifşa eder (CWE-209). |
| Readiness Endpoint | Kubernetes veya Load Balancer, henüz DB bağlantısı oturmamış pod'lara trafik yönlendirirse kullanıcılar %100 oranında 502/503 hatası alır. |
| Graceful Shutdown | Pod yeniden başlatılırken o an yazılmakta olan veritabanı işlemleri yarıda kesilirse veri bozulması (data corruption) yaşanır. |
| LLM Fallback & Token Limiti | Tek bir sağlayıcının çökmesi tüm servisi kilitler. Token limiti konmazsa sonsuz döngüye giren bir bot dakikalar içinde binlerce dolarlık fatura çıkarabilir. |

---

## 4. Sık Yapılan Hatalar (Common Pitfalls)

- ❌ **Stack Trace Açık Unutmak**: `DEBUG=True` kalmış bir Django veya `express-errors` ile stack trace'in prodüksiyona fırlatılması.
- ❌ **Liveness ile Readiness'ı Karıştırmak**: `/healthz` içine ağır veritabanı sorgusu koymak. Veritabanı biraz yavaşlayınca load balancer tüm pod'ları öldürüp sistemi tamamen çökertir (cascading failure).
- ❌ **Dış Servis İsteklerinde Timeout Vermemek**: `requests.get()` veya `fetch()` çağrısına timeout tanımlamamak; dış servis donduğunda worker thread'lerinin tamamının kilitlenmesi.
- ❌ **AI Çıktılarını Doğrulamadan Kabul Etmek**: LLM'den gelen JSON'ı schema doğrulaması (Zod/Pydantic) yapmadan doğrudan iş mantığına göndermek (Prompt Injection ve Hallucination riski).
