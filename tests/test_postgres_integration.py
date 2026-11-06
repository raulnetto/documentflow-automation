import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import make_url

from app import database
from app.repositories import processamento_repository as repository
from app.main import app


pytestmark = pytest.mark.skipif(
    not os.getenv("DF011_TEST_DATABASE_URL"),
    reason="DF011_TEST_DATABASE_URL must point to an isolated PostgreSQL test database",
)


def test_postgres_repository_roundtrip(monkeypatch):
    database_url = os.environ["DF011_TEST_DATABASE_URL"]
    parsed_url = make_url(database_url)
    if parsed_url.drivername != "postgresql+psycopg":
        pytest.fail("DF011_TEST_DATABASE_URL must use the postgresql+psycopg driver")
    if parsed_url.host not in {"localhost", "127.0.0.1", "::1"}:
        pytest.fail("PostgreSQL integration is restricted to a local test server")
    if "test" not in (parsed_url.database or "").lower():
        pytest.fail("PostgreSQL integration database name must contain 'test'")

    monkeypatch.setenv("DATABASE_URL", database_url)
    database.inicializar_banco()
    registro = {
        "id": str(uuid4()),
        "data_hora": "2026-11-05T00:00:00+00:00",
        "arquivo_origem": "integration.pdf",
        "origem": "pytest",
        "id_fluxo": "df011",
        "status": "sucesso",
        "mecanismo": "pymupdf",
        "arquivo_saida": "integration.txt",
        "quantidade_paginas": 1,
        "quantidade_caracteres": 12,
        "mensagem_erro": None,
    }
    inserido = False
    try:
        repository.inserir_processamento(registro)
        inserido = True
        assert repository.buscar_processamento_por_id(registro["id"])["id"] == registro["id"]
        assert any(item["id"] == registro["id"] for item in repository.listar_processamentos())
        assert repository.obter_resumo_processamentos()["total"] >= 1
        resposta = TestClient(app).get("/processamentos")
        assert resposta.status_code == 200
        assert any(item["id"] == registro["id"] for item in resposta.json())
    finally:
        if inserido:
            from sqlalchemy import text

            with database.criar_conexao() as conexao:
                with conexao.begin():
                    conexao.execute(
                        text("DELETE FROM processamentos WHERE id = :id"),
                        {"id": registro["id"]},
                    )
