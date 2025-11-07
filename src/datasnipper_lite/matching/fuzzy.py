"""
Fuzzy metin eşleştirme yardımcıları.

`rapidfuzz` kullanarak snippet metinlerini tablo hücreleriyle skorlamak için fonksiyonlar sağlar.
"""

from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

import pandas as pd
from rapidfuzz import fuzz, process

from datasnipper_lite.core.models import MatchCandidate, MatchResult, Snippet, Table
from datasnipper_lite.preprocessing import normalize_text


def match_snippets_to_table(
    snippets: Sequence[Snippet],
    table: Table,
    *,
    limit: int = 5,
) -> List[MatchResult]:
    """
    Snippet koleksiyonunu tek bir tabloya fuzzy matching ile bağlar.

    Args:
        snippets: Eşleştirilecek snippet koleksiyonu.
        table: Hedef tablo.
        limit: Her snippet için döndürülecek en fazla aday sayısı.
    """

    if table.data.empty:
        return [MatchResult(snippet=snippet, best_match=None, candidates=()) for snippet in snippets]

    choices, payloads = _prepare_table_choices(table)
    if not choices:
        return [MatchResult(snippet=snippet, best_match=None, candidates=()) for snippet in snippets]

    results: List[MatchResult] = []
    for snippet in snippets:
        normalized_snippet = normalize_text(snippet.text)
        if not normalized_snippet:
            results.append(MatchResult(snippet=snippet, best_match=None, candidates=()))
            continue

        matches = process.extract(
            normalized_snippet,
            choices,
            scorer=fuzz.WRatio,
            limit=limit,
            processor=None,
        )

        candidates: List[MatchCandidate] = []
        for rank, match in enumerate(matches, start=1):
            _, score, index = match
            payload = payloads[index]
            candidate = MatchCandidate(
                table_name=table.name,
                cell_coordinates=payload["coordinates"],
                score=score / 100.0,
                snippet=snippet,
                value=payload["value"],
                rank=rank,
                metadata={
                    "column_name": payload["column_name"],
                    "row_index": payload["row_index"],
                    "normalized_value": payload["normalized"],
                },
            )
            candidates.append(candidate)

        best_match = candidates[0] if candidates else None
        results.append(
            MatchResult(snippet=snippet, best_match=best_match, candidates=tuple(candidates))
        )

    return results


def _prepare_table_choices(table: Table) -> Tuple[List[str], List[Dict[str, object]]]:
    """
    RapidFuzz için tablo hücrelerini normalize eder ve payload bilgilerini hazırlar.

    Returns:
        choices: Normalize edilmiş hücre metinleri listesi.
        payloads: Her hücre için koordinat ve ham değer bilgileri.
    """

    choices: List[str] = []
    payloads: List[Dict[str, object]] = []
    column_names = list(table.data.columns)
    values = table.data.to_numpy()

    for row_pos in range(values.shape[0]):
        for col_pos in range(values.shape[1]):
            raw_value = values[row_pos, col_pos]
            if pd.isna(raw_value):
                continue
            text_value = str(raw_value)
            normalized_value = normalize_text(text_value)
            if not normalized_value:
                continue
            choices.append(normalized_value)
            payloads.append(
                {
                    "coordinates": (row_pos, col_pos),
                    "row_index": table.data.index[row_pos],
                    "column_name": str(column_names[col_pos]),
                    "value": raw_value,
                    "normalized": normalized_value,
                }
            )

    return choices, payloads
