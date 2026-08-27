# Investigação de uma execução completa (requisito 4.6)

- **Data:** 2026-08-24
- **`execution_id`:** `e4554c0e-9ad1-494e-ad42-f0e16758d2a3`
- **Pergunta do usuário:** "Como calcular o IBS e a CBS na venda?"
- **Como foi gerada:** invocação real de `build_graph().invoke(...)`, com
  `get_llm()` mockado (nenhuma API key real está configurada neste
  ambiente — mesma convenção usada em todos os testes do projeto). O
  grafo, o logger `reformatax` e a trilha de auditoria rodaram de ponta a
  ponta normalmente; apenas a chamada de rede ao provedor de LLM foi
  substituída.
- **Fontes:** log estruturado (stdout, logger `reformatax`) e
  `docs/evidencias/auditoria.jsonl` — todas as linhas abaixo filtradas
  pelo `execution_id` acima, provando a correlação entre os dois sinais.

## Sequência de nodes executados e latência

| # | Node | Duração (ms) | Decisão |
|---|------|--------------:|---------|
| 1 | `validar_entrada` | 0.0024 | `sem_decisao_relevante` (entrada válida) |
| 2 | `identificar_cenario` | 0.0070 | `cenario_identificado=calculo_impostos` |
| 3 | `triagem_seguranca` *(paralelo)* | 0.0051 | `risco_detectado=False` |
| 3 | `consultar_base_local` *(paralelo)* | 0.5745 | `dados_base_local_encontrados` |
| 4 | `avaliar_seguranca` (fan-in) | 0.0004 | `sem_decisao_relevante` (nó de junção, sem risco) |
| 5 | `gerar_analise` | 0.1404 | `analise_gerada_com_sucesso` (1ª tentativa) |
| 6 | `validar_resposta` | 0.0005 | `sem_decisao_relevante` (nó de junção, resposta válida) |
| 7 | `solicitar_aprovacao_humana` | 0.0016 | `aprovacao_humana_solicitada` |
| 8 | `registrar_historico` | 0.0013 | `historico_atualizado` |

- **Soma da duração dos 9 nodes:** ≈ 0,73 ms.
- **Duração total da execução** (primeiro ao último registro de
  auditoria, incluindo overhead de orquestração do LangGraph entre
  supersteps): ≈ 60,7 ms (`22:37:44.700091Z` → `22:37:44.760830Z`) — a
  maior parte desse tempo (~55 ms) está entre `consultar_base_local` e
  `avaliar_seguranca`, refletindo overhead de agendamento do interpretador
  neste processo (primeira execução após reinício do processo Python),
  não lógica de negócio: a soma da duração medida dentro dos nodes é de
  apenas ≈ 0,73 ms.
- `consultar_base_local` e `triagem_seguranca` recebem o mesmo número de
  passo (#3) porque rodam na mesma superstep do LangGraph (fan-out
  paralelo após `identificar_cenario`); `avaliar_seguranca` só executa
  depois que os dois terminam (fan-in).

## Decisões tomadas nos pontos de ramificação

1. **`identificar_cenario`** classificou a pergunta como
   `calculo_impostos` (palavra-chave "calculo" + "ibs"/"cbs"), o cenário
   de maior risco financeiro/de compliance do domínio.
2. **`avaliar_seguranca`** (após o fan-in) roteou para `gerar_analise` —
   `triagem_seguranca` não detectou nenhum padrão suspeito na pergunta
   (`risco_detectado=False`), então o caminho de bloqueio determinístico
   não foi acionado.
3. **`validar_resposta`** considerou a resposta do LLM válida na
   primeira tentativa (`tentativas_geracao=1`, dentro do limite de
   `MAX_TENTATIVAS_GERACAO=2`) — o caminho de retry não foi exercitado
   nesta execução.
4. Como `cenario_identificado == "calculo_impostos"`, o grafo roteou para
   **`solicitar_aprovacao_humana`** antes de `registrar_historico`: a
   resposta final recebeu o aviso explícito de que a análise "requer
   aprovação humana antes de qualquer notificação externa ser
   disparada" e `aguardando_aprovacao_humana` ficou `True` no estado
   final. Nenhuma notificação externa foi disparada (isso só é
   implementado na Etapa 12).

## Erros e retries

Nenhum erro ou retry ocorreu nesta execução: todos os 9 nodes finalizaram
com `status: "sucesso"` na trilha de auditoria, e `gerar_analise` obteve
uma resposta estruturada válida já na primeira tentativa.

Os dois mecanismos de resiliência que cobririam um cenário de falha
(retry limitado a `MAX_TENTATIVAS_GERACAO=2` chamadas e fallback via
`responder_erro_geracao`) já são exercitados pelos testes automatizados —
ver `tests/test_agent_graph.py::test_gerar_analise_com_retry_ate_sucesso_na_segunda_tentativa`
e `tests/test_agent_graph.py::test_gerar_analise_falha_em_todas_tentativas_aciona_fallback`.
O terceiro mecanismo (timeout explícito na chamada ao LLM, adicionado
nesta etapa) é coberto por
`tests/test_observabilidade.py::test_client_llm_e_instanciado_com_timeout_configurado`.

## Trecho do log estruturado (stdout, uma linha JSON por node)

```json
{"timestamp": "2026-08-24T22:37:44.700091+00:00", "level": "INFO", "logger": "reformatax", "message": "node executado", "execution_id": "e4554c0e-9ad1-494e-ad42-f0e16758d2a3", "node": "validar_entrada", "status": "sucesso", "duracao_ms": 0.0023999964469112456, "decisao": "sem_decisao_relevante"}
{"timestamp": "2026-08-24T22:37:44.760228+00:00", "level": "INFO", "logger": "reformatax", "message": "node executado", "execution_id": "e4554c0e-9ad1-494e-ad42-f0e16758d2a3", "node": "solicitar_aprovacao_humana", "status": "sucesso", "duracao_ms": 0.0015999976312741637, "decisao": "aprovacao_humana_solicitada"}
```

## Trecho da trilha de auditoria (`docs/evidencias/auditoria.jsonl`)

```json
{"timestamp": "2026-08-24T22:37:44.700091+00:00", "execution_id": "e4554c0e-9ad1-494e-ad42-f0e16758d2a3", "node": "validar_entrada", "status": "sucesso", "duracao_ms": 0.0023999964469112456, "decisao": "sem_decisao_relevante", "erro": null}
{"timestamp": "2026-08-24T22:37:44.760830+00:00", "execution_id": "e4554c0e-9ad1-494e-ad42-f0e16758d2a3", "node": "registrar_historico", "status": "sucesso", "duracao_ms": 0.0013000026228837669, "decisao": "historico_atualizado", "erro": null}
```

O `execution_id` idêntico nas duas fontes acima (log e auditoria) é a
prova de correlação entre os dois sinais de observabilidade — a mesma
verificação é feita de forma automatizada em
`tests/test_observabilidade.py::test_execucao_completa_gera_auditoria_correlacionada_com_os_logs`.
