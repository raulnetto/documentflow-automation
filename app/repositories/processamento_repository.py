from typing import Any

from sqlalchemy import text

from app.database import criar_conexao, inicializar_banco

_COLUNAS = "id, data_hora, arquivo_origem, origem, id_fluxo, status, mecanismo, arquivo_saida, quantidade_paginas, quantidade_caracteres, mensagem_erro"

def inserir_processamento(registro: dict[str, Any]) -> None:
    inicializar_banco()
    with criar_conexao() as conexao:
        with conexao.begin():
            conexao.execute(text("""
                INSERT INTO processamentos (
                    id, data_hora, arquivo_origem, origem, id_fluxo, status,
                    mecanismo, arquivo_saida, quantidade_paginas,
                    quantidade_caracteres, mensagem_erro
                ) VALUES (
                    :id, :data_hora, :arquivo_origem, :origem, :id_fluxo,
                    :status, :mecanismo, :arquivo_saida, :quantidade_paginas,
                    :quantidade_caracteres, :mensagem_erro
                )
            """), registro)

def listar_processamentos() -> list[dict[str, Any]]:
    inicializar_banco()
    with criar_conexao() as conexao:
        linhas = conexao.execute(text(f"SELECT {_COLUNAS} FROM processamentos ORDER BY data_hora DESC")).mappings().all()
    return [dict(linha) for linha in linhas]

def buscar_processamento_por_id(identificador: str) -> dict[str, Any] | None:
    inicializar_banco()
    with criar_conexao() as conexao:
        linha = conexao.execute(text(f"SELECT {_COLUNAS} FROM processamentos WHERE id = :id"), {"id": identificador}).mappings().first()
    return dict(linha) if linha is not None else None

def obter_resumo_processamentos() -> dict[str, Any]:
    inicializar_banco()
    with criar_conexao() as conexao:
        total = conexao.execute(text("SELECT COUNT(*) FROM processamentos")).scalar_one()
        sucessos = conexao.execute(text("SELECT COUNT(*) FROM processamentos WHERE status = :status"), {"status": "sucesso"}).scalar_one()
        erros = conexao.execute(text("SELECT COUNT(*) FROM processamentos WHERE status = :status"), {"status": "erro"}).scalar_one()
        mecanismos = conexao.execute(text("SELECT mecanismo, COUNT(*) AS quantidade FROM processamentos WHERE mecanismo IS NOT NULL GROUP BY mecanismo")).all()
    return {"total": total, "sucessos": sucessos, "erros": erros, "por_mecanismo": {mecanismo: quantidade for mecanismo, quantidade in mecanismos}}
