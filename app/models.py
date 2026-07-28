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


class UploadResposta(BaseModel):
    """Resposta devolvida após o armazenamento do arquivo."""

    status: str
    arquivo: str
    tipo_conteudo: str
    tamanho_bytes: int
    caminho_salvo: str
    proxima_etapa: str

class ExtracaoResposta(BaseModel):
    """Resposta devolvida após a extração de texto de um PDF."""

    status: str
    arquivo_origem: str
    arquivo_texto: str
    quantidade_paginas: int
    quantidade_caracteres: int
    caminho_salvo: str

class OCRResposta(BaseModel):
    """Resposta devolvida após o processamento por OCR."""

    status: str
    arquivo_origem: str
    arquivo_texto: str
    quantidade_paginas: int
    quantidade_caracteres: int
    caminho_salvo: str
    mecanismo: str
    