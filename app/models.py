from pydantic import BaseModel, Field


class DocumentoEntrada(BaseModel):
    """Dados recebidos pela API para iniciar o processamento."""

    nome_arquivo: str = Field(
        min_length=3,
        description="Nome do arquivo, incluindo a extensão.",
        examples=["contrato_cliente.pdf"],
    )

    tipo_documento: str = Field(
        min_length=2,
        description="Categoria do documento.",
        examples=["contrato"],
    )


class DocumentoResposta(BaseModel):
    """Resposta devolvida após a validação inicial."""

    status: str
    arquivo: str
    tipo_documento: str
    proxima_etapa: str
    mensagem: str