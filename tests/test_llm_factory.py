import pytest

from app.config import get_settings
from app.llm.factory import get_llm


@pytest.fixture(autouse=True)
def limpar_cache_settings():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_get_llm_retorna_chat_google_generative_ai(monkeypatch):
    from langchain_google_genai import ChatGoogleGenerativeAI

    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GOOGLE_API_KEY", "chave-de-teste-google")

    llm = get_llm()

    assert isinstance(llm, ChatGoogleGenerativeAI)


def test_get_llm_retorna_chat_anthropic(monkeypatch):
    from langchain_anthropic import ChatAnthropic

    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "chave-de-teste-anthropic")

    llm = get_llm()

    assert isinstance(llm, ChatAnthropic)


def test_get_llm_retorna_chat_openai(monkeypatch):
    from langchain_openai import ChatOpenAI

    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "chave-de-teste-openai")

    llm = get_llm()

    assert isinstance(llm, ChatOpenAI)


def test_get_llm_com_provedor_invalido_levanta_erro(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "provedor-inexistente")
    monkeypatch.setenv("GOOGLE_API_KEY", "chave-de-teste-google")

    with pytest.raises(Exception):
        get_llm()
