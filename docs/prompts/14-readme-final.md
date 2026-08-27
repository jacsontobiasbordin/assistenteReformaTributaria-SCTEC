# Prompt 14 — README.md final completo

- **Data de execução:** 2026-08-26
- **Branch:** docs/readme-video
- **Issue:** [#15](https://github.com/jacsontobiasbordin/assistenteReformaTributaria-SCTEC/issues/15)

## Prompt integral

```
Vamos consolidar o README.md final, reorganizando na ordem exata exigida
pelo requisito 5.2 do documento oficial, preenchendo as lacunas restantes
e revisando tudo de ponta a ponta. A única chamada real a uma API de LLM
de todo o roadmap acontece nesta etapa (para capturar exemplos reais de
entrada/saída) — feita manualmente por você, nunca dentro de um teste
automatizado.

Issue relacionada: #15

git checkout develop
git pull origin develop
git checkout -b docs/readme-video

Execute as etapas abaixo, nesta ordem:

1. ADICIONAR UM SUMÁRIO NO TOPO DO README.md
   O README já ficou longo ao longo das 13 etapas anteriores — adicione
   um índice com links âncora para cada seção, logo abaixo do título.

2. REORDENAR AS SEÇÕES NA ORDEM EXATA DO REQUISITO 5.2
   Confira que o README segue esta ordem (mova o que já existe, sem
   reescrever o que já está bom):
   1. Descrição da solução (Etapa 1)
   2. Classificação e arquitetura, com diagrama (Etapas 1, 4, 5)
   3. Tool e integração (Etapa 3)
   4. Contexto e memória (Etapa 6)
   5. Segurança e autonomia (Etapas 7 e 12.1, incluindo a limitação
      documentada)
   6. Instalação e execução (Etapas 2 e 9)
   7. QA, observabilidade e DevOps (Etapas 8, 10 e 11)
   8. Automação low-code/no-code (Etapa 12/12.1)
   9. Cenários de uso (preenchido no passo 3 — ainda incompleto até aqui)
   10. Análise crítica e limitações (novo — passo 4)

3. CAPTURAR EXEMPLOS REAIS DE ENTRADA E SAÍDA (seção "Cenários de uso")
   Configure um `.env` local com uma `GOOGLE_API_KEY` real (nunca
   versionada). Suba a aplicação (`uvicorn app.web.main:app --reload`) e,
   pela interface ou via curl, capture UMA execução real de cada um dos
   dois cenários exigidos:
   - **Fluxo principal**: uma pergunta legítima (ex.: cadastro de
     produtos) → cole a pergunta enviada e a resposta JSON completa
     recebida (real, não inventada);
   - **Cenário de risco**: uma pergunta com tentativa de prompt
     injection → cole a pergunta enviada e a resposta de bloqueio
     recebida, confirmando que nenhuma informação sensível foi revelada.
   Para o cenário de cálculo de impostos, capture também o retorno de
   `POST /api/confirmar-notificacao` (mostrando `aguardando_aprovacao_humana`
   e, depois de confirmar, o resultado da notificação).
   Formate os três como blocos de código no README, com uma frase de
   contexto antes de cada um.

4. ESCREVER "ANÁLISE CRÍTICA E LIMITAÇÕES"
   Consolide, num só lugar, as limitações já mencionadas ao longo do
   projeto (não invente novas, reúna o que já foi documentado):
   - identificação de cenário por palavras-chave simples, não por LLM;
   - base de conhecimento fixa (3 cenários), sem RAG/busca semântica;
   - memória via checkpointer em processo — não sobrevive a reinício da
     aplicação (Etapa 6);
   - mesmo usuário formula a pergunta e confirma a notificação — sem
     papel de revisor distinto (Etapa 12.1);
   - fluxo do n8n minimalista (registro/resposta), sem canal de chat real
     configurado por padrão (Etapa 12);
   - dados de anomalia/tendência da Etapa 11 são simulados, não de
     produção real.
   Linke também os dois ciclos de refinamento
   (`docs/qa/ciclos-de-refinamento.md`) e deixe um placeholder para o
   link do vídeo: "Vídeo de demonstração: [a adicionar na Etapa 15]".

5. REVISÃO GERAL
   Releia o README de ponta a ponta como se fosse a primeira vez vendo o
   projeto: os comandos de instalação realmente funcionam na ordem
   escrita? Algum link interno quebrado? Alguma seção do requisito 5.2
   faltando? Corrija o que encontrar.

6. REGISTRAR O PROMPT
   Crie `docs/prompts/14-readme-final.md` com o texto integral deste
   prompt.

7. COMMITS SEMÂNTICOS
   1. docs: adiciona sumario e reorganiza secoes do README (#15)
   2. docs: adiciona exemplos reais de entrada e saida dos dois cenarios (#15)
   3. docs: adiciona secao de analise critica e limitacoes (#15)
   4. docs: revisao geral do README (#15)
   5. docs: registra o prompt 14 em docs/prompts/14-readme-final.md (#15)

8. ENVIAR A BRANCH E ABRIR O PULL REQUEST
   git push -u origin docs/readme-video

   Mova o card #15 para **Em Revisão** no Project ao abrir o PR.

   Abra o PR direcionado para develop:
     Título: "docs: README.md final completo (#15)"
     Corpo:
       Closes #15

       ## Contexto
       Consolida o README.md na ordem exata do requisito 5.2, com
       exemplos reais de entrada/saida e a analise critica/limitacoes.

       ## O que foi feito
       - Sumario e reorganizacao das secoes
       - Exemplos reais dos dois cenarios (principal e adversarial)
       - Secao de analise critica e limitacoes
       - Revisao geral

       ## Fora do escopo deste PR
       - Link do video (Etapa 15, ainda nao gravado)

       ## Checklist
       - [x] Todas as 10 secoes do requisito 5.2 presentes, na ordem
       - [x] Exemplos de entrada/saida sao reais, nao inventados
       - [x] Nenhuma API key aparece nos exemplos colados

9. VALIDAÇÃO FINAL
   Peça para alguém (ou você mesmo, num ambiente limpo) seguir só as
   instruções do README do zero e confirmar que consegue rodar a
   aplicação sem precisar perguntar nada a mais.

Este é o penúltimo prompt do roadmap. O próximo (Etapa 15) grava e
publica o vídeo de demonstração, e insere o link que ficou pendente aqui.
```

## Resultado obtido

- README.md reorganizado na ordem exata do requisito 5.2 (10 seções),
  com um sumário no topo com links âncora, todos verificados
  programaticamente contra os headings reais do documento;
- três exemplos reais de entrada/saída capturados executando a
  aplicação localmente com uma `GOOGLE_API_KEY` real (a única chamada
  real a um provedor de LLM em todo o roadmap) — fluxo principal
  (cadastro de produtos), cenário de risco (prompt injection bloqueada)
  e cálculo de impostos com o ciclo completo de confirmação via
  `POST /api/confirmar-notificacao`; nenhuma API key aparece nos
  exemplos colados;
- seção "Análise crítica e limitações" consolidando as seis limitações
  já documentadas ao longo do projeto, sem inventar nenhuma nova, com
  link para os dois ciclos de refinamento e placeholder para o vídeo;
- revisão geral corrigiu o diagrama de arquitetura e o texto ao redor
  (que ainda descreviam o grafo como "planejado, não implementado" —
  desatualizado desde a Etapa 1) para refletir o grafo final
  implementado, e duas menções residuais a "aprovação" na seção de
  automação low-code, alinhando-as à linguagem de "confirmação" da
  Etapa 12.1;
- todos os links internos (arquivos e âncoras) verificados
  programaticamente — nenhum link quebrado;
- suíte de testes (`pytest tests/ -v`) executada após as mudanças:
  mesmos 51 testes passando de antes, sem nenhuma regressão (as duas
  falhas remanescentes são pré-existentes e não relacionadas — uma
  incompatibilidade de `.env` local com `GEMINI_MODEL` e um erro de
  permissão de diretório temporário do Windows).
