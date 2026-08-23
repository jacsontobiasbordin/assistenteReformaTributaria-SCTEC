from __future__ import annotations

from operator import add
from typing import Annotated, TypedDict


class AgentState(TypedDict):
    """Estado compartilhado do grafo do agente.

    Campos mínimos necessários até a Etapa 4 (núcleo determinístico do
    grafo). Este TypedDict será estendido nas próximas etapas para
    suportar memória de sessão (Etapa 6), triagem de segurança e
    aprovação humana (Etapa 7) e controle de retry (Etapa 5).

    Atributos:
        pergunta_usuario: pergunta em linguagem natural digitada pelo
            usuário, antes de qualquer validação ou normalização.
        cenario_identificado: um dos três cenários suportados
            ("cadastro_produtos", "emissao_nota_fiscal",
            "calculo_impostos"), "fora_de_escopo", ou None enquanto ainda
            não foi identificado.
        dados_base_local: resultado da consulta à base local de
            conhecimento (serializado de `RespostaCenarioLocal`, via
            `.model_dump()`), ou None se a consulta ainda não ocorreu ou
            falhou.
        resposta_estruturada: resposta final montada para o usuário
            (estrutura ainda evolui nas próximas etapas), ou None
            enquanto o grafo não chegou a um nó de resposta.
        alertas: lista de mensagens de validação, erro ou aviso
            acumuladas ao longo da execução do grafo.
        risco_detectado: preenchido por `triagem_seguranca`; indica se a
            pergunta do usuário contém algum padrão suspeito de tentativa
            de manipular as instruções do sistema. Valor padrão `False`
            quando não informado na chamada de `.invoke()`.
        tentativas_geracao: contador de chamadas ao LLM feitas por
            `gerar_analise` para a pergunta atual, usado para limitar o
            retry a `MAX_TENTATIVAS_GERACAO`. Valor padrão `0` quando não
            informado na chamada de `.invoke()`.
        aguardando_aprovacao_humana: preenchido por
            `solicitar_aprovacao_humana`; indica que a análise envolve
            uma ação de maior risco no domínio (cálculo de impostos) e
            requer aprovação humana antes de qualquer notificação
            externa poder ser disparada. Valor padrão `False` quando não
            informado na chamada de `.invoke()`.
        historico: memória de curto prazo da sessão (mesmo `thread_id`,
            via checkpointer `MemorySaver`). Cada entrada resume uma
            pergunta respondida com sucesso. Diferente de todos os
            outros campos deste estado — que são recalculados e
            sobrescritos a cada nova pergunta, para não "vazar" cenário,
            dados recuperados ou alertas de uma pergunta para outra —
            este campo usa o reducer `operator.add`, então a cada turno
            o LangGraph CONCATENA a nova entrada ao histórico já
            acumulado na sessão, em vez de substituí-lo. É esse
            comportamento que caracteriza a memória de curto prazo.
    """

    pergunta_usuario: str
    cenario_identificado: str | None
    dados_base_local: dict | None
    resposta_estruturada: dict | None
    alertas: list[str]
    risco_detectado: bool
    tentativas_geracao: int
    aguardando_aprovacao_humana: bool
    historico: Annotated[list[dict], add]
