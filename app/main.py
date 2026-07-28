from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile, status

from app.models import (
    DocumentoEntrada,
    DocumentoResposta,
    ExtracaoResposta,
    UploadResposta,
)
from app.services.armazenamento import salvar_upload
from app.services.extrator_pdf import extrair_texto_pdf
from app.services.processador import processar_documento


app = FastAPI(
    title="Automação de Documentos",
    description="API para processamento automatizado de documentos.",
    version="0.3.0",
)


@app.get("/")
def verificar_api() -> dict[str, str]:
    """Confirma que a API está funcionando."""

    return {
        "status": "online",
        "servico": "Automação de Documentos",
        "versao": "0.3.0",
    }


@app.post(
    "/documentos/processar",
    response_model=DocumentoResposta,
    status_code=status.HTTP_202_ACCEPTED,
)
def receber_documento(
    documento: DocumentoEntrada,
) -> DocumentoResposta:
    """Recebe e valida os metadados de um documento."""

    try:
        return processar_documento(documento)

    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro),
        ) from erro


@app.post(
    "/documentos/upload",
    response_model=UploadResposta,
    status_code=status.HTTP_201_CREATED,
)
def receber_upload(
    arquivo: UploadFile = File(...),
) -> UploadResposta:
    """Recebe, valida e armazena um documento real."""

    try:
        caminho_salvo, tamanho_bytes = salvar_upload(arquivo)

        return UploadResposta(
            status="armazenado",
            arquivo=caminho_salvo.name,
            tipo_conteudo=arquivo.content_type or "desconhecido",
            tamanho_bytes=tamanho_bytes,
            caminho_salvo=str(caminho_salvo),
            proxima_etapa="extracao_ocr",
        )

    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro),
        ) from erro

    finally:
        arquivo.file.close()

@app.post(
    "/documentos/{nome_arquivo}/extrair-texto",
    response_model=ExtracaoResposta,
    status_code=status.HTTP_200_OK,
)
def extrair_texto_documento(
    nome_arquivo: str,
) -> ExtracaoResposta:
    """Extrai texto de um PDF previamente armazenado em input/."""

    caminho_pdf = Path("input") / Path(nome_arquivo).name

    try:
        caminho_txt, paginas, caracteres = extrair_texto_pdf(
            caminho_pdf
        )

        return ExtracaoResposta(
            status="texto_extraido",
            arquivo_origem=caminho_pdf.name,
            arquivo_texto=caminho_txt.name,
            quantidade_paginas=paginas,
            quantidade_caracteres=caracteres,
            caminho_salvo=str(caminho_txt),
        )

    except FileNotFoundError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro),
        ) from erro

    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro),
        ) from erro