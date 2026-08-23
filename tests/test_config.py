import pytest

from app.config import Settings, get_settings


def test_get_settings_carrega_provedor_gemini(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GOOGLE_API_KEY", "chave-de-teste")
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.llm_provider == "gemini"
    assert settings.google_api_key == "chave-de-teste"
    assert settings.gemini_model == "gemini-3-flash"


def test_get_settings_e_cacheado(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GOOGLE_API_KEY", "chave-de-teste")
    get_settings.cache_clear()

    assert get_settings() is get_settings()


def test_provedor_ativo_sem_api_key_gera_erro_claro(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    get_settings.cache_clear()

    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
        Settings()


def test_provedor_invalido_gera_erro(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "provedor-inexistente")
    get_settings.cache_clear()

    with pytest.raises(Exception):
        Settings()
