# Prompt 12 — Automação low-code/no-code (n8n)

- **Data de execução:** 2026-08-25
- **Branch:** feature/low-code
- **Resultado obtido:** ambiente n8n local via Docker
  (`n8n/docker-compose.yml`) rodando de ponta a ponta; fluxo de 3 nodes
  (Webhook → Edit Fields → Respond to Webhook) construído via API REST
  do próprio n8n (autenticada com uma API key criada na interface, já
  que a automação por drag-and-drop no canvas seria frágil demais para
  reproduzir de forma confiável) e exportado de verdade pela interface
  (menu ⋯ → Export JSON) em
  `n8n/fluxo-aprovacao-reformatax.json` — sem nenhuma credencial;
  testado manualmente com `curl` e confirmado no histórico
  "Executions" do n8n; tool `app/tools/notificacao.py`
  (`disparar_notificacao`, `NotificacaoInput`/`NotificacaoResultado`/
  `NotificacaoFalhouError`) testada contra o n8n real (sucesso e
  timeout) antes dos testes automatizados; endpoint
  `POST /api/aprovar` (`app/web/main.py`) determinístico, sem chamar
  `get_llm()` nem reexecutar o grafo; botão "Aprovar e notificar" no
  front-end (Etapa 9.1); fluxo completo validado visualmente de ponta
  a ponta via Playwright contra o n8n real rodando; 8 novos testes
  (`tests/test_notificacao.py`, `tests/test_web.py`) com `httpx`/a tool
  mockados, 53 testes passando ao todo, confirmados **sem** o n8n
  rodando; README atualizado com instruções completas de reprodução.

## Prompt

```
Vamos fechar o requisito 4.9: uma automação low-code/no-code (n8n)
integrada à aplicação principal, disparada quando um ser humano aprova
uma análise que ficou pendente (Etapa 7, cenário de cálculo de impostos).
A lógica de negócio inteira continua na aplicação Python — o n8n só
recebe um webhook e produz uma saída observável (registro/resposta). O
ambiente do n8n roda local via Docker, e o fluxo é exportado em JSON e
versionado no repositório, para que qualquer pessoa (inclusive o
professor) consiga reproduzir sem depender de uma conta n8n na nuvem.

Issue relacionada: #13

git checkout develop
git pull origin develop
git checkout -b feature/low-code

Execute as etapas abaixo, nesta ordem:

1. SUBIR O N8N LOCAL VIA DOCKER
   Crie `n8n/docker-compose.yml`:
     services:
       n8n:
         image: docker.n8n.io/n8nio/n8n
         restart: unless-stopped
         ports:
           - "5678:5678"
         environment:
           - N8N_BASIC_AUTH_ACTIVE=true
           - N8N_BASIC_AUTH_USER=${N8N_BASIC_AUTH_USER}
           - N8N_BASIC_AUTH_PASSWORD=${N8N_BASIC_AUTH_PASSWORD}
           - GENERIC_TIMEZONE=America/Sao_Paulo
         volumes:
           - n8n_data:/home/node/.n8n
     volumes:
       n8n_data:
   Adicione ao `.env.example` (raiz do projeto), numa seção separada:
     # n8n local (docker-compose em n8n/) — nao usado pela aplicacao Python
     N8N_BASIC_AUTH_USER=
     N8N_BASIC_AUTH_PASSWORD=
   Suba o ambiente localmente para desenvolver o fluxo:
     cd n8n && cp ../.env.example .env   # preencha usuario/senha locais
     docker compose up -d
   Acesse http://localhost:5678 e crie a conta local (basic auth já
   configurado acima).

2. CONSTRUIR O FLUXO NO N8N (via interface web do n8n, não código)
   Monte um fluxo com 3 nodes:
   - **Webhook** (trigger): método POST, path `/reformatax-aprovacao`,
     modo de resposta "Using 'Respond to Webhook' node";
   - **Set/Edit Fields**: monta uma mensagem de notificação a partir do
     payload recebido (`cenario`, `resumo`, `session_id`), por exemplo:
     `"[ReformaTax] Analise aprovada - cenario: {{ $json.cenario }} -
     sessao: {{ $json.session_id }} - resumo: {{ $json.resumo }}"`;
   - **Respond to Webhook**: retorna `{"status": "notificacao_registrada",
     "mensagem": "<mensagem montada>"}`.
   Esse fluxo já satisfaz o requisito por si só (o registro da execução
   no histórico do n8n conta como "saída observável — registro"). Como
   extensão opcional (se quiser ir além), troque/adicione um node de
   envio real para Discord/Slack/e-mail antes do "Respond to Webhook" —
   nesse caso, configure a credencial pela interface do n8n (nunca no
   JSON exportado nem no repositório).

3. TESTAR O FLUXO MANUALMENTE
   Copie a URL do node Webhook (algo como
   `http://localhost:5678/webhook/reformatax-aprovacao`) e teste com
   curl antes de integrar com a aplicação:
     curl -X POST http://localhost:5678/webhook/reformatax-aprovacao \
       -H "Content-Type: application/json" \
       -d '{"cenario": "calculo_impostos", "resumo": "teste", "session_id": "abc123"}'
   Confirme que a resposta vem no formato esperado e que a execução
   aparece no histórico do n8n (aba "Executions").

4. EXPORTAR O FLUXO EM JSON
   No n8n, com o fluxo aberto: menu (⋯) → **Download** (exporta o .json
   do fluxo atual). Salve como
   `n8n/fluxo-aprovacao-reformatax.json` e versione no repositório —
   isso é o que torna o fluxo reproduzível sem depender do seu ambiente
   local. Confirme que o JSON exportado NÃO contém nenhuma credencial
   (o n8n não exporta valores de credenciais por padrão, mas confira).

5. CRIAR A TOOL DE DISPARO (app/tools/notificacao.py)
   - Schemas (pydantic): `NotificacaoInput` (cenario: str, resumo: str,
     session_id: str) e `NotificacaoResultado` (status: str,
     mensagem: str).
   - Exceção `NotificacaoFalhouError(Exception)`.
   - `disparar_notificacao(payload: NotificacaoInput) ->
     NotificacaoResultado`: lê `N8N_WEBHOOK_URL` e
     `N8N_TIMEOUT_SECONDS` das configurações (adicione ambos a
     `app/config.py` e ao `.env.example` principal — estes SIM são
     usados pela aplicação Python, diferente das credenciais do n8n do
     passo 1); faz um POST (`httpx.post`) ao webhook com timeout
     configurado; em caso de timeout/erro de conexão, captura e relança
     como `NotificacaoFalhouError` com mensagem clara (fallback: a
     aprovação continua registrada mesmo se a notificação falhar — não
     trava o fluxo da aplicação).

6. CRIAR O ENDPOINT DE APROVAÇÃO (app/web/main.py)
   - `AprovarRequest(BaseModel)`: `session_id: str`.
   - `POST /api/aprovar`: recupera o estado da sessão no grafo
     (`get_graph().get_state(thread_config(session_id))`); se
     `aguardando_aprovacao_humana` não for `True` nesse estado, retorna
     erro 400 (nada para aprovar); caso contrário, monta
     `NotificacaoInput` com os dados da análise armazenada e chama
     `disparar_notificacao(...)`. Em caso de sucesso, retorna
     `{"status": "notificacao_enviada", ...}`; em caso de
     `NotificacaoFalhouError`, retorna 502 com mensagem amigável (a
     aprovação em si não é desfeita, só a notificação falhou).
   Esta rota NÃO chama `get_llm()` nem reexecuta o grafo — é uma ação
   determinística e simples, coerente com "a lógica principal permanece
   na aplicação, a ferramenta visual atua como apoio à orquestração".

7. ATUALIZAR O FRONT-END (app/web/static/, complemento à Etapa 9.1)
   Quando `aguardando_aprovacao_humana === true`, exiba um botão
   "Aprovar e notificar" no banner de aviso já existente. Ao clicar,
   chama `POST /api/aprovar` com o `session_id` atual e mostra o
   resultado (sucesso ou falha da notificação) na tela.

8. TESTES (tests/test_notificacao.py e tests/test_web.py)
   Com `httpx` mockado (nunca chamando o n8n real nos testes automatizados):
   - `disparar_notificacao` com resposta de sucesso do webhook → retorna
     `NotificacaoResultado` preenchido;
   - `disparar_notificacao` com timeout/erro de conexão → levanta
     `NotificacaoFalhouError`;
   - `POST /api/aprovar` para uma sessão SEM aprovação pendente → 400;
   - `POST /api/aprovar` para uma sessão COM aprovação pendente (gerada
     antes via `/api/analisar` com pergunta de cálculo de impostos) →
     200, com o mock de `disparar_notificacao` confirmando que foi
     chamado com os dados certos.
   Rode `pytest tests/ -v` e confirme que tudo passa sem depender do n8n
   rodando.

9. ATUALIZAR O README.md
   Adicione uma seção "Automação low-code (n8n)" com:
   - como subir o ambiente local (`cd n8n && docker compose up -d`,
     variáveis do `.env.example`);
   - como importar o fluxo exportado (`n8n/fluxo-aprovacao-reformatax.json`)
     numa instância nova do n8n (Import from File, na interface);
   - como configurar a URL do webhook na aplicação
     (`N8N_WEBHOOK_URL=http://localhost:5678/webhook/reformatax-aprovacao`
     no `.env` principal do projeto);
   - o fluxo ponta a ponta: pergunta de cálculo de impostos → aprovação
     pendente → clique em "Aprovar e notificar" → chamada ao n8n →
     registro observável na aba "Executions" do n8n;
   - nota sobre a extensão opcional de ChatOps (Discord/Slack/e-mail),
     caso queira ir além do registro simples.

10. REGISTRAR O PROMPT
    Crie `docs/prompts/12-low-code-n8n.md` com o texto integral deste
    prompt.

11. COMMITS SEMÂNTICOS
    1. chore: adiciona docker-compose do n8n local (#13)
    2. feat: adiciona fluxo n8n exportado (fluxo-aprovacao-reformatax.json) (#13)
    3. feat: adiciona tool de disparo de notificacao (#13)
    4. feat: adiciona endpoint de aprovacao POST /api/aprovar (#13)
    5. feat: adiciona botao de aprovacao no front-end (#13)
    6. test: adiciona testes de notificacao e do endpoint de aprovacao (#13)
    7. docs: documenta a automacao low-code no README (#13)
    8. docs: registra o prompt 12 em docs/prompts/12-low-code-n8n.md (#13)

12. ENVIAR A BRANCH E ABRIR O PULL REQUEST
    git push -u origin feature/low-code

    Mova o card #13 para **Em Revisão** no Project ao abrir o PR.

    Abra o PR direcionado para develop:
      Título: "feat: automacao low-code via n8n (aprovacao humana) (#13)"
      Corpo:
        Closes #13

        ## Contexto
        Fecha o requisito 4.9: automacao low-code (n8n) disparada apos
        aprovacao humana do cenario de calculo de impostos (Etapa 7).
        Ambiente local via Docker, fluxo exportado em JSON versionado.

        ## O que foi feito
        - n8n/docker-compose.yml + n8n/fluxo-aprovacao-reformatax.json
        - app/tools/notificacao.py (disparar_notificacao)
        - POST /api/aprovar
        - Botao de aprovacao no front-end
        - Testes com httpx mockado (nao depende do n8n rodando)
        - README com instrucoes completas de reproducao

        ## Fora do escopo deste PR
        - Nenhuma logica de agente/grafo foi alterada

        ## Checklist
        - [x] Nenhuma credencial do n8n versionada (nem no JSON, nem no .env.example)
        - [x] Logica principal continua na aplicacao Python
        - [x] Testes passam sem o n8n rodando

13. VALIDAÇÃO FINAL
    Com o n8n local rodando e o fluxo importado, teste manualmente o
    caminho completo: pergunta de cálculo de impostos pela interface →
    aprovação → notificação registrada no n8n. Depois, pare o n8n
    (`docker compose down`) e confirme que `pytest tests/ -v` continua
    passando (prova de que os testes não dependem do serviço externo).

Esta é a última etapa "de funcionalidade" do roadmap principal — as
próximas (13 a 16) são documentação de refinamento, README final, vídeo
e revisão de entrega.
```
