# Aşama 05: Sürekli Entegrasyon ve Dağıtım (CI/CD Pipeline)

> **Amaç**: Kodun test edilmesi, taranması, paketlenmesi ve canlıya aktarılması sürecini insan hatasından arındırıp tamamen tekrarlanabilir, şeffaf, onay mekanizmalı ve otomatik bir ardışık düzene (pipeline) oturtmak.

---

## 1. Yapılacak Maddeler (Action Items)

### A. Pipeline Aşamaları ve Katı Kontroller (Strict Automated Gates)
- [ ] **Tetikleyiciler**: Her Pull Request (PR) açıldığında ve ana dala (`main`/`master`) her merge işleminde CI pipeline'ı otomatik tetiklenmelidir.
- [ ] **Sıralı Adım Mimarisi**:
  1. *Lint & Format Check*: Kod standartları ve tip denetimi (`tsc --noEmit`, `flake8`, `biome`, `ruff`).
  2. *Security SAST & Secret Scan*: Statik kod analizi ve sızıntı denetimi (`gitleaks`, `semgrep`).
  3. *Automated Tests*: Birim ve entegrasyon testlerinin yürütülmesi.
  4. *Docker Build & Vulnerability Scan*: Konteyner derleme ve imaj CVE taraması.
  5. *Artifact Publish*: İmajın özel registry'ye (ECR, GCR, Harbor) SHA etiketiyle yüklenmesi.
- [ ] **Adım Geçiş Zorunluluğu (Fail-Fast)**: Herhangi bir aşama (örn. linter veya tek bir birim test) başarısız olduğunda pipeline derhal durmalı ve sonraki adımlara asla geçmemelidir.

### B. Ortam İzolasyonu ve Secret Güvenliği
- [ ] **Ortam Ayrımı (Environment Scopes)**: CI/CD değişkenleri ve yetkileri `Development`, `Staging` ve `Production` ortamları için birbirinden tamamen izole edilmiş olmalıdır.
- [ ] **Kısa Ömürlü Kimlik Bilgileri (OIDC)**: CI/CD sağlayıcısı (GitHub Actions, GitLab CI) ile bulut sağlayıcısı (AWS, GCP, Azure) arasında sabit uzun ömürlü erişim anahtarları (`AWS_ACCESS_KEY_ID`) yerine OpenID Connect (OIDC) ve IAM Rol üstlenme (AssumeRole) kullanılmalıdır.
- [ ] **Log Maskeleme**: Pipeline loglarında secret'ların otomatik sansürlendiği (masked) teyit edilmelidir.

### C. Dal Koruması ve Manuel Onay Kapıları (Branch Protection & Approvals)
- [ ] **Ana Dal Koruması (Branch Protection Rules)**:
  - `main` dalına doğrudan push (`git push origin main`) kesinlikle engellenmiş olmalıdır.
  - En az 1 kıdemli mühendis kod inceleme (PR approval) onayı zorunlu olmalıdır.
  - Tüm CI kontrollerinin (status checks) yeşil olması şart koşulmalıdır.
- [ ] **Production Yayın Onayı (Manual Deployment Gate)**:
  - Staging ortamına dağıtım otomatik yapılabilirken, Production ortamına dağıtım yetkili bir operatörün/yayın sorumlusunun manuel onayı (manual approval button) olmadan başlayamaz.

---

## 2. Çıkış Kriteri (Exit Gate)

Aşağıdaki koşulların **tamamı** sağlanmadan Aşama 06'ya geçilemez:
1. `GOLIVE.md` dosyasında Aşama 05 maddelerinin tamamı işaretlenmiş olmalı.
2. Örnek bir PR açılarak veya tetiklenerek tüm CI adımlarının (Lint -> Test -> Build -> Scan) hatasız tamamlandığı doğrulanmış olmalı.
3. Ana dal koruma kurallarının (Branch Protection) aktif olduğu repository ayarlarından teyit edilmiş olmalı.
4. Production ortamına geçişte manuel onay kapısının devrede olduğu doğrulanmalıdır.

---

## 3. Her Maddenin Nedeni (Rationale)

| Madde | Neden Zorunlu? |
|:---|:---|
| OIDC ile Buluta Bağlanma | CI platformuna kaydedilen statik AWS Access Key sızdırıldığında saldırgan aylarca fark edilmeden tüm altyapınızı silebilir veya crypto madenciliği yapabilir. |
| Branch Protection | Tek bir geliştiricinin yanlışlıkla lokaldeki yarım kalmış veya kırık kodu doğrudan ana dala push'layıp anında canlıya göndermesini engeller. |
| Manuel Prodüksiyon Onayı | Staging'de gözlemlenmemiş veya beklenmeyen bir saatte (örn. Cuma akşamı veya kampanya ortasında) plansız prodüksiyon güncellemesini önler. |
| Otomatik Secret Taraması | Bir geliştiricinin kazara commit'e eklediği OpenAI veya Stripe anahtarının depoya girdiği saniyede yakalanmasını sağlar. |

---

## 4. Sık Yapılan Hatalar (Common Pitfalls)

- ❌ **`git push --force` İznini Açık Bırakmak**: Ana dal geçmişinin kazara ezilmesine yol açmak.
- ❌ **`--no-verify` ile Testleri Atlamak**: CI'da test çalıştırmak yerine `if: always()` koyup başarısız testlere rağmen yayına devam etmek.
- ❌ **CI Loglarına Secret Yazdırmak**: `echo $SECRET_KEY` veya verbose debug logları ile şifreleri konsol çıktısına dökmek.
- ❌ **Tek Ortam Kullanmak**: Staging ortamı olmadan doğrudan geliştirici makinesinden prodüksiyon veritabanına deploy almak.
