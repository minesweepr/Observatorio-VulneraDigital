(() => {
    "use strict";

    const lista = document.getElementById("lista-cruzamentos");
    lista.style.display = 'block';

    const status = document.getElementById("status-cruzamentos");

    const textoStatus = document.getElementById("texto-status");
    const spinner = status?.querySelector(".spinner");

    function atualizarStatus(mensagem, carregando = false) {
        if (textoStatus) {
            textoStatus.textContent = mensagem;
        }

        if (spinner) {
            spinner.hidden = !carregando;
        }
    }

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
                const total = document.getElementById("total-cruzamentos");
                
                if (total) {
                    total.textContent = resultado.graficos.length;
                }

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
                    ).then(() => {carregados++;})
                );
            });

            await Promise.all(promessas);
            lista.querySelectorAll(".grafico-plot").forEach((elemento) => { if (elemento.data) { window.Plotly.Plots.resize(elemento); } });
            if (status) {
                status.style.display = 'none';
            }
            lista.style.display = 'block';
        } catch (erro) {
            console.error("Erro ao carregar cruzamentos:", erro);
            if (status) {
                status.style.display = 'flex';
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
