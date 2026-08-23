from pydantic import BaseModel, field_validator

CENARIOS_VALIDOS = {"cadastro_produtos", "emissao_nota_fiscal", "calculo_impostos"}


class ConsultaCenarioInput(BaseModel):
    cenario: str

    @field_validator("cenario")
    @classmethod
    def validar_cenario_suportado(cls, valor: str) -> str:
        if valor not in CENARIOS_VALIDOS:
            aceitos = ", ".join(sorted(CENARIOS_VALIDOS))
            raise ValueError(
                f"cenario '{valor}' nao suportado. Valores aceitos: {aceitos}."
            )
        return valor


class RespostaCenarioLocal(BaseModel):
    resumo: str
    pontos_reforma_relacionados: list[str]
    impactos_tecnicos_erp: list[str]
    pontos_atencao: list[str]
    checklist_tecnico: list[str]
