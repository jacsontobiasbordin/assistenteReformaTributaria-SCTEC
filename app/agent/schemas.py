from pydantic import BaseModel, Field


class AnaliseEstruturada(BaseModel):
    cenario_analisado: str = Field(
        description="Nome do cenario analisado (ex.: cadastro de produtos, "
        "emissao de nota fiscal, calculo de IBS/CBS)."
    )
    pontos_reforma_relacionados: list[str] = Field(
        description="Pontos da Reforma Tributaria (IBS/CBS) relacionados a "
        "pergunta do usuario, com base no contexto fornecido."
    )
    impactos_tecnicos_erp: list[str] = Field(
        description="Impactos tecnicos concretos no ERP decorrentes desses "
        "pontos da reforma."
    )
    pontos_atencao: list[str] = Field(
        description="Riscos e pontos de atencao que a equipe tecnica deve "
        "observar ao tratar esse cenario."
    )
    checklist_tecnico: list[str] = Field(
        description="Lista de itens praticos e acionaveis para a equipe "
        "tecnica revisar ou implementar."
    )
