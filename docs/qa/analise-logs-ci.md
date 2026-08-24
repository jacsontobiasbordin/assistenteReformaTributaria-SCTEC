# Análise de logs do CI com IA

- **Execução analisada:** [run #2 do workflow CI](https://github.com/jacsontobiasbordin/assistenteReformaTributaria-SCTEC/actions/runs/32790431070), disparada pelo PR #31 (`feature/devops-anomalias` → `develop`).
- **Data:** 2026-08-24
- **Ferramenta:** Claude (Sonnet 5), dentro do Claude Code, sobre os logs reais baixados com `gh run view --log`.
- **Etapas analisadas:** "Lint (ruff)" (`docs/qa/logs-ci-lint.txt`) e "Testes (pytest)" (`docs/qa/logs-ci-testes.txt`), extraídas do log completo (`docs/qa/logs-ci-completo.txt`).
- **Prompt usado:**

```
Analise os logs abaixo, das etapas "lint" (ruff) e "testes" (pytest)
do pipeline de CI do projeto Assistente para Reforma Tributária.
Explique, em linguagem simples: (1) o que cada etapa verificou; (2) se
passou ou falhou, e por quê; (3) quaisquer avisos (warnings) que
apareçam e se merecem atenção; (4) o tempo de execução de cada etapa,
se estiver nos logs, e se parece razoável para o tamanho do projeto.

Log do lint:
<conteúdo de docs/qa/logs-ci-lint.txt>

Log dos testes:
<conteúdo de docs/qa/logs-ci-testes.txt>
```

## Resposta da IA (na íntegra)

### 1. O que cada etapa verificou

**Lint (ruff)** rodou `ruff check .` sobre todo o repositório — ou
seja, todo arquivo Python do projeto (`app/`, `tests/`, `scripts/`, se
existirem). O `ruff` verifica estilo, convenções de import, padrões
comuns de bug (código morto, comparações erradas, etc.) e formatação —
é uma checagem estática, não executa nenhum código do projeto.

**Testes (pytest)** rodou `pytest tests/ -v --cov=app --cov-report=term-missing`
— ou seja, toda a suíte de testes automatizados do projeto, com relatório
de cobertura de código (`--cov=app`) mostrando quais linhas de `app/`
foram de fato exercitadas pelos testes. É uma verificação dinâmica:
executa o código de verdade (grafo LangGraph completo, API FastAPI via
`TestClient`, configuração, etc.), só que com o LLM sempre mockado (ver
seção "O que passou").

### 2. Passou ou falhou, e por quê

Ambas as etapas **passaram**.

- Lint: `All checks passed!` (linha final de `logs-ci-lint.txt`) — nenhum
  problema de estilo ou padrão encontrado em nenhum arquivo do projeto.
- Testes: `48 passed in 6.10s` (última linha de `logs-ci-testes.txt`).
  Os 48 testes cobrem, entre outras coisas, o grafo completo (núcleo,
  paralelização, memória, segurança, observabilidade), a API (incluindo
  os testes E2E via `TestClient`) e a fábrica de LLM — todos passando
  sem nenhuma chave de API real configurada no runner do GitHub Actions
  (confirmado pela ausência de qualquer erro de autenticação/rede nos
  logs; os testes mockam `get_llm()`).

O relatório de cobertura junto ao resultado mostra `TOTAL 393 22 94%` —
94% das linhas de `app/` foram exercitadas pelos testes, um número alto
para um projeto deste tamanho. As linhas não cobertas
(`app/agent/nodes.py` linhas 121, 160-165, 237-241, 246;
`app/observability/decorators.py` linhas 60-89;
`app/web/main.py` linhas 69-74; mais duas linhas isoladas em
`app/llm/factory.py` e `app/tools/local_kb.py`) são majoritariamente
ramos de tratamento de exceção (caminhos de erro que não são
propositalmente disparados pelos testes felizes) — não sugerem, por si
só, um problema.

### 3. Avisos (warnings) e se merecem atenção

O log de testes analisado aqui **não mostra nenhum warning do
pytest/Python** — diferente de execuções locais deste mesmo projeto
(em ambiente Windows/Python 3.14), que emitem um
`DeprecationWarning` do pacote `google.genai` sobre `_UnionGenericAlias`.
A ausência do warning aqui provavelmente se deve a uma versão diferente
resolvida pelo `pip` no runner (Python 3.11.16, Ubuntu) em relação ao
ambiente de desenvolvimento local — como `requirements.txt` não fixa
versões, isso é esperado e não é, por si só, motivo de preocupação,
mas é um sinal de que **fixar versões** (`pip freeze` → `requirements.txt`
com `==`) traria mais previsibilidade entre ambientes.

Fora do log de testes, mas presente no log completo do run
(`logs-ci-completo.txt`), há um aviso de nível de plataforma, não do
projeto: `Node.js 20 is deprecated. The following actions target
Node.js 20 but are being forced to run on Node.js 24: actions/checkout@v4,
actions/setup-python@v5`. Isso não é um problema do código do projeto —
é um aviso do GitHub Actions sobre as *actions* usadas (`checkout@v4`,
`setup-python@v5`) ainda declararem suporte a uma versão de runtime do
Node.js que está sendo descontinuada na plataforma. Não quebra o
pipeline agora (o GitHub força a execução em Node 24 mesmo assim), mas
merece atenção futura: atualizar para `actions/checkout@v5`/a versão
mais recente de `setup-python` quando disponível evita que o pipeline
pare de funcionar quando o suporte a Node 20 for removido de fato.

### 4. Tempo de execução de cada etapa

Os timestamps de cada linha do log (formato ISO 8601 com milissegundos)
permitem medir cada etapa:

| Etapa | Duração aproximada |
|---|---|
| Instalar dependências (`pip install`) | ~16,4s |
| Lint (ruff) | ~0,02s |
| Testes (pytest, 48 testes + cobertura) | 6,10s (reportado pelo próprio pytest) |
| Build/validação (import da aplicação) | ~0,85s |
| **Pipeline completo** (do "Set up job" ao "Complete job") | ~28,5s |

Para o tamanho atual do projeto (48 testes, ~390 linhas de código de
aplicação em `app/`), esses números são **bastante razoáveis** — a
maior fatia do tempo (mais da metade do pipeline) é a instalação de
dependências pesadas (`langgraph`, `langchain` e seus três provedores
de LLM), não o código do projeto em si. O lint é essencialmente
instantâneo, e os testes rodam em segundos porque nenhum deles faz
chamada de rede real (tudo mockado). Se o projeto crescer
significativamente em número de testes ou dependências, vale a pena
monitorar o tempo de instalação — uma opção futura seria cachear as
dependências do `pip` entre execuções (`actions/setup-python` já
oferece isso via o parâmetro `cache: "pip"`), o que reduziria os ~16s
de instalação nas execuções seguintes.
