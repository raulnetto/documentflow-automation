from fastapi import FastAPI, File, HTTPException, UploadFile, status

from app.models import (
    DocumentoEntrada,
    DocumentoResposta,
    UploadResposta,
)
from app.services.armazenamento import salvar_upload
from app.services.processador import processar_documento


app = FastAPI(
    title="Automação de Documentos",
    description="API para processamento automatizado de documentos.",
    version="0.2.0",
)


@app.get("/")
def verificar_api() -> dict[str, str]:
    """Confirma que a API está funcionando."""

    return {
        "status": "online",
        "servico": "Automação de Documentos",
        "versao": "0.2.0",
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