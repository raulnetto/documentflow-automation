from pathlib import Path

import pytest

from app import database


@pytest.fixture(autouse=True)
def usar_banco_temporario(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Impede que os testes escrevam no banco local real."""

    # SQLite regression tests must not inherit a caller's PostgreSQL target.
    monkeypatch.delenv("DATABASE_URL", raising=False)

    monkeypatch.setattr(
        database,
        "CAMINHO_BANCO",
        tmp_path / "documentflow_test.db",
    )
