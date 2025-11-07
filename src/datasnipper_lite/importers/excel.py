"""
Excel içe aktarma yardımcıları.

Bu modül, `pandas` ve `openpyxl` kombinasyonuyla Excel dosyalarını `Table` ve `Document`
modellerine dönüştürecek yardımcı fonksiyonları barındırır.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Optional, Sequence

import pandas as pd

from datasnipper_lite.core.models import Document, Table


def load_excel_document(
    source: Path | str,
    *,
    sheets: Optional[Sequence[str]] = None,
    use_header: bool = True,
    sheet_name_prefix: str = "",
) -> Document:
    """
    Excel dosyasından `Document` nesnesi üretir.

    Args:
        source: Excel dosyası yolu.
        sheets: Okunacak sayfa isimleri. `None` ise tüm sayfalar okunur.
        use_header: `True` ise ilk satır sütun başlığı olarak yorumlanır.
        sheet_name_prefix: Oluşturulan tablo isimlerine uygulanacak önek.
    """

    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"Excel dosyası bulunamadı: {path}")

    sheet_request = _normalize_sheet_request(sheets)
    header = 0 if use_header else None

    frames = pd.read_excel(
        path,
        sheet_name=sheet_request,
        header=header,
        engine="openpyxl",
    )

    frame_map = _ensure_dict(frames, sheet_request)

    tables = []
    for position, (sheet_name, frame) in enumerate(frame_map.items()):
        normalized_frame = _normalize_frame(frame, use_header=use_header)
        table_name = f"{sheet_name_prefix}{sheet_name}"
        tables.append(
            Table(
                name=table_name,
                data=normalized_frame,
                metadata={
                    "source_path": str(path),
                    "sheet_name": sheet_name,
                    "sheet_position": position,
                },
            )
        )

    return Document(
        source_path=str(path),
        tables=tables,
        metadata={
            "sheet_names": [table.metadata["sheet_name"] for table in tables],
            "sheet_count": len(tables),
        },
    )


def _normalize_sheet_request(sheets: Optional[Sequence[str]]) -> Optional[Iterable[str] | str]:
    if sheets is None:
        return None
    sheets_list = list(sheets)
    if not sheets_list:
        return None
    if len(sheets_list) == 1:
        return sheets_list[0]
    return sheets_list


def _ensure_dict(
    frames: pd.DataFrame | Dict[str, pd.DataFrame],
    sheet_request: Optional[Iterable[str] | str],
) -> Dict[str, pd.DataFrame]:
    if isinstance(frames, pd.DataFrame):
        if isinstance(sheet_request, str):
            key = sheet_request
        elif isinstance(sheet_request, Iterable) and sheet_request:
            key = list(sheet_request)[0]
        else:
            key = "Sheet1"
        return {key: frames}
    return dict(frames)


def _normalize_frame(frame: pd.DataFrame, *, use_header: bool) -> pd.DataFrame:
    """Sütun etiketlerini dizgeye çevirip kopya döndürür."""

    normalized = frame.copy()
    if not use_header:
        normalized.columns = [f"column_{idx}" for idx in range(len(normalized.columns))]
        return normalized

    if isinstance(normalized.columns, pd.MultiIndex):
        normalized.columns = [
            " / ".join(str(level) for level in column if str(level) != "nan") or f"column_{position}"
            for position, column in enumerate(normalized.columns)
        ]
    else:
        normalized.columns = [
            str(column) if str(column).strip() else f"column_{idx}"
            for idx, column in enumerate(normalized.columns)
        ]

    return normalized
