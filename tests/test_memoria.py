from unittest.mock import MagicMock

from app.agent.graph import build_graph, thread_config
from app.agent.schemas import AnaliseEstruturada

_ANALISE_VALIDA = AnaliseEstruturada(
    cenario_analisado="cadastro_produtos",
    pontos_reforma_relacionados=["ponto 1"],
    impactos_tecnicos_erp=["impacto 1"],
    pontos_atencao=["atencao 1"],
    checklist_tecnico=["item 1"],
)


def _estado_inicial(pergunta: str) -> dict:
    return {
        "pergunta_usuario": pergunta,
        "cenario_identificado": None,
        "dados_base_local": None,
        "resposta_estruturada": None,
        "alertas": [],
        "risco_detectado": False,
        "tentativas_geracao": 0,
        "historico": [],
    }


def _mockar_llm(monkeypatch, respostas):
    llm_estruturado = MagicMock()
    llm_estruturado.invoke.side_effect = respostas

    llm = MagicMock()
    llm.with_structured_output.return_value = llm_estruturado

    monkeypatch.setattr("app.agent.nodes.get_llm", lambda: llm)
    return llm_estruturado


def test_segunda_pergunta_mesma_sessao_ve_historico_e_usa_como_contexto(monkeypatch):
    llm_estruturado = _mockar_llm(monkeypatch, [_ANALISE_VALIDA, _ANALISE_VALIDA])
    grafo = build_graph()
    config = thread_config("sessao-continuidade")

    primeira_pergunta = "Como devo cadastrar o NCM dos meus produtos?"
    grafo.invoke(_estado_inicial(primeira_pergunta), config=config)

    resultado_2 = grafo.invoke(
        _estado_inicial("E sobre a classificacao tributaria, o que muda?"),
        config=config,
    )

    # O reducer `add` acumula: a entrada da 1a pergunta permanece, e a 2a
    # pergunta bem-sucedida adiciona mais uma - historico cresce ao longo
    # da sessao em vez de ser sobrescrito.
    assert len(resultado_2["historico"]) == 2
    assert resultado_2["historico"][0]["pergunta"] == primeira_pergunta

    mensagens_segunda_chamada = llm_estruturado.invoke.call_args_list[1].args[0]
    texto_human_message = mensagens_segunda_chamada[1].content
    assert primeira_pergunta in texto_human_message
    assert "Contexto de perguntas anteriores" in texto_human_message


def test_sessoes_com_thread_id_diferentes_nao_compartilham_historico(monkeypatch):
    _mockar_llm(monkeypatch, [_ANALISE_VALIDA, _ANALISE_VALIDA])
    grafo = build_graph()

    grafo.invoke(
        _estado_inicial("Como devo cadastrar o NCM dos meus produtos?"),
        config=thread_config("sessao-a"),
    )

    resultado_sessao_b = grafo.invoke(
        _estado_inicial("Como calcular o IBS e a CBS na venda?"),
        config=thread_config("sessao-b"),
    )

    assert len(resultado_sessao_b["historico"]) == 1
    assert resultado_sessao_b["historico"][0]["cenario"] == "calculo_impostos"


def test_pergunta_invalida_nao_gera_entrada_no_historico():
    grafo = build_graph()
    config = thread_config("sessao-entrada-invalida")

    resultado = grafo.invoke(_estado_inicial("   "), config=config)

    assert resultado["historico"] == []
