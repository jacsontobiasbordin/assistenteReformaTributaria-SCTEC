from pathlib import Path

import pytest
from pydantic import ValidationError

from app.tools import local_kb
from app.tools.local_kb import (
    BaseLocalIndisponivelError,
    carregar_base,
    consultar_cenario,
    listar_cenarios_disponiveis,
)
from app.tools.schemas import (
    CENARIOS_VALIDOS,
    ConsultaCenarioInput,
    RespostaCenarioLocal,
)


@pytest.fixture(autouse=True)
def limpar_cache_base():
    carregar_base.cache_clear()
    yield
    carregar_base.cache_clear()


@pytest.mark.parametrize("cenario", sorted(CENARIOS_VALIDOS))
def test_consultar_cenario_valido_retorna_resposta_completa(cenario):
    payload = ConsultaCenarioInput(cenario=cenario)

    resposta = consultar_cenario(payload)

    assert isinstance(resposta, RespostaCenarioLocal)
    assert resposta.resumo
    assert len(resposta.pontos_reforma_relacionados) > 0
    assert len(resposta.impactos_tecnicos_erp) > 0
    assert len(resposta.pontos_atencao) > 0
    assert len(resposta.checklist_tecnico) > 0


def test_consulta_cenario_input_rejeita_valor_invalido():
    with pytest.raises(ValidationError):
        ConsultaCenarioInput(cenario="invalido")


def test_carregar_base_lanca_erro_quando_arquivo_nao_existe(monkeypatch):
    caminho_inexistente = Path(__file__).resolve().parent / "arquivo_que_nao_existe.json"
    monkeypatch.setattr(local_kb, "_CAMINHO_BASE_LOCAL", caminho_inexistente)

    with pytest.raises(BaseLocalIndisponivelError):
        carregar_base()


def test_listar_cenarios_disponiveis_retorna_os_tres_cenarios():
    cenarios = listar_cenarios_disponiveis()

    assert set(cenarios) == CENARIOS_VALIDOS
    assert len(cenarios) == 3
