from pydantic import BaseModel, Field


class PerguntaRequest(BaseModel):
    pergunta: str = Field(max_length=1000)
    session_id: str | None = Field(
        default=None,
        description="Id da sessao (thread_id do checkpointer). Se omitido, "
        "uma nova sessao e criada e o id e retornado na resposta, para o "
        "cliente reusar em perguntas de acompanhamento na mesma sessao.",
    )


class AnaliseResponse(BaseModel):
    session_id: str
    cenario_identificado: str | None
    resposta_estruturada: dict | None
    alertas: list[str]
    aguardando_aprovacao_humana: bool


class ConfirmarNotificacaoRequest(BaseModel):
    session_id: str


class ConfirmarNotificacaoResponse(BaseModel):
    status: str
    mensagem: str
