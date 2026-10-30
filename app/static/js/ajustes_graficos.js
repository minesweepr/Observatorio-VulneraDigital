export function ajustarFiguraMobile(figura) {
    if (!figura || !Array.isArray(figura.data)) return;
    const ehMobile = window.matchMedia("(max-width: 600px)").matches;
    if (!ehMobile) return;
    const layout = figura.layout ?? {};
    const limitarRotulo = (rotulo, limite = 15) => {
        const texto = String(rotulo);
        return texto.length > limite ? `${texto.slice(0, limite - 3)}...` : texto;
    };
    const lollipops = figura.data.filter(
        serie => serie.type === "scatter" && ["lines", "markers+text"].includes(serie.mode)
    );
    for (const serie of lollipops) {
        if (Array.isArray(serie.y)) {
            serie.y = serie.y.map(rotulo => limitarRotulo(rotulo));
        }
    }
    if (lollipops.length) {
        layout.yaxis = { ...layout.yaxis, automargin: true, tickfont: { size: 10 }, ticklabelstandoff: 15 };
        layout.margin = { ...layout.margin, t: Math.max(layout.margin?.t ?? 0, 40), b: Math.max(layout.margin?.b ?? 0, 60) };
    }
    const heatmaps = figura.data.filter(
        serie => serie.type === "heatmap"
    );
    for (const serie of heatmaps) {
        serie.textfont = { ...serie.textfont, size: 12 };
        serie.colorbar = {
            ...serie.colorbar,
            orientation: "h",
            x: 0.5,
            xanchor: "center",
            y: -0.25,
            yanchor: "top",
            len: 0.8,
            thickness: 10
        };
    }
    if (heatmaps.length) {
        layout.xaxis = { ...layout.xaxis, automargin: true, tickangle: -35, tickfont: { size: 9 } };
        layout.yaxis = { ...layout.yaxis, automargin: true, tickfont: { size: 9 } };
        layout.margin = { ...layout.margin, l: 35, r: 10, b: Math.max(layout.margin?.b ?? 0, 130) };
    }
    const linhasAreas = figura.data.some( serie => ["scatter", "scattergl"].includes(serie.type) && ["lines", "lines+markers"].includes(serie.mode) );
    const barrasVerticais = figura.data.some( serie => serie.type === "bar" && (serie.orientation === "v" || !serie.orientation) );
    if (linhasAreas || barrasVerticais) {
        layout.xaxis = {
            ...layout.xaxis,
            tickangle: -90,
            tickfont: { ...layout.xaxis?.tickfont, size: 10, italic: false }
        };
    }
    const temSubplots = Object.keys(layout) .filter(chave => /^xaxis\d*$/.test(chave)).length > 1;
    if (temSubplots) {
        layout.showlegend = true;
        layout.legend = {
            ...layout.legend,
            orientation: "h",
            x: 0.5,
            xanchor: "center",
            y: -0.12,
            yanchor: "top"
        };
    }
    if (heatmaps.length || temSubplots) {
        layout.margin = { ...layout.margin, b: Math.max(layout.margin?.b ?? 0, 130) };
    }
    figura.layout = layout;
}