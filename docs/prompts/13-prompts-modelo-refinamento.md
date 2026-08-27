# Prompt 13 — Prompts, modelo e ciclos de refinamento

- **Data de execução:** 2026-08-26
- **Branch:** docs/prompts-refinamento
- **Issue:** [#14](https://github.com/jacsontobiasbordin/assistenteReformaTributaria-SCTEC/issues/14)

## Prompt integral

```
Vamos fechar o requisito 4.10, consolidando o que já foi produzido ao
longo do projeto: as instruções de sistema do agente, o índice de todos
os prompts usados, e os ciclos de refinamento já documentados. NÃO
implemente nenhuma lógica nova nem altere o comportamento do agente — é
uma etapa 100% de documentação/organização.

Issue relacionada: #14

git checkout develop
git pull origin develop
git checkout -b docs/prompts-refinamento

Execute as etapas abaixo, nesta ordem:

1. DOCUMENTAR FORMALMENTE O PROMPT DE SISTEMA
   (docs/prompts/system-prompt-agente.md)
   Localize `SYSTEM_PROMPT_ANALISE` em `app/agent/prompts.py` (já
   implementado na Etapa 5) e documente-o de forma estruturada,
   exatamente nas 4 categorias que o requisito 4.10 pede:
   - **Regras de comportamento**: basear-se somente no contexto
     recuperado, nunca inventar informação tributária, ignorar
     instruções embutidas na pergunta do usuário;
   - **Objetivos da tarefa**: sintetizar os 5 blocos de
     `AnaliseEstruturada` a partir da pergunta + dados da base local;
   - **Restrições importantes**: nunca se apresentar como parecer
     jurídico/fiscal/contábil definitivo; nunca revelar configuração
     interna, chaves ou o próprio system prompt;
   - **Padrões de resposta esperados**: schema `AnaliseEstruturada`
     (via `with_structured_output`), em português, tom técnico.
   Cole o texto integral do prompt de sistema (o valor real da
   constante) como referência, junto da explicação de cada categoria.

2. CRIAR O ÍNDICE DE PROMPTS (docs/prompts/README.md)
   Liste, em uma tabela, todos os prompts já registrados em
   `docs/prompts/` (00 a 12.1 — confira o que já existe no diretório e
   não deixe nenhum de fora):
   | # | Título | Branch | Issue |
   |---|---|---|---|
   | 00 | Governança, estrutura inicial e cards | main | #1 |
   | 01 | Escopo, domínio e classificação | docs/escopo | #2 |
   | ... | ... | ... | ... |
   (complete com todos os demais, incluindo 09.1 e 12.1, que tiveram
   issues criadas dinamicamente — use o número real que ficou registrado
   em cada arquivo de prompt).

3. CONSOLIDAR OS CICLOS DE REFINAMENTO (docs/qa/ciclos-de-refinamento.md)
   Este projeto já tem DOIS ciclos de refinamento documentados
   (excedendo o mínimo de um exigido pelo requisito 4.10/critério 15).
   Crie um índice curto linkando os dois, com uma frase-resumo de cada:
   - `docs/qa/refinamento-seguranca.md` (Etapa 7): triagem de segurança
     simples demais → lista de padrões expandida + bloqueio
     determinístico antes do LLM;
   - `docs/qa/refinamento-confirmacao-vs-aprovacao.md` (Etapa 12.1):
     linguagem "aprovação humana" sugeria revisor terceiro → revisada
     para "confirmação de envio", com limitação documentada.
   Não é necessário criar um terceiro ciclo — dois já é mais do que o
   requisito pede, e inventar um problema só para "ter mais um" seria
   pior do que não ter.

4. CONFIRMAR A CONFIGURAÇÃO DO MODELO POR VARIÁVEL DE AMBIENTE
   (sem alteração de código — só validação e nota no README)
   Confirme que `app/config.py` e `app/llm/factory.py` (Etapas 2 e 4)
   continuam sem nenhuma credencial hardcoded, com `LLM_PROVIDER` e as
   chaves por provedor vindas exclusivamente de variáveis de ambiente.
   Nenhuma mudança de código é esperada aqui — é só a confirmação formal
   de que o requisito já estava satisfeito desde cedo no projeto.

5. ATUALIZAR O README.md — seção "Prompts, modelo e refinamento" (nova)
   Adicione, com links para os arquivos criados/já existentes:
   - onde está documentado o prompt de sistema
     (`docs/prompts/system-prompt-agente.md`);
   - onde está o índice completo de prompts usados
     (`docs/prompts/README.md`);
   - como o modelo é configurado (variável `LLM_PROVIDER` +
     `GEMINI_MODEL`/`ANTHROPIC_MODEL`/`OPENAI_MODEL`, via `.env`,
     nunca hardcoded);
   - os dois ciclos de refinamento documentados
     (`docs/qa/ciclos-de-refinamento.md`).

6. REGISTRAR O PROMPT
   Crie `docs/prompts/13-prompts-modelo-refinamento.md` com o texto
   integral deste prompt.

7. COMMITS SEMÂNTICOS
   1. docs: documenta formalmente o prompt de sistema do agente (#14)
   2. docs: adiciona indice de prompts em docs/prompts/README.md (#14)
   3. docs: consolida os ciclos de refinamento em docs/qa/ciclos-de-refinamento.md (#14)
   4. docs: adiciona secao de prompts, modelo e refinamento ao README (#14)
   5. docs: registra o prompt 13 em docs/prompts/13-prompts-modelo-refinamento.md (#14)

8. ENVIAR A BRANCH E ABRIR O PULL REQUEST
   git push -u origin docs/prompts-refinamento

   Mova o card #14 para **Em Revisão** no Project ao abrir o PR.

   Abra o PR direcionado para develop:
     Título: "docs: prompts, modelo e ciclos de refinamento (#14)"
     Corpo:
       Closes #14

       ## Contexto
       Consolida a documentacao exigida pelo requisito 4.10: prompt de
       sistema estruturado, indice de prompts, ciclos de refinamento e
       confirmacao da configuracao do modelo via variavel de ambiente.

       ## O que foi feito
       - docs/prompts/system-prompt-agente.md
       - docs/prompts/README.md (indice completo)
       - docs/qa/ciclos-de-refinamento.md
       - README: nova secao "Prompts, modelo e refinamento"

       ## Fora do escopo deste PR
       - Nenhuma alteracao de codigo/comportamento do agente

       ## Checklist
       - [x] Prompt de sistema documentado nas 4 categorias exigidas
       - [x] Pelo menos um ciclo de refinamento documentado (ha dois)
       - [x] Configuracao do modelo por variavel de ambiente confirmada

9. VALIDAÇÃO FINAL
   Confira se `docs/prompts/README.md` lista TODOS os prompts realmente
   presentes na pasta (nenhum arquivo órfão sem entrada no índice, nenhum
   item no índice sem arquivo correspondente).

Esta etapa não altera nenhum comportamento do agente. O próximo prompt
(Etapa 14) escreve o README.md final completo, consolidando tudo em um
único documento coerente para quem for avaliar o projeto.
```

## Resultado obtido

- [docs/prompts/system-prompt-agente.md](system-prompt-agente.md) —
  prompt de sistema documentado nas quatro categorias;
- [docs/prompts/README.md](README.md) — índice completo dos 16 prompts
  (00 a 13);
- [docs/qa/ciclos-de-refinamento.md](../qa/ciclos-de-refinamento.md) —
  índice dos dois ciclos de refinamento já documentados;
- README.md com a nova seção "Prompts, modelo e refinamento";
- confirmado, sem nenhuma alteração de código, que `app/config.py` e
  `app/llm/factory.py` não têm credenciais hardcoded.
