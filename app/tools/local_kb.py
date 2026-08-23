import json
from functools import lru_cache
from pathlib import Path

from app.tools.schemas import ConsultaCenarioInput, RespostaCenarioLocal

_CAMINHO_BASE_LOCAL = Path(__file__).resolve().parent.parent.parent / "data" / "reforma_tributaria_erp.json"


class CenarioNaoEncontradoError(Exception):
    pass


class BaseLocalIndisponivelError(Exception):
    pass


@lru_cache
def carregar_base() -> dict:
    try:
        with _CAMINHO_BASE_LOCAL.open(encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise BaseLocalIndisponivelError(
            f"Nao foi possivel carregar a base local de conhecimento em "
            f"'{_CAMINHO_BASE_LOCAL}'."
        ) from e


def consultar_cenario(payload: ConsultaCenarioInput) -> RespostaCenarioLocal:
    """Consulta um cenario na base local.

    A validacao do parametro `cenario` (valor dentro do conjunto suportado)
    ja aconteceu na construcao de `payload: ConsultaCenarioInput`, antes
    desta funcao ser chamada.
    """
    base = carregar_base()
    dados_cenario = base.get("cenarios", {}).get(payload.cenario)

    if dados_cenario is None:
        raise CenarioNaoEncontradoError(
            f"Cenario '{payload.cenario}' nao encontrado na base local."
        )

    return RespostaCenarioLocal(
        resumo=dados_cenario["resumo"],
        pontos_reforma_relacionados=dados_cenario["pontos_reforma_relacionados"],
        impactos_tecnicos_erp=dados_cenario["impactos_tecnicos_erp"],
        pontos_atencao=dados_cenario["pontos_atencao"],
        checklist_tecnico=dados_cenario["checklist_tecnico"],
    )


def listar_cenarios_disponiveis() -> list[str]:
    return list(carregar_base()["cenarios"].keys())
