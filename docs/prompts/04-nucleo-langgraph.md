# Prompt 04 — Núcleo do grafo LangGraph (state, nodes, edges)

- **Data de execução:** 2026-08-23
- **Branch:** feature/langgraph-agente
- **Resultado obtido:** `app/agent/state.py` com `AgentState` (TypedDict
  documentado campo a campo); `app/agent/nodes.py` com os 5 nodes
  determinísticos (`validar_entrada`, `identificar_cenario`,
  `consultar_base_local`, `responder_entrada_invalida`,
  `responder_fora_de_escopo`), com docstring de módulo explicitando a
  separação entre lógica determinística e o único node agêntico do
  projeto (`gerar_analise`, Etapa 5); `app/agent/graph.py` com
  `build_graph()` montando o grafo compilado, com arestas condicionais
  após `validar_entrada` e `identificar_cenario`; testes de ponta a
  ponta cobrindo os 3 cenários, entrada inválida e fora de escopo — 20
  testes passando ao todo (incluindo os das Etapas 2 e 3); README
  atualizado ligando o diagrama Mermaid aos arquivos reais. Nenhum
  arquivo em `app/agent/` importa `app.llm.factory` ou qualquer client
  de LLM. Nota: o PR #20 (Etapa 3, tool de consulta local) precisou ser
  mesclado em `develop` antes desta etapa, pois `consultar_base_local`
  depende de `app/tools/local_kb.py` e `app/tools/schemas.py`.

## Prompt

```
Vamos montar o núcleo do grafo do agente com LangGraph: estado
compartilhado tipado, nodes com responsabilidade única, edges explícitas,
execução sequencial e ramificação condicional. Esta etapa é 100%
determinística — NÃO chame get_llm() nem implemente nenhuma lógica
agêntica ainda (isso entra na Etapa 5, junto com a paralelização e a
condição de parada do retry). O grafo desta etapa termina, temporariamente,
no nó consultar_base_local.

Issue relacionada: #5

git checkout develop
git pull origin develop
git checkout -b feature/langgraph-agente

Execute as etapas abaixo, nesta ordem:

1. DEFINIR O ESTADO (app/agent/state.py)
   `TypedDict` chamado `AgentState`, com docstring explicando cada campo:
   - pergunta_usuario: str
   - cenario_identificado: str | None
   - dados_base_local: dict | None   # serializado de RespostaCenarioLocal
   - resposta_estruturada: dict | None
   - alertas: list[str]
   Use `from __future__ import annotations` e tipagem compatível com o
   LangGraph. Este arquivo será estendido nas próximas etapas (memória,
   segurança, retry) — mantenha os campos mínimos necessários agora.

2. IMPLEMENTAR OS NODES DETERMINÍSTICOS (app/agent/nodes.py)
   No topo do arquivo, adicione um comentário/docstring de módulo
   explicando a separação exigida pelo requisito 4.2 do documento oficial:
   "Todos os nodes deste arquivo, até a Etapa 4, são 100% determinísticos
   (regras da aplicação, sem LLM). O único node agêntico de todo o
   projeto é gerar_analise (introduzido na Etapa 5), que usa o LLM apenas
   para sintetizar a resposta final a partir do contexto já recuperado —
   nunca para decidir roteamento, autonomia ou execução de ferramentas."

   Implemente:

   a) validar_entrada(state) -> dict
      - `strip()` na pergunta; se vazia, adiciona a alertas: "Por favor,
        informe uma pergunta ou selecione um cenario.";
      - se tiver mais de 500 caracteres, adiciona a alertas: "Sua
        pergunta e muito longa. Tente resumir em ate 500 caracteres.";
      - não lança exceção — só popula `alertas`.

   b) identificar_cenario(state) -> dict
      - Regra determinística por palavras-chave (case-insensitive):
          cadastro_produtos: ["cadastro", "produto", "ncm",
            "classificacao tributaria", "cclasstrib"]
          emissao_nota_fiscal: ["nota fiscal", "nf-e", "nfe", "nfc-e",
            "emissao", "danfe"]
          calculo_impostos: ["calculo", "imposto", "ibs", "cbs",
            "tributo", "aliquota"]
      - Se nada bater, `cenario_identificado = "fora_de_escopo"`.

   c) consultar_base_local(state) -> dict
      - Monta `ConsultaCenarioInput(cenario=state["cenario_identificado"])`
        (do app.tools.schemas, Etapa 3) e chama `consultar_cenario(...)`;
      - Em caso de sucesso, guarda `.model_dump()` em `dados_base_local`;
      - Se `ConsultaCenarioInput` levantar erro de validação ou a tool
        levantar `CenarioNaoEncontradoError`/`BaseLocalIndisponivelError`,
        capture e adicione mensagem amigável a `alertas`, sem propagar a
        exceção para fora do node.

   d) responder_entrada_invalida(state) -> dict
      - Monta `resposta_estruturada` simplificado (campo `mensagem`)
        repetindo o conteúdo de `alertas`.

   e) responder_fora_de_escopo(state) -> dict
      - Monta `resposta_estruturada` explicando que a pergunta não se
        encaixa nos 3 cenários suportados, sugerindo reformular.

3. MONTAR O GRAFO (app/agent/graph.py)
   Usando `langgraph.graph.StateGraph` e `AgentState`:
   - Nodes: validar_entrada, identificar_cenario, consultar_base_local,
     responder_entrada_invalida, responder_fora_de_escopo;
   - Entry point: validar_entrada;
   - Aresta condicional pós-validar_entrada: `alertas` não vazia →
     responder_entrada_invalida → END; caso contrário → identificar_cenario;
   - Aresta condicional pós-identificar_cenario: `cenario_identificado ==
     "fora_de_escopo"` → responder_fora_de_escopo → END; caso contrário →
     consultar_base_local;
   - Aresta direta: consultar_base_local → END (temporário — na Etapa 5
     este node passa a alimentar, em paralelo, o node de triagem de
     segurança e, na sequência, gerar_analise);
   - Função `build_graph()` que monta e retorna o grafo **compilado**.

4. TESTES (tests/test_agent_graph.py)
   Cubra, via `build_graph().invoke({...})`:
   - pergunta válida para cada um dos 3 cenários → `cenario_identificado`
     correto e `dados_base_local` preenchido;
   - pergunta vazia/só espaços → `resposta_estruturada` com mensagem de
     validação, `dados_base_local` continua `None`;
   - pergunta fora de escopo → `cenario_identificado == "fora_de_escopo"`
     e `resposta_estruturada` com mensagem amigável.
   Rode `pytest tests/ -v` e confirme que tudo passa, junto com os testes
   já existentes das Etapas 2 e 3.

5. ATUALIZAR O README.md — seção "Classificação e arquitetura"
   Adicione uma nota curta ligando o diagrama (já publicado na Etapa 1)
   aos arquivos reais: `app/agent/state.py`, `app/agent/nodes.py`,
   `app/agent/graph.py`. Inclua explicitamente a frase sobre separação
   entre decisão do modelo e regra determinística (mesma do passo 2),
   já que o requisito 5.2 pede isso documentado no README, não só no
   código.

6. REGISTRAR O PROMPT
   Crie `docs/prompts/04-nucleo-langgraph.md` com o texto integral deste
   prompt, seguindo o padrão já estabelecido.

7. COMMITS SEMÂNTICOS
   1. feat: adiciona o estado tipado do agente (AgentState) (#5)
   2. feat: implementa nodes deterministicos de validacao e identificacao de cenario (#5)
   3. feat: implementa node consultar_base_local integrado a tool (#5)
   4. feat: monta o grafo langgraph com arestas condicionais (#5)
   5. test: adiciona testes de ponta a ponta do grafo (#5)
   6. docs: atualiza README com a arquitetura real do grafo (#5)
   7. docs: registra o prompt 04 em docs/prompts/04-nucleo-langgraph.md (#5)

8. ENVIAR A BRANCH E ABRIR O PULL REQUEST
   git push -u origin feature/langgraph-agente

   Mova o card #5 para **Em Revisão** no Project ao abrir o PR.

   Abra o PR direcionado para develop:
     Título: "feat: nucleo do grafo LangGraph - state, nodes, edges (#5)"
     Corpo:
       Closes #5

       ## Contexto
       Monta o nucleo determinístico do grafo do agente: estado
       compartilhado tipado, nodes com responsabilidade unica, edges
       explicitas, execucao sequencial e ramificacao condicional.

       ## O que foi feito
       - app/agent/state.py (AgentState)
       - app/agent/nodes.py (5 nodes deterministicos)
       - app/agent/graph.py (build_graph())
       - Testes de ponta a ponta (3 cenarios + invalida + fora de escopo)
       - README atualizado com a arquitetura real

       ## Fora do escopo deste PR
       - Paralelizacao e condicao de parada (Etapa 5)
       - Chamada ao LLM / node gerar_analise (Etapa 5)
       - Triagem de seguranca (Etapa 7)

       ## Checklist
       - [x] Nenhuma chamada a get_llm() foi feita
       - [x] Todos os nodes sao deterministicos, sem dependencia de LLM
       - [x] Testes passam sem nenhuma API key configurada

9. VALIDAÇÃO FINAL
   Rode `pytest tests/ -v` e confirme que todos os testes passam. Revise
   se nenhum arquivo em app/agent/ importa app.llm.factory ou qualquer
   client de LLM.

Não implemente paralelização, condição de parada, chamada ao LLM ou
qualquer lógica agêntica nesta etapa — isso é o conteúdo integral da
Etapa 5.
```
