# Ciclo de refinamento — triagem de segurança

Registro de um ciclo de refinamento (problema → alteração → resultado),
conforme requisito 4.10 / critério 15 do documento oficial, referente à
evolução da triagem de segurança do agente entre a Etapa 5 e a Etapa 7.

## Problema observado

A `triagem_seguranca` implementada na Etapa 5 (docs/prompts/05-paralelizacao-geracao.md)
era intencionalmente simples: uma lista curta de 6 padrões de texto
(`"ignore as instrucoes"`, `"esqueca as regras"`, `"revele"`,
`"system prompt"`, `"api key"`, `"mostre sua configuracao"`), sem cobrir:

- variações comuns de tentativa de sobrescrever o comportamento do
  sistema (ex.: `"voce agora e"`, `"novo system prompt"`, `"a partir de
  agora voce"`, `"desconsidere o que foi dito"`);
- variações de exfiltração de informação sensível (ex.: `"qual e sua api
  key"`, `"chave de api"`, `"token de acesso"`, `"suas instrucoes
  internas"`);
- marcadores comuns de injeção via delimitadores falsos (ex.: blocos
  `"""system"""`, `[INST]`, `<system>`), uma técnica conhecida de prompt
  injection que a versão da Etapa 5 não detectava.

Além disso, embora `risco_detectado` já fosse calculado na Etapa 5, o
grafo daquela etapa **não bloqueava** a execução com base nesse sinal —
`gerar_analise` era chamado de qualquer forma, e a única defesa contra a
instrução maliciosa era a instrução de sistema pedindo ao LLM para
ignorá-la. Isso significa que a segurança dependia inteiramente do
modelo "se comportar bem", sem nenhuma garantia estrutural.

## Alteração realizada

Na Etapa 7 (docs/prompts/07-seguranca-governanca.md):

1. A lista de padrões suspeitos (`_PADROES_SUSPEITOS` em
   `app/agent/nodes.py`) foi expandida para cobrir as três categorias
   acima, mantendo a detecção 100% determinística (sem LLM) e
   case-insensitive;
2. Um novo node de junção, `avaliar_seguranca`, e um novo node de
   bloqueio, `bloquear_acao_insegura`, foram introduzidos no grafo
   (`app/agent/graph.py`). Quando `risco_detectado == True`, o grafo
   agora roteia **diretamente** para `bloquear_acao_insegura` — que
   nunca chama `get_llm()` — em vez de prosseguir para `gerar_analise`.
   O bloqueio passou a ser uma regra estrutural da aplicação, não uma
   instrução esperançosa dentro do prompt de sistema.

## Resultado obtido

O teste `tests/test_seguranca.py::test_cenario_adversarial_bloqueia_sem_chamar_llm`
comprova, com um assert explícito (`llm.with_structured_output.assert_not_called()`
e `llm_estruturado.invoke.assert_not_called()`), que o LLM **não é sequer
chamado** no cenário adversarial. Isso elimina a dependência da boa
vontade do modelo: mesmo que um provedor de LLM futuro respondesse de
forma diferente a uma instrução maliciosa embutida na pergunta, o
bloqueio já teria ocorrido antes de qualquer chamada de rede ao modelo.
