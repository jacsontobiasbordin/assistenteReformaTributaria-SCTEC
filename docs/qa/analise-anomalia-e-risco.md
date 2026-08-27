# Detecção de anomalia e estimativa de tendência/risco

- **Data:** 2026-08-24
- **Ferramenta:** Claude (Sonnet 5), dentro do Claude Code.
- **Fonte dos dados:** `docs/evidencias/auditoria.jsonl` — as **últimas
  164 entradas** do arquivo (correspondentes exatamente às 20 execuções
  geradas por `python scripts/gerar_dados_simulados.py`: o arquivo tinha
  139 linhas antes de rodar o script e 303 depois).

> ⚠️ **Dados SIMULADOS, não produção real** (requisito 4.8: "dados
> reais ou simulados e documentados"). O projeto ainda não tem uso real
> em produção. As 20 execuções foram geradas com `get_llm()` mockado
> (`scripts/gerar_dados_simulados.py`), com uma taxa de falha simulada
> de ~20% e uma latência artificial aleatória injetadas de propósito
> **só nesse script** — nada disso existe no código de produção
> (`app/agent/nodes.py`).

## Resumo agregado (calculado a partir do arquivo real)

| Node | Execuções | Erros¹ | Taxa de erro | Latência média (ms) | Latência máxima (ms) |
|---|---:|---:|---:|---:|---:|
| `validar_entrada` | 20 | 0 | 0,0% | 0,00 | 0,01 |
| `identificar_cenario` | 20 | 0 | 0,0% | 0,00 | 0,01 |
| `triagem_seguranca` | 20 | 0 | 0,0% | 0,01 | 0,03 |
| `consultar_base_local` | 20 | 0 | 0,0% | 0,08 | 0,69 |
| `avaliar_seguranca` | 20 | 0 | 0,0% | 0,00 | 0,00 |
| `bloquear_acao_insegura` | 2 | 0 | 0,0% | 0,00 | 0,00 |
| **`gerar_analise`** | **19** | **1** | **5,3%** | **46,48** | **84,24** |
| `validar_resposta` | 19 | 0 | 0,0% | 0,00 | 0,00 |
| `solicitar_aprovacao_humana` | 6 | 0 | 0,0% | 0,00 | 0,01 |
| `registrar_historico` | 18 | 0 | 0,0% | 0,00 | 0,01 |

¹ Erro = `status == "erro"` (exceção não tratada) OU
`decisao == "falha_na_geracao_llm"` (a chamada ao LLM falhou dentro do
próprio `gerar_analise`, tratada pelo mecanismo de retry existente
desde a Etapa 5 — não derruba o grafo, mas é um sinal de falha real na
tentativa).

Das 20 perguntas simuladas (18 válidas nos 3 cenários + 2 adversariais),
todas as 18 válidas foram concluídas com sucesso — nenhuma esgotou as
`MAX_TENTATIVAS_GERACAO = 2` tentativas — e as 2 adversariais foram
corretamente bloqueadas por `bloquear_acao_insegura` (0 chamadas ao
LLM nesse caminho, como esperado).

## Prompt usado

```
Abaixo está um resumo agregado das execuções registradas na trilha de
auditoria do agente Assistente para Reforma Tributária (dados
simulados para fins de teste, documentados como tal). Identifique: (1)
se há alguma anomalia (erro recorrente, latência alta, falha de
ferramenta, aumento de taxa de erro) e em qual node ela ocorre; (2)
uma explicação plausível para essa anomalia; (3) uma estimativa
simples de tendência ou risco de falha se o padrão observado
continuar, com a justificativa baseada nos números apresentados.

Resumo agregado:
<tabela acima>
```

## Resposta da IA (na íntegra)

### 1. Anomalia identificada

Há uma anomalia clara e isolada em um único node: **`gerar_analise`**.
É o único node, entre os dez, com qualquer taxa de erro (5,3%, contra
0,0% em todos os outros) e o único com latência mensurável — sua
latência média (46,48 ms) é cerca de **580 vezes maior** que a do
segundo colocado (`consultar_base_local`, 0,08 ms), e seu pico (84,24
ms) é o maior de toda a tabela por larga margem.

### 2. Explicação plausível

A explicação não é misteriosa — é estrutural, e consistente com o
resto do projeto: `gerar_analise` é o **único node agêntico** de todo o
grafo (documentado desde a Etapa 5 em `app/agent/nodes.py` e no
`README.md`). Todos os outros nove nodes são 100% determinísticos —
validação de string, checagem de padrão, leitura de um JSON local — e
por isso rodam em frações de milissegundo, sem qualquer dependência de
rede. `gerar_analise` é o único que faz uma chamada de rede (ao
provedor de LLM, via `get_llm()`), e é exatamente por isso que ele
concentra 100% da latência mensurável e 100% dos erros observados. Uma
chamada de rede pode falhar (timeout, erro do provedor, formato de
resposta inesperado) de formas que uma checagem de string local nunca
falha — o design do sistema já isola esse risco em um único ponto,
o que esta análise apenas confirma com números.

### 3. Estimativa de tendência/risco

O sistema já tem uma mitigação para isso — retry limitado a
`MAX_TENTATIVAS_GERACAO = 2` — e, na amostra observada, ela funcionou:
nenhuma das 18 perguntas válidas esgotou as duas tentativas. Mas vale
quantificar o risco residual, e ele **cresce de forma não-linear** com
a taxa de falha por chamada:

Se `p` é a probabilidade de falha de uma chamada individual ao LLM, e
as duas tentativas são aproximadamente independentes, a probabilidade
de uma pergunta esgotar as duas tentativas e cair no fallback genérico
(`responder_erro_geracao`, "Não foi possível concluir a análise após
múltiplas tentativas...") é `p²`:

| Taxa de falha por chamada (p) | Risco de fallback (p²) |
|---|---|
| 5,3% (observado nesta amostra) | ~0,3% |
| 20% (taxa configurada no script simulador) | 4% |
| 40% (ex.: instabilidade do provedor) | 16% |
| 50% | 25% |

A taxa observada nesta amostra (5,3%) é **menor** que a taxa configurada
no simulador (20%) — esperado, dado o tamanho pequeno da amostra (19
chamadas): com p=20% e n=19, o desvio padrão do número de falhas é
≈1,74, então observar só 1 falha (em vez das ~3,8 esperadas) está
dentro da variação estatística normal para uma amostra desse tamanho,
não indica que a taxa "real" simulada seja menor que 20%.

**Leitura de risco:** enquanto a taxa de falha por chamada ao LLM se
mantiver na faixa observada/configurada aqui (5-20%), o risco de um
usuário receber o fallback genérico em vez de uma análise real é baixo
(0,3% a 4%). Esse risco cresce **quadraticamente**, não linearmente —
se a taxa de falha do provedor de LLM real dobrar de 20% para 40%
(cenário plausível em caso de instabilidade do provedor, não de bug do
projeto), o risco de fallback não dobra, ele **quadruplica** (4% → 16%).
Isso reforça o valor do timeout explícito e do retry já implementados
(Etapa 8) como mitigação de primeira linha, e sugere que, se o volume
real de uso crescer, monitorar a taxa de erro de `gerar_analise`
especificamente (não a taxa agregada do sistema, que sempre vai
parecer baixa por causa dos outros nove nodes determinísticos) é o
sinal mais informativo para saber se o `MAX_TENTATIVAS_GERACAO` atual
(2) continua suficiente ou precisa ser revisto.
