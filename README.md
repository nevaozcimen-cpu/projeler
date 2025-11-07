# datasnipper-lite

Geliştiricilerin DataSnipper benzeri belge mutabakat akışlarını otomatikleştirebilmesi için hazırlanan hafif Python kütüphanesi. Excel ve PDF belgelerindeki tablolu verileri içe aktarır, metin parçalarını hücrelerle eşleştirir ve sonuçları raporlanabilir hale getirir.

## Özellikler (MVP)
- Excel `.xlsx` dosyalarından veri içe aktarma
- Metin normalizasyonu ve benzerlik skorlaması
- JSON formatında eşleştirme sonuçları

## Hızlı Başlangıç
```python
from datasnipper_lite.core import Snippet
from datasnipper_lite.pipeline import SnippingSession

session = SnippingSession("examples/trial_balance.xlsx")
snippets = [
    Snippet(text="Cash balance"),
    Snippet(text="Accounts payable"),
]

results = session.run(snippets)

for result in results:
    if result.best_match:
        print(result.snippet.text, "->", result.best_match.value, result.best_match.score)
```

`SnippingSession`, Excel dosyasını otomatik olarak yükler ve her snippet için en iyi hücre eşleşmesini arar. `MatchResult.to_dict()` metodunu kullanarak sonuçları JSON formatına dönüştürebilirsiniz.

## Testler
```bash
python3 -m pytest
```

## Yol Haritası
- PDF tablo çıkarımı için destek
- Embedding tabanlı gelişmiş eşleştirme
- Web/massaüstü kullanıcı arayüzü

## Bir Sonraki Adımlar
- PDF içe aktarıcı prototipleri
- Eşleştirme sonuçları için güven skoruna göre filtreleme
- Snippet–tablo eşleşmelerini görselleştirmek için örnek Jupyter defteri

## Kurulum
```bash
pip install .
```

Geliştirici ortamını kurmak için:
```bash
pip install .[dev]
```

## Katkı
1. Depoyu forklayın / klonlayın.
2. Özellik/fix branşında çalışın.
3. Testleri (`pytest`) çalıştırın.
4. Pull request gönderin.
