# Aşama 08: Yayın ve Rollback Hazırlığı (Release & Rollback)

> **Amaç**: Canlıya geçiş anını sıfır kesintiyle (zero-downtime) gerçekleştirmek, yayın sırasında oluşabilecek her türlü felaket senaryosuna karşı saniyeler içinde uygulanabilir, test edilmiş bir geri dönüş (instant rollback) planına sahip olmak.

---

## 1. Yapılacak Maddeler (Action Items)

### A. Sıfır Kesinti Dağıtım Stratejisi (Zero-Downtime Deployment)
- [ ] **Dağıtım Modeli**: Sisteme uygun sıfır kesinti stratejisi seçilmelidir:
  - *Blue/Green Deployment*: Eski ve yeni sürümler paralel çalışır, router trafiği anında yeni sürüme yönlendirir.
  - *Canary Deployment*: Trafiğin önce %5-10'u yeni sürüme yönlendirilir; hata oranları temizse kademeli olarak %100'e çıkarılır.
  - *Rolling Update*: Pod'lar teker teker güncellenir; healthcheck geçmeyen yeni pod trafiğe açılmaz.
- [ ] **Bağlantı Boşaltma (Connection Draining)**: Eski sunucuların kapatılmadan önce üzerlerindeki mevcut HTTP isteklerini tamamlaması (draining timeout: örn. 30s) sağlanmalıdır.

### B. Geriye Uyumlu Veritabanı Migrasyonları (Expand & Contract)
- [ ] **Çift Yönlü Uyumluluk**: Veritabanı şeması değişiklikleri hem eski hem de yeni kod sürümüyle aynı anda çalışabilmelidir:
  - Asla canlıdaki bir kolonu doğrudan silmeyin veya adını değiştirmeyin.
  - 1. Adım (Expand): Yeni kolon ekleyin, kodu hem eskiye hem yeniye yazacak şekilde güncelleyin.
  - 2. Adım (Contract): Eski sürüm tamamen kaldırıldıktan sonra eski kolonu temizleyin.
- [ ] **Migrasyon Geri Alma Testi (Down Migration)**: Yazılan her veritabanı migrasyonunun geri alma (`down` / `revert`) script'i önceden test edilmelidir.

### C. Duman Testleri ve Canlı Doğrulama (Post-Deploy Smoke Tests)
- [ ] **Otomatik Duman Testi**: Dağıtım bittiği saniyede kritik API uçlarına otomatik HTTP sorguları atılmalı ve yanıt kodları doğrulanmalıdır.
- [ ] **Sürüm Doğrulama**: `/version` veya `/build-info` endpoint'i üzerinden çalışan uygulamanın gerçekten beklenen commit SHA ve tag olduğu teyit edilmelidir.

### D. Kesin Rollback Protokolü (Tested Instant Rollback)
- [ ] **Tetikleme Kriterleri**: Rollback kararı duygusal değil, metriğe bağlı olmalıdır:
  - Dağıtım sonrası ilk 5 dakikada 5xx hata oranı > %1 olursa.
  - p95 gecikme değeri önceki sürümün 2 katına çıkarsa.
  - Ana iş akışı (ödeme/giriş) smoke testinde başarısız olursa.
- [ ] **Tek Komutlu Geri Dönüş**: Rollback süreci tek bir CLI komutu veya CI pipeline butonu ile maksimum 3 dakika içinde tamamlanabilir olmalıdır.
- [ ] **İletişim ve Yetki**: Rollback kararını kimin vereceği ve hangi kriz kanalından duyurulacağı önceden belirlenmiş olmalıdır.

---

## 2. Çıkış Kriteri (Final Go-Live Gate)

Aşağıdaki koşulların **tamamı** sağlanmadan sistem CANLI (`LIVE`) ilan edilemez:
1. `GOLIVE.md` dosyasında Aşama 08 maddelerinin tamamı işaretlenmiş olmalı.
2. Staging ortamında simüle edilmiş bir rollback senaryosu yürütülmüş ve eski sürüme sorunsuz dönüldüğü kanıtlanmış olmalı.
3. Otomatik duman testleri prodüksiyonda 0 hata ile tamamlanmış olmalı.
4. Dağıtım sonrası 15 dakika boyunca hata ve gecikme metriklerinin normal sınırlar içinde seyrettiği gözlemlenmiş olmalı.

---

## 3. Her Maddenin Nedeni (Rationale)

| Madde | Neden Zorunlu? |
|:---|:---|
| Expand & Contract Migrasyon | Kademeli dağıtımda eski ve yeni pod'lar 5-10 dakika boyunca aynı veritabanına sorgu atar. Kolon doğrudan silinirse eski pod'lar anında çöker ve rollback imkansızlaşır. |
| Otomatik Smoke Testleri | Gerçek kullanıcıların hatayı fark edip şikayet etmesini beklemek yerine, yayın biter bitmez sorunu ilk 10 saniyede tespit etmeyi sağlar. |
| Tek Komutla Rollback | Gece 02:00'de stres altında olan bir mühendisin karmaşık 15 adımlı manuel komut dizisinde hata yapma ihtimali çok yüksektir. |
| Metrik Bazlı Rollback Kararı | "Düzelir mi acaba?" diye bekleyerek kriz süresini uzatmak yerine objektif eşiklerle anında güvenli limana dönülmesini sağlar. |

---

## 4. Sık Yapılan Hatalar (Common Pitfalls)

- ❌ **Veritabanını Geri Alınamaz Şekilde Değiştirmek**: Kolon silip veya veri tipini dönüştürüp, kod patladığında eski koda geri dönememek (Data Lock-in).
- ❌ **Cuma Akşamı Canlıya Çıkmak**: Destek ekiplerinin ve mühendislerin ulaşılabilirliğinin en düşük olduğu zaman diliminde riskli yayına kalkışmak.
- ❌ **Rollback Prosedürünü Önceden Test Etmemek**: İlk defa gerçek kriz anında rollback yapmaya çalışıp script'in yetki hatası verdiğini görmek.
- ❌ **Trafiği Anında %100 Vermek**: Büyük mimari değişikliklerde canary veya kademeli açılış yapmayıp tüm kullanıcı tabanını aynı anda olası bir hataya maruz bırakmak.
