# Prompt 11 — DevOps inteligente: pipeline e análise de anomalia

- **Data de execução:** 2026-08-24
- **Branch:** feature/devops-anomalias
- **Resultado obtido:** pipeline de CI configurado
  (`.github/workflows/ci.yml`: lint com `ruff`, testes com `pytest`
  + cobertura, build/validação via import da aplicação), corrigido um
  YAML inválido encontrado na primeira execução real (colisão de
  `": "` dentro de um scalar plano do `run:`); logs reais do pipeline
  (run #2, disparado pelo PR #31) capturados e analisados com IA em
  `docs/qa/analise-logs-ci.md` (nenhum erro, um aviso real de
  depreciação do Node.js 20 nas actions usadas, ~28,5s de pipeline
  completo); script `scripts/gerar_dados_simulados.py` gerando 20
  execuções simuladas (documentadas como tal) para popular
  `docs/evidencias/auditoria.jsonl` com volume realista, incluindo
  falha simulada de ~20% em `gerar_analise` e latência aleatória;
  anomalia real identificada e explicada com IA em
  `docs/qa/analise-anomalia-e-risco.md` — `gerar_analise` (único node
  agêntico do grafo) concentra 100% da latência e dos erros
  observados, com estimativa quantitativa de risco de fallback
  (`p²`) se a taxa de falha do provedor de LLM aumentar; README
  atualizado com as evidências de DevOps; 48 testes continuam
  passando localmente e no pipeline real do GitHub Actions.

## Prompt

```
Vamos configurar o pipeline de CI (lint, testes, build/validação) e usar
IA para explicar logs de pelo menos duas etapas do pipeline, detectar e
explicar uma anomalia, e produzir uma estimativa simples de tendência/
risco de falha — tudo com evidências reais (do próprio pipeline) ou
simuladas (geradas por um script auxiliar, explicitamente documentadas
como tal). Deploy não é exigido.

Issue relacionada: #12

git checkout develop
git pull origin develop
git checkout -b feature/devops-anomalias

Execute as etapas abaixo, nesta ordem:

1. CRIAR O PIPELINE (.github/workflows/ci.yml)
   name: CI
   on:
     push:
       branches: [develop, main]
     pull_request:
       branches: [develop, main]
   jobs:
     lint-test-build:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: actions/setup-python@v5
           with:
             python-version: "3.11"
         - name: Instalar dependencias
           run: pip install -r requirements.txt
         - name: Lint (ruff)
           run: ruff check .
         - name: Testes (pytest)
           run: pytest tests/ -v --cov=app --cov-report=term-missing
         - name: Build / validacao (import da aplicacao)
           run: python -c "from app.web.main import app; print('OK: aplicacao importada com sucesso')"

2. RODAR O PIPELINE E CAPTURAR OS LOGS REAIS
   Faça um push desta branch (ou abra o PR) para disparar o workflow.
   Depois que rodar, baixe os logs reais:
     gh run list -R jacsontobiasbordin/assistenteReformaTributaria-SCTEC --limit 1
     gh run view <RUN_ID> -R jacsontobiasbordin/assistenteReformaTributaria-SCTEC --log > docs/qa/logs-ci-completo.txt
   Extraia os trechos referentes a "Lint (ruff)" e "Testes (pytest)" para
   dois arquivos separados: `docs/qa/logs-ci-lint.txt` e
   `docs/qa/logs-ci-testes.txt` (se preferir, rode `ruff check .` e
   `pytest tests/ -v` localmente e capture a saída do terminal — também é
   log real dessas duas etapas, só que local em vez de na nuvem).

3. USAR IA PARA EXPLICAR OS LOGS (docs/qa/analise-logs-ci.md)
   Use este prompt (documentado por completo) numa ferramenta de IA,
   colando o conteúdo dos dois arquivos do passo 2:

   ---
   Analise os logs abaixo, das etapas "lint" (ruff) e "testes" (pytest)
   do pipeline de CI do projeto Assistente para Reforma Tributária.
   Explique, em linguagem simples: (1) o que cada etapa verificou; (2) se
   passou ou falhou, e por quê; (3) quaisquer avisos (warnings) que
   apareçam e se merecem atenção; (4) o tempo de execução de cada etapa,
   se estiver nos logs, e se parece razoável para o tamanho do projeto.

   Log do lint:
   <cole aqui o conteudo de docs/qa/logs-ci-lint.txt>

   Log dos testes:
   <cole aqui o conteudo de docs/qa/logs-ci-testes.txt>
   ---

   Salve a resposta integral da IA em `docs/qa/analise-logs-ci.md`, com
   cabeçalho (data, etapas analisadas, prompt usado).

4. GERAR DADOS PARA ANÁLISE DE ANOMALIA (scripts/gerar_dados_simulados.py)
   Como o projeto ainda não tem tráfego real de produção, crie um script
   que roda o grafo várias vezes (com `get_llm()` mockado) para popular
   `docs/evidencias/auditoria.jsonl` com um volume mais realista de
   execuções — deixe claro no cabeçalho do script e no README que estes
   são **dados simulados**, conforme expressamente permitido pelo
   requisito 4.8 ("dados reais ou simulados e documentados"):
   - rode ~20 execuções variando: perguntas válidas nos 3 cenários,
     1-2 perguntas adversariais, e alguns casos com o mock do LLM
     configurado para falhar (`side_effect`) propositalmente em ~20% das
     chamadas a `gerar_analise`, para gerar uma taxa de erro visível no
     node;
   - adicione uma pequena variação de latência simulada (`time.sleep`
     curto e aleatório) só neste script, para que `duracao_ms` no
     `auditoria.jsonl` não seja sempre idêntico.
   Rode o script uma vez: `python scripts/gerar_dados_simulados.py`.

5. DETECTAR E EXPLICAR UMA ANOMALIA + ESTIMAR TENDÊNCIA/RISCO
   (docs/qa/analise-anomalia-e-risco.md)
   Escreva um pequeno resumo agregado a partir de
   `docs/evidencias/auditoria.jsonl` (ex.: contagem de execuções por
   node, taxa de erro por node, latência média/máxima por node — pode
   calcular isso com um script curto ou manualmente a partir do arquivo).
   Use este prompt com uma ferramenta de IA:

   ---
   Abaixo está um resumo agregado das execuções registradas na trilha de
   auditoria do agente Assistente para Reforma Tributária (dados
   simulados para fins de teste, documentados como tal). Identifique: (1)
   se há alguma anomalia (erro recorrente, latência alta, falha de
   ferramenta, aumento de taxa de erro) e em qual node ela ocorre; (2)
   uma explicação plausível para essa anomalia; (3) uma estimativa
   simples de tendência ou risco de falha se o padrão observado
   continuar, com a justificativa baseada nos números apresentados.

   Resumo agregado:
   <cole aqui o resumo (contagens/taxas/latencias por node)>
   ---

   Salve a resposta integral da IA em
   `docs/qa/analise-anomalia-e-risco.md`, com: os dados/evidências
   usados (o resumo agregado), a anomalia identificada, a explicação, a
   estimativa de tendência/risco, e a fonte dos dados (dados simulados
   pelo script do passo 4, não produção real).

6. ATUALIZAR O README.md — seção "QA, observabilidade e DevOps"
   Adicione: como rodar o pipeline localmente (mesmos comandos do
   ci.yml), link para `docs/qa/analise-logs-ci.md` e
   `docs/qa/analise-anomalia-e-risco.md`, e uma nota deixando claro que
   os dados de anomalia/risco são simulados (não produção real, já que o
   projeto ainda não tem uso real).

7. REGISTRAR O PROMPT
   Crie `docs/prompts/11-devops-anomalias.md` com o texto integral deste
   prompt.

8. COMMITS SEMÂNTICOS
   1. ci: adiciona pipeline de lint, testes e build (#12)
   2. docs: adiciona logs reais do pipeline para analise (#12)
   3. docs: documenta analise de logs do CI com IA (#12)
   4. chore: adiciona script de geracao de dados simulados de auditoria (#12)
   5. docs: documenta deteccao de anomalia e estimativa de risco (#12)
   6. docs: atualiza README com evidencias de DevOps (#12)
   7. docs: registra o prompt 11 em docs/prompts/11-devops-anomalias.md (#12)

9. ENVIAR A BRANCH E ABRIR O PULL REQUEST
   git push -u origin feature/devops-anomalias

   Mova o card #12 para **Em Revisão** no Project ao abrir o PR.

   Abra o PR direcionado para develop:
     Título: "ci: pipeline, analise de logs e deteccao de anomalia com IA (#12)"
     Corpo:
       Closes #12

       ## Contexto
       Configura o pipeline de CI e usa IA para explicar logs, detectar
       uma anomalia e estimar tendencia/risco de falha, com evidencias
       documentadas (reais do pipeline + simuladas para o volume de
       execucoes).

       ## O que foi feito
       - .github/workflows/ci.yml (lint, testes, build/validacao)
       - docs/qa/analise-logs-ci.md
       - scripts/gerar_dados_simulados.py
       - docs/qa/analise-anomalia-e-risco.md
       - README atualizado

       ## Fora do escopo deste PR
       - Deploy (nao exigido pelo requisito 4.8)
       - Automacao low-code (Etapa 12)

       ## Checklist
       - [x] Pipeline executa lint, testes e build/validacao com sucesso
       - [x] Logs analisados sao reais (do proprio pipeline)
       - [x] Dados de anomalia/risco sao simulados e claramente identificados como tal

10. VALIDAÇÃO FINAL
    Confirme que o workflow do GitHub Actions rodou com sucesso (aba
    "Actions" do repositório) e que `pytest tests/ -v` continua passando
    localmente.

Não implemente a automação low-code/no-code nesta etapa — isso é o
conteúdo da Etapa 12.
```
