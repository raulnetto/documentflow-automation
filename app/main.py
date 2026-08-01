from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile, status

from app.models import (
    DocumentoEntrada,
    DocumentoResposta,
    ExtracaoResposta,
    OCRResposta,
    ProcessamentoAutomaticoResposta,
    UploadResposta,
    WebhookProcessamentoEntrada,
    WebhookProcessamentoResposta,
)
from app.services.armazenamento import salvar_upload
from app.services.extrator_ocr import extrair_texto_ocr
from app.services.extrator_pdf import extrair_texto_pdf
from app.services.processador import processar_documento
from app.services.processador_automatico import processar_automaticamente
from app.services.registro_processamento import (
    criar_registro_processamento,
)


app = FastAPI(
    title="Automação de Documentos",
    description="API para processamento automatizado de documentos.",
    version="0.8.0",
)


@app.get("/")
def verificar_api() -> dict[str, str]:
    """Confirma que a API está funcionando."""

    return {
        "status": "online",
        "servico": "Automação de Documentos",
        "versao": "0.8.0",
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


@app.post(
    "/documentos/{nome_arquivo}/ocr",
    response_model=OCRResposta,
    status_code=status.HTTP_200_OK,
)
def processar_documento_com_ocr(
    nome_arquivo: str,
) -> OCRResposta:
    """Executa OCR em imagem ou PDF escaneado armazenado em input/."""

    caminho_arquivo = Path("input") / Path(nome_arquivo).name

    try:
        caminho_txt, paginas, caracteres = extrair_texto_ocr(
            caminho_arquivo
        )

        return OCRResposta(
            status="ocr_concluido",
            arquivo_origem=caminho_arquivo.name,
            arquivo_texto=caminho_txt.name,
            quantidade_paginas=paginas,
            quantidade_caracteres=caracteres,
            caminho_salvo=str(caminho_txt),
            mecanismo="tesseract",
        )

    except FileNotFoundError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro),
        ) from erro

    except RuntimeError as erro:
        criar_registro_processamento(
            arquivo_origem=caminho_arquivo.name,
            status="erro",
            mecanismo="tesseract",
            mensagem_erro=str(erro),
        )


        raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=str(erro),
    ) from erro

    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro),
        ) from erro
@app.post(
    "/documentos/{nome_arquivo}/processar-automaticamente",
    response_model=ProcessamentoAutomaticoResposta,
    status_code=status.HTTP_200_OK,
)
def processar_documento_automaticamente(
    nome_arquivo: str,
) -> ProcessamentoAutomaticoResposta:
    """Escolhe automaticamente entre extração digital e OCR."""

    caminho_arquivo = Path("input") / Path(nome_arquivo).name

    try:
        (
            caminho_txt,
            paginas,
            caracteres,
            mecanismo,
        ) = processar_automaticamente(caminho_arquivo)

        registro = criar_registro_processamento(
            arquivo_origem=caminho_arquivo.name,
            status="sucesso",
            mecanismo=mecanismo,
            arquivo_saida=caminho_txt.name,
            quantidade_paginas=paginas,
            quantidade_caracteres=caracteres,
        )

        return ProcessamentoAutomaticoResposta(
    status="processamento_concluido",
    arquivo_origem=caminho_arquivo.name,
    arquivo_texto=caminho_txt.name,
    quantidade_paginas=paginas,
    quantidade_caracteres=caracteres,
    caminho_salvo=str(caminho_txt),
    mecanismo=mecanismo,
    id_registro=registro["id"],
    caminho_registro=registro["caminho_registro"],
)

    except FileNotFoundError as erro:
        criar_registro_processamento(
            arquivo_origem=caminho_arquivo.name,
            status="erro",
            mensagem_erro=str(erro),
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro),
        ) from erro

    except RuntimeError as erro:
        criar_registro_processamento(
        arquivo_origem=caminho_arquivo.name,
        status="erro",
        mecanismo="tesseract",
        mensagem_erro=str(erro),
    )

        raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=str(erro),
    ) from erro

    except ValueError as erro:
        criar_registro_processamento(
            arquivo_origem=caminho_arquivo.name,
            status="erro",
            mensagem_erro=str(erro),
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro),
        ) from erro

@app.post(
    "/webhooks/processar-documento",
    response_model=WebhookProcessamentoResposta,
    status_code=status.HTTP_200_OK,
)
def processar_documento_via_webhook(
    dados: WebhookProcessamentoEntrada,
) -> WebhookProcessamentoResposta:
    """Recebe uma solicitação externa e processa um arquivo já armazenado."""

    caminho_arquivo = Path("input") / Path(dados.nome_arquivo).name

    try:
        (
            caminho_txt,
            paginas,
            caracteres,
            mecanismo,
        ) = processar_automaticamente(caminho_arquivo)

        registro = criar_registro_processamento(
            arquivo_origem=caminho_arquivo.name,
            status="sucesso",
            mecanismo=mecanismo,
            arquivo_saida=caminho_txt.name,
            quantidade_paginas=paginas,
            quantidade_caracteres=caracteres,
            origem=dados.origem,
            id_fluxo=dados.id_fluxo,
        )

        return WebhookProcessamentoResposta(
            status="processamento_concluido",
            origem=dados.origem,
            id_fluxo=dados.id_fluxo,
            arquivo_origem=caminho_arquivo.name,
            arquivo_texto=caminho_txt.name,
            quantidade_paginas=paginas,
            quantidade_caracteres=caracteres,
            mecanismo=mecanismo,
            id_registro=registro["id"],
            caminho_registro=registro["caminho_registro"],
        )

    except FileNotFoundError as erro:
        criar_registro_processamento(
            arquivo_origem=caminho_arquivo.name,
            status="erro",
            mensagem_erro=str(erro),
            origem=dados.origem,
            id_fluxo=dados.id_fluxo,
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro),
        ) from erro

    except RuntimeError as erro:
        criar_registro_processamento(
            arquivo_origem=caminho_arquivo.name,
            status="erro",
            mecanismo="tesseract",
            mensagem_erro=str(erro),
            origem=dados.origem,
            id_fluxo=dados.id_fluxo,
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(erro),
        ) from erro

    except ValueError as erro:
        criar_registro_processamento(
            arquivo_origem=caminho_arquivo.name,
            status="erro",
            mensagem_erro=str(erro),
            origem=dados.origem,
            id_fluxo=dados.id_fluxo,
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro),
        ) from erro