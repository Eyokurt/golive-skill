# Aşama 07: Gözlemlenebilirlik (Observability & Monitoring)

> **Amaç**: Canlıdaki sistemin iç durumunu dışarıdan gelen sinyallerle (loglar, metrikler, dağıtık izler ve alarmlar) tam olarak anlayabilmek; sorunları kullanıcılardan önce tespit edip teşhis süresini (MTTD/MTTR) dakikalar seviyesine indirmek.

---

## 1. Yapılacak Maddeler (Action Items)

### A. Yapılandırılmış Loglama (Structured JSON Logging)
- [ ] **JSON Formatı**: Konsola ve dosyalara basılan tüm loglar tek satırlı yapılandırılmış JSON formatında olmalıdır (`timestamp`, `level`, `message`, `service`, `context`).
- [ ] **Korelasyon ve İzleme Kimliği (Correlation / Trace ID)**: Her HTTP/gRPC isteği için tekil bir `x-request-id` veya OpenTelemetry `trace_id` üretilmeli ve bu ID alt servislere, veritabanı sorgularına ve log satırlarına aktarılmalıdır.
- [ ] **Hassas Veri Maskeleme**: Kredi kartı, parola, TCKN, API token gibi PII (Kişisel Tanımlanabilir Bilgi) log satırlarına düşmeden önce otomatik regex maskelemesinden geçirilmelidir.

### B. Temel Servis Metrikleri (The Four Golden Signals)
- [ ] **Trafik (Traffic)**: Saniye başına istek sayısı (Requests Per Second - RPS).
- [ ] **Hata Oranı (Errors)**: Toplam istekler içindeki HTTP 5xx oranı ve unhandled exception frekansı.
- [ ] **Gecikme (Latency)**: İstek tamamlama sürelerinin yüzdelik dağılımı (p50, p95, p99).
- [ ] **Doygunluk (Saturation)**: Pod / sunucu CPU kullanımı, RAM tüketimi, disk doluluk oranı ve veritabanı aktif bağlantı havuzu doluluğu (%80 üstü uyarı vermelidir).

### C. AI / LLM Özel Gözlemlenebilirlik (LLM Telemetry & Cost Tracking)
- [ ] **Token Tüketimi**: İstek ve yanıt başına harcanan girdi/çıktı token sayıları kaydedilmelidir.
- [ ] **Maliyet İzleme**: Model sağlayıcısı bazında anlık ve kümülatif maliyet ($/gün, $/servis) metriğe dönüştürülmelidir.
- [ ] **Model Yanıt Kalitesi ve Gecikmesi**: Time-To-First-Token (TTFT), toplam streaming süresi ve model sağlayıcısının HTTP 429/500 hata oranları izlenmelidir.
- [ ] **Geri Bildirim Döngüsü (User Feedback Tracking)**: Kullanıcıların AI yanıtlarına verdiği olumlu/olumsuz oylar (thumbs up/down) loglanmalıdır.

### D. Alarm Kuralları ve Nöbetçi Entegrasyonu (Alerting & Paging)
- [ ] **Kritik Eşik Alarmları**:
  - Hata Oranı: 5xx yanıtları son 5 dakikada > %1 ise.
  - Gecikme: p95 süresi 3 dakika boyunca > 1500ms ise.
  - Kaynak: Disk alanı < %15 veya RAM kullanımı > %85 ise.
  - LLM Bütçe: Günlük maliyet eşiği aşıldığında (örn. günlük bütçenin %80'ine ulaşıldığında).
- [ ] **Bildirim Kanalları**: Alarmlar doğrudan nöbetçi mühendise veya ilgili Slack/Discord/PagerDuty kanalına gitmeli; alarm metni hatanın ne olduğunu ve runbook bağlantısını açıkça içermelidir.

---

## 2. Çıkış Kriteri (Exit Gate)

Aşağıdaki koşulların **tamamı** sağlanmadan Aşama 08'e geçilemez:
1. `GOLIVE.md` dosyasında Aşama 07 maddelerinin tamamı işaretlenmiş olmalı.
2. Servise gönderilen test isteklerinin oluşturduğu logların merkezi log toplayıcıda (Datadog, Loki, CloudWatch) JSON olarak ve aynı `trace_id` ile görüntülendiği doğrulanmalı.
3. Test amacıyla tetiklenen sahte bir 500 hatası veya yüksek gecikme sonucunda alarm kanalına doğru bildirim düştüğü teyit edilmelidir.
4. LLM token ve maliyet dashboard'unun anlık veri gösterdiği doğrulanmalıdır.

---

## 3. Her Maddenin Nedeni (Rationale)

| Madde | Neden Zorunlu? |
|:---|:---|
| Structured JSON Loglama | Düz metin loglarda milyonlarca satır arasında arama yapmak imkansızdır. JSON loglar Elasticsearch veya Loki ile saniyeler içinde filtrelenebilir. |
| Correlation / Trace ID | Mikroservis mimarisinde veya asenkron kuyruklarda bir kullanıcının yaşadığı hatanın hangi alt serviste meydana geldiğini bulmanın tek kesin yoludur. |
| Doygunluk Takibi | Disk dolduğunda veritabanı kendiliğinden çöker ve veri bozulması yaşanır. %85 doluluk alarmı müdahale için zaman kazandırır. |
| LLM Maliyet Alarmı | Kontrolsüz bir prompt döngüsü veya scraper saldırısı durumunda ay sonunda 50.000 dolarlık fatura şoku yaşamayı engeller. |

---

## 4. Sık Yapılan Hatalar (Common Pitfalls)

- ❌ **Alarm Yorgunluğu (Alert Fatigue)**: Önemsiz her uyarı için nöbetçiyi arayan alarmlar kurmak; zamanla ekibin gerçek kriz alarmlarını da görmezden gelmesine yol açar.
- ❌ **Kişisel Verileri Loglamak**: Şifreleri veya kullanıcı e-postalarını doğrudan loglara yazıp KVKK/GDPR cezalarına maruz kalmak.
- ❌ **Sadece CPU'ya Bakmak**: CPU %15 seviyesinde rahat görünürken veritabanı bağlantı havuzunun tükendiğini veya event loop'un tıkandığını fark edememek.
- ❌ **Alarmın Nereye Gittiğini Test Etmemek**: Alarmları kurup test etmemek ve tatil gününde kimsenin bakmadığı bir e-posta kutusuna düştüğünü kriz anında anlamak.
