# Ciclos de refinamento

Índice dos ciclos de refinamento (problema → alteração → resultado)
documentados no projeto, conforme requisito 4.10 / critério 15 do
documento oficial. O critério exige pelo menos um ciclo documentado;
este projeto documenta dois.

| Etapa | Ciclo | Resumo |
|---|---|---|
| 7 | [docs/qa/refinamento-seguranca.md](refinamento-seguranca.md) | A triagem de segurança da Etapa 5 cobria poucos padrões de texto e, mesmo detectando risco, não bloqueava a execução — o LLM era chamado de qualquer forma. Foi expandida para mais categorias de ataque e passou a bloquear deterministicamente, antes de qualquer chamada ao LLM. |
| 12.1 | [docs/qa/refinamento-confirmacao-vs-aprovacao.md](refinamento-confirmacao-vs-aprovacao.md) | O texto "aprovação humana" e o botão "Aprovar e notificar" (Etapa 12) sugeriam revisão por um usuário diferente do solicitante, o que não reflete a aplicação (sem autenticação multiusuário). A linguagem foi revisada para "confirmação de envio", com a limitação documentada explicitamente no README. |

Um terceiro ciclo não foi criado: dois já excedem o mínimo exigido, e
inventar um problema apenas para "ter mais um" seria pior do que não
ter um terceiro ciclo.
