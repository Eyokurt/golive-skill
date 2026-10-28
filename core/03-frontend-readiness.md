# Aşama 03: Frontend Hazırlığı (Frontend Readiness)

> **Amaç**: İstemci tarafı uygulamasının (SPA, SSR, Mobile Web) prodüksiyon ortamında yüksek performanslı, dayanıklı, erişilebilir ve kurumsal standartlara uygun (Anti-AI-Slop ilkelerine sadık) bir kullanıcı deneyimi sunmasını sağlamak.

---

## 1. Yapılacak Maddeler (Action Items)

### A. Derleme ve Paket Optimizasyonu (Build & Bundle Optimization)
- [ ] **Sıfır Hata / Uyarı ile Build**: `npm run build` (veya `vite build` / `next build`) komutu sıfır TypeScript tipi hatası ve sıfır linter hatası ile tamamlanmalı.
- [ ] **Paket Boyutu ve Code-Splitting**: 
  - İlk yüklenen JavaScript demeti (Initial JS bundle) gzipped < 200 KB olmalıdır.
  - Rota bazlı dinamik yükleme (`React.lazy`, dynamic `import()`) uygulanmalıdır.
  - Ağır kütüphaneler (Moment.js yerine Day.js, Lodash yerine native ES6) elenmelidir.
- [ ] **Statik Varlık Yönetimi ve Önbellekleme (Asset Caching)**:
  - JS/CSS dosyaları içerik hash'i (content hash: örn. `main.a8f29c.js`) ile üretilmelidir.
  - Statik varlıklar için `Cache-Control: public, max-age=31536000, immutable`, `index.html` için `Cache-Control: no-cache` tanımlanmalıdır.

### B. Dayanıklılık ve Hata Sınırları (Resilience & Error Boundaries)
- [ ] **Global ve Bölgesel Error Boundary**: Bir bileşendeki JavaScript çökmesi tüm sayfayı beyaz ekrana (blank screen) boğmamalı; çöken bileşenin yerine kullanıcı dostu hata mesajı ve "Yeniden Dene" butonu gösterilmelidir.
- [ ] **API Kesinti ve Ağ Fallback'i**: Backend API'sine ulaşılamadığında veya 500 hatası döndüğünde uygulama sonsuz yüklenmede (infinite spinner) takılmamalı, net bir hata durumu (error state) sunmalıdır.

### C. Anti-AI-Slop Standartları ve UI/UX Hijyeni
- [ ] **4-Durumlu Bileşen Mimarisi**: Veri çeken veya etkileşimli her bileşende 4 temel durum eksiksiz uygulanmalıdır:
  1. *Loading*: İçeriğin boyutuna uygun skeleton (asla devasa zıplayan spinner değil).
  2. *Empty*: Veri olmadığında bilgilendirici ve eyleme yönlendiren boş durum (empty state).
  3. *Error*: Hata mesajı ve doğrudan tekrar deneme (retry) aksiyonu.
  4. *Interactive*: Normal, hover, focus-visible ve disabled durumları.
- [ ] **Emoji Yasağı**: Butonlarda, başlıklarda, bildirimlerde veya menü ikonlarında asla Unicode emojiler (🚀, 💡, 🔥, 🤖) kullanılmamalı; tek renkli vektör SVG ikon setleri (Lucide, Heroicons vb.) tercih edilmelidir.
- [ ] **Görsel ve Metin Hijyeni**: Var olmayan statik dosya yolları (`/placeholder.svg`) bulunmamalı, avatar bulunmadığında baş harf (initials) gösterilmeli, gerçekçi içerikler kullanılmalıdır (asla `Lorem Ipsum` yok).
- [ ] **Semantik HTML ve Klavye Erişilebilirliği**: `<div onClick>` kesinlikle yasaktır; yerel `<button>` ve `<a>` etiketleri kullanılmalı, klavye navigasyonunda `:focus-visible` çerçeveleri korunmalıdır.

### D. Performans ve Web Vitals Kontrolü
- [ ] Core Web Vitals eşikleri sağlanmalıdır:
  - LCP (Largest Contentful Paint) < 2.5s
  - CLS (Cumulative Layout Shift) < 0.1
  - INP (Interaction to Next Paint) < 200ms

---

## 2. Çıkış Kriteri (Exit Gate)

Aşağıdaki koşulların **tamamı** sağlanmadan Aşama 04'e geçilemez:
1. `GOLIVE.md` dosyasında Aşama 03 maddelerinin tamamı işaretlenmiş olmalı.
2. Production build komutu yerel veya CI ortamında başarıyla tamamlanmalı ve artifact oluşturulmalı.
3. Ağ bağlantısı simüle olarak kesildiğinde sayfanın beyaz ekrana düşmediği, graceful offline/error ekranı gösterdiği doğrulanmış olmalı.
4. UI chrome ve butonlarda hiçbir Unicode emoji bulunmadığı taranmış olmalı.

---

## 3. Her Maddenin Nedeni (Rationale)

| Madde | Neden Zorunlu? |
|:---|:---|
| Code-Splitting | 5 MB'lık tek bir devasa JS dosyasını mobil cihazlarda indirmek ve parse etmek 10+ saniye sürer ve kullanıcıların sayfayı terk etmesine yol açar. |
| Cache-Control Ayrımı | `index.html` önbelleklenirse, yeni sürüm yayınlandığında kullanıcılar eski JS dosyalarını aramaya devam eder ve 404/MIME uyuşmazlığı hataları patlar. |
| Error Boundary | Tek bir `undefined.map()` hatası yüzünden kullanıcının tüm ekranı kaybetmesini engeller, çöküşü bölgesel tutar. |
| 4-Durumlu Bileşenler | Yükleme ekranı veya boş ekran tasarlanmamış bileşenler, veri geciktiğinde veya sonuç boş geldiğinde arayüzü bozar ve profesyonel olmayan bir izlenim yaratır. |
| Semantik HTML & Focus | Engelli kullanıcıların ekran okuyucularla sistemi kullanabilmesini ve klavye kullanan profesyonel kullanıcıların sisteme erişebilmesini sağlar. |

---

## 4. Sık Yapılan Hatalar (Common Pitfalls)

- ❌ **`index.html`'i Yıllarca Önbelleğe Almak**: Tarayıcının yeni sürümü algılamasını engelleyerek kullanıcıları eski kodda hapsetmek.
- ❌ **Sonsuz Yüklenme Spinner'ı**: API çağrısı `catch` bloğunda `setIsLoading(false)` çağırmayı unutup kullanıcıyı sonsuz dönen çemberde bırakmak.
- ❌ **Yanlış Çevre Değişkeni İfşası**: `NEXT_PUBLIC_` veya `VITE_` önekiyle istemciye gizli API anahtarlarını (private secret) derleme anında gömmek.
- ❌ **Stil Patlaması (Layout Shift - CLS)**: Yüklenen görsellere `width` ve `height` vermeyip görsel yüklendiğinde metinlerin aşağı fırlamasına neden olmak.
