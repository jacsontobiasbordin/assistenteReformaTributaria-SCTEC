"""Nodes do grafo do agente.

Todos os nodes deste arquivo, até a Etapa 4, são 100% determinísticos
(regras da aplicação, sem LLM). O único node agêntico de todo o projeto
é gerar_analise (introduzido na Etapa 5), que usa o LLM apenas para
sintetizar a resposta final a partir do contexto já recuperado — nunca
para decidir roteamento, autonomia ou execução de ferramentas.
"""

from __future__ import annotations

import json

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import ValidationError

from app.agent.prompts import SYSTEM_PROMPT_ANALISE
from app.agent.schemas import AnaliseEstruturada
from app.agent.state import AgentState
from app.llm.factory import get_llm
from app.tools.local_kb import (
    BaseLocalIndisponivelError,
    CenarioNaoEncontradoError,
    consultar_cenario,
)
from app.tools.schemas import ConsultaCenarioInput

_PADROES_SUSPEITOS = [
    "ignore as instrucoes",
    "esqueca as regras",
    "revele",
    "system prompt",
    "api key",
    "mostre sua configuracao",
]

_PALAVRAS_CHAVE_POR_CENARIO = {
    "cadastro_produtos": [
        "cadastro",
        "produto",
        "ncm",
        "classificacao tributaria",
        "cclasstrib",
    ],
    "emissao_nota_fiscal": [
        "nota fiscal",
        "nf-e",
        "nfe",
        "nfc-e",
        "emissao",
        "danfe",
    ],
    "calculo_impostos": [
        "calculo",
        "imposto",
        "ibs",
        "cbs",
        "tributo",
        "aliquota",
    ],
}

_TAMANHO_MAXIMO_PERGUNTA = 500


def validar_entrada(state: AgentState) -> dict:
    pergunta = state["pergunta_usuario"].strip()
    alertas = list(state.get("alertas", []))

    if not pergunta:
        alertas.append("Por favor, informe uma pergunta ou selecione um cenario.")
    elif len(pergunta) > _TAMANHO_MAXIMO_PERGUNTA:
        alertas.append(
            "Sua pergunta e muito longa. Tente resumir em ate 500 caracteres."
        )

    return {"pergunta_usuario": pergunta, "alertas": alertas}


def identificar_cenario(state: AgentState) -> dict:
    pergunta = state["pergunta_usuario"].lower()

    for cenario, palavras_chave in _PALAVRAS_CHAVE_POR_CENARIO.items():
        if any(palavra in pergunta for palavra in palavras_chave):
            return {"cenario_identificado": cenario}

    return {"cenario_identificado": "fora_de_escopo"}


def triagem_seguranca(state: AgentState) -> dict:
    # Deteccao inicial simples (Etapa 5). Sera substituida por uma versao
    # mais robusta na Etapa 7, junto com o cenario adversarial completo e
    # o bloqueio de acao sensivel.
    pergunta = state["pergunta_usuario"].lower()
    risco_detectado = any(padrao in pergunta for padrao in _PADROES_SUSPEITOS)
    return {"risco_detectado": risco_detectado}


def consultar_base_local(state: AgentState) -> dict:
    alertas = list(state.get("alertas", []))

    try:
        payload = ConsultaCenarioInput(cenario=state["cenario_identificado"])
        resposta = consultar_cenario(payload)
        return {"dados_base_local": resposta.model_dump(), "alertas": alertas}
    except (ValidationError, CenarioNaoEncontradoError, BaseLocalIndisponivelError):
        alertas.append(
            "Nao foi possivel consultar a base local de conhecimento para "
            "este cenario no momento."
        )
        return {"dados_base_local": None, "alertas": alertas}


def gerar_analise(state: AgentState) -> dict:
    """Unico node agentico do projeto.

    Usa o LLM (via `get_llm()`) apenas para sintetizar a resposta final a
    partir do contexto ja recuperado por `consultar_base_local` — nunca
    para decidir roteamento, autonomia ou execucao de ferramentas.
    """
    tentativas = state.get("tentativas_geracao", 0) + 1
    alertas = list(state.get("alertas", []))

    contexto = json.dumps(state.get("dados_base_local"), ensure_ascii=False, indent=2)
    mensagens = [
        SystemMessage(SYSTEM_PROMPT_ANALISE),
        HumanMessage(
            f"Pergunta do usuario: {state['pergunta_usuario']}\n\n"
            f"Contexto recuperado da base local (dados_base_local):\n{contexto}"
        ),
    ]

    try:
        llm = get_llm()
        estruturado = llm.with_structured_output(AnaliseEstruturada)
        resultado = estruturado.invoke(mensagens)
        return {
            "tentativas_geracao": tentativas,
            "resposta_estruturada": resultado.model_dump(),
        }
    except Exception:  # noqa: BLE001 - falha de LLM (rede/timeout/formato) nao pode propagar
        alertas.append(
            "Nao foi possivel gerar a analise no momento. Tentando novamente..."
        )
        return {"tentativas_geracao": tentativas, "alertas": alertas}


def responder_entrada_invalida(state: AgentState) -> dict:
    mensagem = " ".join(state.get("alertas", []))
    return {"resposta_estruturada": {"mensagem": mensagem}}


def responder_fora_de_escopo(state: AgentState) -> dict:
    return {
        "resposta_estruturada": {
            "mensagem": (
                "Sua pergunta nao se encaixa em nenhum dos 3 cenarios "
                "suportados (cadastro de produtos, emissao de nota fiscal "
                "ou calculo de IBS/CBS). Tente reformular mencionando um "
                "desses temas."
            )
        }
    }
