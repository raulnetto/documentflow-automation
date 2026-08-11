import sqlite3
from pathlib import Path
from sqlite3 import Connection


CAMINHO_BANCO = Path("dados") / "documentflow.db"


def criar_conexao() -> Connection:
    """Cria uma conexão com o banco SQLite do DocumentFlow."""

    CAMINHO_BANCO.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    return sqlite3.connect(CAMINHO_BANCO)


def inicializar_banco() -> None:
    """Cria a estrutura inicial do banco, caso ainda não exista."""

    with criar_conexao() as conexao:
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS processamentos (
                id TEXT PRIMARY KEY,
                data_hora TEXT NOT NULL,
                arquivo_origem TEXT NOT NULL,
                origem TEXT,
                id_fluxo TEXT,
                status TEXT NOT NULL,
                mecanismo TEXT,
                arquivo_saida TEXT,
                quantidade_paginas INTEGER,
                quantidade_caracteres INTEGER,
                mensagem_erro TEXT
            )
            """
        )