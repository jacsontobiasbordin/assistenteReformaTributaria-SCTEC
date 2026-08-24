from functools import lru_cache
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    llm_provider: Literal["gemini", "anthropic", "openai"] = "gemini"

    google_api_key: str = ""
    gemini_model: str = "gemini-3-flash"

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-5"

    openai_api_key: str = ""
    openai_model: str = "gpt-5.1"

    app_env: str = "development"

    # Timeout explicito na chamada ao LLM (requisito 4.6, junto com o
    # retry limitado de app/agent/nodes.py::MAX_TENTATIVAS_GERACAO e o
    # fallback de app/agent/nodes.py::responder_erro_geracao).
    llm_timeout_seconds: int = 30

    @model_validator(mode="after")
    def _validar_api_key_do_provedor_ativo(self) -> "Settings":
        chave_por_provedor = {
            "gemini": ("GOOGLE_API_KEY", self.google_api_key),
            "anthropic": ("ANTHROPIC_API_KEY", self.anthropic_api_key),
            "openai": ("OPENAI_API_KEY", self.openai_api_key),
        }
        nome_variavel, valor = chave_por_provedor[self.llm_provider]
        if not valor:
            raise ValueError(
                f"LLM_PROVIDER='{self.llm_provider}' requer a variavel de "
                f"ambiente {nome_variavel} preenchida."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
