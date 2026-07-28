from pathlib import Path

import pymupdf
from app.exceptions import DocumentoSemTextoDigitalError


PASTA_OUTPUT = Path("output")


def extrair_texto_pdf(caminho_pdf: Path) -> tuple[Path, int, int]:
    """
    Extrai texto de um PDF digital.

    Retorna:
    - caminho do TXT gerado;
    - quantidade de páginas;
    - quantidade de caracteres extraídos.
    """

    if not caminho_pdf.exists():
        raise FileNotFoundError(
            f"O arquivo '{caminho_pdf}' não foi encontrado."
        )

    if caminho_pdf.suffix.lower() != ".pdf":
        raise ValueError(
            "A extração desta versão aceita apenas arquivos PDF."
        )

    try:
        with pymupdf.open(caminho_pdf) as documento:
            quantidade_paginas = documento.page_count

            textos_formatados: list[str] = []
            textos_extraidos: list[str] = []

            for numero_pagina, pagina in enumerate(documento, start=1):
                texto = pagina.get_text().strip()

                if texto:
                    textos_extraidos.append(texto)

                textos_formatados.append(
                    f"--- Página {numero_pagina} ---\n{texto}"
                )

    except pymupdf.FileDataError as erro:
        raise ValueError(
            "O arquivo informado não é um PDF válido ou está corrompido."
        ) from erro

    texto_real = "\n".join(textos_extraidos).strip()

    if not texto_real:
        raise DocumentoSemTextoDigitalError(
        "Nenhum texto digital foi encontrado. "
        "O documento pode ser escaneado e exigir OCR."
    )

    texto_completo = "\n\n".join(textos_formatados).strip()

    PASTA_OUTPUT.mkdir(parents=True, exist_ok=True)

    caminho_txt = PASTA_OUTPUT / f"{caminho_pdf.stem}_extraido.txt"

    caminho_txt.write_text(
        texto_completo,
        encoding="utf-8",
    )

    quantidade_caracteres = len(texto_real)

    return caminho_txt, quantidade_paginas, quantidade_caracteres