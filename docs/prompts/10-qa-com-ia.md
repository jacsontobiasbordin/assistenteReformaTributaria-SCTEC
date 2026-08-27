# Prompt 10 — QA com IA: code review e teste gerado

- **Data de execução:** 2026-08-24
- **Branch:** feature/qa-inteligente
- **Resultado obtido:** revisão com IA sobre o diff real do PR #24
  (Etapa 7 — segurança/governança), documentada na íntegra em
  `docs/qa/code-review-etapa07-seguranca.md`; a revisão encontrou gaps
  reais na detecção de prompt injection (a lista de padrões evadia
  acentuação correta do português, espaçamento irregular e frases em
  inglês, e uma pergunta classificada como `fora_de_escopo` nunca
  passava pela triagem de segurança), 1 gap de baixo risco corrigido
  nesta etapa (`_normalizar_para_deteccao` em `app/agent/nodes.py`, 5
  novos testes de regressão) e os demais registrados como débito
  técnico com justificativa explícita de por que não foram corrigidos
  agora; teste E2E gerado com apoio de IA
  (`tests/test_e2e_cenarios.py`, 3 testes cobrindo o fluxo principal e
  o cenário adversarial via `TestClient` completo — prompt documentado
  em `docs/qa/prompt-geracao-teste-e2e.md`); priorização de testes por
  risco documentada em `docs/qa/priorizacao-testes.md`, justificando o
  cenário adversarial como prioritário; README atualizado com as três
  evidências; 48 testes passando ao todo no projeto.

## Prompt

```
Vamos usar IA em duas frentes de QA, sobre código real do projeto (não
exemplos fictícios): (1) revisão de um PR já mesclado, identificando
problemas/oportunidades reais; (2) geração/refinamento de um teste E2E
cobrindo os dois cenários (principal e adversarial) através da API
completa, com a justificativa de qual cenário é prioritário e por quê.
NÃO altere a lógica de negócio da aplicação nesta etapa além do que for
estritamente necessário para corrigir algo que a revisão apontar como
problema real.

Issue relacionada: #11

git checkout develop
git pull origin develop
git checkout -b feature/qa-inteligente

Execute as etapas abaixo, nesta ordem:

1. OBTER O DIFF DE UM PR REAL PARA REVISÃO
   Escolha o PR da Etapa 7 (segurança/governança — o de maior risco do
   projeto, por isso o mais relevante para revisão crítica). Extraia o
   diff real:
     gh pr diff 8 -R jacsontobiasbordin/assistenteReformaTributaria-SCTEC > docs/qa/diff-pr-08-seguranca.txt
   (ajuste o número do PR se tiver sido diferente de #8 no seu histórico
   real.)

2. RODAR A REVISÃO COM IA E DOCUMENTAR
   Use este prompt (documentado por completo, palavra por palavra, é
   parte da entrega) em uma ferramenta de IA, colando o conteúdo de
   docs/qa/diff-pr-08-seguranca.txt no lugar indicado:

   ---
   Revise o diff abaixo, do Pull Request de segurança/governança do
   projeto Assistente para Reforma Tributária (agente em LangGraph que
   analisa impactos da Reforma Tributária em ERPs). O diff implementa:
   detecção de prompt injection (triagem_seguranca), bloqueio
   determinístico de entrada adversarial (bloquear_acao_insegura) e um
   portão de aprovação humana para o cenário de cálculo de impostos
   (solicitar_aprovacao_humana).

   Analise e responda, com trechos específicos do diff citados:
   1. Há algum padrão de prompt injection comum que a lista de detecção
      NÃO cobre? Dê exemplos concretos de entradas que passariam.
   2. O bloqueio realmente impede qualquer chamada ao LLM no caminho
      adversarial, ou existe algum caminho de código onde isso poderia
      ser contornado?
   3. A regra de aprovação humana (calculo_impostos) é adequada, ou
      deveria cobrir outros casos também?
   4. Que testes adicionais (além dos já existentes) você recomendaria
      para aumentar a confiança nesta implementação?

   Diff:
   <cole aqui o conteúdo de docs/qa/diff-pr-08-seguranca.txt>
   ---

   Salve a resposta integral da IA em `docs/qa/code-review-etapa07-seguranca.md`,
   com um cabeçalho: PR revisado, data, prompt usado (referencie o bloco
   acima), e a resposta da IA na íntegra.

3. AVALIAR E, SE FIZER SENTIDO, APLICAR UMA MELHORIA REAL
   Releia os pontos levantados pela IA. Se algum for um problema real e
   de baixo risco de corrigir agora (ex.: um padrão de injection óbvio
   que faltou na lista da Etapa 7), implemente a correção nesta branch e
   documente em `docs/qa/code-review-etapa07-seguranca.md` uma seção
   final "Ações tomadas" explicando o que foi aceito, o que foi
   descartado (com justificativa) e por quê. Se nada exigir mudança de
   código, registre isso explicitamente também — não invente um problema
   só para "ter o que corrigir".

4. GERAR/REFINAR UM TESTE E2E COM APOIO DE IA (tests/test_e2e_cenarios.py)
   Peça à IA para gerar um teste E2E (ponta a ponta, via `TestClient` da
   API, cobrindo o fluxo completo: requisição HTTP → grafo → resposta)
   para os dois cenários exigidos pelo requisito 4.1/vídeo:
   - fluxo principal (pergunta legítima sobre um dos 3 cenários,
     resposta estruturada completa);
   - cenário de risco (prompt injection via `/api/analisar`, resposta
     bloqueada, mock do LLM nunca chamado — reaproveite/estenda o teste
     equivalente já existente da Etapa 7, agora na camada E2E completa
     via API, não só no grafo isolado).
   Documente o prompt usado para gerar/refinar esse teste em
   `docs/qa/prompt-geracao-teste-e2e.md` (mesmo padrão do passo 2:
   prompt usado + o que foi gerado + ajustes manuais feitos depois, se
   houver). Rode `pytest tests/test_e2e_cenarios.py -v` e confirme que
   passa sem nenhuma API key configurada.

5. DOCUMENTAR A PRIORIZAÇÃO POR RISCO (docs/qa/priorizacao-testes.md)
   Justifique por que o **cenário adversarial (prompt injection)** é o
   teste/cenário prioritário do projeto, com base em:
   - Risco: falha aqui significa vazamento de informação sensível ou
     execução de instrução não autorizada;
   - Impacto: o domínio é fiscal/tributário — erro de segurança tem
     consequência de compliance, não só técnica;
   - Criticidade: é o único critério do documento oficial que pode zerar
     a nota inteira do projeto se malfeito (créditos expostos/ação não
     autorizada executada).
   Cite o teste específico (`test_e2e_cenarios.py`) que cobre esse
   cenário como evidência.

6. ATUALIZAR O README.md — seção "QA, observabilidade e DevOps"
   Adicione: o code review com IA feito (linkando
   `docs/qa/code-review-etapa07-seguranca.md`), o teste E2E gerado
   (linkando `docs/qa/prompt-geracao-teste-e2e.md`), e a priorização por
   risco (linkando `docs/qa/priorizacao-testes.md`).

7. REGISTRAR O PROMPT
   Crie `docs/prompts/10-qa-com-ia.md` com o texto integral deste prompt.

8. COMMITS SEMÂNTICOS
   1. docs: adiciona diff do PR de seguranca para revisao com IA (#11)
   2. docs: documenta code review com IA do PR de seguranca (#11)
   3. test: adiciona teste E2E dos dois cenarios via API (#11)
   4. docs: documenta o prompt usado para gerar o teste E2E (#11)
   5. docs: documenta a priorizacao de testes por risco (#11)
   6. docs: atualiza README com as evidencias de QA (#11)
   7. docs: registra o prompt 10 em docs/prompts/10-qa-com-ia.md (#11)
   (adicione um commit extra tipo `fix:` ou `security:` se o passo 3
   resultar em correção real de código)

9. ENVIAR A BRANCH E ABRIR O PULL REQUEST
   git push -u origin feature/qa-inteligente

   Mova o card #11 para **Em Revisão** no Project ao abrir o PR.

   Abra o PR direcionado para develop:
     Título: "docs: QA com IA - code review, teste E2E e priorizacao (#11)"
     Corpo:
       Closes #11

       ## Contexto
       Aplica IA em duas frentes de QA sobre codigo real do projeto:
       revisao do PR de seguranca e geracao de teste E2E, com
       priorizacao justificada por risco.

       ## O que foi feito
       - docs/qa/code-review-etapa07-seguranca.md
       - tests/test_e2e_cenarios.py + docs/qa/prompt-geracao-teste-e2e.md
       - docs/qa/priorizacao-testes.md
       - README atualizado com as evidencias

       ## Fora do escopo deste PR
       - Pipeline de CI (Etapa 11)
       - Automacao low-code (Etapa 12)

       ## Checklist
       - [x] Revisao de IA feita sobre um diff real (nao um exemplo fictício)
       - [x] Teste E2E cobre os dois cenarios exigidos
       - [x] Priorizacao justificada por risco/impacto/criticidade

10. VALIDAÇÃO FINAL
    Rode `pytest tests/ -v` (suíte completa) e confirme que tudo passa,
    sem nenhuma API key configurada.

Não implemente pipeline de CI nem automação low-code nesta etapa — isso é
o conteúdo das Etapas 11 e 12.
```
