# Prompt 03 — Tool de consulta à base local

- **Data de execução:** 2026-08-23
- **Branch:** feature/tool-integracao
- **Resultado obtido:** `data/reforma_tributaria_erp.json` criado com a
  base de conhecimento dos três cenários; `app/tools/schemas.py` com
  `ConsultaCenarioInput` (validação de cenário suportado) e
  `RespostaCenarioLocal`; `app/tools/local_kb.py` com `carregar_base()`
  (cache via `lru_cache`, caminho fixo dentro de `data/`,
  `BaseLocalIndisponivelError` em caso de falha de leitura),
  `consultar_cenario()` (com `CenarioNaoEncontradoError` como defesa
  extra) e `listar_cenarios_disponiveis()`; testes cobrindo os 3
  cenários válidos, entrada inválida, falha de leitura do arquivo e
  listagem de cenários — todos passando; README atualizado com a seção
  "Tool e integração". Nenhum grafo do LangGraph ou chamada ao LLM foi
  implementado.

## Prompt

```
Vamos implementar a ferramenta (tool) funcional do agente: consulta a uma
base local de conhecimento sobre a Reforma Tributária aplicada a ERP
(data/reforma_tributaria_erp.json), com entrada e saída definidas por
schema (pydantic), validação de parâmetros e tratamento de falhas — sem
depender de respostas fixas hardcoded no código de negócio. Esta tool é
100% determinística e somente leitura (não executa nenhuma ação
destrutiva ou externa; ações sensíveis ficam nas Etapas 7 e 12). NÃO
implemente o grafo do LangGraph nem qualquer chamada ao LLM nesta etapa.

Issue relacionada: #4

git checkout develop
git pull origin develop
git checkout -b feature/tool-integracao

Execute as etapas abaixo, nesta ordem:

1. CRIAR data/reforma_tributaria_erp.json
   Crie o arquivo com o conteúdo abaixo (base de conhecimento local,
   reaproveitada do mini-projeto):

   [conteúdo integral do JSON com metadata (título, descrição, versão,
   fundamentos legais, aviso legal, cronograma geral, glossário) e os
   três cenários: cadastro_produtos, emissao_nota_fiscal,
   calculo_impostos, cada um com nome, resumo,
   pontos_reforma_relacionados, impactos_tecnicos_erp, pontos_atencao e
   checklist_tecnico]

2. CRIAR app/tools/schemas.py
   Defina os contratos de entrada e saída da tool com `pydantic`:
   - `ConsultaCenarioInput(BaseModel)`: campo `cenario: str`, com um
     `field_validator` que rejeita qualquer valor fora de
     `{"cadastro_produtos", "emissao_nota_fiscal", "calculo_impostos"}`,
     levantando erro de validação com mensagem listando os valores
     aceitos.
   - `RespostaCenarioLocal(BaseModel)`: campos `resumo: str`,
     `pontos_reforma_relacionados: list[str]`,
     `impactos_tecnicos_erp: list[str]`, `pontos_atencao: list[str]`,
     `checklist_tecnico: list[str]` — espelhando exatamente a estrutura
     de cada cenário dentro do JSON.

3. IMPLEMENTAR A TOOL (app/tools/local_kb.py)
   - Exceções customizadas: `CenarioNaoEncontradoError(Exception)` e
     `BaseLocalIndisponivelError(Exception)`.
   - `carregar_base() -> dict`:
     - Resolve o caminho do JSON de forma fixa, relativa à raiz do
       projeto (nunca aceita caminho vindo de fora da função — evita
       leitura de arquivos fora da pasta data/);
     - Usa `functools.lru_cache` para não reler o arquivo a cada chamada;
     - Captura `FileNotFoundError`/`json.JSONDecodeError` e relança como
       `BaseLocalIndisponivelError` (com `raise ... from e`), com
       mensagem clara — este é o tratamento de falha desta tool (o
       "serviço" de leitura de arquivo pode falhar; a chamada não deve
       propagar um traceback bruto para quem consumir a tool).
   - `consultar_cenario(payload: ConsultaCenarioInput) -> RespostaCenarioLocal`:
     - Recebe o payload já validado pelo schema pydantic (a validação de
       parâmetro acontece na própria construção do `ConsultaCenarioInput`,
       antes de chegar aqui — documente isso no docstring);
     - Chama `carregar_base()`, busca `cenarios.<cenario>`;
     - Se a chave não existir no JSON carregado (defesa extra, além da
       validação do schema), lança `CenarioNaoEncontradoError`;
     - Monta e retorna um `RespostaCenarioLocal` a partir dos dados
       encontrados (validação de saída também via pydantic — se o JSON
       estiver com campo faltando, o pydantic já acusa erro aqui).
   - `listar_cenarios_disponiveis() -> list[str]`: retorna os 3 cenários
     válidos (reaproveitado depois pela interface/API).

4. ATUALIZAR O README.md — seção "Tool e integração" (requisito 5.2)
   Descreva:
   - o que a tool faz e por que ela conta como integração por "serviço/
     backend" (não é uma API externa nem MCP nesta etapa — é um serviço
     interno da aplicação com contrato de entrada/saída bem definido);
   - o schema de entrada (`ConsultaCenarioInput`) e saída
     (`RespostaCenarioLocal`);
   - como a validação de parâmetros acontece (pydantic) e como as falhas
     são tratadas (`CenarioNaoEncontradoError`,
     `BaseLocalIndisponivelError`, sem traceback bruto vazando);
   - uma nota explícita: esta tool é somente leitura, não executa ação
     destrutiva/irreversível — o controle de ação sensível (que exige
     aprovação humana) é implementado na Etapa 7/12, sobre uma ferramenta
     diferente (notificação).

5. TESTES (tests/test_local_kb.py)
   Com `pytest`, cubra:
   - os 3 cenários válidos retornam `RespostaCenarioLocal` com os 5
     campos preenchidos e coerentes com o JSON;
   - `ConsultaCenarioInput(cenario="invalido")` levanta erro de validação
     do pydantic (parâmetro inválido barrado antes mesmo de chegar à
     lógica da tool);
   - `carregar_base()` lança `BaseLocalIndisponivelError` quando o
     arquivo não existe (teste isolado, sem alterar a função para aceitar
     caminho externo);
   - `listar_cenarios_disponiveis()` retorna exatamente os 3 cenários.
   Rode `pytest tests/ -v` e confirme que tudo passa.

6. REGISTRAR O PROMPT
   Crie `docs/prompts/03-tool-consulta-local.md` com o texto integral
   deste prompt, seguindo o padrão já estabelecido.

7. COMMITS SEMÂNTICOS
   1. feat: adiciona data/reforma_tributaria_erp.json (#4)
   2. feat: adiciona schemas de entrada e saida da tool (#4)
   3. feat: implementa a tool de consulta a base local com validacao e tratamento de falhas (#4)
   4. test: adiciona testes da tool com casos validos e invalidos (#4)
   5. docs: documenta a tool e sua integracao no README (#4)
   6. docs: registra o prompt 03 em docs/prompts/03-tool-consulta-local.md (#4)

8. ENVIAR A BRANCH E ABRIR O PULL REQUEST
   git push -u origin feature/tool-integracao

   Mova o card #4 para **Em Revisão** no Project ao abrir o PR.

   Abra o PR direcionado para develop:
     Título: "feat: tool de consulta a base local com validacao (#4)"
     Corpo:
       Closes #4

       ## Contexto
       Implementa a ferramenta funcional do agente: consulta a base local
       de conhecimento tributario, com schema de entrada/saida (pydantic)
       e tratamento de falhas.

       ## O que foi feito
       - data/reforma_tributaria_erp.json
       - app/tools/schemas.py (ConsultaCenarioInput, RespostaCenarioLocal)
       - app/tools/local_kb.py (tool + excecoes customizadas)
       - Testes cobrindo casos validos, invalidos e falha de leitura
       - README: secao "Tool e integracao"

       ## Fora do escopo deste PR
       - Nenhum grafo do LangGraph foi criado
       - Nenhuma chamada a get_llm() foi feita
       - Esta tool nao executa nenhuma acao destrutiva (e somente leitura)

       ## Checklist
       - [x] Validacao de parametros via schema (pydantic)
       - [x] Tratamento de falhas sem vazar traceback bruto
       - [x] Testes passam sem nenhuma dependencia externa

9. VALIDAÇÃO FINAL
   Rode `pytest tests/ -v` e confirme que todos os testes passam. Revise
   se `app/tools/local_kb.py` não aceita nenhum caminho de arquivo vindo
   de fora da função (proteção contra leitura fora de data/).

Não implemente o grafo do LangGraph, os nós do agente ou qualquer chamada
ao LLM nesta etapa — isso começa na Etapa 4.
```
