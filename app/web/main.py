"""API local que expoe o grafo completo do agente (Etapas 4 a 8).

Formato de interface aceito pelo requisito 5.1. `/` serve a interface web
estatica (Etapa 9.1, app/web/static/); o Swagger UI automatico do
FastAPI (rota /docs) continua disponivel como alternativa.
"""

from __future__ import annotations

import logging
import uuid
from functools import lru_cache

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from app.agent.graph import build_graph, thread_config
from app.observability.logging_config import configurar_logging
from app.tools.local_kb import listar_cenarios_disponiveis
from app.tools.notificacao import (
    NotificacaoFalhouError,
    NotificacaoInput,
    disparar_notificacao,
)
from app.web.schemas import (
    AnaliseResponse,
    ConfirmarNotificacaoRequest,
    ConfirmarNotificacaoResponse,
    PerguntaRequest,
)

configurar_logging()
logger = logging.getLogger("reformatax")

app = FastAPI(
    title="Assistente para Reforma Tributaria",
    description=(
        "API local que expoe o grafo do agente (nucleo, paralelizacao, "
        "memoria de sessao, seguranca/aprovacao humana e observabilidade)."
    ),
)


@lru_cache
def get_graph():
    return build_graph()


@app.get("/api/cenarios")
def listar_cenarios() -> list[str]:
    return listar_cenarios_disponiveis()


@app.post("/api/analisar", response_model=AnaliseResponse)
def analisar(payload: PerguntaRequest) -> AnaliseResponse:
    session_id = payload.session_id or str(uuid.uuid4())

    # Estado de entrada: reseta explicitamente todos os campos que nao
    # devem persistir entre perguntas da mesma sessao. O checkpointer
    # (MemorySaver, Etapa 6) restaura o estado anterior da sessao — sem
    # esse reset, alertas/risco/aprovacao de uma pergunta "vazariam" para
    # a proxima. So `historico` deve realmente acumular, e por isso nao
    # aparece aqui: fica a cargo do reducer `operator.add` do proprio
    # AgentState, alimentado pelo node registrar_historico.
    estado = {
        "pergunta_usuario": payload.pergunta,
        "cenario_identificado": None,
        "dados_base_local": None,
        "resposta_estruturada": None,
        "alertas": [],
        "tentativas_geracao": 0,
        "risco_detectado": False,
        "aguardando_aprovacao_humana": False,
        "execution_id": None,
    }

    try:
        resultado = get_graph().invoke(estado, config=thread_config(session_id))
    except Exception:
        logger.exception(
            "Falha inesperada ao processar a pergunta.",
            extra={"session_id": session_id},
        )
        raise HTTPException(
            status_code=500,
            detail="Erro inesperado ao processar a pergunta. Tente novamente.",
        ) from None

    return AnaliseResponse(
        session_id=session_id,
        cenario_identificado=resultado.get("cenario_identificado"),
        resposta_estruturada=resultado.get("resposta_estruturada"),
        alertas=resultado.get("alertas", []),
        aguardando_aprovacao_humana=resultado.get("aguardando_aprovacao_humana", False),
    )


@app.post("/api/confirmar-notificacao", response_model=ConfirmarNotificacaoResponse)
def confirmar_notificacao(
    payload: ConfirmarNotificacaoRequest,
) -> ConfirmarNotificacaoResponse:
    """Dispara a notificacao do n8n apos confirmacao humana (Etapa 7).

    Rota deterministica e simples: NAO chama get_llm() nem reexecuta o
    grafo — so le o estado ja calculado da sessao e, se houver
    confirmacao pendente, aciona a ferramenta visual (n8n) como apoio a
    orquestracao. A logica principal continua na aplicacao.
    """
    estado = get_graph().get_state(thread_config(payload.session_id)).values

    if not estado.get("aguardando_aprovacao_humana"):
        raise HTTPException(
            status_code=400,
            detail="Nao ha confirmacao pendente para esta sessao.",
        )

    resposta_estruturada = estado.get("resposta_estruturada") or {}
    notificacao_input = NotificacaoInput(
        cenario=estado.get("cenario_identificado") or "",
        resumo=resposta_estruturada.get("cenario_analisado", ""),
        session_id=payload.session_id,
    )

    try:
        resultado = disparar_notificacao(notificacao_input)
    except NotificacaoFalhouError as erro:
        logger.exception(
            "Falha ao notificar o n8n apos confirmacao humana.",
            extra={"session_id": payload.session_id},
        )
        raise HTTPException(status_code=502, detail=str(erro)) from None

    return ConfirmarNotificacaoResponse(
        status="notificacao_enviada", mensagem=resultado.mensagem
    )


# Montado por ultimo, depois de todas as rotas /api/*, para nao
# conflitar com elas (StaticFiles com html=True serve index.html em "/").
app.mount("/", StaticFiles(directory="app/web/static", html=True), name="static")
