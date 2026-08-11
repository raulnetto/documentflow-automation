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
    assert corpo["versao"] == "0.10.0"


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
def test_webhook_processa_documento_com_sucesso(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifica o processamento iniciado por uma automação externa."""

    caminho_txt = Path("output/documento_extraido.txt")
    registro_criado: dict[str, Any] = {}

    def processar_falso(
        caminho_arquivo: Path,
    ) -> tuple[Path, int, int, str]:
        assert caminho_arquivo == Path("input/documento.pdf")

        return (
            caminho_txt,
            4,
            2000,
            "pymupdf",
        )

    def criar_registro_falso(
        **dados: Any,
    ) -> dict[str, str]:
        registro_criado.update(dados)

        return {
            "id": "registro-webhook-001",
            "caminho_registro": (
                "registros/registro-webhook-001.json"
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
        "/webhooks/processar-documento",
        json={
            "nome_arquivo": "documento.pdf",
            "origem": "n8n",
            "id_fluxo": "workflow-001",
        },
    )

    assert resposta.status_code == 200

    corpo = resposta.json()

    assert corpo["status"] == "processamento_concluido"
    assert corpo["origem"] == "n8n"
    assert corpo["id_fluxo"] == "workflow-001"
    assert corpo["arquivo_origem"] == "documento.pdf"
    assert corpo["mecanismo"] == "pymupdf"
    assert corpo["id_registro"] == "registro-webhook-001"

    assert registro_criado["origem"] == "n8n"
    assert registro_criado["id_fluxo"] == "workflow-001"
    assert registro_criado["status"] == "sucesso"

def test_webhook_retorna_404_e_registra_origem(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifica o webhook quando o arquivo solicitado não existe."""

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
            "id": "registro-webhook-404",
            "caminho_registro": (
                "registros/registro-webhook-404.json"
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
        "/webhooks/processar-documento",
        json={
            "nome_arquivo": "arquivo_inexistente.pdf",
            "origem": "n8n",
            "id_fluxo": "workflow-erro-001",
        },
    )

    assert resposta.status_code == 404
    assert "não foi encontrado" in resposta.json()["detail"]

    assert registro_criado["arquivo_origem"] == (
        "arquivo_inexistente.pdf"
    )
    assert registro_criado["origem"] == "n8n"
    assert registro_criado["id_fluxo"] == "workflow-erro-001"
    assert registro_criado["status"] == "erro"

def test_webhook_retorna_400_e_registra_origem(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifica o webhook quando o documento não possui conteúdo válido."""

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
            "id": "registro-webhook-400",
            "caminho_registro": (
                "registros/registro-webhook-400.json"
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
        "/webhooks/processar-documento",
        json={
            "nome_arquivo": "imagem_sem_texto.jpg",
            "origem": "n8n",
            "id_fluxo": "workflow-erro-400",
        },
    )

    assert resposta.status_code == 400
    assert "não possui texto reconhecível" in (
        resposta.json()["detail"]
    )

    assert registro_criado["arquivo_origem"] == (
        "imagem_sem_texto.jpg"
    )
    assert registro_criado["origem"] == "n8n"
    assert registro_criado["id_fluxo"] == "workflow-erro-400"
    assert registro_criado["status"] == "erro"

def test_webhook_retorna_503_e_registra_origem(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifica o webhook quando o mecanismo externo fica indisponível."""

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
            "id": "registro-webhook-503",
            "caminho_registro": (
                "registros/registro-webhook-503.json"
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
        "/webhooks/processar-documento",
        json={
            "nome_arquivo": "documento_escaneado.pdf",
            "origem": "n8n",
            "id_fluxo": "workflow-erro-503",
        },
    )

    assert resposta.status_code == 503
    assert "Tesseract não está disponível" in (
        resposta.json()["detail"]
    )

    assert registro_criado["arquivo_origem"] == (
        "documento_escaneado.pdf"
    )
    assert registro_criado["origem"] == "n8n"
    assert registro_criado["id_fluxo"] == "workflow-erro-503"
    assert registro_criado["status"] == "erro"
    assert registro_criado["mecanismo"] == "tesseract"

def test_lista_historico_processamentos(
    monkeypatch,
) -> None:
    """Verifica se a API retorna o histórico de processamentos."""

    historico = [
        {
            "id": "processamento-001",
            "data_hora": "2026-08-10T23:30:00-03:00",
            "arquivo_origem": "documento.pdf",
            "origem": "n8n",
            "id_fluxo": "workflow-001",
            "status": "sucesso",
            "mecanismo": "pymupdf",
            "arquivo_saida": "documento.txt",
            "quantidade_paginas": 2,
            "quantidade_caracteres": 500,
            "mensagem_erro": None,
        }
    ]

    monkeypatch.setattr(
        "app.main.obter_historico_processamentos",
        lambda: historico,
    )

    resposta = client.get("/processamentos")

    assert resposta.status_code == 200
    assert resposta.json() == historico


def test_consulta_processamento_por_id(
    monkeypatch,
) -> None:
    """Verifica se a API retorna um processamento específico."""

    processamento = {
        "id": "processamento-001",
        "data_hora": "2026-08-10T23:30:00-03:00",
        "arquivo_origem": "documento.pdf",
        "origem": None,
        "id_fluxo": None,
        "status": "sucesso",
        "mecanismo": "pymupdf",
        "arquivo_saida": "documento.txt",
        "quantidade_paginas": 2,
        "quantidade_caracteres": 500,
        "mensagem_erro": None,
    }

    monkeypatch.setattr(
        "app.main.obter_processamento_por_id",
        lambda identificador: processamento,
    )

    resposta = client.get("/processamentos/processamento-001")

    assert resposta.status_code == 200
    assert resposta.json() == processamento


def test_consulta_processamento_inexistente_retorna_404(
    monkeypatch,
) -> None:
    """Verifica o retorno 404 para processamento inexistente."""

    monkeypatch.setattr(
        "app.main.obter_processamento_por_id",
        lambda identificador: None,
    )

    resposta = client.get("/processamentos/id-que-nao-existe")

    assert resposta.status_code == 404
    assert resposta.json() == {
        "detail": "Processamento não encontrado."
    }

def test_resumo_processamentos(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifica se a API retorna o resumo dos processamentos."""

    resumo = {
        "total": 3,
        "sucessos": 2,
        "erros": 1,
        "por_mecanismo": {
            "pymupdf": 1,
            "tesseract": 1,
        },
    }

    monkeypatch.setattr(
        main_module,
        "obter_resumo_historico",
        lambda: resumo,
    )

    resposta = client.get("/processamentos/resumo")

    assert resposta.status_code == 200
    assert resposta.json() == resumo