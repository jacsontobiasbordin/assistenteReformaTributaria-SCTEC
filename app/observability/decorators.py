"""Decorator de instrumentacao dos nodes do grafo.

`observar()` aplica os dois sinais de observabilidade (log estruturado +
trilha de auditoria) a um node existente, correlacionando-os pelo mesmo
`execution_id`, sem alterar a logica de negocio original do node.
"""

from __future__ import annotations

import functools
import logging
import time
import uuid
from collections.abc import Callable

from app.observability.audit import registrar_auditoria

logger = logging.getLogger("reformatax")


def _resumir_decisao(resultado: dict) -> str:
    if "risco_detectado" in resultado:
        return f"risco_detectado={resultado['risco_detectado']}"
    if "cenario_identificado" in resultado:
        return f"cenario_identificado={resultado['cenario_identificado']}"
    if resultado.get("aguardando_aprovacao_humana"):
        return "aprovacao_humana_solicitada"
    if "dados_base_local" in resultado:
        return (
            "dados_base_local_encontrados"
            if resultado["dados_base_local"] is not None
            else "dados_base_local_indisponivel"
        )
    if "historico" in resultado:
        return "historico_atualizado"
    if "tentativas_geracao" in resultado:
        return (
            "analise_gerada_com_sucesso"
            if resultado.get("resposta_estruturada") is not None
            else "falha_na_geracao_llm"
        )
    if "resposta_estruturada" in resultado:
        return "resposta_definida"
    if resultado.get("alertas"):
        return "alerta_registrado"
    return "sem_decisao_relevante"


def observar(nome_node: str) -> Callable[[Callable[[dict], dict]], Callable[[dict], dict]]:
    def decorador(funcao_node: Callable[[dict], dict]) -> Callable[[dict], dict]:
        @functools.wraps(funcao_node)
        def envolvida(state: dict) -> dict:
            execution_id_existente = state.get("execution_id")
            execution_id = execution_id_existente or str(uuid.uuid4())
            gerou_execution_id_agora = execution_id_existente is None

            inicio = time.perf_counter()
            try:
                resultado = dict(funcao_node(state))
            except Exception as erro:  # noqa: BLE001 - rede de seguranca extra do node
                duracao_ms = (time.perf_counter() - inicio) * 1000
                mensagem_erro = str(erro)

                logger.error(
                    "node falhou com excecao nao tratada",
                    extra={
                        "execution_id": execution_id,
                        "node": nome_node,
                        "status": "erro",
                        "duracao_ms": duracao_ms,
                        "erro": mensagem_erro,
                    },
                )
                registrar_auditoria(
                    execution_id=execution_id,
                    node=nome_node,
                    status="erro",
                    duracao_ms=duracao_ms,
                    decisao="excecao_nao_tratada",
                    erro=mensagem_erro,
                )

                resultado_erro = {
                    "alertas": list(state.get("alertas", []))
                    + [f"Erro inesperado no node '{nome_node}'."]
                }
                if gerou_execution_id_agora:
                    resultado_erro["execution_id"] = execution_id
                return resultado_erro

            duracao_ms = (time.perf_counter() - inicio) * 1000
            decisao = _resumir_decisao(resultado)

            logger.info(
                "node executado",
                extra={
                    "execution_id": execution_id,
                    "node": nome_node,
                    "status": "sucesso",
                    "duracao_ms": duracao_ms,
                    "decisao": decisao,
                },
            )
            registrar_auditoria(
                execution_id=execution_id,
                node=nome_node,
                status="sucesso",
                duracao_ms=duracao_ms,
                decisao=decisao,
            )

            if gerou_execution_id_agora:
                resultado.setdefault("execution_id", execution_id)
            return resultado

        return envolvida

    return decorador
