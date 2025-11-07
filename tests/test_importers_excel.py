from pathlib import Path

import pandas as pd
import pytest

from datasnipper_lite.importers import load_excel_document


def test_load_excel_document_reads_single_sheet(tmp_path: Path) -> None:
    df = pd.DataFrame({"Account": ["Cash", "Revenue"], "Amount": [1250, 980]})
    file_path = tmp_path / "sample.xlsx"
    df.to_excel(file_path, index=False)

    document = load_excel_document(file_path)

    assert document.source_path == str(file_path)
    assert len(document.tables) == 1
    table = document.tables[0]
    assert table.name == "Sheet1"
    assert list(table.data.columns) == ["Account", "Amount"]
    assert table.data.iloc[0, 0] == "Cash"


def test_load_excel_document_supports_sheet_subset(tmp_path: Path) -> None:
    file_path = tmp_path / "multi.xlsx"
    with pd.ExcelWriter(file_path) as writer:
        pd.DataFrame({"A": [1, 2]}).to_excel(writer, sheet_name="SheetA", index=False)
        pd.DataFrame({"B": [3, 4]}).to_excel(writer, sheet_name="SheetB", index=False)

    document = load_excel_document(file_path, sheets=["SheetB"], sheet_name_prefix="pref__")

    assert len(document.tables) == 1
    assert document.tables[0].name == "pref__SheetB"
    assert list(document.metadata["sheet_names"]) == ["SheetB"]


def test_load_excel_document_no_header(tmp_path: Path) -> None:
    df = pd.DataFrame(
        [
            ["Header", "Value"],
            ["Row1", 10],
            ["Row2", 20],
        ]
    )
    file_path = tmp_path / "no_header.xlsx"
    df.to_excel(file_path, index=False, header=False)

    document = load_excel_document(file_path, use_header=False)

    assert list(document.tables[0].data.columns) == ["column_0", "column_1"]
    assert document.tables[0].data.iloc[0, 0] == "Header"


def test_load_excel_document_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_excel_document(tmp_path / "missing.xlsx")
