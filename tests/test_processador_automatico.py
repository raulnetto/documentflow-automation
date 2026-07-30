from pathlib import Path

import pytest

from app.exceptions import DocumentoSemTextoDigitalError
from app.services import processador_automatico


def test_pdf_digital_utiliza_pymupdf(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifica se um PDF digital utiliza o extrator PyMuPDF."""

    caminho_pdf = tmp_path / "documento_digital.pdf"
    caminho_pdf.touch()

    caminho_txt_esperado = (
        tmp_path / "documento_digital_extraido.txt"
    )

    def extrair_pdf_falso(
        caminho_arquivo: Path,
    ) -> tuple[Path, int, int]:
        assert caminho_arquivo == caminho_pdf

        return (
            caminho_txt_esperado,
            3,
            1500,
        )

    def ocr_nao_deve_ser_executado(
        caminho_arquivo: Path,
    ) -> tuple[Path, int, int]:
        raise AssertionError(
            f"O OCR não deveria ser chamado para "
            f"{caminho_arquivo.name}."
        )

    monkeypatch.setattr(
        processador_automatico,
        "extrair_texto_pdf",
        extrair_pdf_falso,
    )

    monkeypatch.setattr(
        processador_automatico,
        "extrair_texto_ocr",
        ocr_nao_deve_ser_executado,
    )

    (
        caminho_txt,
        paginas,
        caracteres,
        mecanismo,
    ) = processador_automatico.processar_automaticamente(
        caminho_pdf
    )

    assert caminho_txt == caminho_txt_esperado
    assert paginas == 3
    assert caracteres == 1500
    assert mecanismo == "pymupdf"


def test_pdf_sem_texto_digital_utiliza_ocr(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifica o fallback para OCR em PDF sem texto digital."""

    caminho_pdf = tmp_path / "documento_escaneado.pdf"
    caminho_pdf.touch()

    caminho_txt_esperado = (
        tmp_path / "documento_escaneado_ocr.txt"
    )

    def extrair_pdf_sem_texto(
        caminho_arquivo: Path,
    ) -> tuple[Path, int, int]:
        assert caminho_arquivo == caminho_pdf

        raise DocumentoSemTextoDigitalError(
            "O PDF não possui texto digital."
        )

    def extrair_ocr_falso(
        caminho_arquivo: Path,
    ) -> tuple[Path, int, int]:
        assert caminho_arquivo == caminho_pdf

        return (
            caminho_txt_esperado,
            2,
            800,
        )

    monkeypatch.setattr(
        processador_automatico,
        "extrair_texto_pdf",
        extrair_pdf_sem_texto,
    )

    monkeypatch.setattr(
        processador_automatico,
        "extrair_texto_ocr",
        extrair_ocr_falso,
    )

    (
        caminho_txt,
        paginas,
        caracteres,
        mecanismo,
    ) = processador_automatico.processar_automaticamente(
        caminho_pdf
    )

    assert caminho_txt == caminho_txt_esperado
    assert paginas == 2
    assert caracteres == 800
    assert mecanismo == "tesseract"

def test_imagem_utiliza_ocr_diretamente(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifica se imagens são enviadas diretamente ao OCR."""

    caminho_imagem = tmp_path / "documento.jpg"
    caminho_imagem.touch()

    caminho_txt_esperado = (
        tmp_path / "documento_ocr.txt"
    )

    def extrair_pdf_nao_deve_ser_executado(
        caminho_arquivo: Path,
    ) -> tuple[Path, int, int]:
        raise AssertionError(
            f"O extrator de PDF não deveria ser chamado para "
            f"{caminho_arquivo.name}."
        )

    def extrair_ocr_falso(
        caminho_arquivo: Path,
    ) -> tuple[Path, int, int]:
        assert caminho_arquivo == caminho_imagem

        return (
            caminho_txt_esperado,
            1,
            420,
        )

    monkeypatch.setattr(
        processador_automatico,
        "extrair_texto_pdf",
        extrair_pdf_nao_deve_ser_executado,
    )

    monkeypatch.setattr(
        processador_automatico,
        "extrair_texto_ocr",
        extrair_ocr_falso,
    )

    (
        caminho_txt,
        paginas,
        caracteres,
        mecanismo,
    ) = processador_automatico.processar_automaticamente(
        caminho_imagem
    )

    assert caminho_txt == caminho_txt_esperado
    assert paginas == 1
    assert caracteres == 420
    assert mecanismo == "tesseract"

def test_arquivo_inexistente_gera_erro(
    tmp_path: Path,
) -> None:
    """Verifica se um arquivo inexistente gera FileNotFoundError."""

    caminho_inexistente = tmp_path / "arquivo_inexistente.pdf"

    with pytest.raises(
        FileNotFoundError,
        match="não foi encontrado",
    ):
        processador_automatico.processar_automaticamente(
            caminho_inexistente
        )


def test_extensao_nao_suportada_gera_erro(
    tmp_path: Path,
) -> None:
    """Verifica se uma extensão proibida gera ValueError."""

    caminho_txt = tmp_path / "documento.txt"
    caminho_txt.touch()

    with pytest.raises(
    ValueError,
    match="aceita apenas PDF",
    ):
        processador_automatico.processar_automaticamente(
            caminho_txt
        )