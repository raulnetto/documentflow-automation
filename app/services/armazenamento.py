from pathlib import Path
from shutil import copyfileobj

from fastapi import UploadFile


PASTA_INPUT = Path("input")

EXTENSOES_PERMITIDAS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
}


def validar_extensao(nome_arquivo: str) -> str:
    """Valida a extensão do arquivo recebido."""

    extensao = Path(nome_arquivo).suffix.lower()

    if extensao not in EXTENSOES_PERMITIDAS:
        formatos = ", ".join(sorted(EXTENSOES_PERMITIDAS))

        raise ValueError(
            f"Extensão '{extensao or 'ausente'}' não permitida. "
            f"Formatos aceitos: {formatos}."
        )

    return extensao


def salvar_upload(arquivo: UploadFile) -> tuple[Path, int]:
    """Salva o upload e devolve caminho e tamanho do arquivo."""

    if not arquivo.filename:
        raise ValueError("O arquivo enviado não possui um nome válido.")

    validar_extensao(arquivo.filename)

    PASTA_INPUT.mkdir(parents=True, exist_ok=True)

    nome_seguro = Path(arquivo.filename).name
    caminho_destino = PASTA_INPUT / nome_seguro

    with caminho_destino.open("wb") as destino:
        copyfileobj(arquivo.file, destino)

    tamanho_bytes = caminho_destino.stat().st_size

    if tamanho_bytes == 0:
        caminho_destino.unlink(missing_ok=True)
        raise ValueError("O arquivo enviado está vazio.")

    return caminho_destino, tamanho_bytes