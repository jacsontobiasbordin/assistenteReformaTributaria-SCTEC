# Plano de Construção — 17 Etapas

Referência única entre o plano do projeto, os cards do GitHub Project e os
prompts registrados em `docs/prompts/`.

| # | Etapa | Requisito(s) atendido(s) | Branch |
|---|-------|---------------------------|--------|
| 0 | Governança: regras de commit e cards automáticos | Governança inicial do repositório | main (setup inicial) |
| 1 | Escopo, domínio e classificação da solução | Definição de problema, público, riscos e classificação (workflow híbrido) | docs/escopo |
| 2 | Estrutura do projeto, config multi-LLM e requirements | Estrutura instalável, configuração de modelo via variável de ambiente | chore/estrutura-inicial |
| 3 | Tool de consulta à base local com validação e tratamento de falhas | Ferramenta funcional com validação de payload/parâmetros | feature/tool-integracao |
| 4 | Núcleo do grafo LangGraph (state, nodes, edges) | State tipado, nodes de responsabilidade única, edges explícitas | feature/langgraph-agente |
| 5 | Paralelização e condição de parada explícita | Fan-out/fan-in, condição de parada sem loop indefinido | feature/langgraph-agente |
| 6 | Memória de sessão (checkpointer) | Memória de curto prazo entre perguntas da mesma sessão | feature/memoria-rag |
| 7 | Segurança, governança e aprovação humana | Triagem de prompt injection, limites de autonomia, human-in-the-loop | feature/governanca |
| 8 | Observabilidade e resiliência | Logs estruturados, trilha de auditoria, timeout/retry/fallback | feature/observabilidade |
| 9 | Interface executável da aplicação (API) | Exposição do grafo via API local (FastAPI) | feature/interface |
| 9.1 | Front-end web baseado no mockup do mini-projeto | Interface web estática (HTML/CSS/JS) consumindo a API da Etapa 9 — issue [#28](https://github.com/jacsontobiasbordin/assistenteReformaTributaria-SCTEC/issues/28), adicional ao plano original de 17 etapas | feature/frontend-web |
| 10 | QA com IA: code review e teste gerado | Revisão de PR/diff real e geração/refino de teste com IA | feature/qa-inteligente |
| 11 | DevOps inteligente: pipeline e análise de anomalia | Pipeline CI, explicação de logs, detecção de anomalia, risco | feature/devops-anomalias |
| 12 | Automação low-code/no-code (n8n) | Fluxo n8n disparado por webhook após aprovação humana | feature/low-code |
| 13 | Prompts e ciclo de refinamento | Documentação de prompts e ciclo de refinamento | docs/prompts-refinamento |
| 14 | README.md completo | Todas as seções obrigatórias do documento oficial | docs/readme-video |
| 15 | Gravação e publicação do vídeo de demonstração | Vídeo de demonstração (até 12 min, não listado) | docs/readme-video |
| 16 | Revisão final e entrega | Checklist oficial, PR develop → main, submissão no AVA | chore/entrega-final |
