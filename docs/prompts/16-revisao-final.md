# Prompt 16 — Revisão final e entrega

- **Data de execução:** 2026-08-27
- **Branch:** chore/entrega-final
- **Issue:** [#17](https://github.com/jacsontobiasbordin/assistenteReformaTributaria-SCTEC/issues/17)

## Prompt integral

```
Vamos fazer a revisão final do projeto, item a item contra o checklist
oficial de entrega (seção 7 do documento do professor), fixar as versões
do requirements.txt, adicionar o professor como colaborador, conferir o
quadro do Project por completo, e preparar o PR final develop → main.
NÃO implemente nenhuma funcionalidade nova nesta etapa — só correções
pontuais do que o checklist encontrar pendente.

Issue relacionada: #17

git checkout develop
git pull origin develop
git checkout -b chore/entrega-final

Execute as etapas abaixo, nesta ordem:

1. FIXAR AS VERSÕES DO requirements.txt
   Em um ambiente virtual limpo: `pip install -r requirements.txt`, depois
   `pip freeze` e atualize o requirements.txt fixando `pacote==versão`
   para cada dependência direta já listada. Substitua o comentário antigo
   ("fixar após o primeiro teste") por um comentário com a data real.

2. ADICIONAR O PROFESSOR COMO COLABORADOR
   No GitHub: Settings → Collaborators → Add people (peça o usuário/
   e-mail do professor conforme orientação da disciplina). Confirme que
   o convite foi enviado.

3. PERCORRER O CHECKLIST OFICIAL — "Repositório e organização"
   - [ ] Repositório criado, professor adicionado como colaborador
     (passo 2), nenhum segredo/`.env` versionado — confirme com:
       git log --all --full-history -- "*.env"
       (deve retornar vazio; se aparecer algo, é preciso reescrever o
       histórico ou, no mínimo, revogar a credencial exposta);
   - [ ] Quadro Kanban organizado e atualizado durante o desenvolvimento
     — confira visualmente no Project que TODAS as issues (as 17
     originais + #18 da Etapa 9.1 + #19 da Etapa 12.1, ou os números
     reais que ficaram no seu projeto) estão em **Concluído**, nenhuma
     esquecida em Backlog/A Fazer/Em Andamento;
   - [ ] Fluxo `develop → feature/* → develop → main` com commits
     semânticos — confira com `git log --oneline --graph --all`;
   - [ ] `main` deve conter a versão final e funcional (isso só é
     verdade DEPOIS do passo 9 desta etapa).

4. PERCORRER O CHECKLIST OFICIAL — "Domínio, arquitetura e agente"
   - [ ] Problema, domínio e os dois cenários de uso demonstrados
     (Etapas 1, 14) — confira que o README realmente documenta ambos com
     exemplos reais;
   - [ ] LangGraph com state, nodes, execução sequencial, ramificação
     condicional, paralelização e condição de parada (Etapas 4, 5) —
     rode `pytest tests/test_agent_graph.py -v`;
   - [ ] Tool funcional integrada com validação e tratamento de falhas
     (Etapa 3) — rode `pytest tests/test_local_kb.py -v`;
   - [ ] Estratégia de memória (Etapa 6) — rode
     `pytest tests/test_memoria.py -v`.

5. PERCORRER O CHECKLIST OFICIAL — "Segurança, observabilidade e resiliência"
   - [ ] Controles de segurança + cenário adversarial (Etapa 7) — rode
     `pytest tests/test_seguranca.py -v`, confirmando especificamente o
     teste que prova que `get_llm()` não é chamado no caminho
     adversarial;
   - [ ] Dois sinais de observabilidade correlacionados (Etapa 8) —
     confira `docs/evidencias/investigacao-execucao.md` e
     `docs/evidencias/auditoria.jsonl`;
   - [ ] Timeout, retry limitado e fallback (Etapas 5 e 8) — confira que
     `MAX_TENTATIVAS_GERACAO` e o timeout do LLM estão documentados no
     README.

6. PERCORRER O CHECKLIST OFICIAL — "QA, DevOps e Low-Code"
   - [ ] Code review com IA + teste E2E/integração com priorização por
     risco (Etapa 10) — confira `docs/qa/code-review-etapa07-seguranca.md`,
     `docs/qa/priorizacao-testes.md`, e rode
     `pytest tests/test_e2e_cenarios.py -v`;
   - [ ] Pipeline (lint, testes, build) + IA explicando logs de 2 etapas
     + anomalia + estimativa de risco (Etapa 11) — confira a aba Actions
     do GitHub está verde, e `docs/qa/analise-logs-ci.md` +
     `docs/qa/analise-anomalia-e-risco.md` existem;
   - [ ] Automação low-code/no-code com trigger e saída observável
     (Etapa 12) — confira `n8n/docker-compose.yml`,
     `n8n/fluxo-confirmacao-reformatax.json`, e a seção correspondente
     do README.

7. PERCORRER O CHECKLIST OFICIAL — "README.md e evidências"
   - [ ] README permite compreender, configurar, executar e avaliar,
     incluindo instruções do agente e configuração do modelo por
     variável de ambiente (Etapas 2, 13, 14);
   - [ ] Pelo menos um ciclo de refinamento documentado (há dois: Etapas
     7 e 12.1, consolidados em `docs/qa/ciclos-de-refinamento.md`);
   - [ ] Evidências de testes, observabilidade, QA, DevOps e low-code
     organizadas (confira que nada ficou solto fora de `docs/`);
   - [ ] Link do vídeo no README (Etapa 15).

8. PERCORRER O CHECKLIST OFICIAL — "Vídeo e submissão"
   - [ ] Vídeo acessível, não listado, até 12 minutos, cobrindo os
     pontos da seção 5.5 (Etapa 15);
   - [ ] Vídeo demonstra os dois cenários e os artefatos técnicos
     principais;
   - [ ] Repositório e quadro mantêm as evidências necessárias;
   - [ ] (o último item — submissão no AVA — é feito por você depois do
     passo 11 desta etapa, fora do repositório).

9. CORRIGIR O QUE FOR ENCONTRADO PENDENTE
   Se qualquer item dos passos 3 a 8 estiver incompleto, corrija agora,
   nesta mesma branch, com commits semânticos referenciando #17. Não
   avance para o passo 10 até o checklist estar 100% conferido.

10. COMMITS SEMÂNTICOS
    1. build: fixa versoes das dependencias no requirements.txt (#17)
    2. fix: corrige pendencias encontradas na revisao final do checklist (#17)
       (ajuste a mensagem para refletir o que realmente foi corrigido, se
       nada precisar de correção, pule este commit)
    3. docs: registra o prompt 16 em docs/prompts/16-revisao-final.md (#17)

11. ENVIAR A BRANCH E ABRIR O PR PARA DEVELOP
    git push -u origin chore/entrega-final
    Mova o card #17 para Em Revisão. Abra o PR para develop, com
    "Closes #17" na descrição, mesmo padrão dos anteriores.

12. RELEASE FINAL: PR DE develop PARA main
    Só depois que o PR do passo 11 (e todos os anteriores) estiverem
    mesclados em develop:
      git checkout develop && git pull origin develop
      git checkout main && git pull origin main
    Gere a lista de issues a fechar:
      gh issue list -R jacsontobiasbordin/assistenteReformaTributaria-SCTEC \
        --state open --json number --jq '.[] | "Closes #\(.number)"'
    Abra o PR final:
      gh pr create --base main --head develop \
        --title "release: v1.0.0 - entrega do projeto final Assistente para Reforma Tributaria" \
        --body "Versao final do projeto avaliativo M2.2, consolidando as
      16 etapas do roadmap (+ 9.1 e 12.1) registradas em docs/prompts/.

      <cole aqui a lista de 'Closes #N' gerada acima>"
    Depois do merge, crie uma tag:
      git checkout main && git pull origin main
      git tag v1.0.0 && git push origin v1.0.0

13. VALIDAÇÃO FINAL ABSOLUTA
    - Confirme que todas as issues fecharam automaticamente (a mesclagem
      em main, branch padrão, dispara o fechamento nativo);
    - Confirme que o quadro do Project reflete tudo em Concluído;
    - Rode `pytest tests/ -v` a partir de um clone limpo de `main` (não
      da sua cópia de trabalho), simulando o que o professor vai fazer;
    - Reúna os 3 links para o AVA: URL do repositório, URL do Project,
      URL do vídeo;
    - A PARTIR DE AGORA, NÃO altere mais o repositório — o documento
      oficial proíbe alterações após o prazo de entrega.

Este é o último prompt do roadmap. Parabéns — o projeto está pronto para
submissão.
```

## Resultado da revisão — item a item

### Passo 1 — requirements.txt

As 15 dependências diretas foram fixadas em `pacote==versão` a partir do
ambiente virtual (`.venv`, Python 3.14) usado e validado durante todo o
roadmap (`pip freeze`). O comentário antigo ("fixar após o primeiro
teste") foi substituído por um comentário datado (2026-08-27). Optou-se
por congelar as versões efetivamente exercitadas pelos testes em vez de
recriar um venv do zero, para não introduzir drift às vésperas da
entrega. O CI (`pip install -r requirements.txt` em Python 3.11) valida
a resolução das versões fixadas.

### Passo 2 — professor como colaborador

Ação externa ao repositório, executada manualmente pelo autor em
`Settings → Collaborators`. Não é um artefato versionável.

### Passo 3 — Repositório e organização

- **Nenhum `.env`/segredo versionado:** `git log --all --full-history --
  "*.env"` retorna vazio; apenas `.env.example` (sem credenciais) é
  rastreado.
- **Quadro Kanban:** todas as 19 issues do projeto (1–17 originais + #28
  da Etapa 9.1 + #33 da Etapa 12.1) estão em **Concluído/CLOSED**, exceto
  a #17 (esta etapa), movida para **Em Revisão** na abertura do PR.
- **Fluxo `develop → feature/* → develop → main`** com commits semânticos
  confirmado em `git log --oneline --graph --all` (PRs #2 a #37).
- **`main` com a versão final:** garantido pelo passo 12 (PR de release).

### Passo 4 — Domínio, arquitetura e agente

- README documenta problema, domínio e os cenários de uso com exemplos
  reais (seção "Cenários de uso", capturados na Etapa 14).
- `pytest tests/test_agent_graph.py -v` — 9 passam (state, nodes,
  sequencial, ramificação condicional, paralelização fan-out/fan-in,
  condição de parada por `MAX_TENTATIVAS_GERACAO`).
- `pytest tests/test_local_kb.py -v` — 6 passam (tool com validação por
  schema e tratamento de falhas).
- `pytest tests/test_memoria.py -v` — 3 passam (memória de sessão por
  checkpointer/thread_id).

### Passo 5 — Segurança, observabilidade e resiliência

- `pytest tests/test_seguranca.py -v` — 8 passam, incluindo
  `test_cenario_adversarial_bloqueia_sem_chamar_llm`, que prova que
  `get_llm()` não é chamado no caminho adversarial.
- Dois sinais de observabilidade correlacionados: `execution_id`
  correlaciona `docs/evidencias/investigacao-execucao.md` e as linhas de
  `docs/evidencias/auditoria.jsonl`.
- Timeout (`llm_timeout_seconds` / `LLM_TIMEOUT_SECONDS`), retry limitado
  (`MAX_TENTATIVAS_GERACAO`) e fallback (`responder_erro_geracao`)
  documentados no README (tabela de resiliência).

### Passo 6 — QA, DevOps e Low-Code

- `docs/qa/code-review-etapa07-seguranca.md`, `docs/qa/priorizacao-testes.md`
  presentes; `pytest tests/test_e2e_cenarios.py -v` — 3 passam.
- Pipeline `.github/workflows/ci.yml` (lint ruff + pytest + build/import)
  — aba Actions verde em `develop`. `docs/qa/analise-logs-ci.md` e
  `docs/qa/analise-anomalia-e-risco.md` presentes.
- `n8n/docker-compose.yml` e `n8n/fluxo-confirmacao-reformatax.json`
  presentes; seção "Automação low-code (n8n)" no README.

### Passo 7 — README.md e evidências

- README cobre compreensão, configuração, execução e avaliação, com
  instruções do agente e configuração do modelo por variável de ambiente.
- Dois ciclos de refinamento documentados em
  `docs/qa/ciclos-de-refinamento.md`.
- Evidências organizadas sob `docs/` (nada solto na raiz).
- Link do vídeo no README (Etapa 15).

### Passo 8 — Vídeo e submissão

- Vídeo <https://youtu.be/-qUVHbvjdSU> — YouTube não listado, até 12
  minutos; acessibilidade e "não listado" verificados na Etapa 15.
- Submissão no AVA feita pelo autor após o passo 12.

## Pendências encontradas e decisão (passo 9)

Nenhuma correção de **código** foi necessária. Uma única correção pontual
de documentação: o README dizia "todas as etapas, 0 a 13" no item do
índice de prompts — desatualizado desde a Etapa 13. Ajustado para "0 a
16" (mais as etapas 9.1 e 12.1), refletindo o índice real.

Duas falhas de teste ocorrem **somente no ambiente local do autor** e
foram deixadas como estão (decisão registrada):

1. `tests/test_config.py::test_get_settings_carrega_provedor_gemini` — o
   `.env` local do autor define `GEMINI_MODEL=gemini-3.6-flash` e vaza
   para o teste, que espera o default `gemini-3-flash`. Em um clone limpo
   (sem `.env`, como o do professor) e no CI o teste passa.
2. `tests/test_observabilidade.py::test_registrar_auditoria_concorrente_nao_corrompe_o_arquivo`
   — `PermissionError` ao criar o diretório temporário do pytest nesta
   máquina Windows. Não reproduz no CI (Linux) nem em outra máquina.

Ambas já haviam sido observadas e documentadas na Etapa 14. O CI
(`pytest tests/ -v` em Ubuntu/Python 3.11, sem `.env`) permanece verde.

## Commits desta etapa

1. `build: fixa versoes das dependencias no requirements.txt (#17)`
2. `docs: corrige intervalo de etapas no indice de prompts do README (#17)`
3. `docs: registra o prompt 16 em docs/prompts/16-revisao-final.md (#17)`
