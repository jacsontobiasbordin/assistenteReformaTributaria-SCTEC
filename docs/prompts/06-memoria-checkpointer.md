# Prompt 06 — Memória de sessão (checkpointer)

- **Data de execução:** 2026-08-23
- **Branch:** feature/memoria-rag
- **Resultado obtido:** `AgentState` estendido com `historico:
  Annotated[list[dict], add]`, o único campo que acumula entre turnos em
  vez de ser sobrescrito; `registrar_historico` implementado em
  `app/agent/nodes.py`, rodando apenas no caminho de sucesso;
  `gerar_analise` ajustado para incluir as 1-2 últimas entradas do
  histórico como contexto adicional na mensagem ao LLM; `app/agent/
  graph.py` compilado com `MemorySaver`, node `registrar_historico`
  inserido entre `validar_resposta` (caminho válido) e `END`, e função
  utilitária `thread_config(thread_id)`; testes em `tests/
  test_memoria.py` cobrindo continuidade entre perguntas na mesma
  sessão (incluindo inspeção da mensagem enviada ao mock do LLM),
  isolamento entre sessões com `thread_id` diferentes e ausência de
  entrada de histórico para pergunta inválida — 26 testes passando ao
  todo; README atualizado com a seção "Contexto e memória". Nota: como o
  grafo passou a exigir `thread_id` no `config` de toda chamada
  `.invoke()` (exigência do checkpointer), os testes já existentes em
  `tests/test_agent_graph.py` precisaram ser atualizados para passar
  `config=thread_config(...)`.

## Prompt

```
Vamos implementar a estratégia de memória do agente, usando o checkpointer
nativo do LangGraph (MemorySaver) para dar memória de curto prazo entre
perguntas feitas na mesma sessão (mesmo thread_id) — sem precisar de RAG
nem de banco de dados persistente, adequado ao domínio (o histórico só
precisa durar a conversa, não anos). NÃO implemente RAG, armazenamento em
banco externo, nem qualquer interface/API nesta etapa (isso é a Etapa 9).

Issue relacionada: #7

git checkout develop
git pull origin develop
git checkout -b feature/memoria-rag

Execute as etapas abaixo, nesta ordem:

1. ATUALIZAR O ESTADO (app/agent/state.py)
   Adicione o campo `historico`, usando um reducer para que ele ACUMULE
   entre turnos em vez de ser sobrescrito (diferente dos demais campos,
   que devem ser recalculados a cada pergunta):

     from typing import Annotated
     from operator import add
     ...
     historico: Annotated[list[dict], add]

   Documente: todo campo do estado SEM esse reducer é sobrescrito a cada
   nova pergunta (comportamento correto: cenário, dados recuperados e
   alertas não devem "vazar" de uma pergunta para outra). Só `historico`
   deve persistir e crescer ao longo da sessão — é isso que caracteriza a
   memória de curto prazo.

2. IMPLEMENTAR O NODE registrar_historico (app/agent/nodes.py)
   - `registrar_historico(state) -> dict`: só roda no caminho de sucesso
     (resposta válida). Monta uma entrada resumida:
       {"pergunta": state["pergunta_usuario"],
        "cenario": state["cenario_identificado"],
        "resumo": state["resposta_estruturada"]["cenario_analisado"]}
     e retorna `{"historico": [entrada]}` — o reducer do passo 1 cuida de
     concatenar com o histórico já existente na sessão.
   - Justifique em comentário por que só o caminho de sucesso grava
     histórico: perguntas inválidas ou fora de escopo não agregam
     contexto útil para perguntas futuras na mesma sessão.

3. USAR O HISTÓRICO EM gerar_analise (app/agent/nodes.py)
   Ajuste a montagem da `HumanMessage` em `gerar_analise`: se
   `state.get("historico")` não estiver vazio, inclua as 1-2 últimas
   entradas como contexto adicional antes da pergunta atual (ex.:
   "Contexto de perguntas anteriores nesta sessão: ..."). Isso é o que
   faz a memória ser efetivamente USADA pela aplicação, não só armazenada
   — atende à exigência do requisito 4.4 ("a estratégia adotada deverá
   permitir que a solução utilize informações relevantes... de interações
   anteriores").

4. ATUALIZAR O GRAFO (app/agent/graph.py)
   - Compile o grafo com um checkpointer:
       from langgraph.checkpoint.memory import MemorySaver
       grafo = builder.compile(checkpointer=MemorySaver())
   - Adicione o node `registrar_historico` entre `validar_resposta`
     (caminho válido) e `END` — troque a aresta
     `validar_resposta --(valida)--> END` por
     `validar_resposta --(valida)--> registrar_historico --> END`.
   - Adicione uma função utilitária `thread_config(thread_id: str) -> dict`
     que retorna `{"configurable": {"thread_id": thread_id}}`, para ser
     usada em `.invoke(estado, config=thread_config(id_da_sessao))`.
   - Comente no topo do arquivo: "Limitação assumida nesta versão: o
     MemorySaver mantém o histórico em memória do processo — reinicia se
     a aplicação for reiniciada. Suficiente para o escopo deste projeto
     (memória de curto prazo por sessão); armazenamento persistente entre
     reinicializações fica como evolução futura."

5. TESTES (tests/test_memoria.py)
   Usando mock de `get_llm()`:
   - duas chamadas `.invoke()` com o MESMO thread_id: a segunda pergunta
     deve encontrar `historico` com 1 entrada da primeira, E a mensagem
     enviada ao mock do LLM na segunda chamada deve conter a pergunta
     anterior como contexto (inspecione os argumentos da chamada ao mock);
   - duas chamadas com thread_id DIFERENTES: confirme que não há
     vazamento de histórico entre sessões;
   - uma pergunta inválida (vazia) não deve gerar entrada em `historico`.
   Rode `pytest tests/ -v` e confirme que tudo passa.

6. ATUALIZAR O README.md — seção "Contexto e memória" (requisito 5.2)
   Explique: uso do checkpointer (`MemorySaver`) do LangGraph, por
   `thread_id`; o que é persistido (`historico`, só em respostas bem-
   sucedidas) e como é usado (contexto extra em `gerar_analise`); a
   limitação assumida (memória em processo, não sobrevive a reinício) e
   por que essa escolha é adequada ao domínio (sessão de consulta, não
   histórico definitivo).

7. REGISTRAR O PROMPT
   Crie `docs/prompts/06-memoria-checkpointer.md` com o texto integral
   deste prompt.

8. COMMITS SEMÂNTICOS
   1. feat: adiciona campo historico com reducer ao estado (#7)
   2. feat: implementa node registrar_historico (#7)
   3. feat: usa o historico como contexto em gerar_analise (#7)
   4. feat: compila o grafo com checkpointer MemorySaver (#7)
   5. test: adiciona testes de memoria entre sessoes (#7)
   6. docs: documenta a estrategia de memoria no README (#7)
   7. docs: registra o prompt 06 em docs/prompts/06-memoria-checkpointer.md (#7)

9. ENVIAR A BRANCH E ABRIR O PULL REQUEST
   git push -u origin feature/memoria-rag

   Mova o card #7 para **Em Revisão** no Project ao abrir o PR.

   Abra o PR direcionado para develop:
     Título: "feat: memoria de sessao via checkpointer (#7)"
     Corpo:
       Closes #7

       ## Contexto
       Implementa memoria de curto prazo entre perguntas da mesma sessao,
       usando o checkpointer nativo do LangGraph (MemorySaver).

       ## O que foi feito
       - historico com reducer no AgentState
       - node registrar_historico (so no caminho de sucesso)
       - uso do historico como contexto em gerar_analise
       - grafo compilado com MemorySaver + thread_config()
       - Testes de continuidade e isolamento entre sessoes

       ## Fora do escopo deste PR
       - RAG ou base de conhecimento externa
       - Persistencia entre reinicializacoes da aplicacao
       - Interface/API que gere thread_id por usuario (Etapa 9)

       ## Checklist
       - [x] Historico so acumula em respostas bem-sucedidas
       - [x] Sessoes com thread_id diferentes nao compartilham historico
       - [x] Testes passam sem nenhuma API key configurada

10. VALIDAÇÃO FINAL
    Rode `pytest tests/ -v` e confirme que todos os testes passam,
    incluindo a prova de que o histórico é efetivamente usado (não só
    armazenado) na segunda chamada ao LLM.

Não implemente RAG, armazenamento persistente externo, nem qualquer
interface/API nesta etapa — isso continua nas próximas etapas.
```
