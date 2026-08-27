"""Configuracao de logging estruturado do agente.

Todo registro do logger "reformatax" e emitido como uma linha JSON no
stdout, correlacionavel com a trilha de auditoria (`app/observability/
audit.py`) pelo mesmo `execution_id`. `configurar_logging()` deve ser
chamada uma unica vez no ponto de entrada da aplicacao (Etapa 9); nesta
etapa, e chamada no inicio dos testes/scripts que exercitam o grafo.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone

_CAMPOS_PADRAO_LOG_RECORD = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
    "taskName",
}


class _FormatadorJson(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        registro = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        campos_extras = {
            chave: valor
            for chave, valor in record.__dict__.items()
            if chave not in _CAMPOS_PADRAO_LOG_RECORD and chave not in registro
        }
        registro.update(campos_extras)

        return json.dumps(registro, ensure_ascii=False, default=str)


def configurar_logging(nivel: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger("reformatax")
    logger.setLevel(nivel)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(_FormatadorJson())
        logger.addHandler(handler)

    return logger
