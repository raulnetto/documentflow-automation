from pathlib import Path

from app.exceptions import DocumentoSemTextoDigitalError
from app.services.extrator_ocr import extrair_texto_ocr
from app.services.extrator_pdf import extrair_texto_pdf


EXTENSOES_IMAGEM = {
    ".png",
    ".jpg",
    ".jpeg",
}


def processar_automaticamente(
    caminho_arquivo: Path,
) -> tuple[Path, int, int, str]:
    """
    Escolhe automaticamente o mecanismo adequado.

    Retorna:
    - caminho do TXT gerado;
    - quantidade de páginas;
    - quantidade de caracteres;
    - mecanismo utilizado.
    """

    if not caminho_arquivo.exists():
        raise FileNotFoundError(
            f"O arquivo '{caminho_arquivo}' não foi encontrado."
        )

    extensao = caminho_arquivo.suffix.lower()

    if extensao == ".pdf":
        try:
            caminho_txt, paginas, caracteres = extrair_texto_pdf(
                caminho_arquivo
            )

            return (
                caminho_txt,
                paginas,
                caracteres,
                "pymupdf",
            )

        except DocumentoSemTextoDigitalError:
            caminho_txt, paginas, caracteres = extrair_texto_ocr(
                caminho_arquivo
            )

            return (
                caminho_txt,
                paginas,
                caracteres,
                "tesseract",
            )

    if extensao in EXTENSOES_IMAGEM:
        caminho_txt, paginas, caracteres = extrair_texto_ocr(
            caminho_arquivo
        )

        return (
            caminho_txt,
            paginas,
            caracteres,
            "tesseract",
        )

    raise ValueError(
        "O processamento automático aceita apenas "
        "PDF, PNG, JPG ou JPEG."
    )