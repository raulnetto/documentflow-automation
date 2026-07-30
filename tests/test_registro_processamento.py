import json
from pathlib import Path

import pytest

from app.services import registro_processamento


def test_cria_registro_json_em_pasta_temporaria(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifica se um processamento é persistido corretamente em JSON."""

    monkeypatch.setattr(
        registro_processamento,
        "PASTA_REGISTROS",
        tmp_path,
    )

    registro = registro_processamento.criar_registro_processamento(
        arquivo_origem="documento_teste.pdf",
        status="sucesso",
        mecanismo="pymupdf",
        arquivo_saida="documento_teste_extraido.txt",
        quantidade_paginas=3,
        quantidade_caracteres=1500,
    )

    caminho_registro = Path(registro["caminho_registro"])

    assert caminho_registro.exists()
    assert caminho_registro.suffix == ".json"

    conteudo = json.loads(
        caminho_registro.read_text(encoding="utf-8")
    )

    assert conteudo["id"] == registro["id"]
    assert conteudo["arquivo_origem"] == "documento_teste.pdf"
    assert conteudo["status"] == "sucesso"
    assert conteudo["mecanismo"] == "pymupdf"
    assert conteudo["arquivo_saida"] == "documento_teste_extraido.txt"
    assert conteudo["quantidade_paginas"] == 3
    assert conteudo["quantidade_caracteres"] == 1500
    assert conteudo["mensagem_erro"] is None
    assert "data_hora" in conteudo