from app.models import ProcessamentoHistoricoResposta
from app.models import ProcessamentoResumoResposta
from app.repositories.processamento_repository import (
    buscar_processamento_por_id,
    listar_processamentos,
    obter_resumo_processamentos,
)


def obter_historico_processamentos() -> list[ProcessamentoHistoricoResposta]:
    """Retorna o histórico completo de processamentos."""

    registros = listar_processamentos()

    return [
        ProcessamentoHistoricoResposta(**registro)
        for registro in registros
    ]


def obter_processamento_por_id(
    identificador: str,
) -> ProcessamentoHistoricoResposta | None:
    """Retorna um processamento específico pelo identificador."""

    registro = buscar_processamento_por_id(identificador)

    if registro is None:
        return None

    return ProcessamentoHistoricoResposta(**registro)

def obter_resumo_historico() -> ProcessamentoResumoResposta:
    """Retorna um resumo estatístico dos processamentos."""

    resumo = obter_resumo_processamentos()

    return ProcessamentoResumoResposta(**resumo)