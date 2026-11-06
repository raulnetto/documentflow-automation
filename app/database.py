import os
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection, Engine

CAMINHO_BANCO = Path("dados") / "documentflow.db"

def obter_database_url() -> str:
    configurada = os.getenv("DATABASE_URL")
    return configurada or f"sqlite:///{CAMINHO_BANCO.as_posix()}"

def criar_engine() -> Engine:
    if not os.getenv("DATABASE_URL"):
        CAMINHO_BANCO.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(obter_database_url(), future=True)

def criar_conexao() -> Connection:
    return criar_engine().connect()

def inicializar_banco() -> None:
    with criar_engine().begin() as conexao:
        conexao.execute(text("""
            CREATE TABLE IF NOT EXISTS processamentos (
                id VARCHAR(255) PRIMARY KEY,
                data_hora VARCHAR(255) NOT NULL,
                arquivo_origem VARCHAR(255) NOT NULL,
                origem VARCHAR(255), id_fluxo VARCHAR(255),
                status VARCHAR(50) NOT NULL, mecanismo VARCHAR(100),
                arquivo_saida VARCHAR(255), quantidade_paginas INTEGER,
                quantidade_caracteres INTEGER, mensagem_erro TEXT
            )
        """))
