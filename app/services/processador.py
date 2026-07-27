from pathlib import Path

from app.models import DocumentoEntrada, DocumentoResposta


EXTENSOES_PERMITIDAS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
}


def processar_documento(documento: DocumentoEntrada) -> DocumentoResposta:
    """Valida o documento e cria o primeiro resultado do pipeline."""

    caminho = Path(documento.nome_arquivo)
    extensao = caminho.suffix.lower()

    if extensao not in EXTENSOES_PERMITIDAS:
        extensoes_formatadas = ", ".join(sorted(EXTENSOES_PERMITIDAS))

        raise ValueError(
            f"Extensão '{extensao or 'ausente'}' não permitida. "
            f"Formatos aceitos: {extensoes_formatadas}."
        )

    return DocumentoResposta(
        status="recebido",
        arquivo=caminho.name,
        tipo_documento=documento.tipo_documento.strip().lower(),
        proxima_etapa="extracao_ocr",
        mensagem="Documento validado e encaminhado para o pipeline.",
    )