(() => {
    "use strict";

    const lista = document.getElementById("lista-cruzamentos");
    const status = document.getElementById("status-cruzamentos");

    if (!lista) {
        console.error("Elemento #lista-cruzamentos não encontrado.");
        return;
    }

    if (typeof window.Plotly === "undefined") {
        if (status) {
            status.textContent = "A biblioteca Plotly não foi carregada. Verifique o script CDN.";
        }
        return;
    }

    async function carregarCruzamentos() {
        if (status) {
            status.textContent = "Carregando cruzamentos...";
        }

        try {
            const resposta = await fetch("/api/analise", { headers: { Accept: "application/json" } });
            const resultado = await resposta.json();

            if (!resposta.ok || resultado.erro) {
                throw new Error( resultado.erro || `Falha HTTP ${resposta.status}` );
            }

            if ( !Array.isArray(resultado.graficos) || resultado.graficos.length === 0 ) {
                if (status) { status.textContent = "Nenhum cruzamento disponível."; }
                return;
            }

            let carregados = 0;
            const promessas = [];

            resultado.graficos.forEach((grafico) => {
                const id = `cruzamento-${grafico.pergunta_1}-${grafico.pergunta_2}`;
                const area = document.getElementById(id);
                const titulo = document.getElementById(`titulo-cruzamento-${grafico.pergunta_1}-${grafico.pergunta_2}`);

                if (titulo) {
                    titulo.textContent = grafico.titulo;
                }

                // OBS Se não existir uma div no HTML para esse cruzamento, ele não vai ser desenhado.
                // mas existe
                if (!area) {
                    console.warn(`Div #${id} não encontrada no HTML.`);
                    return;
                }

                const layout = {
                    ...(grafico.figure.layout || {}),
                    autosize: true,
                    margin: { ...(grafico.figure.layout?.margin || {}), autoexpand: true }
                };

                delete layout.width;

                promessas.push(
                    window.Plotly.newPlot(
                        area,
                        grafico.figure.data || [],
                        layout,
                        {
                            responsive: true,
                            displaylogo: false,
                            displayModeBar: true,
                            modeBarButtonsToRemove: [
                                "pan2d",
                                "resetScale2d",
                                "select2d",
                                "lasso2d",
                                "zoom2d",
                                "toImage"
                            ]
                        }
                    ).then(() => { carregados++; })
                );
            });

            await Promise.all(promessas);
            lista.querySelectorAll(".grafico-plot").forEach((elemento) => { if (elemento.data) { window.Plotly.Plots.resize(elemento); } });
            if (status) {
                status.textContent = `${carregados} cruzamento(s) carregado(s).`;
            }
        } catch (erro) {
            console.error("Erro ao carregar cruzamentos:", erro);
            if (status) {
                status.textContent = `Erro ao carregar cruzamentos: ${erro.message}`;
            }
        }
    }

    window.addEventListener("resize", () => {
        lista.querySelectorAll(".grafico-plot").forEach((elemento) => {
            if (elemento.data) {
                window.Plotly.Plots.resize(elemento);
            }
        });
    });
    carregarCruzamentos();
})();
