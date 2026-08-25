"""Tool de disparo de notificacao apos aprovacao humana (Etapa 7).

Chama o webhook do fluxo n8n local (n8n/fluxo-aprovacao-reformatax.json)
depois que um humano aprova uma analise pendente (cenario de calculo de
impostos). A logica de negocio (o que aprovar, quando aprovar) continua
inteiramente na aplicacao Python — o n8n so recebe o payload via webhook
e produz uma saida observavel (registro na aba "Executions" do n8n +
resposta HTTP), sem nenhuma decisao de negocio da propria ferramenta
visual.
"""

from __future__ import annotations

import httpx
from pydantic import BaseModel

from app.config import get_settings


class NotificacaoInput(BaseModel):
    cenario: str
    resumo: str
    session_id: str


class NotificacaoResultado(BaseModel):
    status: str
    mensagem: str


class NotificacaoFalhouError(Exception):
    pass


def disparar_notificacao(payload: NotificacaoInput) -> NotificacaoResultado:
    """Dispara o webhook do n8n. Nao trava o fluxo da aplicacao: a
    aprovacao ja foi registrada no estado do grafo antes desta chamada
    — se a notificacao falhar (timeout, erro de conexao, erro HTTP), o
    chamador recebe NotificacaoFalhouError e decide como informar o
    usuario, mas a aprovacao em si nao e desfeita.
    """
    settings = get_settings()

    try:
        resposta = httpx.post(
            settings.n8n_webhook_url,
            json=payload.model_dump(),
            timeout=settings.n8n_timeout_seconds,
        )
        resposta.raise_for_status()
    except httpx.HTTPError as erro:
        raise NotificacaoFalhouError(
            f"Nao foi possivel notificar o n8n em "
            f"'{settings.n8n_webhook_url}': {erro}"
        ) from erro

    dados = resposta.json()
    return NotificacaoResultado(
        status=dados.get("status", "desconhecido"),
        mensagem=dados.get("mensagem", ""),
    )
