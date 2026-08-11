import json
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4
from app.repositories.processamento_repository import inserir_processamento


PASTA_REGISTROS = Path("registros")


def criar_registro_processamento(
    *,
    arquivo_origem: str,
    status: str,
    mecanismo: str | None = None,
    arquivo_saida: str | None = None,
    quantidade_paginas: int | None = None,
    quantidade_caracteres: int | None = None,
    mensagem_erro: str | None = None,
    origem: str | None = None,
    id_fluxo: str | None = None,
) -> dict[str, Any]:
    """Cria e persiste um registro estruturado de processamento."""

    identificador = str(uuid4())

    registro: dict[str, Any] = {
        "id": identificador,
        "data_hora": datetime.now().astimezone().isoformat(),
        "arquivo_origem": arquivo_origem,
        "origem": origem,
        "id_fluxo": id_fluxo,
        "status": status,
        "mecanismo": mecanismo,
        "arquivo_saida": arquivo_saida,
        "quantidade_paginas": quantidade_paginas,
        "quantidade_caracteres": quantidade_caracteres,
        "mensagem_erro": mensagem_erro,
    }

    PASTA_REGISTROS.mkdir(
        parents=True,
        exist_ok=True,
    )

    caminho_registro = (
        PASTA_REGISTROS
        / f"{identificador}.json"
    )

    caminho_registro.write_text(
        json.dumps(
            registro,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    inserir_processamento(registro)

    registro["caminho_registro"] = str(caminho_registro)

    return registro