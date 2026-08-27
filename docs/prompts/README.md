# Índice de prompts

Todos os prompts usados ao longo do projeto, na ordem de execução,
conforme requisito 4.10. Cada linha aponta para o arquivo com o texto
integral do prompt e o resultado obtido. As etapas 09.1 e 12.1 tiveram
issues criadas dinamicamente durante o desenvolvimento (fora da
numeração original de 17 cards) — o número de issue listado é o
realmente registrado no card do GitHub Projects.

| # | Título | Branch | Issue |
|---|---|---|---|
| [00](00-governanca.md) | Governança, estrutura inicial e cards | main | [#1](https://github.com/jacsontobiasbordin/assistenteReformaTributaria-SCTEC/issues/1) |
| [01](01-escopo.md) | Escopo, domínio e classificação da solução | docs/escopo | [#2](https://github.com/jacsontobiasbordin/assistenteReformaTributaria-SCTEC/issues/2) |
| [02](02-config-multi-llm.md) | Configuração multi-LLM e requirements | chore/estrutura-inicial | [#3](https://github.com/jacsontobiasbordin/assistenteReformaTributaria-SCTEC/issues/3) |
| [03](03-tool-consulta-local.md) | Tool de consulta à base local | feature/tool-integracao | [#4](https://github.com/jacsontobiasbordin/assistenteReformaTributaria-SCTEC/issues/4) |
| [04](04-nucleo-langgraph.md) | Núcleo do grafo LangGraph (state, nodes, edges) | feature/langgraph-agente | [#5](https://github.com/jacsontobiasbordin/assistenteReformaTributaria-SCTEC/issues/5) |
| [05](05-paralelizacao-geracao.md) | Paralelização, condição de parada e `gerar_analise` | feature/langgraph-agente | [#6](https://github.com/jacsontobiasbordin/assistenteReformaTributaria-SCTEC/issues/6) |
| [06](06-memoria-checkpointer.md) | Memória de sessão (checkpointer) | feature/memoria-rag | [#7](https://github.com/jacsontobiasbordin/assistenteReformaTributaria-SCTEC/issues/7) |
| [07](07-seguranca-governanca.md) | Segurança, governança e aprovação humana | feature/governanca | [#8](https://github.com/jacsontobiasbordin/assistenteReformaTributaria-SCTEC/issues/8) |
| [08](08-observabilidade-resiliencia.md) | Observabilidade e resiliência | feature/observabilidade | [#9](https://github.com/jacsontobiasbordin/assistenteReformaTributaria-SCTEC/issues/9) |
| [09](09-interface-api.md) | Interface executável da aplicação (API) | feature/interface | [#10](https://github.com/jacsontobiasbordin/assistenteReformaTributaria-SCTEC/issues/10) |
| [09.1](09.1-frontend-web.md) | Front-end web baseado no mockup do mini-projeto | feature/frontend-web | [#28](https://github.com/jacsontobiasbordin/assistenteReformaTributaria-SCTEC/issues/28) |
| [10](10-qa-com-ia.md) | QA com IA: code review e teste gerado | feature/qa-inteligente | [#11](https://github.com/jacsontobiasbordin/assistenteReformaTributaria-SCTEC/issues/11) |
| [11](11-devops-anomalias.md) | DevOps inteligente: pipeline e análise de anomalia | feature/devops-anomalias | [#12](https://github.com/jacsontobiasbordin/assistenteReformaTributaria-SCTEC/issues/12) |
| [12](12-low-code-n8n.md) | Automação low-code/no-code (n8n) | feature/low-code | [#13](https://github.com/jacsontobiasbordin/assistenteReformaTributaria-SCTEC/issues/13) |
| [12.1](12.1-refinamento-confirmacao.md) | Refinamento: confirmação em vez de aprovação de terceiro | fix/confirmacao-vs-aprovacao | [#33](https://github.com/jacsontobiasbordin/assistenteReformaTributaria-SCTEC/issues/33) |
| [13](13-prompts-modelo-refinamento.md) | Prompts, modelo e ciclos de refinamento | docs/prompts-refinamento | [#14](https://github.com/jacsontobiasbordin/assistenteReformaTributaria-SCTEC/issues/14) |
| [14](14-readme-final.md) | README.md final completo | docs/readme-video | [#15](https://github.com/jacsontobiasbordin/assistenteReformaTributaria-SCTEC/issues/15) |
| [15](15-video-demonstracao.md) | Vídeo de demonstração | docs/readme-video-link | [#16](https://github.com/jacsontobiasbordin/assistenteReformaTributaria-SCTEC/issues/16) |

## Documentos relacionados

- [system-prompt-agente.md](system-prompt-agente.md) — documentação
  formal do prompt de sistema do agente (`SYSTEM_PROMPT_ANALISE`), nas
  quatro categorias exigidas pelo requisito 4.10.
- [docs/qa/ciclos-de-refinamento.md](../qa/ciclos-de-refinamento.md) —
  índice dos ciclos de refinamento (problema → alteração → resultado)
  documentados no projeto.
