from pathlib import Path

import pymupdf
import pytesseract
from PIL import Image, UnidentifiedImageError


PASTA_OUTPUT = Path("output")

TESSERACT_EXECUTAVEL = Path(
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

EXTENSOES_IMAGEM = {
    ".png",
    ".jpg",
    ".jpeg",
}


pytesseract.pytesseract.tesseract_cmd = str(
    TESSERACT_EXECUTAVEL
)


def executar_ocr_imagem(imagem: Image.Image) -> str:
    """Executa OCR em uma imagem utilizando português e inglês."""

    return pytesseract.image_to_string(
        imagem,
        lang="por+eng",
    ).strip()


def extrair_texto_ocr(
    caminho_arquivo: Path,
) -> tuple[Path, int, int]:
    """
    Executa OCR em imagens ou PDFs escaneados.

    Retorna:
    - caminho do TXT gerado;
    - quantidade de páginas processadas;
    - quantidade de caracteres extraídos.
    """

    if not caminho_arquivo.exists():
        raise FileNotFoundError(
            f"O arquivo '{caminho_arquivo}' não foi encontrado."
        )

    if not TESSERACT_EXECUTAVEL.exists():
        raise RuntimeError(
            "O executável do Tesseract não foi encontrado em "
            f"'{TESSERACT_EXECUTAVEL}'."
        )

    extensao = caminho_arquivo.suffix.lower()

    textos_extraidos: list[str] = []
    textos_formatados: list[str] = []

    try:
        if extensao == ".pdf":
            with pymupdf.open(caminho_arquivo) as documento:
                quantidade_paginas = documento.page_count

                for numero_pagina, pagina in enumerate(
                    documento,
                    start=1,
                ):
                    matriz = pymupdf.Matrix(2, 2)

                    pixmap = pagina.get_pixmap(
                        matrix=matriz,
                        alpha=False,
                    )

                    imagem = Image.frombytes(
                        "RGB",
                        [pixmap.width, pixmap.height],
                        pixmap.samples,
                    )

                    texto = executar_ocr_imagem(imagem)

                    if texto:
                        textos_extraidos.append(texto)

                    textos_formatados.append(
                        f"--- Página {numero_pagina} ---\n{texto}"
                    )

        elif extensao in EXTENSOES_IMAGEM:
            quantidade_paginas = 1

            with Image.open(caminho_arquivo) as imagem:
                texto = executar_ocr_imagem(
                    imagem.convert("RGB")
                )

            if texto:
                textos_extraidos.append(texto)

            textos_formatados.append(
                f"--- Página 1 ---\n{texto}"
            )

        else:
            raise ValueError(
                "O OCR aceita apenas PDF, PNG, JPG ou JPEG."
            )

    except pymupdf.FileDataError as erro:
        raise ValueError(
            "O PDF informado é inválido ou está corrompido."
        ) from erro

    except UnidentifiedImageError as erro:
        raise ValueError(
            "O arquivo informado não contém uma imagem válida."
        ) from erro

    texto_real = "\n".join(textos_extraidos).strip()

    if not texto_real:
        raise ValueError(
            "O OCR foi executado, mas nenhum texto foi reconhecido."
        )

    texto_completo = "\n\n".join(textos_formatados).strip()

    PASTA_OUTPUT.mkdir(
        parents=True,
        exist_ok=True,
    )

    caminho_txt = (
        PASTA_OUTPUT
        / f"{caminho_arquivo.stem}_ocr.txt"
    )

    caminho_txt.write_text(
        texto_completo,
        encoding="utf-8",
    )

    quantidade_caracteres = len(texto_real)

    return (
        caminho_txt,
        quantidade_paginas,
        quantidade_caracteres,
    )