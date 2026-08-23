import pytest

from app.agent.graph import build_graph
from app.tools.schemas import CENARIOS_VALIDOS


def _estado_inicial(pergunta: str) -> dict:
    return {
        "pergunta_usuario": pergunta,
        "cenario_identificado": None,
        "dados_base_local": None,
        "resposta_estruturada": None,
        "alertas": [],
    }


@pytest.mark.parametrize(
    "pergunta,cenario_esperado",
    [
        ("Como devo cadastrar o NCM dos meus produtos?", "cadastro_produtos"),
        ("Preciso emitir uma NF-e com os novos campos", "emissao_nota_fiscal"),
        ("Como calcular o IBS e a CBS na venda?", "calculo_impostos"),
    ],
)
def test_grafo_identifica_cenario_e_consulta_base_local(pergunta, cenario_esperado):
    resultado = build_graph().invoke(_estado_inicial(pergunta))

    assert resultado["cenario_identificado"] == cenario_esperado
    assert resultado["dados_base_local"] is not None
    assert resultado["dados_base_local"]["resumo"]


def test_grafo_com_pergunta_vazia_retorna_mensagem_de_validacao():
    resultado = build_graph().invoke(_estado_inicial("   "))

    assert resultado["dados_base_local"] is None
    assert resultado["resposta_estruturada"] is not None
    assert "pergunta" in resultado["resposta_estruturada"]["mensagem"].lower()


def test_grafo_com_pergunta_fora_de_escopo():
    resultado = build_graph().invoke(_estado_inicial("Qual a previsao do tempo hoje?"))

    assert resultado["cenario_identificado"] == "fora_de_escopo"
    assert resultado["resposta_estruturada"] is not None
    assert resultado["dados_base_local"] is None


def test_cenarios_suportados_cobrem_os_tres_definidos():
    assert CENARIOS_VALIDOS == {
        "cadastro_produtos",
        "emissao_nota_fiscal",
        "calculo_impostos",
    }
