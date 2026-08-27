# Prompt 15 — Vídeo de demonstração

- **Data de execução:** 2026-08-27
- **Branch:** docs/readme-video-link
- **Issue:** [#16](https://github.com/jacsontobiasbordin/assistenteReformaTributaria-SCTEC/issues/16)
- **Link do vídeo:** <https://youtu.be/-qUVHbvjdSU> (YouTube, não listado, até 12 minutos)

## Prompt integral

O vídeo de demonstração já foi gravado e publicado no YouTube como não
listado. Vamos apenas inserir o link no README e registrar este prompt —
nenhuma outra alteração de código ou documentação nesta etapa.

Link do vídeo: https://youtu.be/-qUVHbvjdSU

Issue relacionada: #16

```
git checkout develop
git pull origin develop
git checkout -b docs/readme-video

1. Substitua o placeholder "Vídeo de demonstração: [a adicionar na Etapa
   15]" (adicionado na Etapa 14) pelo link real do vídeo que publiquei acima.

2. Crie docs/prompts/15-video-demonstracao.md com o texto integral deste
   prompt (Parte 1 e Parte 2), incluindo o link do vídeo já preenchido.

3. Commits semânticos:
   1. docs: adiciona link do video de demonstracao ao README (#16)
   2. docs: registra o prompt 15 em docs/prompts/15-video-demonstracao.md (#16)

4. git push -u origin docs/readme-video
   Mova o card #16 para Em Revisão no Project ao abrir o PR.

   Abra o PR direcionado para develop:
     Título: "docs: adiciona link do video de demonstracao (#16)"
     Corpo:
       Closes #16

       ## Contexto
       Insere o link do video de demonstracao (YouTube, nao listado) no
       README, conforme exigido pelo requisito 5.5.

       ## Checklist
       - [x] Video acessivel, ate 12 minutos
       - [x] Link testado (abre corretamente, nao listado)

5. Validação final: abra o link do vídeo em uma aba anônima do navegador
   e confirme que ele abre normalmente (prova de que "não listado" não
   virou "privado" por engano).
```

## Desvios em relação ao prompt

- **Branch:** `docs/readme-video` já existia (usada e mergeada no PR #36,
  Etapa 14). Para não recriar uma branch já consumida, esta etapa usou
  `docs/readme-video-link`. O `push` e o PR seguiram para essa branch.
- **Índice de prompts:** além do arquivo desta página, a linha do
  prompt 15 foi acrescentada em [docs/prompts/README.md](README.md) para
  manter o índice consistente.

## Resultado obtido

- Placeholder `**Vídeo de demonstração:** [a adicionar na Etapa 15]` do
  README substituído pelo link real (`https://youtu.be/-qUVHbvjdSU`),
  identificado como YouTube não listado e com duração até 12 minutos,
  fechando o requisito 5.5;
- este arquivo criado com o texto integral do prompt e o link já
  preenchido; índice de prompts atualizado com a linha 15;
- link aberto em aba anônima do navegador: o vídeo carrega normalmente
  (não listado, não privado);
- nenhuma alteração de código nesta etapa.
