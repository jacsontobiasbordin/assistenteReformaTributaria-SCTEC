# Assistente para Reforma Tributária

Assistente baseado em agentes para apoiar consultas sobre a Reforma Tributária brasileira.

## Status: em desenvolvimento — estrutura inicial

## Descrição da solução

**Nome do projeto:** Assistente para Reforma Tributária.

**Problema resolvido:** empresas que usam ERP precisam revisar cadastros,
cálculos e documentos fiscais por causa da Reforma Tributária (IBS/CBS).
Times de desenvolvimento e analistas de sistemas têm dificuldade em
identificar rapidamente o que precisa mudar no sistema diante do volume
de mudanças trazidas pela reforma.

**Público:** desenvolvedores e analistas de sistemas que mantêm ERPs.

**Objetivo:** dado um dos três cenários suportados (cadastro de produtos,
emissão de nota fiscal, cálculo de IBS/CBS), descritos em linguagem
natural pelo usuário, o assistente retorna uma resposta estruturada
identificando o cenário, os pontos da reforma relacionados, os impactos
técnicos no ERP, os pontos de atenção e um checklist técnico.

**Valor entregue:** apoio técnico inicial para priorizar o que revisar no
sistema — **não** um parecer jurídico/fiscal definitivo.

> Este projeto é uma evolução do mini-projeto desenvolvido no módulo
> anterior, reaproveitando o grafo base, a tool de consulta à base local e
> a configuração multi-LLM, e adicionando paralelização, triagem de
> segurança, aprovação humana, memória de sessão, observabilidade,
> QA/DevOps com IA e automação low-code. Detalhes completos em
> [docs/escopo.md](docs/escopo.md).

## Classificação e arquitetura

**Classificação: sistema híbrido.**

A maior parte do fluxo é workflow determinístico (validação de entrada,
identificação de cenário por regras, triagem de segurança, controle de
retry e condição de parada), e um único nó é agêntico: o LLM decide como
sintetizar a resposta final a partir do contexto recuperado — mas nunca
decide sozinho sobre autonomia, segurança ou quais ferramentas executar;
isso é sempre regra determinística da aplicação.

**Justificativa:** um domínio fiscal/tributário exige rastreabilidade e
previsibilidade. Deixar decisões de segurança/roteamento a cargo do
modelo aumentaria o risco sem necessidade real, já que os cenários
suportados são bem definidos. Ver detalhamento completo em
[docs/escopo.md](docs/escopo.md).

### Diagrama de arquitetura

O diagrama abaixo representa o fluxo completo planejado para o projeto
(ainda não implementado nesta etapa — a implementação ocorre nas Etapas 2
a 12):

```mermaid
flowchart TD
    A[validar_entrada] -->|entrada invalida| Z1[responder_entrada_invalida] --> END1[FIM]
    A -->|entrada valida| B[identificar_cenario]
    B -->|fora de escopo| Z2[responder_fora_de_escopo] --> END2[FIM]
    B -->|cenario valido| C[consultar_base_local]
    B -->|cenario valido| D[triagem_seguranca]
    C --> E[gerar_analise]
    D --> E
    E --> F[validar_resposta]
    F -->|invalida, tentativas < limite| E
    F -->|invalida, limite atingido| Z3[responder_erro_geracao] --> END3[FIM]
    F -->|valida, sem risco| END4[FIM: resposta ao usuario]
    F -->|valida, risco/acao sensivel| G[solicitar_aprovacao_humana]
    G -->|aprovado| H[disparar_notificacao_low_code] --> END5[FIM]
    G -->|nao aprovado/pendente| END6[FIM: resposta com alerta pendente]
```

A partir da Etapa 4, o núcleo determinístico deste diagrama já está
implementado em código: o estado compartilhado tipado está em
[app/agent/state.py](app/agent/state.py) (`AgentState`), os nodes
`validar_entrada`, `identificar_cenario`, `consultar_base_local`,
`responder_entrada_invalida` e `responder_fora_de_escopo` estão em
[app/agent/nodes.py](app/agent/nodes.py), e a montagem do grafo (nodes,
entry point e arestas condicionais) está em
[app/agent/graph.py](app/agent/graph.py) (`build_graph()`). Por ora, o
grafo termina em `consultar_base_local`; os demais nodes do diagrama
(`triagem_seguranca`, `gerar_analise`, `validar_resposta`,
`solicitar_aprovacao_humana`, `disparar_notificacao_low_code`) entram
nas próximas etapas.

Todos os nodes implementados até aqui são **100% determinísticos**
(regras da aplicação, sem LLM). O único node agêntico de todo o projeto
é `gerar_analise` (introduzido na Etapa 5), que usa o LLM apenas para
sintetizar a resposta final a partir do contexto já recuperado — nunca
para decidir roteamento, autonomia ou execução de ferramentas.

A partir da Etapa 5, o grafo cumpre todos os requisitos de arquitetura
agêntica exigidos:

- **Execução sequencial** ✓ — `validar_entrada → identificar_cenario → … → validar_resposta`;
- **Ramificação condicional** ✓ — entrada inválida, fora de escopo e o
  resultado de `validar_resposta` roteiam para nodes diferentes;
- **Paralelização simples** ✓ — `consultar_base_local` e
  `triagem_seguranca` rodam em paralelo (fan-out/fan-in na mesma
  superstep do LangGraph), a partir de `identificar_cenario`;
- **Condição de parada explícita** ✓ — `gerar_analise` nunca é chamado
  mais que `MAX_TENTATIVAS_GERACAO` (2) vezes para a mesma pergunta;
  esgotado o limite, o grafo encerra em `responder_erro_geracao`;
- **Separação decisão do modelo / regra determinística** ✓ — apenas
  `gerar_analise` usa o LLM (via `get_llm()`); a triagem de segurança
  desta etapa é uma detecção inicial simples por padrões de texto, sem
  LLM, que será refinada na Etapa 7.

## Contexto e memória

A memória de curto prazo entre perguntas da mesma sessão é implementada
com o **checkpointer nativo do LangGraph** (`MemorySaver`,
`langgraph.checkpoint.memory`), sem RAG e sem banco de dados persistente
— adequado ao domínio, já que o histórico só precisa durar a conversa,
não anos.

- **Identificação da sessão:** cada conversa é um `thread_id` distinto.
  O grafo é compilado com `grafo.compile(checkpointer=MemorySaver())`
  (`app/agent/graph.py`), e cada chamada usa
  `.invoke(estado, config=thread_config(thread_id))`, onde
  `thread_config()` monta `{"configurable": {"thread_id": ...}}`.
- **O que é persistido:** apenas o campo `historico` do `AgentState`, que
  usa um reducer (`Annotated[list[dict], operator.add]`) para **acumular**
  entre turnos, em vez de ser sobrescrito como os demais campos do
  estado (cenário, dados recuperados e alertas são recalculados a cada
  pergunta, para não vazar de uma pergunta para outra). Uma entrada só é
  gravada no caminho de sucesso — pelo node `registrar_historico` —
  porque perguntas inválidas ou fora de escopo não agregam contexto útil
  para perguntas futuras na mesma sessão.
- **Como é usado:** em `gerar_analise`, se a sessão já tiver histórico,
  as 1-2 últimas entradas são incluídas como contexto adicional na
  mensagem enviada ao LLM, antes da pergunta atual. Isso é o que torna a
  memória efetivamente **usada** pela aplicação, e não apenas
  armazenada.
- **Limitação assumida:** o `MemorySaver` mantém o histórico em memória
  do processo — ele reinicia se a aplicação for reiniciada. Isso é
  suficiente para o escopo deste projeto (memória de curto prazo por
  sessão de consulta); armazenamento persistente entre reinicializações
  fica como evolução futura, fora do escopo desta etapa.

## Segurança e autonomia

A solução trata segurança e limites de autonomia em duas frentes
distintas e complementares, atendendo ao requisito 4.5.

**A) Bloqueio determinístico de entrada adversarial (prompt injection).**
`triagem_seguranca` (`app/agent/nodes.py`) verifica, por padrões de texto
case-insensitive e 100% determinísticos (sem LLM), tentativas de
sobrescrever as instruções do sistema (ex.: "ignore as instrucoes",
"voce agora e"), tentativas de exfiltração de informação sensível (ex.:
"revele", "api key", "system prompt") e marcadores comuns de injeção via
delimitadores falsos (ex.: `[INST]`, `<system>`). Quando um padrão bate,
o node de junção `avaliar_seguranca` roteia diretamente para
`bloquear_acao_insegura` — **antes de qualquer chamada ao LLM**. Esse
node nunca chama `get_llm()`: a resposta de segurança é fixa e montada
inteiramente por código, garantindo por regra da aplicação — não por
"boa vontade" do modelo — que nenhuma instrução maliciosa seja seguida e
que nenhuma informação sensível (chave de API, system prompt) possa ser
revelada por esse caminho. Essa defesa em profundidade é comprovada por
teste: `tests/test_seguranca.py::test_cenario_adversarial_bloqueia_sem_chamar_llm`
verifica explicitamente que o mock de `get_llm()` **nunca é chamado**
nesse cenário.

**B) Portão de aprovação humana para ação sensível.** Análises sobre
**cálculo de impostos** — o cenário de maior risco financeiro/de
compliance no domínio — sempre passam pelo node
`solicitar_aprovacao_humana` antes do fim do grafo. Esse node marca
`aguardando_aprovacao_humana = True` e adiciona um aviso explícito à
resposta; ele **não dispara nenhuma notificação externa** — o disparo
real (webhook/automação low-code) só é implementado na Etapa 12. Nesta
etapa existe apenas o "portão": a decisão de agir de fato continua
dependendo de um humano.

**Limites de autonomia definidos:**
- Uma ação **executa** automaticamente apenas quando é 100%
  determinística e reversível (ex.: consultar a base local, gerar a
  análise via LLM dentro do contexto validado);
- Uma ação é **bloqueada** quando a entrada é classificada como
  adversarial — o grafo nunca chega a chamar o LLM nesse caso;
- Uma ação de maior risco (cálculo de impostos) fica **pendente de
  aprovação humana** antes que qualquer efeito externo possa ocorrer.

**Credenciais:** protegidas via variável de ambiente (`.env`), nunca
hardcoded no código — ver [Instalação e execução](#instalação-e-execução)
e a Etapa 2 (`app/config.py`).

O refinamento da triagem de segurança (da versão simples da Etapa 5 para
a versão atual) está documentado como ciclo de refinamento em
[docs/qa/refinamento-seguranca.md](docs/qa/refinamento-seguranca.md).

## Automação low-code (n8n)

Fecha o requisito 4.9: o portão de aprovação humana (`solicitar_aprovacao_humana`,
acima) agora dispara uma automação **low-code/no-code** real quando um
humano aprova uma análise de cálculo de impostos. A lógica de negócio
inteira continua na aplicação Python — o n8n só recebe um webhook e
produz uma saída observável (registro na aba "Executions" + resposta
HTTP); nenhuma decisão de roteamento, segurança ou aprovação é feita
pela ferramenta visual.

**Subir o ambiente local:**

```bash
cd n8n
cp ../.env.example .env   # preencha N8N_BASIC_AUTH_USER/PASSWORD locais
docker compose up -d
```

Acesse [http://localhost:5678](http://localhost:5678) e crie a conta
local (basic auth já configurado pelo `docker-compose.yml`).

**Importar o fluxo já exportado**, numa instância nova do n8n: menu
(⋯) → **Import from File** → selecione
[n8n/fluxo-aprovacao-reformatax.json](n8n/fluxo-aprovacao-reformatax.json)
→ **Activate** o fluxo (toggle no canto superior direito). O fluxo tem
3 nodes: **Webhook** (trigger, `POST /reformatax-aprovacao`) → **Edit
Fields** (monta a mensagem a partir de `cenario`, `resumo`,
`session_id`) → **Respond to Webhook** (retorna
`{"status": "notificacao_registrada", "mensagem": "..."}`). Nenhuma
credencial é exportada no JSON (confirmado manualmente).

**Configurar a aplicação Python** — no `.env` principal do projeto
(raiz, não o `n8n/.env`):

```bash
N8N_WEBHOOK_URL=http://localhost:5678/webhook/reformatax-aprovacao
N8N_TIMEOUT_SECONDS=10
```

**Fluxo ponta a ponta:** pergunta de cálculo de impostos → resposta
com `aguardando_aprovacao_humana: true` → clique em **"Aprovar e
notificar"** no banner de aviso → `POST /api/aprovar` (app/web/main.py,
determinístico, não chama `get_llm()` nem reexecuta o grafo) →
`app/tools/notificacao.py::disparar_notificacao` chama o webhook do
n8n → registro observável na aba "Executions" do n8n.

![Tela da interface web mostrando a notificação enviada ao n8n após aprovação humana de uma análise de cálculo de impostos](docs/apresentacao/tela-aprovacao-n8n.png)

Se a notificação falhar (timeout, n8n fora do ar), a API retorna 502
com mensagem amigável — a aprovação em si **não é desfeita**, só a
notificação falha (fallback documentado em
`app/tools/notificacao.py::NotificacaoFalhouError`). Os testes
automatizados (`tests/test_notificacao.py`, `tests/test_web.py`) mockam
`httpx`/a tool de notificação e passam **sem o n8n rodando**.

> **Extensão opcional (ChatOps):** para ir além do registro simples,
> troque/adicione um node de envio real para Discord/Slack/e-mail antes
> do "Respond to Webhook", configurando a credencial pela própria
> interface do n8n — nunca no JSON exportado nem no repositório.

## Instalação e execução

1. Crie e ative um ambiente virtual:

   ```bash
   python -m venv .venv
   # Linux/macOS
   source .venv/bin/activate
   # Windows (PowerShell)
   .venv\Scripts\Activate.ps1
   ```

2. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

3. Copie `.env.example` para `.env` e preencha a chave do provedor
   padrão (`GOOGLE_API_KEY`, obtida no
   [Google AI Studio](https://aistudio.google.com/app/apikey)) — ou as
   variáveis do provedor escolhido, caso troque `LLM_PROVIDER` (ver
   seção abaixo):

   ```bash
   cp .env.example .env
   ```

4. Rode os testes:

   ```bash
   pytest tests/ -v
   ```

   Nenhum teste do projeto faz chamada real a provedores de LLM (todos
   mockam `get_llm()`) — os testes rodam sem nenhuma API key real
   configurada.

5. Suba a API local:

   ```bash
   uvicorn app.web.main:app --reload
   ```

   [http://127.0.0.1:8000/](http://127.0.0.1:8000/) já abre a **interface
   web completa** (Etapa 9.1: `app/web/static/`, HTML/CSS/JS estático,
   sem framework front-end), com os dois cenários de uso demonstráveis
   visualmente — pergunta válida (com os 5 blocos da análise) e pergunta
   adversarial (bloqueio de segurança, banner de alerta). O
   **Swagger UI** continua disponível como alternativa em
   [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

   ![Tela da interface web mostrando o bloqueio de uma pergunta adversarial, com o banner de alerta e os 5 blocos da análise](docs/apresentacao/tela-interface-web.png)

   Exemplo de chamada via `curl` — a segunda pergunta reusa o
   `session_id` retornado pela primeira, demonstrando a memória de
   sessão da Etapa 6:

   ```bash
   curl -X POST http://127.0.0.1:8000/api/analisar \
     -H "Content-Type: application/json" \
     -d '{"pergunta": "Como calcular o IBS e a CBS na venda?"}'
   # -> {"session_id": "...", "cenario_identificado": "calculo_impostos", ...}

   curl -X POST http://127.0.0.1:8000/api/analisar \
     -H "Content-Type: application/json" \
     -d '{"pergunta": "E a classificacao tributaria, o que muda?", "session_id": "COLE_O_SESSION_ID_AQUI"}'
   ```

### Provedores de LLM suportados

A aplicação suporta três provedores de LLM, alternáveis apenas por
variável de ambiente (`LLM_PROVIDER`), sem qualquer alteração de código:

| `LLM_PROVIDER` | Modelo padrão | Variável de API key |
|----------------|---------------|----------------------|
| `gemini` (padrão) | `gemini-3-flash` | `GOOGLE_API_KEY` |
| `anthropic`    | `claude-sonnet-5` | `ANTHROPIC_API_KEY` |
| `openai`       | `gpt-5.1`      | `OPENAI_API_KEY` |

O **Gemini 3 Flash** é o provedor padrão recomendado pelo melhor
custo-benefício. Para trocar de provedor, altere `LLM_PROVIDER` no `.env`
e preencha a API key correspondente — nenhum código precisa ser alterado,
pois toda a lógica de seleção do client fica centralizada em
`app/llm/factory.py`.

## Tool e integração

A primeira ferramenta (tool) do agente é a **consulta à base local de
conhecimento** (`app/tools/local_kb.py`), que lê
[data/reforma_tributaria_erp.json](data/reforma_tributaria_erp.json) e
retorna a análise correspondente a um dos três cenários suportados
(cadastro de produtos, emissão de nota fiscal, cálculo de IBS/CBS).

Ela conta como integração por **serviço/backend interno** — não é uma API
externa nem um servidor MCP nesta etapa: é uma função Python com contrato
de entrada e saída explícito, validado por schema, que futuramente será
chamada por um nó do grafo do LangGraph.

**Schema de entrada** — `ConsultaCenarioInput` (`app/tools/schemas.py`):
um único campo `cenario: str`, validado por um `field_validator` do
pydantic que só aceita `cadastro_produtos`, `emissao_nota_fiscal` ou
`calculo_impostos`. Qualquer outro valor é rejeitado antes de a tool
sequer ser executada, com uma mensagem de erro listando os valores
aceitos.

**Schema de saída** — `RespostaCenarioLocal` (`app/tools/schemas.py`):
espelha a estrutura de cada cenário no JSON, com os campos `resumo`,
`pontos_reforma_relacionados`, `impactos_tecnicos_erp`,
`pontos_atencao` e `checklist_tecnico`.

**Validação e tratamento de falhas:**
- a validação de parâmetro acontece na própria construção de
  `ConsultaCenarioInput` — um `cenario` inválido nunca chega à lógica de
  negócio da tool;
- `CenarioNaoEncontradoError` é lançada como defesa extra, caso o cenário
  esteja ausente da base local carregada (mesmo já validado pelo schema);
- `BaseLocalIndisponivelError` é lançada quando o arquivo JSON não existe
  ou está corrompido (`FileNotFoundError`/`json.JSONDecodeError`
  capturadas e relançadas com `raise ... from e`), evitando que um
  traceback bruto vaze para quem consome a tool;
- o caminho do arquivo é resolvido de forma fixa dentro de `data/`, nunca
  recebido como parâmetro externo — evitando leitura de arquivos fora
  dessa pasta.

> **Nota:** esta tool é **somente leitura** e não executa nenhuma ação
> destrutiva, irreversível ou externa. O controle de ação sensível —
> que exige aprovação humana antes de disparar uma notificação — é
> implementado nas Etapas 7 e 12, sobre uma ferramenta diferente desta.

## QA, observabilidade e DevOps

> Esta seção documenta observabilidade/resiliência (requisito 4.6), QA
> com IA (Etapa 10) e DevOps/CI com IA (Etapa 11).

**Dois sinais de observabilidade correlacionados:**

- **Log estruturado** — `configurar_logging()`
  (`app/observability/logging_config.py`) configura o logger
  `"reformatax"` para emitir cada registro como uma linha JSON no stdout
  (`timestamp`, `level`, `logger`, `message` + campos extras).
- **Trilha de auditoria** — `registrar_auditoria()`
  (`app/observability/audit.py`) grava uma linha JSON por node em
  `docs/evidencias/auditoria.jsonl`, com `execution_id`, `node`, `status`,
  `duracao_ms`, `decisao` e `erro`.

Os dois sinais são aplicados a **todos os nodes do grafo** por um único
decorator — `observar()` (`app/observability/decorators.py`) — sem
alterar a lógica de negócio de nenhum node. `execution_id` (`uuid4`) é
gerado uma única vez pelo primeiro node do fluxo (`validar_entrada`) e
reaproveitado por todos os demais (inclusive pelos dois nodes que rodam
em paralelo, `consultar_base_local` e `triagem_seguranca`), o que
permite correlacionar log e auditoria de uma mesma execução — provado em
`tests/test_observabilidade.py`.

Uma execução real investigada de ponta a ponta (sequência de nodes,
latência, decisões em cada ramificação e ausência de erros) está
documentada em
[docs/evidencias/investigacao-execucao.md](docs/evidencias/investigacao-execucao.md).

**Três práticas de resiliência (requisito 4.6):**

| Prática | Onde está implementada |
|---|---|
| Timeout explícito na chamada ao LLM | `app/config.py` (`llm_timeout_seconds`, padrão 30s, configurável via `LLM_TIMEOUT_SECONDS`) + `app/llm/factory.py` (passado a cada client) |
| Retry limitado | `app/agent/nodes.py` (`MAX_TENTATIVAS_GERACAO`, desde a Etapa 5) |
| Fallback | `app/agent/nodes.py::responder_erro_geracao` (desde a Etapa 5) |

### QA com IA

IA aplicada em duas frentes de QA, sobre código real do projeto (não
exemplos fictícios):

- **Code review com IA** de um PR já mesclado — o PR de
  segurança/governança (Etapa 7), escolhido por ser o de maior risco do
  projeto. A revisão encontrou gaps reais na detecção de prompt
  injection (a lista de padrões evadia a acentuação correta do
  português, espaçamento irregular e frases em inglês) e um deles foi
  corrigido nesta mesma etapa. Íntegra da revisão, com os gaps
  corrigidos e os registrados-mas-não-corrigidos (com justificativa),
  em [docs/qa/code-review-etapa07-seguranca.md](docs/qa/code-review-etapa07-seguranca.md).
- **Teste E2E gerado/refinado com IA**
  (`tests/test_e2e_cenarios.py`), cobrindo os dois cenários exigidos
  pelo requisito 4.1 através da pilha completa (requisição HTTP → API →
  grafo → resposta). Prompt usado e ajustes manuais em
  [docs/qa/prompt-geracao-teste-e2e.md](docs/qa/prompt-geracao-teste-e2e.md).
- **Priorização de testes por risco**, justificando por que o cenário
  adversarial (prompt injection) é o teste prioritário do projeto —
  ver [docs/qa/priorizacao-testes.md](docs/qa/priorizacao-testes.md).

### DevOps: pipeline de CI e análise com IA

O pipeline de CI (`.github/workflows/ci.yml`) roda em todo push/PR para
`develop`/`main`: lint (`ruff`), testes (`pytest`, com cobertura) e uma
etapa de build/validação (import da aplicação). Para rodar os mesmos
passos localmente:

```bash
ruff check .
pytest tests/ -v --cov=app --cov-report=term-missing
python -c "from app.web.main import app; print('OK: aplicacao importada com sucesso')"
```

- **Análise dos logs reais do CI com IA** — o que cada etapa verificou,
  se passou/falhou e por quê, avisos encontrados (incluindo um aviso
  real de depreciação do Node.js 20 nas actions usadas) e se o tempo de
  execução é razoável para o tamanho do projeto — em
  [docs/qa/analise-logs-ci.md](docs/qa/analise-logs-ci.md).
- **Detecção de anomalia e estimativa de tendência/risco com IA** —
  a partir de um resumo agregado de `docs/evidencias/auditoria.jsonl`,
  identificando que `gerar_analise` (o único node que chama o LLM)
  concentra 100% da latência e dos erros observados, com uma estimativa
  quantitativa de risco de fallback se a taxa de falha do provedor
  aumentar — em [docs/qa/analise-anomalia-e-risco.md](docs/qa/analise-anomalia-e-risco.md).

  > ⚠️ Os dados de anomalia/risco acima são **simulados**
  > (`scripts/gerar_dados_simulados.py`), não produção real — o projeto
  > ainda não tem uso real em produção, conforme permitido e exigido
  > (documentado como tal) pelo requisito 4.8.
