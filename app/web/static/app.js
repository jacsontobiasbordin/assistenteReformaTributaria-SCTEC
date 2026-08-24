(() => {
  "use strict";

  let sessionId = null;

  const campoPergunta = document.getElementById("pergunta");
  const btnAnalisar = document.getElementById("btn-analisar");
  const progresso = document.getElementById("progresso");
  const secaoResultado = document.getElementById("resultado-section");

  const blocoMensagem = document.getElementById("bloco-mensagem");
  const textoMensagem = document.getElementById("texto-mensagem");

  const blocoCenario = document.getElementById("bloco-cenario");
  const textoCenario = document.getElementById("texto-cenario");

  const blocoPontosReforma = document.getElementById("bloco-pontos-reforma");
  const listaPontosReforma = document.getElementById("lista-pontos-reforma");

  const blocoImpactosErp = document.getElementById("bloco-impactos-erp");
  const listaImpactosErp = document.getElementById("lista-impactos-erp");

  const blocoPontosAtencao = document.getElementById("bloco-pontos-atencao");
  const listaPontosAtencao = document.getElementById("lista-pontos-atencao");

  const blocoChecklist = document.getElementById("bloco-checklist");
  const listaChecklist = document.getElementById("lista-checklist");

  const btnCopiar = document.getElementById("btn-copiar");
  const btnBaixar = document.getElementById("btn-baixar");

  document.querySelectorAll(".botao-rapido").forEach((botao) => {
    botao.addEventListener("click", () => {
      campoPergunta.value = botao.dataset.exemplo;
      campoPergunta.focus();
    });
  });

  function preencherLista(elementoUl, itens) {
    elementoUl.innerHTML = "";
    (itens || []).forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      elementoUl.appendChild(li);
    });
  }

  function esconderTodosOsBlocos() {
    [
      blocoMensagem,
      blocoCenario,
      blocoPontosReforma,
      blocoImpactosErp,
      blocoPontosAtencao,
      blocoChecklist,
    ].forEach((bloco) => {
      bloco.hidden = true;
    });
  }

  function renderizarResultado(dados) {
    secaoResultado.hidden = false;
    esconderTodosOsBlocos();

    const resposta = dados.resposta_estruturada;
    if (resposta && "cenario_analisado" in resposta) {
      textoCenario.textContent = resposta.cenario_analisado;
      blocoCenario.hidden = false;

      preencherLista(listaPontosReforma, resposta.pontos_reforma_relacionados);
      blocoPontosReforma.hidden = false;

      preencherLista(listaImpactosErp, resposta.impactos_tecnicos_erp);
      blocoImpactosErp.hidden = false;

      preencherLista(listaPontosAtencao, resposta.pontos_atencao);
      blocoPontosAtencao.hidden = false;

      preencherLista(listaChecklist, resposta.checklist_tecnico);
      blocoChecklist.hidden = false;
    } else if (resposta && "mensagem" in resposta) {
      textoMensagem.textContent = resposta.mensagem;
      blocoMensagem.hidden = false;
    }

    btnCopiar.disabled = false;
    btnBaixar.disabled = false;
  }

  function montarTextoResultado() {
    const partes = [];
    document.querySelectorAll("#blocos-analise .bloco, #blocos-analise .bloco-simples").forEach((bloco) => {
      if (bloco.hidden) {
        return;
      }
      const titulo = bloco.querySelector("h3");
      if (titulo) {
        partes.push(titulo.textContent);
      }
      bloco.querySelectorAll("ul li").forEach((item) => {
        partes.push("- " + item.textContent);
      });
      bloco.querySelectorAll("p").forEach((paragrafo) => {
        partes.push(paragrafo.textContent);
      });
      partes.push("");
    });
    return partes.join("\n").trim();
  }

  async function analisar() {
    btnAnalisar.disabled = true;
    progresso.hidden = false;

    try {
      const resposta = await fetch("/api/analisar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          pergunta: campoPergunta.value,
          session_id: sessionId,
        }),
      });

      if (!resposta.ok) {
        throw new Error("Falha ao processar a pergunta (HTTP " + resposta.status + ").");
      }

      const dados = await resposta.json();
      sessionId = dados.session_id;
      renderizarResultado(dados);
    } catch (erro) {
      secaoResultado.hidden = false;
      esconderTodosOsBlocos();
      textoMensagem.textContent = erro.message || "Erro inesperado ao analisar a pergunta.";
      blocoMensagem.hidden = false;
    } finally {
      progresso.hidden = true;
      btnAnalisar.disabled = false;
    }
  }

  btnAnalisar.addEventListener("click", analisar);

  btnCopiar.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(montarTextoResultado());
    } catch (erro) {
      console.error("Não foi possível copiar a resposta.", erro);
    }
  });

  btnBaixar.addEventListener("click", () => {
    const blob = new Blob([montarTextoResultado()], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "analise-reforma-tributaria.txt";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  });
})();
