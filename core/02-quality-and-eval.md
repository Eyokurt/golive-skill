# Aşama 02: Kalite ve Değerlendirme (Quality & Eval)

> **Amaç**: Sistemin iş mantığı doğruluğunu, regresyon dayanıklılığını ve performans limitlerini prodüksiyon yükü altına girmeden önce kanıtlamak. Geleneksel yazılım testleri ile AI/LLM model davranışsal değerlendirmelerini (eval) birleştirmek.

---

## 1. Yapılacak Maddeler (Action Items)

### A. Birim ve Entegrasyon Testleri (Unit & Integration Testing)
- [ ] **Birim Testleri**: Servisin temel algoritmaları, yardımcı fonksiyonları ve veri dönüşümleri bağımsız mock'lar ile test edilmiş ve tüm testler başarılı (0 failed) olmalıdır.
- [ ] **Entegrasyon Testleri**: Veritabanı işlemleri, kuyruk mekanizmaları ve API controller uçları gerçek veya ephemeral test konteynerleri (örn. Testcontainers) ile test edilmelidir.
- [ ] **Test Kapsama Oranı (Code Coverage)**: İş mantığı (domain logic) için minimum %80 kapsama oranı hedeflenmeli; kritik ödeme, yetkilendirme ve veri silme akışlarında %100 kapsama sağlanmalıdır.

### B. Uçtan Uca (E2E) ve Duman Testleri (Smoke Testing)
- [ ] **Kritik Kullanıcı Yolculukları**: Kayıt olma, giriş yapma, ana fonksiyonu icra etme, veri kaydetme ve ödeme/tamamlama akışları otomatik E2E testleri (Playwright, Cypress veya API suite) ile doğrulanmalıdır.
- [ ] **Karanlık Senaryolar (Negative Testing)**: Geçersiz payload'lar, süresi dolmuş token'lar, büyük dosyalar ve yetkisiz kaynak erişim denemelerinin doğru HTTP 4xx kodlarıyla reddedildiği test edilmelidir.

### C. AI / LLM Değerlendirme Seti (Eval Dataset & Regression Suite)
- [ ] **Altın Veri Seti (Golden Dataset)**: Sistemin karşılaşacağı temsil edici en az 50-100 girdi-çıktı senaryosunu içeren sürüm kontrollü bir eval seti oluşturulmalıdır.
- [ ] **Regresyon ve Kalite Metrikleri**:
  - LLM çıktısının yapısal doğruluğu (JSON şemasına uyum oranı = %100).
  - Semantik benzerlik veya kural bazlı başarı skoru (Accuracy / Precision / Recall >= belirlenen eşik, örn. %90).
  - Güvenlik ve zararlı içerik (Harm / Hallucination / Prompt Injection) taraması.
- [ ] **Eval Karşılaştırması**: Yeni model sürümü veya güncellenen prompt şablonu, önceki temel (baseline) skordan daha düşük puan almamalıdır.

### D. Performans, Gecikme ve Yük Benchmark'ı (Latency & Load Testing)
- [ ] **Gecikme Hedefleri (Latency Budgets)**:
  - Backend API p95 yanıt süresi < 250ms (LLM streaming hariç).
  - LLM Time-To-First-Token (TTFT) < 1200ms, toplam yanıt süresi p95 < 6s.
- [ ] **Yük Dayanıklılığı (Load & Stress Test)**: Hedeflenen eşzamanlı kullanıcı sayısının en az 1.5 katı yük (k6, Locust veya Hey kullanılarak) altında sistemin bellek tüketimi, CPU doygunluğu ve hata oranı ölçülmelidir.

---

## 2. Çıkış Kriteri (Exit Gate)

Aşağıdaki koşulların **tamamı** sağlanmadan Aşama 03'e geçilemez:
1. `GOLIVE.md` dosyasında Aşama 02 maddelerinin tamamı işaretlenmiş olmalı.
2. Tüm birim ve entegrasyon testlerinin geçtiğini gösteren CI/yerel test raporu mevcut olmalı.
3. AI Eval test setinde doğruluk oranı belirlenen eşik değerin üzerinde olmalı ve sıfır şema hatası (`0 schema violations`) üretilmeli.
4. Yük testi altında 5xx hata oranı <%0.1 ve p95 gecikme değeri tanımlanan bütçenin altında kalmalıdır.

---

## 3. Her Maddenin Nedeni (Rationale)

| Madde | Neden Zorunlu? |
|:---|:---|
| Testcontainers ile Entegrasyon | SQLite üzerinde yeşil yanan testler, PostgreSQL'in dialect, constraint veya transaction izolasyonu farkları yüzünden prodüksiyonda patlayabilir. |
| Altın Eval Seti (Golden Dataset) | Prompt'ta yapılan ufacık bir ifade değişikliği, görünüşte iyi çalışsa da kenar vakalarda (edge cases) %30'a varan doğruluk kaybına yol açabilir. |
| Negatif Senaryo Testi | Sadece beklenen akışı test etmek (happy path bias), ilk kötü niyetli veya hatalı kullanıcı girdisinde uygulamanın unhandled exception ile çökmesine sebep olur. |
| Yük & Gecikme Testi | Sistem ilk canlıya çıktığında eşzamanlı 20 kullanıcı geldiğinde veritabanı bağlantı havuzunun dolduğunu görmek yerine bu darboğazı önceden tespit etmek gerekir. |

---

## 4. Sık Yapılan Hatalar (Common Pitfalls)

- ❌ **Yalnızca "Happy Path" Test Etmek**: Sadece doğru girdilerle test yapıp ağ kesintilerini, 429 yanıtlarını veya boş listeleri test etmemek.
- ❌ **Testleri Harici Servislere Bağımlı Bırakmak**: Birim testlerinde gerçek OpenAI veya Stripe API'sini çağırmak (maliyet çıkarır, testleri aşırı yavaşlatır ve ağ kopunca CI'ı bozar).
- ❌ **Eval Setini Güncellememek**: Prodüksiyonda kullanıcıların yaşadığı hatalı cevapları altın eval setine eklememek (Feedback Loop eksikliği).
- ❌ **Gecikmede Sadece Ortalama (Average) Değere Bakmak**: Ortalama 200ms görünürken p99 kullanıcılarının 8 saniye beklediğini fark edememek.
