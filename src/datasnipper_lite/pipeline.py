"""
Yüksek seviye çalışma akışı yardımcıları.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

from datasnipper_lite.core.models import Document, MatchResult, Snippet
from datasnipper_lite.importers.excel import load_excel_document
from datasnipper_lite.matching.fuzzy import match_snippets_to_table


@dataclass
class SnippingSession:
    """
    Belge içe aktarma ve eşleştirme sürecini orkestre eden temel sınıf.

    Not:
        `run` metodu MVP implementasyonu kapsamında doldurulacaktır.
    """

    source: Path | str
    table_names: Optional[Sequence[str]] = None

    def run(self, snippets: Sequence[Snippet]) -> Sequence[MatchResult]:
        """
        Eşleştirme akışını tetikler.

        Not:
            Gövde, `task-3` kapsamında tamamlanacaktır.
        """

        document: Document = load_excel_document(self.source, sheets=self.table_names)
        results: list[MatchResult] = []
        for table in document.tables:
            table_results = match_snippets_to_table(snippets, table)
            results.extend(table_results)
        return results
