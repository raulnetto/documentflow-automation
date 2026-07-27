from fastapi import FastAPI, HTTPException, status

from app.models import DocumentoEntrada, DocumentoResposta
from app.services.processador import processar_documento


app = FastAPI(
    title="Automação de Documentos",
    description="API para processamento automatizado de documentos.",
    version="0.1.0",
)


@app.get("/")
def verificar_api() -> dict[str, str]:
    """Confirma que a API está funcionando."""

    return {
        "status": "online",
        "servico": "Automação de Documentos",
        "versao": "0.1.0",
    }


@app.post(
    "/documentos/processar",
    response_model=DocumentoResposta,
    status_code=status.HTTP_202_ACCEPTED,
)
def receber_documento(documento: DocumentoEntrada) -> DocumentoResposta:
    """Recebe e valida os metadados de um documento."""

    try:
        return processar_documento(documento)

    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro),
        ) from erro