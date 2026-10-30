import { buscarJSON, desenharGrafico, definirVisibilidade, atualizarStatus, observarRedimensionamento } from "./carregamento.js";
import { ajustarFiguraMobile } from "./ajustes_graficos.js";
(() => {
    "use strict";
    const lista = document.getElementById("lista-cruzamentos");
    const status = document.getElementById("status-cruzamentos");
    const total = document.getElementById("total-cruzamentos");
    if (!lista) {
        console.error("Elemento #lista-cruzamentos não encontrado.");
        return;
    }
    definirVisibilidade(lista, true);
    if (typeof window.Plotly === "undefined") {
        atualizarStatus( status, "A biblioteca Plotly não foi carregada. Verifique o script CDN." );
        return;
    }
    observarRedimensionamento(lista);
    function registrarErro(erro, grafico, figura, id) {
        console.error(`Erro ao renderizar o gráfico: ${id}`, erro);
        console.error("Perguntas:", { pergunta_1: grafico.pergunta_1, pergunta_2: grafico.pergunta_2 });
        console.error("Tipo:", grafico.tipo);
        if (figura?.layout) {
            console.table(
                Object.entries(figura.layout)
                    .filter(([chave]) => /^xaxis\d*$|^yaxis\d*$/.test(chave))
                    .map(([eixo, config]) => ({ eixo, type: config.type, range: JSON.stringify(config.range), domain: JSON.stringify(config.domain), autorange: config.autorange }))
            );
        }
        console.error("Figura:", figura);
    }
    async function carregarCruzamentos() {
        lista.classList.add("carregando");
        atualizarStatus(status, "Carregando cruzamentos...", true);
        try {
            const resultado = await buscarJSON("/api/analise");
            const graficos = resultado?.graficos;
            if (!Array.isArray(graficos) || graficos.length === 0) {
                if (total) total.textContent = "0";
                atualizarStatus(status, "Nenhum cruzamento disponível.");
                definirVisibilidade(status, true, "flex");
                return;
            }
            if (total) {
                total.textContent = graficos.length;
            }
            const promessas = [];
            for (const grafico of graficos) {
                const sufixo = `${grafico.pergunta_1}-${grafico.pergunta_2}`;
                const id = `cruzamento-${sufixo}`;

                const area = document.getElementById(id);
                const titulo = document.getElementById(`titulo-cruzamento-${sufixo}`);

                if (titulo) { titulo.textContent = grafico.titulo ?? ""; }
                if (!area) { console.warn(`Div #${id} não encontrada no HTML.`); continue; }

                const figura = grafico.figure;

                if (!figura || !Array.isArray(figura.data)) {
                    console.warn(`Figura inválida para o gráfico: ${id}`);
                    continue;
                }
                ajustarFiguraMobile(figura);
                promessas.push(
                    Promise.resolve()
                        .then(() => desenharGrafico(area, figura))
                        .catch(erro => { registrarErro(erro, grafico, figura, id); return null; })
                );
            }
            await Promise.all(promessas);
            definirVisibilidade(status, false);
        } catch (erro) {
            console.error("Erro ao carregar cruzamentos:", erro);
            atualizarStatus(status, `Erro ao carregar cruzamentos: ${erro.message}`);
            definirVisibilidade(status, true, "flex");
        } finally {
            lista.classList.remove("carregando");
        }
    }
    carregarCruzamentos();
})();