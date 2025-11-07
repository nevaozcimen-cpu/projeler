"""
Temel veri modelleri.

Bu modüller, belge içe aktarma ve eşleştirme katmanları arasında veri taşıma görevini
üstlenen sade veri sınıflarını barındırır.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd


@dataclass(slots=True)
class Table:
    """Excel/PDF gibi kaynaklardan çıkarılan tablolar için iç temsil."""

    name: str
    data: pd.DataFrame
    metadata: Dict[str, Any] = field(default_factory=dict)

    def cell_value(self, row: int, column: int) -> Any:
        """İlgili hücre değerini güvenli şekilde döndürür."""
        return self.data.iat[row, column]


@dataclass(slots=True)
class Snippet:
    """Belge üzerindeki metin parçaları veya referans etiketleri."""

    text: str
    context: Optional[str] = None
    location: Optional[Tuple[int, int]] = None  # sayfa, koordinat
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class MatchCandidate:
    """Bir snippet ile tablo hücresi arasındaki aday eşleşme."""

    table_name: str
    cell_coordinates: Tuple[int, int]
    score: float
    snippet: Snippet
    value: Any
    rank: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class MatchResult:
    """En iyi aday eşleşmeler ve açıklayıcı bilgiler."""

    snippet: Snippet
    best_match: Optional[MatchCandidate]
    candidates: Sequence[MatchCandidate] = ()
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Serileştirilebilir JSON çıktısı üretir."""
        return {
            "snippet": {
                "text": self.snippet.text,
                "context": self.snippet.context,
                "location": self.snippet.location,
                "metadata": self.snippet.metadata,
            },
            "best_match": _candidate_to_dict(self.best_match),
            "candidates": [_candidate_to_dict(candidate) for candidate in self.candidates],
            "created_at": self.created_at.isoformat(),
        }


@dataclass(slots=True)
class Document:
    """Çok tablolı belgeler için üst seviye taşıyıcı."""

    source_path: Optional[str]
    tables: List[Table]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def table(self, name: str) -> Table:
        """Tablo adına göre hızlı erişim sağlar."""
        for table in self.tables:
            if table.name == name:
                return table
        raise KeyError(f"Table '{name}' not found in document.")


def _candidate_to_dict(candidate: Optional[MatchCandidate]) -> Optional[Dict[str, Any]]:
    if candidate is None:
        return None
    return {
        "table_name": candidate.table_name,
        "cell_coordinates": candidate.cell_coordinates,
        "score": candidate.score,
        "value": candidate.value,
        "rank": candidate.rank,
        "metadata": candidate.metadata,
    }
