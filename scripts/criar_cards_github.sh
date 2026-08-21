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
