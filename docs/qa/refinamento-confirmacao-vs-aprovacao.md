# Ciclo de refinamento — confirmação em vez de aprovação de terceiro

Registro de um ciclo de refinamento (problema → alteração → resultado),
conforme requisito 4.10 / critério 15 do documento oficial, referente à
revisão de linguagem do portão de notificação introduzido na Etapa 12
(#13).

## Problema observado

Uma revisão de design identificou um problema de linguagem, não de
arquitetura, no portão de notificação implementado na Etapa 7 e ligado
ao n8n na Etapa 12: o texto "aprovação humana" (exibido no aviso da
análise) e o botão "Aprovar e notificar" sugeriam que uma pessoa
**diferente** do solicitante revisava a análise antes de autorizar o
envio da notificação.

Isso não reflete o comportamento real da aplicação: o projeto não
implementa autenticação multiusuário, então quem formula a pergunta é
exatamente quem clica no botão que dispara a notificação. Não existe
hoje nenhum mecanismo de revisão por um segundo usuário. A mecânica de
segurança em si estava correta — nenhuma notificação sai sem uma ação
humana explícita — mas a palavra "aprovação" comunicava uma garantia de
revisão por terceiro que a aplicação não oferece.

## Alteração realizada

A linguagem foi revisada de "aprovação" para "confirmação de envio" em
todos os pontos voltados ao usuário, sem alterar nenhuma lógica de
negócio:

1. Mensagem do node `solicitar_aprovacao_humana`
   (`app/agent/nodes.py`): o aviso agora diz "Confirme para notificar a
   área fiscal responsável; nenhuma notificação é enviada
   automaticamente", em vez de "requer aprovação humana";
2. Endpoint `POST /api/aprovar` renomeado para
   `POST /api/confirmar-notificacao` (`app/web/main.py`,
   `app/web/schemas.py`), mantendo exatamente a mesma verificação de
   `aguardando_aprovacao_humana` e o mesmo tratamento de
   `NotificacaoFalhouError`;
3. Botão do front-end renomeado de "Aprovar e notificar" para
   "Confirmar e notificar a área fiscal", com a chamada JS apontando
   para o novo endpoint (`app/web/static/index.html`,
   `app/web/static/app.js`);
4. Fluxo do n8n: path do webhook trocado de `/reformatax-aprovacao`
   para `/reformatax-confirmacao` e mensagem de saída ajustada de
   "Analise aprovada" para "Notificacao confirmada pelo usuario"
   (`n8n/fluxo-confirmacao-reformatax.json`);
5. Limitação documentada explicitamente no README, na seção
   "Segurança e autonomia": nesta versão não há papel de
   revisor/aprovador distinto do solicitante, por ausência de
   autenticação multiusuário.

O campo de estado `aguardando_aprovacao_humana` e o nome da função
`solicitar_aprovacao_humana` foram **mantidos** — eles descrevem
corretamente o comportamento interno (uma ação humana explícita segue
sendo exigida antes de qualquer notificação externa). Apenas a
comunicação voltada ao usuário mudou.

## Resultado obtido

A interface e a documentação agora comunicam com precisão o nível de
controle que realmente existe: uma confirmação explícita do próprio
solicitante, não uma revisão por um segundo usuário. Nenhuma referência
antiga (`/api/aprovar`, "Aprovar e notificar",
`fluxo-aprovacao-reformatax.json`) permanece no projeto, e a suíte de
testes (`pytest tests/ -v`) continua passando após a renomeação.
