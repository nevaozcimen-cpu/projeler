import pandas as pd

from datasnipper_lite.core import Snippet, Table
from datasnipper_lite.matching import match_snippets_to_table


def test_match_snippets_returns_best_candidate() -> None:
    table = Table(
        name="ledger",
        data=pd.DataFrame(
            {
                "Account": ["Cash", "Accounts Payable", "Revenue"],
                "Amount": [1250, -800, 2150],
            }
        ),
    )
    snippet = Snippet(text="cash balance")

    results = match_snippets_to_table([snippet], table)

    assert len(results) == 1
    best = results[0].best_match
    assert best is not None
    assert best.metadata["column_name"] == "Account"
    assert best.value == "Cash"
    assert 0.9 <= best.score <= 1.0


def test_match_snippets_handles_empty_snippet() -> None:
    table = Table(
        name="ledger",
        data=pd.DataFrame({"Account": ["Cash"], "Amount": [100]}),
    )
    snippet = Snippet(text="")

    result = match_snippets_to_table([snippet], table)[0]

    assert result.best_match is None
    assert result.candidates == ()
