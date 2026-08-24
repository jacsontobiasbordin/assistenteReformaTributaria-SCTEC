"""Trilha de auditoria do agente.

Segundo sinal de observabilidade (o primeiro e o log estruturado em
`app/observability/logging_config.py`), correlacionado ao log pelo mesmo
`execution_id`. Cada chamada de `registrar_auditoria` adiciona uma linha
a `docs/evidencias/auditoria.jsonl`.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

_ARQUIVO_AUDITORIA = (
    Path(__file__).resolve().parent.parent.parent
    / "docs"
    / "evidencias"
    / "auditoria.jsonl"
)


def registrar_auditoria(
    execution_id: str,
    node: str,
    status: str,
    duracao_ms: float,
    decisao: str,
    erro: str | None = None,
) -> None:
    entrada = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "execution_id": execution_id,
        "node": node,
        "status": status,
        "duracao_ms": duracao_ms,
        "decisao": decisao,
        "erro": erro,
    }

    _ARQUIVO_AUDITORIA.parent.mkdir(parents=True, exist_ok=True)
    with _ARQUIVO_AUDITORIA.open("a", encoding="utf-8") as arquivo:
        arquivo.write(json.dumps(entrada, ensure_ascii=False, default=str) + "\n")
