## Vision
`datasnipper-lite` kütüphanesi, farklı kaynaklardan (özellikle Excel ve PDF) gelen tablolu verileri yapılandırılmış biçimde içe aktararak, metin–tablo eşleştirmeleri ve doğrulama akışlarını basitleştirmeyi hedefler. Öncelik, geliştiricilerin ve veri analistlerinin belge içi mutabakat ve kanıt toplama adımlarını otomatikleştirmesine yardımcı olacak yeniden kullanılabilir bir Python paketi sunmaktır.

## Kullanım Senaryoları
- Süreç denetimlerinde Excel/PDF belgelerinden kanıt toplama ve belgeleme.
- Finansal tablolardaki referans metinleri ile e-tablodaki değerleri eşleştirerek doğrulama.
- Kurumsal iş akışlarında belgeler arası tutarlılık kontrollerini otomatikleştirme.

## Mimari Genel Bakış
- **Çekirdek Model (`core`)**  
  - `Document`, `Table`, `Snippet`, `MatchResult` veri sınıfları.  
  - Doğrudan pandas `DataFrame` nesneleriyle uyumlu arabirimler.
- **İçe Aktarıcılar (`importers`)**  
  - `excel.py`: `openpyxl` veya `pandas` tabanlı sheet parser.  
  - `pdf.py`: ilk etapta `pdfplumber` ile tablo çıkarımı için iskelet; MVP’de öncelikli değil.
- **Önişleme (`preprocessing`)**  
  - Metin normalizasyonu, tokenizasyon, sadeleştirme.
- **Eşleştirme (`matching`)**  
  - Basit metin benzerliği (`rapidfuzz`) ile referans–hücre eşleştirme.  
  - İleri aşamada embedding tabanlı arama katmanı.
- **Skorlama ve Açıklama (`scoring`)**  
  - Eşleşmeler için güven skorları, bağlamsal açıklamalar.
- **Çıktı Katmanı (`exporters`)**  
  - Eşleşme sonuçlarını Excel/PDF/JSON’a geri yazmak için yardımcı fonksiyonlar.
- **İstemci Arabirimleri (`interfaces`)**  
  - CLI/Notebook yardımcıları; ilerleyen aşamada web tabanlı veya masaüstü UI.

## Veri Akışı
1. Girdi belgesi (örn. `.xlsx`) `importers` üzerinden okunur ve `Table` koleksiyonuna dönüştürülür.
2. Referans metin listesi veya etiketli hücreler `Snippet` objelerine çevrilir.
3. `matching` katmanı, metin benzerliği kuralları ile en uygun tablo hücrelerini seçer.
4. `scoring`, eşleşmeler için güven puanı hesaplar.
5. `exporters`, sonuçları raporlamak üzere formatlar.

## MVP Kapsamı
- Excel `.xlsx` dosyalarından veri okuma (`pandas` + `openpyxl` bağımlılığı).
- Referans metinleriyle tablo hücrelerini `rapidfuzz` skoru kullanarak eşleştirme.
- Basit bir CLI veya Python API ile sonuçları JSON olarak döndürme.
- Örnek çalışma defteri ve test verileri.

## Yol Haritası
1. **MVP**: Excel içe aktarıcı, metin normalizasyonu, fuzzy matching, JSON çıktısı.  
2. **PDF Entegrasyonu**: `pdfplumber` veya `camelot` ile tablo çıkarımı.  
3. **Gelişmiş Eşleştirme**: Embedding tabanlı arama, konum bilgisini kullanma.  
4. **Kullanıcı Arayüzü**: React/Electron tabanlı görselleştirme, highlight, doğrulama.  
5. **Kurumsal Hazırlık**: Loglama, denetim izi, çoklu belge akışları, gizlilik ayarları.

## Riskler ve Dikkat Noktaları
- Belgeler arası biçim tutarsızlıklarının normalizasyonu.
- PDF tablo çıkarımında düşük doğruluk; manuel düzeltme ihtiyacı.
- Hassas verilerle çalışırken güvenlik ve offline çalışabilme gereksinimleri.
- Büyük dosyalarda performans ve bellek yönetimi.
