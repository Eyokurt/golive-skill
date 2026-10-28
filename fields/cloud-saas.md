# Saha Eklentisi: Cloud / SaaS (Cloud & SaaS Field Branch)

> **Amaç**: Genel veya özel bulut ortamlarında (AWS, GCP, Azure, Hetzner vb.) çalışan çok kullanıcılı (multi-tenant) veya bağımsız SaaS mimarilerinde altyapı güvenliği, esnek ölçekleme, alan adı/TLS yönetimi ve bütçe kontrolünü sağlamak.

---

## 1. Yapılacak Maddeler (Action Items)

### A. Altyapı Kod Olarak (Infrastructure as Code - IaC)
- [ ] **Tam Deklaratif Altyapı**: Tüm bulut kaynakları (VPC, subnet, veritabanı, load balancer, S3 bucket) Terraform, OpenTofu, Pulumi veya AWS CDK ile tanımlanmış olmalıdır.
- [ ] **Manuel Değişiklik Yasağı (No ClickOps)**: Bulut konsolundan el ile yapılan hiçbir ayar bulunmamalı; `terraform plan` çıktısında beklenmedik değişiklik (drift) olmamalıdır.
- [ ] **Uzak Durum Kilitleme (Remote State & Lock)**: IaC state dosyaları versiyonlu ve şifreli bir depoda (örn. S3 + DynamoDB table locking) saklanmalıdır.

### B. DNS, Alan Adı ve TLS Sertifika Yönetimi
- [ ] **Otomatik TLS Yenileme**: SSL/TLS sertifikaları Let's Encrypt, AWS ACM veya Cloudflare üzerinden otomatik yenilenen mekanizmalara bağlanmalıdır.
- [ ] **DNS TTL Ayarı**: Canlıya geçiş öncesinde ilgili DNS A/CNAME kayıtlarının TTL süresi düşük bir değere (örn. 60-300 saniye) çekilmeli; böylece olası IP/yönlendirme değişimleri anında yansımalıdır.

### C. Otomatik Ölçekleme ve Kaynak Limitleri (Auto-Scaling & Limits)
- [ ] **Yatay Pod/Sunucu Ölçekleme (HPA / Auto Scaling Groups)**: CPU > %70 veya RPS artışına göre otomatik yeni instance açma ve trafik düşünce küçülme (scale-in) kuralları tanımlanmalıdır.
- [ ] **Kubernetes Resource Requests & Limits**: Her konteyner için minimum `requests` ve tavan `limits` (CPU ve RAM) açıkça belirtilmeli; limitsiz (unbounded) konteyner bırakılmamalıdır.

### D. Bulut Bütçe Alarmları ve Maliyet Kontrolü (FinOps)
- [ ] **Bütçe Alarmı (Budget Alerts)**: Aylık beklenen bulut harcamasının %50, %80 ve %100 eşiklerine ulaşıldığında e-posta/Slack uyarısı gönderen kurallar kurulmalıdır.
- [ ] **Gereksiz Kaynak Temizliği**: Boşta bekleyen NAT Gateway'ler, kullanılmayan unattached EBS hacimleri veya devasa test bucket'ları temizlenmelidir.

### E. Kademeli ve Ağırlıklı Yayın (Canary & Weighted Routing)
- [ ] Ingress veya Service Mesh (Istio, AWS ALB, Cloudflare Workers) üzerinde ağırlıklı trafik bölme (örn. %95 kararlı v1, %5 canary v2) yapılandırması hazır olmalıdır.

---

## 2. Çıkış Kriteri (Field Gate: Cloud/SaaS)

Aşağıdaki koşulların **tamamı** sağlanmadan Cloud sahasına çıkış yapılamaz:
1. `GOLIVE.md` dosyasındaki Cloud/SaaS maddeleri eksiksiz işaretlenmiş olmalı.
2. `terraform plan` komutu sıfır beklenmedik değişiklik (`No changes. Infrastructure is up-to-date.`) üretmeli.
3. TLS sertifikasının geçerliliği ve HSTS başlığı `https://` üzerinden doğrulanmış olmalı.
4. Bulut sağlayıcı bütçe alarmının aktif olduğu panelden doğrulanmış olmalı.

---

## 3. Her Maddenin Nedeni (Rationale)

| Madde | Neden Zorunlu? |
|:---|:---|
| IaC Zorunluluğu | Konsoldan elle açılan bir güvenlik grubu kuralı felaket anında unutulur; altyapıyı başka bir bölgede (region) sıfırdan ayağa kaldırmayı imkansız kılar. |
| Düşük DNS TTL | Canlıya geçiş anında sunucu IP'si veya ingress değişirse, 86400s (24 saat) TTL yüzünden kullanıcıların yarısı eski sunucuya gidip hata almaya devam eder. |
| Resource Limits | Sınır konulmamış tek bir bellek sızıntılı pod, Kubernetes düğümündeki tüm RAM'i tüketip yanındaki kritik veritabanı veya ingress pod'larını da (OOMKilled) öldürür. |
| FinOps Bütçe Alarmı | DDoS saldırısı, hatalı bir worker döngüsü veya auto-scaling bug'ı yüzünden hafta sonu binlerce dolarlık faturayla karşılaşılmasını önler. |

---

## 4. Sık Yapılan Hatalar (Common Pitfalls)

- ❌ **Konsoldan "Hızlıca" Ayar Değiştirmek**: Acil durumda konsoldan IP veya port açıp bunu Terraform koduna eklememek (State Drift).
- ❌ **State Dosyasını Git'e Atmak**: `terraform.tfstate` dosyasını git deposuna ekleyip içindeki veritabanı şifrelerini ifşa etmek.
- ❌ **NAT Gateway Maliyet Tuzağı**: İki farklı kullanılmayan availability zone'a NAT Gateway açıp ayda yüzlerce dolar boş yere ödemek.
- ❌ **Ölçekleme Süresini Hesaba Katmamak**: Yeni sunucunun ayağa kalkıp trafiği kabul etmesinin 3-5 dakika süreceğini unutup ani trafik dalgalanmalarında çökmek.
