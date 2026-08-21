# Prompt 00 — Governança, estrutura inicial e cards

- **Data de execução:** 2026-08-20
- **Branch:** main (setup inicial)
- **Resultado obtido:** Repositório local inicializado e conectado ao remoto,
  `.gitignore`, `CONTRIBUTING.md`, estrutura completa de pastas (com
  `.gitkeep`), `docs/etapas-construcao.md` com o plano de 17 etapas e o
  script `scripts/criar_cards_github.sh` criados. Labels, 17 issues e seus
  respectivos cards no GitHub Project foram criados via `gh`, e as branches
  `main`/`develop` foram publicadas no remoto.

## Prompt

```
Vamos configurar a governança inicial do projeto Assistente para Reforma
Tributária (versão final): estrutura mínima de repositório, regras de commit, o arquivo
CONTRIBUTING.md e a criação automática de todas as issues (cards) no
GitHub Project, já adicionadas ao quadro. NÃO implemente nenhuma lógica de
agente, grafo ou LLM nesta etapa — é só governança e planejamento.

Repositório remoto (já criado, vazio): https://github.com/jacsontobiasbordin/assistenteReformaTributaria-SCTEC.git
Project (já criado manualmente, com as colunas renomeadas): número 2

Execute as etapas abaixo, nesta ordem:

1. INICIALIZAR O REPOSITÓRIO LOCAL E CONECTAR AO REMOTO
   git init
   git branch -M main
   git remote add origin https://github.com/jacsontobiasbordin/assistenteReformaTributaria-SCTEC.git

2. CRIAR O .gitignore
   Igual ao padrão de projeto Python já usado no mini-projeto: ambientes
   virtuais (.venv/, venv/), cache (__pycache__/, *.pyc), .env, .vscode/,
   .idea/, .DS_Store, build/, dist/, *.egg-info/, *.log.

3. CRIAR O CONTRIBUTING.md (na raiz do repositório)
   Copie o conteúdo abaixo integralmente — ele define a convenção de
   commits e como issues/PRs/cards se relacionam neste projeto:

   ---
   # Guia de Contribuição — Assistente para Reforma Tributária (Projeto Final)

   ## Commits semânticos
   Formato: `<tipo>(<escopo opcional>): <descrição curta no imperativo> (#<issue>)`

   Tipos: feat, fix, docs, chore, refactor, test, ci, security.

   Exemplo: `feat(langgraph): adiciona no triagem_seguranca (#9)`

   ## Branches
   main (versão final) ← develop (integração) ← feature/*, docs/*, chore/*, ci/*

   ## Relação entre commits, PRs e cards (issues)
   O card é movido manualmente ao longo do fluxo, seguindo estes momentos:
   1. Ao começar a trabalhar num card, mover de Backlog/A Fazer para
      Em Andamento;
   2. Toda PR de feature/* para develop inclui "Closes #N" na descrição
      (cria o vínculo com a issue) — ao abrir o PR, mover o card para
      Em Revisão;
   3. Ao mesclar o PR em develop, mover o card para Concluído;
   4. Quando develop for mesclada em main (etapa final do projeto), as
      issues com "Closes #N" fecham automaticamente (merge na branch
      padrão) — esse é o fechamento oficial da issue, coerente com o card
      já estar em Concluído desde o passo 3.

   ## Segredos
   Nunca commitar chaves, tokens ou arquivos .env reais. Usar sempre
   .env.example com apenas os nomes das variáveis.
   ---

4. CRIAR A ESTRUTURA DE PASTAS DO PROJETO
   Crie a estrutura abaixo (pastas vazias devem conter um arquivo
   `.gitkeep` para serem versionadas pelo Git). Nenhum arquivo `.py` deve
   conter lógica além de imports/comentários — implementação real começa
   só a partir da Etapa 3 em diante:

   assistenteReformaTributaria-SCTEC/
   ├── app/
   │   ├── __init__.py
   │   ├── agent/
   │   │   ├── __init__.py
   │   │   └── .gitkeep          # grafo LangGraph — a partir da Etapa 4
   │   ├── tools/
   │   │   ├── __init__.py
   │   │   └── .gitkeep          # ferramenta de consulta local — Etapa 3
   │   └── web/
   │       ├── __init__.py
   │       └── .gitkeep          # interface/API — Etapa 9
   ├── data/
   │   └── .gitkeep              # base local de conhecimento — Etapa 3
   ├── docs/
   │   ├── etapas-construcao.md  # criado no passo 5
   │   ├── prompts/
   │   │   └── .gitkeep          # prompts registrados a partir deste
   │   ├── qa/
   │   │   └── .gitkeep          # evidencias de QA/DevOps — Etapas 10-11
   │   ├── evidencias/
   │   │   └── .gitkeep          # observabilidade/seguranca — Etapas 7-8
   │   └── apresentacao/
   │       └── .gitkeep
   ├── tests/
   │   ├── __init__.py
   │   └── .gitkeep
   ├── scripts/
   │   └── .gitkeep              # script de automacao — passo 7
   ├── .github/
   │   └── workflows/
   │       └── .gitkeep          # pipeline CI — Etapa 11
   ├── .env.example               # preenchido na Etapa 2
   ├── .gitignore                 # ja criado no passo 2
   ├── CONTRIBUTING.md            # ja criado no passo 3
   ├── README.md                  # esqueleto minimo por enquanto
   └── requirements.txt           # preenchido na Etapa 2

   Crie o README.md apenas com um esqueleto mínimo nesta etapa: nome do
   projeto ("Assistente para Reforma Tributária"), uma linha de descrição
   e uma seção "Status: em desenvolvimento — estrutura inicial". O
   conteúdo completo (escopo, arquitetura, cenários etc.) é escrito na
   Etapa 1 e na Etapa 14. Crie `.env.example` e `requirements.txt` vazios
   por enquanto, cada um com um comentário indicando que serão preenchidos
   na Etapa 2.

5. CRIAR O ARQUIVO docs/etapas-construcao.md
   Copie a tabela de 17 etapas (0 a 16) do plano de construção do projeto
   já definido, com as colunas: #, Etapa, Requisito(s) atendido(s), Branch.
   Este arquivo serve de referência única entre o plano, os cards do
   Project e os prompts que serão executados nas próximas etapas.

6. REGISTRAR ESTE PROMPT EM docs/prompts/
   Crie o arquivo `docs/prompts/00-governanca.md` com o texto integral
   deste prompt (todo o conteúdo da seção "Prompt" que você acabou de
   executar), precedido de um cabeçalho curto:
   - título: "Prompt 00 — Governança, estrutura inicial e cards"
   - data de execução
   - branch: main (setup inicial)
   - resultado obtido: resumo de 2-3 linhas do que foi criado
   A partir da próxima etapa, todo prompt executado deve ser registrado
   da mesma forma, com numeração sequencial (`01-escopo.md`,
   `02-estrutura-python.md`, ...), atendendo ao requisito 4.10 do
   documento oficial (manter documentadas as principais instruções
   utilizadas ao longo do projeto).

7. CRIAR O SCRIPT DE AUTOMAÇÃO (scripts/criar_cards_github.sh)
   Crie o script abaixo (os valores de REPO, OWNER e PROJECT_NUMBER já
   estão preenchidos). Ele cria as labels, as 17 issues (uma por
   etapa do docs/etapas-construcao.md) e adiciona cada uma ao Project:

   #!/usr/bin/env bash
   set -euo pipefail

   REPO="jacsontobiasbordin/assistenteReformaTributaria-SCTEC"
   OWNER="jacsontobiasbordin"
   PROJECT_NUMBER="2"

   gh label create "governanca"      -R "$REPO" -c "#5319E7" -f
   gh label create "escopo"          -R "$REPO" -c "#5319E7" -f
   gh label create "langgraph"       -R "$REPO" -c "#1D76DB" -f
   gh label create "tool"            -R "$REPO" -c "#0E8A16" -f
   gh label create "memoria"         -R "$REPO" -c "#0E8A16" -f
   gh label create "seguranca"       -R "$REPO" -c "#B60205" -f
   gh label create "observabilidade" -R "$REPO" -c "#FBCA04" -f
   gh label create "interface"       -R "$REPO" -c "#BFD4F2" -f
   gh label create "qa"              -R "$REPO" -c "#5319E7" -f
   gh label create "devops"          -R "$REPO" -c "#D93F0B" -f
   gh label create "low-code"        -R "$REPO" -c "#C2E0C6" -f
   gh label create "docs"            -R "$REPO" -c "#C5DEF5" -f
   gh label create "entrega"         -R "$REPO" -c "#000000" -f

   criar_card () {
     local titulo="$1" corpo="$2" label="$3"
     url=$(gh issue create -R "$REPO" --title "$titulo" --body "$corpo" --label "$label")
     gh project item-add "$PROJECT_NUMBER" --owner "$OWNER" --url "$url"
     echo "Criado: $titulo -> $url"
   }

   criar_card "Etapa 0 — Governanca: regras de commit e cards automaticos" \
     $'Objetivo: publicar CONTRIBUTING.md e configurar labels/issues/Project.\nResultado esperado: repositorio com governanca definida e quadro populado.\nBranch: main (setup inicial, sem feature branch)' \
     "governanca"

   criar_card "Etapa 1 — Escopo, dominio e classificacao da solucao" \
     $'Objetivo: definir problema, publico, entradas/saidas, riscos e criterios de sucesso; classificar a solucao como workflow hibrido, com justificativa.\nResultado esperado: docs/escopo.md + secao inicial do README.\nBranch: docs/escopo' \
     "escopo"

   criar_card "Etapa 2 — Estrutura do projeto, config multi-LLM e requirements" \
     $'Objetivo: estrutura de pastas, .gitignore, requirements.txt, configuracao do modelo via variavel de ambiente.\nResultado esperado: projeto instalavel localmente, sem logica de agente ainda.\nBranch: chore/estrutura-inicial' \
     "escopo"

   criar_card "Etapa 3 — Tool de consulta a base local com validacao e tratamento de falhas" \
     $'Objetivo: implementar a ferramenta funcional (servico/backend) com validacao de payload/parametros e tratamento de erros.\nResultado esperado: tool testada isoladamente, sem grafo ainda.\nBranch: feature/tool-integracao' \
     "tool"

   criar_card "Etapa 4 — Nucleo do grafo LangGraph (state, nodes, edges)" \
     $'Objetivo: state tipado, nodes com responsabilidade unica, edges explicitas, execucao sequencial e ramificacao condicional.\nResultado esperado: grafo funcional de ponta a ponta no caminho principal.\nBranch: feature/langgraph-agente' \
     "langgraph"

   criar_card "Etapa 5 — Paralelizacao e condicao de parada explicita" \
     $'Objetivo: paralelizar consulta a base local e triagem de seguranca (fan-out/fan-in); garantir condicao de parada sem loop indefinido.\nResultado esperado: grafo atualizado e testado com paralelizacao real.\nBranch: feature/langgraph-agente' \
     "langgraph"

   criar_card "Etapa 6 — Memoria de sessao (checkpointer)" \
     $'Objetivo: adicionar checkpointer do LangGraph para memoria de curto prazo entre perguntas da mesma sessao.\nResultado esperado: teste com 2 perguntas em sequencia mantendo contexto.\nBranch: feature/memoria-rag' \
     "memoria"

   criar_card "Etapa 7 — Seguranca, governanca e aprovacao humana" \
     $'Objetivo: no de triagem de prompt injection/entrada nao confiavel, limites de autonomia, acao sensivel condicionada a aprovacao humana.\nResultado esperado: cenario adversarial demonstrado e documentado.\nBranch: feature/governanca' \
     "seguranca"

   criar_card "Etapa 8 — Observabilidade e resiliencia" \
     $'Objetivo: logs estruturados + trilha de auditoria correlacionados; investigar 1 execucao; timeout, retry limitado e fallback.\nResultado esperado: evidencia de investigacao de execucao documentada em docs/evidencias.\nBranch: feature/observabilidade' \
     "observabilidade"

   criar_card "Etapa 9 — Interface executavel da aplicacao (API)" \
     $'Objetivo: expor o grafo via API local (FastAPI), suficiente para demonstrar os dois cenarios.\nResultado esperado: endpoint testado localmente.\nBranch: feature/interface' \
     "interface"

   criar_card "Etapa 10 — QA com IA: code review e teste gerado" \
     $'Objetivo: usar IA para revisar um PR/diff real e gerar ou refinar um teste de integracao ou E2E; justificar prioridade por risco.\nResultado esperado: docs/qa/ com evidencias e prompt usado.\nBranch: feature/qa-inteligente' \
     "qa"

   criar_card "Etapa 11 — DevOps inteligente: pipeline e analise de anomalia" \
     $'Objetivo: pipeline CI (lint, testes, build); IA explicando logs de pelo menos 2 etapas; deteccao/explicacao de 1 anomalia; estimativa simples de risco.\nResultado esperado: docs/qa/ com analises e evidencias.\nBranch: feature/devops-anomalias' \
     "devops"

   criar_card "Etapa 12 — Automacao low-code/no-code (n8n)" \
     $'Objetivo: fluxo no n8n disparado por webhook apos aprovacao humana, gerando notificacao observavel.\nResultado esperado: instrucoes de reproducao no README.\nBranch: feature/low-code' \
     "low-code"

   criar_card "Etapa 13 — Prompts e ciclo de refinamento" \
     $'Objetivo: documentar as instrucoes de sistema do agente e pelo menos 1 ciclo de refinamento (problema, alteracao, resultado).\nResultado esperado: docs/prompts/ atualizado.\nBranch: docs/prompts-refinamento' \
     "docs"

   criar_card "Etapa 14 — README.md completo" \
     $'Objetivo: todas as secoes obrigatorias (descricao, classificacao+diagrama, tool, memoria, seguranca, instalacao, QA/observabilidade/DevOps, low-code, 2 cenarios, analise critica/limitacoes).\nResultado esperado: README revisado de ponta a ponta.\nBranch: docs/readme-video' \
     "docs"

   criar_card "Etapa 15 — Gravacao e publicacao do video de demonstracao" \
     $'Objetivo: gravar, editar e publicar o video (ate 12 min, nao listado) e linkar no README.\nResultado esperado: link do video acessivel.\nBranch: docs/readme-video' \
     "entrega"

   criar_card "Etapa 16 — Revisao final e entrega" \
     $'Objetivo: revisar o checklist oficial, conferir o quadro, abrir PR develop -> main, submeter os links no AVA.\nResultado esperado: repositorio, quadro e video prontos para avaliacao.\nBranch: chore/entrega-final' \
     "entrega"

   echo "Todas as issues foram criadas e adicionadas ao Project."

8. TORNAR O SCRIPT EXECUTÁVEL E RODAR
   chmod +x scripts/criar_cards_github.sh
   ./scripts/criar_cards_github.sh
   Confirme na saída do terminal que as 17 issues foram criadas com
   sucesso e que cada uma foi adicionada ao Project (mensagens "Criado:").

9. CONFERIR O QUADRO
   Confirme que todas as 17 issues aparecem na coluna Backlog do Project.
   A movimentação entre colunas (Em Andamento, Em Revisão, Concluído) é
   feita manualmente ao longo do projeto, seguindo as regras descritas no
   CONTRIBUTING.md — o documento oficial não exige automação para isso,
   só que o quadro reflita o andamento real do trabalho.

10. COMMITS SEMÂNTICOS E PRIMEIRO PUSH
   Como esta é a configuração inicial do repositório (sem feature branch,
   conforme já registrado no próprio card da Etapa 0), os commits abaixo
   vão direto para main:
   1. chore: cria estrutura inicial de pastas do projeto
   2. docs: adiciona CONTRIBUTING.md com regras de commit e governanca
   3. chore: adiciona .gitignore inicial
   4. docs: adiciona docs/etapas-construcao.md com o plano das 17 etapas
   5. docs: registra o prompt 00 em docs/prompts/00-governanca.md
   6. chore: adiciona script de criacao automatica de issues e cards

   git push -u origin main

11. CRIAR A BRANCH develop
   git checkout -b develop
   git push -u origin develop

12. VALIDAÇÃO FINAL
    Mostre a saída de `git log --oneline`, `git branch -a` e confirme:
    - A estrutura de pastas, CONTRIBUTING.md, .gitignore,
      docs/etapas-construcao.md, docs/prompts/00-governanca.md e o
      script estão todos versionados;
    - As 17 issues existem no repositório remoto e estão no Project, na
      coluna Backlog;
    - As branches main e develop existem localmente e no remoto;
    - Nenhum segredo foi commitado.

Não implemente nenhuma lógica de agente, grafo, tool ou LLM nesta etapa —
isso começa na Etapa 1 (escopo) e Etapa 2 (configuração multi-LLM e
requirements, dentro da estrutura já criada aqui),
cada uma com seu próprio prompt.
```
