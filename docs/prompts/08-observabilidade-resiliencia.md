# Prompt 08 — Observabilidade e resiliência

- **Data de execução:** 2026-08-24
- **Branch:** feature/observabilidade
- **Resultado obtido:** dois sinais de observabilidade correlacionados —
  log estruturado (`app/observability/logging_config.py`, logger
  `"reformatax"`, JSON no stdout) e trilha de auditoria
  (`app/observability/audit.py`, `docs/evidencias/auditoria.jsonl`) — via
  um único decorator (`app/observability/decorators.py::observar`)
  aplicado a todos os 13 nodes do grafo, sem alterar a lógica de negócio
  de nenhum node; `AgentState` estendido com `execution_id`, gerado pelo
  primeiro node (`validar_entrada`) e reaproveitado pelos demais
  (inclusive nos dois nodes que rodam em paralelo); timeout explícito
  adicionado à chamada do LLM (`app/config.py::llm_timeout_seconds`,
  `LLM_TIMEOUT_SECONDS`, passado em `app/llm/factory.py`), fechando as
  três práticas de resiliência do requisito 4.6 junto com o retry
  limitado e o fallback já existentes desde a Etapa 5; execução real
  investigada de ponta a ponta em
  `docs/evidencias/investigacao-execucao.md`; 3 novos testes em
  `tests/test_observabilidade.py` (32 testes passando ao todo) provando
  a correlação entre os dois sinais e o timeout configurado no client do
  LLM; README atualizado com a seção "QA, observabilidade e DevOps".

## Prompt

```
Vamos implementar dois sinais de observabilidade correlacionados (logs
estruturados + trilha de auditoria), usá-los para investigar uma execução
completa do agente, e formalizar o tratamento de falhas já parcialmente
existente (retry limitado da Etapa 5) com um timeout explícito na chamada
ao LLM. NÃO altere a lógica de negócio dos nodes já existentes — apenas
instrumente-os.

Issue relacionada: #9

git checkout develop
git pull origin develop
git checkout -b feature/observabilidade

Execute as etapas abaixo, nesta ordem:

1. CRIAR app/observability/logging_config.py
   - Função `configurar_logging()`: configura um logger chamado
     "reformatax" para emitir cada registro como uma linha JSON
     (timestamp, level, logger, message, e os campos extras passados via
     `extra={}`), no stdout. Chame essa função uma vez, no ponto de
     entrada da aplicação (será usado pela interface na Etapa 9; por
     enquanto, chame no início dos testes/scripts desta etapa).

2. CRIAR app/observability/audit.py
   - Função `registrar_auditoria(execution_id, node, status, duracao_ms,
     decisao, erro=None)`: monta um dicionário com esses campos + um
     timestamp ISO 8601, serializa como JSON e faz `append` de uma linha
     em `docs/evidencias/auditoria.jsonl` (crie o diretório se não
     existir). Este é o segundo sinal de observabilidade (registro de
     auditoria), correlacionado ao log estruturado pelo mesmo
     `execution_id`.

3. CRIAR O DECORATOR DE INSTRUMENTAÇÃO (app/observability/decorators.py)
   - `observar(nome_node)`: decorator que envolve qualquer função de node
     do grafo:
     - gera (ou reaproveita, se já existir em `state`) um `execution_id`
       (uuid4) — só o primeiro node do fluxo (validar_entrada) precisa
       gerar; os demais reaproveitam o que já está no estado;
     - mede o tempo de execução do node (`time.perf_counter()`);
     - chama a função original dentro de um `try/except` — se lançar uma
       exceção não tratada (rede de segurança extra, além do tratamento
       já existente em cada node), converte em uma entrada de `alertas`
       em vez de derrubar o grafo;
     - loga (via logger "reformatax") e registra auditoria
       (`registrar_auditoria`) com: execution_id, nome do node, status
       (sucesso/erro), duração em ms, e uma "decisão" resumida (derivada
       do retorno do node — ex.: cenário identificado, risco_detectado,
       se a resposta foi válida etc., o que fizer sentido por node);
     - retorna o resultado original do node (incluindo `execution_id` no
       dicionário de retorno, quando for o node que o gerou).

4. APLICAR O DECORATOR A TODOS OS NODES (app/agent/nodes.py)
   Decore cada node existente com `@observar("<nome>")`: validar_entrada,
   identificar_cenario, consultar_base_local, triagem_seguranca,
   avaliar_seguranca, bloquear_acao_insegura, gerar_analise,
   validar_resposta, responder_erro_geracao, solicitar_aprovacao_humana,
   registrar_historico, responder_entrada_invalida,
   responder_fora_de_escopo.

5. ATUALIZAR O ESTADO (app/agent/state.py)
   Adicione `execution_id: str | None` (gerado pelo decorator no primeiro
   node executado).

6. ADICIONAR TIMEOUT EXPLÍCITO À CHAMADA DO LLM (app/config.py e
   app/llm/factory.py)
   - Em `app/config.py`, adicione `llm_timeout_seconds: int = 30` às
     configurações (também configurável via variável de ambiente
     `LLM_TIMEOUT_SECONDS`, documentada no `.env.example`).
   - Em `app/llm/factory.py`, passe esse timeout na instanciação de cada
     client (`ChatGoogleGenerativeAI`, `ChatAnthropic`, `ChatOpenAI` —
     todos aceitam um parâmetro de timeout, confirme o nome exato do
     parâmetro em cada wrapper do LangChain e ajuste se necessário).
   - Documente no código: o retry limitado já existe desde a Etapa 5
     (`MAX_TENTATIVAS_GERACAO`); o fallback já existe desde a Etapa 5
     (`responder_erro_geracao`); esta etapa adiciona o timeout que
     faltava para fechar as três práticas de resiliência exigidas pelo
     requisito 4.6.

7. TESTES (tests/test_observabilidade.py)
   Usando mock de `get_llm()` e o fixture `caplog` do pytest:
   - rode uma execução completa do grafo (cenário válido) e confirme que
     há linhas de log para múltiplos nodes, todas com o MESMO
     `execution_id`;
   - confirme que `docs/evidencias/auditoria.jsonl` recebeu entradas
     correspondentes (leia o arquivo depois da execução) com o mesmo
     `execution_id` dos logs — essa é a prova de correlação entre os dois
     sinais;
   - confirme que cada entrada de auditoria tem `duracao_ms` numérica;
   - confirme (via inspeção do mock) que o client do LLM foi instanciado
     com o parâmetro de timeout configurado.
   Rode `pytest tests/ -v` e confirme que tudo passa.

8. INVESTIGAR UMA EXECUÇÃO (docs/evidencias/investigacao-execucao.md)
   Rode uma execução real (ou via teste) do cenário principal, capture o
   `execution_id` gerado, e documente neste arquivo:
   - a sequência de nodes executados (extraída dos logs/auditoria);
   - a duração de cada node e o total da execução;
   - as decisões tomadas em cada ponto de ramificação (cenário
     identificado, risco_detectado, necessidade de aprovação humana);
   - qualquer erro/retry ocorrido (ou confirmação de que não houve).
   Este documento é a evidência exigida pelo requisito 4.6 ("investigar
   pelo menos uma execução... identificando fluxo, decisões, erros e
   latência").

9. ATUALIZAR O README.md — seção "QA, observabilidade e DevOps" (criar,
   se ainda não existir, mesmo que parcial — será completada nas Etapas
   10/11)
   Documente: os dois sinais (logs estruturados + auditoria), como se
   correlacionam (`execution_id`), onde encontrar a investigação de
   exemplo (`docs/evidencias/investigacao-execucao.md`), e as três
   práticas de resiliência (timeout, retry limitado, fallback) com onde
   cada uma está implementada.

10. REGISTRAR O PROMPT
    Crie `docs/prompts/08-observabilidade-resiliencia.md` com o texto
    integral deste prompt.

11. COMMITS SEMÂNTICOS
    1. feat: adiciona configuracao de logging estruturado (#9)
    2. feat: adiciona registro de auditoria correlacionado (#9)
    3. feat: adiciona decorator de instrumentacao dos nodes (#9)
    4. feat: instrumenta todos os nodes do grafo (#9)
    5. feat: adiciona timeout explicito a chamada ao LLM (#9)
    6. test: adiciona testes de observabilidade e correlacao de sinais (#9)
    7. docs: adiciona investigacao de execucao de exemplo (#9)
    8. docs: documenta observabilidade e resiliencia no README (#9)
    9. docs: registra o prompt 08 em docs/prompts/08-observabilidade-resiliencia.md (#9)

12. ENVIAR A BRANCH E ABRIR O PULL REQUEST
    git push -u origin feature/observabilidade

    Mova o card #9 para **Em Revisão** no Project ao abrir o PR.

    Abra o PR direcionado para develop:
      Título: "feat: observabilidade e resiliencia (#9)"
      Corpo:
        Closes #9

        ## Contexto
        Adiciona dois sinais de observabilidade correlacionados (logs
        estruturados + auditoria) e fecha as tres praticas de resiliencia
        exigidas (timeout, retry limitado, fallback).

        ## O que foi feito
        - app/observability/ (logging, auditoria, decorator)
        - Todos os nodes instrumentados com execution_id compartilhado
        - Timeout explicito na chamada ao LLM
        - docs/evidencias/investigacao-execucao.md
        - Testes provando a correlacao entre os dois sinais

        ## Fora do escopo deste PR
        - Interface/API (Etapa 9 do roadmap geral)
        - Analise de logs de pipeline com IA (Etapa 11)

        ## Checklist
        - [x] Logs e auditoria compartilham o mesmo execution_id
        - [x] Pelo menos uma execucao foi investigada e documentada
        - [x] Timeout, retry limitado e fallback confirmados no codigo

13. VALIDAÇÃO FINAL
    Rode `pytest tests/ -v` e confirme que todos os testes passam. Abra
    `docs/evidencias/auditoria.jsonl` gerado pelos testes e confirme que
    as entradas fazem sentido e são legíveis.

Não implemente interface/API nem QA/DevOps com IA nesta etapa — a
interface é o próximo prompt (Etapa 9), e QA/DevOps entram nas Etapas
10/11.
```
