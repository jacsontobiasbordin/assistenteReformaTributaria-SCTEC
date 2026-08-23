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

MAX_TENTATIVAS_GERACAO = 2

# Deteccao 100% deterministica (sem LLM), refinada na Etapa 7 a partir da
# versao simples da Etapa 5 (ver docs/qa/refinamento-seguranca.md). Esta
# lista pode continuar crescendo conforme novos padroes de tentativa de
# manipulacao forem observados (ciclo de refinamento continuo).
_PADROES_SUSPEITOS = [
    # tentativas de sobrescrever as instrucoes do sistema
    "ignore as instrucoes",
    "esqueca as regras",
    "desconsidere o que foi dito",
    "voce agora e",
    "novo system prompt",
    "a partir de agora voce",
    # tentativas de exfiltracao de informacao sensivel
    "revele",
    "mostre sua configuracao",
    "qual e sua api key",
    "system prompt",
    "api key",
    "chave de api",
    "token de acesso",
    "suas instrucoes internas",
    # marcadores comuns de injecao via delimitadores falsos
    '"""system"""',
    "[inst]",
    "<system>",
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
    # Deteccao 100% deterministica (sem LLM). Versao refinada na Etapa 7
    # a partir da deteccao simples da Etapa 5 — ver
    # docs/qa/refinamento-seguranca.md para o ciclo de refinamento.
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


def avaliar_seguranca(state: AgentState) -> dict:
    # Node de juncao (fan-in) entre consultar_base_local e
    # triagem_seguranca. Nao altera o estado — existe apenas para a
    # decisao de roteamento (bloquear vs. seguir para gerar_analise)
    # feita no grafo.
    return {}


def bloquear_acao_insegura(state: AgentState) -> dict:
    # Bloqueio 100% deterministico, executado ANTES de qualquer chamada
    # ao LLM. Nunca chama get_llm() — garante, por regra da aplicacao (e
    # nao por "boa vontade" do modelo), que nenhuma instrucao maliciosa
    # seja seguida e que nenhuma informacao sensivel (system prompt, API
    # key) possa ser revelada por este caminho.
    alertas = list(state.get("alertas", []))
    alertas.append("Tentativa de instrucao nao autorizada detectada e bloqueada.")

    return {
        "resposta_estruturada": {
            "cenario_analisado": "Solicitacao nao processada por motivo de seguranca.",
            "pontos_reforma_relacionados": [],
            "impactos_tecnicos_erp": [],
            "pontos_atencao": ["A pergunta continha uma instrucao que nao sera seguida."],
            "checklist_tecnico": [],
        },
        "alertas": alertas,
    }


def gerar_analise(state: AgentState) -> dict:
    """Unico node agentico do projeto.

    Usa o LLM (via `get_llm()`) apenas para sintetizar a resposta final a
    partir do contexto ja recuperado por `consultar_base_local` — nunca
    para decidir roteamento, autonomia ou execucao de ferramentas.
    """
    tentativas = state.get("tentativas_geracao", 0) + 1
    alertas = list(state.get("alertas", []))

    contexto = json.dumps(state.get("dados_base_local"), ensure_ascii=False, indent=2)

    partes_mensagem = []
    historico = state.get("historico") or []
    if historico:
        ultimas_entradas = json.dumps(historico[-2:], ensure_ascii=False, indent=2)
        partes_mensagem.append(
            f"Contexto de perguntas anteriores nesta sessao:\n{ultimas_entradas}"
        )
    partes_mensagem.append(f"Pergunta do usuario: {state['pergunta_usuario']}")
    partes_mensagem.append(
        f"Contexto recuperado da base local (dados_base_local):\n{contexto}"
    )

    mensagens = [
        SystemMessage(SYSTEM_PROMPT_ANALISE),
        HumanMessage("\n\n".join(partes_mensagem)),
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


def _resposta_e_valida(resposta: dict | None) -> bool:
    if not resposta:
        return False

    campos_obrigatorios = (
        "cenario_analisado",
        "pontos_reforma_relacionados",
        "impactos_tecnicos_erp",
        "pontos_atencao",
        "checklist_tecnico",
    )
    return all(resposta.get(campo) for campo in campos_obrigatorios)


def validar_resposta(state: AgentState) -> dict:
    # Node "passivo": nao altera o estado. Existe apenas para a decisao de
    # roteamento (retry vs. sucesso vs. falha definitiva) feita no grafo.
    return {}


def registrar_historico(state: AgentState) -> dict:
    # So roda no caminho de sucesso (resposta valida): perguntas invalidas
    # ou fora de escopo nao agregam contexto util para perguntas futuras
    # na mesma sessao, entao nao valem a pena reter na memoria de curto
    # prazo.
    entrada = {
        "pergunta": state["pergunta_usuario"],
        "cenario": state["cenario_identificado"],
        "resumo": state["resposta_estruturada"]["cenario_analisado"],
    }
    return {"historico": [entrada]}


def responder_erro_geracao(state: AgentState) -> dict:
    return {
        "resposta_estruturada": {
            "mensagem": (
                "Nao foi possivel concluir a analise apos multiplas "
                "tentativas. Tente novamente em instantes ou reformule a "
                "pergunta."
            )
        },
        "alertas": list(state.get("alertas", [])),
    }


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
