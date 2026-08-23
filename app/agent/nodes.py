"""Nodes do grafo do agente.

Todos os nodes deste arquivo, até a Etapa 4, são 100% determinísticos
(regras da aplicação, sem LLM). O único node agêntico de todo o projeto
é gerar_analise (introduzido na Etapa 5), que usa o LLM apenas para
sintetizar a resposta final a partir do contexto já recuperado — nunca
para decidir roteamento, autonomia ou execução de ferramentas.
"""

from __future__ import annotations

from app.agent.state import AgentState

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
