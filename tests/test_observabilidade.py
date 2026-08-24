import json
import logging
from unittest.mock import MagicMock

from app.agent.graph import build_graph, thread_config
from app.agent.schemas import AnaliseEstruturada
from app.config import get_settings
from app.observability.audit import _ARQUIVO_AUDITORIA
from app.observability.logging_config import configurar_logging

_ANALISE_VALIDA = AnaliseEstruturada(
    cenario_analisado="cadastro_produtos",
    pontos_reforma_relacionados=["ponto 1"],
    impactos_tecnicos_erp=["impacto 1"],
    pontos_atencao=["atencao 1"],
    checklist_tecnico=["item 1"],
)

_NODES_DO_CAMINHO_PRINCIPAL = {
    "validar_entrada",
    "identificar_cenario",
    "consultar_base_local",
    "triagem_seguranca",
    "avaliar_seguranca",
    "gerar_analise",
    "validar_resposta",
    "registrar_historico",
}


def _estado_inicial(pergunta: str) -> dict:
    return {
        "pergunta_usuario": pergunta,
        "cenario_identificado": None,
        "dados_base_local": None,
        "resposta_estruturada": None,
        "alertas": [],
        "risco_detectado": False,
        "tentativas_geracao": 0,
        "aguardando_aprovacao_humana": False,
        "historico": [],
    }


def _mockar_llm(monkeypatch, respostas):
    llm_estruturado = MagicMock()
    llm_estruturado.invoke.side_effect = respostas

    llm = MagicMock()
    llm.with_structured_output.return_value = llm_estruturado

    monkeypatch.setattr("app.agent.nodes.get_llm", lambda: llm)
    return llm_estruturado


def _ler_auditoria() -> list[dict]:
    with _ARQUIVO_AUDITORIA.open(encoding="utf-8") as arquivo:
        return [json.loads(linha) for linha in arquivo]


def test_execucao_completa_gera_logs_para_multiplos_nodes_com_mesmo_execution_id(
    monkeypatch, caplog
):
    _mockar_llm(monkeypatch, [_ANALISE_VALIDA])
    configurar_logging()
    caplog.set_level(logging.INFO, logger="reformatax")

    resultado = build_graph().invoke(
        _estado_inicial("Como devo cadastrar o NCM dos meus produtos?"),
        config=thread_config("teste-observabilidade-logs"),
    )
    execution_id = resultado["execution_id"]

    registros_desta_execucao = [
        registro
        for registro in caplog.records
        if getattr(registro, "execution_id", None) == execution_id
    ]
    nodes_logados = {registro.node for registro in registros_desta_execucao}

    assert execution_id
    assert len(registros_desta_execucao) >= 5
    assert _NODES_DO_CAMINHO_PRINCIPAL <= nodes_logados


def test_execucao_completa_gera_auditoria_correlacionada_com_os_logs(
    monkeypatch, caplog
):
    _mockar_llm(monkeypatch, [_ANALISE_VALIDA])
    configurar_logging()
    caplog.set_level(logging.INFO, logger="reformatax")

    resultado = build_graph().invoke(
        _estado_inicial("Como devo cadastrar o NCM dos meus produtos?"),
        config=thread_config("teste-observabilidade-auditoria"),
    )
    execution_id = resultado["execution_id"]

    entradas_desta_execucao = [
        entrada for entrada in _ler_auditoria() if entrada["execution_id"] == execution_id
    ]
    nodes_auditados = {entrada["node"] for entrada in entradas_desta_execucao}
    execution_ids_dos_logs = {
        registro.execution_id
        for registro in caplog.records
        if hasattr(registro, "execution_id")
    }

    assert len(entradas_desta_execucao) >= 5
    assert _NODES_DO_CAMINHO_PRINCIPAL <= nodes_auditados
    # prova de correlacao: o mesmo execution_id aparece nos dois sinais
    assert execution_id in execution_ids_dos_logs
    assert all(
        isinstance(entrada["duracao_ms"], (int, float))
        for entrada in entradas_desta_execucao
    )


def test_client_llm_e_instanciado_com_timeout_configurado(monkeypatch):
    from app.llm import factory

    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GOOGLE_API_KEY", "chave-de-teste")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "7")
    get_settings.cache_clear()

    mock_chat_google = MagicMock()
    monkeypatch.setattr("langchain_google_genai.ChatGoogleGenerativeAI", mock_chat_google)

    factory.get_llm()
    get_settings.cache_clear()

    _, kwargs_da_chamada = mock_chat_google.call_args
    assert kwargs_da_chamada["timeout"] == 7
