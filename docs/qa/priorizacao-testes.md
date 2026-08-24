# Priorização de testes por risco

## Cenário prioritário: prompt injection (cenário adversarial)

Entre os dois cenários de uso exigidos pelo requisito 4.1 — fluxo
principal e cenário de risco — o **cenário adversarial (prompt
injection)** é o teste prioritário do projeto. Justificativa:

### Risco

Uma falha aqui não é "a resposta ficou incompleta" ou "o formato veio
errado" — é o agente **seguir uma instrução não autorizada** embutida
na pergunta do usuário ou **vazar informação sensível** (chave de API,
system prompt, instruções internas). São os dois piores desfechos
possíveis para um agente que tem acesso a credenciais de LLM
(`app/config.py`) e que, em versões futuras do projeto (Etapa 12), vai
ganhar a capacidade de disparar ações externas.

### Impacto

O domínio da aplicação é **fiscal/tributário** — o assistente existe
para apoiar decisões técnicas sobre cadastro de produtos, emissão de
nota fiscal e cálculo de IBS/CBS em sistemas de ERP reais. Uma falha de
segurança aqui não é só um bug técnico: é uma falha de **compliance**
em um domínio regulatório, com potencial de expor a organização a
risco legal/financeiro, não apenas a um resultado tecnicamente
incorreto. Comparado com o fluxo principal — onde uma resposta
imperfeita é, na pior hipótese, um checklist técnico incompleto que um
analista humano ainda vai revisar — a superfície de dano do cenário
adversarial é qualitativamente maior.

### Criticidade

É o único critério do documento oficial do projeto que pode **zerar a
nota inteira**, não apenas descontar pontos: se a triagem falhar e uma
instrução maliciosa for seguida (ex.: o agente revelar a API key
configurada, ou executar uma ação não solicitada pelo usuário), isso
conta como "credenciais expostas" ou "ação não autorizada executada" —
as duas condições de reprovação automática listadas nos critérios de
avaliação. Um bug no fluxo principal (ex.: uma lista vazia, um campo
faltando) é uma perda de pontos pontual; um bug no bloqueio de
segurança é estrutural e desqualificante.

## Evidência

O cenário adversarial é coberto em três camadas, da mais isolada à mais
completa:

1. **Node isolado** — `tests/test_seguranca.py` (chamada direta a
   `triagem_seguranca`, incluindo os 5 testes de regressão adicionados
   nesta etapa após o code review — acentuação, espaçamento, inglês,
   ordem invertida — ver
   [docs/qa/code-review-etapa07-seguranca.md](code-review-etapa07-seguranca.md)).
2. **Grafo completo, sem API** — `tests/test_seguranca.py::test_cenario_adversarial_bloqueia_sem_chamar_llm`
   (via `build_graph().invoke(...)`).
3. **Ponta a ponta via API** — `tests/test_e2e_cenarios.py::test_e2e_cenario_de_risco_prompt_injection_bloqueia_via_api`
   e `test_e2e_cenario_de_risco_com_acentuacao_correta_tambem_bloqueia_via_api`
   (via `TestClient`, requisição HTTP real → API → grafo → resposta) —
   ver [docs/qa/prompt-geracao-teste-e2e.md](prompt-geracao-teste-e2e.md).

Em todas as três camadas, a asserção mais forte é a mesma: o mock de
`get_llm()` **nunca é chamado** no caminho adversarial
(`llm_estruturado.invoke.assert_not_called()`), provando que a
instrução maliciosa não teve nenhuma chance de chegar ao modelo — o
bloqueio é uma regra estrutural da aplicação, não uma expectativa de
que o LLM "se comporte bem".

## Nota sobre limites conhecidos

A priorização acima não significa que a cobertura seja perfeita. O
code review desta mesma etapa
([docs/qa/code-review-etapa07-seguranca.md](code-review-etapa07-seguranca.md))
identificou e deixou registrado, sem corrigir agora, dois gaps
conhecidos: (1) uma pergunta adversarial classificada como
`fora_de_escopo` nunca passa por `triagem_seguranca` — o teste E2E de
acentuação teve que ser ajustado justamente por causa disso, ver
[docs/qa/prompt-geracao-teste-e2e.md](prompt-geracao-teste-e2e.md); e
(2) não existe filtro do lado da saída do LLM, apenas do lado da
entrada. Priorizar este cenário como o mais crítico é exatamente o que
justifica continuar investindo em fechar esses gaps em etapas futuras,
em vez de considerar o trabalho de segurança "concluído".
