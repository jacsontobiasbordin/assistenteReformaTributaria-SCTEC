"""Montagem do grafo LangGraph do agente.

Fluxo atual (Etapa 7):

    validar_entrada
        -> [invalida] responder_entrada_invalida -> END
        -> [valida] identificar_cenario
    identificar_cenario
        -> [fora_de_escopo] responder_fora_de_escopo -> END
        -> [valido] fan-out: consultar_base_local + triagem_seguranca
    consultar_base_local + triagem_seguranca (rodam em paralelo, mesma
    superstep do LangGraph)
        -> fan-in: avaliar_seguranca
    avaliar_seguranca
        -> [risco_detectado] bloquear_acao_insegura -> END
        -> [sem risco] gerar_analise
    gerar_analise -> validar_resposta
    validar_resposta
        -> [invalida, tentativas < MAX_TENTATIVAS_GERACAO] gerar_analise (retry)
        -> [invalida, tentativas >= MAX_TENTATIVAS_GERACAO] responder_erro_geracao -> END
        -> [valida, cenario == calculo_impostos] solicitar_aprovacao_humana -> registrar_historico -> END
        -> [valida, demais cenarios] registrar_historico -> END

Duas frentes de seguranca (requisito 4.5):
    A) Bloqueio deterministico de entrada adversarial: quando
       triagem_seguranca detecta um padrao suspeito, avaliar_seguranca
       roteia direto para bloquear_acao_insegura, ANTES de qualquer
       chamada ao LLM — o bloqueio e uma regra da aplicacao, nao depende
       do modelo "se comportar bem".
    B) Portao de aprovacao humana para acao sensivel: analises de
       calculo_impostos (maior risco financeiro/de compliance do
       dominio) sempre passam por solicitar_aprovacao_humana antes do
       fim. Nenhuma notificacao externa e disparada aqui — o "portao" so
       sinaliza a pendencia; o disparo real fica para a Etapa 12.

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
    avaliar_seguranca,
    bloquear_acao_insegura,
    consultar_base_local,
    gerar_analise,
    identificar_cenario,
    registrar_historico,
    responder_entrada_invalida,
    responder_erro_geracao,
    responder_fora_de_escopo,
    solicitar_aprovacao_humana,
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


def _rotear_apos_avaliar_seguranca(state: AgentState) -> str:
    if state.get("risco_detectado"):
        return "bloquear"
    return "seguro"


def _rotear_apos_validar_resposta(state: AgentState) -> str:
    if _resposta_e_valida(state.get("resposta_estruturada")):
        if state.get("cenario_identificado") == "calculo_impostos":
            return "requer_aprovacao"
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
    grafo.add_node("avaliar_seguranca", avaliar_seguranca)
    grafo.add_node("bloquear_acao_insegura", bloquear_acao_insegura)
    grafo.add_node("gerar_analise", gerar_analise)
    grafo.add_node("validar_resposta", validar_resposta)
    grafo.add_node("solicitar_aprovacao_humana", solicitar_aprovacao_humana)
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

    # Fan-in: avaliar_seguranca so executa depois que os dois ramos
    # paralelos (consultar_base_local e triagem_seguranca) terminarem.
    grafo.add_edge("consultar_base_local", "avaliar_seguranca")
    grafo.add_edge("triagem_seguranca", "avaliar_seguranca")

    # Frente A: bloqueio deterministico ANTES de qualquer chamada ao LLM.
    grafo.add_conditional_edges(
        "avaliar_seguranca",
        _rotear_apos_avaliar_seguranca,
        {
            "bloquear": "bloquear_acao_insegura",
            "seguro": "gerar_analise",
        },
    )
    grafo.add_edge("bloquear_acao_insegura", END)

    grafo.add_edge("gerar_analise", "validar_resposta")

    # Frente B: portao de aprovacao humana para calculo_impostos.
    grafo.add_conditional_edges(
        "validar_resposta",
        _rotear_apos_validar_resposta,
        {
            "valida": "registrar_historico",
            "requer_aprovacao": "solicitar_aprovacao_humana",
            "retry": "gerar_analise",
            "erro": "responder_erro_geracao",
        },
    )
    grafo.add_edge("solicitar_aprovacao_humana", "registrar_historico")
    grafo.add_edge("registrar_historico", END)
    grafo.add_edge("responder_erro_geracao", END)

    return grafo.compile(checkpointer=MemorySaver())
