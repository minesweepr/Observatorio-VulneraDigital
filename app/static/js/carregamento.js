"use strict";

const CONFIG_PLOTLY = {
    responsive: true,
    displaylogo: false,
    scrollZoom: false,
    displayModeBar: true,
    modeBarButtonsToRemove: [
        "pan2d",
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

export function atualizarStatus(
    elemento,
    mensagem,
    { visivel = true, display = "block" } = {}
) {
    if (!elemento) return;

    elemento.textContent = mensagem;
    elemento.style.display = visivel ? display : "none";
}

export async function buscarJSON(url) {
    const resposta = await fetch(url, {
        headers: { Accept: "application/json" }
    });

    const resultado = await resposta.json();

    if (!resposta.ok || resultado.erro) {
        throw new Error(
            resultado.erro || `Falha HTTP ${resposta.status}`
        );
    }

    return resultado;
}

export function desenharGrafico(
    area,
    figure,
    opcoes = {}
) {
    if (!area) {
        throw new Error("Área do gráfico não encontrada.");
    }

    if (typeof window.Plotly === "undefined") {
        throw new Error("A biblioteca Plotly não foi carregada.");
    }

    const layout = {
        ...(figure.layout || {}),
        autosize: true,
        margin: {
            ...(figure.layout?.margin || {}),
            autoexpand: true
        },
        ...opcoes.layout
    };

    delete layout.width;

    return window.Plotly.newPlot(
        area,
        figure.data || [],
        layout,
        {
            ...CONFIG_PLOTLY,
            ...opcoes.config
        }
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
