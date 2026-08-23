from __future__ import annotations

from langgraph.graph import END, StateGraph

from app.agent.nodes import (
    consultar_base_local,
    identificar_cenario,
    responder_entrada_invalida,
    responder_fora_de_escopo,
    validar_entrada,
)
from app.agent.state import AgentState


def _rotear_apos_validar_entrada(state: AgentState) -> str:
    if state.get("alertas"):
        return "invalida"
    return "valida"


def _rotear_apos_identificar_cenario(state: AgentState) -> str:
    if state.get("cenario_identificado") == "fora_de_escopo":
        return "fora_de_escopo"
    return "valido"


def build_graph():
    grafo = StateGraph(AgentState)

    grafo.add_node("validar_entrada", validar_entrada)
    grafo.add_node("identificar_cenario", identificar_cenario)
    grafo.add_node("consultar_base_local", consultar_base_local)
    grafo.add_node("responder_entrada_invalida", responder_entrada_invalida)
    grafo.add_node("responder_fora_de_escopo", responder_fora_de_escopo)

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
            "fora_de_escopo": "responder_fora_de_escopo",
            "valido": "consultar_base_local",
        },
    )

    grafo.add_edge("responder_entrada_invalida", END)
    grafo.add_edge("responder_fora_de_escopo", END)
    # Temporario: na Etapa 5, consultar_base_local passa a alimentar, em
    # paralelo, a triagem de seguranca e, na sequencia, gerar_analise.
    grafo.add_edge("consultar_base_local", END)

    return grafo.compile()
