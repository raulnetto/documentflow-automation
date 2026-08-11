import sqlite3
from typing import Any

from app.database import criar_conexao, inicializar_banco


def inserir_processamento(
    registro: dict[str, Any],
) -> None:
    """Persiste um registro de processamento no banco SQLite."""

    inicializar_banco()

    with criar_conexao() as conexao:
        conexao.execute(
            """
            INSERT INTO processamentos (
                id,
                data_hora,
                arquivo_origem,
                origem,
                id_fluxo,
                status,
                mecanismo,
                arquivo_saida,
                quantidade_paginas,
                quantidade_caracteres,
                mensagem_erro
            )
            VALUES (
                :id,
                :data_hora,
                :arquivo_origem,
                :origem,
                :id_fluxo,
                :status,
                :mecanismo,
                :arquivo_saida,
                :quantidade_paginas,
                :quantidade_caracteres,
                :mensagem_erro
            )
            """,
            registro,
        )


def listar_processamentos() -> list[dict[str, Any]]:
    """Retorna todos os processamentos registrados no banco."""

    inicializar_banco()

    with criar_conexao() as conexao:
        conexao.row_factory = sqlite3.Row

        linhas = conexao.execute(
            """
            SELECT
                id,
                data_hora,
                arquivo_origem,
                origem,
                id_fluxo,
                status,
                mecanismo,
                arquivo_saida,
                quantidade_paginas,
                quantidade_caracteres,
                mensagem_erro
            FROM processamentos
            ORDER BY data_hora DESC
            """
        ).fetchall()

    return [dict(linha) for linha in linhas]


def buscar_processamento_por_id(
    identificador: str,
) -> dict[str, Any] | None:
    """Retorna um processamento específico pelo identificador."""

    inicializar_banco()

    with criar_conexao() as conexao:
        conexao.row_factory = sqlite3.Row

        linha = conexao.execute(
            """
            SELECT
                id,
                data_hora,
                arquivo_origem,
                origem,
                id_fluxo,
                status,
                mecanismo,
                arquivo_saida,
                quantidade_paginas,
                quantidade_caracteres,
                mensagem_erro
            FROM processamentos
            WHERE id = ?
            """,
            (identificador,),
        ).fetchone()

    if linha is None:
        return None

    return dict(linha)

def obter_resumo_processamentos() -> dict[str, Any]:
    """Retorna estatísticas agregadas dos processamentos."""

    inicializar_banco()

    with criar_conexao() as conexao:
        total = conexao.execute(
            """
            SELECT COUNT(*)
            FROM processamentos
            """
        ).fetchone()[0]

        sucessos = conexao.execute(
            """
            SELECT COUNT(*)
            FROM processamentos
            WHERE status = ?
            """,
            ("sucesso",),
        ).fetchone()[0]

        erros = conexao.execute(
            """
            SELECT COUNT(*)
            FROM processamentos
            WHERE status = ?
            """,
            ("erro",),
        ).fetchone()[0]

        mecanismos = conexao.execute(
            """
            SELECT mecanismo, COUNT(*)
            FROM processamentos
            WHERE mecanismo IS NOT NULL
            GROUP BY mecanismo
            """
        ).fetchall()

    return {
        "total": total,
        "sucessos": sucessos,
        "erros": erros,
        "por_mecanismo": {
            mecanismo: quantidade
            for mecanismo, quantidade in mecanismos
        },
    }