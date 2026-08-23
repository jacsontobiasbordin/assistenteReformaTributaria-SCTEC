"""Montagem do grafo LangGraph do agente.

Fluxo atual (Etapa 6):

    validar_entrada
        -> [invalida] responder_entrada_invalida -> END
        -> [valida] identificar_cenario
    identificar_cenario
        -> [fora_de_escopo] responder_fora_de_escopo -> END
        -> [valido] fan-out: consultar_base_local + triagem_seguranca
    consultar_base_local + triagem_seguranca (rodam em paralelo, mesma
    superstep do LangGraph)
        -> fan-in: gerar_analise
    gerar_analise -> validar_resposta
    validar_resposta
        -> [valida] registrar_historico -> END
        -> [invalida, tentativas < MAX_TENTATIVAS_GERACAO] gerar_analise (retry)
        -> [invalida, tentativas >= MAX_TENTATIVAS_GERACAO] responder_erro_geracao -> END

A partir da Etapa 7, a aresta pos-validar_resposta valida vai rotear
tambem por risco_detectado, inserindo o node solicitar_aprovacao_humana
antes do fim.

Limitacao assumida nesta versao: o MemorySaver mantem o historico em
memoria do processo — reinicia se a aplicacao for reiniciada. Suficiente
para o escopo deste projeto (memoria de curto prazo por sessao);
armazenamento persistente entre reinicializacoes fica como evolucao
futura.
"""

from __future__ import annotations

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from app.agent.nodes import (
    MAX_TENTATIVAS_GERACAO,
    _resposta_e_valida,
    consultar_base_local,
    gerar_analise,
    identificar_cenario,
    registrar_historico,
    responder_entrada_invalida,
    responder_erro_geracao,
    responder_fora_de_escopo,
    triagem_seguranca,
    validar_entrada,
    validar_resposta,
)
from app.agent.state import AgentState


def thread_config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}


def _rotear_apos_validar_entrada(state: AgentState) -> str:
    if state.get("alertas"):
        return "invalida"
    return "valida"


def _rotear_apos_identificar_cenario(state: AgentState) -> str | list[str]:
    if state["cenario_identificado"] == "fora_de_escopo":
        return "responder_fora_de_escopo"
    return ["consultar_base_local", "triagem_seguranca"]


def _rotear_apos_validar_resposta(state: AgentState) -> str:
    if _resposta_e_valida(state.get("resposta_estruturada")):
        return "valida"
    if state.get("tentativas_geracao", 0) < MAX_TENTATIVAS_GERACAO:
        return "retry"
    return "erro"


def build_graph():
    grafo = StateGraph(AgentState)

    grafo.add_node("validar_entrada", validar_entrada)
    grafo.add_node("identificar_cenario", identificar_cenario)
    grafo.add_node("consultar_base_local", consultar_base_local)
    grafo.add_node("triagem_seguranca", triagem_seguranca)
    grafo.add_node("gerar_analise", gerar_analise)
    grafo.add_node("validar_resposta", validar_resposta)
    grafo.add_node("responder_entrada_invalida", responder_entrada_invalida)
    grafo.add_node("responder_fora_de_escopo", responder_fora_de_escopo)
    grafo.add_node("responder_erro_geracao", responder_erro_geracao)
    grafo.add_node("registrar_historico", registrar_historico)

    grafo.set_entry_point("validar_entrada")

    grafo.add_conditional_edges(
        "validar_entrada",
        _rotear_apos_validar_entrada,
        {
            "invalida": "responder_entrada_invalida",
            "valida": "identificar_cenario",
        },
    )
    grafo.add_conditional_edges(
        "identificar_cenario",
        _rotear_apos_identificar_cenario,
        {
            "responder_fora_de_escopo": "responder_fora_de_escopo",
            "consultar_base_local": "consultar_base_local",
            "triagem_seguranca": "triagem_seguranca",
        },
    )

    grafo.add_edge("responder_entrada_invalida", END)
    grafo.add_edge("responder_fora_de_escopo", END)

    # Fan-in: gerar_analise so executa depois que os dois ramos paralelos
    # (consultar_base_local e triagem_seguranca) terminarem.
    grafo.add_edge("consultar_base_local", "gerar_analise")
    grafo.add_edge("triagem_seguranca", "gerar_analise")

    grafo.add_edge("gerar_analise", "validar_resposta")

    grafo.add_conditional_edges(
        "validar_resposta",
        _rotear_apos_validar_resposta,
        {
            "valida": "registrar_historico",
            "retry": "gerar_analise",
            "erro": "responder_erro_geracao",
        },
    )
    grafo.add_edge("registrar_historico", END)
    grafo.add_edge("responder_erro_geracao", END)

    return grafo.compile(checkpointer=MemorySaver())
