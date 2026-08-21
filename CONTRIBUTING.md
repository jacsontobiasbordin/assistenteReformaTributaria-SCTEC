# Guia de Contribuição — Assistente para Reforma Tributária (Projeto Final)

## Commits semânticos
Formato: `<tipo>(<escopo opcional>): <descrição curta no imperativo> (#<issue>)`

Tipos: feat, fix, docs, chore, refactor, test, ci, security.

Exemplo: `feat(langgraph): adiciona no triagem_seguranca (#9)`

## Branches
main (versão final) ← develop (integração) ← feature/*, docs/*, chore/*, ci/*

## Relação entre commits, PRs e cards (issues)
O card é movido manualmente ao longo do fluxo, seguindo estes momentos:
1. Ao começar a trabalhar num card, mover de Backlog/A Fazer para
   Em Andamento;
2. Toda PR de feature/* para develop inclui "Closes #N" na descrição
   (cria o vínculo com a issue) — ao abrir o PR, mover o card para
   Em Revisão;
3. Ao mesclar o PR em develop, mover o card para Concluído;
4. Quando develop for mesclada em main (etapa final do projeto), as
   issues com "Closes #N" fecham automaticamente (merge na branch
   padrão) — esse é o fechamento oficial da issue, coerente com o card
   já estar em Concluído desde o passo 3.

## Segredos
Nunca commitar chaves, tokens ou arquivos .env reais. Usar sempre
.env.example com apenas os nomes das variáveis.
