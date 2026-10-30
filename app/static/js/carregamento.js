"use strict";
const CONFIG_PLOTLY = {
    responsive: true,
    displaylogo: false,
    scrollZoom: false,
    displayModeBar: true,
    modeBarButtonsToRemove: [
        "resetScale2d",
        "select2d",
        "lasso2d",
        "zoom2d",
        "toImage"
    ]
};
export function definirVisibilidade(elemento, visivel, display = "block") {
    if (!elemento) return;
    elemento.style.display = visivel ? display : "none";
}
export function atualizarStatus(elemento, mensagem, carregando = false) {
    if (!elemento) return;

    const textoStatus = elemento.querySelector("#texto-status");
    const spinner = elemento.querySelector(".spinner");

    if (textoStatus) { textoStatus.textContent = mensagem; }

    if (spinner) { spinner.hidden = !carregando; }

    elemento.style.display = carregando ? "flex" : "none";

    if (!textoStatus && !carregando) {
        elemento.textContent = mensagem;
        elemento.style.display = "flex";
    }
}

export async function buscarJSON(url) {
    const resposta = await fetch(url, { headers: { Accept: "application/json" } });
    const resultado = await resposta.json();
    if (!resposta.ok || resultado.erro) {
        throw new Error( resultado.erro || `Falha HTTP ${resposta.status}` );
    }

    return resultado;
}

export function desenharGrafico(area, figure, opcoes = {}) {
    if (!area) {
        throw new Error("Área do gráfico não encontrada.");
    }
    if (typeof window.Plotly === "undefined") {
        throw new Error("A biblioteca Plotly não foi carregada.");
    }
    const layoutOriginal = figure?.layout || {};
    const layout = { ...layoutOriginal, autosize: true, margin: { ...(layoutOriginal.margin || {}), autoexpand: true }, ...opcoes.layout };
    delete layout.width;
    return window.Plotly.newPlot(
        area,
        figure?.data || [],
        layout,
        { ...CONFIG_PLOTLY, ...opcoes.config }
    );
}

export function redimensionarGraficos(lista) {
    if (!lista || typeof window.Plotly === "undefined") {
        return;
    }

    lista.querySelectorAll(".grafico-plot").forEach((elemento) => {
        if (elemento.data) {
            window.Plotly.Plots.resize(elemento);
        }
    });
}

export function observarRedimensionamento(lista) {
    const redimensionar = () => redimensionarGraficos(lista);

    window.addEventListener("resize", redimensionar);

    return () => {
        window.removeEventListener("resize", redimensionar);
    };
}
