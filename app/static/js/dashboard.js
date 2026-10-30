import { buscarJSON, desenharGrafico, definirVisibilidade, atualizarStatus, observarRedimensionamento } from "./carregamento.js";
import { ajustarFiguraMobile } from "./ajustes_graficos.js";
(() => {
    "use strict";
    const lista = document.getElementById("lista-graficos");
    const filtro = document.getElementById("filtro-categoria");
    const limpar = document.getElementById("limpar-filtros");
    const status = document.getElementById("status-cruzamentos");
    if (!lista) {
        console.error("Elemento #lista-graficos não encontrado.");
        return;
    }
    if (typeof window.Plotly === "undefined") {
        atualizarStatus( status, "A biblioteca Plotly não foi carregada. Verifique o script CDN." );
        return;
    }
    let requisicaoAtual = 0;
    observarRedimensionamento(lista);
    async function carregarGraficos() {
        const id = ++requisicaoAtual;
        const parametros = new URLSearchParams();
        if (filtro?.value) { parametros.set("categoria", filtro.value); }
        atualizarStatus(status, "Carregando gráficos...", true);
        lista.replaceChildren();
        try {
            const resultado = await buscarJSON( `/api/dashboard?${parametros.toString()}` );
            if (id !== requisicaoAtual) return;
            if ( !Array.isArray(resultado.graficos) || resultado.graficos.length === 0 ) {
                atualizarStatus( status, "Nenhum gráfico disponível. Verifique as colunas do CSV." );
                return;
            }
            const fragmento = document.createDocumentFragment();
            for (const grafico of resultado.graficos) {
                const cartao = document.createElement("article");
                cartao.className = "grafico-card";
                const titulo = document.createElement("h3");
                titulo.className = "grafico-titulo";
                titulo.textContent = grafico.titulo;
                const area = document.createElement("div");
                area.id = `grafico-${grafico.numero}`;
                area.className = "grafico-plot";
                cartao.append(titulo, area);
                fragmento.appendChild(cartao);
            }
            lista.replaceChildren(fragmento);
            await Promise.all(
                resultado.graficos.map((grafico) => {
                    const area = document.getElementById(`grafico-${grafico.numero}`);
                    ajustarFiguraMobile(grafico.figure);
                    return desenharGrafico(area, grafico.figure);
                })
            );
            if (id !== requisicaoAtual) return;
            definirVisibilidade(status, false);
        } catch (erro) {
            if (id !== requisicaoAtual) return;
            console.error("Erro ao carregar os gráficos:", erro);
            lista.replaceChildren();
            definirVisibilidade(status, true, "flex");
            atualizarStatus( status, `Erro ao carregar os gráficos: ${erro.message}` );
        }
    }
    if (filtro) { filtro.addEventListener("change", carregarGraficos); }
    if (limpar) {
        limpar.addEventListener("click", () => { if (filtro) { filtro.value = ""; } carregarGraficos(); });
    }
    carregarGraficos();
})();