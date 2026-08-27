# Prompt 09 — Interface executável da aplicação (API)

- **Data de execução:** 2026-08-24
- **Branch:** feature/interface
- **Resultado obtido:** API local em FastAPI (`app/web/main.py`,
  `app/web/schemas.py`) expondo o grafo completo (Etapas 4 a 8) via
  `GET /api/cenarios` e `POST /api/analisar`; `session_id` gerenciado na
  borda da API — gerado com `uuid4()` quando omitido, reaproveitado via
  `thread_config()` (Etapa 6) para testar a memória de sessão; estado de
  entrada resetado explicitamente a cada pergunta (exceto `historico`,
  que só acumula via reducer); exceções não tratadas do `.invoke()`
  convertidas em HTTP 500 genérico, sem vazar stack trace; nenhum
  front-end HTML/JS customizado — demonstração via Swagger UI
  (`/docs`); 6 novos testes em `tests/test_web.py` usando `TestClient` e
  mock de `get_llm()` (38 testes passando ao todo), cobrindo os dois
  cenários de uso (principal e adversarial) e a memória entre chamadas
  com o mesmo `session_id`; README atualizado com instruções de
  execução, uso do Swagger UI e exemplo de `curl` reusando `session_id`.

## Prompt

```
Vamos expor o grafo completo (Etapas 4 a 8: núcleo, paralelização,
memória, segurança e observabilidade) através de uma API local em
FastAPI — formato aceito pelo requisito 5.1 e suficiente para demonstrar
os dois cenários de uso no vídeo. NÃO construa uma interface HTML/JS
customizada nesta etapa: o Swagger UI automático do FastAPI (rota /docs)
já é suficiente para demonstrar a aplicação de forma visual, sem gastar
tempo extra com front-end — o tempo do projeto é curto e isso não é
exigido pelo requisito 5.1 (API local já é um formato aceito por si só).

Issue relacionada: #10

git checkout develop
git pull origin develop
git checkout -b feature/interface

Execute as etapas abaixo, nesta ordem:

1. CRIAR OS SCHEMAS DA API (app/web/schemas.py)
   - `PerguntaRequest(BaseModel)`: `pergunta: str` (max_length=1000),
     `session_id: str | None = None` (se omitido, uma nova sessão é
     criada e o id é retornado na resposta, para o cliente reusar em
     perguntas de acompanhamento e testar a memória da Etapa 6).
   - `AnaliseResponse(BaseModel)`: `session_id: str`,
     `cenario_identificado: str | None`, `resposta_estruturada: dict |
     None`, `alertas: list[str]`, `aguardando_aprovacao_humana: bool`.

2. IMPLEMENTAR A API (app/web/main.py)
   - Ao subir a aplicação, chame `configurar_logging()` (Etapa 8).
   - `get_graph()` com `lru_cache`, chamando `build_graph()` uma única vez
     (o grafo já vem compilado com checkpointer, desde a Etapa 6).
   - `GET /api/cenarios`: retorna `listar_cenarios_disponiveis()`.
   - `POST /api/analisar`:
     - se `session_id` não vier no payload, gere um novo com `uuid4()`;
     - monte o estado parcial de entrada **resetando explicitamente todos
       os campos que não devem persistir entre perguntas** (isso é
       importante: o checkpointer restaura o estado anterior da sessão, e
       só o campo `historico` deve realmente acumular):
         {
           "pergunta_usuario": payload.pergunta,
           "cenario_identificado": None,
           "dados_base_local": None,
           "resposta_estruturada": None,
           "alertas": [],
           "tentativas_geracao": 0,
           "risco_detectado": False,
           "aguardando_aprovacao_humana": False,
           "execution_id": None,
         }
     - chame `get_graph().invoke(estado, config=thread_config(session_id))`
       (helper da Etapa 6);
     - retorne um `AnaliseResponse` com `session_id` (para o cliente
       reusar) e os campos relevantes do estado final.
   - Trate exceções inesperadas do `.invoke()` retornando HTTP 500 com
     mensagem genérica, sem vazar stack trace (defesa adicional — os
     nodes já tratam seus próprios erros desde as etapas anteriores).
   - NÃO monte arquivos estáticos/HTML nesta etapa.

3. ATUALIZAR O .env.example E README.md
   - Adicione, se ainda não existir, `APP_PORT=8000` (opcional) ao
     `.env.example`.
   - No README, seção "Instalação e execução", adicione:
     - comando para rodar: `uvicorn app.web.main:app --reload`;
     - a URL local e a menção explícita de que `http://127.0.0.1:8000/docs`
       (Swagger UI, gerado automaticamente pelo FastAPI) é o jeito mais
       rápido de demonstrar a aplicação, incluindo os dois cenários de
       uso, sem precisar de front-end customizado;
     - um exemplo de chamada via curl para `/api/analisar`, incluindo o
       reuso de `session_id` numa segunda pergunta (demonstrando memória).

4. TESTES (tests/test_web.py)
   Usando `TestClient` e mock de `get_llm()` (nunca API real):
   - `GET /api/cenarios` retorna os 3 cenários esperados;
   - `POST /api/analisar` com pergunta válida retorna 200, com
     `session_id` preenchido e `resposta_estruturada` completo;
   - duas chamadas seguidas com o MESMO `session_id` (pergunta de
     cálculo de impostos, depois uma pergunta de acompanhamento) —
     confirme que a segunda não quebra e que o grafo reconhece a sessão
     (ex.: inspecionando os argumentos passados ao mock do LLM na segunda
     chamada, como já validado na Etapa 6, agora na camada de API);
   - `POST /api/analisar` com pergunta adversarial (prompt injection) —
     confirme bloqueio (sem chamada ao mock do LLM) e resposta segura;
   - `POST /api/analisar` com pergunta de cálculo de impostos — confirme
     `aguardando_aprovacao_humana == True` na resposta;
   - `POST /api/analisar` com pergunta vazia — confirme `alertas`
     preenchido.
   Rode `pytest tests/ -v` e confirme que tudo passa sem nenhuma API key
   configurada.

5. REGISTRAR O PROMPT
   Crie `docs/prompts/09-interface-api.md` com o texto integral deste
   prompt.

6. COMMITS SEMÂNTICOS
   1. feat: adiciona schemas da API (PerguntaRequest, AnaliseResponse) (#10)
   2. feat: implementa API FastAPI expondo o grafo completo (#10)
   3. feat: adiciona gestao de session_id para reuso de memoria (#10)
   4. test: adiciona testes da API cobrindo os dois cenarios (#10)
   5. docs: documenta execucao da API e uso do Swagger UI no README (#10)
   6. docs: registra o prompt 09 em docs/prompts/09-interface-api.md (#10)

7. ENVIAR A BRANCH E ABRIR O PULL REQUEST
   git push -u origin feature/interface

   Mova o card #10 para **Em Revisão** no Project ao abrir o PR.

   Abra o PR direcionado para develop:
     Título: "feat: interface executavel via API FastAPI (#10)"
     Corpo:
       Closes #10

       ## Contexto
       Expoe o grafo completo (nucleo, paralelizacao, memoria, seguranca
       e observabilidade) via API local, formato aceito pelo requisito
       5.1, demonstravel via Swagger UI sem front-end customizado.

       ## O que foi feito
       - app/web/schemas.py e app/web/main.py
       - Reset explicito de estado por pergunta, preservando so o historico
       - Testes cobrindo os dois cenarios (principal e adversarial) via API
       - README: instrucoes de execucao e demonstracao via /docs

       ## Fora do escopo deste PR
       - Front-end HTML/JS customizado (nao exigido pelo requisito 5.1)
       - QA/DevOps com IA (Etapas 10/11)

       ## Checklist
       - [x] Nenhuma chave de API exposta na API/respostas
       - [x] Estado resetado corretamente entre perguntas da mesma sessao
       - [x] Testes passam sem nenhuma API key configurada

8. VALIDAÇÃO FINAL
   Rode `pytest tests/ -v` e confirme que todos os testes passam. Suba a
   API localmente (`uvicorn app.web.main:app --reload`) e teste
   manualmente pelo Swagger UI os dois cenários (principal e adversarial),
   confirmando visualmente o comportamento esperado antes de gravar o
   vídeo.

Não implemente análise de código/testes com IA nem pipeline de DevOps
nesta etapa — isso é o conteúdo das Etapas 10 e 11.
```
