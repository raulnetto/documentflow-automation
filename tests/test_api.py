from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app import main as main_module
from app.main import app


client = TestClient(app)


def test_rota_raiz_retorna_servico_disponivel() -> None:
    """Verifica se a rota principal responde e apresenta os dados básicos."""

    resposta = client.get("/")

    assert resposta.status_code == 200

    corpo = resposta.json()

    assert "status" in corpo
    assert "servico" in corpo
    assert corpo["versao"] == "0.7.0"


def test_processamento_automatico_retorna_sucesso(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifica a resposta de sucesso da rota automática."""

    caminho_txt = Path("output/documento_extraido.txt")

    def processar_falso(
        caminho_arquivo: Path,
    ) -> tuple[Path, int, int, str]:
        assert caminho_arquivo == Path("input/documento.pdf")

        return (
            caminho_txt,
            3,
            1500,
            "pymupdf",
        )

    def criar_registro_falso(
        **dados: Any,
    ) -> dict[str, str]:
        assert dados["arquivo_origem"] == "documento.pdf"
        assert dados["status"] == "sucesso"
        assert dados["mecanismo"] == "pymupdf"

        return {
            "id": "registro-teste-123",
            "caminho_registro": (
                "registros/registro-teste-123.json"
            ),
        }

    monkeypatch.setattr(
        main_module,
        "processar_automaticamente",
        processar_falso,
    )

    monkeypatch.setattr(
        main_module,
        "criar_registro_processamento",
        criar_registro_falso,
    )

    resposta = client.post(
        "/documentos/documento.pdf/processar-automaticamente"
    )

    assert resposta.status_code == 200, resposta.json()

    corpo = resposta.json()

    assert corpo["status"] == "processamento_concluido"
    assert corpo["arquivo_origem"] == "documento.pdf"
    assert corpo["arquivo_texto"] == "documento_extraido.txt"
    assert corpo["quantidade_paginas"] == 3
    assert corpo["quantidade_caracteres"] == 1500
    assert corpo["mecanismo"] == "pymupdf"
    assert corpo["id_registro"] == "registro-teste-123"


def test_processamento_automatico_retorna_404(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifica a resposta quando o arquivo não existe."""

    registro_criado: dict[str, Any] = {}

    def processar_arquivo_inexistente(
        caminho_arquivo: Path,
    ) -> tuple[Path, int, int, str]:
        raise FileNotFoundError(
            f"O arquivo '{caminho_arquivo}' não foi encontrado."
        )

    def criar_registro_falso(
        **dados: Any,
    ) -> dict[str, str]:
        registro_criado.update(dados)

        return {
            "id": "registro-erro-404",
            "caminho_registro": (
                "registros/registro-erro-404.json"
            ),
        }

    monkeypatch.setattr(
        main_module,
        "processar_automaticamente",
        processar_arquivo_inexistente,
    )

    monkeypatch.setattr(
        main_module,
        "criar_registro_processamento",
        criar_registro_falso,
    )

    resposta = client.post(
        "/documentos/arquivo_inexistente.pdf/"
        "processar-automaticamente"
    )

    assert resposta.status_code == 404
    assert "não foi encontrado" in resposta.json()["detail"]

    assert registro_criado["arquivo_origem"] == (
        "arquivo_inexistente.pdf"
    )
    assert registro_criado["status"] == "erro"
    assert "não foi encontrado" in str(
        registro_criado["mensagem_erro"]
    )


def test_processamento_automatico_retorna_400(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifica a resposta quando o processamento gera ValueError."""

    registro_criado: dict[str, Any] = {}

    def processar_conteudo_invalido(
        caminho_arquivo: Path,
    ) -> tuple[Path, int, int, str]:
        raise ValueError(
            f"O arquivo '{caminho_arquivo.name}' "
            "não possui texto reconhecível."
        )

    def criar_registro_falso(
        **dados: Any,
    ) -> dict[str, str]:
        registro_criado.update(dados)

        return {
            "id": "registro-erro-400",
            "caminho_registro": (
                "registros/registro-erro-400.json"
            ),
        }

    monkeypatch.setattr(
        main_module,
        "processar_automaticamente",
        processar_conteudo_invalido,
    )

    monkeypatch.setattr(
        main_module,
        "criar_registro_processamento",
        criar_registro_falso,
    )

    resposta = client.post(
        "/documentos/imagem_sem_texto.jpg/"
        "processar-automaticamente"
    )

    assert resposta.status_code == 400
    assert "não possui texto reconhecível" in (
        resposta.json()["detail"]
    )

    assert registro_criado["arquivo_origem"] == (
        "imagem_sem_texto.jpg"
    )
    assert registro_criado["status"] == "erro"
    assert "não possui texto reconhecível" in str(
        registro_criado["mensagem_erro"]
    )
def test_processamento_automatico_retorna_503(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifica a resposta quando o mecanismo externo fica indisponível."""

    registro_criado: dict[str, Any] = {}

    def processar_com_servico_indisponivel(
        caminho_arquivo: Path,
    ) -> tuple[Path, int, int, str]:
        raise RuntimeError(
            f"O Tesseract não está disponível para "
            f"processar '{caminho_arquivo.name}'."
        )

    def criar_registro_falso(
        **dados: Any,
    ) -> dict[str, str]:
        registro_criado.update(dados)

        return {
            "id": "registro-erro-503",
            "caminho_registro": (
                "registros/registro-erro-503.json"
            ),
        }

    monkeypatch.setattr(
        main_module,
        "processar_automaticamente",
        processar_com_servico_indisponivel,
    )

    monkeypatch.setattr(
        main_module,
        "criar_registro_processamento",
        criar_registro_falso,
    )

    resposta = client.post(
        "/documentos/documento_escaneado.pdf/"
        "processar-automaticamente"
    )

    assert resposta.status_code == 503
    assert "Tesseract não está disponível" in (
        resposta.json()["detail"]
    )

    assert registro_criado["arquivo_origem"] == (
        "documento_escaneado.pdf"
    )
    assert registro_criado["status"] == "erro"
    assert registro_criado["mecanismo"] == "tesseract"
    assert "Tesseract não está disponível" in str(
        registro_criado["mensagem_erro"]
    )