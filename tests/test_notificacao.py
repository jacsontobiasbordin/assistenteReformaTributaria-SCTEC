import httpx
import pytest

from app.config import get_settings
from app.tools.notificacao import (
    NotificacaoFalhouError,
    NotificacaoInput,
    disparar_notificacao,
)

_URL_TESTE = "http://n8n-teste.local/webhook/reformatax-confirmacao"


@pytest.fixture(autouse=True)
def configurar_settings_de_teste(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "chave-de-teste")
    monkeypatch.setenv("N8N_WEBHOOK_URL", _URL_TESTE)
    monkeypatch.setenv("N8N_TIMEOUT_SECONDS", "5")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_disparar_notificacao_com_resposta_de_sucesso_retorna_resultado(monkeypatch):
    resposta_mock = httpx.Response(
        200,
        json={
            "status": "notificacao_registrada",
            "mensagem": "[ReformaTax] Analise aprovada - cenario: calculo_impostos",
        },
        request=httpx.Request("POST", _URL_TESTE),
    )
    monkeypatch.setattr(
        "app.tools.notificacao.httpx.post", lambda *args, **kwargs: resposta_mock
    )

    resultado = disparar_notificacao(
        NotificacaoInput(
            cenario="calculo_impostos", resumo="resumo de teste", session_id="sessao-1"
        )
    )

    assert resultado.status == "notificacao_registrada"
    assert "ReformaTax" in resultado.mensagem


def test_disparar_notificacao_com_timeout_levanta_notificacao_falhou_error(monkeypatch):
    def levantar_timeout(*args, **kwargs):
        raise httpx.TimeoutException("timed out")

    monkeypatch.setattr("app.tools.notificacao.httpx.post", levantar_timeout)

    with pytest.raises(NotificacaoFalhouError):
        disparar_notificacao(
            NotificacaoInput(cenario="calculo_impostos", resumo="x", session_id="sessao-2")
        )


def test_disparar_notificacao_com_erro_de_conexao_levanta_notificacao_falhou_error(
    monkeypatch,
):
    def levantar_erro_conexao(*args, **kwargs):
        raise httpx.ConnectError("connection refused")

    monkeypatch.setattr("app.tools.notificacao.httpx.post", levantar_erro_conexao)

    with pytest.raises(NotificacaoFalhouError):
        disparar_notificacao(
            NotificacaoInput(cenario="calculo_impostos", resumo="x", session_id="sessao-3")
        )
