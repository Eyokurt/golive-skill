# Aşama 04: Paketleme ve Konteynerleştirme (Packaging)

> **Amaç**: Uygulamanın her ortamda (geliştirici makinesi, test kümesi, staging, prodüksiyon) özdeş, izole, güvenli ve en az kaynak tüketecek şekilde hafif bir konteyner imajı veya dağıtım paketi haline getirilmesi.

---

## 1. Yapılacak Maddeler (Action Items)

### A. Çok Aşamalı Derleme (Multi-Stage Builds)
- [ ] **Derleyici ve Çalıştırıcı Ayrımı**: `Dockerfile` içerisinde en az 2 aşama bulunmalı (örn. `builder` ve `runner`).
- [ ] **Temiz Son İmaj**: Derleme için gereken SDK'lar (gcc, python-dev, devDependencies, npm, git) son imajda yer almamalı; yalnızca derlenmiş binary / bundle ve prodüksiyon bağımlılıkları kopyalanmalıdır.
- [ ] **Minimal Taban İmaj**: Mümkün olan en küçük ve güncel resmi taban imaj seçilmelidir (örn. `alpine`, `distroless`, `slim`).

### B. Güvenlik ve İzin Sıkılaştırma (Non-Root & Security)
- [ ] **Non-Root Kullanıcı**: İmaj içinde mutlaka ayrı bir sistem kullanıcısı ve grubu oluşturulmalı (`USER appuser:appgroup` veya `USER 10001:10001`) ve uygulama asla `root` olarak çalıştırılmamalıdır.
- [ ] **İzinler ve Dosya Sahipliği**: Uygulama dosyaları sadece okuma iznine sahip olmalı (`chmod -R 550`), geçici yazma gereken yerler (örn. `/tmp`) açıkça sınırlandırılmalıdır.

### C. Bağımlılık Sabitleme ve Yeniden Üretilebilirlik (Reproducibility)
- [ ] **Kilit Dosyaları (Lockfiles)**: Bağımlılıklar kesinlikle kilit dosyalarından (`package-lock.json`, `pnpm-lock.yaml`, `poetry.lock`, `uv.lock`, `go.sum`, `Cargo.lock`) kurulmalıdır (`npm ci`, `poetry install --no-dev`, `uv sync --frozen`).
- [ ] **İmaj İmzası ve Hash**: Dağıtım için `:latest` etiketi kesinlikle yasaktır; git commit SHA veya semver etiketi kullanılmalı (`myapp:v1.2.0-sha1a2b3c`), imaj digest (SHA256) kaydedilmelidir.

### D. `.dockerignore` ve Varlık Hijyeni
- [ ] `.dockerignore` dosyası eksiksiz tanımlanmalıdır. Aşağıdakiler kesinlikle imaja girmemelidir:
  - `.git`, `.github`
  - `.env`, `.env.*` (yerel secret dosyaları)
  - `node_modules`, `venv`, `__pycache__`, `.pytest_cache`
  - `Dockerfile`, `docker-compose*.yml`, `tests/`, `docs/`
- [ ] İmaj güvenlik tarayıcısı (Trivy, Grype, Docker Scout) ile taranmalı; `CRITICAL` seviyeli bilinen açık (CVE) barındırmamalıdır.

---

## 2. Çıkış Kriteri (Exit Gate)

Aşağıdaki koşulların **tamamı** sağlanmadan Aşama 05'e geçilemez:
1. `GOLIVE.md` dosyasında Aşama 04 maddelerinin tamamı işaretlenmiş olmalı.
2. `docker run --rm <image_tag> whoami` çalıştırıldığında çıktının `root` **olmadığı** kanıtlanmalı.
3. Trivy/Grype tarama raporunda 0 CRITICAL CVE olduğu teyit edilmeli.
4. İmaj boyutu hedeflenen sınırlar içinde olmalı (örn. Node.js backend < 180MB, Python FastAPI < 150MB, Go binary < 40MB).

---

## 3. Her Maddenin Nedeni (Rationale)

| Madde | Neden Zorunlu? |
|:---|:---|
| Multi-Stage Build | İmaj boyutunu 1.5 GB'tan 80 MB'a düşürür. Boyut küçüldükçe ağ transfer süresi, pod açılma hızı (cold start) ve saldırı yüzeyi (attack surface) dramatik olarak azalır. |
| Non-Root Kullanıcı | Konteynerden kaçış (container breakout) açığı oluştuğunda saldırgan doğrudan ana host makinede root yetkisi elde edemez. |
| Lockfile ile Kurulum | `npm install` gibi açık kurulumlar, kütüphane geliştiricisi yama geçtiğinde prodüksiyonda beklenmedik API kırılmalarına yol açar. |
| `.dockerignore` | Yerel makinedeki `.env` dosyasının yanlışlıkla konteyner imajına gömülüp Docker Hub'da herkese açık hale gelmesini önler. |

---

## 4. Sık Yapılan Hatalar (Common Pitfalls)

- ❌ **`root` Olarak Çalıştırmak**: Varsayılan Dockerfile davranışıyla uygulamanın root olarak kalması ve güvenlik açıklarına davetiye çıkarması.
- ❌ **Konteyner İçine `.env` Kopyalamak**: `COPY . .` yaparken `.dockerignore` tanımlamayıp yerel parolaları imaja gömmek.
- ❌ **`latest` Etiketini Prodüksiyona Göndermek**: Rollback anında hangi commit'e dönüleceğinin bilinememesi ve cache tutarsızlıkları.
- ❌ **Katman (Layer) Önbelleğini Boşaltmak**: Kod dosyasını bağımlılık manifestosundan (`package.json`) önce kopyalayıp her kod değişiminde tüm kütüphanelerin sıfırdan indirilmesine sebep olmak.
