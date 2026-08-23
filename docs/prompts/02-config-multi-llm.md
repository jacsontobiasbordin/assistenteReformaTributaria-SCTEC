# Prompt 02 — Configuração multi-LLM e requirements

- **Data de execução:** 2026-08-23
- **Branch:** chore/estrutura-inicial
- **Resultado obtido:** `requirements.txt` preenchido com as dependências
  iniciais do projeto; `.env.example` preenchido com as variáveis dos
  três provedores de LLM (Gemini, Anthropic, OpenAI); `app/config.py`
  com `Settings` (pydantic-settings) e validação da API key do provedor
  ativo; `app/llm/factory.py` com `get_llm()`, único ponto do projeto
  que conhece as classes específicas de cada provedor; README atualizado
  com as seções "Instalação e execução" e "Provedores de LLM
  suportados"; testes de configuração e fábrica de LLM (`tests/
  test_config.py`, `tests/test_llm_factory.py`) passando sem nenhuma API
  key real configurada. Nenhuma chamada real de rede foi feita.

## Prompt

```
Vamos configurar as dependências do projeto e a camada de acesso ao LLM,
seguindo a mesma abordagem multi-provedor usada no mini-projeto: o modelo
padrão é o Gemini 3 Flash, mas a aplicação deve ser capaz de rodar com
Claude (Anthropic) ou OpenAI trocando apenas variáveis de ambiente — nunca
código. NÃO implemente o grafo do LangGraph, os nós do agente nem a tool
de consulta local nesta etapa. O único código Python permitido aqui é
configuração (settings) e a fábrica de LLM, sem nenhuma chamada real de
rede.

Issue relacionada: #3

git checkout develop
git pull origin develop
git checkout -b chore/estrutura-inicial

Execute as etapas abaixo, nesta ordem:

1. PREENCHER O requirements.txt
   (o arquivo já existe, vazio, criado na Etapa 0 — substitua o conteúdo)
   Comentário no topo indicando que as versões serão fixadas após o
   primeiro teste de instalação, seguido de:
   - langgraph
   - langchain
   - langchain-core
   - langchain-google-genai
   - langchain-anthropic
   - langchain-openai
   - python-dotenv
   - pydantic
   - pydantic-settings
   - fastapi
   - uvicorn
   - pytest
   - pytest-cov
   - ruff

2. PREENCHER O .env.example
   (arquivo já existe, vazio, criado na Etapa 0)
     LLM_PROVIDER=gemini

     # Gemini (Google AI Studio) — provedor padrao do projeto
     GOOGLE_API_KEY=
     GEMINI_MODEL=gemini-3-flash

     # Claude (Anthropic) — usado se LLM_PROVIDER=anthropic
     ANTHROPIC_API_KEY=
     ANTHROPIC_MODEL=claude-sonnet-5

     # OpenAI — usado se LLM_PROVIDER=openai
     OPENAI_API_KEY=
     OPENAI_MODEL=gpt-5.1

     APP_ENV=development

3. CRIAR app/config.py
   Classe de configurações com `pydantic-settings` (`BaseSettings`):
   - llm_provider: Literal["gemini", "anthropic", "openai"] = "gemini"
   - google_api_key, gemini_model (default "gemini-3-flash")
   - anthropic_api_key, anthropic_model (default "claude-sonnet-5")
   - openai_api_key, openai_model (default "gpt-5.1")
   - app_env: str = "development"
   Adicione uma validação (validator do pydantic-settings ou função
   auxiliar) que verifica, ao carregar as configurações, se a API key do
   provedor selecionado em `llm_provider` está preenchida, levantando erro
   claro se não estiver. Exponha `get_settings()` com `lru_cache`. NÃO
   importe nem instancie nenhum client de LLM neste módulo.

4. CRIAR app/llm/factory.py
   Pacote `app/llm/` com `__init__.py`. Função `get_llm()` que:
   - Lê as configurações via `get_settings()`;
   - Com base em `llm_provider`, instancia e retorna o client
     correspondente (`ChatGoogleGenerativeAI`, `ChatAnthropic` ou
     `ChatOpenAI`), todos compatíveis com `BaseChatModel` do LangChain;
   - Levanta erro claro se `llm_provider` tiver valor não suportado.
   Este é o único arquivo do projeto que deve conhecer as classes
   específicas de cada provedor — qualquer nó do agente, em etapas
   futuras, deve chamar apenas `get_llm()`. NÃO chame `.invoke()` nem
   qualquer método que dispare requisição de rede nesta etapa.

5. ATUALIZAR O README.md
   Preencha a seção "Instalação e execução" (requisito 5.2 do documento
   oficial):
   - criação de ambiente virtual (`python -m venv .venv`);
   - `pip install -r requirements.txt`;
   - copiar `.env.example` para `.env` e preencher `GOOGLE_API_KEY`
     (com link para o Google AI Studio) — ou as variáveis do provedor
     escolhido, se for trocar `LLM_PROVIDER`;
   - como rodar os testes (`pytest tests/ -v`), adiantando o que será
     testado nesta etapa.
   Adicione também uma sub-seção curta "Provedores de LLM suportados"
   explicando a troca via `LLM_PROVIDER`, com Gemini 3 Flash como padrão
   recomendado por custo-benefício.

6. TESTES (sem nenhuma chamada real de API)
   - tests/test_config.py: com variáveis de ambiente de teste
     (monkeypatch/fixture), confirme que `get_settings()` carrega
     corretamente e que a ausência da API key do provedor ativo gera erro
     claro.
   - tests/test_llm_factory.py: para os 3 provedores (usando
     monkeypatch para setar `LLM_PROVIDER` e a respectiva API key de
     teste), confirme que `get_llm()` retorna uma instância da classe
     esperada, sem invocar `.invoke()`. Confirme também que um
     `LLM_PROVIDER` inválido levanta erro.
   Rode `pytest tests/ -v` e confirme que todos os testes passam sem
   nenhuma API key real configurada.

7. REGISTRAR O PROMPT
   Crie `docs/prompts/02-config-multi-llm.md` com o texto integral deste
   prompt, seguindo o padrão já estabelecido.

8. COMMITS SEMÂNTICOS
   1. build: adiciona requirements.txt com dependencias iniciais (#3)
   2. chore: preenche .env.example com variaveis multi-LLM (#3)
   3. chore: adiciona configuracao e fabrica multi-LLM (#3)
   4. docs: adiciona secao de instalacao e execucao ao README (#3)
   5. test: adiciona testes de configuracao e fabrica de LLM (#3)
   6. docs: registra o prompt 02 em docs/prompts/02-config-multi-llm.md (#3)

9. ENVIAR A BRANCH E ABRIR O PULL REQUEST
   git push -u origin chore/estrutura-inicial

   Mova o card #3 para **Em Revisão** no Project ao abrir o PR.

   Abra o PR direcionado para develop:
     Título: "chore: configuracao multi-LLM e requirements (#3)"
     Corpo:
       Closes #3

       ## Contexto
       Configura as dependencias do projeto e a camada de acesso ao LLM,
       com Gemini 3 Flash como provedor padrao e suporte a Claude/OpenAI
       via variavel de ambiente.

       ## O que foi feito
       - requirements.txt
       - .env.example preenchido
       - app/config.py (settings validadas por provedor)
       - app/llm/factory.py (get_llm())
       - README: instalacao/execucao + provedores suportados
       - Testes de configuracao e fabrica (sem chamada real de API)

       ## Fora do escopo deste PR
       - Nenhuma tool, no ou grafo do LangGraph foi implementado
       - Nenhuma chamada real a nenhum provedor de LLM foi feita

       ## Checklist
       - [x] Nenhuma chave de API real foi versionada
       - [x] Testes passam sem GOOGLE_API_KEY configurada
       - [x] Commits seguem o padrao semantico do projeto

10. VALIDAÇÃO FINAL
    Rode `pip install -r requirements.txt` em ambiente limpo e confirme
    instalação sem erros. Mostre `pytest tests/ -v` (sem nenhuma API key
    configurada) e confirme que app/config.py e app/llm/factory.py não
    fazem nenhuma chamada de rede.

Não implemente a tool de consulta local, o grafo do LangGraph ou qualquer
lógica de agente nesta etapa — isso começa na Etapa 3.
```
